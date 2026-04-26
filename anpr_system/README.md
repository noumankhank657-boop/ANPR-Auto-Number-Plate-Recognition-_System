# ANPR Traffic Monitoring System

An AI-powered real-time vehicle monitoring system for traffic videos.

## Setup

```bash
cd anpr_system
pip install -r requirements.txt
```

## Place Your Videos

Copy your traffic video files into:

```bash
cp your_video1.mp4 data/videos/video1.mp4
cp your_video2.mp4 data/videos/video2.mp4
cp your_video3.mp4 data/videos/video3.mp4
```

## Run the Video Pipeline

```bash
python main.py --video video1.mp4
python main.py --video video2.mp4
python main.py --video video3.mp4
```

## Start the API

```bash
uvicorn api.app:app --reload --port 8000
```

## Start the Streamlit Dashboard

```bash
streamlit run dashboard/streamlit_app.py
```

## Project Structure

- `main.py`: Entry point for full pipeline processing.
- `config.py`: Paths, detection thresholds, and runtime settings.
- `detection/vehicle_detector.py`: YOLOv8 COCO vehicle detection.
- `detection/plate_detector.py`: License plate localization with fallback.
- `tracking/tracker.py`: DeepSORT object tracking.
- `utils/line_counter.py`: Line crossing detection and counters.
- `utils/ocr.py`: EasyOCR and plate text cleaning.
- `utils/visualization.py`: Frame annotation for live display.
- `database/db.py`: SQLite CRUD operations.
- `api/app.py`: FastAPI endpoints for logs and analytics.
- `dashboard/streamlit_app.py`: Streamlit dashboard with live view.

## Notes

- The system processes every `N`th frame to improve performance.
- License plate detection only triggers when a vehicle crosses the configured line.
- Logs are stored in SQLite at `database/vehicle_logs.db`.
