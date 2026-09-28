# Contributing to OSS Tools Dataset

Thank you for helping make this dataset better! There are several ways to contribute.

---

## 📌 Inclusion Criteria

To maintain dataset quality, consistency, and reliability for researchers and developers, all tools in this dataset must meet the following criteria:

1. **Minimum Stars**: The repository must have at least **100+ GitHub stars** to demonstrate community traction.
2. **Active Maintenance**: The repository must be actively maintained, with commits or releases within the past **12 months** (not archived or abandoned).
3. **Legitimate Open-Source License**: The project must have a recognized, OSI-approved open-source license with an SPDX identifier (e.g. `MIT`, `Apache-2.0`, `GPL-3.0`, `AGPL-3.0`, `MPL-2.0`, `BSD-3-Clause`). Proprietary or source-available code without an open-source license will not be accepted.
4. **No Single-Tool Self-Promotion PRs**: Please do not open a pull request solely to add your own personal app or a single project. 
   - If you want to suggest an individual tool (including your own), please open an issue using the **[➕ Add a Tool](../../issues/new?template=add_tool.yml)** template.
   - Direct Pull Requests for tool additions are accepted **only for curated batches of 20+ tools** at a time to prevent link farming and keep review manageable.

---

## 🛠️ Ways to Contribute

### 1. Suggest a Tool (Issues)
Open an issue using the **[➕ Add a Tool](../../issues/new?template=add_tool.yml)** template. If it meets the inclusion criteria (100+ stars, active, open-source), we will verify and ingest it into the dataset.

### 2. Batch Tool Contributions (PRs)
If you have a curated batch of **20+ tools** that meet the inclusion criteria, you can submit a PR. Please ensure new entries adhere to the schema and include valid UUIDs for all rows.

### 3. Fix Incorrect Data
Found an outdated website URL, wrong license, broken GitHub repository, or typo? Open a **[🐛 Fix Data Error](../../issues/new?template=fix_data.yml)** issue or open a PR with the corrected values.

### 4. Fill in `tags` or `platforms`
`tags` and `platforms` are currently null across the dataset. If you would like to help define a standardized tagging taxonomy or fill in platform targets (Web, CLI, Desktop, Mobile, Self-Hosted), please open an issue to coordinate.

### 5. Improve the Automation & Scripts
The `scripts/` directory contains tools for scraping sources, refreshing GitHub metadata, and schema validation. Improvements, bug fixes, and new scraper sources are very welcome.

---

## 📋 PR Checklist

Before submitting a pull request:

- [ ] Run `python scripts/validate_schema.py` — all rows must pass
- [ ] If submitting data additions, ensure you are adding **20+ tools** meeting the inclusion criteria (100+ stars, active, OSS license)
- [ ] Ensure all records have a valid `github_url`
- [ ] UUIDs for new rows must be valid UUID v4 (use `python -c "import uuid; print(uuid.uuid4())"`)
- [ ] Keep `data/tools.csv`, `data/tools.json`, and `data/tools.sql` in parity
- [ ] CSV and JSON must parse cleanly without syntax errors
- [ ] No trailing whitespace or BOM in CSV

---

## 🚀 Development Setup

```bash
git clone https://github.com/i-ayushsingh/oss-tools-dataset.git
cd oss-tools-dataset
pip install -r scripts/requirements.txt
```

Run schema validation:
```bash
python scripts/validate_schema.py
```

---

Questions? Open an issue or start a discussion!
