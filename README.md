# CBS StatLine Hackathon Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Kilo skill for data journalism hackathons using CBS StatLine open data, focused on housing (woningen) and energy transition (energietransitie) in the Netherlands.

## Overview

This skill transforms an AI agent into a knowledgeable CBS StatLine research partner that can:

- Discover relevant tables from the CBS catalog
- Understand table structure and metadata
- Download and join data from multiple tables
- Perform analysis and help frame findings as data journalism story angles

The skill focuses on the intersection of **housing** and **energy transition** in the Netherlands, with curated tables covering:

- Dutch housing stock and characteristics
- Energy labels and efficiency
- Heat pumps and solar panels
- Gas-free homes
- Building permits
- Housing prices
- Neighbourhood-level (wijk/buurt) statistics

## Installation

### For Kilo Users

Download the `cbs-skill.zip` package and install it using:

```bash
kilo skill install cbs-skill.zip
```

Or place the skill directory in your Kilo skills folder:

```
~/.kilo/skills/cbs-statline-hackathon/
```

### Dependencies

The Python helper module requires:

```bash
pip install requests pandas
```

## Usage

The skill is designed for mixed audiences (journalists + coders) and generates complete, runnable Python code.

### Example Workflow

```python
from cbs_client import CBSClient

client = CBSClient()

# Search for tables
results = client.search_tables("zonnestroom woningen")

# Inspect a table
meta = client.get_metadata("84518NED")
meta.show()

# Download data with filters
df = client.get_data("84518NED", filters={"Perioden": "2023JJ00"})

# Add human-readable labels
df = client.add_labels(df, "84518NED")
```

### With Context Manager (Recommended)

```python
with CBSClient() as client:
    df = client.get_data("84518NED")
```

## Skill Structure

```
cbs-statline-hackathon/
├── SKILL.md              # Main skill definition with workflow
├── cbs_client.py         # Python helper module for CBS OData v4 API
├── table-registry.md     # Curated list of ~35 vetted tables with join keys
├── analysis-recipes.md   # Story templates for data journalism
├── odata-v4-guide.md     # OData v4 API patterns and filtering
├── geo-pdok.md           # Geographic visualization with PDOK
└── evals.json            # Evaluation prompts for skill testing
```

## Features

### cbs_client.py Module

The included Python module handles:

- **Catalog search** — Keyword search across all CBS tables
- **Metadata retrieval** — Human-readable display of table structure
- **Data download** — Automatic pagination and filtering
- **Code-to-label resolution** — Convert CBS codes to readable labels
- **Period parsing** — Convert CBS period codes to Python dates
- **Region code normalization** — Strip whitespace and identify region levels

### Input Validation

- Table IDs validated against pattern `[0-9]{5}[A-Z]{3}` (e.g., "84518NED")
- Period codes validated for quarter (1-4) and month (1-12) ranges
- Request timeout protection (30s default)

### Resource Management

- Context manager support (`with CBSClient() as client:`)
- Session cleanup on exit
- Instance-level metadata caching

## CBS Data Knowledge

### Period Codes (Perioden)

- `2023JJ00` — Year 2023
- `2023KW01` — Q1 2023
- `2023MM06` — June 2023
- `2023X000` — Half year (rare)

### Region Codes (RegioS)

- `NL00`/`NL01` — Netherlands total
- `LD##` — Landsdeel
- `PV##` — Provincie
- `CR##` — COROP-gebied
- `GM####` — Gemeente
- `WK######` — Wijk
- `BU########` — Buurt

**Note:** Region codes often have trailing spaces — always `.strip()` them.

### Data Status

- **Definitief** — Final figures
- **Voorlopig** (*) — Provisional, may change
- **Nader voorlopig** (**) — Revised provisional

## Deprecation Warnings (2025–2026)

Several key housing tables are being replaced due to methodology changes:

- `82900NED` (Voorraad woningen eigendom) → new tables from 2026
- `84948NED` (Hoofdverwarmingsinstallaties) → replaced by ASD-tables for 2022+

Always check the `status` field in the table registry.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

- **Issue Tracker:** https://github.com/linksmith/cbs-skill/issues
- **Pull Requests:** https://github.com/linksmith/cbs-skill/pulls

## Resources

- [CBS StatLine](https://opendata.cbs.nl/)
- [CBS OData v4 API Documentation](https://datasets.cbs.nl/odata/v1/)
- [PDOK Geodata](https://www.pdok.nl/)
