import requests
import time

# Test with different agents using different LLM providers/models
test_cases = [
    {
        "name": "Chef Agent (llama-3.1-8b-instant)",
        "agent_id": "37abd9cb-8a42-4065-b5cf-069e9045e6da",
        "message1": "My favorite cuisine is Italian",
        "message2": "What is my favorite cuisine?"
    }
]

for test in test_cases:
    print(f"\n{'='*60}")
    print(f"Testing: {test['name']}")
    print(f"{'='*60}")
    
    thread_id = f"test_dynamic_{int(time.time())}"
    agent_id = test['agent_id']
    
    # First message
    print(f"\n1. Storing fact: '{test['message1']}'")
    response1 = requests.post(
        f"http://localhost:8001/api/v1/agents/{agent_id}/chat/",
        json={"message": test['message1'], "thread_id": thread_id}
    )
    
    if response1.status_code == 200:
        print(f"✅ Status: {response1.status_code}")
        print(f"Response preview: {response1.json()['response'][:150]}...")
    else:
        print(f"❌ Failed: {response1.status_code}")
        continue
    
    # Wait for memory processing
    time.sleep(3)
    
    # Second message - test recall
    print(f"\n2. Testing recall: '{test['message2']}'")
    response2 = requests.post(
        f"http://localhost:8001/api/v1/agents/{agent_id}/chat/",
        json={"message": test['message2'], "thread_id": thread_id}
    )
    
    if response2.status_code == 200:
        print(f"✅ Status: {response2.status_code}")
        answer = response2.json()['response']
        print(f"Response: {answer[:300]}")
        
        # Check if memory was recalled
        if "italian" in answer.lower():
            print("\n✅ MEMORY WORKING! Agent remembered the fact.")
        else:
            print("\n⚠️  Agent response doesn't explicitly mention Italian")
    else:
        print(f"❌ Failed: {response2.status_code}")
    
    # Check stored memories
    print(f"\n3. Checking stored memories...")
    response3 = requests.get(
        f"http://localhost:8001/api/v1/agents/memory/user/{thread_id}"
    )
    
    if response3.status_code == 200:
        memories = response3.json().get('data', [])
        print(f"Total memories: {len(memories)}")
        for i, mem in enumerate(memories[:5], 1):
            print(f"  {i}. {mem.get('memory', 'N/A')[:80]}")
    
    # Cleanup
    requests.delete(f"http://localhost:8001/api/v1/agents/memory/session/{thread_id}")
    
print(f"\n{'='*60}")
print("Test completed!")
print(f"{'='*60}")
