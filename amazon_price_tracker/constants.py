from typing import Any

from dotenv import dotenv_values

ENV_VARS: dict[str, Any] = dotenv_values()

PRODUCT_PAGE_URL = (
    'https://www.amazon.com.br/PlayStation%C2%AE5-God-of-War-Ragnar%C3%B6k/dp/'
    'B0BLW5C5KN/'
)

REQUEST_HEADERS: dict[str, Any] = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/44.0.2403.157 Safari/537.36'
    ),
    'Accept-Language': 'en-US, en;q=0.5',
}

TARGET_PRICE = 4_000

SMTP_SERVER_HOST = ENV_VARS['SMTP_SERVER_HOST']
SMTP_SERVER_PORT = ENV_VARS['SMTP_SERVER_PORT']
SMTP_SERVER_USERNAME = ENV_VARS['SMTP_SERVER_USERNAME']
SMTP_SERVER_PASSWORD = ENV_VARS['SMTP_SERVER_PASSWORD']
EMAIL_SENDER = ENV_VARS['EMAIL_SENDER']
EMAIL_RECIPIENTS = ENV_VARS['EMAIL_RECIPIENTS'].split(',')
