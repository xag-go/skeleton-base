# Changelog

Changes to the skeleton structure and tools (not to anyone's content).

## v1.3.4 - 2026-11-11
- Uninstall keeps your data (owner rule: removing Skeleton Base never loses anything of the user's).
  - `uninstall` first writes a full backup of the base (`.git` and dotfiles included) to
    `~/skeleton-base-backups/NAME-YYYYmmdd-HHMMSS.tar.gz` (mode 600, folder 700, outside the base, read back and
    checked), prints its path and a one-line restore command (`tar -xpzf`, file modes kept); a failed backup stops the uninstall with nothing
    changed. `--backup-dir DIR` (refused inside the base), `--no-backup` only when given.
  - After uninstall it prints what was kept and where (per folder, git commit count) and how to re-open or
    reinstall (`init` adopts the files).
  - Generated maps: `.brain/map.json` records what `map` wrote. A map you changed is no longer deleted by
    uninstall nor overwritten by `map`/`init` (before: any file with the map marker was deleted/overwritten);
    `map --force` keeps a copy in `.brain/backups/map-TIME/` first, also over a file map did not make.
    `map` exits 0 when the only thing it left alone is your edited map (an installer re-running it does not fail).
  - Text you wrote inside our block of `AGENTS.md`/`CLAUDE.md`/`GEMINI.md`/`.gitignore` is copied to
    `.base-folder/backup/` before the block (or a block-only file) is removed.
  - `.claude/settings.json` / `.gemini/settings.json`: when removing our keys leaves your original settings, your
    original bytes are put back (layout too), from init's backup.
  - `.brain/collector.lock` is removed with the other run-time files; `.brain/search.db` is still removed (an
    index rebuilt from your files); everything else in `.brain/` stays.
  - Importing Frugal-Bridge files never overwrites an existing `wiki/me/frugal-user.md`,
    `wiki/decisions/frugal-decisions.md` or `progress/frugal-progress.md` without a copy in `.base-folder/backup/`.
  - `.gitignore` block also ignores `.brain/map.json`.
- Tests: every test command runs with an isolated temporary HOME (before, a few ran with the real one). 7 new
  tests (98 in total): a rich base (pages, raw incl. collected and sqlite-sourced items, cards, edited template
  and agent, `hot.md`, `progress/agents.log`, user text in `AGENTS.md` outside the block, 3 git commits, `.brain`
  state and backups, unknown files, a symlink, an edited map) is uninstalled with every user file byte-identical
  and the git log intact, the archive (mode 600) restores the exact tree; reinstall adopts without loss or
  duplication; edits inside the kit block copied; backup dir inside the base or unwritable refuses and changes
  nothing; map edits survive `map` and `init`; your own `.claude/settings.json` layout comes back byte-identical; `disconnect` changes nothing in the base but `.kits.json`.

## v1.3.3 - 2026-11-11
- Pointer file: `connect` (and auto-connect) writes `~/.config/skeleton-base/base` (one line, the base folder),
  recorded in `.kits.json` like the systemd units; `disconnect` removes it, or gives back the bytes another base
  wrote there, with its folders: the home is byte-identical. Frugal-Bridge (from 4920444) reads it, so it finds the
  base even when no tool rules file carries the pointer block (only Hermes without `SOUL.md`): no second user file.
- `disconnect` / `uninstall` with Frugal-Bridge at user level: pointer blocks, systemd units and the pointer file
  are removed first, then Frugal-Bridge is told to forget the base (`--no-base` when its setup takes it, else the
  `base` entry in its `global.json`, which it now looks at first, is dropped; a `FRUGAL_BASE` naming this base is
  kept out of its environment) and its `install --global` is re-run. It really goes back to its own `USER.md`: no
  more "still points at this base".
- `connect` passes `--base <this base>` to Frugal-Bridge's `install --global` when its setup takes that flag.
- Re-running Frugal-Bridge always names its tools (`--hosts`): the ones in its `global.json` plus those waiting for
  a rules file (`needs_user`, e.g. Hermes without `SOUL.md`). With none recorded it is not re-run: its
  auto-detection would otherwise add a tool the user never picked (found because its program is on `PATH`).
- Frugal-Bridge capabilities are read from its setup script (`frugal_caps`: quoted `Path:`, pointer file, systemd
  units, `--base`, `--no-base`, recorded base), not from its version or its messages. The space-path note only
  shows for a Frugal-Bridge that can find such a base in none of these ways.
- Tests: the 4 Frugal-Bridge tests that broke with its new base discovery now check the new behaviour (no second
  user file, block order, export back, Frugal-Bridge on its own file after disconnect, re-runs byte-identical); they
  read which user file Frugal-Bridge's block names from the paths in it, not its wording. 5 new tests (91 in
  total): disconnect with watch units + pointer file, a home with only Hermes (no `SOUL.md`) found through the
  pointer file (with another tool's program on `PATH` that must not be added), `frugal_caps`, `--base`/`--no-base`
  passed to a Frugal setup that takes them, and a pointer file of another base given back. Test runs drop
  `FRUGAL_HOME`, `FRUGAL_BASE`, `HERMES_AGENT` from the environment.

## v1.3.2 - 2026-11-11
- Base paths with spaces: the pointer block's `Path:` line keeps its format for a plain path; a path with a space,
  quote, backslash, backtick or `$` is wrapped in the first of `"` `'` `` ` `` it does not contain, no escaping
  (`Path: "/home/me/My Base"`). The `cd` command in the block is shell-quoted (hooks already were), and the systemd
  units escape `ExecStart=` for systemd (`%%`, `$$`, `\\`, `\"`, double quotes around a word with a space). A path
  with a line break is refused for the units. Older Frugal-Bridge builds (without quoted `Path:` support) cannot read
  such a line: `connect` says so and Frugal keeps its own user file (README).
- Zero-touch with Frugal-Bridge: when the watcher (or `connect`) connects a NEW tool and Frugal-Bridge uses this
  base, it runs Frugal's `install --global --hosts TOOL` for that tool alone, if Frugal supports it and does not
  have it yet. The new tool gets both blocks, base first.
- `.kits.json` records the product release (`kits.base-folder.release`, `RELEASE` in `tools/brain.py`), so an
  installer can tell a newer base from an older one and never downgrade it.
- 5 new tests (86 in total): a base path with spaces, `$`, `%` and quotes (block, hooks run by a shell, systemd
  `ExecStart=` parsed back, `systemd-analyze verify`, disconnect byte-identical), the quoting rules, a new tool after
  both kits with the real Frugal-Bridge setup, a new tool when Frugal does not use the base, and a path with spaces
  plus Frugal-Bridge (old and new Frugal parser).

## v1.3.1 - 2026-11-11
- Frugal first, base later, at user level: when Frugal-Bridge is installed with `install --global`, `connect` and
  the watcher's auto-connect merge the filled lines of `~/.frugal-bridge/USER.md` (or `$FRUGAL_HOME/USER.md`) into
  the base user slot (`wiki/me/who-i-am.md`, `wiki/me/how-to-talk-to-me.md`). Empty fields are filled, other lines
  added under `## From Frugal-Bridge USER.md`; nothing is overwritten. Duplicates and conflicts go on a board card
  (`board/DATE-review-frugal-user-import.md`). Backup in `.brain/backups/frugal-import-TIME/`, record in
  `.kits.json` (`kits.base-folder.frugal_user`, kept by `init`): a re-run imports nothing new.
- Then `connect` runs Frugal-Bridge's own `kit/setup.py install --global` (from `~/frugal-bridge` or
  `FRUGAL_BRIDGE_KIT`; skipped with a note when not found) for the tools it already has, so it switches to the
  base. Its old `USER.md` stays where it is.
- Block order in user-level files: the base block is inserted in front of an existing Frugal-Bridge block, whose
  bytes are never changed; an older base block found after it is moved in front.
- `disconnect` and `uninstall`: while Frugal-Bridge uses the base, the user slot is exported back to its
  `USER.md` (old one backed up to `FRUGAL_HOME/backup/skeleton-base-TIME/`) and its `install --global` re-run, so
  it uses its own file again.
- `collect` / `watch` leave Frugal-Bridge's rules block out of collected rules-file memories (`~/.gemini/GEMINI.md`,
  `~/.qwen/QWEN.md`, added files), like the base's own block: it is a kit's rules, not something the user taught.
- 6 new tests with the real Frugal-Bridge setup in a temp HOME and FRUGAL_HOME (81 in total).

## v1.3.0 - 2026-11-11
- `brain.py watch`: instant collect. Foreground daemon, standard library only: inotify through `ctypes`, polling
  every 5 s where inotify is not available (`--poll`). Debounce 2 s quiet / 10 s max (`--quiet-s`, `--max-s`).
  Each run, in a child process: auto-connect, collect, then `index` + `map` + a git commit of only the files it
  writes, only when something is new (never pushes). Missing folders are picked up when they appear, deleted ones
  when re-created; a full rescan every 10 minutes. SQLite stores count only real writes to `-wal` (any reader,
  our own read-only collect too, opens `-wal` / `-shm`). One watcher per base (`.brain/watch.lock`). The daemon
  re-executes itself from bytecode in `.brain/pycache/`: ~19 MB idle.
- `watch --add PATH [--source NAME] [--match GLOB,...] [--depth N]`, `--remove PATH`, `--list`, `--discover`
  (suggestions only), `--once`. Added locations live in `.brain/watch.json` and are reloaded live. Any SQLite
  store is read read-only: text columns of each row become one item, volatile columns (access counters, scores,
  last use, embeddings) are left out. `collect --only` accepts the added sources.
- New built-in locations: Hermes profiles (`~/.hermes/profiles/*/memories/*.md` and `*/memory_store.db`), Qwen Code
  (`~/.qwen/QWEN.md`, new `qwen` source).
- `connect` covers more tools: Qwen Code, opencode, Windsurf, Kiro (created if missing), OpenClaw and Hermes
  (`SOUL.md`, only when it exists), Cursor listed as needs-user. `connect --print` prints the block.
- Zero-touch: on a connected base the watcher connects a known tool as soon as its folder appears, and an unknown
  folder that looks like an AI tool (rules file, memory folder or memory database) through its existing rules
  file, and watches its memory. No rules file: listed as `needs-user` in `.brain/watch.json` and `watch --list`.
  Other folders are never touched. All of it is recorded in `.kits.json` and undone by `disconnect`.
  `"never"` in `.brain/watch.json` (folders or globs under `~`) keeps tools or files out of connect and auto-connect.
- `connect --watch` writes `~/.config/systemd/user/skeleton-base-watch.service` (`Restart=on-failure`,
  `MemoryMax=40M`, `Nice=10`) plus the daily timer as a safety net, and prints the enable command; `--kick` adds a
  Claude Code `PostToolUse` (`Write|Edit`) hook that writes `.brain/kick`. `disconnect` removes both.
- `.gitignore` block also ignores `.brain/watch.lock`, `.brain/kick`, `.brain/*.tmp`, `.brain/pycache/`;
  uninstall removes them.

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
