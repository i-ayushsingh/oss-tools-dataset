# 🛠️ Open Source Tools Dataset

A curated, machine-readable dataset of **1,208 open-source tools** — enriched with GitHub metadata — scraped from 7 popular OSS discovery platforms.

Originally collected for a personal project; now released as open data for anyone building directories, analytics, recommendation engines, or research on the OSS ecosystem.

---

## 📊 Dataset at a Glance

| Metric | Value |
|---|---|
| Total tools | **1,208** |
| Active (not archived) | **1,167** |
| Archived | **41** |
| Self-hostable | **842** |
| Combined GitHub ⭐ | **15,591,718** |
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

## 🌐 Sources

Data was scraped from these platforms:

| # | Platform |
|---|---|
| 1 | [OpenAlternative](https://openalternative.co/) |
| 2 | [Prism Break](https://prism-break.org/en/) |
| 3 | [Baserow OSS Gallery](https://baserow.io/public/gallery/ufQOorUxMGxBLExuQyJsRzRkj1ie85liilCEELjorIs) |
| 4 | [OpenSourceAlternative.to](https://www.opensourcealternative.to/) |
| 5 | [OpenSourceAlternatives.to](https://www.opensourcealternatives.to/) |
| 6 | [btw.so Open Source Alternatives](https://www.btw.so/open-source-alternatives) |
| 7 | [IndieGoodies Awesome OSS](https://indiegoodies.com/awesome-open-source-alternatives) |

GitHub metadata (stars, languages, license, release info, owner type, etc.) was fetched separately via the GitHub API.

---

## 📁 Repository Structure

```
oss-tools-dataset/
├── README.md          ← You are here
├── LICENSE            ← CC0 1.0 Universal (public domain)
└── data/
    ├── tools.csv      ← Comma-separated, UTF-8
    ├── tools.json     ← JSON array of objects
    └── tools.sql      ← PostgreSQL INSERT statements
```

All three files contain **identical data** — use whichever format suits your stack.

---

## 🗂️ Schema

Every record has the following 20 fields:

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Unique identifier for the tool |
| `name` | string | Tool name |
| `description` | string | One-line description |
| `github_url` | string \| null | GitHub repository URL |
| `website_url` | string \| null | Official website URL |
| `stars` | integer \| null | GitHub star count (at time of collection) |
| `last_updated` | timestamp | When this record was last refreshed |
| `tags` | string \| null | Comma-separated tags *(reserved — currently null)* |
| `platforms` | string \| null | Target platforms *(reserved — currently null)* |
| `license` | string[] \| null | SPDX license identifiers (e.g. `["MIT"]`, `["AGPL-3.0"]`) |
| `origin_country` | string \| null | Country where the project originates, or `"Global"` |
| `language` | string[] \| null | Primary programming languages from GitHub |
| `country_code` | string \| null | ISO 3166-1 alpha-2 country code (e.g. `"US"`, `"DE"`, `"UN"` for Global) |
| `is_archived` | boolean | Whether the GitHub repo is archived |
| `owner_type` | string \| null | `"Organization"` or `"User"` |
| `avatar_url` | string \| null | Logo URL (via logo.dev) |
| `latest_release_tag` | string \| null | Most recent GitHub release tag |
| `latest_release_at` | timestamp \| null | Date of most recent release |
| `pricing_type` | string | `"Free"`, `"Freemium"`, or `"Paid"` |
| `is_self_hosted` | boolean \| null | Whether the tool can be self-hosted |

> **Note on `tags` and `platforms`:** These fields were planned but not populated. They are kept in the schema as explicit null to signal future work — contributions welcome!

---

## 💡 Usage Examples

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
-- Import
\i data/tools.sql

-- Query: TypeScript tools with 10k+ stars
SELECT name, stars, website_url
FROM tools
WHERE 'TypeScript' = ANY(language)
  AND stars >= 10000
ORDER BY stars DESC;
```

### JavaScript / Node.js

```js
const tools = require("./data/tools.json");

const selfHostedFree = tools.filter(
  (t) => t.is_self_hosted && t.pricing_type === "Free"
);
console.log(`${selfHostedFree.length} free, self-hostable tools`);
```

---

## ⚠️ Data Quality Notes

- **Stars and release dates** reflect the time the data was collected (April 2026) and will drift over time.
- A small number of entries have `null` stars or languages where GitHub metadata was unavailable.
- `origin_country = "Global"` means the project has no clear single-country origin, not that it's missing.
- `country_code = "UN"` is used as a proxy for "Global" (no ISO code for stateless projects).
- `license = ["Other"]` or `["Proprietary"]` appears for repos with non-standard or missing SPDX identifiers.
- The `tags` and `platforms` fields are intentionally null — see above.

---

## 🤝 Contributing

Contributions are welcome! Ideas:

- **Add missing tools** — open a PR with new rows following the schema above
- **Fill in `tags`** — a standardized tagging taxonomy would make filtering much more useful
- **Fill in `platforms`** — e.g. `Web`, `macOS`, `Linux`, `Android`, `iOS`, `CLI`
- **Refresh stale metadata** — stars and release info go stale; a refresh script would help
- **Fix data errors** — wrong GitHub URLs, misattributed metadata, etc.

Please open an issue before large PRs so we can coordinate.

---

## 📄 License

This dataset is released under the **Creative Commons Zero v1.0 Universal (CC0)** license — it is dedicated to the public domain. You can copy, modify, distribute, and use the data for any purpose, commercial or non-commercial, without asking permission.

See [`LICENSE`](./LICENSE) for the full text.

---

## 🙏 Acknowledgements

Thanks to the teams behind OpenAlternative, Prism Break, Baserow, and the other platforms that make OSS discovery easier. All tool metadata ultimately originates from GitHub and the respective project maintainers.

---

*Last refreshed: April 2026 · 1,208 tools · [Open an issue](../../issues) if something looks wrong*
