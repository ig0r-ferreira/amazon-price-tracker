import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import requests
from babel.numbers import NumberFormatError, parse_decimal
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from amazon_price_tracker.email_client import get_email_client, make_message
from amazon_price_tracker.log_manager import get_logger
from amazon_price_tracker.scraper import (
    extract_locale,
    extract_product_price,
    extract_product_title,
)
from amazon_price_tracker.settings import (
    EMAIL_SETTINGS,
    REQUEST_HEADERS,
    TARGET_PRODUCT,
)


@dataclass(frozen=True)
class Product:
    title: str
    price_amount: Decimal
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


def remove_currency_symbol(currency_str: str) -> str:
    return re.sub(r'[^\d,\.]+', '', currency_str)


def convert_currency_str_to_decimal(currency_str: str, locale: str) -> Decimal:
    return parse_decimal(
        remove_currency_symbol(currency_str), locale.replace('-', '_')
    )


def make_template_email(product: Product) -> dict[str, Any]:
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

    if (
        not (product_title := extract_product_title(soup))
        or not (product_price := extract_product_price(soup))
        or not (locale := extract_locale(soup))
    ):
        return

    try:
        price_amount = convert_currency_str_to_decimal(product_price, locale)
    except NumberFormatError:
        logger.exception(f'Failed to convert {product_price!a} to decimal.')
    else:
        if price_amount > TARGET_PRODUCT.price:
            return

        product = Product(
            title=product_title,
            link=TARGET_PRODUCT.url,
            price_amount=price_amount,
            display_price=product_price,
        )

        client = get_email_client()
        msg = make_message(
            from_address=EMAIL_SETTINGS.sender,
            to_address=EMAIL_SETTINGS.recipients,
            **make_template_email(product),
        )
        client.send_message(msg)


if __name__ == '__main__':
    logger = get_logger(__name__)
    logger.info('Started')
    main()
    logger.info('Finished')
