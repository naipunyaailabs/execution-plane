import asyncio
import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

async def test_knowledge_base_flow():
    """
    Test the complete knowledge base flow:
    1. Create an agent
    2. Create a knowledge base for that agent
    3. Add documents (text, URL)
    4. Query the knowledge base
    5. Chat with the agent using knowledge base context
    """
    
    print("=" * 60)
    print("Testing Knowledge Base Implementation")
    print("=" * 60)
    
    # Step 1: Create an agent
    print("\n[Step 1] Creating test agent...")
    agent_data = {
        "name": "Knowledge Base Test Agent",
        "agent_type": "react",
        "llm_provider": "groq",
        "llm_model": "llama-3.1-8b-instant",
        "api_key": "YOUR_GROQ_API_KEY",  # Replace with actual key
        "temperature": 0.7,
        "system_prompt": "You are a helpful AI assistant with access to a knowledge base.",
        "tools": [],
        "max_iterations": 15,
        "memory_type": "memory-saver",
        "streaming_enabled": True,
        "human_in_loop": False,
        "recursion_limit": 25
    }
    
    response = requests.post(f"{BASE_URL}/agents/", json=agent_data)
    if response.status_code == 200:
        agent = response.json()
        agent_id = agent['agent_id']
        print(f"✅ Agent created: {agent_id}")
    else:
        print(f"❌ Failed to create agent: {response.text}")
        return
    
    # Step 2: Create a knowledge base
    print("\n[Step 2] Creating knowledge base...")
    kb_data = {
        "agent_id": agent_id,
        "name": "Test Knowledge Base",
        "description": "Knowledge base for testing",
        "embedding_model": "qwen3-embedding:0.6b",
        "chunk_size": 1000,
        "chunk_overlap": 200
    }
    
    response = requests.post(f"{BASE_URL}/knowledge-bases/", json=kb_data)
    if response.status_code == 200:
        kb = response.json()
        kb_id = kb['kb_id']
        print(f"✅ Knowledge base created: {kb_id}")
        print(f"   Collection name: {kb['collection_name']}")
    else:
        print(f"❌ Failed to create knowledge base: {response.text}")
        return
    
    # Step 3a: Add text document
    print("\n[Step 3a] Adding text document...")
    text_content = """
    Python is a high-level, interpreted programming language.
    It was created by Guido van Rossum and first released in 1991.
    Python emphasizes code readability with significant whitespace.
    It supports multiple programming paradigms including procedural, 
    object-oriented, and functional programming.
    Python is widely used for web development, data science, 
    machine learning, automation, and scripting.
    """
    
    form_data = {"text": text_content}
    response = requests.post(
        f"{BASE_URL}/knowledge-bases/{kb_id}/documents/text",
        data=form_data
    )
    if response.status_code == 200:
        doc = response.json()
        print(f"✅ Text document added: {doc['doc_id']}")
        print(f"   Chunks created: {doc['chunk_count']}")
        print(f"   Status: {doc['status']}")
    else:
        print(f"❌ Failed to add text document: {response.text}")
    
    # Step 3b: Add URL document
    print("\n[Step 3b] Adding URL document...")
    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    form_data = {"url": url}
    response = requests.post(
        f"{BASE_URL}/knowledge-bases/{kb_id}/documents/url",
        data=form_data
    )
    if response.status_code == 200:
        doc = response.json()
        print(f"✅ URL document added: {doc['doc_id']}")
        print(f"   Chunks created: {doc['chunk_count']}")
        print(f"   Status: {doc['status']}")
    else:
        print(f"⚠️  Failed to add URL document (might need internet): {response.status_code}")
    
    # Wait for documents to be processed
    await asyncio.sleep(2)
    
    # Step 4: Query the knowledge base
    print("\n[Step 4] Querying knowledge base...")
    query_data = {
        "query": "What is Python used for?",
        "top_k": 3
    }
    
    response = requests.post(
        f"{BASE_URL}/knowledge-bases/{kb_id}/query",
        json=query_data
    )
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Found {len(results)} relevant chunks:")
        for i, result in enumerate(results, 1):
            print(f"\n   [{i}] Score: {result['score']:.4f}")
            print(f"       Content: {result['content'][:100]}...")
    else:
        print(f"❌ Failed to query knowledge base: {response.text}")
    
    # Step 5: Chat with agent (knowledge base will be auto-queried)
    print("\n[Step 5] Chatting with agent using knowledge base context...")
    chat_data = {
        "message": "What programming paradigms does Python support?",
        "thread_id": f"test_kb_{agent_id}"
    }
    
    response = requests.post(
        f"{BASE_URL}/agents/{agent_id}/chat/",
        json=chat_data
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Agent response:")
        print(f"   {result['response']}")
    else:
        print(f"❌ Failed to chat with agent: {response.text}")
    
    # Step 6: Get knowledge base details
    print("\n[Step 6] Getting knowledge base details...")
    response = requests.get(f"{BASE_URL}/knowledge-bases/{kb_id}")
    if response.status_code == 200:
        kb_details = response.json()
        print(f"✅ Knowledge base details:")
        print(f"   Name: {kb_details['name']}")
        print(f"   Agent ID: {kb_details['agent_id']}")
        print(f"   Collection: {kb_details['collection_name']}")
        print(f"   Documents: {len(kb_details.get('documents', []))}")
    else:
        print(f"❌ Failed to get knowledge base details: {response.text}")
    
    # Cleanup
    print("\n[Cleanup] Cleaning up test resources...")
    
    # Delete knowledge base
    response = requests.delete(f"{BASE_URL}/knowledge-bases/{kb_id}")
    if response.status_code == 200:
        print("✅ Knowledge base deleted")
    else:
        print(f"⚠️  Failed to delete knowledge base")
    
    # Delete agent
    response = requests.delete(f"{BASE_URL}/agents/{agent_id}/")
    if response.status_code == 200:
        print("✅ Agent deleted")
    else:
        print(f"⚠️  Failed to delete agent")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_knowledge_base_flow())
