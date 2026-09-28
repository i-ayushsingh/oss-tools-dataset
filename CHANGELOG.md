# Changelog

All notable changes to this dataset are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions align with dataset snapshot dates.

---

## [1.1.0] — 2026-09-29

### Added
- Net addition of major open-source tools including Redis, Ollama, FreeCodeCamp, Firecrawl, PostHog, OpenHands, MarkItDown, FFmpeg, AppFlowy, and Unleash.
- Added full `CREATE TABLE IF NOT EXISTS tools (...)` PostgreSQL DDL schema definition at the top of `data/tools.sql`.
- Added tri-file parity validation in `scripts/validate_schema.py` ensuring CSV, JSON, and SQL records match exactly.
- Added repository and domain blacklisting in `scripts/scrape_sources.py` to prevent platform footer links from hijacking tool URLs.
- Added case-insensitive URL deduplication check in CI workflows.

### Changed
- Streamlined schema from 20 columns to 18 high-value columns by removing unused empty fields (`tags` and `platforms`).
- Hardened GitHub Actions workflows (`weekly_update.yml`, `refresh_data.yml`, `validate_data.yml`) against token expiration and phantom commits.
- Updated README metrics to reflect 1,222 verified tools with 19.3M+ combined GitHub stars.

### Fixed
- Fixed 11 major tools whose repository links were incorrectly pointing to `btw-so/btw` (Node-RED, FullCalendar, Dolibarr, Athens, Beehive, Winter CMS, DeckDeckGo, PrivacyIDEA, Umbraco, LavaLite, Flogo).
- Deduplicated multiple entries across the dataset (Cal.com, Fonoster, LibreOffice, Fathom, Unleash, PostHog, AppFlowy).
- Removed non-open-source proprietary entry (Plivo).
- Fixed all placeholder usernames (`YOUR_USERNAME`) across documentation and scripts.

---

## [1.0.0] — 2026-06-24

### Added
- Initial public release
- 1,208 open-source tools scraped from 7 OSS discovery platforms
- GitHub metadata: stars, languages, license, owner type, release info
- Three formats: CSV, JSON, PostgreSQL SQL dump
- Schema documentation in README
- CC0 license (public domain)

### Data sources
- OpenAlternative
- Prism Break
- Baserow OSS Gallery
- OpenSourceAlternative.to
- OpenSourceAlternatives.to
- btw.so Open Source Alternatives
- IndieGoodies Awesome OSS
