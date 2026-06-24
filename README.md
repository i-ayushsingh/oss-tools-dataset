# Open Source Tools Dataset

[![License: CC0](https://img.shields.io/badge/License-CC0%201.0-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)
[![Tools](https://img.shields.io/badge/tools-1%2C208-blue)](data/tools.csv)
[![Last Refresh](https://img.shields.io/badge/last%20refresh-April%202026-green)](CHANGELOG.md)
[![Weekly Update](https://github.com/i-ayushsingh/oss-tools-dataset/actions/workflows/weekly_update.yml/badge.svg)](https://github.com/i-ayushsingh/oss-tools-dataset/actions/workflows/weekly_update.yml)

A curated, machine-readable dataset of **1,208 open-source tools** enriched with live GitHub metadata — scraped from 7 popular OSS discovery platforms.

Originally collected for a personal project; now released as open data for anyone building directories, analytics, recommendation engines, or research on the OSS ecosystem.

---

## Quick Start

Download the data in your preferred format:

```bash
# Clone the full repo
git clone https://github.com/i-ayushsingh/oss-tools-dataset.git

# Or download just the CSV (no git needed)
curl -O https://raw.githubusercontent.com/i-ayushsingh/oss-tools-dataset/main/data/tools.csv
```

Then load it:

```python
import pandas as pd
df = pd.read_csv("data/tools.csv")
print(df.shape)           # (1208, 20)
print(df.columns.tolist())
```

---

## Dataset at a Glance

| Metric | Value |
|---|---|
| Total tools | **1,208** |
| Active (not archived) | **1,167** |
| Archived | **41** |
| Self-hostable | **842** |
| Combined GitHub stars | **15,591,718** |
| Average stars per tool | **13,080** |
| Tools with a website URL | **1,180** |
| Tools with a tracked release | **1,081** |

**Pricing breakdown**

| Type | Count |
|---|---|
| Free | 629 |
| Freemium | 446 |
| Paid | 133 |

**Top origin countries** (excluding tools marked "Global")

United States · Germany · France · United Kingdom · India · Singapore · Canada · Netherlands · Sweden · Switzerland

**Top programming languages** (from GitHub repo metadata)

Shell · JavaScript · CSS · HTML · Dockerfile · TypeScript · Python · Makefile · SCSS · Go

**Top licenses**

MIT · Other · AGPL-3.0 · Apache-2.0 · GPL-3.0 · GPL-2.0 · MPL-2.0 · Proprietary · BSD-3-Clause

---

## Repository Structure

```
oss-tools-dataset/
├── README.md                        ← You are here
├── LICENSE                          ← CC0 1.0 Universal (public domain)
├── CHANGELOG.md                     ← Version history
├── CONTRIBUTING.md                  ← How to contribute
├── data/
│   ├── tools.csv                    ← Comma-separated, UTF-8 (607 KB)
│   ├── tools.json                   ← JSON array of objects (1.1 MB)
│   └── tools.sql                    ← PostgreSQL INSERT statements (658 KB)
├── scripts/
│   ├── scrape_sources.py            ← Scrapes 7 OSS platforms for new tools
│   ├── refresh_github_meta.py       ← Refreshes stars/releases/license via GitHub API
│   ├── validate_schema.py           ← Schema validation (used in CI)
│   └── requirements.txt             ← Python dependencies
└── .github/
    ├── workflows/
    │   ├── weekly_update.yml        ← Scrape + refresh every Monday 03:00 UTC
    │   ├── refresh_data.yml         ← Metadata-only refresh every Monday 02:00 UTC
    │   └── validate_data.yml        ← Schema validation on every PR and push
    └── ISSUE_TEMPLATE/
        ├── add_tool.yml             ← Template for submitting a new tool
        └── fix_data.yml             ← Template for reporting a data error
```

All three data files contain **identical records** — use whichever format fits your stack.

---

## Schema

Every record has 20 fields:

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Unique identifier for the tool |
| `name` | string | Tool name |
| `description` | string | One-line description |
| `github_url` | string \| null | GitHub repository URL |
| `website_url` | string \| null | Official website URL |
| `stars` | integer \| null | GitHub star count (at last refresh) |
| `last_updated` | timestamp | When this record was last refreshed |
| `tags` | string \| null | Comma-separated tags *(reserved — currently null)* |
| `platforms` | string \| null | Target platforms *(reserved — currently null)* |
| `license` | string[] \| null | SPDX license identifiers e.g. `["MIT"]`, `["AGPL-3.0"]` |
| `origin_country` | string \| null | Country of origin, or `"Global"` |
| `language` | string[] \| null | Primary programming languages from GitHub |
| `country_code` | string \| null | ISO 3166-1 alpha-2 code (`"US"`, `"DE"`, `"UN"` for Global) |
| `is_archived` | boolean | Whether the GitHub repo is archived |
| `owner_type` | string \| null | `"Organization"` or `"User"` |
| `avatar_url` | string \| null | Logo URL (via logo.dev) |
| `latest_release_tag` | string \| null | Most recent GitHub release tag |
| `latest_release_at` | timestamp \| null | Date of most recent release |
| `pricing_type` | string | `"Free"`, `"Freemium"`, or `"Paid"` |
| `is_self_hosted` | boolean \| null | Whether the tool can be self-hosted |

> `tags` and `platforms` are intentionally null — they are kept in the schema to signal planned work. Contributions to fill them in are very welcome.

---

## Usage Examples

### Python (pandas)

```python
import pandas as pd

df = pd.read_csv("data/tools.csv")

# Top 10 most starred free tools
top_free = (
    df[df["pricing_type"] == "Free"]
    .sort_values("stars", ascending=False)
    .head(10)[["name", "stars", "website_url"]]
)
print(top_free)
```

### Python (JSON)

```python
import json

with open("data/tools.json") as f:
    tools = json.load(f)

# All MIT-licensed, self-hosted tools
mit_selfhosted = [
    t for t in tools
    if "MIT" in (t.get("license") or [])
    and t.get("is_self_hosted") is True
]
print(f"{len(mit_selfhosted)} MIT-licensed self-hosted tools")
```

### PostgreSQL

```sql
-- Import the full dataset
\i data/tools.sql

-- TypeScript tools with 10k+ stars
SELECT name, stars, website_url
FROM tools
WHERE 'TypeScript' = ANY(language)
  AND stars >= 10000
ORDER BY stars DESC;

-- Count tools by license
SELECT license, COUNT(*) AS total
FROM tools, unnest(license) AS license
GROUP BY license
ORDER BY total DESC;
```

### JavaScript / Node.js

```js
const tools = require("./data/tools.json");

// Free, self-hostable tools sorted by stars
const results = tools
  .filter(t => t.is_self_hosted && t.pricing_type === "Free")
  .sort((a, b) => (b.stars || 0) - (a.stars || 0));

console.log(`${results.length} free, self-hostable tools`);
console.log(results.slice(0, 5).map(t => t.name));
```

---

## Data Sources

Scraped from 7 OSS discovery platforms:

| # | Platform | Focus |
|---|---|---|
| 1 | [OpenAlternative](https://openalternative.co/) | Open-source alternatives to popular SaaS |
| 2 | [Prism Break](https://prism-break.org/en/) | Privacy-respecting tools |
| 3 | [Baserow OSS Gallery](https://baserow.io/public/gallery/ufQOorUxMGxBLExuQyJsRzRkj1ie85liilCEELjorIs) | Curated OSS tools |
| 4 | [OpenSourceAlternative.to](https://www.opensourcealternative.to/) | OSS alternatives |
| 5 | [OpenSourceAlternatives.to](https://www.opensourcealternatives.to/) | OSS alternatives |
| 6 | [btw.so Open Source Alternatives](https://www.btw.so/open-source-alternatives) | OSS alternatives directory |
| 7 | [IndieGoodies Awesome OSS](https://indiegoodies.com/awesome-open-source-alternatives) | Indie OSS tools |

GitHub metadata (stars, languages, license, release info, owner type) was fetched separately using the GitHub API.

---

## Automation

Three GitHub Actions workflows keep the dataset fresh automatically:

| Workflow | Schedule | What it does |
|---|---|---|
| `weekly_update.yml` | Every Monday 03:00 UTC | Scrapes all 7 sources for new tools, refreshes GitHub metadata, commits changes |
| `refresh_data.yml` | Every Monday 02:00 UTC | Refreshes GitHub metadata (stars, releases, license) for existing tools only |
| `validate_data.yml` | On every PR and push to `main` | Validates schema, checks for duplicate IDs and GitHub URLs |

Both update workflows require a `GH_PAT` repository secret (a GitHub Personal Access Token with `repo` scope) to authenticate API calls and push commits back to the repo.

To set it up: **Settings → Secrets and variables → Actions → New repository secret** — name it `GH_PAT`.

You can also trigger any workflow manually from the **Actions** tab using the "Run workflow" button.

---

## Scripts

| Script | Description |
|---|---|
| `scripts/scrape_sources.py` | Scrapes all 7 discovery platforms and appends new tools to the dataset |
| `scripts/refresh_github_meta.py` | Calls the GitHub API to update stars, language, license, and release fields |
| `scripts/validate_schema.py` | Validates `data/tools.csv` against the expected schema; exits 1 on errors |

To run locally:

```bash
pip install -r scripts/requirements.txt

# Refresh GitHub metadata (requires GITHUB_TOKEN env var)
GITHUB_TOKEN=your_pat python scripts/refresh_github_meta.py

# Validate the dataset
python scripts/validate_schema.py
```

---

## Data Quality Notes

- **Stars and release dates** reflect the time the data was last refreshed and will drift between weekly runs.
- A small number of entries have null stars or languages where GitHub metadata was unavailable.
- `origin_country = "Global"` means the project has no clear single-country origin.
- `country_code = "UN"` is used as a proxy for "Global" (no ISO code for stateless projects).
- `license = ["Other"]` or `["Proprietary"]` appears for repos with non-standard or missing SPDX identifiers.
- `tags` and `platforms` are intentionally null — planned for a future release.

---

## Roadmap

- [ ] Fill `tags` with a standardized taxonomy
- [ ] Fill `platforms` column (Web / CLI / Mobile / Desktop)
- [ ] Deduplicate tools that appear across multiple sources
- [ ] Add `category` field (e.g. DevOps, Security, Productivity)
- [ ] Expand to additional discovery sources

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

Quick ways to help:

- **Add a missing tool** — open a PR with new rows following the schema
- **Fill in `tags` or `platforms`** — a standardized taxonomy would make filtering much more useful
- **Fix a data error** — wrong GitHub URLs, misattributed metadata, etc.
- **Add a discovery source** — extend `scrape_sources.py` to cover more platforms

Use the issue templates to report problems or propose additions.

---

## License

Released under [CC0 1.0 Universal](LICENSE) — public domain. Copy, modify, distribute, and use for any purpose, commercial or non-commercial, without asking permission.

---

## Acknowledgements

Thanks to the teams behind OpenAlternative, Prism Break, Baserow, and the other platforms that make OSS discovery accessible. All tool metadata ultimately originates from GitHub and the respective project maintainers.

---

*Last refreshed: April 2026 · 1,208 tools · [Open an issue](../../issues) if something looks wrong*
