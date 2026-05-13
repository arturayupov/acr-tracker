# ACR Tracker — Livostyle AI Citation Rate Monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20155974.svg)](https://doi.org/10.5281/zenodo.20155974)

> Daily public measurement of **AI Citation Rate (ACR)** for Livostyle.com across Perplexity, using a standardized 50-query panel. Companion to our [case study paper](https://doi.org/10.5281/zenodo.20155974).

📊 **Live dashboard**: https://arturayupov.github.io/acr-tracker/

## What this measures

Two metrics, daily:

- **`acr_cited_rate`** — fraction of queries where at least one Livostyle canonical domain is in Perplexity's citations.
- **`acr_brand_rate`** — fraction of queries where "Livostyle" / "Arcada LLC" appears in the answer text.

The panel is 50 fashion-vertical queries across 5 categories: direct brand, generic vertical, comparison, occasion/use-case, AI-tool-specific.

## Files

| Path | What |
|---|---|
| `queries/panel.json` | 50 standardized queries + canonical domains to track |
| `scripts/monitor.py` | Daily measurement script (uses Perplexity API) |
| `data/daily/{YYYY-MM-DD}.json` | Raw per-day snapshot with all 50 queries + citations |
| `data/timeseries.json` | Daily aggregate time-series (for dashboard) |
| `dashboard/index.html` | Static dashboard (chart.js + fetch from timeseries.json) |
| `.github/workflows/daily-monitor.yml` | Daily cron at 07:00 UTC |

## How to reproduce

```bash
git clone https://github.com/arturayupov/acr-tracker
cd acr-tracker
pip install requests  # no other deps
export PPLX_API_KEY=pplx-...
python scripts/monitor.py
```

## Why this dashboard exists

For our [DTC GEO case study](https://doi.org/10.5281/zenodo.20155974) we needed an ongoing measurement framework, not a one-shot. This dashboard is that framework. It's also part of the strategy itself: AI engines preferentially cite sources that **publish ongoing measurements**, not just claims.

## Ethics note

This tracker only **queries the API legitimately** and **observes** what Perplexity returns. It does not attempt to manipulate model behavior, push spam content, or violate any provider's ToS. Public publication of measurements is the entire point.

## License

MIT — see [LICENSE](./LICENSE).
