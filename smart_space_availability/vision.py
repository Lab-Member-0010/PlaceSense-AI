"""YOLO inference and occupancy calculations."""

from __future__ import annotations

from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO


def occupancy_status(count: int, capacity: int) -> tuple[str, float | None, int | None]:
    """Calculate a simple status, occupancy percentage, and available capacity."""
    if capacity <= 0:
        return "Count only", None, None
    occupancy = min(count / capacity, 1.0)
    status = "Available" if occupancy < 0.35 else "Moderate" if occupancy <= 0.70 else "Busy"
    return status, occupancy, max(capacity - count, 0)


class OccupancyAnalyzer:
    """Run person detection/tracking and count people inside configured zones."""

    def __init__(self, model_name: str = "yolo11n.pt") -> None:
        self.model_name = model_name
        self.model = YOLO(model_name)

    @staticmethod
    def _point_in_polygon(point: tuple[int, int], polygon: np.ndarray) -> bool:
        return cv2.pointPolygonTest(polygon, point, False) >= 0

    def analyze(self, frame: np.ndarray, zones: list[dict[str, Any]], confidence: float = 0.35) -> tuple[np.ndarray, list[dict[str, Any]], int]:
        """Analyze one frame and return annotated frame, zone summaries, and total people."""
        result = self.model.track(frame, persist=True, classes=[0], conf=confidence, verbose=False)[0]
        annotated = result.plot()
        height, width = frame.shape[:2]
        centers: list[tuple[int, int]] = []
        if result.boxes is not None and result.boxes.xyxy is not None:
            boxes = result.boxes.xyxy.cpu().numpy().astype(int)
            # OpenCV 5 requires native Python numbers for pointPolygonTest arguments.
            centers = [(int((x1 + x2) // 2), int((y1 + y2) // 2)) for x1, y1, x2, y2 in boxes]

        summaries = []
        for zone in zones:
            polygon = np.array([[int(x * width), int(y * height)] for x, y in zone["points"]], dtype=np.int32)
            count = sum(self._point_in_polygon(center, polygon) for center in centers)
            status, occupancy, available = occupancy_status(count, zone["capacity"])
            summaries.append({"name": zone["name"], "count": count, "capacity": zone["capacity"], "status": status, "occupancy": occupancy, "available": available})
            color = (0, 180, 0) if status == "Available" else (0, 165, 255) if status == "Moderate" else (0, 0, 220)
            cv2.polylines(annotated, [polygon], True, color, 3)
            label = f"{zone['name']}: {count}/{zone['capacity']} ({status})" if zone["capacity"] else f"{zone['name']}: {count} ({status})"
            x, y = polygon[0]
            cv2.rectangle(annotated, (x, max(0, y - 32)), (min(width - 1, x + 320), y), color, -1)
            cv2.putText(annotated, label, (x + 6, max(20, y - 9)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        for center in centers:
            cv2.circle(annotated, center, 4, (255, 0, 255), -1)
        return annotated, summaries, len(centers)
