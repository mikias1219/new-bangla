import re
import logging
from typing import Dict, Any, Union

class PIIMaskingFilter(logging.Filter):
    """Logging filter to mask PII in log messages"""

    def __init__(self):
        super().__init__()
        # Patterns for different types of PII
        self.pii_patterns = {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b(\+?88)?[0-9]{3,4}[-\s]?[0-9]{3,4}[-\s]?[0-9]{3,4}[-\s]?[0-9]{0,4}\b'),
            'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            'ssn': re.compile(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'),
            'bangladesh_nid': re.compile(r'\b\d{10}|\d{13}|\d{17}\b'),  # Bangladesh National ID patterns
        }

    def filter(self, record):
        if hasattr(record, 'getMessage'):
            original_msg = record.getMessage()
            masked_msg = self.mask_pii(original_msg)
            record.msg = masked_msg
            record.args = ()  # Clear args since we modified msg

        return True

    def mask_pii(self, text: str) -> str:
        """Mask PII in the given text"""
        masked_text = text

        for pii_type, pattern in self.pii_patterns.items():
            masked_text = pattern.sub(self._get_mask(pii_type), masked_text)

        return masked_text

    def _get_mask(self, pii_type: str) -> str:
        """Get appropriate mask for PII type"""
        masks = {
            'email': '[EMAIL_MASKED]',
            'phone': '[PHONE_MASKED]',
            'credit_card': '[CARD_MASKED]',
            'ssn': '[SSN_MASKED]',
            'bangladesh_nid': '[NID_MASKED]'
        }
        return masks.get(pii_type, '[PII_MASKED]')

class PIIMasker:
    """Utility class for masking PII in data structures"""

    def __init__(self):
        self.pii_fields = {
            'email', 'phone', 'phone_number', 'mobile', 'contact',
            'address', 'street_address', 'postal_code', 'zip_code',
            'credit_card', 'card_number', 'ssn', 'social_security',
            'nid', 'national_id', 'passport', 'driver_license',
            'first_name', 'last_name', 'full_name'  # Names can be considered PII in some contexts
        }

    def mask_data(self, data: Union[Dict[str, Any], list, str]) -> Union[Dict[str, Any], list, str]:
        """Recursively mask PII in nested data structures"""
        if isinstance(data, dict):
            return self._mask_dict(data)
        elif isinstance(data, list):
            return [self.mask_data(item) for item in data]
        elif isinstance(data, str):
            return self._mask_string_pii(data)
        else:
            return data

    def _mask_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask PII in dictionary"""
        masked = {}
        for key, value in data.items():
            if key.lower() in self.pii_fields:
                masked[key] = self._mask_value(value)
            else:
                masked[key] = self.mask_data(value)
        return masked

    def _mask_value(self, value: Any) -> str:
        """Mask a single PII value"""
        if isinstance(value, str):
            if len(value) <= 2:
                return '*' * len(value)
            elif '@' in value:  # Email
                parts = value.split('@')
                if len(parts) == 2:
                    return f"{parts[0][:2]}***@{parts[1]}"
            elif value.replace('-', '').replace(' ', '').isdigit():  # Numbers (phone, ID, etc.)
                return f"{value[:2]}***{value[-2:]}" if len(value) > 4 else '*' * len(value)
            else:  # Text fields
                return f"{value[:2]}***{value[-2:]}" if len(value) > 4 else '*' * len(value)
        else:
            return str(value)

    def _mask_string_pii(self, text: str) -> str:
        """Mask PII patterns in plain text"""
        # Email pattern
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_MASKED]', text)

        # Phone pattern (Bangladesh and international)
        text = re.sub(r'\b(\+?88)?[0-9]{3,4}[-\s]?[0-9]{3,4}[-\s]?[0-9]{3,4}[-\s]?[0-9]{0,4}\b', '[PHONE_MASKED]', text)

        # Credit card pattern
        text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD_MASKED]', text)

        # Bangladesh NID pattern
        text = re.sub(r'\b\d{10}|\d{13}|\d{17}\b', '[NID_MASKED]', text)

        return text

# Global instances
pii_filter = PIIMaskingFilter()
pii_masker = PIIMasker()

def setup_logging_with_pii_masking():
    """Setup logging with PII masking filter"""
    # Get the root logger
    logger = logging.getLogger()

    # Add PII masking filter to all handlers
    for handler in logger.handlers:
        handler.addFilter(pii_filter)

    # Also add to specific loggers that might be created later
    for name in ['app.services.whatsapp_service',
                 'app.services.facebook_service',
                 'app.services.instagram_service',
                 'app.services.ai_chat']:
        service_logger = logging.getLogger(name)
        for handler in service_logger.handlers:
            handler.addFilter(pii_filter)
