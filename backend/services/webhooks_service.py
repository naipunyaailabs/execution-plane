"""
Webhooks Service
Manages webhook triggers for workflow execution
"""
import uuid
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from models.workflow import Workflow

logger = logging.getLogger(__name__)


class WebhooksService:
    """Service for managing webhook triggers"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_webhook_trigger(self, workflow_id: str, trigger_data: Dict[str, Any]) -> dict:
        """Create a new webhook trigger for a workflow"""
        # Get the workflow
        workflow = self.db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
        
        if not workflow:
            raise ValueError("Workflow not found")
        
        trigger_id = str(uuid.uuid4())
        
        # Get existing definition
        definition = workflow.definition or {}
        triggers = definition.get("triggers", [])
        
        # Create new trigger
        new_trigger = {
            "id": trigger_id,
            "type": "webhook",
            "name": trigger_data.get("name", "Webhook Trigger"),
            "method": trigger_data.get("method", "POST"),
            "auth_type": trigger_data.get("auth_type", "none"),
            "auth_config": trigger_data.get("auth_config", {}),
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        triggers.append(new_trigger)
        definition["triggers"] = triggers
        
        # Update workflow
        workflow.definition = definition
        workflow.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(workflow)
        
        # Generate webhook URL
        new_trigger["webhook_url"] = f"/api/v1/webhooks/{workflow_id}/{trigger_id}"
        
        return new_trigger
    
    async def get_webhook_trigger(self, workflow_id: str, trigger_id: str) -> Optional[dict]:
        """Get a specific webhook trigger"""
        workflow = self.db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
        
        if not workflow:
            return None
        
        definition = workflow.definition or {}
        triggers = definition.get("triggers", [])
        
        for trigger in triggers:
            if trigger.get("id") == trigger_id and trigger.get("type") == "webhook":
                trigger["webhook_url"] = f"/api/v1/webhooks/{workflow_id}/{trigger_id}"
                return trigger
        
        return None
    
    async def list_workflow_webhooks(self, workflow_id: str) -> List[dict]:
        """List all webhook triggers for a workflow"""
        workflow = self.db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
        
        if not workflow:
            return []
        
        definition = workflow.definition or {}
        triggers = definition.get("triggers", [])
        
        # Filter only webhook triggers
        webhook_triggers = [
            {
                **trigger,
                "webhook_url": f"/api/v1/webhooks/{workflow_id}/{trigger['id']}"
            }
            for trigger in triggers
            if trigger.get("type") == "webhook"
        ]
        
        return webhook_triggers
    
    async def update_webhook_trigger(self, workflow_id: str, trigger_id: str, trigger_data: Dict[str, Any]) -> Optional[dict]:
        """Update a webhook trigger"""
        workflow = self.db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
        
        if not workflow:
            return None
        
        definition = workflow.definition or {}
        triggers = definition.get("triggers", [])
        
        # Find and update trigger
        updated = False
        for i, trigger in enumerate(triggers):
            if trigger.get("id") == trigger_id and trigger.get("type") == "webhook":
                # Update fields
                if "name" in trigger_data:
                    trigger["name"] = trigger_data["name"]
                if "method" in trigger_data:
                    trigger["method"] = trigger_data["method"]
                if "auth_type" in trigger_data:
                    trigger["auth_type"] = trigger_data["auth_type"]
                if "auth_config" in trigger_data:
                    trigger["auth_config"] = trigger_data["auth_config"]
                if "is_active" in trigger_data:
                    trigger["is_active"] = trigger_data["is_active"]
                
                trigger["updated_at"] = datetime.utcnow().isoformat()
                triggers[i] = trigger
                updated = True
                break
        
        if not updated:
            return None
        
        # Update workflow
        definition["triggers"] = triggers
        workflow.definition = definition
        workflow.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(workflow)
        
        # Find the updated trigger
        for trigger in triggers:
            if trigger.get("id") == trigger_id:
                trigger["webhook_url"] = f"/api/v1/webhooks/{workflow_id}/{trigger_id}"
                return trigger
        
        return None
    
    async def delete_webhook_trigger(self, workflow_id: str, trigger_id: str) -> bool:
        """Delete a webhook trigger"""
        workflow = self.db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
        
        if not workflow:
            return False
        
        definition = workflow.definition or {}
        triggers = definition.get("triggers", [])
        
        # Remove trigger
        original_length = len(triggers)
        triggers = [t for t in triggers if not (t.get("id") == trigger_id and t.get("type") == "webhook")]
        
        if len(triggers) == original_length:
            return False
        
        # Update workflow
        definition["triggers"] = triggers
        workflow.definition = definition
        workflow.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
