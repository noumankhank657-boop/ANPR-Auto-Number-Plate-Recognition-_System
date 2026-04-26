import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
VIDEO_DIR = os.path.join(DATA_DIR, "videos")
OUTPUT_DIR = os.path.join(DATA_DIR, "outputs")
DB_PATH = os.path.join(BASE_DIR, "database", "vehicle_logs.db")

VIDEO_PATHS = {
    "video1.mp4": os.path.join(VIDEO_DIR, "video1.mp4"),
    "video2.mp4": os.path.join(VIDEO_DIR, "video2.mp4"),
    "video3.mp4": os.path.join(VIDEO_DIR, "video3.mp4"),
}

VIDEO_CLASSES = ["car", "motorcycle", "truck", "bus"]

VIDEO_WIDTH = 640
FRAME_SKIP = 2
LINE_POSITION_RATIO = 0.5

DETECTION_CONFIDENCE = 0.25
PLATE_CONFIDENCE = 0.3
OCR_LANGUAGES = ["en"]

PLATE_MODEL_PATH = None
USE_CUDA = False

API_HOST = "127.0.0.1"
API_PORT = 8000

# Optional live source support for Streamlit or CLI
DEFAULT_VIDEO_SOURCE = VIDEO_PATHS["video1.mp4"]

# Ensure output path exists when the app starts
os.makedirs(OUTPUT_DIR, exist_ok=True)
