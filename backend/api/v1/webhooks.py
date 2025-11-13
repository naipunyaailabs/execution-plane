"""
Webhooks API Endpoints
Handles webhook triggers for workflow execution
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import hmac
import hashlib

from core.database import get_db
from services.workflow_service import WorkflowService
from services.webhooks_service import WebhooksService
from schemas.workflow import WorkflowExecutionCreate

router = APIRouter()


@router.post("/{workflow_id}/{trigger_id}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_workflow_webhook(
    workflow_id: str,
    trigger_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Trigger workflow execution via webhook
    
    Accepts POST, GET, or PUT requests and executes the associated workflow
    with the provided data as input
    """
    webhooks_service = WebhooksService(db)
    
    try:
        # Get the webhook trigger configuration
        trigger = await webhooks_service.get_webhook_trigger(workflow_id, trigger_id)
        
        if not trigger:
            raise HTTPException(status_code=404, detail="Webhook trigger not found")
        
        if not trigger.get("is_active", False):
            raise HTTPException(status_code=403, detail="Webhook trigger is disabled")
        
        # Validate authentication
        auth_type = trigger.get("auth_type", "none")
        
        if auth_type == "api_key":
            # Validate API key
            expected_key = trigger.get("auth_config", {}).get("api_key")
            if not authorization or authorization != f"Bearer {expected_key}":
                raise HTTPException(status_code=401, detail="Invalid API key")
        
        elif auth_type == "bearer":
            # Validate bearer token
            expected_token = trigger.get("auth_config", {}).get("token")
            if not authorization or authorization != f"Bearer {expected_token}":
                raise HTTPException(status_code=401, detail="Invalid bearer token")
        
        # Get request data
        method = request.method
        
        if method == "POST" or method == "PUT":
            try:
                input_data = await request.json()
            except Exception:
                input_data = {}
        elif method == "GET":
            input_data = dict(request.query_params)
        else:
            raise HTTPException(status_code=405, detail=f"Method {method} not allowed")
        
        # Add webhook metadata
        input_data["_webhook"] = {
            "trigger_id": trigger_id,
            "method": method,
            "headers": dict(request.headers),
            "timestamp": str(request.state.start_time) if hasattr(request.state, 'start_time') else None
        }
        
        # Execute the workflow asynchronously
        workflow_service = WorkflowService(db)
        execution_data = WorkflowExecutionCreate(
            workflow_id=workflow_id,
            input_data=input_data
        )
        execution = await workflow_service.create_workflow_execution(execution_data)
        
        # Queue the execution (in a production system, use a task queue like Celery or RQ)
        # For now, we'll execute synchronously
        try:
            result = await workflow_service.execute_workflow(workflow_id, input_data)
            return {
                "success": True,
                "execution_id": execution.execution_id,
                "status": result.status,
                "message": "Workflow execution completed"
            }
        except Exception as e:
            return {
                "success": False,
                "execution_id": execution.execution_id,
                "error": str(e),
                "message": "Workflow execution failed"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


@router.get("/{workflow_id}/triggers")
async def list_workflow_webhooks(
    workflow_id: str,
    db: Session = Depends(get_db)
):
    """
    List all webhook triggers for a workflow
    """
    webhooks_service = WebhooksService(db)
    
    try:
        triggers = await webhooks_service.list_workflow_webhooks(workflow_id)
        return triggers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list webhooks: {str(e)}")


@router.post("/{workflow_id}/triggers")
async def create_workflow_webhook(
    workflow_id: str,
    trigger_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Create a new webhook trigger for a workflow
    """
    webhooks_service = WebhooksService(db)
    
    try:
        trigger = await webhooks_service.create_webhook_trigger(workflow_id, trigger_data)
        return trigger
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create webhook: {str(e)}")


@router.put("/{workflow_id}/triggers/{trigger_id}")
async def update_workflow_webhook(
    workflow_id: str,
    trigger_id: str,
    trigger_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update a webhook trigger
    """
    webhooks_service = WebhooksService(db)
    
    try:
        trigger = await webhooks_service.update_webhook_trigger(workflow_id, trigger_id, trigger_data)
        if not trigger:
            raise HTTPException(status_code=404, detail="Webhook trigger not found")
        return trigger
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update webhook: {str(e)}")


@router.delete("/{workflow_id}/triggers/{trigger_id}")
async def delete_workflow_webhook(
    workflow_id: str,
    trigger_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a webhook trigger
    """
    webhooks_service = WebhooksService(db)
    
    try:
        success = await webhooks_service.delete_webhook_trigger(workflow_id, trigger_id)
        if not success:
            raise HTTPException(status_code=404, detail="Webhook trigger not found")
        return {"message": "Webhook trigger deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete webhook: {str(e)}")
