---
name: cbs-statline-skill
description: "Skill for exploring and analysing CBS StatLine open data from the Netherlands. Use this skill whenever the user wants to find, evaluate, download, analyse, or visualise CBS open data. Also trigger when the user mentions StatLine, CBS, OData, or Dutch statistics. Includes a curated registry of housing and energy transition tables, but works with any CBS table. Generates complete, runnable Python code with explanations."
---
repo: https://github.com/linksmith/cbs-statline-skill
---

## Purpose

Turn an AI agent into a knowledgeable CBS StatLine research partner that can
discover relevant tables, understand their structure, download and join data,
perform analysis, and help frame findings as story angles or research
insights — all focused on the intersection of **housing** and **energy
transition** in the Netherlands.

## Audience

Mixed: researchers, analysts, journalists, and developers who may not know
CBS data. Every code block you generate must be **complete and runnable** with
clear comments. Never assume the user knows CBS conventions (period codes,
region codes, metadata structure). Explain as you go.

## Quick-reference: key resources

Before starting any task, read the relevant reference file:

| Need | File | When to read |
|---|---|---|
| Which tables exist for housing × energy | `table-registry.md` | **Always read first** — this is the curated list of ~35 vetted tables with join keys |
| Story angle templates and analysis patterns | `analysis-recipes.md` | When the user wants ideas, or when you need to suggest an analysis path |
| OData v4 API patterns, pagination, filtering | `odata-v4-guide.md` | When writing any data retrieval code |
| Geographic visualization with PDOK | `geo-pdok.md` | When the user wants maps or regional analysis |

## Workflow

Follow this sequence for any CBS data task:

### Step 1: Understand the question

Restate the user's question as a clear research hypothesis. Examples:
- "Is the energy transition happening faster in wealthy neighbourhoods?"
- "Which municipalities are falling behind on gas-free housing targets?"
- "Do homes with solar panels also have better energy labels?"

### Step 2: Identify tables

First check `table-registry.md` — it contains curated tables for housing,
energy, and starter tables for demographics, labour, health, education,
crime, agriculture, transport, and economy.

If the user's question falls outside the registry, **search the full CBS
catalog** using the helper module:

```python
from cbs_client import CBSClient
client = CBSClient()
results = client.search_tables("your search terms")
print(results)  # shows table ID, title, and last modified date
```

The CBS catalog contains 4,000+ tables. Use Dutch keywords for best results
(e.g. "werkloosheid" not "unemployment", "onderwijs" not "education").

Select 1–3 tables that can answer the question. Prioritise tables that:
- Share a **join key** (RegioS codes at the same geographic level)
- Have overlapping **Perioden** (time periods)
- Are **not deprecated** (check the `status` field in the registry)

Tell the user which tables you picked and why. Show the table ID, title, and
what dimensions/measures are relevant.

### Step 3: Inspect metadata

Before downloading data, always fetch and display the metadata first. This
helps the user understand what's in the table and lets you build the right
filters. Read `odata-v4-guide.md` for the API patterns.

```python
# Always start with metadata inspection
from scripts.cbs_client import CBSClient
client = CBSClient()
meta = client.get_metadata("TABLE_ID")
```

### Step 4: Retrieve and process data

Download only what you need using OData filters. For wijk/buurt tables this is
critical — they can have millions of rows. Read `odata-v4-guide.md`
for filtering and pagination patterns.

Key processing steps (all handled by the helper module):
1. **Code → label resolution**: CBS returns numeric codes, not labels
2. **Region code cleanup**: Trailing spaces in RegioS codes (strip them!)
3. **Period parsing**: Convert CBS period codes to Python dates
4. **Cross-table joins**: Match on normalised RegioS + Perioden

### Step 5: Analyse and find stories

Read `analysis-recipes.md` for pre-built patterns. The best stories
come from **contrast and surprise** — look for:
- Regional outliers (gemeente or wijk that bucks the trend)
- Temporal inflection points (when did something change?)
- Correlation between housing characteristics and energy metrics
- Gaps between policy targets and reality

### Step 6: Visualise

For charts: use Plotly (interactive) or Matplotlib (static). For maps: read
`geo-pdok.md` for PDOK geodata integration.

## Critical CBS knowledge

### Period codes (Perioden)
CBS uses a specific format — the agent MUST understand this:
- `2023JJ00` = year 2023
- `2023KW01` = Q1 2023
- `2023MM06` = June 2023
- `2023X000` = half year (rare)

### Region codes (RegioS)
- `NL00` or `NL01` = Netherlands total
- `LD##` = Landsdeel
- `PV##` = Provincie
- `CR##` = COROP-gebied
- `GM####` = Gemeente
- `WK######` = Wijk
- `BU########` = Buurt

Region codes often have **trailing spaces** — always `.strip()` them.

### Data status
- **Definitief**: final figures
- **Voorlopig** (`*`): provisional, may change
- **Nader voorlopig** (`**`): revised provisional

### ⚠️ Deprecation warnings (2025–2026)
Several key housing tables are being replaced due to methodology changes:
- `82900NED` (Voorraad woningen eigendom) → new tables from 2026
- `84948NED` (Hoofdverwarmingsinstallaties) → replaced by ASD-tables
  for 2022+ with new methodology and additional data sources

Always check the `status` field in the table registry and warn the user
about deprecated tables.

## Environment setup

Many users will have a minimal dev environment (Python via uv, Node via Vite).
Before generating any code, the agent MUST detect the setup and adapt.

### Python detection

Run these checks silently before the first code block:

1. **Detect package manager**: check if `uv` is available (`which uv`). If yes,
   use `uv` commands. Fall back to `pip` / `pip3` only if `uv` is not found.
2. **Detect Python command**: try `python3 --version` first, then `python --version`.
   macOS may not have a `python` command at all. Use whichever works.
3. **Virtual environment**: if no venv is active (`echo $VIRTUAL_ENV` is empty),
   create one before installing anything:
   - With uv: `uv venv && source .venv/bin/activate`
   - Without uv: `python3 -m venv .venv && source .venv/bin/activate`

### Installing dependencies

Always install into a venv. Never use `sudo pip install`.

```bash
# Preferred (uv)
uv pip install requests pandas

# Fallback (pip)
pip install requests pandas
```

For visualisation tasks, also install plotting libraries:
```bash
# Preferred (uv)
uv pip install matplotlib plotly

# Fallback (pip)
pip install matplotlib plotly
```

### Common beginner pitfalls to handle

- **`ModuleNotFoundError`**: the venv is not activated, or packages were
  installed in a different environment. Re-activate and reinstall.
- **`command not found: python`**: use `python3` instead.
- **`pip: command not found`**: use `uv pip` or `python3 -m pip`.
- **Permission errors on install**: user is not in a venv. Create one first.
- **SSL certificate errors on macOS**: run
  `open /Applications/Python\ 3.*/Install\ Certificates.command` or use uv
  which bundles its own certificates.

## Helper module

The skill includes `scripts/cbs_client.py` — a self-contained Python module
for CBS OData v4 access. It handles:
- Catalog search (keyword search across all CBS tables)
- Metadata retrieval and human-readable display
- Data download with automatic pagination
- Code-to-label resolution
- Period code parsing
- Region code normalisation

### Importing the helper

The helper module lives at `scripts/cbs_client.py` relative to this skill's
root directory. The agent must locate it at runtime. Strategy:

1. **Find the skill directory**: search for `cbs_client.py` in the project
   tree. Common locations depending on the tool:
   - `.claude/skills/cbs-statline-skill/scripts/` (Claude Code, Open Code, Kilo Code)
   - `.cursor/cbs-statline-skill/scripts/` (Cursor)
   - `.cline/cbs-statline-skill/scripts/` (Cline)
   - Project root `scripts/` or `cbs_client.py` at root (standalone clone)
2. **Copy to the working directory**: to avoid fragile path hacks, copy
   `cbs_client.py` into the user's working directory if it's not already there.
   This is the most robust approach across all tools.

Generated code should always use a simple import:
```python
from cbs_client import CBSClient
```

If `cbs_client.py` is not in the working directory, copy it there first:
```bash
cp <path-to-skill>/scripts/cbs_client.py .
# or
cp <path-to-skill>/cbs_client.py .
```

## Output format

Always produce:
1. **A clear data question** (the hypothesis)
2. **Complete Python code** in a single script or notebook
3. **A finding summary** (2–3 sentences summarising the key insight)
4. **Caveats** (data freshness, methodology notes, what the data can't tell you)
