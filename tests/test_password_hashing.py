from kalamna.core.security import hash_password, verify_password


# 1 Test hashing works
def test_hash_password_creates_non_plaintext_hash():
    password = "SuperSecret123!"
    hashed = hash_password(password)

    assert hashed != password, "Hash should not equal the plaintext password"
    assert isinstance(hashed, str)
    assert len(hashed) > 20  # bcrypt hashes are ~60 chars


# 2 Test password verification works
def test_verify_password_success():
    password = "MyStrongPassword!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


# 3 Test wrong password verification fails
def test_verify_password_failure():
    hashed = hash_password("OriginalPass123")

    assert verify_password("WrongPass999", hashed) is False
