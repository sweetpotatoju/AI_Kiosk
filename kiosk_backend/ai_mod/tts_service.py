import threading
import pyttsx3


class TTSService:
    def __init__(self, rate: int = 165, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self.is_speaking = False
        self.lock = threading.Lock()

    def speak_async(self, text: str):
        with self.lock:
            if self.is_speaking:
                return
            self.is_speaking = True

        def _run():
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", self.rate)
                engine.setProperty("volume", self.volume)

                # 한국어 음성 선택 시도
                try:
                    voices = engine.getProperty("voices")
                    for voice in voices:
                        name = getattr(voice, "name", "")
                        if "Korean" in name or "Heami" in name or "한국어" in name:
                            engine.setProperty("voice", voice.id)
                            break
                except Exception:
                    pass

                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"[TTS 오류] {e}")
            finally:
                with self.lock:
                    self.is_speaking = False

        threading.Thread(target=_run, daemon=False).start()

    def speak_blocking(self, text: str):
        """TTS가 완전히 끝날 때까지 블로킹."""
        done = threading.Event()

        def _run():
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", self.rate)
                engine.setProperty("volume", self.volume)
                try:
                    voices = engine.getProperty("voices")
                    for voice in voices:
                        name = getattr(voice, "name", "")
                        if "Korean" in name or "Heami" in name or "한국어" in name:
                            engine.setProperty("voice", voice.id)
                            break
                except Exception:
                    pass
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"[TTS 오류] {e}")
            finally:
                done.set()

        threading.Thread(target=_run, daemon=False).start()
        done.wait()


tts_service = TTSService()