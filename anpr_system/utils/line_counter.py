from config import VIDEO_CLASSES


class LineCounter:
    def __init__(self, line_position_ratio=0.5):
        self.line_position_ratio = line_position_ratio
        self.last_positions = {}
        self.crossed_ids = set()
        self.counts = {vehicle_type: 0 for vehicle_type in VIDEO_CLASSES}

    def get_line_y(self, frame_height):
        return int(frame_height * self.line_position_ratio)

    def update(self, tracked_objects, frame_height):
        line_y = self.get_line_y(frame_height)
        crossed = []

        for tracked in tracked_objects:
            track_id = tracked["id"]
            x1, y1, x2, y2 = tracked["bbox"]
            centroid_y = int((y1 + y2) / 2)
            prev_y = self.last_positions.get(track_id, centroid_y)
            vehicle_type = tracked.get("class_name", "unknown")

            if track_id not in self.crossed_ids:
                if (prev_y < line_y <= centroid_y) or (prev_y > line_y >= centroid_y):
                    self.crossed_ids.add(track_id)
                    if vehicle_type not in self.counts:
                        self.counts[vehicle_type] = 0
                    self.counts[vehicle_type] += 1
                    crossed.append(
                        {
                            "track_id": track_id,
                            "vehicle_type": vehicle_type,
                            "bbox": tracked["bbox"],
                            "timestamp": None,
                        }
                    )

            self.last_positions[track_id] = centroid_y

        return crossed
