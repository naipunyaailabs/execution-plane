# No-Code Workflow Builder - Setup & Installation

## ✅ Installation Complete

All files have been created and integrated. Follow these steps to get started.

---

## 📦 Required Dependencies

The workflow builder requires the React Flow library. If not already installed, run:

```bash
cd frontend
npm install reactflow
# or
yarn add reactflow
# or
pnpm add reactflow
```

---

## 🗂️ Files Created

### Components
1. **CustomNodes.tsx** - 7 custom node type definitions
2. **NodePalette.tsx** - Draggable node palette sidebar
3. **NoCodeWorkflowBuilder.tsx** - Main workflow builder component

### Updated Files
1. **workflow/index.ts** - Export new components
2. **App.tsx** - Added `/workflow-builder` route
3. **pages/Index.tsx** - Updated "Create Workflow" button
4. **pages/Workflows.tsx** - Added "Visual Builder" button

---

## 🚀 Quick Start

### 1. Install Dependencies (if needed)
```bash
cd /Users/apple/Desktop/execution-plane/frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

### 3. Access the Builder
Open browser and navigate to:
- **Direct URL:** `http://localhost:5173/workflow-builder`
- **From Home:** Click "Create Workflow" button
- **From Workflows:** Click "Visual Builder" button

---

## 🎯 First Workflow Tutorial

### Step 1: Create New Workflow
1. Navigate to `/workflow-builder`
2. Enter workflow name: "My First Workflow"
3. Enter description: "A simple agent workflow"

### Step 2: Add Nodes
1. **Drag "Start"** from palette to canvas (left side)
2. **Drag "Agent"** to the right of Start
3. **Drag "End"** to the right of Agent

### Step 3: Connect Nodes
1. Click and drag from **Start's bottom handle**
2. Drop on **Agent's top handle**
3. Click and drag from **Agent's bottom handle**
4. Drop on **End's top handle**

### Step 4: Configure Agent
1. Click the **Agent node**
2. In dialog, select an agent from dropdown
3. Add description: "Process the input data"
4. Click "Save"

### Step 5: Save Workflow
1. Click **"Save Workflow"** button in toolbar
2. Wait for success toast notification
3. Workflow is now saved to backend

---

## 🎨 Node Types Reference

### Visual Guide
```
🟢 START        Entry point (green, rounded)
🔴 END          Exit point (red, rounded)
🤖 AGENT        AI agent task (blue, rectangular)
🔀 CONDITION    Branch logic (yellow, diamond)
🔁 LOOP         Repeat actions (purple, dashed)
⚙️  ACTION       Custom action (indigo, rectangular)
⚠️  ERROR        Error handler (orange, rectangular)
```

### Connection Rules
- **Start Node**: Only outgoing connections
- **End Node**: Only incoming connections
- **Agent Node**: One input, one output
- **Condition Node**: One input, two outputs (true/false)
- **Loop Node**: One input, two outputs (continue/loop back)
- **Action Node**: One input, one output
- **Error Handler**: One input, one output

---

## 🔧 Canvas Controls

### React Flow Controls
- **Zoom In/Out**: Mouse wheel or controls
- **Pan**: Click and drag on empty space
- **Fit View**: Click fit view button
- **MiniMap**: Overview in bottom-right
- **Select Node**: Single click
- **Multi-select**: Cmd/Ctrl + click

### Toolbar Actions
- **Save Workflow**: Persist to backend
- **Export**: Download as JSON
- **Import**: Load from JSON file
- **Delete Node**: Remove selected node
- **Clear Canvas**: Remove all nodes

---

## 📡 Backend Requirements

### Endpoints Needed
1. **GET /api/v1/agents/** - List available agents
2. **POST /api/v1/workflows** - Save workflow

### Expected Response Format

#### Agents List
```json
[
  {
    "agent_id": "uuid",
    "name": "Agent Name"
  }
]
```

#### Workflow Create
```json
{
  "name": "Workflow Name",
  "description": "Description",
  "definition": {
    "steps": [...],
    "dependencies": {...},
    "conditions": {}
  }
}
```

---

## 🎨 Customization Options

### Adding New Node Types

1. **Add to CustomNodes.tsx**
```tsx
export const MyCustomNode = ({ data, selected }: NodeProps) => {
  return (
    <div className="custom-node-styles">
      <Handle type="target" position={Position.Top} />
      {/* Your node content */}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
};

// Add to exports
export const nodeTypes = {
  // ... existing types
  myCustomNode: MyCustomNode,
};
```

2. **Add to NodePalette.tsx**
```tsx
const nodeTypeConfigs: NodeTypeConfig[] = [
  // ... existing configs
  {
    type: "myCustomNode",
    label: "My Custom",
    icon: MyIcon,
    description: "Description",
    color: "text-custom-600",
    bgColor: "bg-custom-50 hover:bg-custom-100",
  },
];
```

3. **Add configuration in NoCodeWorkflowBuilder.tsx**
```tsx
// In getDefaultNodeData()
case "myCustomNode":
  return { label: "Custom", customField: "" };

// In configuration dialog
{selectedNode.type === "myCustomNode" && (
  <div>
    {/* Custom configuration fields */}
  </div>
)}
```

---

## 🐛 Common Issues & Solutions

### Issue: "reactflow is not defined"
**Solution:**
```bash
npm install reactflow
```

### Issue: Nodes not appearing in palette
**Solution:** Check NodePalette.tsx configuration array

### Issue: Cannot connect nodes
**Solution:** Verify Handle components in CustomNodes.tsx

### Issue: Workflow not saving
**Solution:** Check backend API is running and CORS configured

### Issue: Dark mode colors wrong
**Solution:** Add dark: classes to Tailwind CSS

---

## 🔍 File Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── workflow/
│   │       ├── CustomNodes.tsx          ✨ NEW
│   │       ├── NodePalette.tsx          ✨ NEW
│   │       ├── NoCodeWorkflowBuilder.tsx ✨ NEW
│   │       ├── VisualWorkflowBuilder.tsx (existing)
│   │       ├── WorkflowBuilder.tsx      (existing)
│   │       ├── WorkflowList.tsx         (existing)
│   │       └── index.ts                 📝 UPDATED
│   ├── pages/
│   │   ├── Index.tsx                    📝 UPDATED
│   │   └── Workflows.tsx                📝 UPDATED
│   └── App.tsx                          📝 UPDATED
```

---

## 📊 Performance Tips

### Optimize for Large Workflows
1. **Use React Flow's Built-in Optimization**
   - Already implemented: fitView, Controls, MiniMap
   
2. **Limit Node Complexity**
   - Keep node data minimal
   - Avoid heavy computations in node render

3. **Batch Updates**
   - Use setNodes/setEdges for multiple changes
   
4. **Lazy Load Agents**
   - Already implemented: useEffect on mount

---

## 🎯 Testing Checklist

### Functionality Tests
- [ ] Drag node from palette to canvas
- [ ] Connect two nodes
- [ ] Click node to open config dialog
- [ ] Save node configuration
- [ ] Delete a node
- [ ] Save complete workflow
- [ ] Export workflow as JSON
- [ ] Import workflow from JSON
- [ ] Clear canvas
- [ ] Navigate back to home

### Visual Tests
- [ ] Light mode renders correctly
- [ ] Dark mode renders correctly
- [ ] All node types display properly
- [ ] Icons render correctly
- [ ] Connections animate smoothly
- [ ] MiniMap updates in real-time
- [ ] Controls work (zoom, fit view)

### Integration Tests
- [ ] Backend saves workflow
- [ ] Agents load from API
- [ ] Toast notifications appear
- [ ] Navigation works
- [ ] Protected route redirects

---

## 📚 Resources

### React Flow Documentation
- **Official Docs:** https://reactflow.dev/
- **Examples:** https://reactflow.dev/examples
- **API Reference:** https://reactflow.dev/api-reference

### Related Technologies
- **Tailwind CSS:** https://tailwindcss.com/
- **shadcn/ui:** https://ui.shadcn.com/
- **Lucide Icons:** https://lucide.dev/

---

## 🎉 Success Criteria

You'll know everything is working when:

✅ You can drag nodes onto the canvas
✅ Nodes connect with animated edges
✅ Configuration dialog opens and saves
✅ Workflow saves to backend successfully
✅ Export creates valid JSON file
✅ Import loads workflow correctly
✅ All navigation links work
✅ Dark/light mode both look good

---

## 🚀 Next Steps

1. **Test the Builder**
   - Create a few test workflows
   - Try all node types
   - Test import/export

2. **Backend Integration**
   - Ensure workflow API endpoint works
   - Test workflow execution

3. **User Training**
   - Create workflow templates
   - Document best practices
   - Share example workflows

4. **Future Enhancements**
   - Add more node types
   - Implement workflow versioning
   - Add collaboration features

---

## 💡 Tips for Success

- **Start Simple**: Begin with linear workflows (Start → Agent → End)
- **Use Descriptions**: Document what each node does
- **Export Often**: Save your work as JSON backups
- **Name Clearly**: Use descriptive workflow and node names
- **Test Incrementally**: Validate as you build

---

## ✨ You're All Set!

The No-Code Workflow Builder is ready to use. Start creating visual AI workflows and let us know if you need any help! 🎊
