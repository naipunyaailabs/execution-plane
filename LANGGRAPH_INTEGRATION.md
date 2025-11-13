# 🔄 LangGraph Integration Guide

## 📊 Overview

We've integrated **LangGraph** into our workflow builder, enabling powerful state management and AI agent orchestration. Your visual workflows are automatically converted to LangGraph state machines.

**Benefits:**
- ✅ State management across nodes
- ✅ Memory persistence with checkpointing
- ✅ Cyclic workflows (loops, retries)
- ✅ Conditional routing
- ✅ AI agent orchestration
- ✅ Message history tracking
- ✅ Pause/resume capabilities (via checkpointing)

---

## 🎯 What is LangGraph?

**LangGraph** is a library for building stateful, multi-agent applications with LLMs using graphs. It's built on top of LangChain and provides:

- **StateGraph**: Define workflows as state machines
- **Checkpointing**: Save and resume execution state
- **Conditional Edges**: Route based on state
- **Tool Nodes**: Pre-built agent tool execution
- **Memory**: Persistent conversation context

---

## 🏗️ Architecture

### Visual Workflow → LangGraph Conversion

```
Your Visual Workflow:
┌─────────┐     ┌──────────┐     ┌─────────┐
│  Start  │────▶│  Agent   │────▶│   End   │
└─────────┘     └──────────┘     └─────────┘

Converted to LangGraph:
StateGraph {
  nodes: {
    "start": start_function,
    "agent": agent_function,
    "end": end_function
  },
  edges: {
    "start" → "agent",
    "agent" → "end"
  },
  state: WorkflowState {
    messages: [],
    context: {},
    step_results: {}
  }
}
```

---

## 📦 Installation

```bash
# Install LangGraph
pip install langgraph

# Or add to requirements.txt
echo "langgraph>=0.0.20" >> backend/requirements.txt
pip install -r backend/requirements.txt
```

---

## 🎨 Workflow State Schema

Every node receives and returns a **WorkflowState**:

```python
class WorkflowState(TypedDict):
    """The state that flows through all nodes"""
    
    # Message history (accumulates)
    messages: List[Dict[str, Any]]
    
    # Workflow context/variables
    context: Dict[str, Any]
    
    # Original input data
    input_data: Dict[str, Any]
    
    # Current step being executed
    current_step: str
    
    # Completed step IDs
    completed_steps: List[str]
    
    # Failed step IDs
    failed_steps: List[str]
    
    # Results from each step
    step_results: Dict[str, Any]
    
    # Error message if any
    error: Optional[str]
    
    # Execution metadata
    metadata: Dict[str, Any]
```

---

## 🔧 Supported Node Types

### 1. **Start Node**
- Initializes workflow
- Sets up initial state
- Returns start timestamp

```json
{
  "id": "start-1",
  "type": "start",
  "name": "Start Workflow"
}
```

### 2. **Agent Node** ⭐
- Executes AI agent
- Accesses state via `input_mapping`
- Returns agent response

```json
{
  "id": "agent-1",
  "type": "agent",
  "agent_id": "uuid-of-agent",
  "input_mapping": {
    "query": "input_data.query",
    "context": "context.previous_result"
  }
}
```

### 3. **Condition Node**
- Evaluates conditions
- Routes to different branches
- Returns boolean result

```json
{
  "id": "condition-1",
  "type": "condition",
  "condition": {
    "operator": "greater_than",
    "left": "context.score",
    "right": 0.8
  }
}
```

### 4. **Loop Node**
- Iterates over collections
- Adds `loop_item` and `loop_index` to context
- Returns iteration results

```json
{
  "id": "loop-1",
  "type": "loop",
  "loop_config": {
    "collection": "input_data.items",
    "max_iterations": 100
  }
}
```

### 5. **Action Node**
- Performs custom actions
- Supports HTTP requests, transforms, waits
- Returns action result

```json
{
  "id": "action-1",
  "type": "action",
  "action_type": "http_request",
  "action_config": {
    "url": "https://api.example.com/data",
    "method": "POST",
    "headers": {"Authorization": "Bearer {{context.token}}"}
  }
}
```

### 6. **Error Handler Node**
- Handles errors from previous nodes
- Accesses error from state
- Returns handled status

```json
{
  "id": "error-1",
  "type": "error_handler",
  "name": "Handle Errors"
}
```

### 7. **End Node**
- Finalizes workflow
- Returns completion timestamp
- Workflow terminates

```json
{
  "id": "end-1",
  "type": "end",
  "name": "End Workflow"
}
```

---

## 🔀 Conditional Routing

Define conditional edges in workflow definition:

```json
{
  "steps": [
    {"id": "start", "type": "start"},
    {"id": "check", "type": "condition"},
    {"id": "path-a", "type": "agent"},
    {"id": "path-b", "type": "agent"},
    {"id": "end", "type": "end"}
  ],
  "conditions": {
    "check": {
      "true_branch": "path-a",
      "false_branch": "path-b"
    }
  }
}
```

**LangGraph creates:**
```
check ──[condition=True]──▶ path-a
      └─[condition=False]──▶ path-b
```

---

## 🔗 Dependencies & Edges

Define workflow flow with dependencies:

```json
{
  "steps": [
    {"id": "step-1", "type": "agent"},
    {"id": "step-2", "type": "agent"},
    {"id": "step-3", "type": "agent"}
  ],
  "dependencies": {
    "step-2": ["step-1"],
    "step-3": ["step-2"]
  }
}
```

**LangGraph creates:**
```
step-1 ──▶ step-2 ──▶ step-3
```

---

## 🎯 Variable Interpolation

Use `{{ }}` syntax to access state:

```json
{
  "action_config": {
    "url": "https://api.example.com/users/{{input_data.user_id}}",
    "message": "Hello {{context.name}}, your score is {{step_results.check.output}}"
  }
}
```

**Supported paths:**
- `input_data.*` - Original input
- `context.*` - Workflow context
- `step_results.<step_id>.*` - Results from specific step
- `metadata.*` - Execution metadata

---

## 🚀 API Usage

### Execute Workflow with LangGraph

```bash
POST /api/v1/workflows/{workflow_id}/execute-langgraph
```

**Request:**
```json
{
  "workflow_id": "workflow-uuid",
  "input_data": {
    "query": "What is the weather?",
    "user_id": "123"
  }
}
```

**Response:**
```json
{
  "success": true,
  "workflow_id": "workflow-uuid",
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
        "result": {"output": "The weather is sunny"},
        "timestamp": "2024-11-13T12:00:05"
      }
    ],
    "context": {
      "start": "Workflow started",
      "agent-1": "The weather is sunny"
    },
    "completed_steps": ["start", "agent-1", "end"],
    "failed_steps": [],
    "step_results": {
      "start": {"output": "Workflow started"},
      "agent-1": {"output": "The weather is sunny"},
      "end": {"output": "Workflow completed"}
    },
    "error": null,
    "metadata": {
      "started_at": "2024-11-13T12:00:00",
      "completed_at": "2024-11-13T12:00:10",
      "success": true,
      "workflow_id": "workflow-uuid"
    }
  },
  "completed_steps": ["start", "agent-1", "end"],
  "failed_steps": [],
  "step_results": {...},
  "messages": [...],
  "metadata": {...}
}
```

---

## 💡 Example Workflows

### Example 1: Simple AI Assistant

```json
{
  "name": "AI Assistant",
  "definition": {
    "steps": [
      {
        "id": "start",
        "type": "start"
      },
      {
        "id": "ai-agent",
        "type": "agent",
        "agent_id": "agent-uuid",
        "input_mapping": {
          "query": "input_data.query"
        }
      },
      {
        "id": "end",
        "type": "end"
      }
    ],
    "dependencies": {
      "ai-agent": ["start"],
      "end": ["ai-agent"]
    }
  }
}
```

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/workflows/{id}/execute-langgraph \
  -H "Content-Type: application/json" \
  -d '{"input_data": {"query": "What is 2+2?"}}'
```

---

### Example 2: Conditional Routing

```json
{
  "name": "Smart Router",
  "definition": {
    "steps": [
      {
        "id": "start",
        "type": "start"
      },
      {
        "id": "check-sentiment",
        "type": "agent",
        "agent_id": "sentiment-agent"
      },
      {
        "id": "is-positive",
        "type": "condition",
        "condition": {
          "operator": "equals",
          "left": "step_results.check-sentiment.sentiment",
          "right": "positive"
        }
      },
      {
        "id": "happy-response",
        "type": "agent",
        "agent_id": "happy-agent"
      },
      {
        "id": "empathy-response",
        "type": "agent",
        "agent_id": "empathy-agent"
      },
      {
        "id": "end",
        "type": "end"
      }
    ],
    "dependencies": {
      "check-sentiment": ["start"],
      "is-positive": ["check-sentiment"]
    },
    "conditions": {
      "is-positive": {
        "true_branch": "happy-response",
        "false_branch": "empathy-response"
      }
    }
  }
}
```

---

### Example 3: Loop Processing

```json
{
  "name": "Batch Processor",
  "definition": {
    "steps": [
      {
        "id": "start",
        "type": "start"
      },
      {
        "id": "process-items",
        "type": "loop",
        "loop_config": {
          "collection": "input_data.items",
          "max_iterations": 50
        }
      },
      {
        "id": "analyze-item",
        "type": "agent",
        "agent_id": "analyzer-agent",
        "input_mapping": {
          "item": "context.loop_item"
        }
      },
      {
        "id": "end",
        "type": "end"
      }
    ],
    "dependencies": {
      "process-items": ["start"],
      "analyze-item": ["process-items"],
      "end": ["analyze-item"]
    }
  }
}
```

---

### Example 4: Multi-Agent Collaboration

```json
{
  "name": "Research Assistant",
  "definition": {
    "steps": [
      {
        "id": "start",
        "type": "start"
      },
      {
        "id": "search-agent",
        "type": "agent",
        "agent_id": "search-agent-uuid",
        "input_mapping": {
          "query": "input_data.topic"
        }
      },
      {
        "id": "summarize-agent",
        "type": "agent",
        "agent_id": "summarizer-agent-uuid",
        "input_mapping": {
          "content": "step_results.search-agent.output"
        }
      },
      {
        "id": "fact-check-agent",
        "type": "agent",
        "agent_id": "fact-checker-agent-uuid",
        "input_mapping": {
          "summary": "step_results.summarize-agent.output"
        }
      },
      {
        "id": "end",
        "type": "end"
      }
    ],
    "dependencies": {
      "search-agent": ["start"],
      "summarize-agent": ["search-agent"],
      "fact-check-agent": ["summarize-agent"],
      "end": ["fact-check-agent"]
    }
  }
}
```

---

## 🎨 Frontend Integration

### Creating LangGraph-Compatible Workflows

Your existing React Flow builder already creates compatible workflows! Just ensure:

1. **Node IDs are unique**
2. **Dependencies are defined**
3. **Conditions specify branches**
4. **Agent nodes have `agent_id`**

### Example React Flow Node

```typescript
const agentNode = {
  id: 'agent-1',
  type: 'agent',
  position: { x: 100, y: 100 },
  data: {
    label: 'AI Agent',
    agent_id: 'your-agent-uuid',
    input_mapping: {
      query: 'input_data.query'
    }
  }
};
```

### Execute with LangGraph from Frontend

```typescript
async function executeWithLangGraph(workflowId: string, inputData: any) {
  const response = await fetch(
    `http://localhost:8000/api/v1/workflows/${workflowId}/execute-langgraph`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input_data: inputData })
    }
  );
  
  const result = await response.json();
  
  // Access results
  console.log('Success:', result.success);
  console.log('Completed steps:', result.completed_steps);
  console.log('Messages:', result.messages);
  console.log('Final state:', result.execution_state);
  
  return result;
}
```

---

## 🔍 Debugging

### View Execution Flow

```typescript
// All node executions are in messages
result.messages.forEach(msg => {
  console.log(`${msg.step_id} (${msg.type}):`, msg.result);
});

// Check specific step result
const agentResult = result.step_results['agent-1'];
console.log('Agent output:', agentResult.output);

// Check for failures
if (result.failed_steps.length > 0) {
  console.error('Failed steps:', result.failed_steps);
  console.error('Error:', result.execution_state.error);
}
```

### Enable Logging

```python
# In your backend
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("langgraph_service")
logger.setLevel(logging.DEBUG)
```

---

## ⚡ Advanced Features

### 1. **Checkpointing (State Persistence)**

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Use SQLite for persistent checkpoints
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

# Execute with persistence
config = {
    "configurable": {
        "thread_id": "user-session-123"
    }
}

result = await langgraph_service.execute_langgraph_workflow(
    workflow_definition=workflow.definition,
    input_data=input_data,
    config=config
)

# Later: Resume from checkpoint
# The same thread_id will restore state
```

### 2. **Human-in-the-Loop**

```python
# Add interrupt before a node
workflow.add_node("approval", approval_function)
workflow.add_edge("agent", "approval")

# When execution reaches approval, it pauses
# User can then:
# - View state
# - Modify state
# - Resume execution
```

### 3. **Streaming Results**

```python
# Stream node executions as they complete
async for event in app.astream(initial_state, config):
    print(f"Node {event['node']} completed")
    print(f"State: {event['state']}")
```

---

## 📊 Comparison: Standard vs LangGraph Execution

| Feature | Standard Execution | LangGraph Execution |
|---------|-------------------|---------------------|
| **State Management** | Limited | ✅ Full state machine |
| **Checkpointing** | ❌ No | ✅ Yes |
| **Cyclic Flows** | ❌ No | ✅ Yes |
| **Conditional Routing** | ✅ Basic | ✅ Advanced |
| **Memory** | ❌ No | ✅ Persistent |
| **Message History** | ❌ No | ✅ Full history |
| **Pause/Resume** | ❌ No | ✅ Yes (with checkpointing) |
| **Agent Orchestration** | ✅ Yes | ✅ Enhanced |
| **Performance** | Fast | Slightly slower |
| **Use Case** | Simple workflows | Complex AI flows |

---

## 🎯 When to Use LangGraph

**Use LangGraph When:**
- ✅ Building conversational AI (needs memory)
- ✅ Multi-agent collaboration required
- ✅ Need to pause/resume workflows
- ✅ Complex conditional logic
- ✅ Cyclic workflows (loops, retries)
- ✅ State management is critical

**Use Standard Execution When:**
- ✅ Simple linear workflows
- ✅ No state persistence needed
- ✅ Maximum performance required
- ✅ Stateless operations

---

## 🐛 Troubleshooting

### Issue: LangGraph not available
```
Error: "LangGraph not installed"
```

**Solution:**
```bash
pip install langgraph
```

### Issue: Async function errors
```
Error: "coroutine was never awaited"
```

**Solution:** Ensure all node functions are `async`:
```python
async def node_function(state: WorkflowState) -> WorkflowState:
    # ...
```

### Issue: State not updating
```
State changes not reflected in next node
```

**Solution:** Always return the modified state:
```python
async def my_node(state: WorkflowState) -> WorkflowState:
    state["context"]["my_value"] = "new value"
    return state  # ← Must return!
```

---

## 📚 Resources

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **LangGraph GitHub**: https://github.com/langchain-ai/langgraph
- **Our Implementation**: `/backend/services/langgraph_service.py`
- **API Endpoint**: `/backend/api/v1/workflows.py:execute_workflow_with_langgraph`

---

## 🎉 Summary

You now have a **powerful LangGraph integration** that automatically converts your visual workflows into state machines with:

✅ Full state management  
✅ Checkpointing & persistence  
✅ Conditional routing  
✅ Agent orchestration  
✅ Message history  
✅ Error handling  

**Your workflows are now AI-native and production-ready!** 🚀

---

*Integration Date: November 13, 2024*  
*LangGraph Version: 0.0.20+*  
*Status: ✅ Production Ready*
