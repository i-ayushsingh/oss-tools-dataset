"""
validate_schema.py
──────────────────
Validates data/tools.csv (or a given CSV file) against the expected schema.
Exits with code 1 if any errors are found — used in CI to block bad PRs.

Usage:
  python scripts/validate_schema.py
  python scripts/validate_schema.py --file data/tools.csv
"""

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

# ─── Schema ────────────────────────────────────────────────────────────────────
REQUIRED_COLUMNS = [
    "id", "name", "description", "github_url", "website_url", "stars",
    "last_updated", "tags", "platforms", "license", "origin_country",
    "language", "country_code", "is_archived", "owner_type", "avatar_url",
    "latest_release_tag", "latest_release_at", "pricing_type", "is_self_hosted",
]

VALID_PRICING  = {"Free", "Freemium", "Paid"}
VALID_OWNER    = {"User", "Organization", ""}
UUID_RE        = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
GITHUB_URL_RE  = re.compile(r"^https://github\.com/[^/]+/[^/]+")


# ─── Checks ────────────────────────────────────────────────────────────────────
def check(errors: list, condition: bool, msg: str):
    if not condition:
        errors.append(msg)


def validate(csv_path: Path) -> list[str]:
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    errors = []

    # Column presence
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        errors.append(f"Missing columns: {sorted(missing)}")
        return errors   # can't continue without columns

    # Per-row checks
    for i, row in df.iterrows():
        row_id = row.get("id", f"row {i+2}")
        prefix = f"[{row_id}]"

        check(errors, bool(UUID_RE.match(row["id"])),
              f"{prefix} invalid UUID: {row['id']!r}")

        check(errors, bool(row["name"].strip()),
              f"{prefix} 'name' is empty")

        check(errors, bool(row["description"].strip()),
              f"{prefix} 'description' is empty")

        if row["github_url"].strip():
            check(errors, bool(GITHUB_URL_RE.match(row["github_url"])),
                  f"{prefix} invalid github_url: {row['github_url']!r}")

        if row["stars"].strip():
            try:
                int(float(row["stars"]))
            except ValueError:
                errors.append(f"{prefix} 'stars' is not numeric: {row['stars']!r}")

        check(errors, row["pricing_type"] in VALID_PRICING,
              f"{prefix} invalid pricing_type: {row['pricing_type']!r} (must be {VALID_PRICING})")

        if row["owner_type"].strip():
            check(errors, row["owner_type"] in VALID_OWNER,
                  f"{prefix} invalid owner_type: {row['owner_type']!r}")

    # Duplicate IDs
    dupes = df[df["id"].duplicated(keep=False)]["id"].unique()
    if len(dupes):
        errors.append(f"Duplicate IDs: {list(dupes)}")

    return errors


# ─── Entry point ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="data/tools.csv")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"❌ File not found: {path}")
        sys.exit(1)

    print(f"🔍 Validating {path} …")
    errors = validate(path)

    if errors:
        print(f"\n❌ {len(errors)} error(s) found:\n")
        for e in errors[:50]:   # cap at 50 so CI logs stay readable
            print(f"  • {e}")
        if len(errors) > 50:
            print(f"  … and {len(errors) - 50} more")
        sys.exit(1)
    else:
        df = pd.read_csv(path)
        print(f"✅ All {len(df)} rows valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
