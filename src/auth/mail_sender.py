from typing import List

from fastapi_mail import ConnectionConfig, MessageSchema, MessageType, FastMail
from pydantic import EmailStr, BaseModel

from src.config import MAIL_EMAIL, MAIL_PASSWORD, MAIL_HOST




conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_EMAIL,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_EMAIL,
    MAIL_PORT=587,
    MAIL_SERVER=MAIL_HOST,
    MAIL_FROM_NAME="Desired Name",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


async def send_email(email_data, token):
    html = f"""your token
            {str(token)}
   """
    lst = []
    print(email_data)
    lst.append(email_data)
    print(lst)
    print("sfmksd")
    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=lst,
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)