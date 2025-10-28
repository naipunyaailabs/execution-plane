import uuid
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from models.agent import Agent as AgentModel
from schemas.agent import AgentCreate, AgentInDB
from core.config import settings

class AgentService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_agent(self, agent_data: AgentCreate) -> AgentInDB:
        """Create a new agent in the database"""
        agent_id = str(uuid.uuid4())
        
        db_agent = AgentModel(
            agent_id=agent_id,
            name=agent_data.name,
            agent_type=agent_data.agent_type,
            llm_provider=agent_data.llm_provider,
            llm_model=agent_data.llm_model,
            temperature=agent_data.temperature,
            system_prompt=agent_data.system_prompt,
            tools=agent_data.tools,
            max_iterations=agent_data.max_iterations,
            memory_type=agent_data.memory_type,
            streaming_enabled=agent_data.streaming_enabled,
            human_in_loop=agent_data.human_in_loop,
            recursion_limit=agent_data.recursion_limit
        )
        
        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)
        print(f"Agent committed to database: {db_agent.agent_id}")
        
        return AgentInDB.model_validate(db_agent)
    
    async def get_agent(self, agent_id: str) -> Optional[AgentInDB]:
        """Retrieve an agent by ID"""
        db_agent = self.db.query(AgentModel).filter(AgentModel.agent_id == agent_id).first()
        if db_agent:
            return AgentInDB.model_validate(db_agent)
        return None
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent by ID"""
        db_agent = self.db.query(AgentModel).filter(AgentModel.agent_id == agent_id).first()
        if db_agent:
            self.db.delete(db_agent)
            self.db.commit()
            return True
        return False
    
    async def execute_agent(self, agent_id: str, input_text: str, thread_id: Optional[str] = None) -> str:
        """Execute an agent with the given input"""
        agent = await self.get_agent(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        # Create the LangGraph agent based on configuration
        langgraph_agent = self._create_langgraph_agent(agent)
        
        # Execute the agent
        config = {"configurable": {"thread_id": thread_id or agent_id}}
        response = langgraph_agent.invoke({"messages": [HumanMessage(content=input_text)]}, config)
        
        # Extract the final response
        final_message = response["messages"][-1]
        return final_message.content if hasattr(final_message, 'content') else str(final_message)
    
    async def stream_agent(self, websocket, agent_id: str):
        """Stream agent responses via WebSocket"""
        agent = await self.get_agent(agent_id)
        if not agent:
            await websocket.send_text(json.dumps({"error": "Agent not found"}))
            await websocket.close()
            return
        
        # For streaming, we would implement a callback mechanism
        # This is a simplified version - in practice, you'd need to handle
        # the streaming properly with LangGraph's streaming capabilities
        await websocket.send_text(json.dumps({"status": "Streaming not fully implemented in this example"}))
        await websocket.close()
    
    def _create_langgraph_agent(self, agent_config: AgentInDB):
        """Create a LangGraph agent based on the configuration"""
        # Initialize the LLM based on provider
        llm = self._initialize_llm(
            agent_config.llm_provider,
            agent_config.llm_model,
            agent_config.temperature
        )
        
        # Create the agent graph based on type
        if agent_config.agent_type == "react":
            return self._create_react_agent(llm, agent_config)
        elif agent_config.agent_type == "plan-execute":
            return self._create_plan_execute_agent(llm, agent_config)
        elif agent_config.agent_type == "reflection":
            return self._create_reflection_agent(llm, agent_config)
        else:  # custom
            return self._create_custom_agent(llm, agent_config)
    
    def _initialize_llm(self, provider: str, model: str, temperature: float):
        """Initialize the LLM based on provider"""
        if provider == "openai":
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=settings.OPENAI_API_KEY
            )
        elif provider == "anthropic":
            return ChatAnthropic(
                model=model,
                temperature=temperature,
                anthropic_api_key=settings.ANTHROPIC_API_KEY
            )
        # Add other providers as needed
        else:
            # Default to OpenAI if provider not recognized
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=settings.OPENAI_API_KEY
            )
    
    def _create_react_agent(self, llm, agent_config):
        """Create a ReAct agent"""
        # This is a simplified implementation
        # In practice, you would use LangGraph's prebuilt ReAct agent
        workflow = StateGraph(dict)
        
        # Define the agent logic here
        # This would include the ReAct loop, tool calling, etc.
        
        workflow.set_entry_point("agent")
        workflow.add_node("agent", lambda x: x)  # Placeholder
        workflow.add_edge("agent", END)
        
        return workflow.compile()
    
    def _create_plan_execute_agent(self, llm, agent_config):
        """Create a Plan & Execute agent"""
        # Implementation for Plan & Execute pattern
        workflow = StateGraph(dict)
        
        # Define the plan-execute logic here
        
        workflow.set_entry_point("planner")
        workflow.add_node("planner", lambda x: x)  # Placeholder
        workflow.add_node("executor", lambda x: x)  # Placeholder
        workflow.add_edge("planner", "executor")
        workflow.add_edge("executor", END)
        
        return workflow.compile()
    
    def _create_reflection_agent(self, llm, agent_config):
        """Create a Reflection agent"""
        # Implementation for Reflection pattern
        workflow = StateGraph(dict)
        
        # Define the reflection logic here
        
        workflow.set_entry_point("agent")
        workflow.add_node("agent", lambda x: x)  # Placeholder
        workflow.add_node("reflector", lambda x: x)  # Placeholder
        workflow.add_edge("agent", "reflector")
        workflow.add_edge("reflector", END)
        
        return workflow.compile()
    
    def _create_custom_agent(self, llm, agent_config):
        """Create a custom agent graph"""
        # Implementation for custom graph pattern
        workflow = StateGraph(dict)
        
        # Define custom logic based on agent_config
        
        workflow.set_entry_point("start")
        workflow.add_node("start", lambda x: x)  # Placeholder
        workflow.add_edge("start", END)
        
        return workflow.compile()