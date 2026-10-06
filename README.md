# Multi-Source Web Scraping & Data Consolidation

## Project overview
This project scrapes public data from Books to Scrape and Quotes to Scrape, cleans and standardizes the records, validates them, removes duplicates, and exports a final consolidated dataset to the `output/` folder.

## Python version
Python 3.11+

## Installation and setup
1. Clone or download the project.
2. Create a virtual environment and activate it.
3. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Dependencies
- requests
- beautifulsoup4
- pandas
- pytest

## How to run the scraper
From the project root:

```bash
python main.py
```

Optional page limit:

```bash
python main.py --max-pages 3
```

## How pagination works
- Books to Scrape iterates over listing pages in the pattern `/catalogue/page-N.html`, starting from the root landing page.
- Quotes to Scrape iterates over `/page/N/` until the scraper sees no more `div.quote` elements or no `li.next` link.
- The scraper stops when a page contains no records or pagination ends.

## Data model
The final output uses a common schema to represent each record:

- `source`: source name
- `source_url`: original URL of the item or page
- `name_or_title`: primary title or quote text
- `category`: category when available
- `price`: numeric price when available
- `rating`: numeric rating from 0 to 5 when available
- `author`: author name when present
- `tags`: list of tags for quote records
- `description`: description or additional metadata
- `scraped_at`: timestamp of scraping

Missing fields are stored as `null` / empty values in the cleaned data, and validation rejects clearly incomplete records.

## Cleaning approach
The cleaning layer normalizes the raw fields before validation:
- trim extra whitespace
- collapse repeated spaces
- convert prices from strings such as `£51.77` into numeric values
- normalize star ratings from text like `Three` into integers such as `3`
- normalize URLs into absolute URLs when needed
- convert tags to a clean list and remove duplicates
- ensure missing values are stored consistently

## Validation approach
Records are validated before deduplication:
- required fields such as `source`, `name_or_title`, and `source_url` must exist
- URLs must look like valid HTTP/HTTPS addresses
- price values must be numeric and non-negative
- rating values must be between 0 and 5
- source names must be one of the known sources

Invalid records are kept in an internal rejection list, and the final export only includes valid records.

## Deduplication approach
Duplicate detection uses a normalized fingerprint based on:
- source
- normalized title / quote text
- normalized author name
- category for Books to Scrape records

The logic intentionally normalizes differences in whitespace, capitalization, and punctuation so equivalent records are treated as duplicates even when formatting differs. The first valid occurrence is retained; later duplicates are removed and counted in the summary report.

## Error handling approach
The scraper catches and logs common issues such as:
- connection failures
- HTTP errors
- timeouts
- missing elements
- unexpected page structures
- partial failures on individual pages

The scraper continues processing other pages and sources rather than aborting the whole run.

## Output description
The project writes:

- `output/final_dataset.csv`: final standardized dataset
- `output/summary_report.json`: summary metrics and counts
- `logs/scraper.log`: detailed execution log

## Assumptions
- The target sites are public and accessible as documented.
- Books to Scrape detail pages are the primary source of category and description details.
- Quotes to Scrape supports pagination through the standard `/page/N/` pattern.

## Known limitations
- The scraped quote dataset does not include a formal per-item URL because the site exposes quotes within paginated pages rather than unique quote pages.
- Some site fields are optional and may be missing depending on the record.
- The solution is tuned for these public practice websites and not a general-purpose scraper for arbitrary sites.

## AI usage summary
This project used AI-assisted review and debugging for selector validation, data-model design, and refinement of the cleaning and validation flow. The final implementation was reviewed, corrected, and verified by running the actual pipeline end-to-end.
