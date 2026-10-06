import pytest

from processing.cleaning import clean_record, normalize_rating, parse_price
from processing.deduplication import deduplicate_records
from processing.validation import validate_record


def test_clean_record_converts_price_and_rating():
    raw = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/catalogue/test/index.html",
        "name_or_title": "  Example Title  ",
        "category": " Poetry ",
        "price": "£12.50",
        "rating": "Three",
        "author": "  Jane Doe  ",
        "tags": ["book", " book ", "fiction"],
        "description": "  Example description  ",
        "scraped_at": "2024-01-01T00:00:00Z",
    }

    cleaned = clean_record(raw)
    assert cleaned["name_or_title"] == "Example Title"
    assert cleaned["category"] == "Poetry"
    assert cleaned["price"] == 12.5
    assert cleaned["rating"] == 3
    assert cleaned["author"] == "Jane Doe"
    assert cleaned["tags"] == ["book", "fiction"]


def test_validate_record_rejects_invalid_url():
    record = {
        "source": "Quotes to Scrape",
        "source_url": "not-a-url",
        "name_or_title": "A sample quote",
        "price": None,
        "rating": 4,
        "author": "Alice",
    }
    result = validate_record(record)
    assert result["is_valid"] is False
    assert "source_url is not a valid HTTP URL" in result["errors"]


def test_deduplicate_records_handles_whitespace_and_case_variants():
    records = [
        {"source": "Books to Scrape", "name_or_title": "  Example Title  ", "author": "Jane Doe", "category": "Poetry"},
        {"source": "Books to Scrape", "name_or_title": "EXAMPLE TITLE", "author": " jane doe ", "category": "Poetry"},
        {"source": "Quotes to Scrape", "name_or_title": "Life is short", "author": "Alice"},
    ]

    kept, removed = deduplicate_records(records)
    assert len(kept) == 2
    assert len(removed) == 1
    assert kept[0]["name_or_title"] == "Example Title"


def test_helper_functions_handle_float_parse_and_rating_conversion():
    assert parse_price("£18.99") == 18.99
    assert normalize_rating("Four") == 4
    assert normalize_rating(2.1) == 2
