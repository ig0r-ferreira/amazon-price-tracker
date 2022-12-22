import json
import unicodedata
from typing import Any

from bs4 import BeautifulSoup

from amazon_price_tracker.log_manager import get_logger

logger = get_logger(__name__)


def normalize_string(text: str) -> str:
    return unicodedata.normalize('NFKD', text)


def extract_product_title(soup: BeautifulSoup) -> str:
    tag_id = 'productTitle'
    tag = soup.find(name='span', id=tag_id)

    if tag is None:
        logger.error(f'No tag with id equal to {tag_id} was found.')
        return ''

    return tag.get_text(strip=True)


def extract_product_price(soup: BeautifulSoup) -> str:
    tag_class = 'a-offscreen'
    tag = soup.find(name='span', class_=tag_class)

    if tag is None:
        logger.error(f'No tag with class {tag_class} was found.')
        return ''

    return tag.get_text(strip=True)


def extract_locale(soup: BeautifulSoup) -> str:
    tag_class = 'twister-plus-buying-options-price-data'
    tag = soup.find(name='div', class_=tag_class)

    if tag is None:
        logger.error(f'No tag with class {tag_class} was found.')
        return ''

    try:
        price_data: dict[str, Any] = json.loads(
            normalize_string(tag.get_text(strip=True))
        )[0]
    except (IndexError, json.JSONDecodeError):
        logger.error('Failed to extract page locale from tag content.')
        return ''

    return price_data.get('locale', '')
