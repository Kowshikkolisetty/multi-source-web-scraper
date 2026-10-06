import logging
from time import sleep

import requests

LOGGER = logging.getLogger("scraping_assignment")


def fetch_html(url, max_retries=3, timeout=20):
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"},
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_error = exc
            LOGGER.warning("Request failed for %s (attempt %s/%s): %s", url, attempt, max_retries, exc)
            if attempt < max_retries:
                sleep(1.5 * attempt)
    raise RuntimeError(f"Unable to fetch {url}: {last_error}")
