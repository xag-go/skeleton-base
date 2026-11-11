---
name: base-lint
description: Check the knowledge base with brain.py lint and fix what it reports (frontmatter, broken links, orphans, quotes not in source, stale pages, board cards). Use after editing the wiki or when the user asks to check or clean the base.
---

# base-lint

1. Run `python3 tools/brain.py lint`. Exit code 0 = clean, 2 = problems (listed one per line).
2. Fix each problem:
   - missing frontmatter / field: add `title`, `sources`, `updated`, `scope`.
   - broken link `[[x]]`: fix the name or create the page.
   - orphan: link the page from a related page or run `python3 tools/brain.py index`.
   - QUOTE NOT IN SOURCE: copy the exact text from the raw file, or remove the claim.
   - changed since ingest: re-read the raw file, update the listed pages, then run `done` again.
   - board card: use a valid status, an owner role that exists in `agents/`, a project page that exists.
3. Warnings (NEW raw files) are not errors: they are waiting for `base-ingest`.
4. Run lint again until it passes. Do not silence a check by deleting content you were not asked to delete.
