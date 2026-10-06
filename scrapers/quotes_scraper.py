import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .common import fetch_html

LOGGER = logging.getLogger("scraping_assignment")


class QuotesScraper:
    def __init__(self, base_url="https://quotes.toscrape.com"):
        self.base_url = base_url.rstrip("/")

    def _extract_author_details(self, author_url):
        try:
            html = fetch_html(author_url)
        except RuntimeError as exc:
            LOGGER.warning("Unable to fetch author page %s: %s", author_url, exc)
            return None

        soup = BeautifulSoup(html, "html.parser")
        details = soup.select_one("div.author-details")
        if not details:
            return None

        return re.sub(r"\s+", " ", details.get_text(" ", strip=True)).strip()

    def scrape(self, max_pages=None):
        records = []
        page_number = 1
        seen_urls = set()

        while True:
            if page_number == 1:
                page_url = f"{self.base_url}/"
            else:
                page_url = f"{self.base_url}/page/{page_number}/"

            if page_url in seen_urls:
                break
            seen_urls.add(page_url)

            try:
                html = fetch_html(page_url)
            except RuntimeError as exc:
                LOGGER.warning("Failed to fetch quotes page %s: %s", page_url, exc)
                break

            soup = BeautifulSoup(html, "html.parser")
            quotes = soup.select("div.quote")
            if not quotes:
                LOGGER.info("No quote records found on %s; stopping pagination.", page_url)
                break

            for quote in quotes:
                text_elem = quote.select_one("span.text")
                author_elem = quote.select_one("small.author")
                tag_elems = quote.select("a.tag")

                if not text_elem:
                    continue

                text = text_elem.get_text(" ", strip=True)
                author = author_elem.get_text(" ", strip=True) if author_elem else None
                tags = [tag.get_text(" ", strip=True) for tag in tag_elems if tag.get_text(" ", strip=True)]

                description = None
                author_link = quote.select_one('a[href*="/author/"]')
                if author_link and author_link.get("href"):
                    author_url = urljoin(self.base_url, author_link.get("href"))
                    description = self._extract_author_details(author_url)

                record = {
                    "source": "Quotes to Scrape",
                    "source_url": page_url,
                    "name_or_title": text,
                    "category": None,
                    "price": None,
                    "rating": None,
                    "author": author,
                    "tags": tags,
                    "description": description,
                }
                records.append(record)

            next_link = soup.select_one("li.next > a")
            if not next_link or (max_pages is not None and page_number >= max_pages):
                break

            page_number += 1

        LOGGER.info("Collected %s records from Quotes to Scrape.", len(records))
        return records
