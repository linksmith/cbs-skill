# CBS StatLine Hackathon Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An AI agent skill for data journalism hackathons using CBS StatLine open data, focused on housing (woningen) and energy transition (energietransitie) in the Netherlands. Works with Claude Code, Open Code, Kilo Code, Cursor, Windsurf, Cline, Aider, and 40+ other AI coding tools.

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

### Dependencies

The Python helper module requires:

```bash
pip install requests pandas
```

### Quick Install (Any Agent)

If you use the [Vercel Skills CLI](https://github.com/vercel-labs/skills), this works across 40+ agents:

```bash
npx skills add linksmith/cbs-statline-skill
```

See below for tool-specific instructions.

### Cursor

**Option 1: Clone to Cursor rules directory**

```bash
git clone https://github.com/linksmith/cbs-statline-skill.git ~/.cursor/rules/cbs-statline-skill
```

**Option 2: Add to project `.cursorrules`**

```bash
# In your project root
curl -L https://raw.githubusercontent.com/linksmith/cbs-statline-skill/main/SKILL.md -o .cursorrules
```

**Option 3: Project-level installation**

```bash
# Clone into your project
git clone https://github.com/linksmith/cbs-statline-skill.git .cursor/cbs-statline-skill
```

Then reference in `.cursorrules`:
```
Use the CBS StatLine skill in .cursor/cbs-statline-skill/ for all Dutch housing and energy data queries.
```

### Windsurf (Codeium)

**Option 1: Global rules**

```bash
git clone https://github.com/linksmith/cbs-statline-skill.git ~/.windsurf/rules/cbs-statline-skill
```

**Option 2: Project-level**

Create `.windsurf/rules/cbs-statline-skill.md` in your project:
```bash
curl -L https://raw.githubusercontent.com/linksmith/cbs-statline-skill/main/SKILL.md -o .windsurf/rules/cbs-statline-skill.md
```

### Claude Code / Open Code / Kilo Code

All three tools support the same plugin format:

**Option 1: Install as a plugin** (recommended, no npm/node required)

```bash
claude plugin install --from https://github.com/linksmith/cbs-statline-skill
```

Replace `claude` with `open` or `kilo` depending on your tool.

**Option 2: Add as a project skill**

```bash
mkdir -p .claude/skills
git clone https://github.com/linksmith/cbs-statline-skill.git .claude/skills/cbs-statline-skill
```

**Option 3: Add as a slash command**

```bash
mkdir -p .claude/commands
curl -L https://raw.githubusercontent.com/linksmith/cbs-statline-skill/main/skills/cbs-statline-skill/SKILL.md \
  -o .claude/commands/cbs-statline-skill.md
```

### Cline (VS Code Extension)

**Option 1: Add to .clinerules**

```bash
curl -L https://raw.githubusercontent.com/linksmith/cbs-statline-skill/main/SKILL.md -o .clinerules
```

**Option 2: Workspace settings**

1. Clone the skill to your workspace:
```bash
git clone https://github.com/linksmith/cbs-statline-skill.git .cline/cbs-statline-skill
```

2. In VS Code settings, add to `cline.customInstructions`:
```
Use CBS StatLine skill for Dutch housing/energy data. See .cline/cbs-statline-skill/SKILL.md
```

### Roo Code (VS Code Extension)

**Option 1: Add to .roorules**

```bash
curl -L https://raw.githubusercontent.com/linksmith/cbs-statline-skill/main/SKILL.md -o .roorules
```

**Option 2: Custom instructions**

In VS Code, open Roo Code settings and add to Custom Instructions:
```
For CBS StatLine Dutch data queries, reference the skill at:
https://github.com/linksmith/cbs-statline-skill

Download cbs_client.py and table-registry.md for data access.
```

### Aider

**Option 1: Add as read-only context**

```bash
# Clone to a location aider can access
git clone https://github.com/linksmith/cbs-statline-skill.git ~/skills/cbs-statline-skill

# Add to your aider session
aider --read ~/skills/cbs-statline-skill/SKILL.md ~/skills/cbs-statline-skill/table-registry.md
```

**Option 2: Add to .aider.conf.yml**

```yaml
read:
  - ~/skills/cbs-statline-skill/SKILL.md
  - ~/skills/cbs-statline-skill/table-registry.md
  - ~/skills/cbs-statline-skill/cbs_client.py
```

### OpenHands

**Option 1: Add to workspace**

```bash
git clone https://github.com/linksmith/cbs-statline-skill.git .openhands/cbs-statline-skill
```

**Option 2: Custom instructions**

Add to `.openhands/instructions.md`:
```
For CBS StatLine Dutch housing and energy data:
1. Read .openhands/cbs-statline-skill/SKILL.md for workflow
2. Use cbs_client.py for data access
3. Reference table-registry.md for available tables
```

### Goose (Block)

**Option 1: Add to Goose extensions**

```bash
git clone https://github.com/linksmith/cbs-statline-skill.git ~/.goose/extensions/cbs-statline-skill
```

**Option 2: Add instruction file**

```bash
curl -L https://raw.githubusercontent.com/linksmith/cbs-statline-skill/main/SKILL.md -o ~/.goose/instructions/cbs-statline-skill.md
```

### GitHub Copilot

**Option 1: Add to .github/copilot-instructions.md**

```bash
mkdir -p .github
curl -L https://raw.githubusercontent.com/linksmith/cbs-statline-skill/main/SKILL.md -o .github/copilot-instructions.md
```

**Option 2: Reference in VS Code settings**

In `.vscode/settings.json`:
```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "file": ".github/copilot-instructions.md"
    }
  ]
}
```

### Generic AI Assistants

For any AI assistant that supports custom instructions or context files:

1. Download the SKILL.md file:
```bash
curl -L https://raw.githubusercontent.com/linksmith/cbs-statline-skill/main/SKILL.md -o cbs-statline-skill-instructions.md
```

2. Paste the contents into your AI assistant's custom instructions or system prompt.

3. For code generation, also download `cbs_client.py`:
```bash
curl -L https://raw.githubusercontent.com/linksmith/cbs-statline-skill/main/cbs_client.py -o cbs_client.py
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
cbs-statline-skill/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest for Claude/Open/Kilo Code
├── skills/
│   └── cbs-statline-skill/
│       └── SKILL.md          # Main skill definition with workflow
├── scripts/
│   └── cbs_client.py         # Python helper module for CBS OData v4 API
├── SKILL.md                  # Root copy (for tools that expect it here)
├── table-registry.md         # Curated list of ~35 vetted tables with join keys
├── analysis-recipes.md       # Story templates for data journalism
├── odata-v4-guide.md         # OData v4 API patterns and filtering
├── geo-pdok.md               # Geographic visualization with PDOK
└── evals.json                # Evaluation prompts for skill testing
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

- **Issue Tracker:** https://github.com/linksmith/cbs-statline-skill/issues
- **Pull Requests:** https://github.com/linksmith/cbs-statline-skill/pulls

## Resources

- [CBS StatLine](https://opendata.cbs.nl/)
- [CBS OData v4 API Documentation](https://datasets.cbs.nl/odata/v1/)
- [PDOK Geodata](https://www.pdok.nl/)
