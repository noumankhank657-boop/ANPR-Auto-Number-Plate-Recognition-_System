import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import LINE_POSITION_RATIO, VIDEO_PATHS, VIDEO_WIDTH, FRAME_SKIP
from database.db import get_all_logs, get_analytics, insert_log
from detection.plate_detector import PlateDetector
from detection.vehicle_detector import VehicleDetector
from tracking.tracker import ObjectTracker
from utils.line_counter import LineCounter
from utils.ocr import read_plate
from utils.visualization import draw_annotations


def resize_frame(frame, target_width):
    height, width = frame.shape[:2]
    scale = target_width / width
    return cv2.resize(frame, (target_width, int(height * scale)))


def run_live_processing(video_path, line_ratio):
    detector = VehicleDetector()
    tracker = ObjectTracker()
    plate_detector = PlateDetector()
    counter = LineCounter(line_ratio)

    cap = cv2.VideoCapture(video_path)
    last_plate_text = "NONE"
    frame_placeholder = st.empty()
    stats_placeholder = st.empty()

    while cap.isOpened() and st.session_state.running:
        ret, frame = cap.read()
        if not ret:
            break

        frame = resize_frame(frame, VIDEO_WIDTH)
        results = detector.detect_vehicles(frame)
        tracks = tracker.update(results, frame)
        crossed = counter.update(tracks, frame.shape[0])

        for event in crossed:
            plate_box = plate_detector.detect_plate(frame, event["bbox"])
            plate_image = frame[plate_box[1]:plate_box[3], plate_box[0]:plate_box[2]]
            plate_text = read_plate(plate_image)
            last_plate_text = plate_text
            insert_log(event["vehicle_type"], plate_text, None, os.path.basename(video_path))

        annotated = draw_annotations(
            frame,
            tracks,
            counter.get_line_y(frame.shape[0]),
            counter.counts,
            last_plate_text,
            [event["track_id"] for event in crossed],
        )

        frame_placeholder.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), channels="RGB", use_column_width=True)
        stats_placeholder.metric("Last plate", last_plate_text)
        time.sleep(0.03)

    cap.release()


def main():
    st.set_page_config(page_title="ANPR Traffic Dashboard", layout="wide")
    st.title("AI Traffic ANPR Dashboard")

    if "running" not in st.session_state:
        st.session_state.running = False

    with st.sidebar:
        selected_video = st.selectbox("Select video", list(VIDEO_PATHS.keys()))
        line_position = st.slider("Virtual line position", 0.1, 0.9, LINE_POSITION_RATIO, step=0.05)
        if st.button("Start"):
            st.session_state.running = True
        if st.button("Stop"):
            st.session_state.running = False

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Video source**")
    st.sidebar.write(VIDEO_PATHS[selected_video])

    tab1, tab2, tab3 = st.tabs(["Live View", "Plate Logs", "Analytics"])

    with tab1:
        st.header("Live View")
        if st.session_state.running:
            run_live_processing(VIDEO_PATHS[selected_video], line_position)
        else:
            st.info("Press Start to begin processing the selected video.")

    with tab2:
        st.header("Plate Logs")
        logs = get_all_logs()
        dataframe = pd.DataFrame(logs)
        if dataframe.empty:
            st.write("No logs available yet.")
        else:
            vehicle_filter = st.selectbox("Filter by vehicle type", ["All"] + sorted(dataframe["vehicle_type"].unique().tolist()))
            video_filter = st.selectbox("Filter by video source", ["All"] + sorted(dataframe["video_source"].unique().tolist()))
            if vehicle_filter != "All":
                dataframe = dataframe[dataframe["vehicle_type"] == vehicle_filter]
            if video_filter != "All":
                dataframe = dataframe[dataframe["video_source"] == video_filter]
            st.dataframe(dataframe)
            csv = dataframe.to_csv(index=False).encode("utf-8")
            st.download_button("Download logs as CSV", csv, file_name="vehicle_logs.csv", mime="text/csv")

    with tab3:
        st.header("Analytics")
        analytics = get_analytics()
        counts = analytics.get("vehicle_type_counts", [])
        hourly = analytics.get("hourly_counts", [])

        if not counts:
            st.write("No analytics available yet.")
        else:
            counts_df = pd.DataFrame(counts)
            hourly_df = pd.DataFrame(hourly)

            st.subheader("Vehicle count per class")
            st.bar_chart(counts_df.set_index("vehicle_type"))

            st.subheader("Hourly traffic")
            if not hourly_df.empty:
                hourly_df["hour"] = pd.to_datetime(hourly_df["hour"])
                hourly_df = hourly_df.sort_values("hour")
                st.line_chart(hourly_df.set_index("hour"))

            st.subheader("Vehicle type distribution")
            st.write(counts_df)
            st.write("Per-video breakdown is available in the Plate Logs tab.")


if __name__ == "__main__":
    main()
