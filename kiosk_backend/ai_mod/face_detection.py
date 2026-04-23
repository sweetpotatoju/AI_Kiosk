import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from ai_mod.config import (
    MODEL_PATH,
    MIN_DETECTION_CONFIDENCE,
    MIN_SUPPRESSION_THRESHOLD,
)

# from config import (
#     MODEL_PATH,
#     MIN_DETECTION_CONFIDENCE,
#     MIN_SUPPRESSION_THRESHOLD,
# )

HOLD_SECONDS = 1.0
NO_FACE_TIMEOUT_SECONDS = 3.0
MIN_FACE_SIZE = 60  # 가까이 있다고 판단하는 최소 바운딩박스 크기(px)


class LiveFaceDetector:
    def __init__(self):
        self.detector = None
        self.latest_result = None

        self.face_start_time = None
        self.has_announced = False
        self.was_detected = False

        self.greeting_triggered = False

        self.last_seen_time = None
        self.no_face_triggered = False

    def _result_callback(self, result, output_image, timestamp_ms: int):
        self.latest_result = result
        now = time.time()

        if result and result.detections:
            best_detection = result.detections[0]
            bbox = best_detection.bounding_box
            is_close = bbox.width >= MIN_FACE_SIZE and bbox.height >= MIN_FACE_SIZE

            if is_close:
                self.last_seen_time = now
                self.no_face_triggered = False

                if not self.was_detected:
                    self.face_start_time = now
                    self.has_announced = False
                    self.was_detected = True
                    print("[상태] 얼굴 감지")

                elapsed = now - self.face_start_time
                if elapsed >= HOLD_SECONDS and not self.has_announced:
                    self.greeting_triggered = True
                    self.has_announced = True
                return

        # 얼굴 없거나 너무 작은 경우
        if self.was_detected:
            print("[상태] 얼굴 사라짐 -> 초기화")
        self._reset_state()

        if self.last_seen_time is not None:
            if now - self.last_seen_time >= NO_FACE_TIMEOUT_SECONDS:
                self.no_face_triggered = True

    def _reset_state(self):
        self.face_start_time = None
        self.has_announced = False
        self.was_detected = False

    def consume_greeting_trigger(self) -> bool:
        if self.greeting_triggered:
            self.greeting_triggered = False
            return True
        return False

    def consume_no_face_trigger(self) -> bool:
        if self.no_face_triggered:
            self.no_face_triggered = False
            self.last_seen_time = None
            return True
        return False

    def create(self):
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.FaceDetectorOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            result_callback=self._result_callback,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_suppression_threshold=MIN_SUPPRESSION_THRESHOLD,
        )
        self.detector = vision.FaceDetector.create_from_options(options)

    def detect_async(self, frame_bgr, timestamp_ms: int):
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        self.detector.detect_async(mp_image, timestamp_ms)

    def draw(self, frame_bgr):
        if not self.latest_result or not self.latest_result.detections:
            return frame_bgr

        for detection in self.latest_result.detections:
            bbox = detection.bounding_box
            x, y = int(bbox.origin_x), int(bbox.origin_y)
            w, h = int(bbox.width), int(bbox.height)

            is_close = w >= MIN_FACE_SIZE and h >= MIN_FACE_SIZE
            color = (0, 255, 0) if is_close else (0, 0, 255)

            cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), color, 2)
            cv2.putText(
                frame_bgr,
                "DETECTED" if is_close else "TOO FAR",
                (x, max(30, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
            )

        return frame_bgr

    def close(self):
        if self.detector is not None:
            self.detector.close()
            self.detector = None