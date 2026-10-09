#!/usr/bin/env python3
"""Search the compact Meishe iOS Streaming SDK skill index."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "references" / "skill-lookup-index.json"


def tokens(value: str) -> set[str]:
    return {item for item in re.split(r"[^\w:+.-]+", value.casefold()) if item}


def alias_match(alias: str, query: str) -> bool:
    alias_folded = alias.casefold()
    if alias_folded in query:
        return True
    cjk = [char for char in alias_folded if "\u4e00" <= char <= "\u9fff"]
    return len(cjk) >= 2 and sum(char in query for char in cjk) >= max(2, len(cjk) - 1)


def score(entry: dict, query: str) -> int:
    query_folded = query.casefold()
    query_tokens = tokens(query)
    fields = [entry.get("id", ""), entry.get("title", ""), entry.get("category", "")]
    fields += entry.get("aliases", []) + entry.get("api_classes", []) + entry.get("api_signatures", [])
    haystack = " ".join(fields).casefold()
    value = sum(3 for token in query_tokens if token in tokens(haystack))
    value += sum(5 for alias in entry.get("aliases", []) if alias_match(alias, query_folded))
    value += sum(7 for api in entry.get("api_classes", []) if api.casefold() in query_folded)
    value += 10 if entry.get("id", "").casefold() in query_folded else 0
    return value


def compact(entry: dict) -> dict:
    keep = ["id", "title", "category", "api_refs", "feature_refs", "resource_keys", "module_ids", "blueprint_ids", "optional_template_features"]
    result = {key: entry.get(key, []) for key in keep}
    ids = entry.get("simple_code_ids", [])
    result["simple_code_ids"] = ids[:6]
    if len(ids) > 6:
        result["simple_code_ids_truncated"] = len(ids) - 6
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Search the compact Meishe iOS Streaming SDK skill lookup index.")
    parser.add_argument("query", nargs="*", help="User request, class, selector, or module terms.")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--compact", action="store_true", help="Keep routing fields and shorten long code-unit lists.")
    args = parser.parse_args()

    entries = json.loads(INDEX.read_text(encoding="utf-8"))["entries"]
    if args.list:
        output = [{"id": item["id"], "title": item["title"], "category": item["category"]} for item in entries]
    else:
        query = " ".join(args.query).strip()
        ranked = sorted(((score(item, query), item) for item in entries), key=lambda pair: (-pair[0], pair[1]["id"]))
        output = [item for item_score, item in ranked if item_score > 0][: max(1, args.limit)]
        if not output and query:
            output = entries[: max(1, args.limit)]
    if args.compact:
        output = [compact(item) for item in output]
    if args.json or True:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
