import requests


class LLMService:
    def __init__(self, model_name="qwen2.5:3b", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    def generate_answer(self, user_text: str) -> str:
        user_text = (user_text or "").strip()
        if not user_text:
            return "질문을 잘 듣지 못했어요. 다시 말씀해 주세요."

        prompt = f"""
당신은 회사 안내 키오스크 AI입니다.
사용자의 질문에 한국어로 자연스럽고 간결하게 답변하세요.
모르는 내용은 아는 척하지 말고, 정확하지 않으면 정확한 정보가 필요하다고 말하세요.

사용자 질문:
{user_text}
""".strip()

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()

            answer = data.get("response", "").strip()
            if not answer:
                return "답변을 생성하지 못했습니다."
            return answer

        except requests.exceptions.RequestException as e:
            print(f"[LLM 오류] {e}")
            return "현재 AI 응답 서비스를 사용할 수 없습니다."