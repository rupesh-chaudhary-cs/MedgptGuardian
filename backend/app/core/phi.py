# import re
# import logging
# from typing import Tuple

# # Configure professional terminal logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# class PrivacyGateway:
#     """
#     Enterprise Privacy Controller for HIPAA Compliance.
#     Intercepts and neutralizes PHI via pre-compiled regex engines.
#     """
    
#     PHONE_REGEX = re.compile(r'\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\b')
#     SSN_REGEX = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
#     EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
#     NAME_REGEX = re.compile(r'(?i)\b(?:patient|name|mr\.|mrs\.|ms\.|dr\.)[\s:]+([A-Z][a-z]+(?: [A-Z][a-z]+)?)\b')
#     AGE_REGEX = re.compile(r'\b(\d{1,3})\s*(?:years? old|yo|y\.o\.)\b', re.IGNORECASE)

#     @classmethod
#     def scrub_phi(cls, text: str) -> Tuple[str, bool]:
#         """
#         Scrub sensitive clinical data. Returns a tuple: (safe_text, phi_was_detected).
#         """
#         if not text:
#             return text, False

#         original_text = text
        
#         # Apply redaction pipelines
#         text = cls.PHONE_REGEX.sub('[REDACTED_PHONE]', text)
#         text = cls.SSN_REGEX.sub('[REDACTED_SSN]', text)
#         text = cls.EMAIL_REGEX.sub('[REDACTED_EMAIL]', text)
#         text = cls.NAME_REGEX.sub(r'\g<0>'.replace(r'\1', '[REDACTED_NAME]'), text)
#         text = cls.AGE_REGEX.sub('[REDACTED_AGE]', text)

#         phi_detected = original_text != text
        
#         if phi_detected:
#             logger.warning("🛡️ Privacy Gateway Alert: PHI intercepted and neutralized prior to engine routing.")
            
#         return text, phi_detected



import re
import logging
from typing import Tuple

# Configure professional terminal logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class PrivacyGateway:
    """
    Enterprise Privacy Controller for HIPAA Compliance.
    Intercepts and neutralizes PHI via pre-compiled regex engines.
    """
    
    # Updated to catch 10-12 continuous digits (like 094832993899) and standard formats
    PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|\b\d{10,12}\b')
    SSN_REGEX = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    # Removed strict word boundaries that fail when an email is immediately followed by a period
    EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    # Updated to properly catch "name is", "patient is", "patient name is"
    NAME_REGEX = re.compile(r'(?i)\b(name is|patient is|patient name is|mr\.|mrs\.|ms\.|dr\.)\s+([A-Z][a-z]+(?: [A-Z][a-z]+)?)\b')
    AGE_REGEX = re.compile(r'\b(\d{1,3})\s*(?:years? old|yo|y\.o\.)\b', re.IGNORECASE)

    @classmethod
    def scrub_phi(cls, text: str) -> Tuple[str, bool]:
        """
        Scrub sensitive clinical data. Returns a tuple: (safe_text, phi_was_detected).
        """
        if not text:
            return text, False

        original_text = text
        
        # Apply redaction pipelines
        text = cls.PHONE_REGEX.sub('[REDACTED_PHONE]', text)
        text = cls.SSN_REGEX.sub('[REDACTED_SSN]', text)
        text = cls.EMAIL_REGEX.sub('[REDACTED_EMAIL]', text)
        # Replaces the name while keeping the prefix (e.g., "name is [REDACTED_NAME]")
        text = cls.NAME_REGEX.sub(r'\1 [REDACTED_NAME]', text)
        text = cls.AGE_REGEX.sub('[REDACTED_AGE]', text)

        phi_detected = original_text != text
        
        if phi_detected:
            logger.warning("🛡️ Privacy Gateway Alert: PHI intercepted and neutralized prior to engine routing.")
            
        return text, phi_detected


def scrub_phi(text: str) -> tuple[str, bool]:
    """Standalone wrapper for enterprise compatibility."""
    return PrivacyGateway.scrub_phi(text)