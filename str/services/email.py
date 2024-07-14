from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from str.conf.config import settings

from str.services.auth import auth_service

try:
    conf = ConnectionConfig(
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=settings.mail_password,
        MAIL_FROM=settings.mail_from,
        MAIL_PORT=settings.mail_port,
        MAIL_SERVER=settings.mail_server,
        MAIL_FROM_NAME="Example email",
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=True,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER= Path("C:/programming.study/software/goit-software-12/str/services/templates"),
                                    
    )
except Exception as e:
    print(e)

async def send_email(email: EmailStr, username: str, host: str):
    """
    Send a confirmation email to the user.

    :param email: The email address to send the confirmation to.
    :type email: EmailStr
    :param username: The username of the recipient.
    :type username: str
    :param host: The host URL to include in the email.
    :type host: str
    :raises ConnectionErrors: If there is an error connecting to the email server.
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="example.html")
    except ConnectionErrors as err:
        print(err)

