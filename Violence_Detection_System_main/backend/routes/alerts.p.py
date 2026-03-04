from fastapi import APIRouter
from services.storage import load_incidents

router = APIRouter()

@router.get("")
def alerts():
    incidents = load_incidents()
    return incidents[::-1]
