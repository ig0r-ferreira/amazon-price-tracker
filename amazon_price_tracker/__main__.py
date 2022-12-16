from typing import Any

import requests

from amazon_price_tracker.constants import PRODUCT_PAGE_URL, REQUEST_HEADERS


def get_html_page(url: str, headers: dict[str, Any] | None = None) -> str:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def main() -> None:
    html_page = get_html_page(url=PRODUCT_PAGE_URL, headers=REQUEST_HEADERS)
    print(len(html_page))


if __name__ == '__main__':
    main()
