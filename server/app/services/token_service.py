import hmac
import hashlib
import time
import base64
import json
from typing import Optional, Dict, Any
from app.core.config import settings


class ActionTokenService:
    """
    Generates and verifies cryptographic, tamper-proof tokens for 1-click email magic actions
    (e.g., Mark as Paid, Snooze Alert) without requiring the user to authenticate via password.
    """

    @staticmethod
    def generate_token(payload: Dict[str, Any], expires_in_seconds: int = 604800) -> str:
        """
        Generate an HMAC-SHA256 signed action token.
        Default expiry: 7 days (604800 seconds).
        """
        data = payload.copy()
        data["exp"] = int(time.time()) + expires_in_seconds
        
        # Serialize payload
        payload_bytes = json.dumps(data, separators=(',', ':'), sort_keys=True).encode('utf-8')
        encoded_payload = base64.urlsafe_b64encode(payload_bytes).decode('utf-8').rstrip('=')
        
        # Generate signature
        signature = hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            encoded_payload.encode('utf-8'),
            hashlib.sha256
        ).digest()
        encoded_sig = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
        
        return f"{encoded_payload}.{encoded_sig}"

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify the signature and expiration of an action token.
        Returns the payload dictionary if valid, None otherwise.
        """
        try:
            parts = token.split('.')
            if len(parts) != 2:
                return None
            
            encoded_payload, encoded_sig = parts
            
            # Recalculate signature
            expected_sig = hmac.new(
                settings.SECRET_KEY.encode('utf-8'),
                encoded_payload.encode('utf-8'),
                hashlib.sha256
            ).digest()
            expected_encoded_sig = base64.urlsafe_b64encode(expected_sig).decode('utf-8').rstrip('=')
            
            if not hmac.compare_digest(encoded_sig, expected_encoded_sig):
                return None
            
            # Pad base64 payload if needed
            padding = '=' * (-len(encoded_payload) % 4)
            payload_json = base64.urlsafe_b64decode(encoded_payload + padding).decode('utf-8')
            payload = json.loads(payload_json)
            
            # Check expiration
            if payload.get("exp", 0) < int(time.time()):
                return None
                
            return payload
        except Exception:
            return None
