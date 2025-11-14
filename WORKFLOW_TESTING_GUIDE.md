# Workflow Testing Guide

## ✅ Fixes Implemented

### 1. **Removed Advanced Tab from Agent Nodes** ✅
- Agent nodes now show only: General, Parameters, Output tabs
- Cleaner, simpler configuration for agents
- Advanced settings moved to action nodes where they're more relevant

### 2. **Added Workflow Execution Input Dialog** ✅
- When you click "Execute Workflow", an input dialog appears
- Provide JSON input data that will be available to all nodes
- Input is accessible via `{{ $json.fieldName }}` expressions
- Example:
  ```json
  {
    "query": "What is the capital of France?",
    "user_id": "123",
    "context": "geography"
  }
  ```

### 3. **Created Chat/Manual Trigger Node** ✅
- New node type: **Chat / Manual**
- Like n8n's Manual Trigger node
- Perfect for interactive workflows
- Can be used instead of Start node for user-initiated workflows

---

## 🧪 Testing: Simple Start → Agent → Stop Workflow

### Prerequisites

1. **Agent Must Exist**
   - Go to `/agents` in the UI
   - Create an agent named "cognitbotz" (or any name)
   - Configure it with:
     - Model: Any (e.g., gpt-4, claude-3-5-sonnet)
     - Instructions: "You are a helpful assistant"
     - Temperature: 0.7

### Test Workflow 1: Basic Agent Query

**Steps:**

1. **Create Workflow**
   - Go to `/production-workflow`
   - Name: "Test Agent Workflow"
   - Description: "Simple workflow to test agent execution"

2. **Add Nodes**
   - Drag **Start** node to canvas
   - Drag **Agent** node to canvas
   - Drag **End** node to canvas
   - Connect them: Start → Agent → End

3. **Configure Agent Node**
   - Click the Agent node
   - **General Tab:**
     - Node Name: "Ask Agent"
     - Select Agent: Choose "cognitbotz" (or your agent name)
     - Description: "Query the agent"
   
   - **Parameters Tab:**
     - Click "Add Parameter"
     - Key: `query`
     - Value: `{{ $json.query }}`
     - This maps the input query to the agent's query parameter

4. **Save Workflow**
   - Click "Save Workflow" button
   - Should see success toast

5. **Execute Workflow**
   - Click "Execute" button (Play icon)
   - **Input Dialog appears!** 📝
   - Enter JSON input:
     ```json
     {
       "query": "What is the capital of France?"
     }
     ```
   - Click "Execute Workflow"

6. **View Results**
   - Workflow executes
   - Check Execution History tab
   - Should see completed execution
   - Click Agent node → Output tab → See agent response

**Expected Result:** ✅
- Agent receives "What is the capital of France?"
- Agent responds with "Paris" (or similar answer)
- Workflow completes successfully
- Output visible in node and execution history

---

### Test Workflow 2: Chat Node Workflow

**Steps:**

1. **Create New Workflow**
   - Name: "Interactive Chat Workflow"

2. **Add Nodes**
   - Drag **Chat / Manual** node (NEW! 🎉)
   - Drag **Agent** node
   - Drag **End** node
   - Connect: Chat → Agent → End

3. **Configure Chat Node**
   - Click Chat node
   - Name: "User Input"
   - Welcome Message: "Hello! Ask me anything about AI."

4. **Configure Agent Node**
   - Select your agent
   - **Parameters:**
     - Key: `query`
     - Value: `{{ $json.query }}`

5. **Execute**
   - Click Execute
   - Provide input in dialog
   - Watch it flow through the workflow

---

## 🔍 What to Verify

### ✅ Input Flow
- [ ] Input dialog appears when clicking Execute
- [ ] JSON input can be provided
- [ ] Input validation works (shows error for invalid JSON)
- [ ] Input is passed to workflow execution

### ✅ Agent Configuration
- [ ] Agent dropdown shows available agents
- [ ] Can select "cognitbotz" agent
- [ ] No Advanced tab visible for agent nodes
- [ ] Only 3 tabs: General, Parameters, Output

### ✅ Parameter Mapping
- [ ] Can add parameters in Parameters tab
- [ ] Expression `{{ $json.query }}` works
- [ ] Agent receives the query from input data
- [ ] Agent executes successfully

### ✅ Workflow Execution
- [ ] Workflow validates before execution
- [ ] Shows proper error if agent not selected
- [ ] Executes all nodes in order
- [ ] Updates node status during execution
- [ ] Shows results in Output tab

### ✅ New Chat Node
- [ ] Chat node appears in palette
- [ ] Can drag and drop to canvas
- [ ] Has cyan color and MessageSquare icon
- [ ] Can be configured
- [ ] Acts as manual trigger

---

## 🐛 Common Issues & Solutions

### Issue 1: "No agent_id specified"
**Cause:** Agent not selected in node configuration
**Solution:** Click agent node → General tab → Select agent from dropdown

### Issue 2: "Cannot find agent"
**Cause:** Agent doesn't exist or wrong ID
**Solution:** 
1. Go to `/agents`
2. Create agent first
3. Copy agent name/ID
4. Use in workflow

### Issue 3: Agent doesn't receive input
**Cause:** Parameters not mapped correctly
**Solution:**
1. Click agent node → Parameters tab
2. Add parameter: `query` → `{{ $json.query }}`
3. Ensure input JSON has `query` field

### Issue 4: Execution hangs
**Cause:** Node not connected properly
**Solution:** Verify all nodes connected with edges

### Issue 5: Invalid JSON error
**Cause:** Malformed JSON in input dialog
**Solution:** Validate JSON syntax - use proper quotes, commas, brackets

---

## 📊 Test Data Examples

### Simple Query
```json
{
  "query": "Explain quantum computing in simple terms"
}
```

### With Context
```json
{
  "query": "What are the benefits?",
  "context": "We're discussing solar panels",
  "user_id": "user_123"
}
```

### Multiple Parameters
```json
{
  "query": "Translate this to Spanish",
  "text": "Hello, how are you?",
  "target_language": "Spanish",
  "formal": true
}
```

### Conversation
```json
{
  "query": "Continue our discussion about AI",
  "conversation_history": [
    {"role": "user", "content": "What is AI?"},
    {"role": "assistant", "content": "AI is..."}
  ]
}
```

---

## 🎯 Success Criteria

### Minimum Viable Test ✅
- [ ] Create workflow with Start → Agent → End
- [ ] Select cognitbotz agent
- [ ] Map query parameter: `{{ $json.query }}`
- [ ] Execute with input: `{"query": "test"}`
- [ ] Workflow completes successfully
- [ ] See agent response in Output tab

### Full Feature Test ✅
- [ ] All above ✅
- [ ] Try Chat node instead of Start
- [ ] Test multiple parameter mappings
- [ ] Test complex JSON input
- [ ] Verify execution history saves correctly
- [ ] Test error handling (no agent selected)

---

## 🚀 Advanced Test Scenarios

### Scenario 1: Conditional Agent Response
```
Start → Agent → Condition (check response) → [True: End, False: Agent again]
```

### Scenario 2: Loop Through Questions
```
Start → Loop (questions array) → Agent → End
Input: { "questions": ["Q1", "Q2", "Q3"] }
```

### Scenario 3: Agent Chain
```
Chat → Agent 1 (research) → Agent 2 (summarize) → End
```

---

## 📝 Notes

### Input Data Access Patterns
- In agent parameters: `{{ $json.fieldName }}`
- In conditions: `{{ $json.score > 0.5 }}`
- In actions: `{{ $json.url }}`

### Agent Parameter Naming
- `query` - Main question/prompt
- `input` - Alternative to query
- `text` - Text to process
- `context` - Additional context
- Custom parameters work too!

### Best Practices
1. Always provide `query` or `input` parameter for agents
2. Use descriptive node names
3. Add descriptions to complex nodes
4. Test with simple input first
5. Check execution history for debugging

---

## ✅ Verification Checklist

Before marking as complete, verify:

- [x] Advanced tab removed from agent nodes
- [x] Execution input dialog added
- [x] Chat/Manual node created and working
- [ ] **Test workflow executes successfully**
- [ ] Agent receives input correctly
- [ ] Output visible in node
- [ ] Execution history records properly
- [ ] No console errors
- [ ] UI is responsive

---

**Ready to test! Follow the "Test Workflow 1" steps above to verify everything works.** 🎉
