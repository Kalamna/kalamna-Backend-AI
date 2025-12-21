"""
Authentication tests
Test user registration, login, JWT tokens, and permissions
"""
import os
from uuid import uuid4

import pytest

# IMPORTANT:
# Make sure JWT_SECRET exists before importing the module
os.environ.setdefault("JWT_SECRET", "test-secret-key")

from kalamna.core.security import (  # adjust import path if needed
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


@pytest.fixture
def employee_id() -> str:
    return str(uuid4())


@pytest.fixture
def role() -> str:
    return "owner"


def test_create_and_decode_access_token(employee_id, role):
    token = create_access_token(employee_id, role)
    print("\nACCESS TOKEN:", token)

    payload = decode_token(token, audience="access")
    print("DECODED ACCESS PAYLOAD:", payload)

    assert payload["sub"] == employee_id
    assert payload["role"] == role
    assert payload["aud"] == "access"
    assert "jti" in payload


def test_create_and_decode_refresh_token(employee_id):
    token = create_refresh_token(employee_id)
    print("\nREFRESH TOKEN:", token)

    payload = decode_token(token, audience="refresh")
    print("DECODED REFRESH PAYLOAD:", payload)

    assert payload["sub"] == employee_id
    assert payload["aud"] == "refresh"
    assert "jti" in payload


def test_access_token_wrong_audience_fails(employee_id, role):
    token = create_access_token(employee_id, role)

    with pytest.raises(Exception) as exc:
        decode_token(token, audience="refresh")

    print("\nWRONG AUDIENCE ERROR:", exc.value)


def test_password_hash_and_verify():
    password = "SuperSecret123!"
    hashed = hash_password(password)

    print("\nHASHED PASSWORD:", hashed)

    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False
