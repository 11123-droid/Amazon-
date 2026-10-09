#!/usr/bin/env python3
"""Validate dashboard data and inject it into the fixed offline HTML template."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PLACEHOLDER = "__LOW_RATING_DASHBOARD_DATA_JSON__"
REQUIRED_TOP = {
    "status",
    "blockReason",
    "marketplace",
    "rootCategory",
    "rootNodeIdPath",
    "month",
    "maxAvgRating",
    "minAvgRatings",
    "resultCount",
    "items",
}
REQUIRED_ITEM = {"nodeIdPath", "avgRating", "categoryPathEn", "categoryPathZh"}


def validate(data: dict) -> None:
    missing = REQUIRED_TOP - data.keys()
    if missing:
        raise ValueError(f"missing top-level fields: {sorted(missing)}")
    if data["status"] not in {"ready", "blocked"}:
        raise ValueError("status must be ready or blocked")
    if data["status"] == "blocked":
        if not str(data["blockReason"]).strip():
            raise ValueError("blocked output requires blockReason")
        if data["items"]:
            raise ValueError("blocked output must not contain items")
        return

    items = data["items"]
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if data["resultCount"] != len(items):
        raise ValueError("resultCount does not equal item count")

    seen: set[str] = set()
    expected_order: list[tuple[float, str]] = []
    for item in items:
        missing_item = REQUIRED_ITEM - item.keys()
        if missing_item:
            raise ValueError(f"missing item fields: {sorted(missing_item)}")
        path = str(item["nodeIdPath"])
        rating = float(item["avgRating"])
        if path in seen:
            raise ValueError(f"duplicate nodeIdPath: {path}")
        seen.add(path)
        if len(path.split(":")) < 4:
            raise ValueError(f"node path has fewer than four levels: {path}")
        if not 0 < rating <= float(data["maxAvgRating"]):
            raise ValueError(f"rating outside threshold: {path}")
        if not str(item["categoryPathEn"]).strip() or not str(item["categoryPathZh"]).strip():
            raise ValueError(f"empty category path: {path}")
        expected_order.append((rating, path))

    for path in seen:
        if any(other != path and other.startswith(path + ":") for other in seen):
            raise ValueError(f"parent node remains in final items: {path}")
    if expected_order != sorted(expected_order):
        raise ValueError("items are not sorted by avgRating then nodeIdPath")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=Path, help="Dashboard JSON input")
    parser.add_argument("--output", type=Path, help="Output HTML path")
    args = parser.parse_args()

    data = json.loads(args.data.read_text(encoding="utf-8"))
    validate(data)
    template_path = Path(__file__).resolve().parents[1] / "assets" / "dashboard-template.html"
    template = template_path.read_text(encoding="utf-8")
    if template.count(PLACEHOLDER) != 1:
        raise ValueError("template must contain exactly one data placeholder")

    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    output = args.output or Path.cwd() / "outputs" / (
        f"amazon_low_rating_leaf_categories_{data['marketplace']}_{data['month']}.html"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template.replace(PLACEHOLDER, payload), encoding="utf-8", newline="\n")
    print(output.resolve())


if __name__ == "__main__":
    main()
