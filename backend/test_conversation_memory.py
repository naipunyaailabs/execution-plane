import requests
import time

# Test conversational memory with assistant questions
agent_id = "37abd9cb-8a42-4065-b5cf-069e9045e6da"  # Chef Agent
thread_id = f"test_conv_{int(time.time())}"

print(f"Testing Conversational Memory")
print(f"Thread ID: {thread_id}")
print("=" * 60)

# Turn 1: Assistant asks a question
print("\n[Turn 1] User: I want to cook something special")
r1 = requests.post(
    f"http://localhost:8001/api/v1/agents/{agent_id}/chat/",
    json={"message": "I want to cook something special", "thread_id": thread_id}
)
print(f"Assistant: {r1.json()['response'][:200]}...")
time.sleep(2)

# Turn 2: User provides specific requirement (answering assistant's question)
print("\n[Turn 2] User: I prefer vegetarian dishes and I'm allergic to nuts")
r2 = requests.post(
    f"http://localhost:8001/api/v1/agents/{agent_id}/chat/",
    json={"message": "I prefer vegetarian dishes and I'm allergic to nuts", "thread_id": thread_id}
)
print(f"Assistant: {r2.json()['response'][:200]}...")
time.sleep(2)

# Turn 3: Follow-up question that requires context from Turn 2
print("\n[Turn 3] User: What ingredients do I need?")
r3 = requests.post(
    f"http://localhost:8001/api/v1/agents/{agent_id}/chat/",
    json={"message": "What ingredients do I need?", "thread_id": thread_id}
)
response3 = r3.json()['response']
print(f"Assistant: {response3[:300]}...")

# Check if assistant remembers the dietary restrictions
print("\n" + "=" * 60)
print("CONTEXT CHECK:")
has_vegetarian = "vegetarian" in response3.lower() or "veg" in response3.lower()
has_no_nuts = "nut" not in response3.lower() or "allerg" in response3.lower()

if has_vegetarian:
    print("✅ Assistant remembered: vegetarian preference")
else:
    print("⚠️  Assistant may not have remembered vegetarian preference")

print("\n" + "=" * 60)
print("Stored Memories:")
r_mem = requests.get(f"http://localhost:8001/api/v1/agents/memory/user/{thread_id}")
memories = r_mem.json().get('data', [])
print(f"Total: {len(memories)}")
for i, mem in enumerate(memories[:10], 1):
    print(f"  {i}. {mem.get('memory', 'N/A')}")

# Cleanup
requests.delete(f"http://localhost:8001/api/v1/agents/memory/session/{thread_id}")
print("\n" + "=" * 60)
print("Test completed!")
