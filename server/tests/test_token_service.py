import pytest
import time
from app.services.token_service import ActionTokenService


def test_generate_and_verify_token():
    payload = {"action": "mark_paid", "bill_id": "123", "user_id": "u1"}
    token = ActionTokenService.generate_token(payload, expires_in_seconds=3600)
    
    assert isinstance(token, str)
    assert "." in token
    
    verified = ActionTokenService.verify_token(token)
    assert verified is not None
    assert verified["action"] == "mark_paid"
    assert verified["bill_id"] == "123"
    assert verified["user_id"] == "u1"


def test_tampered_token_rejected():
    payload = {"action": "mark_paid", "bill_id": "123"}
    token = ActionTokenService.generate_token(payload)
    
    # Tamper with the token string
    tampered = token[:-2] + "xx"
    verified = ActionTokenService.verify_token(tampered)
    assert verified is None


def test_expired_token_rejected():
    payload = {"action": "mark_paid", "bill_id": "123"}
    # Token that expired 5 seconds ago
    token = ActionTokenService.generate_token(payload, expires_in_seconds=-5)
    
    verified = ActionTokenService.verify_token(token)
    assert verified is None
