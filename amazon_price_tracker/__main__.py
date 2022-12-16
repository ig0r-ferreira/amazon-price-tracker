import json
import unicodedata
from smtplib import SMTP
from typing import Any

import requests
from bs4 import BeautifulSoup

from amazon_price_tracker.constants import (
    EMAIL_RECIPIENTS,
    EMAIL_SENDER,
    PRODUCT_PAGE_URL,
    REQUEST_HEADERS,
    SMTP_SERVER_HOST,
    SMTP_SERVER_PASSWORD,
    SMTP_SERVER_PORT,
    SMTP_SERVER_USERNAME,
    TARGET_PRICE,
)
from amazon_price_tracker.email_client import EmailClient, make_message


def get_html_page(url: str, headers: dict[str, Any] | None = None) -> str:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def normalize_string(text: str) -> str:
    return unicodedata.normalize('NFKD', text)


def extract_price_data(soup: BeautifulSoup) -> dict[str, Any] | None:
    price_data_tag = soup.select_one('.twister-plus-buying-options-price-data')
    if price_data_tag is None:
        return None

    price_data = json.loads(normalize_string(price_data_tag.get_text()))[0]

    return {
        'displayed_price': price_data['displayPrice'],
        'price_amount': float(price_data['priceAmount']),
    }


def send_email(
    client: EmailClient, product_name: str, price: str, link: str
) -> None:
    msg = make_message(
        from_address=EMAIL_SENDER,
        to_address=EMAIL_RECIPIENTS,
        subject='Amazon Price Alert',
        body=f'{product_name} is now {price}.\n{link}',
    )
    client.send_message(msg)


def main() -> None:
    html_page = get_html_page(url=PRODUCT_PAGE_URL, headers=REQUEST_HEADERS)
    soup = BeautifulSoup(html_page, 'lxml')

    price_data = extract_price_data(soup)

    if price_data is None or price_data['price_amount'] > TARGET_PRICE:
        return

    email_client = EmailClient(
        smtp_server=SMTP(host=f'{SMTP_SERVER_HOST}:{SMTP_SERVER_PORT}'),
        credentials=(
            SMTP_SERVER_USERNAME,
            SMTP_SERVER_PASSWORD,
        ),
    )
    send_email(
        email_client, 'PS5', price_data['displayed_price'], PRODUCT_PAGE_URL
    )


if __name__ == '__main__':
    main()
