from deep_sort_realtime.deepsort_tracker import DeepSort


class ObjectTracker:
    def __init__(self):
        self.tracker = DeepSort(max_age=30, n_init=3)

    def update(self, detections, frame=None):
        formatted = []
        for det in detections:
            x1, y1, x2, y2 = det["xyxy"]
            formatted.append(
                [
                    [x1, y1, x2 - x1, y2 - y1],
                    det["confidence"],
                    det["class_name"],
                ]
            )

        tracks = self.tracker.update_tracks(formatted, frame=frame)
        tracked_objects = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            tlbr = track.to_tlbr()
            conf = 0.0
            if hasattr(track, 'get_det_conf'):
                det_conf = track.get_det_conf()
                conf = float(det_conf) if det_conf is not None else 0.0
            
            tracked_objects.append(
                {
                    "id": track.track_id,
                    "bbox": [int(tlbr[0]), int(tlbr[1]), int(tlbr[2]), int(tlbr[3])],
                    "class_name": track.det_class or "unknown",
                    "confidence": conf,
                }
            )
        return tracked_objects
