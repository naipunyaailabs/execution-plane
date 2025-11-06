import requests
import time

# Test memory flow
agent_id = "1b74ea9d-27b1-43f0-b03f-4c687c5399ec"
thread_id = f"test_thread_{int(time.time())}"

print(f"Testing with thread_id: {thread_id}")
print("=" * 60)

# First message
print("\n1. First message: 'My name is Alice'")
response1 = requests.post(
    f"http://localhost:8001/api/v1/agents/{agent_id}/chat/",
    json={"message": "My name is Alice", "thread_id": thread_id}
)
print(f"Status: {response1.status_code}")
print(f"Response: {response1.json()['response'][:200]}...")

# Wait a bit for memory to process
time.sleep(2)

# Second message - should remember
print("\n2. Second message: 'What is my name?'")
response2 = requests.post(
    f"http://localhost:8001/api/v1/agents/{agent_id}/chat/",
    json={"message": "What is my name?", "thread_id": thread_id}
)
print(f"Status: {response2.status_code}")
print(f"Response: {response2.json()['response'][:500]}")

# Check if "Alice" is in the response
if "Alice" in response2.json()['response'] or "alice" in response2.json()['response'].lower():
    print("\n✅ Memory is working! Agent remembered the name.")
else:
    print("\n❌ Memory is NOT working. Agent didn't remember the name.")

# Check memories
print("\n3. Checking stored memories...")
response3 = requests.get(
    f"http://localhost:8001/api/v1/agents/memory/user/{thread_id}"
)
memories = response3.json().get('data', [])
print(f"Total memories stored: {len(memories)}")
for i, mem in enumerate(memories[:5]):
    print(f"  {i+1}. {mem.get('memory', 'N/A')[:100]}")
