from fastapi import APIRouter
from app.core.state_store import state_store

router = APIRouter()

@router.get("/state")
def read_state():
    return state_store.get_state()