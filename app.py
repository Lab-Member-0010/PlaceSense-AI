"""Streamlit operator interface for the Smart Space Availability POC."""

from __future__ import annotations

import tempfile
import time
from pathlib import Path
from typing import Any

import cv2
import streamlit as st

from smart_space_availability.config import parse_zones
from smart_space_availability.vision import OccupancyAnalyzer


ROOT = Path(__file__).parent
DEFAULT_ZONES = (ROOT / "zones.json").read_text(encoding="utf-8")


@st.cache_resource
def load_analyzer(model_name: str) -> OccupancyAnalyzer:
    """Cache one model per Streamlit process."""
    return OccupancyAnalyzer(model_name)


def process_stream(source: Any, analyzer: OccupancyAnalyzer, zones: list[dict[str, Any]], confidence: float, frame_placeholder: Any, metric_placeholder: Any, max_seconds: int) -> None:
    """Process a webcam or video file until it ends or reaches the time limit."""
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        st.error("Could not open the selected video source.")
        return
    started = time.time()
    frames = 0
    try:
        while time.time() - started < max_seconds:
            ok, frame = capture.read()
            if not ok:
                break
            annotated, summaries, total_people = analyzer.analyze(frame, zones, confidence)
            frame_placeholder.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)
            frames += 1
            elapsed = max(time.time() - started, 0.001)
            with metric_placeholder.container():
                st.caption(f"People in frame: {total_people} · Processing: {frames / elapsed:.1f} FPS · {time.strftime('%H:%M:%S')}")
                columns = st.columns(min(len(summaries), 4))
                for column, summary in zip(columns, summaries):
                    with column:
                        st.metric(summary["name"], f"{summary['count']} people")
                        if summary["available"] is not None:
                            st.write(f"Available: **{summary['available']} / {summary['capacity']}**")
                        st.write(f"Status: **{summary['status']}**")
        st.success("Stream finished. Start it again to process more frames.")
    finally:
        capture.release()


def main() -> None:
    st.set_page_config(page_title="Smart Space Availability POC", page_icon="📍", layout="wide")
    st.title("Smart Space Availability POC")
    st.caption("Local occupancy estimation using a webcam/video and Ultralytics YOLO.")

    with st.sidebar:
        st.header("Configuration")
        model_name = st.text_input("YOLO model", value="yolo11n.pt")
        confidence = st.slider("Detection confidence", 0.05, 0.95, 0.35, 0.05)
        max_seconds = st.slider("Maximum run time (seconds)", 10, 300, 60, 10)
        zones_raw = st.text_area("Zones JSON", value=DEFAULT_ZONES, height=260)
        uploaded = st.file_uploader("Optional video file", type=["mp4", "avi", "mov", "mkv"])

    try:
        zones = parse_zones(zones_raw)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    st.info("Tip: for the first test, stand inside the default central zone. The model counts people, not physical seats or parking slots.")
    frame_placeholder = st.empty()
    metric_placeholder = st.empty()
    if st.button("Start analysis", type="primary"):
        with st.spinner("Loading model and starting video analysis..."):
            analyzer = load_analyzer(model_name)
            if uploaded is None:
                process_stream(0, analyzer, zones, confidence, frame_placeholder, metric_placeholder, max_seconds)
            else:
                with tempfile.NamedTemporaryFile(suffix=Path(uploaded.name).suffix, delete=True) as temp_file:
                    temp_file.write(uploaded.getbuffer())
                    temp_file.flush()
                    process_stream(temp_file.name, analyzer, zones, confidence, frame_placeholder, metric_placeholder, max_seconds)

    st.divider()
    st.caption("POC only: estimates may be inaccurate. Do not use this application for medical, safety, access-control, or identity decisions.")


if __name__ == "__main__":
    main()
