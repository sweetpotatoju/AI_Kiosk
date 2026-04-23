from fastapi import APIRouter
from app.core.state_store import state_store

router = APIRouter()

@router.post("/session/reset")
def reset_session():
    return state_store.reset()