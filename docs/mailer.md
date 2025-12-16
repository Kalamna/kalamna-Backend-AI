# Mailer Utility

A utility module for sending templated HTML emails asynchronously using FastMail and Jinja2.

## Overview

The mailer utility provides a simple interface to send emails in the background without blocking API responses. It uses:

- **FastMail** – For SMTP email delivery
- **Jinja2** – For HTML template rendering
- **FastAPI BackgroundTasks** – For non-blocking async email sending

## Configuration

The mailer requires the following environment variables:

| Variable             | Description                        | Example              |
|----------------------|------------------------------------|----------------------|
| `EMAIL_HOST_USER`    | SMTP username / sender email       | `noreply@kalamna.com`|
| `EMAIL_HOST_PASSWORD`| SMTP password or app password      | `your-password`      |
| `EMAIL_HOST`         | SMTP server hostname               | `smtp.gmail.com`     |
| `EMAIL_PORT`         | SMTP port                          | `587`                |
| `EMAIL_USE_TLS`      | Enable STARTTLS (TRUE/FALSE)       | `TRUE`               |
| `EMAIL_USE_SSL`      | Enable SSL/TLS (TRUE/FALSE)        | `FALSE`              |

## Available Templates

Templates are located in `kalamna/templates/`:

| Template                  | Purpose                          |
|---------------------------|----------------------------------|
| `mail.html`               | General email (Arabic)           |
| `mail_en.html`            | General email (English)          |
| `verifcation.html`        | Email verification (Arabic)      |
| `verification_en.html`    | Email verification (English)     |
| `reset_password.html`     | Password reset (Arabic)          |
| `reset_password_en.html`  | Password reset (English)         |
| `invite_member.html`      | Team invitation (Arabic)         |
| `invite_member_en.html`   | Team invitation (English)        |

## Usage

### Basic Example

```python
from fastapi import BackgroundTasks
from kalamna.utils.mailer import send_email

@router.post("/send-welcome")
async def send_welcome_email(
    background_tasks: BackgroundTasks,
    email: str,
):
    await send_email(
        background_tasks=background_tasks,
        subject="Welcome to Kalamna!",
        email_to=[email],
        template_name="mail.html",
        context={"name": "John Doe"},
    )
    return {"message": "Email sent in the background."}
```

### Function Signature

```python
async def send_email(
    background_tasks: BackgroundTasks,
    subject: str,
    email_to: List[EmailStr],
    template_name: str,
    context: dict,
) -> None
```

### Parameters

| Parameter          | Type              | Description                                      |
|--------------------|-------------------|--------------------------------------------------|
| `background_tasks` | `BackgroundTasks` | FastAPI BackgroundTasks for async execution      |
| `subject`          | `str`             | Email subject line                               |
| `email_to`         | `List[EmailStr]`  | List of recipient email addresses                |
| `template_name`    | `str`             | Jinja2 template filename from templates folder   |
| `context`          | `dict`            | Variables to pass into the template              |

## Template Context Examples

### Verification Email

```python
await send_email(
    background_tasks=background_tasks,
    subject="Verify Your Email",
    email_to=["user@example.com"],
    template_name="verification_en.html",
    context={
        "name": "John Doe",
        "verification_link": "https://kalamna.com/verify?token=abc123",
    },
)
```

### Password Reset

```python
await send_email(
    background_tasks=background_tasks,
    subject="Reset Your Password",
    email_to=["user@example.com"],
    template_name="reset_password_en.html",
    context={
        "name": "John Doe",
        "reset_link": "https://kalamna.com/reset?token=xyz789",
    },
)
```

### Team Invitation

```python
await send_email(
    background_tasks=background_tasks,
    subject="You're Invited to Join Kalamna",
    email_to=["newmember@example.com"],
    template_name="invite_member_en.html",
    context={
        "inviter_name": "Admin User",
        "business_name": "Acme Corp",
        "invite_link": "https://kalamna.com/invite?token=def456",
    },
)
```

## Notes

- Emails are sent **in the background**, so the API response returns immediately.
- The function validates email addresses using Pydantic's `EmailStr`.
- Make sure your SMTP credentials are correctly configured in the `.env` file.
