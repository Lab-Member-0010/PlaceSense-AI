# Smart Space Availability POC

A local, cost-free occupancy estimation demo using a laptop webcam or uploaded video, Ultralytics YOLO, headless OpenCV, FastAPI, and Streamlit.

## Run locally

The webcam is accessed by the computer running Streamlit. Run the application on the laptop if you want to use the laptop's built-in camera.

Use a Python virtual environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

In a second terminal, start the API service when you need the backend endpoint:

```bash
source .venv/bin/activate
uvicorn smart_space_availability.api:app --reload
```

The API exposes `GET /health` and `POST /analyze/frame`. The Streamlit UI uses the same shared vision module directly for the local webcam workflow; the API is the integration boundary for future web or mobile clients.

The first run may download the small `yolo11n.pt` model. This is the only model download required by the POC.

## Try it

1. Start the application.
2. Choose **Upload a video** in the sidebar for a cloud demo.
3. Upload a short MP4, AVI, MOV, or MKV clip.
4. Set the zone name, capacity, and rectangle position using the simple controls.
5. Choose the object types to detect. People are selected by default; vehicles, chairs, and dining tables are also available.
6. Click **Start analysis**.

For a local run, choose **Use local webcam**. The webcam must be connected to the computer running Streamlit.

## Zone configuration

Zones use normalized coordinates, where `(0, 0)` is the top-left and `(1, 1)` is the bottom-right:

```json
{
  "zones": [
    {
      "name": "Waiting Area",
      "capacity": 12,
      "points": [[0.1, 0.2], [0.9, 0.2], [0.9, 0.85], [0.1, 0.85]]
    }
  ]
}
```

## Scope and limitations

The default model detects common COCO categories such as people, vehicles, chairs, and dining tables. Detection is not the same as physical seat/table availability or parking-slot occupancy. This is a local experiment and should not be used for medical decisions, emergency response, access control, identity, or surveillance decisions.
