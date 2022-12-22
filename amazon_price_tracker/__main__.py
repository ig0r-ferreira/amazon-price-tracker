import json
import unicodedata
from dataclasses import dataclass
from typing import Any

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from amazon_price_tracker.email_client import get_email_client, make_message
from amazon_price_tracker.log_manager import get_logger
from amazon_price_tracker.settings import (
    EMAIL_SETTINGS,
    REQUEST_HEADERS,
    TARGET_PRODUCT,
)


@dataclass(frozen=True)
class Product:
    title: str
    price_amount: float
    display_price: str
    link: str


def get_html_page(url: str, headers: dict[str, Any] | None = None) -> str:
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except RequestException:
        logger.exception('Error accessing the page.')
        return ''
    else:
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


def extract_price_data(soup: BeautifulSoup) -> dict[str, Any]:
    tag_class = 'twister-plus-buying-options-price-data'
    price_data_tag = soup.find(name='div', class_=tag_class)

    if price_data_tag is None:
        logger.error('No tag with class %s was found.', tag_class)
        return {}

    try:
        price_data = json.loads(normalize_string(price_data_tag.get_text()))[0]
    except (IndexError, json.JSONDecodeError):
        logger.error('Failed to get price tag content.')
        return {}

    return {
        'display_price': price_data['displayPrice'],
        'price_amount': float(price_data['priceAmount']),
    }


def get_template_email(product: Product) -> dict[str, Any]:
    return {
        'subject': f'Amazon - Low Price for {product.title[:30]}...',
        'body': f'We know you are interested in {product.title}.\n'
        f'Buy now for {product.display_price}.\n\n'
        f'Visit the link to buy: {product.link}',
    }


def main() -> None:
    html_page = get_html_page(
        url=TARGET_PRODUCT.url,
        headers={
            'User-Agent': REQUEST_HEADERS.user_agent,
            'Accept-Language': REQUEST_HEADERS.accept_lang,
        },
    )

    if not html_page:
        return

    soup = BeautifulSoup(html_page, 'lxml')

    if not (product_title := extract_product_title(soup)):
        return

    price_data = extract_price_data(soup)
    price_amount = price_data.get('price_amount')

    if not price_amount or price_amount > TARGET_PRODUCT.price:
        return

    product = Product(
        title=product_title, link=TARGET_PRODUCT.url, **price_data
    )

    client = get_email_client()
    msg = make_message(
        from_address=EMAIL_SETTINGS.sender,
        to_address=EMAIL_SETTINGS.recipients,
        **get_template_email(product),
    )
    client.send_message(msg)


if __name__ == '__main__':
    logger = get_logger(__name__)
    logger.info('Started')
    main()
    logger.info('Finished')
