import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "models", "blaze_face_short_range.tflite")

CAMERA_INDEX = 0
MIN_DETECTION_CONFIDENCE = 0.5
MIN_SUPPRESSION_THRESHOLD = 0.3

WINDOW_NAME = "Live Face Detection"
EXIT_KEY = "q"
PRINT_COOLDOWN_SEC = 2.0