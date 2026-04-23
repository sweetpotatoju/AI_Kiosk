from fastapi import APIRouter
from pydantic import BaseModel

from app.services.conversation_service import conversation_service

router = APIRouter()


class ChatRequest(BaseModel):
    text: str


@router.post("/chat")
def chat(req: ChatRequest):
    text = req.text.strip()
    if not text:
        return {"success": False, "message": "text is empty"}
    conversation_service.inject_text(text)
    return {"success": True}
