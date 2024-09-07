from pydantic_settings import BaseSettings
from firebase_admin import credentials, initialize_app
import firebase_admin
from firebase_admin import credentials

class Setting(BaseSettings):
    POSTGRES_HOSTNAME: str
    PASSWORD_POSTGRES: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    CLOUD_NAME: str
    API_KEY: str
    API_SECRET: str

    class Config:
        env_file = ".env"
        extra = 'allow'

cred = credentials.Certificate("/home/ameni/Downloads/pos-project-8d951-firebase-adminsdk-u3f4p-ef9f3961c5.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'gs://pos-project-8d951.appspot.com'
})

setting = Setting()
