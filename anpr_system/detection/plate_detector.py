import os

from ultralytics import YOLO

from config import PLATE_CONFIDENCE, PLATE_MODEL_PATH


class PlateDetector:
    def __init__(self):
        self.use_model = False
        if PLATE_MODEL_PATH and os.path.exists(PLATE_MODEL_PATH):
            self.model = YOLO(PLATE_MODEL_PATH)
            self.use_model = True
        else:
            self.model = None

    def detect_plate(self, frame, vehicle_box):
        x1, y1, x2, y2 = [int(v) for v in vehicle_box]
        if x2 <= x1 or y2 <= y1:
            return [x1, y1, x2, y2]

        roi = frame[y1:y2, x1:x2]
        if self.use_model:
            results = self.model.predict(
                roi,
                conf=PLATE_CONFIDENCE,
                imgsz=320,
                verbose=False,
            )
            if results and results[0].boxes is not None and len(results[0].boxes) > 0:
                best = results[0].boxes[0]
                rx1, ry1, rx2, ry2 = best.xyxy[0].tolist()
                return [
                    int(x1 + rx1),
                    int(y1 + ry1),
                    int(x1 + rx2),
                    int(y1 + ry2),
                ]

        return self._fallback_plate_box(vehicle_box)

    def _fallback_plate_box(self, vehicle_box):
        x1, y1, x2, y2 = [int(v) for v in vehicle_box]
        width = x2 - x1
        height = y2 - y1
        plate_y1 = y1 + int(height * 0.55)
        plate_y2 = y2
        plate_x1 = x1 + int(width * 0.15)
        plate_x2 = x2 - int(width * 0.15)
        return [plate_x1, plate_y1, plate_x2, plate_y2]
