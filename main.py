import argparse
import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import deduplicate_records
from processing.validation import validate_records
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "output"
LOG_DIR = ROOT_DIR / "logs"


def configure_logging():
    LOG_DIR.mkdir(exist_ok=True)
    log_path = LOG_DIR / "scraper.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def dump_csv(records, path):
    fieldnames = [
        "source",
        "source_url",
        "name_or_title",
        "category",
        "price",
        "rating",
        "author",
        "tags",
        "description",
        "scraped_at",
    ]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = {field: record.get(field, "") for field in fieldnames}
            if isinstance(row.get("tags"), list):
                row["tags"] = "; ".join(row["tags"])
            writer.writerow(row)


def scrape_all(max_pages=None):
    logger = logging.getLogger("scraping_assignment")
    start = datetime.now(timezone.utc)

    books = BooksScraper().scrape(max_pages=max_pages)
    quotes = QuotesScraper().scrape(max_pages=max_pages)

    cleaned = []
    for raw in books + quotes:
        cleaned.append(clean_record(raw, default_base_url="https://books.toscrape.com" if raw.get("source") == "Books to Scrape" else "https://quotes.toscrape.com"))

    valid_records, invalid_records = validate_records(cleaned)

    deduplicated_records, duplicates = deduplicate_records(valid_records)

    final_records = deduplicated_records
    elapsed = datetime.now(timezone.utc) - start

    summary = {
        "execution_started_at": start.isoformat(),
        "execution_time_seconds": round(elapsed.total_seconds(), 3),
        "sources": {
            "Books to Scrape": {
                "collected": len(books),
                "after_cleaning": sum(1 for record in cleaned if record.get("source") == "Books to Scrape"),
                "rejected": sum(1 for entry in invalid_records if entry["record"].get("source") == "Books to Scrape"),
                "duplicates_removed": sum(1 for record in duplicates if record.get("source") == "Books to Scrape"),
            },
            "Quotes to Scrape": {
                "collected": len(quotes),
                "after_cleaning": sum(1 for record in cleaned if record.get("source") == "Quotes to Scrape"),
                "rejected": sum(1 for entry in invalid_records if entry["record"].get("source") == "Quotes to Scrape"),
                "duplicates_removed": sum(1 for record in duplicates if record.get("source") == "Quotes to Scrape"),
            },
        },
        "total_records_collected": len(books) + len(quotes),
        "total_records_after_cleaning": len(cleaned),
        "records_rejected_during_validation": len(invalid_records),
        "duplicate_records_removed": len(duplicates),
        "final_record_count": len(final_records),
    }

    OUTPUT_DIR.mkdir(exist_ok=True)
    dump_csv(final_records, OUTPUT_DIR / "final_dataset.csv")
    with open(OUTPUT_DIR / "summary_report.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    logger.info("Scraping complete. Final dataset has %s records.", len(final_records))
    return final_records, summary


def main():
    parser = argparse.ArgumentParser(description="Scrape and consolidate data from books and quotes sources.")
    parser.add_argument("--max-pages", type=int, default=None, help="Optional limit on how many pages to scrape per source.")
    args = parser.parse_args()

    configure_logging()
    scrape_all(max_pages=args.max_pages)


if __name__ == "__main__":
    main()
