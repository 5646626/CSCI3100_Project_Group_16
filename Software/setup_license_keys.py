import argparse
import json
import os
from typing import List, Dict, Any

from bson import ObjectId

from services.licence_service import LicenceService
from repositories.licence_repository import LicenceRepository
from setup_schema import ensure_schema


def load_from_json(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Accept either list of strings or list of objects with key/role
    if isinstance(data, list):
        normalized = []
        for item in data:
            if isinstance(item, str):
                normalized.append({"key": item, "role": "Members"})
            elif isinstance(item, dict):
                key = item.get("key")
                role = item.get("role", "Members")
                if not key:
                    raise ValueError("JSON item missing 'key' field")
                normalized.append({"key": key, "role": role})
            else:
                raise ValueError("Unsupported JSON item format; use string or {key, role}")
        return normalized
    raise ValueError("Unsupported JSON format; expected a list")


def seed_keys(records: List[Dict[str, Any]], dry_run: bool = False) -> Dict[str, int]:
    # Ensure DB schema (including unique indexes) before seeding keys
    try:
        ensure_schema()
    except Exception as e:
        print(f"Warning: Schema setup failed before seeding: {e}")

    repo = LicenceRepository()  # ensures indexes
    service = LicenceService(repo)

    inserted = 0
    skipped = 0
    errors = 0

    for rec in records:
        key = rec.get("key")
        role = rec.get("role", "Members")
        if not key:
            print("Skipping record with no 'key' field")
            errors += 1
            continue

        # Skip duplicates
        existing = repo.find_licence_by_key(key)
        if existing:
            print(f"Skip existing key: {key} (role={existing.role})")
            skipped += 1
            continue

        if dry_run:
            print(f"[dry-run] Would insert key: {key} role={role}")
            inserted += 1
            continue

        try:
            # Owner not assigned yet in seed (None). When redeemed, app can set owner.
            service.create_licence(key=key, owner_id=None, role=role)  # type: ignore[arg-type]
            print(f"Inserted key: {key} role={role}")
            inserted += 1
        except Exception as e:
            print(f"Error inserting {key}: {e}")
            errors += 1

    return {"inserted": inserted, "skipped": skipped, "errors": errors}


def main():
    parser = argparse.ArgumentParser(
        description="Seed initial licence keys into the database (with roles)."
    )
    parser.add_argument(
        "--from-json",
        dest="json_path",
        help="Path to JSON file: either ['AAAA-...', ...] or [{key, role}, ...]",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and show actions without inserting",
    )

    args = parser.parse_args()

    # Determine JSON path: CLI arg or default to project-root/license.json
    json_path = args.json_path
    if not json_path:
        project_root = os.path.dirname(__file__)
        default_json = os.path.join(project_root, "license.json")
        if os.path.exists(default_json):
            json_path = default_json
        else:
            print("Error: Provide --from-json <path> or create license.json in the project root.")
            return

    records = load_from_json(json_path)

    summary = seed_keys(records, dry_run=args.dry_run)
    print(
        f"\nSummary: inserted={summary['inserted']} skipped={summary['skipped']} errors={summary['errors']}"
    )


if __name__ == "__main__":
    main()
