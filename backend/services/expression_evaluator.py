"""
Expression evaluator for workflow conditions and transformations
Safely evaluates expressions with variable interpolation
"""

import re
import json
from typing import Any, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExpressionEvaluator:
    """
    Evaluates expressions in workflow context
    Supports {{ variable }} syntax like n8n
    """
    
    def __init__(self):
        self.expression_pattern = re.compile(r'\{\{(.+?)\}\}')
    
    def evaluate_expression(self, expression: str, context: Dict[str, Any]) -> Any:
        """
        Evaluate an expression with variable interpolation
        
        Args:
            expression: Expression string (may contain {{ }} placeholders)
            context: Variables available for interpolation
            
        Returns:
            Evaluated result
        """
        if not expression:
            return expression
        
        # Check if entire expression is wrapped in {{ }}
        if expression.strip().startswith('{{') and expression.strip().endswith('}}'):
            # Extract and evaluate the inner expression
            inner = expression.strip()[2:-2].strip()
            return self._evaluate_code(inner, context)
        
        # Replace all {{ }} placeholders in the string
        def replace_placeholder(match):
            code = match.group(1).strip()
            try:
                result = self._evaluate_code(code, context)
                return str(result) if result is not None else ''
            except Exception as e:
                logger.error(f"Error evaluating placeholder {code}: {str(e)}")
                return match.group(0)  # Return original on error
        
        result = self.expression_pattern.sub(replace_placeholder, expression)
        
        # Try to parse as JSON if it looks like JSON
        if result.startswith(('{', '[')):
            try:
                return json.loads(result)
            except:
                pass
        
        return result
    
    def _evaluate_code(self, code: str, context: Dict[str, Any]) -> Any:
        """
        Safely evaluate code expression
        
        Supports:
        - Variable access: $json.field, $node.stepName.json.field
        - Built-in variables: $now, $today
        - JavaScript-like operations: value > 10, value.toUpperCase()
        - Math operations: value * 1.2
        """
        # Build safe evaluation context
        eval_context = self._build_eval_context(context)
        
        # Transform JavaScript-like syntax to Python
        python_code = self._transform_to_python(code, eval_context)
        
        try:
            # Safe evaluation with restricted builtins
            result = eval(python_code, {"__builtins__": {}}, eval_context)
            return result
        except Exception as e:
            logger.error(f"Error evaluating code '{code}': {str(e)}")
            raise ValueError(f"Expression evaluation failed: {str(e)}")
    
    def _build_eval_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build evaluation context with safe built-ins
        """
        eval_context = {}
        
        # Add context variables with $ prefix mapping
        if 'input_data' in context:
            eval_context['json'] = context['input_data']
        if 'step_results' in context:
            eval_context['node'] = context['step_results']
        if 'context' in context:
            eval_context['context'] = context['context']
        
        # Built-in variables
        eval_context['now'] = datetime.utcnow().isoformat()
        eval_context['today'] = datetime.utcnow().date().isoformat()
        eval_context['timestamp'] = datetime.utcnow().timestamp()
        
        # Safe functions
        eval_context['len'] = len
        eval_context['str'] = str
        eval_context['int'] = int
        eval_context['float'] = float
        eval_context['bool'] = bool
        eval_context['list'] = list
        eval_context['dict'] = dict
        eval_context['sum'] = sum
        eval_context['min'] = min
        eval_context['max'] = max
        eval_context['abs'] = abs
        eval_context['round'] = round
        
        return eval_context
    
    def _transform_to_python(self, code: str, context: Dict[str, Any]) -> str:
        """
        Transform JavaScript-like syntax to Python
        """
        python_code = code
        
        # Transform $json to json
        python_code = re.sub(r'\$json', 'json', python_code)
        
        # Transform $node.stepName to node['stepName']
        python_code = re.sub(r'\$node\.(\w+)', r"node['\1']", python_code)
        
        # Transform $now to now
        python_code = re.sub(r'\$now', 'now', python_code)
        python_code = re.sub(r'\$today', 'today', python_code)
        python_code = re.sub(r'\$timestamp', 'timestamp', python_code)
        
        # Transform string methods to Python equivalents
        # .toUpperCase() -> .upper()
        python_code = re.sub(r'\.toUpperCase\(\)', '.upper()', python_code)
        # .toLowerCase() -> .lower()
        python_code = re.sub(r'\.toLowerCase\(\)', '.lower()', python_code)
        # .trim() -> .strip()
        python_code = re.sub(r'\.trim\(\)', '.strip()', python_code)
        
        # Transform JavaScript ternary to Python conditional
        # value ? 'a' : 'b' -> 'a' if value else 'b'
        ternary_pattern = r'(.+?)\s*\?\s*(.+?)\s*:\s*(.+)'
        if '?' in python_code and ':' in python_code:
            match = re.match(ternary_pattern, python_code)
            if match:
                condition, true_val, false_val = match.groups()
                python_code = f"({true_val}) if ({condition}) else ({false_val})"
        
        return python_code
    
    def evaluate_condition(self, condition_expr: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition expression to boolean
        
        Args:
            condition_expr: Boolean expression
            context: Workflow context
            
        Returns:
            Boolean result
        """
        try:
            result = self.evaluate_expression(condition_expr, context)
            return bool(result)
        except Exception as e:
            logger.error(f"Condition evaluation failed: {str(e)}")
            return False


# Global evaluator instance
evaluator = ExpressionEvaluator()


def evaluate_expression(expression: str, context: Dict[str, Any]) -> Any:
    """Convenience function for expression evaluation"""
    return evaluator.evaluate_expression(expression, context)


def evaluate_condition(condition: str, context: Dict[str, Any]) -> bool:
    """Convenience function for condition evaluation"""
    return evaluator.evaluate_condition(condition, context)
