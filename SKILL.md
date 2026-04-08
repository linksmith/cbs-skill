---
name: cbs-statline-hackathon
description: "Skill for data journalism hackathons using CBS StatLine open data, focused on housing (woningen) and energy transition (energietransitie) in the Netherlands. Use this skill whenever the user wants to find, evaluate, download, analyse, or visualise CBS open data — especially tables about Dutch housing stock, energy labels, heat pumps, solar panels, gas-free homes, building permits, housing prices, or neighbourhood-level (wijk/buurt) statistics. Also trigger when the user mentions StatLine, CBS, OData, Dutch statistics, energielabel, warmtepomp, zonnepanelen, aardgasvrij, woningvoorraad, or any combination of housing and energy data for the Netherlands. This skill is designed for mixed audiences (journalists + coders) and generates complete, runnable Python code with explanations."
---
repo: https://github.com/linksmith/cbs-skill
---

## Purpose

Turn an AI agent into a knowledgeable CBS StatLine research partner that can
discover relevant tables, understand their structure, download and join data,
perform analysis, and help frame findings as data journalism story angles —
all focused on the intersection of **housing** and **energy transition** in
the Netherlands.

## Audience

Mixed: data journalists who can read Python, and developers who may not know
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

Restate the user's question as a data journalism hypothesis. Examples:
- "Is the energy transition happening faster in wealthy neighbourhoods?"
- "Which municipalities are falling behind on gas-free housing targets?"
- "Do homes with solar panels also have better energy labels?"

### Step 1b: Create METHODE.md

At the very start of every analysis, create a file called `METHODE.md` in the
working directory. This is a living document that grows with each step. It
serves as the single source of truth for reproducibility and verification.

Start it with:
```markdown
# Methodologie

## Onderzoeksvraag
<the hypothesis from Step 1>

## Databronnen
<will be filled in Step 2>

## Bewerkingen
<will be filled in Step 4>

## Aannames en beperkingen
<will be filled in Step 5>

## Verificatie
<will be filled in Step 7>
```

Update `METHODE.md` at every subsequent step. Never wait until the end.

### Step 2: Identify tables

Read `table-registry.md` and select 1–3 tables that can answer the
question. Prioritise tables that:
- Share a **join key** (RegioS codes at the same geographic level)
- Have overlapping **Perioden** (time periods)
- Are **not deprecated** (check the `status` field in the registry)

Tell the user which tables you picked and why. Show the table ID, title, and
what dimensions/measures are relevant.

**Update METHODE.md — Databronnen**: for each table, document:
- CBS table ID and full title
- Direct URL: `https://opendata.cbs.nl/statline/#/CBS/nl/dataset/TABLE_ID`
- Date of data retrieval
- Data status (Definitief / Voorlopig)
- Which dimensions and measures are used
- Any filters applied (periods, regions)

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

**Update METHODE.md — Bewerkingen**: document every transformation applied to
the raw data. For each processing step, record:
- What was done (e.g. "filtered to GM-level regions", "joined on RegioS")
- Why it was done (e.g. "buurt-level data too granular for this question")
- Row counts before and after (e.g. "84,302 rows → 388 rows after filter")
- Any rows dropped and why (e.g. "12 rows with missing values removed")
- Formulas or calculations used (e.g. "percentage = count / total * 100")
- Join keys and join type (e.g. "inner join on RegioS + Perioden")

### Step 5: Analyse and find stories

Read `analysis-recipes.md` for pre-built patterns. The best stories
come from **contrast and surprise** — look for:
- Regional outliers (gemeente or wijk that bucks the trend)
- Temporal inflection points (when did something change?)
- Correlation between housing characteristics and energy metrics
- Gaps between policy targets and reality

**Update METHODE.md — Aannames en beperkingen**: document:
- Assumptions made (e.g. "we assume provisional 2024 data is directionally correct")
- Theories being tested and their basis
- Statistical methods or algorithms used (e.g. "Pearson correlation", "year-over-year % change")
- Known limitations (e.g. "CBS changed methodology in 2022, pre/post comparison is approximate")
- What the data cannot tell you (e.g. "correlation does not imply causation")

### Step 6: Visualise

For charts: use Plotly (interactive) or Matplotlib (static). For maps: read
`geo-pdok.md` for PDOK geodata integration.

### Step 7: Verify results

This step is **mandatory**. Never skip it. After completing the analysis,
the agent must verify its own work using `METHODE.md` as the reference.

#### 7a: Self-verification

Re-read `METHODE.md` and verify each section:

1. **Data provenance check**: re-fetch a small sample from the CBS API and
   compare it against the data used in the analysis. Do the numbers match?
   If not, document why (e.g. data updated since retrieval, filter mismatch).
2. **Calculation check**: pick 2–3 representative rows and manually
   recalculate the derived values (percentages, aggregations, joins) step by
   step. Show the manual calculation and compare against the script output.
   If results differ, find and fix the bug.
3. **Analysis sanity check**: review the findings against common sense and
   domain knowledge. For example:
   - Are percentages between 0–100%?
   - Do totals add up?
   - Are trends directionally plausible given known context?
   - Do outliers have a plausible explanation?

#### 7b: Document verification results

**Update METHODE.md — Verificatie**: record:
- What checks were performed
- Sample values compared (expected vs actual)
- Whether any discrepancies were found and how they were resolved
- Confidence level in the results (high / medium / low) with justification

#### 7c: Flag items for human review

At the end of `METHODE.md`, add a section:

```markdown
## Te controleren door een specialist
- [ ] <specific finding that should be reviewed by a domain expert>
- [ ] <any statistical claim that warrants a second opinion>
- [ ] <any data point that seemed surprising or counterintuitive>
```

Tell the user: these findings should ideally be reviewed by someone with
domain expertise (e.g. a housing policy researcher, energy statistician, or
experienced data journalist) before publication.

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
   - `.claude/skills/cbs-statline-hackathon/scripts/` (Claude Code, Open Code, Kilo Code)
   - `.cursor/cbs-skill/scripts/` (Cursor)
   - `.cline/cbs-skill/scripts/` (Cline)
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

For hackathon participants, always produce:
1. **A clear data question** (the hypothesis)
2. **Complete Python code** in a single script or notebook
3. **`METHODE.md`** — the full methodology document (data sources, processing,
   assumptions, verification results, items for specialist review)
4. **A finding summary** (2–3 sentences a journalist could use as a lede)
5. **Caveats** (data freshness, methodology notes, what the data can't tell you)

`METHODE.md` is a **required deliverable**, not optional. It is what makes
the analysis reproducible and trustworthy. A data journalism story without
documented methodology is not publishable.
