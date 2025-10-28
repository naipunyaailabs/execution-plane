from fastapi import APIRouter
from . import agents

router = APIRouter()
router.include_router(agents.router, prefix="/agents", tags=["agents"])