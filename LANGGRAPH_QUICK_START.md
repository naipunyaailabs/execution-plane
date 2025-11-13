# 🚀 LangGraph Quick Start

## ✅ Installation (2 minutes)

```bash
# 1. Install LangGraph
cd backend
./venv/bin/pip install langgraph

# 2. Verify installation
./venv/bin/python -c "from langgraph.graph import StateGraph; print('✅ LangGraph installed')"

# 3. Restart backend
./venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🎯 Test LangGraph Execution

### Step 1: Create a Workflow (if you haven't)

```bash
curl -X POST http://localhost:8000/api/v1/workflows/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LangGraph Test",
    "description": "Testing LangGraph execution",
    "definition": {
      "steps": [
        {
          "id": "start",
          "type": "start",
          "name": "Start"
        },
        {
          "id": "agent-1",
          "type": "agent",
          "name": "AI Agent",
          "agent_id": "31ab0b60-98ae-4b3e-b9c5-44481a9155eb"
        },
        {
          "id": "end",
          "type": "end",
          "name": "End"
        }
      ],
      "dependencies": {
        "agent-1": ["start"],
        "end": ["agent-1"]
      }
    }
  }'
```

**Copy the `workflow_id` from response!**

---

### Step 2: Execute with LangGraph

```bash
# Replace {workflow_id} with your actual ID
curl -X POST http://localhost:8000/api/v1/workflows/{workflow_id}/execute-langgraph \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "query": "What is 10 + 10?"
    }
  }' | python3 -m json.tool
```

---

## 📊 Understanding the Response

```json
{
  "success": true,
  "workflow_id": "...",
  "execution_state": {
    "messages": [
      {
        "step_id": "start",
        "type": "start",
        "result": {"output": "Workflow started"},
        "timestamp": "2024-11-13T12:00:00"
      },
      {
        "step_id": "agent-1",
        "type": "agent",
        "result": {"output": "20"},
        "timestamp": "2024-11-13T12:00:05"
      },
      {
        "step_id": "end",
        "type": "end",
        "result": {"output": "Workflow completed"},
        "timestamp": "2024-11-13T12:00:06"
      }
    ],
    "completed_steps": ["start", "agent-1", "end"],
    "failed_steps": [],
    "step_results": {
      "start": {"output": "Workflow started"},
      "agent-1": {"output": "20"},
      "end": {"output": "Workflow completed"}
    },
    "context": {
      "start": "Workflow started",
      "agent-1": "20",
      "end": "Workflow completed"
    },
    "metadata": {
      "started_at": "2024-11-13T12:00:00",
      "completed_at": "2024-11-13T12:00:06",
      "success": true
    }
  }
}
```

### Key Fields:
- **`messages`**: Complete execution history (all nodes)
- **`completed_steps`**: List of successfully executed steps
- **`step_results`**: Results from each step
- **`context`**: Shared state between nodes
- **`metadata`**: Execution timing and status

---

## 🔄 Compare: Standard vs LangGraph

### Standard Execution
```bash
POST /api/v1/workflows/{workflow_id}/execute
```
**Returns:** Simple execution record with status

### LangGraph Execution  
```bash
POST /api/v1/workflows/{workflow_id}/execute-langgraph
```
**Returns:** Full state machine with:
- Complete message history
- State at each step
- Context sharing
- Metadata tracking

---

## 🎨 Key Features You Get

### 1. **State Management**
```json
{
  "context": {
    "user_name": "John",
    "previous_result": "42"
  }
}
```
Access in next nodes: `{{ context.user_name }}`

### 2. **Message History**
Every node execution is logged:
```json
{
  "messages": [
    {"step_id": "start", "result": {...}},
    {"step_id": "agent-1", "result": {...}},
    {"step_id": "end", "result": {...}}
  ]
}
```

### 3. **Conditional Routing**
```json
{
  "conditions": {
    "check": {
      "true_branch": "path-a",
      "false_branch": "path-b"
    }
  }
}
```

### 4. **Loops**
```json
{
  "type": "loop",
  "loop_config": {
    "collection": "input_data.items",
    "max_iterations": 100
  }
}
```

---

## 🧪 Example Workflows

### Example 1: Simple AI Chat
```json
{
  "name": "AI Chat",
  "definition": {
    "steps": [
      {"id": "start", "type": "start"},
      {"id": "chat", "type": "agent", "agent_id": "your-agent-id"},
      {"id": "end", "type": "end"}
    ],
    "dependencies": {
      "chat": ["start"],
      "end": ["chat"]
    }
  }
}
```

### Example 2: Conditional Flow
```json
{
  "name": "Smart Router",
  "definition": {
    "steps": [
      {"id": "start", "type": "start"},
      {"id": "check", "type": "condition", "condition": {...}},
      {"id": "yes-path", "type": "agent", "agent_id": "..."},
      {"id": "no-path", "type": "agent", "agent_id": "..."},
      {"id": "end", "type": "end"}
    ],
    "conditions": {
      "check": {
        "true_branch": "yes-path",
        "false_branch": "no-path"
      }
    }
  }
}
```

---

## 🎯 Next Steps

1. **Read full guide**: `LANGGRAPH_INTEGRATION.md`
2. **Build complex workflows**: Use conditions, loops, multi-agents
3. **Add checkpointing**: For pause/resume capability
4. **Integrate frontend**: Update UI to use LangGraph endpoint

---

## 🔧 Troubleshooting

**Error: "LangGraph not installed"**
```bash
./venv/bin/pip install langgraph
```

**Error: "Module not found"**
```bash
# Make sure you're using the venv python
./venv/bin/python -m uvicorn main:app --reload
```

**Want to see logs?**
```bash
# Backend logs show LangGraph execution
# Look for: "Executing LangGraph node: ..."
```

---

## ✅ Success Checklist

- [  ] LangGraph installed
- [ ] Backend restarted
- [ ] Test workflow created
- [ ] LangGraph execution works
- [ ] Can see message history
- [ ] State persists between nodes
- [ ] Ready to build complex flows!

---

**🎉 You're ready to build AI-powered workflows with LangGraph!**

*Quick Start Date: November 13, 2024*  
*Status: ✅ Ready to Use*
