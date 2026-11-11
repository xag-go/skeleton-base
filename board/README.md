# Board

Your own task board, inside the base. Any agent or tool can read and write it: it is just files.

- One card = one Markdown file: `board/YYYY-MM-DD-slug.md` (date the card was created).
- Frontmatter (all required except `due`):

```yaml
title: Call the accountant
status: todo        # todo | doing | waiting | done
owner: me           # me, or a role from agents/ (assistant, twin, ...), never a tool name
project: none       # none, or the slug of a page in wiki/projects/
due: 2026-12-01     # optional
updated: 2026-11-11
scope: private
```

- Body: what, why, next step, links.
- Done cards stay (history). `hot.md` lists the 3-5 cards that matter now.
- `board.base` is an Obsidian Bases view of all cards grouped by status. Open it in Obsidian; agents just read the files.
- `python3 tools/brain.py lint` checks every card (status, owner role, project page, dates).
- Template: `templates/card.md`.
