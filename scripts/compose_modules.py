#!/usr/bin/env python3
"""Resolve dependency-closed Meishe iOS Streaming SDK module plans."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "references" / "sdk-module-registry.json"
INDEX_PATH = ROOT / "references" / "skill-lookup-index.json"


def split_ids(value: str | None) -> list[str]:
    return [item for item in re.split(r"[,\s]+", value or "") if item]


def load() -> tuple[dict, dict[str, dict], dict[str, dict], dict[str, dict]]:
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    modules = {item["id"]: item for item in data["modules"]}
    recipes = {item["id"]: item for item in data["api_recipes"]}
    blueprints = {item["id"]: item for item in data["blueprints"]}
    return data, modules, recipes, blueprints


def query_routes(query: str) -> tuple[list[str], list[str]]:
    if not query:
        return [], []
    entries = json.loads(INDEX_PATH.read_text(encoding="utf-8"))["entries"]
    folded = query.casefold()
    scored = []
    for item in entries:
        terms = [item["id"], item["title"], *item.get("aliases", []), *item.get("api_classes", [])]
        score = sum(1 for term in terms if term.casefold() in folded or folded in term.casefold())
        if score:
            scored.append((score, item))
    scored.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    module_ids: list[str] = []
    blueprint_ids: list[str] = []
    for _, item in scored[:5]:
        module_ids.extend(item.get("module_ids", []))
        blueprint_ids.extend(item.get("blueprint_ids", []))
    return list(dict.fromkeys(module_ids)), list(dict.fromkeys(blueprint_ids))


def compose(module_ids: list[str], blueprint_ids: list[str], mode: str) -> dict:
    _, modules, recipes, blueprints = load()
    unknown_modules = sorted(set(module_ids) - modules.keys())
    unknown_blueprints = sorted(set(blueprint_ids) - blueprints.keys())
    if unknown_modules or unknown_blueprints:
        raise ValueError(f"Unknown modules={unknown_modules}, blueprints={unknown_blueprints}")
    if mode == "new-app" and len(blueprint_ids) > 1:
        raise ValueError("Select at most one product blueprint for new-app mode.")

    requested = list(module_ids)
    for blueprint_id in blueprint_ids:
        requested.extend(blueprints[blueprint_id].get("requires", []))

    ordered: list[str] = []
    active: set[str] = set()
    done: set[str] = set()

    def visit(module_id: str) -> None:
        if module_id in done:
            return
        if module_id in active:
            raise ValueError(f"Dependency cycle at {module_id}")
        if module_id not in modules:
            raise ValueError(f"Module dependency does not exist: {module_id}")
        active.add(module_id)
        for dependency in modules[module_id].get("requires", []):
            visit(dependency)
        active.remove(module_id)
        done.add(module_id)
        ordered.append(module_id)

    for module_id in dict.fromkeys(requested):
        visit(module_id)

    module_items = [modules[item] for item in ordered]
    recipe_ids = list(dict.fromkeys(recipe for item in module_items for recipe in item.get("api_recipes", [])))
    unit_ids = list(dict.fromkeys(unit for item in module_items for unit in item.get("simple_code_ids", [])))
    resources = list(dict.fromkeys(resource for item in module_items for resource in item.get("resources", [])))
    permissions = list(dict.fromkeys(permission for item in module_items for permission in item.get("privacy_usage_descriptions", [])))
    templates = list(dict.fromkeys(feature for item in module_items for feature in item.get("template_features", [])))
    return {
        "mode": mode,
        "blueprints": blueprint_ids,
        "requested_modules": list(dict.fromkeys(module_ids)),
        "resolved_modules": ordered,
        "api_recipes": recipe_ids,
        "simple_code_ids": unit_ids,
        "resources": resources,
        "privacy_usage_descriptions": permissions,
        "template_features": templates,
        "guards": list(dict.fromkeys(guard for item in module_items for guard in item.get("guards", []))),
        "verification_states": {item["id"]: item.get("verification_state", "contract_only") for item in module_items},
        "recipe_details": [recipes[item] for item in recipe_ids if item in recipes]
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compose dependency-closed Meishe iOS Streaming SDK modules.")
    parser.add_argument("--query", default="", help="Natural-language feature or application request.")
    parser.add_argument("--modules", default="", help="Comma/space-separated module IDs.")
    parser.add_argument("--blueprint", default="", help="One product blueprint ID for new-app mode.")
    parser.add_argument("--mode", choices=["new-app", "incremental", "api-only"], default="new-app")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    _, modules, _, blueprints = load()
    if args.list:
        print(json.dumps({"modules": sorted(modules), "blueprints": sorted(blueprints)}, indent=2))
        return 0
    module_ids = split_ids(args.modules)
    blueprint_ids = split_ids(args.blueprint)
    routed_modules, routed_blueprints = query_routes(args.query)
    module_ids.extend(item for item in routed_modules if item not in module_ids)
    if not blueprint_ids and args.mode == "new-app" and routed_blueprints:
        blueprint_ids = routed_blueprints[:1]
    plan = compose(module_ids, blueprint_ids, args.mode)
    if args.compact:
        plan.pop("recipe_details", None)
        plan["simple_code_ids"] = plan["simple_code_ids"][:12]
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
