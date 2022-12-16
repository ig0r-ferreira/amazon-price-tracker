from typing import Any

import requests
from bs4 import BeautifulSoup

from amazon_price_tracker.constants import (
    PRODUCT_PAGE_URL,
    REQUEST_HEADERS,
    TARGET_PRICE,
)


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
    whole_part = whole_part.rstrip(',.').replace('.', '_')
    return float(whole_part) + (int(decimal_part) / 100)


def main() -> None:
    html_page = get_html_page(url=PRODUCT_PAGE_URL, headers=REQUEST_HEADERS)
    soup = BeautifulSoup(html_page, 'lxml')

    price = extract_price(soup)

    if price is None:
        return

    product_price = format_price(*price)
    if product_price <= TARGET_PRICE:
        print(
            'The product you are interested in has reached the desired price.',
            f'Current price: {product_price:.2f}',
            sep='\n',
        )


if __name__ == '__main__':
    main()
