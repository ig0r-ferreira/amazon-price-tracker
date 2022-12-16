import json
import unicodedata
from dataclasses import dataclass
from smtplib import SMTP
from typing import Any

import requests
from bs4 import BeautifulSoup

from amazon_price_tracker.constants import (
    EMAIL_RECIPIENTS,
    EMAIL_SENDER,
    PRODUCT_URL,
    REQUEST_HEADERS,
    SMTP_SERVER_HOST,
    SMTP_SERVER_PASSWORD,
    SMTP_SERVER_PORT,
    SMTP_SERVER_USERNAME,
    TARGET_PRICE,
)
from amazon_price_tracker.email_client import EmailClient, make_message


@dataclass(frozen=True)
class Product:
    title: str
    price_amount: float
    display_price: str
    link: str


def get_html_page(url: str, headers: dict[str, Any] | None = None) -> str:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def normalize_string(text: str) -> str:
    return unicodedata.normalize('NFKD', text)


def extract_product_title(soup: BeautifulSoup) -> str:
    product_tag = soup.select_one('span#productTitle')
    if product_tag is None:
        return ''

    return product_tag.get_text(strip=True)


def extract_price_data(soup: BeautifulSoup) -> dict[str, Any] | None:
    price_data_tag = soup.select_one('.twister-plus-buying-options-price-data')
    if price_data_tag is None:
        return None

    price_data = json.loads(normalize_string(price_data_tag.get_text()))[0]

    return {
        'display_price': price_data['displayPrice'],
        'price_amount': float(price_data['priceAmount']),
    }


def send_email(client: EmailClient, product: Product) -> None:
    msg = make_message(
        from_address=EMAIL_SENDER,
        to_address=EMAIL_RECIPIENTS,
        subject=f'Amazon - Low Price for {product.title[:30]}...',
        body=f'We know you are interested in {product.title}.\n'
        f'Buy now for {product.display_price}.\n\n'
        f'Visit the link to buy: {product.link}',
    )
    client.send_message(msg)


def main() -> None:
    html_page = get_html_page(url=PRODUCT_URL, headers=REQUEST_HEADERS)
    soup = BeautifulSoup(html_page, 'lxml')

    product_title = extract_product_title(soup)
    price_data = extract_price_data(soup)

    if price_data is None or price_data['price_amount'] > TARGET_PRICE:
        return

    product = Product(title=product_title, link=PRODUCT_URL, **price_data)

    email_client = EmailClient(
        smtp_server=SMTP(host=f'{SMTP_SERVER_HOST}:{SMTP_SERVER_PORT}'),
        credentials=(
            SMTP_SERVER_USERNAME,
            SMTP_SERVER_PASSWORD,
        ),
    )
    send_email(email_client, product)


if __name__ == '__main__':
    main()
