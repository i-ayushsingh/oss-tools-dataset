"""
scrape_sources.py
─────────────────
Scrapes all 7 OSS discovery sources, finds new GitHub repos,
fetches their metadata, and merges them into the dataset.

Run locally:  GITHUB_TOKEN=ghp_xxx python scripts/scrape_sources.py
In CI:        called automatically by the weekly workflow
"""

import json, os, re, time, uuid, logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
DATA_DIR  = Path(__file__).parent.parent / "data"
JSON_PATH = DATA_DIR / "tools.json"
CSV_PATH  = DATA_DIR / "tools.csv"
SQL_PATH  = DATA_DIR / "tools.sql"

GH_TOKEN   = os.environ.get("GITHUB_TOKEN", "")
GH_HEADERS = {"Authorization": f"Bearer {GH_TOKEN}", "Accept": "application/vnd.github+json"}
GH_API     = "https://api.github.com"
SLEEP      = 0.5   # seconds between GitHub API calls

GITHUB_RE = re.compile(r"github\.com/([A-Za-z0-9._-]+/[A-Za-z0-9._-]+)")

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "oss-tools-dataset/1.0 (+https://github.com/YOUR_USERNAME/oss-tools-dataset)"
})


# ── Utility ────────────────────────────────────────────────────────────────────
def normalise(url: str) -> Optional[str]:
    """Normalise any github.com link → https://github.com/owner/repo."""
    m = GITHUB_RE.search(url or "")
    if not m:
        return None
    parts = m.group(1).rstrip("/").split("/")
    if len(parts) < 2 or parts[1] in ("", "tree", "blob", "issues", "pulls", "releases", "wiki"):
        return None
    return f"https://github.com/{parts[0]}/{parts[1]}"


def extract_from_html(html: str) -> list[str]:
    """Pull all unique normalised github.com/owner/repo URLs out of raw HTML."""
    found = []
    for m in GITHUB_RE.finditer(html):
        n = normalise(m.group(0))
        if n and n not in found:
            found.append(n)
    return found


def get(url: str, **kw) -> Optional[requests.Response]:
    """GET with timeout + silent error handling."""
    try:
        r = SESSION.get(url, timeout=20, **kw)
        r.raise_for_status()
        return r
    except Exception as e:
        log.warning(f"GET {url} → {e}")
        return None


# ── Source scrapers ────────────────────────────────────────────────────────────

def scrape_openalternative() -> list[str]:
    """
    openalternative.co — Next.js site.
    Tries the JSON API first; falls back to paginated HTML scraping.
    """
    log.info("openalternative.co …")
    urls: list[str] = []

    # Attempt 1: public JSON API (may return 404 if they don't expose one)
    r = get("https://openalternative.co/api/tools")
    if r and r.headers.get("content-type", "").startswith("application/json"):
        try:
            data = r.json()
            items = data if isinstance(data, list) else (data.get("tools") or data.get("data") or [])
            for item in items:
                gh = item.get("repository") or item.get("github_url") or item.get("githubUrl") or ""
                n = normalise(gh)
                if n:
                    urls.append(n)
            log.info(f"  openalternative API → {len(urls)} urls")
            return list(set(urls))
        except Exception:
            pass

    # Attempt 2: paginated HTML
    page = 1
    while True:
        r = get(f"https://openalternative.co/?page={page}")
        if not r:
            break
        new = extract_from_html(r.text)
        if not new:
            break
        before = len(set(urls))
        urls.extend(new)
        if len(set(urls)) == before:   # no new unique URLs on this page
            break
        # check for next page link
        soup = BeautifulSoup(r.text, "html.parser")
        if not soup.find("a", attrs={"rel": "next"}):
            break
        page += 1
        time.sleep(1)

    result = list(set(urls))
    log.info(f"  openalternative HTML → {len(result)} urls")
    return result


def scrape_prism_break() -> list[str]:
    """prism-break.org — static Hugo site, easy HTML scrape."""
    log.info("prism-break.org …")
    r = get("https://prism-break.org/en/all/")
    if not r:
        return []
    urls = extract_from_html(r.text)
    log.info(f"  prism-break → {len(urls)} urls")
    return urls


def scrape_baserow() -> list[str]:
    """
    Baserow public gallery.
    Uses Baserow's public-view REST API via the slug token.
    """
    log.info("baserow gallery …")
    slug = "ufQOorUxMGxBLExuQyJsRzRkj1ie85liilCEELjorIs"
    urls: list[str] = []

    # Step 1: resolve the slug → table_id
    meta = get(f"https://api.baserow.io/api/database/views/slug/{slug}/")
    if not meta:
        # Fallback: scrape the gallery page HTML
        r = get(f"https://baserow.io/public/gallery/{slug}")
        if r:
            urls = extract_from_html(r.text)
        log.info(f"  baserow (HTML fallback) → {len(urls)} urls")
        return list(set(urls))

    view_data = meta.json()
    table_id = (
        view_data.get("table", {}).get("id")
        or view_data.get("table_id")
    )
    if not table_id:
        log.warning("  baserow: could not find table_id in view metadata")
        return []

    # Step 2: paginate through rows
    page = 1
    while True:
        r = get(
            f"https://api.baserow.io/api/database/rows/table/{table_id}/",
            params={"user_field_names": "true", "page": page, "size": 200},
            headers={"Authorization": f"Token {slug}"},
        )
        if not r:
            break
        data = r.json()
        results = data.get("results", [])
        if not results:
            break
        for row in results:
            # Try the most common field names for a GitHub URL
            for field in ["github_url", "GitHub", "Repository", "repo", "url", "GitHub URL", "link"]:
                val = str(row.get(field, ""))
                if "github.com" in val:
                    n = normalise(val)
                    if n:
                        urls.append(n)
                    break
        if not data.get("next"):
            break
        page += 1
        time.sleep(0.3)

    result = list(set(urls))
    log.info(f"  baserow API → {len(result)} urls")
    return result


def scrape_simple(url: str, label: str) -> list[str]:
    """
    Generic scraper for sites that render GitHub links in plain HTML.
    Works for: opensourcealternative.to, opensourcealternatives.to,
               btw.so/open-source-alternatives, indiegoodies.com
    """
    log.info(f"{label} …")
    urls: list[str] = []

    # Some of these sites are paginated; try a few pages
    for page in range(1, 10):
        sep = "&" if "?" in url else "?"
        r = get(f"{url}{sep}page={page}")
        if not r:
            break
        new = extract_from_html(r.text)
        if not new:
            break
        before = len(set(urls))
        urls.extend(new)
        if len(set(urls)) == before:
            break
        soup = BeautifulSoup(r.text, "html.parser")
        if not soup.find("a", attrs={"rel": "next"}) and page > 1:
            break
        time.sleep(0.8)

    result = list(set(urls))
    log.info(f"  {label} → {len(result)} urls")
    return result


def scrape_all() -> list[str]:
    """Run all scrapers and return one deduplicated list of GitHub URLs."""
    all_urls: list[str] = []
    all_urls += scrape_openalternative()
    all_urls += scrape_prism_break()
    all_urls += scrape_baserow()
    all_urls += scrape_simple("https://www.opensourcealternative.to",  "opensourcealternative.to")
    all_urls += scrape_simple("https://www.opensourcealternatives.to", "opensourcealternatives.to")
    all_urls += scrape_simple("https://www.btw.so/open-source-alternatives", "btw.so")
    all_urls += scrape_simple("https://indiegoodies.com/awesome-open-source-alternatives", "indiegoodies")

    unique = list(set(filter(None, all_urls)))
    log.info(f"Total unique GitHub URLs scraped: {len(unique)}")
    return unique


# ── GitHub metadata ────────────────────────────────────────────────────────────
def fetch_meta(github_url: str) -> Optional[dict]:
    """Fetch stars, license, language, release info etc. for one repo."""
    m = GITHUB_RE.search(github_url)
    if not m:
        return None
    repo_path = m.group(1).rstrip("/")

    r = SESSION.get(f"{GH_API}/repos/{repo_path}", headers=GH_HEADERS, timeout=15)
    time.sleep(SLEEP)
    if r.status_code != 200:
        log.warning(f"  GitHub {r.status_code} for {repo_path}")
        return None
    repo = r.json()

    # Latest release
    rel = SESSION.get(f"{GH_API}/repos/{repo_path}/releases/latest", headers=GH_HEADERS, timeout=15)
    time.sleep(SLEEP)
    release_tag = release_at = None
    if rel.status_code == 200:
        rd = rel.json()
        release_tag = rd.get("tag_name")
        release_at  = rd.get("published_at")

    lic = repo.get("license") or {}
    spdx = lic.get("spdx_id") or lic.get("name") or "Unknown"
    if spdx == "NOASSERTION":
        spdx = "Unknown"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    return {
        "id":                 str(uuid.uuid4()),
        "name":               repo.get("name", ""),
        "description":        (repo.get("description") or "")[:300],
        "github_url":         f"https://github.com/{repo_path}",
        "website_url":        repo.get("homepage") or None,
        "stars":              repo.get("stargazers_count"),
        "last_updated":       now,
        "tags":               None,
        "platforms":          None,
        "license":            [spdx],
        "origin_country":     None,
        "language":           [repo["language"]] if repo.get("language") else [],
        "country_code":       None,
        "is_archived":        repo.get("archived", False),
        "owner_type":         (repo.get("owner") or {}).get("type", ""),
        "avatar_url":         None,
        "latest_release_tag": release_tag,
        "latest_release_at":  release_at,
        "pricing_type":       "Free",   # default; enrich manually if needed
        "is_self_hosted":     None,
    }


# ── Merge ──────────────────────────────────────────────────────────────────────
def merge(existing: list[dict], scraped_urls: list[str]) -> tuple[list[dict], int]:
    """Add genuinely new tools to the existing list."""
    known = {normalise(t.get("github_url", "")) for t in existing if t.get("github_url")}
    added = 0

    for url in scraped_urls:
        norm = normalise(url)
        if not norm or norm in known:
            continue
        log.info(f"  + new tool: {norm}")
        meta = fetch_meta(norm)
        if meta:
            existing.append(meta)
            known.add(norm)
            added += 1

    return existing, added


# ── Write all 3 formats ────────────────────────────────────────────────────────
def write_all(tools: list[dict]):
    import pandas as pd

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(tools, f, indent=2, default=str, ensure_ascii=False)

    pd.DataFrame(tools).to_csv(CSV_PATH, index=False)

    cols = list(tools[0].keys()) if tools else []

    def pg(v):
        if v is None or v == "": return "NULL"
        if isinstance(v, bool):  return "TRUE" if v else "FALSE"
        if isinstance(v, (int, float)): return str(v)
        if isinstance(v, list):
            inner = ", ".join(f"'{str(x).replace(chr(39), chr(39)*2)}'" for x in v)
            return f"ARRAY[{inner}]"
        return f"'{str(v).replace(chr(39), chr(39)*2)}'"

    rows = ["  (" + ", ".join(pg(t.get(c)) for c in cols) + ")" for t in tools]
    sql  = (
        f"-- OSS Tools Dataset | generated {datetime.now(timezone.utc).date()} | {len(tools)} records\n\n"
        f"INSERT INTO tools (\n  {', '.join(cols)}\n) VALUES\n"
        + ",\n".join(rows) + ";"
    )
    SQL_PATH.write_text(sql, encoding="utf-8")

    log.info(f"Wrote {len(tools)} records → CSV, JSON, SQL")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    if not GH_TOKEN:
        log.warning("GITHUB_TOKEN not set — rate limit is 60 req/hr (may fail on large datasets)")

    # Load existing
    existing = json.loads(JSON_PATH.read_text()) if JSON_PATH.exists() else []
    log.info(f"Existing tools: {len(existing)}")

    # Scrape sources
    scraped_urls = scrape_all()

    # Add new tools
    merged, added = merge(existing, scraped_urls)
    log.info(f"New tools added: {added}  |  Total: {len(merged)}")

    # Write
    write_all(merged)
    log.info("Done.")


if __name__ == "__main__":
    main()
