import argparse
import os
import threading
import time
from collections import deque
from pathlib import Path

import cv2

from config import FRAME_SKIP, LINE_POSITION_RATIO, OUTPUT_DIR, VIDEO_DIR, VIDEO_PATHS, VIDEO_WIDTH
from database.db import insert_log
from detection.plate_detector import PlateDetector
from detection.vehicle_detector import VehicleDetector
from tracking.tracker import ObjectTracker
from utils.line_counter import LineCounter
from utils.ocr import read_plate
from utils.visualization import draw_annotations


class FrameReader(threading.Thread):
    def __init__(self, capture, queue, stop_event):
        super().__init__(daemon=True)
        self.capture = capture
        self.queue = queue
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            ret, frame = self.capture.read()
            if not ret:
                self.stop_event.set()
                break
            self.queue.append(frame)
            time.sleep(0.005)


def process_video(video_filename):
    video_path = VIDEO_PATHS.get(video_filename) or os.path.join(VIDEO_DIR, video_filename)
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    output_path = Path(OUTPUT_DIR) / f"{Path(video_filename).stem}_annotated.mp4"
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (VIDEO_WIDTH, int((height / width) * VIDEO_WIDTH)),
    )

    detector = VehicleDetector()
    tracker = ObjectTracker()
    plate_detector = PlateDetector()
    line_counter = LineCounter(LINE_POSITION_RATIO)

    queue = deque(maxlen=10)
    stop_event = threading.Event()
    reader = FrameReader(cap, queue, stop_event)
    reader.start()

    frame_index = 0
    last_annotated = None

    try:
        while not stop_event.is_set() or queue:
            if not queue:
                time.sleep(0.01)
                continue

            frame = queue.popleft()
            frame = cv2.resize(frame, (VIDEO_WIDTH, int((height / width) * VIDEO_WIDTH)))
            frame_index += 1

            if frame_index % FRAME_SKIP != 0:
                if last_annotated is not None:
                    writer.write(last_annotated)
                    cv2.imshow("ANPR Traffic", last_annotated)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
                continue

            detections = detector.detect_vehicles(frame)
            tracks = tracker.update(detections, frame)
            crossed = line_counter.update(tracks, frame.shape[0])
            last_plate_text = "NONE"

            for event in crossed:
                vehicle_type = event["vehicle_type"]
                track_id = event["track_id"]
                bbox = event["bbox"]
                plate_box = plate_detector.detect_plate(frame, bbox)
                plate_image = frame[plate_box[1]:plate_box[3], plate_box[0]:plate_box[2]]
                plate_text = read_plate(plate_image)
                last_plate_text = plate_text
                insert_log(vehicle_type, plate_text, None, video_filename)
                print(f"[{video_filename}] {vehicle_type} #ID={track_id} crossed line → Plate: {plate_text}")

            annotated = draw_annotations(
                frame,
                tracks,
                int(LINE_POSITION_RATIO * frame.shape[0]),
                line_counter.counts,
                last_plate_text,
                [event["track_id"] for event in crossed],
            )
            last_annotated = annotated
            writer.write(annotated)
            cv2.imshow("ANPR Traffic", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("Stopping pipeline...")
    finally:
        stop_event.set()
        reader.join(timeout=1.0)
        cap.release()
        writer.release()
        cv2.destroyAllWindows()
        print(f"Saved annotated output to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ANPR Traffic Pipeline")
    parser.add_argument("--video", default="video1.mp4", help="Video filename to process")
    args = parser.parse_args()
    process_video(args.video)
