# Build Progress

## 2026-10-19 — Initial POC

### Completed

- Defined the first POC scope in `PRD.md`.
- Chosen a local Python + Streamlit application so the experiment requires no paid services.
- Chosen Ultralytics YOLO person detection and tracking as the inference layer.
- Designed normalized polygon zones so the same configuration can be reused across video resolutions.
- Added webcam and uploaded-video input requirements.
- Refactored the code into a `smart_space_availability` Python package.
- Added a FastAPI backend with health and single-frame analysis endpoints.
- Kept Streamlit as the local operator interface using the shared analyzer module.

### In progress

- Implemented the Streamlit application.
- Added zone validation, occupancy calculations, visualization, webcam input, uploaded-video input, and runtime controls.

### Verification

- `python3 -m py_compile app.py` passed.
- Python compilation passed for the application package and API modules.
- The current environment does not have the runtime dependencies installed, so the Streamlit UI and model inference still require a local dependency installation.

### Compatibility fix

- Fixed OpenCV 5 `pointPolygonTest` compatibility by converting NumPy coordinate values to native Python integers.
- Added `lap` to `requirements.txt` so Ultralytics tracking dependencies are installed before runtime.

### Handoff

- Added `README.md` with setup, run, and zone-configuration instructions.
- Added `requirements.txt` for the free local stack.

### Validation planned

- Python compilation check.
- Dependency/import smoke check where the local environment permits it.
- Manual run with a webcam or short video after dependencies are installed.

### Known limitations

- The default model may need to be downloaded once when first run.
- CPU inference may be slow on some laptops.
- Zone capacities and status thresholds are demonstration values.
- This version counts people, not actual seats, tables, or parking slots.
