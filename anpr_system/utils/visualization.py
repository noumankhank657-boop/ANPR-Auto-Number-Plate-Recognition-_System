import cv2

CLASS_COLORS = {
    "car": (0, 255, 0),
    "motorcycle": (255, 165, 0),
    "truck": (0, 128, 255),
    "bus": (255, 0, 0),
    "unknown": (255, 255, 255),
}


def draw_annotations(frame, tracked_objects, line_y, counts, last_plate_text, highlighted_ids=None):
    highlighted_ids = set(highlighted_ids or [])
    annotated = frame.copy()

    cv2.line(annotated, (0, line_y), (annotated.shape[1], line_y), (0, 0, 255), 2)

    for tracked in tracked_objects:
        x1, y1, x2, y2 = tracked["bbox"]
        class_name = tracked["class_name"]
        track_id = tracked["id"]
        color = CLASS_COLORS.get(class_name, CLASS_COLORS["unknown"])
        if track_id in highlighted_ids:
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 255), 3)
        else:
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            annotated,
            f"{class_name} #{track_id}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
        )

    x_offset = 10
    y_offset = 30
    for vehicle_type, count in counts.items():
        cv2.putText(
            annotated,
            f"{vehicle_type}: {count}",
            (x_offset, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        y_offset += 30

    cv2.putText(
        annotated,
        f"Last plate: {last_plate_text}",
        (10, annotated.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    return annotated
