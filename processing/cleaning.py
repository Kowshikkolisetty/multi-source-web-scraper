import re
from datetime import datetime, timezone
from urllib.parse import urljoin


def normalize_whitespace(value):
    if value is None:
        return None
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    return str(value).strip()


def normalize_text(value):
    normalized = normalize_whitespace(value)
    return normalized if normalized not in ("", "None", "null") else None


def normalize_url(value, base_url=None):
    normalized = normalize_text(value)
    if not normalized:
        return None
    if normalized.startswith(("http://", "https://")):
        return normalized
    if base_url:
        return urljoin(base_url, normalized)
    return normalized


def normalize_tags(value):
    if value is None:
        return []
    if isinstance(value, str):
        items = [item.strip() for item in value.split(",")]
    elif isinstance(value, list):
        items = value
    else:
        items = [str(value)]
    cleaned = []
    seen = set()
    for item in items:
        tag = normalize_text(item)
        if not tag:
            continue
        key = tag.lower()
        if key not in seen:
            cleaned.append(tag)
            seen.add(key)
    return cleaned


def parse_price(value):
    if value is None:
        return None
    text = normalize_text(value)
    if not text:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
    if not match:
        return None
    return float(match.group(0))


def normalize_rating(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        numeric = float(value)
        return round(numeric) if 0 <= numeric <= 5 else None

    text = normalize_text(value)
    if not text:
        return None

    mapping = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
    }
    lowered = text.lower()
    if lowered in mapping:
        return mapping[lowered]

    match = re.search(r"(\d+)", text)
    if match:
        rating = int(match.group(1))
        return rating if 0 <= rating <= 5 else None
    return None


def normalize_datetime(value):
    if value is None:
        return datetime.now(timezone.utc).isoformat()
    return value


def clean_record(record, default_base_url=None):
    if record is None:
        return {}

    cleaned = {}
    for field in [
        "source",
        "source_url",
        "name_or_title",
        "category",
        "price",
        "rating",
        "author",
        "tags",
        "description",
    ]:
        value = record.get(field)
        if field == "source_url":
            cleaned[field] = normalize_url(value, default_base_url)
        elif field == "price":
            cleaned[field] = parse_price(value)
        elif field == "rating":
            cleaned[field] = normalize_rating(value)
        elif field == "tags":
            cleaned[field] = normalize_tags(value)
        elif field == "description":
            cleaned[field] = normalize_text(value)
        else:
            cleaned[field] = normalize_text(value)

    cleaned["scraped_at"] = normalize_datetime(record.get("scraped_at"))
    return cleaned
