import torch
from ultralytics import YOLO

from config import DETECTION_CONFIDENCE, VIDEO_CLASSES, VIDEO_WIDTH


class VehicleDetector:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = YOLO("yolov8n.pt")
        self.half = self.device == "cuda"
        self.model.to(self.device)
        if self.half:
            self.model.model.half()
        self.class_ids = [
            class_id
            for class_id, class_name in self.model.names.items()
            if class_name in VIDEO_CLASSES
        ]

    def detect_vehicles(self, frame):
        detections = []
        results = self.model.predict(
            frame,
            stream=True,
            device=self.device,
            half=self.half,
            conf=DETECTION_CONFIDENCE,
            imgsz=VIDEO_WIDTH,
            classes=self.class_ids,
            verbose=False,
        )
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf[0].item())
                class_id = int(box.cls[0].item())
                class_name = self.model.names.get(class_id, "unknown")
                if class_name not in VIDEO_CLASSES:
                    continue
                detections.append(
                    {
                        "xyxy": [int(x1), int(y1), int(x2), int(y2)],
                        "confidence": confidence,
                        "class_name": class_name,
                    }
                )
        return detections
