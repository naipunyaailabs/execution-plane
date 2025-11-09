"""
PII Detection and Filtering Middleware

This middleware provides comprehensive PII detection and filtering capabilities
based on user-configurable policies. It follows the LangChain middleware patterns
and supports both built-in and custom PII types.

Strategies:
- block: Raise exception when PII detected
- redact: Replace with [REDACTED_TYPE]
- mask: Partially obscure (e.g., ****-****-****-1234)
- hash: Replace with deterministic hash
"""

import re
import hashlib
from typing import Dict, List, Optional, Callable, Any
from enum import Enum


class PIIStrategy(str, Enum):
    """PII handling strategies"""
    BLOCK = "block"
    REDACT = "redact"
    MASK = "mask"
    HASH = "hash"


class PIIType(str, Enum):
    """Built-in PII types"""
    EMAIL = "pii_email"
    PHONE = "pii_phone"
    NAME = "pii_name"
    ADDRESS = "pii_address"
    SSN = "pii_ssn"
    DOB = "pii_dob"
    FINANCIAL = "pii_financial"
    MEDICAL = "pii_medical"
    IP = "pii_ip"
    BIOMETRIC = "pii_biometric"
    CREDIT_CARD = "credit_card"
    MAC_ADDRESS = "mac_address"
    URL = "url"
    API_KEY = "api_key"


class PIIDetectionError(Exception):
    """Raised when PII is detected and strategy is BLOCK"""
    pass


class PIIDetector:
    """Base class for PII detectors"""
    
    # Built-in regex patterns for common PII types
    PATTERNS = {
        PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        PIIType.PHONE: r'\b\+?\d{1,4}[-.\s]?(?:\d{1,4}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}(?:[-.\s]?\d{1,4})*\b',
        PIIType.SSN: r'\b\d{3}-\d{2}-\d{4}\b',
        PIIType.CREDIT_CARD: r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        PIIType.IP: r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        PIIType.MAC_ADDRESS: r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b',
        PIIType.URL: r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
        PIIType.API_KEY: r'\b(?:sk|pk|api)[-_]?[a-zA-Z0-9]{20,}\b',
        PIIType.DOB: r'\b(?:0[1-9]|1[0-2])[/-](?:0[1-9]|[12][0-9]|3[01])[/-](?:19|20)\d{2}\b',
    }
    
    # Patterns for financial data
    FINANCIAL_PATTERNS = [
        r'\b(?:account|acct)[\s#:]*\d{8,17}\b',  # Account numbers
        r'\b(?:routing|aba)[\s#:]*\d{9}\b',  # Routing numbers
        r'\b\d{4}[-\s]?\d{6}[-\s]?\d{5}\b',  # IBAN-like
    ]
    
    # Patterns for medical record numbers
    MEDICAL_PATTERNS = [
        r'\b(?:MRN|medical[\s-]?record)[\s#:]*\d{6,10}\b',
        r'\b(?:patient[\s-]?id)[\s#:]*\d{6,10}\b',
    ]
    
    # Common name patterns (simplified - requires context for accuracy)
    NAME_PATTERNS = [
        r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b',
        r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',  # Capitalized names
    ]
    
    # Address patterns (simplified)
    ADDRESS_PATTERNS = [
        r'\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b',
        r'\b(?:P\.?O\.?\s+Box|\b[0-9]{5}(?:-[0-9]{4})?)\b',  # PO Box or ZIP
    ]
    
    @classmethod
    def detect(cls, text: str, pii_type: str) -> List[str]:
        """Detect PII of a specific type in text"""
        matches = []
        
        # Handle built-in types
        if pii_type in cls.PATTERNS:
            pattern = cls.PATTERNS[pii_type]
            matches = re.findall(pattern, text, re.IGNORECASE)
        elif pii_type == PIIType.FINANCIAL:
            for pattern in cls.FINANCIAL_PATTERNS:
                matches.extend(re.findall(pattern, text, re.IGNORECASE))
        elif pii_type == PIIType.MEDICAL:
            for pattern in cls.MEDICAL_PATTERNS:
                matches.extend(re.findall(pattern, text, re.IGNORECASE))
        elif pii_type == PIIType.NAME:
            for pattern in cls.NAME_PATTERNS:
                matches.extend(re.findall(pattern, text))
        elif pii_type == PIIType.ADDRESS:
            for pattern in cls.ADDRESS_PATTERNS:
                matches.extend(re.findall(pattern, text))
        
        # Return unique matches
        return list(set([m if isinstance(m, str) else ''.join(m) for m in matches]))
    
    @classmethod
    def detect_with_custom_pattern(cls, text: str, pattern: str) -> List[str]:
        """Detect PII using a custom regex pattern"""
        matches = re.findall(pattern, text, re.IGNORECASE)
        return list(set([m if isinstance(m, str) else ''.join(m) for m in matches]))


class PIIFilter:
    """PII filtering and redaction"""
    
    @staticmethod
    def redact(text: str, pii_value: str, pii_type: str) -> str:
        """Replace PII with [REDACTED_TYPE]"""
        redaction_text = f"[REDACTED_{pii_type.upper().replace('PII_', '')}]"
        return text.replace(pii_value, redaction_text)
    
    @staticmethod
    def mask(text: str, pii_value: str, pii_type: str) -> str:
        """Partially mask PII (show last 4 characters)"""
        if len(pii_value) <= 4:
            masked = "*" * len(pii_value)
        else:
            # Show last 4 characters
            visible_chars = pii_value[-4:]
            masked = "*" * (len(pii_value) - 4) + visible_chars
        
        return text.replace(pii_value, masked)
    
    @staticmethod
    def hash_pii(text: str, pii_value: str) -> str:
        """Replace PII with deterministic hash"""
        hash_value = hashlib.sha256(pii_value.encode()).hexdigest()[:16]
        return text.replace(pii_value, f"[HASH:{hash_value}]")
    
    @staticmethod
    def apply_strategy(text: str, pii_value: str, pii_type: str, strategy: PIIStrategy) -> str:
        """Apply PII filtering strategy"""
        if strategy == PIIStrategy.REDACT:
            return PIIFilter.redact(text, pii_value, pii_type)
        elif strategy == PIIStrategy.MASK:
            return PIIFilter.mask(text, pii_value, pii_type)
        elif strategy == PIIStrategy.HASH:
            return PIIFilter.hash_pii(text, pii_value)
        elif strategy == PIIStrategy.BLOCK:
            raise PIIDetectionError(f"PII detected: {pii_type}")
        return text


class PIIMiddleware:
    """
    Middleware for detecting and filtering PII in agent conversations.
    
    This can be applied to:
    - User input (before sending to LLM)
    - Agent output (after LLM response)
    - Tool results (after tool execution)
    """
    
    def __init__(
        self,
        blocked_pii_types: List[str],
        custom_pii_configs: Optional[List[Dict[str, Any]]] = None,
        default_strategy: PIIStrategy = PIIStrategy.REDACT,
        apply_to_input: bool = True,
        apply_to_output: bool = False,
        apply_to_tool_results: bool = False,
    ):
        """
        Initialize PII middleware.
        
        Args:
            blocked_pii_types: List of PII types that should be blocked/filtered
            custom_pii_configs: List of custom PII configurations with 'id', 'label', 'pattern'
            default_strategy: Strategy to use for blocked PII
            apply_to_input: Check user messages before model call
            apply_to_output: Check AI messages after model call
            apply_to_tool_results: Check tool result messages after execution
        """
        self.blocked_pii_types = set(blocked_pii_types)
        self.custom_pii_configs = custom_pii_configs or []
        self.default_strategy = default_strategy
        self.apply_to_input = apply_to_input
        self.apply_to_output = apply_to_output
        self.apply_to_tool_results = apply_to_tool_results
        
        # Build list of PII types to filter (those that are blocked)
        self.pii_types_to_filter = list(self.blocked_pii_types)
        
        # Add custom PII patterns that are blocked
        for custom_config in self.custom_pii_configs:
            custom_id = custom_config.get('id')
            if custom_id and custom_id in self.blocked_pii_types:
                self.pii_types_to_filter.append(custom_id)
    
    def filter_text(self, text: str) -> str:
        """
        Filter PII from text based on configuration.
        
        Args:
            text: Input text to filter
            
        Returns:
            Filtered text with PII removed/masked based on strategy
            
        Raises:
            PIIDetectionError: If strategy is BLOCK and PII is detected
        """
        if not text:
            return text
        
        filtered_text = text
        detected_pii = []
        
        # Check built-in PII types
        for pii_type in self.pii_types_to_filter:
            # Skip custom PII types in this loop
            if pii_type.startswith('pii_custom_'):
                continue
            
            matches = PIIDetector.detect(filtered_text, pii_type)
            
            for match in matches:
                if match:  # Ensure match is not empty
                    detected_pii.append((pii_type, match))
                    filtered_text = PIIFilter.apply_strategy(
                        filtered_text, match, pii_type, self.default_strategy
                    )
        
        # Check custom PII patterns
        for custom_config in self.custom_pii_configs:
            custom_id = custom_config.get('id')
            custom_pattern = custom_config.get('pattern')
            
            if custom_id in self.pii_types_to_filter and custom_pattern:
                matches = PIIDetector.detect_with_custom_pattern(filtered_text, custom_pattern)
                
                for match in matches:
                    if match:
                        detected_pii.append((custom_id, match))
                        filtered_text = PIIFilter.apply_strategy(
                            filtered_text, match, custom_id, self.default_strategy
                        )
        
        return filtered_text
    
    def process_message(self, message: str, message_type: str = "input") -> str:
        """
        Process a message based on middleware configuration.
        
        Args:
            message: Message content to process
            message_type: Type of message ('input', 'output', 'tool_result')
            
        Returns:
            Processed message
        """
        should_process = False
        
        if message_type == "input" and self.apply_to_input:
            should_process = True
        elif message_type == "output" and self.apply_to_output:
            should_process = True
        elif message_type == "tool_result" and self.apply_to_tool_results:
            should_process = True
        
        if should_process:
            return self.filter_text(message)
        
        return message


def create_pii_middleware_from_config(pii_config: Dict[str, Any]) -> Optional[PIIMiddleware]:
    """
    Create PII middleware from agent configuration.
    
    Args:
        pii_config: Dictionary containing PII configuration from agent
        
    Returns:
        PIIMiddleware instance or None if PII filtering is disabled
    """
    if not pii_config:
        return None
    
    blocked_pii = pii_config.get('blocked_pii_types', [])
    custom_pii = pii_config.get('custom_pii_categories', [])
    strategy = pii_config.get('strategy', PIIStrategy.REDACT)
    
    # Convert string strategy to enum
    if isinstance(strategy, str):
        try:
            strategy = PIIStrategy(strategy)
        except ValueError:
            strategy = PIIStrategy.REDACT
    
    return PIIMiddleware(
        blocked_pii_types=blocked_pii,
        custom_pii_configs=custom_pii,
        default_strategy=strategy,
        apply_to_input=True,
        apply_to_output=bool(blocked_pii),  # Always enable output filtering when PII types are blocked
        apply_to_tool_results=pii_config.get('apply_to_tool_results', False),
    )
