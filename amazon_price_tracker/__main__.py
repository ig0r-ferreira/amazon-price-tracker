import json
import unicodedata
from dataclasses import dataclass
from smtplib import SMTP
from typing import Any, cast

import requests
from bs4 import BeautifulSoup

from amazon_price_tracker.email_client import EmailClient, make_message
from amazon_price_tracker.log_manager import get_logger
from amazon_price_tracker.settings import (
    EMAIL_SETTINGS,
    REQUEST_HEADERS,
    SMTP_SERVER,
    TARGET_PRODUCT,
)


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
    tag_id = 'productTitle'
    product_tag = soup.find(name='span', id=tag_id)

    if product_tag is None:
        logger.error('No tag with id equal to %s was found.', tag_id)
        return ''

    return product_tag.get_text(strip=True)


def extract_price_data(soup: BeautifulSoup) -> dict[str, Any] | None:
    tag_class = 'twister-plus-buying-options-price-data'
    price_data_tag = soup.find(name='div', class_=tag_class)

    if price_data_tag is None:
        logger.error('No tag with class %s was found.', tag_class)
        return None

    try:
        price_data = json.loads(normalize_string(price_data_tag.get_text()))[0]
    except (IndexError, json.JSONDecodeError):
        logger.error('Failed to get price tag content.')
        return None

    return {
        'display_price': price_data['displayPrice'],
        'price_amount': float(price_data['priceAmount']),
    }


def send_email(client: EmailClient, product: Product) -> None:
    msg = make_message(
        from_address=EMAIL_SETTINGS.sender,
        to_address=cast(list[str], EMAIL_SETTINGS.recipients),
        subject=f'Amazon - Low Price for {product.title[:30]}...',
        body=f'We know you are interested in {product.title}.\n'
        f'Buy now for {product.display_price}.\n\n'
        f'Visit the link to buy: {product.link}',
    )
    client.send_message(msg)


def main() -> None:
    html_page = get_html_page(
        url=TARGET_PRODUCT.url,
        headers={
            'User-Agent': REQUEST_HEADERS.user_agent,
            'Accept-Language': REQUEST_HEADERS.accept_lang,
        },
    )
    soup = BeautifulSoup(html_page, 'lxml')

    logger.info('Scraping started...')
    product_title = extract_product_title(soup)
    price_data = extract_price_data(soup)
    logger.info('Scraping finished.')

    if not product_title:
        logger.critical(
            'The script will exit because the product title could '
            'not be obtained.'
        )
        return
    if not price_data:
        logger.critical(
            'The script will exit because the product price data '
            'could not be obtained.'
        )
        return
    if price_data['price_amount'] > TARGET_PRODUCT.price:
        logger.info(
            'The script will terminate given that the product price remains '
            'above the expected value.'
        )
        return

    product = Product(
        title=product_title, link=TARGET_PRODUCT.url, **price_data
    )

    email_client = EmailClient(
        smtp_server=SMTP(host=f'{SMTP_SERVER.host}:{SMTP_SERVER.port}'),
        credentials=(SMTP_SERVER.username, SMTP_SERVER.password),
    )

    logger.info('Sending alert email...')
    send_email(email_client, product)
    logger.info('Email sent.')


if __name__ == '__main__':
    logger = get_logger(__name__)
    main()
