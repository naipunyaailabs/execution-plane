import requests
import time

# Use Code Review Agent which has shorter responses
agent_id = "f6b70f6b-746e-4e73-a2c1-55c64f78826d"  # Code Review Agent
thread_id = f"test_simple_{int(time.time())}"

print(f"Testing memory with Code Review Agent")
print(f"Thread ID: {thread_id}")
print("=" * 60)

# Clear and simple: state a fact
print("\n1. First message: 'Remember: my favorite color is blue'")
response1 = requests.post(
    f"http://localhost:8001/api/v1/agents/{agent_id}/chat/",
    json={"message": "Remember: my favorite color is blue", "thread_id": thread_id}
)
print(f"Status: {response1.status_code}")
print(f"Response: {response1.json()['response'][:300]}")

# Wait for memory
time.sleep(3)

# Ask about it
print("\n2. Second message: 'What is my favorite color?'")
response2 = requests.post(
    f"http://localhost:8001/api/v1/agents/{agent_id}/chat/",
    json={"message": "What is my favorite color?", "thread_id": thread_id}
)
print(f"Status: {response2.status_code}")
response_text = response2.json()['response']
print(f"Response: {response_text[:500]}")

# Check result
if "blue" in response_text.lower():
    print("\n✅ Memory WORKING! Agent remembered 'blue'")
else:
    print("\n❌ Memory NOT working. Agent didn't remember 'blue'")

# Check what was stored
print("\n3. Stored memories:")
response3 = requests.get(
    f"http://localhost:8001/api/v1/agents/memory/user/{thread_id}"
)
memories = response3.json().get('data', [])
print(f"Total: {len(memories)}")
for i, mem in enumerate(memories[:10]):
    print(f"  {i+1}. {mem.get('memory', 'N/A')}")
