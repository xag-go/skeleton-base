# Changelog

Changes to the skeleton structure and tools (not to anyone's content).

## v1.6.0 - 2026-11-12
Everything can live in the base, for any tool:
- **Each tool's folder follows its own setting.** `connect`, `collect`, `watch` and the hooks resolve every tool's
  folder through its own variable (`CLAUDE_CONFIG_DIR` with `.claude.json` inside, `CODEX_HOME`, `HERMES_HOME`,
  `OPENCLAW_STATE_DIR`/`OPENCLAW_HOME`, `COPILOT_HOME`, `GEMINI_CLI_HOME`, XDG for opencode/Kilo/Goose); a relocated
  tool no longer gets an empty `~/.claude` made by `connect`. Collected origins keep the default names.
- **Several folders of one tool**: `connect --tool-dir TOOL=DIR` / `--claude-config-dir DIR` (repeatable) and the
  shared registry `~/.config/ai-tool-dirs.d/*.json` (+ `~/.config/claude-code-dirs.d/`), read by connect, collect,
  watch and Frugal-Bridge; disconnect gives every folder back byte-identical.
- **Layout**: `engines/`, `projects/` (+ `engines.json`, `projects.json`). One per-tool table makes the `.gitignore`
  and `.stignore` blocks (`layout --print`): the safe files of each tool folder (rules, agents, skills, memories,
  hooks, scripts) reach git and Syncthing, secrets never (they come first, path-aware: a skill named `x-token-spend`
  is kept); the `.stignore` block is added to a changed `.stignore` too and stays kit-owned.
- **Pre-commit guard** (`guard`, hook written by `init`), also run by the watcher before its own commits.
- **`engine adopt|release|mirror|unmirror|sync|list`**, **`projects move [--undo]|scan|clone`**, **`doctor`**.
- **Never walked**: archive (uninstall backup), tidy snapshot, MCP `read_page`, `check-public` in a git repo.
- `check` adds the git safety checks; `watch --discover` lists configured tool folders not wired yet.
- README: the MCP server is the generic door for any agent (and why ACP is not).
- 27 new tests (189 in total).

## v1.5.4 - 2026-11-11
Three fixes from a live run of `tidy` and `file` on a real base:
- **`tidy` no longer puts a good page back because the watcher wrote at the same time.** Each page run now holds the
  collector lock (`.brain/collector.lock`, the one `collect` uses), and the watcher's file step holds the wiki lock
  and waits for a tidy run to finish, then goes on (its queue is kept: events are not dropped). The outside-wiki
  check ignores the watcher's generated writes (`maps/`) and NEW collected memories under `raw/inbox/collected/`.
  It still flags a change to an EXISTING raw file, to any other file outside `wiki/`, and a NEW file that is not a
  collected memory. Tests: a fake harness that edits its page while a simulated watcher writes maps and a new memory
  (accepted, and the lock is seen as held during the run); a fake harness that edits an existing raw file (put back).
- **`tidy` exits 0 when a page was put back.** The unit no longer shows `failed` for a put-back that was handled
  (raw kept, retried next run); the log line says `put back`. Non-zero stays for real errors: no harness found for
  `--harness`, a crash, bad arguments.
- **`file` records index lines and duplicates as done.** A noop item gets the same bookkeeping as a filed one, page =
  the page it duplicates or `wiki/index.md`, and `watch` commits that bookkeeping too (a fresh clone no longer sees
  the item as NEW). Test: after `file`, `status` reports 0 pending and `lint` 0 warnings for an index-only item.
  Note: in the fixture this already reported 0 pending; the live case could not be reproduced in the test base, so
  the test pins the behaviour and the commit gap is the part that was really missing.

## v1.5.3 - 2026-11-11
`brain.py file` now flags a small number change as a conflict too: a patch or minor version bump (1.5.1 -> 1.5.2),
a port or a count that changed in the same place of the sentence. Before, only a number with no shared digits
(1.5.1 -> 2.0.0) was flagged. An extra number that is only in the new memory is still no conflict.

## v1.5.2 - 2026-11-11
`brain.py file` no longer flags a false negation conflict:
- A negation (or changed number) is compared only between the page sentence and the part of the new memory that lines
  up with it: the clause of the memory (split on . ; : ! ? dash and newlines) with the most overlap, and inside it the
  words from the first to the last aligned word. A "not" in another clause of a long memory is no conflict.
- A page sentence that is a truncated prefix of the memory's clause: a negation only in the memory's tail is no conflict.
- Real flips still flagged (`X is enabled` vs `X is not enabled`; a changed number that appears on both sides).
- Known gap, unchanged from 1.5.1: a changed version where the old and new numbers share digits (`1.5.1` -> `1.5.2`) is
  not flagged; `1.5.1` -> `2.0.0` is. Tests: 3 new in FileTests.

## v1.5.1 - 2026-11-11
Every tool now knows which role it plays, and a name is never borrowed from the user's own notes:
- Who am I (one rule, in the pointer block `connect` writes for all 26 tools, `connect --print`, and the base's
  AGENTS.md block): the tool's own identity (system prompt, SOUL.md / identity file, a project ROLE.md) wins;
  otherwise the ONE file in `agents/` whose `engines:` lists the tool's id gives its role and `name:`; zero or
  several matches = no personal name, a neutral helper that asks once which role it plays; never a name from
  `wiki/me/` or the user file. Fixes a coding CLI started outside the base calling itself by the twin's name.
- Role files: `engines: [tool-id, ...]` (several tools can play one role); the old single `engine:` line is still
  read (`engine: any` claims nothing). Templates ship `engines: []` and an empty `name:`.
- `lint`: an engine value that is not a tool id is a problem; one engine claimed by two roles is a warning.
- Upgrade: re-run `init` (AGENTS.md block) and `connect` (tool blocks); existing role files are left as they are.
- Watcher unit: `MemoryMax` 40M -> 160M. `watch --once` with filing peaks at about 67 MB on a real base, so the
  1.5.0 watcher was OOM-killed in a restart loop. A test runs `watch --once` on 50 collected items and checks the
  peak RSS leaves 2x headroom under the cap. The collect and tidy units have no memory cap.

## v1.5.0 - 2026-11-11
Memories from any tool reach the wiki at once, with no model, and a rare model pass keeps the pages clean:
- `brain.py file [--dry-run]` (also run by `collect` and by the watcher, right after collecting): each new collected
  item, or each memory of a list file (Hermes `§` sections, GEMINI.md bullets), is filed by code as one cited line
  under `## Collected` at the end of ONE existing page (source, date, origin id, link to the raw copy). Routing:
  same origin as an earlier item -> same page (old line struck through and kept); a link to a page; page names,
  titles and `aliases:` in the item's tags/name/description/title/first sentence, weighted by rarity, with a 2x
  margin; bm25 (names weighted) only breaks a tie between named pages. Not sure, or instruction-like text ->
  `wiki/unsorted.md`. Never creates pages, never rewrites prose. Same text -> skipped; text a page already holds
  -> skipped; a changed number or a negation against a page sentence -> filed and listed under `## Conflicts`.
  Secrets redacted, `[[`/`<!--`/`TODO` neutralised; the raw item is recorded as done (`status` stops listing
  it); `index` + `map` after; the wiki lock and atomic writes. Ledger: `.brain/filed.json`.
- `brain.py tidy [--harness NAME] [--model M] [--tier cheap|mid] [--dry-run] [--force] [--check] [--save]
  [--harnesses]`: the rare LLM pass. A free trigger check first (10 lines waiting, 5 on a page, a line older than
  7 days, a conflict older than 2 days, an unsorted line older than 3 days; never with nothing pending; once per
  24 h unless `--force`). It runs ONE agent CLI the user has (`--harness`, a saved choice, else the first installed
  of claude, codex, gemini, qwen, hermes; UNVERIFIED rows only when chosen), headless in the base, writes scoped to
  the base, stdin closed, timeout, nesting markers scrubbed, one page per call (unsorted lines in batches of 8).
  After each call code checks: only `wiki/` changed (only that page for a page job), frontmatter kept, no new lint
  problem, no secret, every removed line already said or now on a page. A failed check puts the page back and
  retries once on the mid model; a page failing on both is skipped until its lines change (NEEDS YOU in
  `--check`). Mid model by default; conflicts and `wiki/unsorted.md` always mid. Logged in `.brain/tidy.log`
  (tokens and cost when the tool reports them) and `progress/agents.log`; merged pages are committed in a git base.
  The table of headless commands (`HEADLESS`) sits next to `TOOLS`; README table generated (`tidy --harnesses`).
- `connect --timer` (and `--watch`) also writes `skeleton-base-tidy.service` + `.timer` (check every 6 h);
  `disconnect` removes them. The watcher starts the tidy service when a tidy is due (at most once an hour).
- `lint` warns when a page has more than 15 filed lines waiting, or `wiki/unsorted.md` has a conflict older than
  7 days. `search` (and the MCP `search` tool) rank a hit in a page's name, title or aliases above body hits.
- Lab on a real base (61 hand-labelled memories, incl. Darija aliases, hub pages, duplicates, edits, a
  contradiction, an injection line and a fake key): 40 right page, 0 wrong page, 13 to unsorted, 8 correctly
  skipped. Blind judge (Opus, X/Y in random order) on the same 49 items: `file` + `tidy` (mid) 36-39 / 50 against
  25-31 for one LLM ingest of everything; cheap model 33-35, so mid is the default. Real `tidy` runs: Claude Code
  and Hermes pass; Codex and Gemini CLI not run (usage limit, daily quota).
- Tests: 22 new (150): routing cases, dedupe/update/conflict, redaction, injection stays inert, list splitting,
  collect files at once, dry run, lint warnings, search ranking, tidy triggers, harness pick/override/saved/
  UNVERIFIED, merge + log + commit + rate limit, put back + mid retry, every failure kind byte-identical, stuck
  pages skipped, unsorted batches, mid for conflicts, env scrub, no yolo flags, watch starts the tidy service and
  connect/disconnect leave the home as it was.

## v1.4.1 - 2026-11-11
Fixes found by real runs of real tools (Claude Code, Hermes, Qwen Code, each in a fresh temporary home):
- The pointer block's save step: run the `brain.py index` command on its own (the exact form tools allow) and add
  the log line with the file tools. Claude Code chained both in one shell command, which its allow rule did not
  match, so the step was refused.
- "Remember ..." is named as durable knowledge that goes into the base first (facts about the user: the fitting
  page of `wiki/me/`), then a short copy in the tool's memory. Qwen Code on a Gemini model had saved only to its own
  memory; after the change it saved to both.
- `collect` skips empty memory files (a fresh, empty `MEMORY.md` index was collected as an item with no content).
- Tests: the Hermes-only Frugal-Bridge test makes an installed Hermes (its `config.yaml`) instead of relying on a
  real `hermes` on PATH; 3 new tests (128).

## v1.4.0 - 2026-11-11
- Every known harness, one row each (26: Claude Code, Codex and the ChatGPT desktop app, Gemini CLI, Qwen Code,
  opencode v1/v2, Kilo Code, Grok Build, Copilot CLI, OpenClaw, Hermes, Crush, Goose, Amp, Aider, Factory Droid,
  Warp, Cursor, Devin Local/Desktop, Windsurf Cascade (legacy), Kiro, Cline, Roo Code (discontinued: detected
  only), Continue, Zed, Junie, the Claude app). For each: where it finds the base, how it reads and writes it from
  any folder, which of its memories are collected, how it takes the MCP server, and what needs you. The README
  matrix is generated from that table (`connect --matrix`; a test keeps them equal), `connect --print` lists it
  with your base path.
- The pointer block goes into ONE file each tool loads: its own rules folder where it has one
  (`~/.grok/rules/`, `~/.copilot/instructions/`, `~/.continue/rules/`, `~/Documents/Cline/Rules/`, Kiro steering),
  a shared file once for all its readers (`~/.agents/AGENTS.md`: Warp CLI, Droid, Cline; `~/.config/AGENTS.md`:
  Crush, Amp), and no second copy for Kilo and Devin, which already load `~/.claude/CLAUDE.md`. A block that moved
  to a shared file is taken out of the member's own file. Codex: `AGENTS.override.md` when it has text. Qwen:
  `QWEN.md`, not `rules/*.md` (HTML comments are stripped there). Aider: `read:` in `~/.aider.conf.yml` names
  `~/.config/skeleton-base/AGENTS.md`. Blocks of tools no longer found are kept current, never re-added.
- Size check: a WARNING when a rules file is over what the tool loads (Codex 32 KiB with the project's files,
  warned over half; Hermes and OpenClaw 20,000 characters; Droid 80,000).
- Install detection: the tool's own config file (not one we created), or its program on `PATH` plus its folder.
  A shared folder alone is not a tool: `~/.gemini` made by Antigravity no longer counts as Gemini CLI.
- Read + write from any folder through each tool's own user-level setting: Kilo `permission.external_directory`,
  Grok `read_write` of your custom sandbox profile, Droid `sandbox.filesystem.allowWrite`, Cursor `sandbox.json`
  and `cli-config.json`, Devin `permissions.allow`, Kiro `permissions.yaml`, Continue `permissions.yaml`, Junie
  `allowlist.json`; opencode v1 (`permission`, its default asks) and v2 (`permissions` list) told apart from the
  file or `opencode --version`. Format-aware writers: JSONC (comments, trailing commas, layout kept), TOML (checked
  text inserts), YAML (one safe line under a top-level key, else a note). Every entry recorded; `disconnect` gives
  the exact old bytes back, or takes out only our entries when the file changed (also after another program
  reformatted it). Records from 1.3.5 are still undone the old way.
- Memories collected from Qwen's auto-memory (`~/.qwen/projects/*/memory`, `~/.qwen/memories`), Kilo
  (`~/.local/share/kilo/memory`), Goose's Memory extension, Grok (`~/.grok/memory`), Codex `memories_v2`, OpenClaw
  `DREAMS.md`; the watcher watches them too, and wakes up when a tool's config file appears.
- `brain.py mcp`: the base as an MCP server (stdio, JSON-RPC 2.0, standard library): `recent`, `search`,
  `list_pages`, `read_page` (inside the base only: no absolute paths, `..`, hidden files or links out; 256 KB at
  most), `save_note` (a NEW note in `raw/inbox/mcp/` with a DATA header, never overwrites; size and count
  limits); `--read-only`. `connect --mcp` registers it in each tool's MCP config (Claude Code `~/.claude.json`,
  Codex/ChatGPT app `config.toml`, Gemini, Qwen, Cursor, Kiro, Junie, Cline, Copilot, Droid, Amp, Zed, Kilo,
  opencode, Hermes, Goose, the Claude app); tools that import Claude's servers (Devin, Grok, Warp) are not given a
  second copy. Remote use (Claude Duet, web apps) is documented, not automated (it needs a tunnel you trust).
- The base's skills are installed once in `~/.agents/skills/` (plus a `base-home` skill naming the base: Cursor
  finds the base this way), recorded, removed by `disconnect`; a skill of yours with the same name is never
  overwritten.
- Hooks run by other tools (Grok, Cursor, Devin, Continue cn, Copilot read `~/.claude/settings.json`): tested safe
  to run twice, at once, from another folder, with other payloads (exit 0, no output, each item once).
- Tests: 18 new (125): writers, every tool at once (connect --mcp, idempotent, byte-identical disconnect),
  changed-after-connect, shared files, detection, size caps, opencode versions, hooks run twice, a real JSON-RPC
  session over stdio, path traversal and limits, read-only mode, README matrix. Tests now run with a PATH that
  holds only fake programs, so the tools installed on the test machine no longer change the results.

## v1.3.5 - 2026-11-11
- Any tool can read and write the base from any folder. `connect` (and the watcher's auto-connect) adds the base
  to each tool's own user-level allow list: Claude Code `permissions.additionalDirectories` (plus a
  `permissions.allow` rule for `python3 BASE/tools/brain.py *`, so `index` runs from any folder), Codex
  `[sandbox_workspace_write] writable_roots` (a text insert in `~/.codex/config.toml`, checked by parsing: every
  other byte kept; a permission profile or a file it cannot merge safely gets a note instead), Gemini CLI and Qwen
  Code `context.includeDirectories`, opencode an `external_directory` allow rule where its `opencode.json` has
  rules. Merged by key, idempotent, recorded in `kits.base-folder.connect` (`hooks` for Claude Code, `access` for
  the others); an entry that was already there is never duplicated nor removed. `disconnect` removes only our
  entry (and keys we created that are empty again) and gives the exact old bytes back when the file did not change.
  Before, Claude Code started in another folder was denied reading the base.
- The pointer block has an Access section: the base is outside your project; if your tool blocks it, ask the user
  to allow it (the exact setting of each tool). The index command in it is one plain command
  (`python3 BASE/tools/brain.py index`) so the allow rule matches it. `connect --print` also lists the tools that
  have no such wall or setting.
- README: a tool x (finds, reads, writes, collected) matrix with evidence, and why the base works with any
  provider (no step needs a model).
- Tests: 9 new (107): each tool's setting (merge, idempotent, give back, changed-after-connect, bad files left
  alone), coexistence with Frugal-Bridge hooks in one `settings.json`, the block for unknown tools, the matrix.

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
