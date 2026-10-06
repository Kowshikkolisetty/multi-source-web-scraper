import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .common import fetch_html

LOGGER = logging.getLogger("scraping_assignment")


class BooksScraper:
    def __init__(self, base_url="https://books.toscrape.com"):
        self.base_url = base_url.rstrip("/")

    def _parse_rating(self, rating_element):
        if rating_element is None:
            return None
        classes = rating_element.get("class", [])
        for cls in classes:
            if cls.lower() in {"one", "two", "three", "four", "five"}:
                return cls.lower()
        return None

    def _extract_book_from_detail_page(self, page_url, soup):
        title_tag = soup.select_one("h1")
        title = title_tag.get_text(" ", strip=True) if title_tag else None

        breadcrumb = soup.select("ul.breadcrumb li a")
        category = breadcrumb[-1].get_text(" ", strip=True) if len(breadcrumb) >= 2 else None

        price = soup.select_one(".price_color")
        price_text = price.get_text(" ", strip=True) if price else None

        rating_elem = soup.select_one(".star-rating")
        rating = self._parse_rating(rating_elem)

        description_elem = soup.select_one("#product_description + p")
        description = description_elem.get_text(" ", strip=True) if description_elem else None

        return {
            "source": "Books to Scrape",
            "source_url": page_url,
            "name_or_title": title,
            "category": category,
            "price": price_text,
            "rating": rating,
            "author": None,
            "tags": [],
            "description": description,
        }

    def scrape(self, max_pages=None):
        records = []
        page_number = 1
        seen_urls = set()

        while True:
            if page_number == 1:
                page_url = f"{self.base_url}/"
            else:
                page_url = f"{self.base_url}/catalogue/page-{page_number}.html"

            if page_url in seen_urls:
                break
            seen_urls.add(page_url)

            try:
                html = fetch_html(page_url)
            except RuntimeError as exc:
                LOGGER.warning("Failed to fetch books page %s: %s", page_url, exc)
                break

            soup = BeautifulSoup(html, "html.parser")
            items = soup.select("article.product_pod")
            if not items:
                LOGGER.info("No book records found on %s; stopping pagination.", page_url)
                break

            for item in items:
                link = item.select_one("h3 a")
                if not link:
                    continue
                href = link.get("href")
                if not href:
                    continue
                detail_url = urljoin(page_url, href)
                try:
                    detail_html = fetch_html(detail_url)
                    detail_soup = BeautifulSoup(detail_html, "html.parser")
                    record = self._extract_book_from_detail_page(detail_url, detail_soup)
                    records.append(record)
                except RuntimeError as exc:
                    LOGGER.warning("Unable to scrape book detail page %s: %s", detail_url, exc)
                    continue

            next_link = soup.select_one("li.next a")
            if not next_link or (max_pages is not None and page_number >= max_pages):
                break

            page_number += 1

        LOGGER.info("Collected %s records from Books to Scrape.", len(records))
        return records
