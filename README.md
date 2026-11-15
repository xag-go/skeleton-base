# Skeleton Base

A personal knowledge base as a plain folder of Markdown files. Any AI tool can pick up your work from it: it reads
one short rules file, then only the pages the task needs. No app, no server, no account. Python 3.10+ standard
library only.

## Start here

- **Owner:** [wiki/how-this-base-works.md](wiki/how-this-base-works.md) (plain words: what each folder is, what syncs).
- **Every command:** `python3 tools/brain.py help`. The full reference (`docs/REFERENCE.md`: the sync rules, the tool
  matrix) and the list of changes (`CHANGELOG.md`) are in the Skeleton Base repository, not in an installed base.
- **Rules for the AI tools:** [AGENTS.md](AGENTS.md) and [CLAUDE.md](CLAUDE.md).
- **Security:** [SECURITY.md](SECURITY.md).

## Quick commands (run inside the base)

```
python3 tools/brain.py status      what is new since the last ingest
python3 tools/brain.py lint        check the pages
python3 tools/brain.py doctor      check the whole setup, with the fix for each problem
python3 tools/brain.py sessions    write wiki/sessions.md
python3 tools/brain.py products    write wiki/products.md (which release of each product is installed)
python3 tools/brain.py server      write wiki/server.md (what runs here)
```
