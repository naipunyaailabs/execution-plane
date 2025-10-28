import asyncio
from sqlalchemy.orm import Session
from core.database import get_db, init_db
from services.agent_service import AgentService
from schemas.agent import AgentCreate

async def test_retrieve():
    print("Testing Agent Retrieval...")
    
    # Initialize database
    await init_db()
    print("Database initialized")
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    # Create agent service
    agent_service = AgentService(db)
    
    # Get all agents
    print("Retrieving all agents...")
    agents = await agent_service.get_agents()
    print(f"Found {len(agents)} agents")
    
    for agent in agents:
        print(f"Agent: {agent}")
        
        # Try to retrieve specific agent
        print(f"Retrieving agent {agent.agent_id}...")
        retrieved_agent = await agent_service.get_agent(agent.agent_id)
        print(f"Retrieved agent: {retrieved_agent}")

if __name__ == "__main__":
    asyncio.run(test_retrieve())