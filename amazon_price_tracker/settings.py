import json
from pathlib import Path
from typing import Any, Sequence

from dotenv import load_dotenv
from pydantic import BaseSettings, EmailStr, HttpUrl, validator

load_dotenv()


class SMTPServer(BaseSettings):
    host: str
    port: int
    username: str
    password: str

    class Config:
        env_prefix = 'SMTP_SERVER_'


class RequestHeaders(BaseSettings):
    user_agent: str
    accept_lang: str

    class Config:
        env_prefix = 'REQUEST_HEADERS_'


class EmailSettings(BaseSettings):
    sender: EmailStr
    recipients: Sequence[EmailStr]

    class Config:
        env_prefix = 'EMAIL_'
        json_loads = json.loads

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            if field_name == 'recipients':
                return [email.strip() for email in raw_val.split(',')]

            return cls.json_loads(raw_val)


class TargetProduct(BaseSettings):
    url: HttpUrl
    price: float

    class Config:
        env_prefix = 'TARGET_PRODUCT_'

    @validator('url')
    def url_must_contain_amazon_domain(cls, value: str) -> str:
        if not value.startswith('https://www.amazon.'):
            raise ValueError("'url' must contain Amazon domain.")

        return value


ROOT_DIR = Path(__file__).parent.parent.absolute()
SMTP_SERVER = SMTPServer()
REQUEST_HEADERS = RequestHeaders()
EMAIL_SETTINGS = EmailSettings()
TARGET_PRODUCT = TargetProduct()
