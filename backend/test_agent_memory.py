import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import get_db, init_db
from services.agent_service import AgentService

async def test_agent_memory_persistence():
    print('Testing Agent Memory Persistence with Mechanic Agent...')
    
    # Initialize database
    await init_db()
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    # Create agent service
    agent_service = AgentService(db)
    
    # Get all agents
    agents = await agent_service.get_agents()
    print(f'Found {len(agents)} agents:')
    for agent in agents:
        print(f'  - {agent.name} ({agent.agent_id}) - {agent.agent_type} agent')
    
    # Find the Mechanic Agent
    mechanic_agent = None
    for agent in agents:
        if agent.name == 'Mechanic Agent':
            mechanic_agent = agent
            break
    
    if not mechanic_agent:
        print('Mechanic Agent not found!')
        return
    
    print(f'\nUsing agent: {mechanic_agent.name} ({mechanic_agent.agent_id})')
    
    # Use a fixed thread_id for testing
    thread_id = 'mechanic_test_thread_123'
    print(f'Using thread_id: {thread_id}')
    
    # First message - introduce a problem
    print('\n--- First Message ---')
    try:
        response1 = await agent_service.chat_with_agent(
            mechanic_agent.agent_id, 
            'My car is making a strange noise when I accelerate. It sounds like grinding.', 
            thread_id
        )
        print(f'First response: {response1}')
    except Exception as e:
        print(f'Error in first message: {e}')
        import traceback
        traceback.print_exc()
        return
    
    # Second message - ask for more details
    print('\n--- Second Message ---')
    try:
        response2 = await agent_service.chat_with_agent(
            mechanic_agent.agent_id, 
            'When does the noise happen exactly - is it when I first start accelerating or throughout?', 
            thread_id
        )
        print(f'Second response: {response2}')
        
        # Check if the agent remembered the car issue
        if 'car' in response2.lower() or 'noise' in response2.lower() or 'grinding' in response2.lower():
            print('✓ Memory persistence seems to be working - agent remembered the context')
        else:
            print('✗ Memory persistence may not be working - agent might have forgotten the context')
    except Exception as e:
        print(f'Error in second message: {e}')
        import traceback
        traceback.print_exc()

    # Third message - ask for diagnostic steps
    print('\n--- Third Message ---')
    try:
        response3 = await agent_service.chat_with_agent(
            mechanic_agent.agent_id, 
            'What should I check first to diagnose this issue?', 
            thread_id
        )
        print(f'Third response: {response3}')
        
        # Check if the agent remembered the previous conversation
        if 'car' in response3.lower() or 'noise' in response3.lower() or 'grinding' in response3.lower():
            print('✓ Memory persistence is working - agent remembered the full context')
        else:
            print('✗ Memory persistence is NOT working - agent forgot the context')
    except Exception as e:
        print(f'Error in third message: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_agent_memory_persistence())