from services.memory_service import MemoryService
import time

# Initialize memory service
ms = MemoryService()

if not ms.is_enabled():
    print("❌ Memory service is not enabled!")
    exit(1)

print("✅ Memory service is enabled")

# Test user ID
test_user = f"test_debug_{int(time.time())}"

# Add a memory
print(f"\n1. Adding memory for user: {test_user}")
messages = [
    {"role": "user", "content": "My name is Bob"},
    {"role": "assistant", "content": "Nice to meet you, Bob!"}
]
result = ms.add_memory(messages, user_id=test_user, agent_id="test_agent")
print(f"Add result: {result}")

# Wait for indexing
print("\n2. Waiting 3 seconds for indexing...")
time.sleep(3)

# Search for the memory
print(f"\n3. Searching for 'What is my name?' in user: {test_user}")
search_results = ms.search_memory(
    query="What is my name?",
    user_id=test_user,
    agent_id="test_agent",
    top_k=5
)
print(f"Search results: {search_results}")

# Get all memories
print(f"\n4. Getting all memories for user: {test_user}")
all_memories = ms.get_user_memories(user_id=test_user, agent_id="test_agent")
print(f"All memories: {all_memories}")

# Try without agent_id filter
print(f"\n5. Getting all memories WITHOUT agent_id filter:")
all_memories_no_filter = ms.get_user_memories(user_id=test_user)
print(f"All memories (no filter): {all_memories_no_filter}")
