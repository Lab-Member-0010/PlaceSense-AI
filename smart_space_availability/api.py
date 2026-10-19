"""FastAPI service for local and future client integrations."""

from __future__ import annotations

from functools import lru_cache

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, Query, UploadFile

from .config import parse_zones
from .vision import OccupancyAnalyzer


app = FastAPI(title="Smart Space Availability API", version="0.1.0")


@lru_cache(maxsize=2)
def get_analyzer(model_name: str) -> OccupancyAnalyzer:
    return OccupancyAnalyzer(model_name)


@app.get("/health")
def health() -> dict[str, str]:
    """Return service health without loading the model."""
    return {"status": "ok", "service": "smart-space-availability"}


@app.post("/analyze/frame")
async def analyze_frame(
    file: UploadFile = File(...),
    zones: str = Query(..., description="JSON object containing a zones list."),
    model: str = Query("yolo11n.pt", description="Ultralytics model name or path."),
    confidence: float = Query(0.35, ge=0.05, le=0.95),
) -> dict:
    """Analyze one uploaded image and return aggregate occupancy results."""
    try:
        zone_config = parse_zones(zones)
        image_bytes = await file.read()
        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("The uploaded file is not a readable image.")
        _, summaries, total_people = get_analyzer(model).analyze(image, zone_config, confidence)
        return {"total_people": total_people, "zones": summaries}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
