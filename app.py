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
VIDEO_TYPES = ["mp4", "avi", "mov", "mkv"]


@st.cache_resource
def load_analyzer(model_name: str) -> OccupancyAnalyzer:
    """Cache one model per Streamlit process."""
    return OccupancyAnalyzer(model_name)


def simple_rectangle_zone(name: str, capacity: int, x: float, y: float, width: float, height: float) -> list[dict[str, Any]]:
    """Build one normalized rectangular zone from friendly UI controls."""
    right = min(x + width, 1.0)
    bottom = min(y + height, 1.0)
    return [{"name": name.strip() or "Main Area", "capacity": capacity, "points": [[x, y], [right, y], [right, bottom], [x, bottom]]}]


def process_stream(source: Any, analyzer: OccupancyAnalyzer, zones: list[dict[str, Any]], confidence: float, frame_placeholder: Any, metric_placeholder: Any, max_seconds: int) -> None:
    """Process a webcam or video file until it ends or reaches the time limit."""
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        st.error("We could not open this video source. Try another file or run webcam mode locally.")
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
                st.caption(f"{frames / elapsed:.1f} FPS · {total_people} people detected in the latest frame")
                columns = st.columns(min(len(summaries), 4))
                for column, summary in zip(columns, summaries):
                    with column:
                        st.metric(summary["name"], f"{summary['count']} people")
                        if summary["available"] is not None:
                            st.write(f"Available: **{summary['available']} / {summary['capacity']}**")
                        st.write(f"Status: **{summary['status']}**")
        st.success("Analysis complete. You can change the settings and run it again.")
    finally:
        capture.release()


def sidebar_configuration() -> tuple[str, str, list[dict[str, Any]], float, int, Any]:
    """Render controls and return the selected analysis configuration."""
    with st.sidebar:
        st.header("1. Choose input")
        source_mode = st.radio("Analysis source", ["Upload a video", "Use local webcam"], help="Upload a video for the cloud demo. Webcam mode works only when Streamlit runs on the same computer as the camera.")

        st.header("2. Define monitored space")
        zone_mode = st.radio("Zone setup", ["Simple single zone", "Advanced JSON"], label_visibility="collapsed")
        if zone_mode == "Simple single zone":
            zone_name = st.text_input("Zone name", "Main Area")
            capacity = st.number_input("Maximum capacity", min_value=0, value=10, step=1, help="Use 0 if you only want a people count.")
            x = st.slider("Left position", 0.0, 0.8, 0.15, 0.05)
            y = st.slider("Top position", 0.0, 0.8, 0.20, 0.05)
            width = st.slider("Zone width", 0.1, 1.0, 0.70, 0.05)
            height = st.slider("Zone height", 0.1, 1.0, 0.65, 0.05)
            zones = simple_rectangle_zone(zone_name, int(capacity), x, y, width, height)
        else:
            zones_raw = st.text_area("Zones JSON", value=DEFAULT_ZONES, height=250, help="Use normalized coordinates from 0.0 to 1.0.")
            try:
                zones = parse_zones(zones_raw)
            except ValueError as exc:
                st.error(str(exc))
                st.stop()

        with st.expander("Advanced settings"):
            model_name = st.text_input("YOLO model", value="yolo11n.pt", help="The small model is recommended for CPU demos.")
            confidence = st.slider("Detection confidence", 0.05, 0.95, 0.35, 0.05)
            max_seconds = st.slider("Maximum run time (seconds)", 10, 300, 60, 10)

        uploaded = st.file_uploader("Video file", type=VIDEO_TYPES) if source_mode == "Upload a video" else None
    return source_mode, model_name, zones, confidence, max_seconds, uploaded


def main() -> None:
    st.set_page_config(page_title="PlaceSense AI", page_icon="📍", layout="wide", initial_sidebar_state="expanded")
    st.title("PlaceSense AI")
    st.subheader("Smart space availability, made easy to test")
    st.write("Upload a short CCTV-style video or use a local webcam to estimate how busy a monitored area is.")

    with st.expander("How this POC works", expanded=False):
        st.markdown("""
        1. Choose a video or local webcam.
        2. Define the area to monitor and its estimated capacity.
        3. Start analysis and review the people count, availability, and status.

        The result is an estimate based on detected people. It does not detect actual seats, tables, or parking slots yet.
        """)

    source_mode, model_name, zones, confidence, max_seconds, uploaded = sidebar_configuration()

    if source_mode == "Upload a video":
        if uploaded is None:
            st.info("Upload a short MP4, AVI, MOV, or MKV video using the sidebar to begin.")
        else:
            st.success(f"Video ready: **{uploaded.name}** · {uploaded.size / 1024 / 1024:.1f} MB")
    else:
        st.warning("Webcam mode is for local runs only. A cloud deployment cannot access your laptop camera; use video upload for a shared demo.")

    st.divider()
    frame_placeholder = st.empty()
    metric_placeholder = st.empty()
    can_start = uploaded is not None if source_mode == "Upload a video" else True
    start_help = None if can_start else "Upload a video in the sidebar first. The analysis button becomes available when a video is ready."
    if st.button("Start analysis", type="primary", disabled=not can_start, help=start_help, use_container_width=True):
        with st.spinner("Loading the vision model and analyzing the video..."):
            analyzer = load_analyzer(model_name)
            if source_mode == "Use local webcam":
                process_stream(0, analyzer, zones, confidence, frame_placeholder, metric_placeholder, max_seconds)
            else:
                with tempfile.NamedTemporaryFile(suffix=Path(uploaded.name).suffix, delete=True) as temp_file:
                    temp_file.write(uploaded.getbuffer())
                    temp_file.flush()
                    process_stream(temp_file.name, analyzer, zones, confidence, frame_placeholder, metric_placeholder, max_seconds)

    st.divider()
    st.caption("POC estimate only. Do not use this application for medical, safety, access-control, or identity decisions.")


if __name__ == "__main__":
    main()
