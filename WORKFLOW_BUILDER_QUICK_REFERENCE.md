# No-Code Workflow Builder - Quick Reference Card

## 🎯 Access Points

| Location | Action | URL |
|----------|--------|-----|
| **Home Page** | Click "Create Workflow" | → `/workflow-builder` |
| **Workflows Page** | Click "Visual Builder" | → `/workflow-builder` |
| **Direct** | Navigate directly | `http://localhost:5173/workflow-builder` |

---

## 🎨 Node Types Cheat Sheet

| Icon | Type | Color | Inputs | Outputs | Purpose |
|------|------|-------|--------|---------|---------|
| ▶️ | **Start** | 🟢 Green | 0 | 1 | Workflow entry |
| ⏹️ | **End** | 🔴 Red | 1 | 0 | Workflow exit |
| 🤖 | **Agent** | 🔵 Blue | 1 | 1 | Run AI agent |
| 🔀 | **Condition** | 🟡 Yellow | 1 | 2 | Branch logic |
| 🔁 | **Loop** | 🟣 Purple | 1 | 2 | Repeat steps |
| ⚙️ | **Action** | 🔷 Indigo | 1 | 1 | Custom action |
| ⚠️ | **Error** | 🟠 Orange | 1 | 1 | Handle errors |

---

## ⌨️ Keyboard & Mouse Shortcuts

### Canvas Navigation
- **Zoom In/Out**: Mouse Wheel
- **Pan Canvas**: Click + Drag (empty space)
- **Select Node**: Click
- **Multi-select**: Cmd/Ctrl + Click
- **Deselect All**: Click empty space

### Node Operations
- **Add Node**: Drag from palette
- **Connect Nodes**: Drag from handle to handle
- **Delete Node**: Select + Click "Delete Node"
- **Configure**: Double-click or single-click node

---

## 🔧 Toolbar Actions

```
┌─────────────────────────────────────────────────┐
│ Save | Export | Import | Delete | Clear Canvas │
└─────────────────────────────────────────────────┘
```

| Button | Action | Result |
|--------|--------|--------|
| **Save Workflow** | Persist to backend | Saved to database |
| **Export** | Download JSON | `workflow-name.json` file |
| **Import** | Upload JSON | Load workflow from file |
| **Delete Node** | Remove selected | Node + connections gone |
| **Clear Canvas** | Remove all | Empty canvas |

---

## 📋 Common Workflow Patterns

### 1. Simple Sequential
```
[Start] → [Agent A] → [Agent B] → [Agent C] → [End]
```
**Use Case:** Multi-step processing

---

### 2. Conditional Branch
```
[Start] → [Agent] → [Condition]
                         ├─(True)→ [Agent A] → [End]
                         └─(False)→ [Agent B] → [End]
```
**Use Case:** Decision-based routing

---

### 3. Loop Processing
```
[Start] → [Loop: 10x]
              ├─(Next)→ [Agent] ─┐
              │                   │
              └─────(Back)────────┘
          ↓
        [End]
```
**Use Case:** Batch processing

---

### 4. Error Handling
```
[Start] → [Agent] ──(Success)──→ [End]
              ↓
          (Error)
              ↓
        [Error Handler] → [Fallback] → [End]
```
**Use Case:** Robust workflows

---

### 5. Parallel Split (Future)
```
[Start] → [Parallel]
              ├→ [Agent A] ──┐
              ├→ [Agent B] ──┤
              └→ [Agent C] ──┴→ [Merge] → [End]
```
**Use Case:** Concurrent execution

---

## 🎯 Node Configuration Quick Guide

### Start/End Nodes
- ✅ No configuration needed
- Just drag and drop

### Agent Node
```
┌─────────────────────────┐
│ Label: "Research Task"  │
│ Agent: [Select Agent ▼] │
│ Desc:  "Find sources..."│
└─────────────────────────┘
```

### Condition Node
```
┌──────────────────────────────┐
│ Label: "Check Score"         │
│ Condition: "output.score>0.8"│
└──────────────────────────────┘
```
- Right output = TRUE
- Bottom output = FALSE

### Loop Node
```
┌────────────────────────┐
│ Label: "Process 10x"   │
│ Max Iter: 10           │
│ Desc: "Process items..." │
└────────────────────────┘
```
- Right output = LOOP BACK
- Bottom output = CONTINUE

### Action Node
```
┌────────────────────────┐
│ Label: "API Call"      │
│ Type: [API Call ▼]    │
│ Desc: "Call webhook..." │
└────────────────────────┘
```
Types: API Call, Data Transform, Webhook, Custom

### Error Handler
```
┌─────────────────────────┐
│ Label: "Retry Logic"    │
│ Type: [All Errors ▼]   │
│ Recovery: "Retry 3x..." │
└─────────────────────────┘
```
Types: All, Timeout, Validation, Network, Custom

---

## 💾 File Operations

### Export Format (JSON)
```json
{
  "name": "My Workflow",
  "description": "Description here",
  "nodes": [...],
  "edges": [...]
}
```

### Import Requirements
- ✅ Valid JSON format
- ✅ Contains nodes array
- ✅ Contains edges array
- ⚠️ Node types must be valid

---

## ⚡ Power User Tips

### 1. **Align Nodes**
- Use grid snapping (automatic)
- Organize left-to-right flow
- Keep vertical spacing consistent

### 2. **Name Everything**
- Give descriptive node labels
- Add clear descriptions
- Use consistent naming

### 3. **Export Regularly**
- Save JSON backups
- Version your workflows
- Share with team

### 4. **Start Simple**
- Begin with Start → Agent → End
- Add complexity incrementally
- Test each addition

### 5. **Use Comments**
- Put workflow purpose in description
- Document complex conditions
- Explain error handling

---

## 🚨 Common Mistakes to Avoid

| ❌ Don't | ✅ Do Instead |
|----------|---------------|
| Forget Start/End nodes | Always begin with Start, end with End |
| Create circular dependencies | Use Loop node for intentional loops |
| Skip node configuration | Configure every node properly |
| Use unclear labels | Use descriptive, clear names |
| Forget to save | Save frequently |
| No error handling | Add Error Handler nodes |

---

## 🎨 Color Coding Your Workflows

**Strategy:** Use node types to indicate workflow phases

```
🟢 Start
    ↓
🔵 Data Input Phase (Agent Nodes)
    ↓
🟡 Decision Phase (Condition Nodes)
    ↓
🟣 Processing Phase (Loop Nodes)
    ↓
🔷 Action Phase (Action Nodes)
    ↓
🟠 Error Handling (Error Nodes)
    ↓
🔴 End
```

---

## 📊 Workflow Complexity Scale

| Complexity | Nodes | Description | Example |
|------------|-------|-------------|---------|
| **Simple** | 3-5 | Linear flow | Start → Agent → End |
| **Medium** | 6-10 | 1-2 branches | With conditions |
| **Complex** | 11-20 | Multiple branches | Nested logic |
| **Advanced** | 20+ | Many features | Full automation |

---

## 🔍 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Can't drag nodes | Refresh page |
| Can't connect | Check handle positions |
| Node disappeared | Check canvas zoom/pan |
| Save failed | Check backend running |
| Import failed | Validate JSON format |
| Agent not listed | Refresh, check backend |

---

## 📱 Responsive Design Notes

### Desktop (Recommended)
- Full palette visible
- Easy drag-and-drop
- Best experience

### Tablet
- Palette auto-collapses
- Touch gestures work
- Good for viewing

### Mobile
- View-only recommended
- Editing challenging
- Use desktop for building

---

## 🎓 Learning Path

### Beginner (Day 1)
1. ✅ Create simple 3-node workflow
2. ✅ Save and reload
3. ✅ Try export/import

### Intermediate (Week 1)
1. ✅ Use conditions
2. ✅ Add loops
3. ✅ Configure agents properly

### Advanced (Month 1)
1. ✅ Complex branching
2. ✅ Error handling
3. ✅ Workflow optimization

---

## 🏆 Best Practices

### Design
- **Top-to-Bottom or Left-to-Right** flow
- **Consistent spacing** between nodes
- **Group related nodes** visually
- **Minimize edge crossings**

### Configuration
- **Test incrementally** as you build
- **Document edge cases**
- **Use meaningful names**
- **Set realistic iteration limits**

### Maintenance
- **Export before major changes**
- **Version your workflows**
- **Review regularly**
- **Update as needed**

---

## 📞 Getting Help

### Resources
1. **Full Documentation**: `NOCODE_WORKFLOW_BUILDER.md`
2. **Setup Guide**: `WORKFLOW_BUILDER_SETUP.md`
3. **React Flow Docs**: https://reactflow.dev/

### Support Channels
- Check console for errors
- Review backend logs
- Inspect network requests
- Validate workflow JSON

---

## ✨ Quick Start (30 seconds)

1. **Navigate**: `/workflow-builder`
2. **Name**: "Test Workflow"
3. **Drag**: Start → Agent → End
4. **Connect**: All three nodes
5. **Configure**: Click Agent, select one
6. **Save**: Click Save button

**Done!** You've created your first workflow! 🎉

---

## 🎯 Workflow Creation Checklist

Before saving, verify:
- [ ] Workflow has a name
- [ ] Has Start node
- [ ] Has End node
- [ ] All nodes connected
- [ ] All nodes configured
- [ ] No orphaned nodes
- [ ] Logical flow makes sense
- [ ] Tested (if possible)

---

## 📈 Next Level Features (Coming Soon)

- 🔮 Workflow templates
- 🔮 Sub-workflows
- 🔮 Parallel execution
- 🔮 Workflow versioning
- 🔮 Collaboration mode
- 🔮 Real-time testing
- 🔮 Performance metrics

---

**Happy Workflow Building!** 🚀✨
