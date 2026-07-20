# Task Spec: Fine-Grained Appearance & Vehicle Attribute Detection

## Objective
The AIVision pipeline currently classifies most clothing/vehicle colors as generic buckets (gray, black, blue) even when the crop is sharp and the actual color is clearly visible (e.g. neon green, maroon, olive). Upgrade the color, garment-type, and vehicle-type/plate detection so that:
- Clear, sharp crops get specific, human-natural color names (not just basic buckets).
- Blurry/low-quality crops still fall back to a safe general color bucket.
- Clothing is split into `upper_body` and `lower_body` with garment type + color as separate fields.
- Vehicles get a `vehicle_type` (car, auto rickshaw, bike/scooter, bus, truck, etc.) and a best-effort `plate_partial` field, even if only 1-2 digits/characters are legible.
- Vehicle type classification is corrected via fine-tuning (the current YOLO detector has no `auto rickshaw`/`e-rickshaw` classes at all — this is a data/class-coverage problem, not a threshold-tuning problem).
- Add a `gender` field (person tracks) using a pretrained person-attribute model, fine-tuned on local samples — not a from-scratch classifier, and not a clothing-style-only heuristic, since clothing alone is a weak/culturally variable signal. Exposed with honest confidence, defaulting to `"unknown"` when uncertain rather than guessing.

---

## Files to touch
| File | Change |
|---|---|
| `src/attributes/color_utils.py` | Replace/augment KMeans+CIEDE2000 naming with CLIP zero-shot color classification (see Section 2); add garment-region split |
| `src/attributes/deep_attribute_extractor.py` | Add garment-type classification head (upper/lower), add vehicle-type classifier, add plate-region OCR hook |
| `src/metadata/metadata_generator.py` | Update fused output schema: `upper_body`, `lower_body`, `vehicle` objects; wire in new confidence-weighted voting for the new fields |
| `src/metadata/metadata_validator.py` | Add validation rules for new fields (unknown fallback, min confidence for plate) |
| `config.yaml` | Add config block for extended color palette, sharpness threshold for fallback, plate OCR settings, and gender-model confidence threshold |
| `src/detection/detector.py` | Point YOLO at fine-tuned weights with expanded class list (see Section 4b) |
| `src/attributes/person_attribute_model.py` *(new)* | Wraps a pretrained person-attribute model (gender, fine-tuned) — see Section 8 |
| training / data pipeline (new, outside `src/`) | Data collection + fine-tuning scripts for both the vehicle detector and the person-attribute model |

---

## 1. Root cause investigation (do this first)
**Note:** a manually expanded CIEDE2000 palette was already tried and still produced excess gray results. This strongly suggests the bug is upstream of naming — in the crop region, masking, or clustering step — not just a thin color dictionary. Before writing more code, log and visually inspect:
- The **actual pixels being clustered** for a sample of "gray-labeled" crops that look clearly colored to a human — dump the raw dominant HSV/RGB cluster values.
- Whether **Shadow/Specular Masking** (`V < 15` / `V > 250`) or **Skin-tone Exclusion** is masking out most of the garment, leaving only a small desaturated pixel remainder to cluster on.
- Whether **Contiguous Spatial Winner Selection** is picking a shadowed/background region instead of the actual garment.

This diagnostic step stays mandatory even with the model swap below — if the crop fed into CLIP is mostly background or shadow, CLIP will guess wrong too.

## 2. Primary fix: CLIP zero-shot color classification (replace KMeans+CIEDE2000 naming)
Manual palettes have a hard ceiling — they can only be as good as the fixed list and the distance metric. Since the pipeline already loads `openai/clip-vit-base-patch32` for embeddings (see `src/attributes/deep_attribute_extractor.py` / pipeline doc Section 1), reuse that same model for color naming instead of extending the KMeans/CIEDE2000 dictionary further:

- Build a bank of text prompts combining color + garment context, e.g. `"a photo of a neon green t-shirt"`, `"a photo of an olive jacket"`, `"a photo of a maroon kurta"` — one per color × rough garment category (upper/lower/vehicle), covering both the ~12 base colors and the ~40-60 fine-grained ones from the earlier expanded list (keep that list — it becomes the prompt vocabulary, not the failed matching mechanism).
- Encode the garment/vehicle crop with CLIP's image encoder (already computed for the embedding step — check whether it can be reused directly instead of re-run).
- Encode all candidate text prompts with CLIP's text encoder (cache these once at startup, they're static).
- Cosine similarity between the crop embedding and each prompt embedding; take the top match (or top-3 for logging/debugging).
- `color_confidence` = the softmax-normalized similarity score of the winning prompt.

Sharpness gating still applies on top of this, since it's an orthogonal signal-quality issue, not a naming-method issue:
- Sharp crop (`quality.sharpness_min_for_finegrained` threshold) → match against the full fine-grained prompt bank.
- Blurry crop → match against only the base-color prompt subset, so low-quality frames don't get false-precision guesses.
- Still return `color_hex` (actual dominant pixel cluster from a lightweight KMeans pass, kept purely for debugging/display) alongside `color_name`, so you can visually sanity-check CLIP's naming against the raw crop.

### Escalation path if CLIP zero-shot still under-performs
If gray persists even after root-cause fixes + CLIP naming, that's a signal to move to a model trained specifically for this rather than zero-shot prompting:
- **Fashion attribute models** (e.g. DeepFashion2 / Fashionpedia-pretrained models) predict garment type *and* color *and* pattern jointly from a crop, rather than as separate heuristic steps — worth adopting if CLIP prompting plateaus.
- **Vehicle-specific pretrained models** (trained on datasets like VeRi-776 / VehicleID) jointly predict vehicle color + type, and would likely outperform reusing generic garment logic on vehicle crops.
- Treat this as a fallback tier, not the first attempt — it's a heavier integration (new model to host/serve, possibly fine-tune on your camera's lighting/angles) and should only be reached for if CLIP zero-shot demonstrably isn't enough after a real test pass.

## 3. Garment type + region split
Add a lightweight garment-type classifier (heuristic or small model — reuse the existing sigmoid-based attribute head pattern in `deep_attribute_extractor.py`) that outputs, separately for the upper and lower body crop regions:
- `garment_type`: e.g. `t-shirt`, `shirt`, `jacket`, `hoodie`, `suit`, `kurta`, `top` (upper); `jeans`, `trousers`, `shorts`, `skirt`, `saree`, `track pants` (lower).
- `color_name`, `color_hex`, `color_confidence` (from the CLIP-based method in Section 2, run independently per region).

This requires splitting the person crop into upper ~55% / lower ~45% (or a pose-based split if a pose estimator is already available anywhere in the pipeline — check before adding a new dependency) before running color/garment classification.

## 4. Vehicle type + plate
For vehicle-class tracks (`car`, `motorcycle`, `bus`, `truck` from the detector, plus a note that `auto rickshaw`/`e-rickshaw` may need a new detector class or a sub-classifier on top of existing "car/motorcycle" boxes):
- `vehicle_type`: normalize/refine into user-facing categories — car, auto rickshaw, bike/scooter, bus, truck, van, e-rickshaw.
- `vehicle_color`: reuse Section 2's CLIP-based naming on the vehicle body region (with a vehicle-appropriate prompt bank, e.g. `"a photo of a yellow auto rickshaw"`).
- `plate_partial`: run a plate-region detector + OCR (e.g. crop the lower-front/rear region, run an existing OCR lib) and return whatever characters are legible with a per-character or overall confidence, rather than requiring a full valid plate. Format: `"plate_partial": "MH12**34", "plate_confidence": 0.42`. If nothing is legible, return `null`, not `"unknown"` string spam.

## 4b. Vehicle detector fine-tuning (fixes misclassification at the source)
The current misclassification isn't a bug to patch with heuristics — COCO (what the pretrained YOLO weights were trained on) has no `auto_rickshaw`, `e_rickshaw`, or fine-grained bike/scooter classes, so the model is guessing among classes it does know (`car`, `motorcycle`) for objects it's never seen labeled correctly. Fix at the source:

1. **Auto-label instead of hand-labeling from zero.** Don't draw every box manually — use one or a combination of:
   - **Model-assisted labeling (active learning):** run the *current* YOLO model over new footage; it will mislabel auto rickshaws/e-rickshaws as `car`/`motorcycle` as it does today, but a human then only needs to **correct the wrong boxes/labels**, not draw from a blank frame. Tools like **CVAT** or **Roboflow** support this natively (model pre-fills, human corrects).
   - **Zero-shot pre-labeling:** run an open-vocabulary detector like **Grounding DINO** with text prompts (`"auto rickshaw"`, `"e-rickshaw"`, `"bike"`) over sample footage to generate candidate boxes automatically, then have a human review/fix rather than label from scratch — typically a 5-10x speedup over fully manual annotation.
   - **Check for existing labeled datasets first:** the **IDD (India Driving Dataset)** includes auto-rickshaw annotations from Indian road footage and may partially cover your vehicle classes already; **Roboflow Universe** often has public pre-labeled rickshaw/tuk-tuk datasets too. Blending a small amount of your own labeled footage with an existing public dataset can reduce how much you need to label from scratch.
   - **Outsource the correction pass** (Labelbox, SuperAnnotate, Scale AI, or a freelance annotator) if the volume of corrections is still large — you review a sample for quality, they do the volume.
   
   Whichever combination you use, the deliverable is the same: a labeled set covering auto rickshaw, e-rickshaw, bike, scooter, van (whichever are common in your camera views), ideally a few hundred boxes per class, with correction/review favored over drawing everything by hand.
2. **Fine-tune the existing pretrained YOLOv11/v12 weights** on the combined class set (original COCO vehicle/person classes + new ones), rather than training a detector from zero — this preserves everything the model already knows about general object shapes/edges and only adapts the classification head (and some backbone layers) to the new categories.
3. **Validate on held-out footage** from different times of day/lighting before replacing the production weights, since rickshaw/bike distinctions are visually subtle and easy to overfit on a small, homogeneous sample.
4. Update `ObjectDetector` (`src/detection/detector.py`) to load the fine-tuned weights and the expanded class list; update the class filter that currently only passes through `person`, `car`, `motorcycle`, `bus`, `truck`.

This is the same "pretrained + fine-tune" pattern as the color fix — reuse Ultralytics' pretrained backbone, don't rebuild detection from scratch.

## 8. Gender classification (person-attribute model, not a clothing heuristic)
Do not implement gender classification as a rule derived from `garment_type`/`color_name` alone — clothing style is a weak, culturally variable signal on its own (uniforms, weather-driven clothing, regional dress all break a clothing-only rule), and using it in isolation will produce confidently wrong answers.

Instead:
1. **Use a pretrained person-attribute recognition model** (trained on datasets such as PETA, RAP, or PA-100k) that predicts gender jointly with build, posture, hair, and clothing attributes from the **full-body crop**, not just the garment region.
2. **Deploy the pretrained model as-is first, before fine-tuning.** These datasets already generalize reasonably well; skip building a labeled correction set upfront. Log every prediction with its confidence in a review queue, and only pull a labeled fine-tuning/correction set from the cases where the model is visibly wrong or low-confidence on your footage — this turns "label a training set from scratch" into "review and correct a much smaller sample," the same active-learning pattern as the vehicle detector above.
3. **Fine-tune only if the review shows a systematic gap** (e.g. consistently wrong on a particular camera angle or clothing style common in your footage) — using that smaller, targeted correction set rather than a large upfront labeling project.
4. Run it on the same 5 keyframes already selected per track, and fuse across frames using the same confidence-weighted approach as other attributes (Section 5's fusion formula, generalized).
5. **Expose real uncertainty.** Output `gender_confidence` alongside `gender`, and apply the same validator rule as other low-confidence attributes: below the configured threshold → `"unknown"`, not a forced guess. This matters more here than for color, since a wrong gender label is more consequential than a wrong t-shirt color.

## 5. Output schema changes (`metadata_generator.py`)
```json
{
  "gender": "female",
  "gender_confidence": 0.79,
  "upper_body": {
    "garment_type": "t-shirt",
    "color_name": "neon green",
    "color_hex": "#39FF14",
    "color_confidence": 0.88
  },
  "lower_body": {
    "garment_type": "jeans",
    "color_name": "navy",
    "color_hex": "#1B2A4A",
    "color_confidence": 0.81
  },
  "vehicle": {
    "vehicle_type": "auto rickshaw",
    "color_name": "yellow",
    "color_hex": "#F4C430",
    "plate_partial": "**12**",
    "plate_confidence": 0.35
  }
}
```
Fuse each field across the 5 keyframes using the **existing dynamic weighting formula** (`base_type_weight * sharpness_ratio * color_confidence`), generalized to also cover `gender` (per-frame gender-model confidence in place of `color_confidence`), applied per-attribute instead of per-track.

## 6. Validation layer (`metadata_validator.py`)
- If confidence for a field is below its configured minimum, overwrite with `"unknown"` (existing behavior) — do **not** invent a color/garment/plate/gender.
- `plate_partial` and `gender` each get their own, higher-strictness confidence threshold, since a wrong plate read or a wrong gender label is more consequential than a wrong t-shirt color.

## 7. Config additions (`config.yaml`)
```yaml
quality:
  sharpness_min_for_finegrained: <tune empirically>
attributes:
  color_palette: extended   # vs "basic"
  plate_ocr:
    enabled: true
    min_confidence: 0.4
  gender_model:
    enabled: true
    min_confidence: 0.6   # tune based on validation results; err strict
detection:
  weights: <path to fine-tuned YOLO weights>
  classes: [person, car, motorcycle, bus, truck, auto_rickshaw, e_rickshaw, bike, scooter, van]
```

## Acceptance criteria
- [ ] On a set of clear, well-lit sample crops with visibly saturated garment colors, output color names are no longer defaulting to gray/black/blue.
- [ ] Blurry crops still degrade gracefully to base color buckets, not fine-grained guesses.
- [ ] `upper_body` and `lower_body` appear as separate objects in the final JSON for every person track.
- [ ] Vehicle tracks include `vehicle_type` distinguishing at minimum car / bike-scooter / auto rickshaw / bus / truck.
- [ ] `plate_partial` is populated whenever any digits/characters are legible, even partially, and is `null` (not a guess) when nothing is legible.
- [ ] No regression in existing MetadataValidator behavior (unstable tracks still dropped, low-confidence attributes still marked unknown).
- [ ] Fine-tuned detector correctly distinguishes auto rickshaw / e-rickshaw / bike / scooter from car / motorcycle on a held-out validation set from your own footage (not just the training sample).
- [ ] `gender` field is populated with an honest `gender_confidence`, defaulting to `"unknown"` below the configured threshold rather than guessing off clothing alone.
- [ ] Gender predictions are validated against a sample of ground-truth-labeled tracks before relying on the field in production.
