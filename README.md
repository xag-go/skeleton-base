# Skeleton Base

A personal knowledge base as a plain folder of Markdown files. Any AI tool can pick up your work from it: it reads
one short rules file, then only the pages the task needs. No app, no server, no account. Python 3.10+ standard
library only.

## Start here

- **Owner:** [wiki/how-this-base-works.md](wiki/how-this-base-works.md) (plain words: what each folder is, what syncs).
- **Full reference:** [docs/REFERENCE.md](docs/REFERENCE.md) (every command, the sync rules, the tool matrix).
- **Rules for the AI tools:** [AGENTS.md](AGENTS.md) and [CLAUDE.md](CLAUDE.md).
- **Changes:** [CHANGELOG.md](CHANGELOG.md). **Security:** [SECURITY.md](SECURITY.md).

## Quick commands (run inside the base)

```
python3 tools/brain.py status      what is new since the last ingest
python3 tools/brain.py lint        check the pages
python3 tools/brain.py doctor      check the whole setup, with the fix for each problem
python3 tools/brain.py sessions    write wiki/sessions.md
```
