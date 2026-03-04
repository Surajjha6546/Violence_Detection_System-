from fastapi import APIRouter
from services.storage import load_incidents

router = APIRouter()

@router.get("")
def analytics():
    incidents = load_incidents()

    violent = sum(1 for i in incidents if i["is_violent"] is True)
    non_violent = sum(1 for i in incidents if i["is_violent"] is False)
    ambiguous = sum(1 for i in incidents if i["is_violent"] == "ambiguous")

    return {
        "violent": violent,
        "non_violent": non_violent,
        "ambiguous": ambiguous
    }
