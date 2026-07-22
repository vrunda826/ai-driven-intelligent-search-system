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
- `configs/camera_info.json` — camera metadata (id, resolution, fps) since none
  existed in the repo. Currently set to `central_bus_depot_entry_gate` / 1920x1080 /
  20fps, matching the real footage in use (see Verification below); was
  `trial_cam_01` / 1092x624 / 30fps while testing against the placeholder trial
  screen-recording input.
- `src/attributes/vlm_captioner.py` — `VLMCaptioner` wraps Microsoft's
  Florence-2-base vision-language model to produce an open-ended, free-text
  description of a track's best keyframe (color, shape, pose, background context,
  visible text, etc.) — not bounded by the heuristic attribute schema in
  `deep_attribute_extractor.py`, which can only ever report what it was explicitly
  coded to look for. Chosen over larger VLMs (LLaVA/Qwen-VL) because this machine
  is CPU-only and Florence-2-base (~0.23B params) is small enough to run at
  reasonable speed there. Runs once per track (on the single best keyframe), not
  once per keyframe, to keep cost down.
  Current default: `num_beams=2`, `max_new_tokens=150`. Went through several rounds
  of retuning against measured timings (see Verification below) after the user
  reported the captions were missing/getting details wrong: the Florence-2 model
  card's own recommended `num_beams=3`/256 tokens measured at ~60-75s/crop on this
  CPU-only machine once `use_cache=False` was forced (see below), which is
  impractical across a whole video's tracks; `num_beams=1`/100 tokens measured at
  ~10-20s/crop but produced more truncated/greedy-decoding-error captions (the
  original quality complaint); `num_beams=2`/150 tokens landed at ~29s/crop
  sequentially, judged the best available tradeoff on this hardware.
- `src/pipeline/__init__.py`, `src/pipeline/parallel_extraction.py` — added to
  parallelize the per-track feature-extraction stage across worker processes, then
  **found not to help** on this machine and left unused by default
  (`performance.num_workers: 1`) — kept in the repo since it's still correct,
  tested code, and would matter on higher-core-count or GPU hardware. See
  Verification below for why it doesn't help here.

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
  - The whole per-track feature-extraction loop (embeddings, VLM caption, heuristic
    attributes) was restructured around two additions, both driven by the user
    asking for reruns on the same input to be faster:
    1. **Per-video track-feature cache** (`{cache_key}_track_features.json` in
       `output/cache/`, alongside the pre-existing detections cache) — on a rerun
       against the identical video, any track already in this cache skips model
       inference entirely (embeddings/VLM/attributes are loaded straight from the
       cache instead of recomputed). First run populates it; every subsequent run
       on that same video is near-instant for this stage.
    2. **Incremental checkpointing** — the cache is flushed to disk every 10
       tracks (not just once at the end), because this stage runs for hours and
       we hit two real interruptions during development (an 18+ hour run that
       outlived a lost session, and a run killed mid-way to fix the parallelism
       issue below) that would otherwise have thrown away all progress made so far.
    3. `performance.num_workers > 1` routes pending tracks through a
       `ProcessPoolExecutor` (`src/pipeline/parallel_extraction.py`) instead of a
       plain loop — implemented, tested, and currently left disabled by default
       (see config + Verification notes) since it didn't actually speed anything
       up on this CPU-only 6-core machine.

- `configs/config.yaml`
  - `video.input_path` / `video.camera_info_path` pointed at nonexistent
    `D:/projects/AIVisionInput/...` paths. Updated to the new `configs/camera_info.json`,
    and `input_path` currently points at the real footage
    `C:/Users/Admin/Downloads/Export__Central Bus Depo-Entry Gate Platform Area_...avi`
    (was pointed at a placeholder trial screen-recording earlier on).
  - `detection.classes` changed from `[0, 2, 3, 5, 7]` (person/car/motorcycle/bus/truck
    only) to `null`, so the detector now picks up every COCO class (animals, general
    objects/"things" included), per the goal of describing everything in frame.
  - Added `models.use_vlm_caption` (bool) and `models.vlm_model_name`
    (`microsoft/Florence-2-base`) to enable/configure the new VLM captioning stage.
  - Added `performance.num_workers` (currently `1`, i.e. sequential) for the
    per-track extraction stage. Tested at `2` on this 6-core CPU-only machine and
    measured **no real speedup** — Florence-2's inference is matrix-multiply-heavy
    and already saturates all cores via multi-threaded BLAS within a single
    process, so N concurrent processes just divide the same fixed core budget
    rather than adding capacity. Capping each worker's thread count
    (`OMP_NUM_THREADS`/`MKL_NUM_THREADS`/etc., see `parallel_extraction.py`) to
    force genuine separation made individual tasks slower with no net gain either.
    Left at `1`; worth revisiting only with a GPU or a much higher core count.

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
     which crashes under the new `Cache` object format → originally worked around
     by passing `use_cache=False` to `generate(...)` (recomputes each decoding step
     instead of caching, correct but slow). **Root-caused and properly fixed in
     Round 3 below** — see that section for the real fix, which restores caching
     instead of disabling it.

## Verification

- Ran the full pipeline four times end-to-end against
  `C:\Users\Admin\Videos\Screen Recordings\Screen Recording 2026-07-21 141855.mp4`
  (outputs in `output/run_0001` .. `run_0004`).
- Unit-tested the new animal/object code paths with synthetic crops (the trial video
  only contained person/car/truck/motorcycle/bus, no animals or generic objects
  survived track-stability filtering), confirming correct schema, description text,
  and CSV export for those categories.
- Standalone-tested `VLMCaptioner` on real crops from `run_0004` after the
  `use_cache=False` fix — captions were detailed and distinct per crop, e.g. "The
  image is a close-up of the rear end of a white car... the license plate clearly
  visible... taken from a low angle", correctly picking up color, vehicle shape,
  motion blur, and background context/signage that the heuristic pipeline's fixed
  schema doesn't capture.
- First full-pipeline attempt with the original `num_beams=3`/`max_new_tokens=256`
  settings (`run_0005`) was left running against the trial video and reached
  ~60s/track; it was still running 18+ hours later when the harness lost track of
  the session, and was killed manually (`run_0005` has no `metadata.json` — no
  usable output). This is what drove the beam=1/100-token retuning above.
- Ran the retuned (beam=1/100-token) pipeline end-to-end against real footage,
  `Export__Central Bus Depo-Entry Gate Platform Area_...avi` (5 min, 1920x1080,
  20fps, 6001 frames) — output in `output/run_0006/`. Detection/tracking produced
  639 candidate tracks; 369 survived `MetadataValidator`'s stability filtering
  (330 person, 37 bus, 2 car). Total wall-clock: ~2h50m (mostly the per-track
  VLM captioning phase at ~10-18s/track).
  - All 369 records have a populated `vlm_description` field.
  - Spot-checked person and bus records: the VLM caption surfaced concrete detail
    the heuristic `description`/`appearance` fields missed entirely — a hat with a
    wide brim and a red shirt stripe on a person the heuristics only reported as
    "lavender jeans"; and the livery text **"OBSRTC"** painted on a bus the
    heuristics only reported as "navy blue bus". This is the concrete case for
    running both: the heuristics are fast/structured/always-on, the VLM caption
    catches whatever they weren't coded to look for.
  - Caveat observed: `vlm_description` is genuinely open-ended text, so it inherits
    the usual VLM risks — occasional truncation mid-sentence at the 100-token
    budget, and occasional speculative/odd reads of cluttered backgrounds (one bus
    caption trailed off into "there is a pink coffin-like..." describing something
    in a crowd, almost certainly a misread rather than a real object). Treat
    `vlm_description` as a supplementary human-readable hint, not a validated
    field the way `appearance`/`vehicle`/`animal`/`object` are.

### Round 2: accuracy complaints + speed retuning

User feedback on `run_0006`: VLM captions still missing detail / getting some
things wrong, some track IDs "missing" (this turned out to be intentional
`MetadataValidator` stability filtering — 639 candidates, 369 kept — not a bug;
`tracking.min_observations`/`min_track_duration_sec` in config.yaml control it),
and reruns on the same input should be faster.

- Bumped to `num_beams=3`/`max_new_tokens=150` for quality. Standalone-tested on
  6 real crops: measured **~74.5s/track** (223.5s / 3 tracks-per-worker across 2
  parallel workers) — ~4x slower than the beam=1 setting, worse than the ~1.5-2x
  originally estimated. Projected to ~6.5hrs for the full 639-track video even
  parallelized — worse than `run_0006`'s 2h50m, so not shipped.
- Retuned down to `num_beams=2`/`max_new_tokens=150`. Standalone-tested on 5 real
  crops: measured **~29.3s/track** sequential — a reasonable middle ground (better
  captions than beam=1, ~1.6x its cost rather than beam=3's ~4x).
- Built parallel per-track extraction (`src/pipeline/parallel_extraction.py`,
  `ProcessPoolExecutor` with a model-loading initializer) to offset the beam=2 cost
  via CPU parallelism (6 physical cores, no hyperthreading, ~6-7GB RAM free at the
  time). Standalone-tested on 6 real crops with `num_workers=2`: **~37-39s/track**
  wall-clock either with or without capping each worker's BLAS thread count —
  effectively no faster than running sequentially. Root cause: Florence-2's
  generate() is matrix-multiply-bound and already saturates all 6 cores via
  multi-threaded BLAS in a single process; splitting into concurrent processes
  divides the same fixed core budget rather than adding capacity, so there's no
  parallelism to exploit here (this only helps workloads that are single-threaded
  or I/O-bound, which this mostly isn't). Confirmed by watching a live full-pipeline
  run settle at ~30-33s/track cumulative with `num_workers=2` — matching the
  single-process rate, not half of it. `performance.num_workers` left at `1`
  as a result; the code path still exists and is exercised (tested working,
  correct results) for hardware where it would actually help.
- Added incremental cache checkpointing (every 10 tracks) after two runs were
  lost to interruptions during this investigation (the original beam=3/256-token
  attempt ran unattended for 18+ hours before the harness lost the session and it
  had to be killed with no output at all; a beam=3-with-parallelism attempt was
  killed mid-run once the poor parallelism scaling was discovered) — previously
  the per-track cache was only written once at the very end, so an interruption
  anywhere in a multi-hour run threw away all completed work.
- Interim settings shipped (superseded below): `num_beams=2`, `max_new_tokens=150`,
  `performance.num_workers=1`, `use_cache=False`. Estimated ~29s/track x 639
  tracks ≈ 5.2hrs for a first run against the bus depot video.

### Round 3: actually fixing the speed problem (real KV-cache fix)

User pushed back on accepting the ~5.2hr estimate as a tradeoff ("so how can we
fix it") instead of just living with it, prompting a proper root-cause dig into
*why* `use_cache=True` crashed, rather than continuing to work around it.

- Traced the crash: `transformers` 4.57.6's `generate()` now wraps
  `past_key_values` in an `EncoderDecoderCache` object by default. Florence-2's
  own (unmaintained, `trust_remote_code=True`) attention layers never got updated
  for this — they still read/write the old plain tuple format directly. Confirmed
  via a debug harness that the `EncoderDecoderCache`'s `get_seq_length()` stayed
  `0` across every decoding step (Florence-2's layers were never actually writing
  into it), and `prepare_inputs_for_generation` crashed trying to index
  `past_key_values[0][0].shape` on a `None` sub-entry.
- Real fix: `transformers` decides whether to build that modern `Cache` wrapper by
  calling `model._supports_default_dynamic_cache()`. Monkeypatching this
  classmethod to return `False` on `type(self.model.language_model)` (inside
  `VLMCaptioner.__init__`) tells `transformers` to fall back to the legacy
  `None`/tuple protocol instead — which Florence-2's own layers actually
  implement correctly. This restores **real, working KV caching** without
  touching Florence-2's own modeling code at all.
  - `describe()` now passes `use_cache=self._cache_patch_applied` (`True` when
    the patch succeeds) instead of always `False`.
- Verified correctness before trusting it: ran the exact same crop through both
  `use_cache=False` and the patched `use_cache=True` path — **byte-for-byte
  identical caption text** both times, confirming the cache fix changes nothing
  about the output, only the compute cost.
  - Also confirmed with `generation flags ... early_stopping` warnings unrelated
    to this fix and safe to ignore.
- Benchmarked cleanly (no competing processes) on 8 real crops from `run_0006` at
  the shipped `num_beams=2`/`max_new_tokens=150` settings: **7.2s/track average**
  (individual crops ranged 6.2s-8.3s), versus ~29.3s/track measured previously
  under `use_cache=False` — **roughly a 4x speedup**, all from restoring real
  caching rather than any quality tradeoff.
- Final settings shipped: `num_beams=2`, `max_new_tokens=150`,
  `performance.num_workers=1`, real KV caching enabled via the patch above.
  Revised estimate for the full 639-track bus depot video: ~7.2s/track x 639
  ≈ **75-80 minutes** for the VLM captioning stage (down from the earlier
  ~5.2hr estimate), plus detection/tracking time. Every subsequent run against
  that same video still skips the extraction stage entirely via the
  track-feature cache regardless of this change.
  Full-pipeline run in progress at the time this file was last updated —
  check `output/run_0009/` (or later) for the final result once it completes.
- Live full-pipeline run (`run_0009`, 599 pending tracks after the track-feature
  cache skipped already-computed ones) is tracking at ~11.5-12s/track, not the
  isolated 7.2s/track benchmark figure above — expected, since this stage also
  runs CLIP + Re-ID embedding extraction and the heuristic
  `DeepAttributeExtractor` per keyframe on top of the one VLM caption call per
  track, none of which the standalone benchmark measured. Revised ETA for this
  run: ~2 hours total.
