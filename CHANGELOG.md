# Changelog

Changes to the skeleton structure and tools (not to anyone's content).

## v1.0.1 - 2026-11-11
- lint ignores fenced code blocks and inline code (examples in docs are not errors); TODO is caught only as a
  marker (`TODO:`, a line or list item starting with TODO), not as a word in a sentence.

## v1 - 2026-11-11
- First version. Full skeleton installed by `tools/brain.py init` (no module menu): AGENTS.md block,
  CLAUDE.md / GEMINI.md pointers, Gemini settings, hot.md, wiki/ with me/ pages, raw/, board/ with an Obsidian
  Bases view, agents/ role templates (assistant, twin), progress log, maps/ (JSON Canvas), templates/,
  skills/ (base-ingest, base-lint), .kits.json, .gitignore block, .stignore example.
- brain.py: init, uninstall, status, done, lint, index, brief, search (SQLite FTS5), check, check-public.
- Coexists with Frugal-Bridge in any install order: marked blocks, `.kits.json` slots, import of its files when
  it was installed first, export back on uninstall.
- Not in v1: multi-project packs, outbox, shared lessons library.
