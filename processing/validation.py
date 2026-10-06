from urllib.parse import urlparse

RECOGNIZED_SOURCES = {"Books to Scrape", "Quotes to Scrape"}


def is_valid_url(url):
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_record(record):
    errors = []
    if not record.get("source"):
        errors.append("source is missing")
    elif record["source"] not in RECOGNIZED_SOURCES:
        errors.append("source is not recognized")

    if not record.get("name_or_title"):
        errors.append("name_or_title is missing")

    source_url = record.get("source_url")
    if not source_url:
        errors.append("source_url is missing")
    elif not is_valid_url(source_url):
        errors.append("source_url is not a valid HTTP URL")

    price = record.get("price")
    if price is not None and (not isinstance(price, (int, float)) or price < 0):
        errors.append("price is invalid")

    rating = record.get("rating")
    if rating is not None and (not isinstance(rating, (int, float)) or rating < 0 or rating > 5):
        errors.append("rating is outside the expected range")

    if record.get("author") is not None and not str(record["author"]).strip():
        errors.append("author is blank")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
    }


def validate_records(records):
    valid = []
    invalid = []

    for record in records:
        result = validate_record(record)
        if result["is_valid"]:
            valid.append(record)
        else:
            invalid.append({"record": record, "errors": result["errors"]})

    return valid, invalid
