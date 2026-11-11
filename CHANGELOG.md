# Changelog

Changes to the skeleton structure and tools (not to anyone's content).

## v1.2.0 - 2026-11-11
- `brain.py map [--force]`: draws the base as a mind map, deterministic (same pages = same bytes).
  - `maps/brain.canvas` (JSON Canvas 1.0, opens in Obsidian): `me` in the centre (`wiki/me/` + `hot.md`), one
    coloured group per wiki folder plus `board` and `agents` around it, a file box per page / card / role, an edge
    per `[[link]]` (deduped, both directions = one edge with two arrows, no self-links; cards also link to their
    `project` and `owner`), no overlapping boxes. The auto list in `wiki/index.md` is not drawn as links.
  - `maps/brain.html`: one self-contained offline file (vanilla JS + canvas, no network): radial layout,
    colours per folder, search, zoom/pan, legend (click to hide a folder), click a dot for title, folder,
    updated date, first lines and links. Page text is embedded as escaped JSON and shown as text only.
  - Never overwrites a `maps/brain.*` file it did not make (unless `--force`).
- init runs `map` once at the end; uninstall removes the generated maps.
- lint: `maps/brain.canvas` is generated, so a stale one is a warning ("run map"), never an error. `index`
  unchanged.

## v1.1.0 - 2026-11-11
- AGENTS.md: new "Saving knowledge" section. Durable knowledge goes into the base (clients, decisions, people,
  project status, then `index` and the agents log); a copy in the tool's own memory is fine, never only there.
- `brain.py collect`: copies new items from Claude Code, Codex (Markdown and SQLite), Gemini CLI, Hermes
  (Markdown and fact store) and OpenClaw memories into `raw/inbox/collected/SOURCE/`, read-only, deduped by hash
  in `.brain/collector.json`. `--baseline`, `--only`, `--since`, `--quiet`. Missing stores and unknown database
  layouts are skipped with a note.
- `brain.py connect [--timer]` / `disconnect`: per-user pointer block (v2) in `~/.claude/CLAUDE.md`,
  `~/.codex/AGENTS.md`, `~/.gemini/GEMINI.md` (only for installed tools; an older block is replaced in place),
  Claude Code `SessionEnd` / `PreCompact` hooks that run `collect`, optional daily systemd user timer. Recorded in
  `.kits.json`; `disconnect` and `uninstall` restore the previous files exactly.
- init: merges `Bash(python3 tools/brain.py *)` into the base's `.claude/settings.json` `permissions.allow`
  (removed by uninstall). `.gitignore` block also ignores `.brain/backups/` and `.brain/collector.lock`.
- init keeps the `connect` record when it is re-run.

## v1.0.1 - 2026-11-11
- lint: quote lines may contain inline code and quotes (only fenced examples are skipped).
- init: a file already identical to the kit stays upgradable.
- init re-run no longer recreates files you deleted after an earlier install (except hot.md, wiki/index.md,
  wiki/log.md, tools/brain.py).
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
