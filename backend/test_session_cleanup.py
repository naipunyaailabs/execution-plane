import requests
import time

agent_id = "1b74ea9d-27b1-43f0-b03f-4c687c5399ec"  # Doctor Agent
thread_id = f"test_cleanup_{int(time.time())}"

print(f"Testing session-based memory cleanup")
print(f"Thread ID: {thread_id}")
print("=" * 60)

# Add memory
print("\n1. First message: 'My name is Bob'")
response1 = requests.post(
    f"http://localhost:8001/api/v1/agents/{agent_id}/chat/",
    json={"message": "My name is Bob", "thread_id": thread_id}
)
print(f"Status: {response1.status_code}")

time.sleep(2)

# Verify memory exists
print("\n2. Check memory exists:")
response2 = requests.get(
    f"http://localhost:8001/api/v1/agents/memory/user/{thread_id}"
)
memories = response2.json().get('data', [])
print(f"Memories before cleanup: {len(memories)}")
for mem in memories[:3]:
    print(f"  - {mem.get('memory', 'N/A')}")

# Simulate page refresh - delete session
print(f"\n3. Simulating page refresh (DELETE session)...")
response3 = requests.delete(
    f"http://localhost:8001/api/v1/agents/memory/session/{thread_id}"
)
print(f"Cleanup status: {response3.status_code}")
print(f"Cleanup message: {response3.json().get('message', 'N/A')}")

time.sleep(1)

# Verify memory cleared
print("\n4. Check memory after cleanup:")
response4 = requests.get(
    f"http://localhost:8001/api/v1/agents/memory/user/{thread_id}"
)
memories_after = response4.json().get('data', [])
print(f"Memories after cleanup: {len(memories_after)}")

if len(memories_after) == 0:
    print("\n✅ Session cleanup WORKING! Memory was cleared.")
else:
    print(f"\n❌ Session cleanup FAILED. Still have {len(memories_after)} memories.")

# Test that new session doesn't know the name
print("\n5. Ask in new session (same thread_id to verify cleanup):")
response5 = requests.post(
    f"http://localhost:8001/api/v1/agents/{agent_id}/chat/",
    json={"message": "What is my name?", "thread_id": thread_id}
)
response_text = response5.json()['response'][:300]
print(f"Response: {response_text}")

if "Bob" in response_text or "bob" in response_text.lower():
    print("\n❌ Agent still remembers Bob (cleanup didn't work)")
else:
    print("\n✅ Agent doesn't remember Bob (cleanup worked!)")
