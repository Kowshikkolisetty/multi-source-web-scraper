# AI Usage

## Tools used
- GitHub Copilot / AI coding assistant
- General code review and debugging assistance

## What each tool was used for
- Explaining site structure and selecting valid HTML selectors
- Designing a common data model for heterogeneous sources
- Drafting the cleaning, validation, and deduplication logic
- Reviewing the pipeline for edge cases such as missing fields and failed requests
- Improving documentation and final verification steps

## Representative prompts
- "Inspect the HTML structure of Books to Scrape and tell me the best selectors for book title, price, and rating."
- "Design a cleaning and validation pipeline for records from Books to Scrape and Quotes to Scrape."
- "Create a deduplication strategy that normalizes whitespace and capitalization differences."

## Which parts of the code were AI-assisted
- Selector strategy for book detail pages and quote pagination
- Initial structure for the standardized schema
- Initial implementation of validation and duplicate detection logic
- Documentation structure and summary metrics design

## Important changes made after reviewing AI output
- Switched from a single generic scraper to separate source-specific scraper modules
- Added explicit source-aware logic for duplicate matching and filtering
- Improved logging to continue past partial failures without aborting the full run
- Added a validation layer and clearer record rejection handling

## Incorrect or incomplete AI-generated suggestions discovered
- Initial generic selectors were too broad and required source-specific handling for nested breadcrumb and quote layouts.
- Duplicate detection needed to be source-aware; a generic title-only rule would wrongly conflate quote and book records.
- The final project needed explicit summary metrics and persistent log output instead of only in-memory prints.

## How the final solution was tested and verified
- The project was run end-to-end with the real public sites.
- The final dataset and summary report were generated in `output/`.
- The cleaning, validation, and duplication functions were tested with small unit tests to confirm correct behavior.
