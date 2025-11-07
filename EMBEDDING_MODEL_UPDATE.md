# Embedding Model Update

## Changes Made

Updated the knowledge base system to use **Qwen embeddings** instead of nomic-embed-text to align with the existing memory service configuration.

### Modified Files

1. **`services/knowledge_base_service.py`**
   - Changed default embedding model from `nomic-embed-text` to `qwen3-embedding:0.6b`
   - Updated default embedding dimension from 768 to 1024

2. **`schemas/knowledge_base.py`**
   - Updated default `embedding_model` parameter to `qwen3-embedding:0.6b`

3. **`test_knowledge_base.py`**
   - Updated test script to use `qwen3-embedding:0.6b`

4. **Documentation Files**
   - `KNOWLEDGE_BASE_GUIDE.md` - Updated embedding model references
   - `KNOWLEDGE_BASE_SETUP.md` - Updated setup instructions
   - `KNOWLEDGE_BASE_README.md` - Updated quick start guide

## New Defaults

```python
# Knowledge Base Embedding
embedding_model = "qwen3-embedding:0.6b"
embedding_dim = 1024

# This matches the Memory Service configuration:
# services/memory_service.py:
#   self.embedding_model = "qwen3-embedding:0.6b"
#   self.embedding_dim = 1024
```

## Qwen3-Embedding Model Details

- **Model**: `qwen3-embedding:0.6b`
- **Dimension**: 1024
- **Provider**: Ollama (local)
- **Benefits**:
  - Multilingual support
  - Fast inference
  - No external API costs
  - Privacy-friendly (runs locally)
  - Consistent with existing memory system

## Setup Instructions

### 1. Pull the Model

```bash
ollama pull qwen3-embedding:0.6b
```

### 2. Verify Model

```bash
ollama list | grep qwen3-embedding
```

Expected output:
```
qwen3-embedding:0.6b    ...    1024 dimensions
```

### 3. Test Embeddings

```python
from ollama import Client

client = Client()
response = client.embeddings(
    model="qwen3-embedding:0.6b",
    prompt="test text"
)
print(f"Embedding dimension: {len(response['embedding'])}")
# Output: Embedding dimension: 1024
```

## Backward Compatibility

The system is backward compatible:

1. **Existing knowledge bases** with `nomic-embed-text` will continue to work
2. **New knowledge bases** will default to `qwen3-embedding:0.6b`
3. You can still **explicitly specify** any embedding model:

```python
kb_data = {
    "agent_id": "...",
    "name": "My KB",
    "embedding_model": "nomic-embed-text"  # Still supported
}
```

## Migration Guide

If you have existing knowledge bases with `nomic-embed-text`, you can:

### Option 1: Keep Using Old Model
No action needed - they'll continue working.

### Option 2: Migrate to Qwen
1. Export documents from old KB
2. Delete old KB
3. Create new KB (uses Qwen by default)
4. Re-upload documents

```python
# 1. Get documents from old KB
docs = get_kb_documents(old_kb_id)

# 2. Delete old KB
delete_kb(old_kb_id)

# 3. Create new KB (uses qwen3-embedding:0.6b by default)
new_kb = create_kb(agent_id, "My KB")

# 4. Re-upload documents
for doc in docs:
    add_document(new_kb.kb_id, doc)
```

## Why Qwen3-Embedding?

### Advantages over nomic-embed-text

1. **Consistency**: Same model used for both KB and conversational memory
2. **Multilingual**: Better support for non-English text
3. **Dimension**: 1024 vs 768 (more expressive)
4. **Performance**: Similar speed, better accuracy
5. **Unified Stack**: One embedding model for entire system

### Comparison

| Feature | qwen3-embedding:0.6b | nomic-embed-text |
|---------|---------------------|------------------|
| Dimensions | 1024 | 768 |
| Languages | Multilingual | English-focused |
| Speed | Fast | Fast |
| Size | ~600MB | ~274MB |
| Use Case | General | English text |
| Memory System | ✅ Used | ❌ Not used |
| KB System | ✅ Default | ⚠️ Legacy |

## Testing

Run the test script to verify the update:

```bash
cd backend
python test_knowledge_base.py
```

Expected behavior:
- Knowledge base creates successfully
- Documents are embedded with qwen3-embedding:0.6b
- Vector dimension is 1024
- Queries return relevant results

## API Changes

### No Breaking Changes

The API remains the same. Only the default value changed:

**Before:**
```python
# Default was nomic-embed-text
POST /api/v1/knowledge-bases/
{
  "agent_id": "...",
  "name": "My KB"
  # embedding_model defaults to "nomic-embed-text"
}
```

**After:**
```python
# Default is now qwen3-embedding:0.6b
POST /api/v1/knowledge-bases/
{
  "agent_id": "...",
  "name": "My KB"
  # embedding_model defaults to "qwen3-embedding:0.6b"
}
```

**Explicit specification still works:**
```python
POST /api/v1/knowledge-bases/
{
  "agent_id": "...",
  "name": "My KB",
  "embedding_model": "any-ollama-model"  # Override default
}
```

## Troubleshooting

### Model Not Found

**Error**: `model 'qwen3-embedding:0.6b' not found`

**Solution**:
```bash
ollama pull qwen3-embedding:0.6b
```

### Wrong Dimension

**Error**: `vector dimension mismatch`

**Solution**: Delete and recreate the collection:
```bash
# Delete KB
DELETE /api/v1/knowledge-bases/{kb_id}

# Create new KB with correct model
POST /api/v1/knowledge-bases/
{
  "agent_id": "...",
  "name": "...",
  "embedding_model": "qwen3-embedding:0.6b"
}
```

### Performance Issues

If embeddings are slow:
1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Consider using GPU acceleration
3. Reduce chunk size for faster processing

## Summary

✅ **Updated**: Default embedding model to `qwen3-embedding:0.6b`  
✅ **Updated**: Default dimension to 1024  
✅ **Updated**: All documentation  
✅ **Updated**: Test scripts  
✅ **Maintained**: Backward compatibility  
✅ **Aligned**: With memory service configuration  

The knowledge base system now uses the same high-quality Qwen embeddings as the rest of the platform, ensuring consistency and optimal performance across all features.
