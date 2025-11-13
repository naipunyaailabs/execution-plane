import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from models.workflow import WorkflowExecution

logger = logging.getLogger(__name__)


class AlertingService:
    """Service for handling alerts based on workflow execution results"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def evaluate_alert_rules(self, execution: WorkflowExecution) -> List[Dict[str, Any]]:
        """
        Evaluate alert rules for a workflow execution.
        In a production environment, this would check against configured alert rules.
        For now, we'll implement basic alerting logic.
        """
        alerts = []
        
        # Basic alert conditions
        execution_status = getattr(execution, 'status', None)
        if execution_status == "failed":
            alerts.append({
                "type": "workflow_failure",
                "severity": "high",
                "message": f"Workflow {execution.workflow_id} execution failed",
                "execution_id": execution.execution_id,
                "timestamp": datetime.utcnow()
            })
            
        # Check for high failure count in execution
        failure_count = getattr(execution, 'failure_count', None)
        if failure_count is not None and failure_count > 3:
            alerts.append({
                "type": "high_failure_count",
                "severity": "medium",
                "message": f"Workflow {execution.workflow_id} had {failure_count} failed steps",
                "execution_id": execution.execution_id,
                "timestamp": datetime.utcnow()
            })
            
        # Check for long execution time (over 5 minutes)
        execution_time = getattr(execution, 'execution_time', None)
        if execution_time is not None and execution_time > 300:
            alerts.append({
                "type": "long_execution_time",
                "severity": "medium",
                "message": f"Workflow {execution.workflow_id} took {execution_time} seconds to execute",
                "execution_id": execution.execution_id,
                "timestamp": datetime.utcnow()
            })
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"ALERT: {alert['message']}")
            
        return alerts
    
    async def send_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Send an alert notification.
        In a production environment, this would integrate with alerting systems like Slack, Email, etc.
        For now, we'll just log the alert.
        """
        logger.info(f"Sending alert: {alert}")
        # In a real implementation, you would integrate with your alerting system here
        return True