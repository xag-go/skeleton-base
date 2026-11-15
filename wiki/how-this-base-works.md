---
title: How this base works
sources: [product guide, 1.7.7]
updated: 2026-11-15
scope: private
---

# How this base works

Read this first. It is short on purpose.

## What each top folder is

- **hot.md**: what matters now. Keep it to about a dozen lines.
- **wiki/**: the pages. `me/` is about you; work goes in `projects/` and `clients/`; `decisions/` holds what was
  decided and why. A sub-folder appears with its first page.
- **board/**: cards of work to do. A card with status `waiting`, or one of your own cards, shows on the dashboard
  under "Waiting on the owner".
- **raw/**: material you dropped in, kept as it was. Nothing here is edited.
- **agents/**, **templates/**, **maps/**, **progress/**, **skills/**: the roles of the AI helpers, page templates,
  the pictures of the base, the activity log, and skills any AI tool can load.
- **projects/**: code repositories. They stay on this computer unless you turn on sync all.
- **engines/**: the settings folders of your AI tools. Secrets are never kept here.
- **tools/**: the `brain.py` program. You do not need to open it.

Other folders (plans, research, data and so on) are made when they are first used. The list below names the ones
this base has.

<!-- base-guide:start -->
<!-- base-guide:end -->

## Where to look first

1. `hot.md`
2. `wiki/index.md`, then only the pages you need.
3. The dashboard, once the daily watch has made it: goals, projects by status, what waits on you.

## What syncs to other computers

By default (the notes scope) only the notes leave this computer: the pages, `hot.md`, the board, the log, the roles,
the templates, the maps and `raw/`, plus the plan and research folders when you have them (without crawled text).
Code in `projects/`, the tool folders in `engines/`, heavy data and the `.brain/` folder never leave.
Change it with `python3 tools/brain.py engine sync-scope notes|all`.

## What never to edit by hand

- The pages made by the program (the list above names them) and everything between `<!-- ... start -->` and
  `<!-- ... end -->` lines: they are rebuilt.
- `.brain/` (the program's own state) and `engines/` secrets.
- `raw/`: keep the originals as they are.

## Everyday

- Save a thought: tell your AI tool, or put a note in `raw/inbox/`.
- Check the setup: `python3 tools/brain.py doctor`. It lists each problem with its fix.
- A project or decision page says where it stands with `status:` (active, waiting, paused, superseded, done).
- Old backups are removed after 30 days (the newest one is always kept); see `doctor` for the next cleanup.
