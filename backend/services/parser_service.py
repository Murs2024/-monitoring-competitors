"""
Сервис парсинга веб-страниц: HTTP + BeautifulSoup или Selenium (USE_SELENIUM=true).
"""
import asyncio
import time
from typing import Optional, Tuple

import httpx
from bs4 import BeautifulSoup

from backend.config import settings


def _extract_from_soup(soup: BeautifulSoup) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Извлечь title, h1, первый абзац из BeautifulSoup. Returns (title, h1, first_paragraph)."""
    title = None
    if soup.find("title"):
        title = soup.find("title").get_text(strip=True)
    h1 = None
    if soup.find("h1"):
        h1 = soup.find("h1").get_text(strip=True)
    first_paragraph = None
    main = soup.find(["main", "article"]) or soup.find("body")
    if main:
        for p in main.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 50:
                first_paragraph = text[:500]
                break
    return title, h1, first_paragraph


class ParserService:
    """Парсинг веб-страниц: title, h1, первый абзац. HTTP или Selenium по настройке."""

    def __init__(self):
        self.timeout = settings.parser_timeout
        self.user_agent = settings.parser_user_agent

    def _parse_with_selenium(
        self, url: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        Синхронный парсинг через Selenium (для страниц с JavaScript).
        Returns: (title, h1, first_paragraph, error)
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager

            opts = Options()
            opts.add_argument("--headless=new")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument(f"user-agent={self.user_agent}")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=opts)
            try:
                driver.get(url)
                time.sleep(settings.parser_selenium_wait)
                html = driver.page_source
            finally:
                driver.quit()
            soup = BeautifulSoup(html, "lxml")
            title, h1, first_paragraph = _extract_from_soup(soup)
            return title, h1, first_paragraph, None
        except Exception as e:
            return None, None, None, f"Selenium: {str(e)}"

    async def parse_url(
        self, url: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        Парсит URL, извлекает title, h1, первый абзац.
        При USE_SELENIUM=true использует Selenium (для страниц с JS).
        Returns: (title, h1, first_paragraph, error)
        """
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        if settings.use_selenium:
            return await asyncio.to_thread(self._parse_with_selenium, url)

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": self.user_agent},
                )
                response.raise_for_status()
                html = response.text
                soup = BeautifulSoup(html, "lxml")
                title, h1, first_paragraph = _extract_from_soup(soup)
                return title, h1, first_paragraph, None
        except httpx.TimeoutException:
            return None, None, None, "Превышено время ожидания запроса"
        except httpx.HTTPStatusError as e:
            return None, None, None, f"HTTP ошибка: {e.response.status_code}"
        except httpx.RequestError as e:
            return None, None, None, f"Ошибка запроса: {str(e)}"
        except Exception as e:
            return None, None, None, f"Неизвестная ошибка: {str(e)}"


parser_service = ParserService()
