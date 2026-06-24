# Changelog

All notable changes to this dataset are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions align with dataset snapshot dates.

---

## [1.0.0] — 2026-04-01

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

---

## [Unreleased]

### Planned
- Fill `tags` column with a standardized taxonomy
- Fill `platforms` column (Web / CLI / Mobile / Desktop)
- Monthly automated star/release refresh via GitHub Actions
- Deduplicate tools that appear across multiple sources
