import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from core.database import get_db, init_db
from services.agent_service import AgentService
from schemas.agent import AgentCreate

async def test_memory_persistence():
    print("Testing Memory Persistence...")
    
    # Initialize database
    await init_db()
    print("Database initialized")
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    # Create agent service
    agent_service = AgentService(db)
    
    # Create test agent with FakeListLLM (no API key needed)
    agent_data = AgentCreate(
        name="Test Memory Agent",
        agent_type="react",
        llm_provider="openai",  # Will use FakeListLLM since no API key
        llm_model="gpt-3.5-turbo",
        api_key="",  # Empty API key will trigger FakeListLLM
        temperature=0.7,
        system_prompt="You are a helpful assistant",
        tools=["web_search"],
        max_iterations=15,
        memory_type="memory-saver",
        streaming_enabled=False,
        human_in_loop=False,
        recursion_limit=25
    )
    
    print("Creating agent...")
    agent = await agent_service.create_agent(agent_data)
    print(f"Agent created: {agent.agent_id}")
    
    # Use a fixed thread_id for testing
    thread_id = "test_thread_123"
    
    # First message
    print("\n--- First Message ---")
    try:
        response1 = await agent_service.chat_with_agent(agent.agent_id, "My name is Alice", thread_id)
        print(f"First response: {response1}")
    except Exception as e:
        print(f"Error in first message: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Second message - should remember the name
    print("\n--- Second Message ---")
    try:
        response2 = await agent_service.chat_with_agent(agent.agent_id, "What is my name?", thread_id)
        print(f"Second response: {response2}")
        
        # Check if the agent remembered the name
        if "alice" in response2.lower():
            print("✓ Memory persistence is working - agent remembered the name")
        else:
            print("✗ Memory persistence is NOT working - agent forgot the name")
    except Exception as e:
        print(f"Error in second message: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_memory_persistence())