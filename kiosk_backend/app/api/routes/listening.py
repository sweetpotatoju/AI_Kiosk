from fastapi import APIRouter
from app.services.listening_service import start_listening

router = APIRouter()

@router.post("/listening")
def listening():
    return start_listening()