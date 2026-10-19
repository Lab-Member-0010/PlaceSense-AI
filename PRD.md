# Smart Space Availability POC — Product Requirements Document

**Status:** POC implementation
**Date:** 2026-10-19
**Owner:** Project team

## 1. Product summary

This proof of concept demonstrates a cost-free, local computer-vision application that uses a laptop webcam or video file to estimate occupancy inside configurable zones. It is the first slice of a broader platform for clinics, parking areas, restaurants, cafés, and malls.

The POC answers one practical question:

> How much space is currently available in a monitored area?

It must run on a laptop without paid cloud services. It is an experiment and must not be treated as a production safety, medical, or access-control system.

## 2. Goals

- Run locally with Python and a laptop webcam.
- Detect and track people in video using Ultralytics YOLO.
- Let the operator define one or more polygonal zones.
- Count people currently inside each zone.
- Estimate available capacity from a configured zone capacity.
- Show annotated video and simple status labels: Available, Moderate, or Busy.
- Support a recorded video fallback when a webcam is unavailable.
- Keep all video processing local by default.
- Produce a small, understandable codebase that can become the foundation for a GitHub repository.

## 3. Non-goals for this POC

- Facial recognition, identity tracking, or license-plate recognition.
- Patient, customer, or employee identification.
- Automatic seat/table/parking-space discovery.
- Reservations, notifications, authentication, or multi-tenant deployment.
- Production-grade accuracy guarantees.
- Long-term forecasting. The POC only provides a current status and a heuristic recommendation.

## 4. Target users

- Project developers testing the concept.
- A site operator configuring a camera and zones.
- A stakeholder evaluating whether occupancy information is useful.

## 5. User stories

1. As an operator, I can choose a laptop webcam or upload a video.
2. As an operator, I can define named zones and their capacities without changing Python code.
3. As an operator, I can see people counted in each zone over the annotated video.
4. As an operator, I can see estimated available capacity and a human-readable status.
5. As a stakeholder, I can understand the system's current estimate without viewing raw detection details.

## 6. Functional requirements

### Input

- Webcam index `0` by default.
- Optional uploaded video file.
- A configurable inference confidence threshold.
- A configurable maximum runtime for live webcam processing.

### Zone configuration

- Zones are named polygons expressed in normalized coordinates from `0.0` to `1.0`.
- Each zone has a capacity.
- The default configuration contains one central demonstration zone.
- The application validates malformed JSON and out-of-range coordinates.

### Vision pipeline

- Use an Ultralytics YOLO person detector.
- Use persistent multi-object tracking for consecutive frames.
- Count a person when the center point of their bounding box is inside a zone.
- Draw detections, track IDs, zones, counts, and status on the frame.

### Dashboard

- Live annotated frame.
- Total people detected in the frame.
- Per-zone count, capacity, available capacity, occupancy percentage, and status.
- Processing FPS and latest update time.
- A recommendation based on occupancy percentage.

## 7. Status rules

- `Available`: occupancy below 35%.
- `Moderate`: occupancy from 35% through 70%.
- `Busy`: occupancy above 70%.
- If a zone has no configured capacity, show count but do not claim availability.

These thresholds are placeholders and must be calibrated with real observations before any operational use.

## 8. Technical design

```text
Webcam or uploaded video
        ↓
OpenCV frame capture
        ↓
Ultralytics YOLO detection + tracking
        ↓
Normalized polygon zone counting
        ↓
Capacity/status calculation
        ↓
Streamlit dashboard
```

Initial stack:

- Python 3.10+ recommended.
- Ultralytics YOLO.
- OpenCV.
- Streamlit.
- NumPy.

No database or external API is required for the POC.

## 9. Privacy and safety requirements

- Process video locally by default.
- Do not save raw video or face embeddings.
- Do not implement facial recognition or re-identification.
- Display a clear disclaimer that the result is an estimate.
- Do not use the POC for medical decisions, emergency response, surveillance decisions, or access control.

## 10. Acceptance criteria

- `pip install -r requirements.txt` installs the dependencies.
- `streamlit run app.py` starts the application.
- The application can open a webcam or uploaded video.
- At least one configured zone produces a count.
- The annotated output shows the zone and detections.
- The dashboard displays available capacity and status.
- A malformed zone configuration produces a readable validation error.
- The code passes Python compilation checks.

## 11. Future phases

1. Add an interactive polygon drawing tool.
2. Add parking-slot mode with fixed parking polygons.
3. Add historical time-series storage and charts.
4. Add confidence-aware smoothing and camera health monitoring.
5. Add location-specific profiles for clinics, restaurants, and malls.
6. Evaluate accuracy against manually labeled test clips.
7. Design production privacy, security, licensing, and deployment controls.
