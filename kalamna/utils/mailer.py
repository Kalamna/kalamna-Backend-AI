import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import EmailStr

load_dotenv()

# Compute absolute path to the templates directory
templates_dir = Path(__file__).parent.parent / "templates"




env = Environment(
    loader=FileSystemLoader(searchpath=str(templates_dir)),
    autoescape=select_autoescape(['html', 'xml'])
)

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("EMAIL_HOST_USER"),
    MAIL_PASSWORD=os.getenv("EMAIL_HOST_PASSWORD"),
    MAIL_FROM=os.getenv("EMAIL_HOST_USER"),
    MAIL_PORT=int(os.getenv("EMAIL_PORT")),
    MAIL_SERVER=os.getenv("EMAIL_HOST"),
    MAIL_FROM_NAME="Kalamna Services",
    MAIL_STARTTLS=os.getenv("EMAIL_USE_TLS", "FALSE").upper() == "TRUE",
    MAIL_SSL_TLS=os.getenv("EMAIL_USE_SSL", "FALSE").upper() == "TRUE",
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_email(background_tasks: BackgroundTasks, subject: str, email_to: List[EmailStr], template_name: str, context: dict):
    """
    Send an email using FastMail with a Jinja2 template.

    :param background_tasks: FastAPI BackgroundTasks instance to run the email sending in the background.
    :param subject: Subject of the email.
    :param email_to: List of recipient email addresses.
    :param template_name: Name of the Jinja2 template file.
    :param context: Context dictionary to render the template.
    """
    template = env.get_template(template_name)
    html_content = template.render(context)

    message = MessageSchema(
        subject=subject,
        recipients=email_to,
        body=html_content,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)



