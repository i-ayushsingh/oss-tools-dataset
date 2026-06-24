"""
refresh_github_meta.py
─────────────────────
Fetches fresh GitHub metadata for every tool in data/tools.json
and writes updated CSV, JSON, and SQL files.

Requirements:
  pip install requests pandas tqdm

Usage:
  GITHUB_TOKEN=ghp_xxx python scripts/refresh_github_meta.py
"""

import json
import os
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

# ─── Config ────────────────────────────────────────────────────────────────────
DATA_DIR   = Path(__file__).parent.parent / "data"
JSON_PATH  = DATA_DIR / "tools.json"
CSV_PATH   = DATA_DIR / "tools.csv"
SQL_PATH   = DATA_DIR / "tools.sql"

GITHUB_API  = "https://api.github.com"
TOKEN       = os.environ.get("GITHUB_TOKEN", "")          # set via env or GH secret
HEADERS     = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}
RATE_SLEEP  = 0.5   # seconds between API calls to stay well under 5 000/hr limit


# ─── Helpers ───────────────────────────────────────────────────────────────────
def extract_repo_path(github_url: str) -> str | None:
    """Extract 'owner/repo' from a GitHub URL."""
    match = re.search(r"github\.com/([^/]+/[^/?\s#]+)", github_url or "")
    return match.group(1).rstrip("/") if match else None


def fetch_repo(repo_path: str) -> dict | None:
    """Return the GitHub API repo object, or None on failure."""
    url = f"{GITHUB_API}/repos/{repo_path}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code == 200:
        return resp.json()
    return None


def fetch_latest_release(repo_path: str) -> tuple[str | None, str | None]:
    """Return (tag_name, published_at) for the latest release, or (None, None)."""
    url = f"{GITHUB_API}/repos/{repo_path}/releases/latest"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("tag_name"), data.get("published_at")
    return None, None


def determine_license(repo: dict) -> list[str]:
    lic = repo.get("license") or {}
    spdx = lic.get("spdx_id") or lic.get("name")
    if not spdx or spdx == "NOASSERTION":
        return ["Unknown"]
    return [spdx]


def determine_owner_type(repo: dict) -> str:
    owner = repo.get("owner") or {}
    return owner.get("type", "")   # "User" or "Organization"


# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    with open(JSON_PATH) as f:
        tools = json.load(f)

    if not TOKEN:
        print("⚠️  GITHUB_TOKEN not set — unauthenticated requests are limited to 60/hr")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    updated = 0

    for tool in tqdm(tools, desc="Refreshing"):
        repo_path = extract_repo_path(tool.get("github_url", ""))
        if not repo_path:
            continue

        repo = fetch_repo(repo_path)
        time.sleep(RATE_SLEEP)

        if not repo:
            continue

        # Update fields from GitHub
        tool["stars"]       = repo.get("stargazers_count")
        tool["is_archived"] = repo.get("archived", False)
        tool["owner_type"]  = determine_owner_type(repo)
        tool["license"]     = determine_license(repo)
        tool["language"]    = list(set(filter(None, [repo.get("language")])))  # primary lang only
        tool["last_updated"] = now

        tag, released_at = fetch_latest_release(repo_path)
        time.sleep(RATE_SLEEP)
        if tag:
            tool["latest_release_tag"] = tag
            tool["latest_release_at"]  = released_at

        updated += 1

    print(f"\n✅ Refreshed {updated}/{len(tools)} tools")

    # ── Write JSON ──────────────────────────────────────────────────────────────
    with open(JSON_PATH, "w") as f:
        json.dump(tools, f, indent=2, default=str, ensure_ascii=False)
    print(f"📄 Wrote {JSON_PATH}")

    # ── Write CSV ───────────────────────────────────────────────────────────────
    df = pd.DataFrame(tools)
    df.to_csv(CSV_PATH, index=False)
    print(f"📄 Wrote {CSV_PATH}")

    # ── Write SQL ───────────────────────────────────────────────────────────────
    write_sql(tools)
    print(f"📄 Wrote {SQL_PATH}")


def write_sql(tools: list[dict]):
    """Write PostgreSQL INSERT statements."""
    cols = [
        "id", "name", "description", "github_url", "website_url", "stars",
        "last_updated", "tags", "platforms", "license", "origin_country",
        "language", "country_code", "is_archived", "owner_type", "avatar_url",
        "latest_release_tag", "latest_release_at", "pricing_type", "is_self_hosted",
    ]

    def pg_val(v):
        if v is None or v == "":
            return "NULL"
        if isinstance(v, bool):
            return "TRUE" if v else "FALSE"
        if isinstance(v, (int, float)):
            return str(v)
        if isinstance(v, list):
            inner = ", ".join(f"'{str(x).replace(chr(39), chr(39)*2)}'" for x in v)
            return f"ARRAY[{inner}]"
        s = str(v).replace("'", "''")
        return f"'{s}'"

    lines = [
        "-- OSS Tools Dataset",
        f"-- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"-- Records: {len(tools)}",
        "",
        "INSERT INTO tools (",
        "  " + ", ".join(cols),
        ") VALUES",
    ]

    rows = []
    for t in tools:
        vals = ", ".join(pg_val(t.get(c)) for c in cols)
        rows.append(f"  ({vals})")

    lines.append(",\n".join(rows) + ";")

    with open(SQL_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
