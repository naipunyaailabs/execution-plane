from mem0 import Memory
import os

# Configure Mem0 exactly like in MemoryService
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "test_collection",
            "path": "/tmp/qdrant_test",
            "embedding_model_dims": 1024,
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "qwen3-embedding:0.6b",
            "ollama_base_url": "http://localhost:11434",
        }
    },
    "llm": {
        "provider": "groq",
        "config": {
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.1,
            "max_tokens": 2000,
        }
    },
    "version": "v1.1"
}

print("Initializing Mem0...")
memory = Memory.from_config(config)
print("✅ Mem0 initialized\n")

# Test adding memory
messages = [
    {"role": "user", "content": "My favorite color is blue"},
    {"role": "assistant", "content": "That's great! Blue is a calming color."}
]

print("Adding memory...")
result = memory.add(messages, user_id="test_user_123")
print(f"Result: {result}\n")

# Check if anything was added
import time
time.sleep(2)

print("Searching for 'favorite color'...")
search_result = memory.search("favorite color", user_id="test_user_123")
print(f"Search result: {search_result}\n")

print("Getting all memories...")
all_memories = memory.get_all(user_id="test_user_123")
print(f"All memories: {all_memories}")
