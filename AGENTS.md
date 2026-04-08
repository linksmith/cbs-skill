# CBS StatLine Hackathon Skill

> **Sync notice:** This file is duplicated as `CLAUDE.md` (for Claude Code). Keep both files in sync when making changes.

## Releases

This project uses GitHub Actions to build releases. To publish a new release:

1. Bump the version in `.claude-plugin/plugin.json`
2. Commit the changes
3. Create and push a git tag: `git tag v<version> && git push origin v<version>`
4. The `.github/workflows/release.yml` workflow will automatically build `cbs-skill.zip` and attach it to the GitHub Release

The zip is then available at:
`https://github.com/linksmith/cbs-skill/releases/latest/download/cbs-skill.zip`

## Project structure

- `.claude-plugin/plugin.json` — Plugin manifest for Claude/Open/Kilo Code
- `skills/cbs-skill/SKILL.md` — Skill definition (plugin layout)
- `scripts/cbs_client.py` — Python helper module (plugin layout)
- `SKILL.md` — Root copy for tools that expect it here (Cursor, Cline, etc.)
- `cbs_client.py` — Root copy of the helper module
- `table-registry.md`, `analysis-recipes.md`, `odata-v4-guide.md`, `geo-pdok.md` — Reference docs read by the skill

## Testing

```bash
pip install requests pandas pytest
pytest test_cbs_client.py
```
