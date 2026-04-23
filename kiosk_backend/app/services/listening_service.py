from app.core.state_store import state_store


def start_listening() -> dict:
    return state_store.start_listening()