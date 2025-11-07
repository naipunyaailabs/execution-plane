from fastapi import APIRouter
from . import agents, knowledge_base

router = APIRouter()
router.include_router(agents.router, prefix="/agents", tags=["agents"])
router.include_router(knowledge_base.router, prefix="/knowledge-bases", tags=["knowledge-bases"])