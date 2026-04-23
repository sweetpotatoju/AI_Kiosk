import os
import sys
import time
import threading
import cv2

from config import MODEL_PATH, CAMERA_INDEX, WINDOW_NAME, EXIT_KEY
from face_detection import LiveFaceDetector
from tts_service import TTSService
from stt_service import STTService
from llm_service import LLMService


def run_conversation(tts_service, stt_service, llm_service, done_callback):
    greet_message = "안녕하세요. 질문 있으세요?"
    print(f"[TTS] {greet_message}")
    tts_service.speak_blocking(greet_message)

    user_text = stt_service.transcribe(seconds=4)
    if user_text:
        print(f"[STT 결과] {user_text}")
        answer = llm_service.generate_answer(user_text)
        print(f"[LLM 답변] {answer}")
        tts_service.speak_blocking(answer)
    else:
        print("[STT 결과] 없음")
        tts_service.speak_blocking("질문을 듣지 못했어요. 다시 말씀해 주세요.")

    done_callback()


def main():
    if not os.path.exists(MODEL_PATH):
        print(f"[오류] 모델 파일이 없습니다: {MODEL_PATH}")
        sys.exit(1)

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("[오류] 웹캠을 열 수 없습니다.")
        sys.exit(1)

    tts_service = TTSService()
    stt_service = STTService(input_device=1)   # 필요하면 마이크 번호 변경
    llm_service = LLMService(model_name="exaone3.5:2.4b") #필요하면 모델 변경
    detector = LiveFaceDetector()
    detector.create()

    is_conversation_running = False

    def on_conversation_done():
        nonlocal is_conversation_running
        is_conversation_running = False

    print("[시작] 웹캠 얼굴 감지 시작")
    print(f"[종료] '{EXIT_KEY}' 키를 누르세요.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[경고] 프레임 읽기 실패")
                break

            timestamp_ms = int(time.time() * 1000)
            detector.detect_async(frame, timestamp_ms)

            output = detector.draw(frame.copy())
            cv2.imshow(WINDOW_NAME, output)

            if detector.consume_greeting_trigger() and not is_conversation_running:
                is_conversation_running = True
                threading.Thread(
                    target=run_conversation,
                    args=(tts_service, stt_service, llm_service, on_conversation_done),
                    daemon=True,
                ).start()

            if cv2.waitKey(1) & 0xFF == ord(EXIT_KEY):
                break

    finally:
        detector.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()