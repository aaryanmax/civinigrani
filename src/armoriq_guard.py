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
        
        # Blocked Keywords
        self.blocked_keywords = [
            "corrupt politician", "vote for", "election fraud", 
            "bribe paid", "commission agent", "private phone",
            "kickback", "don't vote"
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

