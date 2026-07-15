import httpx
from bs4 import BeautifulSoup
from decimal import Decimal, InvalidOperation
import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PriceParser:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    @classmethod
    async def get_html(cls, url: str) -> Optional[str]:
        """Асинхронно скачивает HTML-код страницы."""
        async with httpx.AsyncClient(headers=cls.HEADERS, timeout=10.0, follow_redirects=True) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.text
                logger.error(f"Ошибка скачивания страницы {url}: Статус {response.status_code}")
                return None
            except Exception as e:
                logger.error(f"Сетевая ошибка при запросе к {url}: {e}")
                return None

    @classmethod
    def _clean_price(cls, price_str: str) -> Optional[Decimal]:
        """Очищает строку от пробелов, знаков валют и конвертирует в Decimal."""
        cleaned = price_str.replace('\xa0', '').replace(' ', '')
        match = re.search(r'[\d.,]+', cleaned)
        if not match:
            return None

        price_val = match.group(0).replace(',', '.')
        try:
            return Decimal(price_val)
        except InvalidOperation:
            return None

    @classmethod
    async def parse_product(cls, url: str) -> tuple[Optional[str], Optional[Decimal]]:
        """
        Главный метод: парсит страницу.
        Возвращает кортеж: (Название_товара, Текущая_цена)
        """
        html = await cls.get_html(url)
        if not html:
            return None, None

        soup = BeautifulSoup(html, "html.parser")

        title = None
        title_tag = soup.find('h1', attrs={"itemprop": "name"})
        if title_tag:
            title = title_tag.get_text(strip=True)

        price = None
        price_tag = soup.find('span', attrs={"itemprop": "price"})
        if price_tag:
            price = cls._clean_price(price_tag.get_text())

        return title, price
