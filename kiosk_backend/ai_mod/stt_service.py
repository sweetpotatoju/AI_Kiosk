import tempfile
import wave
import sounddevice as sd
from faster_whisper import WhisperModel


class STTService:
    def __init__(self, input_device=None):
        self.input_device = input_device
        self.model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

    def record(self, seconds=4, samplerate=16000):
        print("[STT] 녹음 시작...")
        audio = sd.rec(
            int(seconds * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype="int16",
            device=self.input_device,
        )
        sd.wait()
        print("[STT] 녹음 종료")
        return audio, samplerate

    def save_wav(self, audio, samplerate):
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")

        with wave.open(temp.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(samplerate)
            wf.writeframes(audio.tobytes())

        return temp.name

    def transcribe(self, seconds=4):
        audio, sr = self.record(seconds=seconds)
        wav_path = self.save_wav(audio, sr)

        segments, _ = self.model.transcribe(
            wav_path,
            language="ko"
        )

        text = " ".join(segment.text.strip() for segment in segments).strip()
        return text