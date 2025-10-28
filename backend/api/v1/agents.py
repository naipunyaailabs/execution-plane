from fastapi import APIRouter, Depends, HTTPException, WebSocket
from typing import List
from sqlalchemy.orm import Session

from schemas.agent import AgentCreate, AgentInDB, AgentExecutionRequest, AgentExecutionResponse
from services.agent_service import AgentService
from core.database import get_db

router = APIRouter()

@router.post("/", response_model=AgentInDB)
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Create a new LangGraph agent"""
    try:
        agent_service = AgentService(db)
        agent = await agent_service.create_agent(agent_data)
        return agent
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{agent_id}", response_model=AgentInDB)
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get agent configuration by ID"""
    try:
        agent_service = AgentService(db)
        agent = await agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """Delete an agent"""
    try:
        agent_service = AgentService(db)
        success = await agent_service.delete_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"message": "Agent deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{agent_id}/execute", response_model=AgentExecutionResponse)
async def execute_agent(agent_id: str, request: AgentExecutionRequest, db: Session = Depends(get_db)):
    """Execute an agent with input"""
    try:
        agent_service = AgentService(db)
        response = await agent_service.execute_agent(agent_id, request.input, request.thread_id)
        return AgentExecutionResponse(response=response, thread_id=request.thread_id or agent_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.websocket("/{agent_id}/stream")
async def stream_agent(websocket: WebSocket, agent_id: str, db: Session = Depends(get_db)):
    """WebSocket endpoint for streaming agent responses"""
    try:
        await websocket.accept()
        agent_service = AgentService(db)
        await agent_service.stream_agent(websocket, agent_id)
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))