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


def extract_price(soup: BeautifulSoup) -> tuple[str, str] | None:
    price_whole_tag = soup.select_one('.a-price-whole')
    price_decimal_tag = soup.select_one('.a-price-fraction')

    if price_whole_tag is None or price_decimal_tag is None:
        return None

    return price_whole_tag.text, price_decimal_tag.text


def format_price(whole_part: str, decimal_part: str) -> float:
    whole_part = whole_part.rstrip(',').replace('.', '_')
    return float(whole_part) + (int(decimal_part) / 100)


def send_email(
    client: EmailClient, product_name: str, price: float, link: str
) -> None:
    msg = make_message(
        from_address=EMAIL_SENDER,
        to_address=EMAIL_RECIPIENTS,
        subject='Amazon Price Alert',
        body=f'{product_name} is now R$ {price}.\n{link}',
    )
    client.send_message(msg)


def main() -> None:
    html_page = get_html_page(url=PRODUCT_PAGE_URL, headers=REQUEST_HEADERS)
    soup = BeautifulSoup(html_page, 'lxml')

    price = extract_price(soup)

    if price is None:
        return

    product_price = format_price(*price)
    if product_price > TARGET_PRICE:
        return

    email_client = EmailClient(
        smtp_server=SMTP(host=f'{SMTP_SERVER_HOST}:{SMTP_SERVER_PORT}'),
        credentials=(
            SMTP_SERVER_USERNAME,
            SMTP_SERVER_PASSWORD,
        ),
    )
    send_email(email_client, 'PS5', product_price, PRODUCT_PAGE_URL)


if __name__ == '__main__':
    main()
