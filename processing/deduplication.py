import re


def _normalize_surface_value(value):
    if value is None:
        return None
    text = str(value).strip()
    return re.sub(r"\s+", " ", text)


def _canonical_text(value):
    if value is None:
        return ""
    text = str(value).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def deduplicate_records(records):
    seen = {}
    kept = []
    removed = []

    for record in records:
        normalized_record = dict(record)
        if normalized_record.get("name_or_title") is not None:
            normalized_record["name_or_title"] = _normalize_surface_value(normalized_record["name_or_title"])
        if normalized_record.get("author") is not None:
            normalized_record["author"] = _normalize_surface_value(normalized_record["author"])
        if normalized_record.get("category") is not None:
            normalized_record["category"] = _normalize_surface_value(normalized_record["category"])

        source = normalized_record.get("source") or "unknown"
        title = _canonical_text(normalized_record.get("name_or_title"))
        author = _canonical_text(normalized_record.get("author"))

        if source == "Books to Scrape":
            key = (source, title, author or _canonical_text(normalized_record.get("category")))
        else:
            key = (source, title, author)

        if key in seen:
            removed.append(normalized_record)
            continue

        seen[key] = normalized_record
        kept.append(normalized_record)

    return kept, removed
