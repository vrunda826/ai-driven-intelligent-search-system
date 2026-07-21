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

## Modified files

- `main.py`
  - `base_output_dir` was hardcoded to `D:\projects\AIvision-output` (a path that
    doesn't exist on this machine). Now defaults to
    `C:\Users\Admin\Downloads\ai-driven-intelligent-search-system-main\output`,
    overridable via the `AIVISION_OUTPUT_DIR` env var.
  - Passes `class_name` through to `DeepAttributeExtractor.extract(...)` so
    animal/generic-object attribute extraction can use the detector's class name.

- `configs/config.yaml`
  - `video.input_path` / `video.camera_info_path` pointed at nonexistent
    `D:/projects/AIVisionInput/...` paths. Updated to the trial video and the new
    `configs/camera_info.json`.
  - `detection.classes` changed from `[0, 2, 3, 5, 7]` (person/car/motorcycle/bus/truck
    only) to `null`, so the detector now picks up every COCO class (animals, general
    objects/"things" included), per the goal of describing everything in frame.

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

- `src/metadata/metadata_validator.py`
  - The confidence-threshold / "unknown" fallback logic only handled `person` vs.
    `vehicle`. Added the same handling for `animal` and `object` categories so
    low-confidence species/object-type/color values are honestly marked `"unknown"`
    instead of silently keeping an unvalidated guess.

## Environment (not code changes, but required to run)

- Installed `supervision` and confirmed `easyocr`/`torch`/`ultralytics`/`transformers`
  were already present in the `C:\Users\Admin\python.exe` (3.11) environment used to
  run the pipeline.

## Verification

- Ran the full pipeline four times end-to-end against
  `C:\Users\Admin\Videos\Screen Recordings\Screen Recording 2026-07-21 141855.mp4`
  (outputs in `output/run_0001` .. `run_0004`).
- Unit-tested the new animal/object code paths with synthetic crops (the trial video
  only contained person/car/truck/motorcycle/bus, no animals or generic objects
  survived track-stability filtering), confirming correct schema, description text,
  and CSV export for those categories.
