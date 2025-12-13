import re


class ValidationError(Exception):
    """Custom validation error for business logic."""

    pass


def validate_password(password: str):
    """
    Validate password strength based on your defined rules.
    Rules:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")

    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")

    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")

    if not re.search(r"[0-9]", password):
        raise ValidationError("Password must contain at least one digit.")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\]", password):
        raise ValidationError("Password must contain at least one special character.")

    # If all checks pass
    return True
