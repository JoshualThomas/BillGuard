"""
Pytest configuration and shared fixtures for BillGuard tests.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    """Provides a TestClient instance for endpoint integration tests."""
    with TestClient(app) as test_client:
        yield test_client
