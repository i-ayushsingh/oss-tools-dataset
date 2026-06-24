# Contributing to OSS Tools Dataset

Thank you for helping make this dataset better! There are several ways to contribute.

---

## 🛠️ Ways to Contribute

### 1. Add a Missing Tool

Open an issue using the **"Add a Tool"** template. Include the GitHub URL and we'll verify and add it.

Or submit a PR directly — add a row to `data/tools.csv` and `data/tools.json` following the schema in the README. Run the validator before opening the PR:

```bash
python scripts/validate_schema.py
```

### 2. Fix Incorrect Data

Open a **"Fix Data"** issue, or submit a PR with the corrected values. Please include a link to the source that confirms the correct value (e.g. the GitHub repo page).

### 3. Fill in `tags` or `platforms`

These two columns are currently null and are the biggest gap in the dataset. If you want to help define a tagging taxonomy and fill them in — please open an issue first to discuss the schema so we can coordinate.

### 4. Improve the Scripts

The `scripts/` folder contains tools for refreshing GitHub metadata and validating the schema. Bug fixes and improvements are very welcome.

---

## 📋 PR Checklist

Before submitting a pull request:

- [ ] Run `python scripts/validate_schema.py` — all rows must pass
- [ ] Ensure new tools have a valid `github_url`
- [ ] UUIDs for new rows must be valid UUID v4 (use `python -c "import uuid; print(uuid.uuid4())"`)
- [ ] JSON array remains valid (test with `python -c "import json; json.load(open('data/tools.json'))"`)
- [ ] CSV column order matches the existing schema
- [ ] No trailing whitespace or BOM in CSV

---

## 🧭 Ground Rules

- Be kind — this is a community project
- One tool per PR keeps review easy
- Don't submit tools that are not genuinely open source
- Don't submit tools that are abandoned (no commits in 3+ years) unless they are historically significant

---

## 🚀 Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/oss-tools-dataset
cd oss-tools-dataset
pip install -r scripts/requirements.txt
```

---

Questions? Open a [Discussion](../../discussions) — not an issue — for general topics.
