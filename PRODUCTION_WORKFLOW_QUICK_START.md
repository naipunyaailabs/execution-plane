# Production Workflow Builder - Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will help you create your first production-ready workflow in minutes.

---

## 📋 Prerequisites

- Frontend running: `cd frontend && npm run dev`
- Backend API running: `http://localhost:8000`
- Logged in to the application

---

## 🎯 Quick Start

### Access the Builder
```
http://localhost:5173/production-workflow
```

Or click **"Create Workflow"** from the home page.

---

## 🏗️ Build Your First Workflow (2 minutes)

### Step 1: Name Your Workflow
```
Name: Email Notification Workflow
Description: Send email when new order is created
```

### Step 2: Add Nodes (Drag & Drop)
1. Drag **Start** node from left sidebar
2. Drag **Agent** node
3. Drag **Action** node  
4. Drag **End** node

### Step 3: Connect Nodes
- Click and drag from Start's **bottom** handle
- Drop on Agent's **top** handle
- Connect Agent → Action
- Connect Action → End

### Step 4: Configure Nodes

#### Agent Node
```
Click Agent node → Configure:
- Name: "Process Order Data"
- Agent: Select from dropdown
- Description: "Extract order details"
```

#### Action Node
```
Click Action node → Configure:
- Name: "Send Email"
- Type: "API Call"
```

### Step 5: Save & Test
```
1. Click "Save" button
2. Enable "Test Mode" checkbox
3. Click "Execute"
4. View results in execution history
```

**Congratulations! You've created your first workflow!** 🎉

---

## 🔐 Add Credentials (3 minutes)

### Step 1: Open Credentials Manager
- Click **🔑 Credentials** tab in sidebar

### Step 2: Add API Credential
```
1. Click "Add Credential"
2. Name: "Email Service API"
3. Type: "API Key"
4. API Key: [your-api-key]
5. Click "Create Credential"
```

### Step 3: Use in Workflow
```
1. Click any Agent or Action node
2. Select credential from dropdown
3. Save node configuration
```

**Credentials are now securely stored!** 🔒

---

## ⚡ Add Webhook Trigger (2 minutes)

### Step 1: Open Triggers
- Click **⚡ Triggers** tab in sidebar

### Step 2: Create Webhook
```
1. Click "Add Trigger"
2. Name: "Order Created Webhook"
3. Type: "Webhook"
4. Method: "POST"
5. Auth: "API Key"
6. Click "Create Trigger"
```

### Step 3: Copy Webhook URL
```
https://yourapp.com/api/v1/webhooks/{workflowId}/{triggerId}
```

### Step 4: Test Webhook
```bash
curl -X POST https://yourapp.com/api/v1/webhooks/... \
  -H "Content-Type: application/json" \
  -d '{"orderId": "12345", "amount": 99.99}'
```

**Your workflow now responds to webhooks!** 🎯

---

## 🕐 Add Schedule Trigger (2 minutes)

### Step 1: Create Schedule
```
1. Click "Add Trigger" in Triggers tab
2. Name: "Daily Report"
3. Type: "Schedule"
4. Cron: "0 9 * * *"  (Every day at 9 AM)
5. Timezone: "UTC"
6. Click "Create Trigger"
```

### Common Schedules
```
0 * * * *      # Every hour
*/30 * * * *   # Every 30 minutes
0 0 * * *      # Daily at midnight
0 9 * * 1      # Every Monday at 9 AM
0 0 1 * *      # First day of month
```

**Workflow will run automatically on schedule!** ⏰

---

## 🔧 Use Expressions (3 minutes)

### Step 1: Add Parameters
```
1. Click any Agent node
2. Go to "Parameters" tab
3. Add parameter:
   - Key: "customerEmail"
   - Value: {{ $json.email }}
```

### Step 2: Common Expressions
```javascript
// Access data
{{ $json.fieldName }}
{{ $node.PreviousNode.json.value }}

// Transform data
{{ $json.name.toUpperCase() }}
{{ $json.price * 1.2 }}

// Conditions
{{ $json.score > 80 ? 'pass' : 'fail' }}

// Arrays
{{ $json.items.length }}
{{ $json.items[0].name }}
```

### Step 3: Test Expression
```
1. Click expression editor icon
2. Enter expression
3. Provide test input JSON
4. Click "Test"
5. View output
```

**Data flows dynamically between nodes!** 🔄

---

## 🐛 Debug Workflow (2 minutes)

### View Execution History
```
1. Click 🕐 History tab
2. Select recent execution
3. View node-by-node results
4. Check errors and outputs
```

### Enable Test Mode
```
1. Check "Test Mode" checkbox
2. Enter test data:
   {
     "orderId": "TEST123",
     "amount": 50.00
   }
3. Click "Test Run"
4. View outputs without side effects
```

### View Node Output
```
1. Execute workflow
2. Click any node
3. Go to "Output" tab
4. View last execution data
```

**Debug issues quickly!** 🔍

---

## 🎛️ Execution Controls

### Run Workflow
```
Click [▶️ Execute] button
```

### Pause Execution
```
During execution, click [⏸️ Pause]
Resume with [▶️ Resume]
```

### Stop Execution
```
Click [⏹️ Stop] to terminate immediately
```

### Monitor Progress
- Watch node status change colors
- Green = completed
- Blue = running
- Red = failed

---

## 📊 Common Workflows

### 1. Simple API Integration
```
[Start]
  → [Agent: Fetch API Data]
  → [Action: Transform Data]
  → [Action: Save to Database]
  → [End]
```

**Time: 5 minutes**

---

### 2. Conditional Processing
```
[Start]
  → [Agent: Analyze Input]
  → [Condition: Score > 80?]
      ├─ (Yes) → [Agent: Approve]
      └─ (No) → [Agent: Review]
  → [End]
```

**Time: 7 minutes**

---

### 3. Scheduled Report
```
[Start]
  → [Schedule: Daily 9 AM]
  → [Agent: Gather Data]
  → [Loop: For each department]
      → [Agent: Generate Report]
  → [Action: Email Summary]
  → [End]
```

**Time: 10 minutes**

---

### 4. Webhook to Email
```
[Start]
  → [Webhook: POST /webhook]
  → [Agent: Extract Data]
  → [Action: Send Email]
  → [End]
```

**Time: 5 minutes**

---

## 💡 Pro Tips

### Organize Your Workflow
- Use descriptive node names
- Group related nodes visually
- Add descriptions to complex nodes
- Keep workflows focused on one task

### Performance
- Limit loop iterations (max 100)
- Cache credential lookups
- Use test mode before production
- Monitor execution times

### Security
- Store all secrets in Credentials
- Use API key auth for webhooks
- Validate input data
- Set reasonable timeouts

### Debugging
- Enable test mode for development
- Check execution history frequently
- Use expression tester
- Add error handler nodes

### Best Practices
- Save frequently
- Export backups regularly
- Document complex expressions
- Test with sample data first
- Monitor execution history

---

## 🚨 Troubleshooting

### Workflow Won't Execute
```
✓ Check all nodes are connected
✓ Verify Start and End nodes exist
✓ Ensure agents are configured
✓ Check credentials are valid
```

### Node Execution Failed
```
✓ View error in execution history
✓ Check node configuration
✓ Verify credentials
✓ Test expressions in editor
```

### Webhook Not Working
```
✓ Check webhook URL is correct
✓ Verify authentication
✓ Test with curl/Postman
✓ Check backend logs
```

### Expression Error
```
✓ Use expression editor to test
✓ Check syntax ({{ }})
✓ Verify data structure
✓ Review available variables
```

---

## 📚 Next Steps

### Learn More
1. Read [PRODUCTION_WORKFLOW_BUILDER.md](./PRODUCTION_WORKFLOW_BUILDER.md)
2. Explore expression examples
3. Try different node types
4. Create workflow templates

### Build Complex Workflows
1. Combine multiple triggers
2. Use loops for batch processing
3. Add error handlers
4. Implement retry logic

### Production Deployment
1. Set up monitoring
2. Configure alerts
3. Backup workflows
4. Document processes

---

## 🎯 Quick Reference

### Essential Shortcuts
| Action | Method |
|--------|--------|
| Add Node | Drag from palette |
| Connect | Drag from handle |
| Configure | Click node |
| Execute | Click Execute button |
| Pause | Click Pause button |
| Test | Enable Test Mode |

### Key Tabs
| Tab | Purpose |
|-----|---------|
| Nodes | Add workflow nodes |
| ⚡ Triggers | Configure webhooks/schedules |
| 🔑 Credentials | Manage API keys |
| 🕐 History | View executions |

### Node Types
| Type | Icon | Use For |
|------|------|---------|
| Start | 🟢 | Workflow entry |
| End | 🔴 | Workflow exit |
| Agent | 🤖 | AI processing |
| Condition | 🔀 | Branch logic |
| Loop | 🔁 | Iterations |
| Action | ⚙️ | API calls |
| Error | ⚠️ | Error handling |

---

## ✅ Checklist: Your First Workflow

- [ ] Access production builder
- [ ] Create and name workflow
- [ ] Add Start, Agent, Action, End nodes
- [ ] Connect all nodes
- [ ] Configure each node
- [ ] Save workflow
- [ ] Add credential (if needed)
- [ ] Add trigger
- [ ] Test with test mode
- [ ] Execute workflow
- [ ] View execution history
- [ ] Export backup

---

## 🎊 You're Ready!

You now know how to:
- ✅ Create workflows
- ✅ Use credentials securely
- ✅ Add webhooks and schedules
- ✅ Write expressions
- ✅ Debug executions
- ✅ Deploy to production

**Start building powerful automation workflows!** 🚀

---

## 📞 Need Help?

### Documentation
- Full guide: `PRODUCTION_WORKFLOW_BUILDER.md`
- API docs: `API_DOCUMENTATION.md`

### Support
- Check execution history for errors
- Review expression syntax
- Test in test mode first
- Export workflows for backup

---

**Happy Automating!** ✨🎯🔥
