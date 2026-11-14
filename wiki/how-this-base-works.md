---
title: How this base works
sources: [product guide, 1.7.4]
updated: 2026-11-14
scope: private
---

# How this base works

Read this first. It is short on purpose.

## What each top folder is

- **hot.md**: what matters now. Keep it to about a dozen lines.
- **wiki/**: the pages. `me/` is about you, `projects/` and `clients/` are work, `decisions/` holds what was decided
  and why, `glossary.md` explains the words used here, `dashboard.md` shows the status at a glance.
- **wiki/sessions.md** and **wiki/memories.md**: generated lists of your AI sessions and of what each tool remembers.
  Do not edit them by hand; they are rebuilt.
- **wiki/weekly/**: one short review per week, written on Sunday.
- **board/**: cards of work to do.
- **raw/**: material you dropped in, kept as it was. Nothing here is edited.
- **plans/**, **progress/**, **agents/**, **templates/**, **maps/**, **sources/**: plans, the activity log, the roles
  of the AI helpers, page templates, the pictures of the base, and raw material saved for later.
- **projects/**: code repositories. They stay on this computer unless you turn on sync all.
- **engines/**: the settings folders of your AI tools. Secrets are never kept here.
- **tools/**: the `brain.py` program. You do not need to open it.

## Where to look first

1. `hot.md`
2. `wiki/index.md`, then only the pages you need.
3. `wiki/dashboard.md` for projects, decisions and goals.

## What syncs to other computers

By default (the **notes** scope) only the notes leave this computer: `wiki/`, `hot.md`, `plans/`, `board/`,
`progress/`, `agents/`, `templates/`, `maps/`, `sources/`, `raw/` and `research/` (without crawled text).
Code in `projects/`, `data/`, `scratch/`, `runs/`, `ops/`, `engines/` and the `.brain/` folder never leave.
Change it with `python3 tools/brain.py engine sync-scope notes|all`.

## What never to edit by hand

- `wiki/sessions.md`, `wiki/memories.md`, `wiki/glossary.md` between its markers, `wiki/dashboard.md` between its
  markers, and everything between `<!-- ... start -->` and `<!-- ... end -->` lines: they are rebuilt.
- `.brain/` (the program's own state) and `engines/` secrets.
- `raw/`: keep the originals as they are.

## Everyday

- Save a thought: tell your AI tool, or put a note in `raw/inbox/`.
- Check the setup: `python3 tools/brain.py doctor`.
- Old backups are removed after 30 days (the newest one is always kept); see `doctor` for the next cleanup.
