from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
import aiofiles
from Settings import setting
from jinja2 import Template

conf = ConnectionConfig(
    MAIL_USERNAME=setting.MAIL_USERNAME,
    MAIL_PASSWORD= setting.MAIL_PASSWORD,
    MAIL_FROM=setting.MAIL_FROM,
    MAIL_PORT=setting.MAIL_PORT,
    MAIL_SERVER=setting.MAIL_SERVER,
    MAIL_FROM_NAME=setting.MAIL_FROM_NAME,
    USE_CREDENTIALS=True,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)
async def send_email(subject: str, email_to: str,  token : str):
    activation_url = f"http://localhost:8000/activate?token={token}"

    async with aiofiles.open("/home/ameni/Projects/POS/app/templates/confirm_mail.html", mode='r') as file:
                        template_content = await file.read()

    template = Template(template_content)

    email_body = template.render(activation_url=activation_url)

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=email_body,
        subtype='html',
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    return {"message": "Test email sent successfully"}
