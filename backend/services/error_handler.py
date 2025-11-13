import asyncio
import time
import logging
from typing import Callable, Any, Dict
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Categories of errors that can occur during workflow execution"""
    NETWORK = "network"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    RESOURCE_LIMIT = "resource_limit"
    BUSINESS_LOGIC = "business_logic"
    UNKNOWN = "unknown"


@dataclass
class RetryPolicy:
    """Configuration for retry behavior"""
    max_retries: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0     # seconds
    exponential_base: float = 2.0


# Default retry policy for all operations
DEFAULT_RETRY_POLICY = RetryPolicy()


class ErrorHandler:
    """Handles errors that occur during workflow execution with categorization and retry logic"""
    
    @staticmethod
    def get_error_details(error: Exception) -> Dict[str, Any]:
        """Categorize an error and extract relevant details"""
        error_type = type(error).__name__
        message = str(error)
        
        # Categorize based on error type and message content
        if "timeout" in message.lower() or "timed out" in message.lower():
            category = ErrorCategory.TIMEOUT
        elif "network" in message.lower() or "connection" in message.lower():
            category = ErrorCategory.NETWORK
        elif "unauthorized" in message.lower() or "forbidden" in message.lower() or "api key" in message.lower():
            category = ErrorCategory.AUTHENTICATION
        elif "validation" in message.lower() or "invalid" in message.lower():
            category = ErrorCategory.VALIDATION
        elif "memory" in message.lower() or "disk space" in message.lower():
            category = ErrorCategory.RESOURCE_LIMIT
        elif "business" in message.lower() or "logic" in message.lower():
            category = ErrorCategory.BUSINESS_LOGIC
        else:
            category = ErrorCategory.UNKNOWN
            
        return {
            "error_type": error_type,
            "message": message,
            "category": category.value
        }
    
    @staticmethod
    async def retry_with_backoff(func: Callable, retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY) -> Any:
        """Execute a function with exponential backoff retry logic"""
        last_exception = None
        
        for attempt in range(retry_policy.max_retries + 1):
            try:
                return await func()
            except Exception as e:
                last_exception = e
                # If this was the last attempt, re-raise the exception
                if attempt == retry_policy.max_retries:
                    if last_exception is not None:
                        raise last_exception
                    else:
                        raise e
                
                # Calculate delay with exponential backoff
                delay = min(
                    retry_policy.initial_delay * (retry_policy.exponential_base ** attempt),
                    retry_policy.max_delay
                )
                
                # Add jitter to prevent thundering herd
                jitter = 0.1 * delay * (2 * (hash(str(attempt)) % 1000) / 1000 - 1)
                delay = max(0, delay + jitter)
                
                logger.warning(
                    f"Attempt {attempt + 1} failed with error: {str(e)}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                
                await asyncio.sleep(delay)
        
        # This should never be reached due to the re-raise above, but included for safety
        # The function will always raise an exception before reaching this point
        raise Exception("Retry logic failed unexpectedly")