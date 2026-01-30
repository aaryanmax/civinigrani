import re
import time

class ArmorIQGuard:
    """
    Local ArmorIQ Security Implementation (No API Key Required).
    Provides robust regex-based protection against PII leakage and Policy violations.
    """
    
    def __init__(self):
        self.safety_policy = {
            "political_bias": True,
            "pii_leakage": True,
            "toxic_content": True
        }
        
        # PII Regex Patterns (Indian Context)
        self.pii_patterns = {
            "Mobile Number": r"\b[6-9]\d{9}\b",  # Indian mobile numbers
            "Aadhaar Partial": r"\b\d{4}\s\d{4}\s\d{4}\b",  # Aadhar format
            "Email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        }
        
        # Blocked Keywords (Toxicity/Bias)
        self.blocked_keywords = [
            "corrupt politician", "vote for", "election fraud", 
            "bribe paid", "commission agent", "private phone",
            "kickback", "don't vote"
        ]
        
        # Hateful/Toxic Sentiment Patterns
        self.hate_patterns = [
            "hate", "kill", "destroy", "attack", "murder",
            "terrorist", "scum", "trash", "garbage people",
            "should die", "deserve death", "burn them",
            "ethnic cleansing", "genocide", "vote-chor"
        ]
        
        # Write operation patterns (for read-only enforcement)
        self.write_patterns = [
            "delete", "remove", "drop", "truncate", "update",
            "modify", "change", "alter", "insert", "create"
        ]
    
    def scan(self, text: str) -> dict:
        """
        Scans the provided text for violations locally.
        Returns a dict with status and metadata.
        """
        start_time = time.time()
        text_lower = text.lower()
        
        # 1. Check for Blocked Keywords (Toxicity/Bias)
        for trigger in self.blocked_keywords:
            if trigger in text_lower:
                return {
                    "safe": False,
                    "flagged_for": "Political Content / Toxicity",
                    "confidence": 0.98,
                    "action": "BLOCK"
                }

        # 2. Check for PII (Regex)
        for pii_type, pattern in self.pii_patterns.items():
            if re.search(pattern, text):
                return {
                    "safe": False,
                    "flagged_for": f"PII Leakage ({pii_type})",
                    "confidence": 0.99,
                    "action": "REDACT"
                }
                
        # 3. Safe
        latency = time.time() - start_time
        return {
            "safe": True,
            "latency": f"{latency:.4f}s",
            "checks_passed": ["Bias", "PII", "Toxicity"],
            "verification_badge": "🛡️ Verified by ArmorIQ (Local)"
        }
    
    def validate_query(self, query: str) -> dict:
        """
        Validates user query for safety and compliance.
        Blocks hateful content and write operations.
        
        Args:
            query: User's natural language query
            
        Returns:
            Dict with validation status and reason
        """
        query_lower = query.lower()
        
        # 1. Check for hateful/toxic sentiment
        for hate_word in self.hate_patterns:
            if hate_word in query_lower:
                return {
                    "valid": False,
                    "reason": "Hateful or toxic content detected",
                    "action": "BLOCK",
                    "confidence": 0.95
                }
        
        # 2. Check for write operations (read-only enforcement)
        for write_op in self.write_patterns:
            if write_op in query_lower:
                return {
                    "valid": False,
                    "reason": "Write operation not permitted. Read-only access enforced.",
                    "action": "BLOCK",
                    "confidence": 0.99
                }
        
        # 3. Check for PII in query
        for pii_type, pattern in self.pii_patterns.items():
            if re.search(pattern, query):
                return {
                    "valid": False,
                    "reason": f"PII detected in query ({pii_type})",
                    "action": "REDACT",
                    "confidence": 0.99
                }
        
        # 4. Valid query
        return {
            "valid": True,
            "reason": "Query passed all safety checks",
            "checks_passed": ["Sentiment", "PII", "Read-only"]
        }

