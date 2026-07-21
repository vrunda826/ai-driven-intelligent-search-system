# Changes

Git is not installed on this machine, so these changes could not be committed/pushed.
This file documents what was modified in the `AIVision` folder so it can be reviewed
and committed manually once git is available.

## New files

- `src/embeddings/__init__.py`
- `src/embeddings/clip_embedder.py` — CLIP (`transformers`) image embedder used for
  semantic search embeddings. This module was imported by `main.py` but did not exist
  in the repo; added a working implementation.
- `src/embeddings/reid_extractor.py` — ImageNet-pretrained ResNet18 (torchvision)
  appearance/re-id embedding extractor. Same situation as above — imported but missing.
- `configs/camera_info.json` — trial camera metadata (id, resolution, fps) since none
  existed in the repo.
- `src/attributes/vlm_captioner.py` — `VLMCaptioner` wraps Microsoft's
  Florence-2-base vision-language model to produce an open-ended, free-text
  description of a track's best keyframe (color, shape, pose, background context,
  visible text, etc.) — not bounded by the heuristic attribute schema in
  `deep_attribute_extractor.py`, which can only ever report what it was explicitly
  coded to look for. Chosen over larger VLMs (LLaVA/Qwen-VL) because this machine
  is CPU-only and Florence-2-base (~0.23B params) is small enough to run at
  reasonable speed there. Runs once per track (on the single best keyframe), not
  once per keyframe, to keep cost down.

## Modified files

- `main.py`
  - `base_output_dir` was hardcoded to `D:\projects\AIvision-output` (a path that
    doesn't exist on this machine). Now defaults to
    `C:\Users\Admin\Downloads\ai-driven-intelligent-search-system-main\output`,
    overridable via the `AIVISION_OUTPUT_DIR` env var.
  - Passes `class_name` through to `DeepAttributeExtractor.extract(...)` so
    animal/generic-object attribute extraction can use the detector's class name.
  - Instantiates `VLMCaptioner` (gated by `models.use_vlm_caption`) and calls
    `.describe(best_crop)` once per track alongside the existing CLIP/Re-ID
    embedding calls, storing results in `vlm_descriptions_dict` and passing it
    through to `MetadataGenerator.finalize(...)`.

- `configs/config.yaml`
  - `video.input_path` / `video.camera_info_path` pointed at nonexistent
    `D:/projects/AIVisionInput/...` paths. Updated to the trial video and the new
    `configs/camera_info.json`.
  - `detection.classes` changed from `[0, 2, 3, 5, 7]` (person/car/motorcycle/bus/truck
    only) to `null`, so the detector now picks up every COCO class (animals, general
    objects/"things" included), per the goal of describing everything in frame.
  - Added `models.use_vlm_caption` (bool) and `models.vlm_model_name`
    (`microsoft/Florence-2-base`) to enable/configure the new VLM captioning stage.

- `src/attributes/deep_attribute_extractor.py`
  - Added `ANIMAL_CLASS_NAMES` and expanded `VEHICLE_CLASS_NAMES` (added bicycle,
    airplane, train, boat).
  - `extract()` now dispatches to person / vehicle / animal / generic-object
    extraction instead of returning `{}` for anything that isn't person/vehicle.
  - Added `_extract_animal_attributes()` (species + dominant color) and
    `_extract_generic_object_attributes()` (object type + dominant color).
  - Fixed a pre-existing bug where the vehicle body-type fallback (`else` branch)
    always returned `"truck"` regardless of actual vehicle type.

- `src/metadata/metadata_generator.py`
  - Added a `_categorize()` helper bucketing each detector class into
    `person` / `vehicle` / `animal` / `object`.
  - `finalize()` previously only branched `person` vs. "everything else treated as a
    vehicle" — animals/objects were being forced into the vehicle schema. Now branches
    into four proper categories, each producing its own top-level field:
    `upper_body`/`lower_body` (person), `vehicle`, `animal`, `object`. Added a
    `category` field to every record.
  - `_build_rich_description()` now generates a category-appropriate narrative for
    animals and generic objects (previously only person/vehicle sentences existed).
  - Fixed "A orange dog" → "An orange dog" style grammar (a pre-existing issue in the
    vehicle sentence too) via a new `_article_for()` helper.
  - `save_csv()` gained `category` and `detected_type` columns (unified species /
    vehicle_type / object_type / "person" column), and `color` now falls back through
    vehicle → animal → object → person appearance.
  - `finalize()` now accepts a `vlm_descriptions_dict` argument and adds a
    `vlm_description` field to every record (also added as a CSV column) —
    the free-text VLM caption, kept alongside (not replacing) the existing
    rule-based `description` field for comparison.

- `src/metadata/metadata_validator.py`
  - The confidence-threshold / "unknown" fallback logic only handled `person` vs.
    `vehicle`. Added the same handling for `animal` and `object` categories so
    low-confidence species/object-type/color values are honestly marked `"unknown"`
    instead of silently keeping an unvalidated guess.

## Environment (not code changes, but required to run)

- Installed `supervision` and confirmed `easyocr`/`torch`/`ultralytics`/`transformers`
  were already present in the `C:\Users\Admin\python.exe` (3.11) environment used to
  run the pipeline.
- Installed `timm` and `einops` (Florence-2-base's vision backbone dependencies).
- Florence-2-base's custom modeling code (`trust_remote_code=True`, unmaintained
  since mid-2024) is incompatible with the installed `transformers` 4.57.6 in two
  ways, both worked around inside `vlm_captioner.py` without touching the globally
  installed `transformers` version (to avoid risking regressions in the
  already-working detection/CLIP/Re-ID code paths):
  1. Model construction checks `self._supports_sdpa`, an attribute recent
     `transformers` versions no longer set by default → fixed by passing
     `attn_implementation="eager"` to `from_pretrained(...)`.
  2. `generate()`'s custom `prepare_inputs_for_generation` indexes
     `past_key_values[0][0].shape` assuming the old tuple-based KV-cache format,
     which crashes under the new `Cache` object format → fixed by passing
     `use_cache=False` to `generate(...)` (recomputes each decoding step instead of
     caching; slower per call, but this only runs once per track).

## Verification

- Ran the full pipeline four times end-to-end against
  `C:\Users\Admin\Videos\Screen Recordings\Screen Recording 2026-07-21 141855.mp4`
  (outputs in `output/run_0001` .. `run_0004`).
- Unit-tested the new animal/object code paths with synthetic crops (the trial video
  only contained person/car/truck/motorcycle/bus, no animals or generic objects
  survived track-stability filtering), confirming correct schema, description text,
  and CSV export for those categories.
- Standalone-tested `VLMCaptioner` on 3 real crops from `run_0004` after the
  `use_cache=False` fix — captions were detailed and distinct per crop, e.g. "The
  image is a close-up of the rear end of a white car... the license plate clearly
  visible... taken from a low angle", correctly picking up color, vehicle shape,
  motion blur, and background context/signage that the heuristic pipeline's fixed
  schema doesn't capture.
- Full pipeline run with `use_vlm_caption: true` was in progress at the time this
  file was last updated (Florence-2 with `use_cache=False` is slow — no KV caching
  means each of the ~5-10s-per-track calls recomputes the full sequence at every
  decoding step); confirm `output/run_0005/metadata/metadata.json` has a populated
  `vlm_description` field per track once it completes.
