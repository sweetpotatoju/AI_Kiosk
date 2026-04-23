import threading

from app.core.state_store import state_store
from ai_mod.tts_service import tts_service
from ai_mod.stt_service import STTService
from ai_mod.llm_service import LLMService


class ConversationService:
    def __init__(self):
        self.running = False
        self.thread = None
        self._stt: STTService | None = None
        self._llm: LLMService | None = None
        self._injected_text: str | None = None
        self._inject_lock = threading.Lock()

    def start(self):
        if self.running:
            return
        if self._stt is None:
            self._stt = STTService()
        if self._llm is None:
            self._llm = LLMService()
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("[CONV] conversation service started")

    def stop(self):
        self.running = False
        print("[CONV] conversation service stop requested")

    def inject_text(self, text: str):
        with self._inject_lock:
            self._injected_text = text
        print(f"[CONV] text injected: {text}")

    def _get_user_input(self) -> str:
        with self._inject_lock:
            if self._injected_text:
                text = self._injected_text
                self._injected_text = None
                print(f"[CONV] using injected text: {text}")
                return text
        return self._stt.transcribe(seconds=4)

    def _run(self):
        print("[CONV] conversation loop started")

        try:
            tts_service.speak_blocking("안녕하세요. 무엇을 도와드릴까요?")

            first = True
            while self.running:
                if first:
                    result = state_store.start_listening()
                    first = False
                else:
                    result = state_store.back_to_listening()

                if not result.get("success"):
                    print(f"[CONV] state transition to LISTENING failed: {result}")
                    break

                if not self.running:
                    break

                print("[CONV] waiting for user input...")
                try:
                    user_text = self._get_user_input()
                except Exception as e:
                    print(f"[CONV][ERROR] STT 실패: {e}")
                    user_text = ""

                print(f"[CONV] user input: '{user_text}'")

                if not self.running:
                    break

                if not user_text:
                    continue

                state_store.start_processing(user_text)

                try:
                    answer = self._llm.generate_answer(user_text)
                except Exception as e:
                    print(f"[CONV][ERROR] LLM 호출 실패: {e}")
                    answer = "죄송합니다. 답변을 생성하지 못했습니다."

                print(f"[CONV] LLM answer: '{answer}'")

                if not self.running:
                    break

                state_store.start_responding(answer)
                tts_service.speak_blocking(answer)

        except Exception as e:
            print(f"[CONV][ERROR] conversation loop 예외 발생: {e}")
            import traceback
            traceback.print_exc()

        print("[CONV] conversation loop ended")


conversation_service = ConversationService()
