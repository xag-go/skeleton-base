# Skeleton Base

A personal knowledge base ("second brain") as a plain folder of Markdown files. Any AI tool can continue
your work from it: it reads one short rules file, then only what the task needs. No app, no server,
no account, no lock-in. Python 3.10+ standard library only.

## What is inside

```
AGENTS.md            rules for every agent (one marked block; other tools may add their own blocks)
CLAUDE.md, GEMINI.md one line: @AGENTS.md (makes those tools load AGENTS.md)
.claude/settings.json lets Claude Code run tools/brain.py in the base
.gemini/settings.json tells Gemini CLI to read AGENTS.md
hot.md               about 12 lines: what matters now. Agents read this first.
wiki/                knowledge written from your sources
  index.md  log.md  glossary.md
  me/                who you are, your goals, how to talk to you
  projects/ clients/ people/ decisions/ concepts/ daily/ sops/
raw/                 your original sources (read-only for agents): inbox, docs, references, clients, videos, exports
board/               your task board: one card = one .md file; board.base = Obsidian view grouped by status
agents/              role templates (assistant, twin) with what each may do, must ask, must never do
progress/agents.log  one line per job, written by every agent
maps/                JSON Canvas maps (open in Obsidian)
templates/           person, client, project, decision, daily, source, card
skills/              base-ingest, base-lint (Agent Skills format: works in any tool that reads SKILL.md)
tools/brain.py       checks and helpers (no AI)
.kits.json           which kits are installed here and where shared files live
```

## Three ways any tool uses it

1. **Files.** Open the folder in a tool that reads files (Claude Code, Codex, Gemini CLI, Cursor, OpenClaw,
   Hermes, ...). It loads `AGENTS.md` and follows the read order: `hot.md`, then `wiki/index.md`, then only the
   pages it needs.
2. **MCP, read-only.** For cloud assistants without file access, serve the folder through any read-only
   Markdown/filesystem MCP server. Pages become resources; the agent follows the same read order.
3. **Paste.** For chat apps and bots with no tools at all, run `python3 tools/brain.py brief` and paste the
   output (rules + hot.md + index + roles + your profile, about 1-2k tokens) as the project instructions.

Roles are fixed and engines are swappable: `agents/assistant.md` says what the assistant may do, whichever tool
plays it. Change the `engine:` line and nothing else changes.

## Setup

```sh
git clone <this repository> skeleton-base-kit
python3 skeleton-base-kit/tools/brain.py init ~/my-base
```

- Installs the whole skeleton (no menu). Re-running it changes nothing.
- An existing folder is fine: your files are never overwritten; shared files (`AGENTS.md`, `CLAUDE.md`,
  `GEMINI.md`, `.gitignore`) only get a marked block, `.gemini/settings.json` only gets its keys merged.
- It asks one question: also install Frugal-Bridge (a separate token-saving kit)? It never bundles it; if you
  say yes it prints the command for Frugal-Bridge's own setup. Non-interactive: `--frugal=no` or `--frugal=yes`.
- If Frugal-Bridge is already installed there, its USER / PROGRESS / DECISIONS / MAP files and `sources/` are
  imported into the base (originals kept in `raw/exports/frugal-DATE/`, one-line stubs left behind).
- Then ask your AI tool: "interview me and fill wiki/me/, one question at a time".
- Remove: `python3 skeleton-base-kit/tools/brain.py uninstall ~/my-base` removes only what init added and you
  did not change. If Frugal-Bridge is installed, your profile, now, decisions and map are exported back to its
  plain files first.

## Daily commands (run inside the base)

```sh
python3 tools/brain.py status          # raw files not yet ingested / changed
python3 tools/brain.py done raw/docs/x.md wiki/concepts/x.md   # record an ingest
python3 tools/brain.py lint            # frontmatter, sources, links, orphans, TODO, quotes, board, maps, skills
python3 tools/brain.py index           # rebuild the page list in wiki/index.md
python3 tools/brain.py map             # redraw the mind map: maps/brain.canvas and maps/brain.html
python3 tools/brain.py search "project-a deadline"
python3 tools/brain.py brief           # paste bundle for chat apps (--short leaves out wiki/me/)
python3 tools/brain.py check           # AGENTS.md size (warn 24 KiB, fail 32 KiB), pointer files, settings
python3 tools/brain.py collect         # copy new items from your tools' own memories into raw/inbox/collected/
```

Lint checks structure and quotes, not truth: a wrong source still gives a faithfully wrong page.

## Saving knowledge

`AGENTS.md` tells every agent: durable knowledge (facts, decisions, people, clients, project status) is saved in
this base, not only in the tool's own memory. Client -> `wiki/clients/`, decision -> `wiki/decisions/DATE-SLUG.md`,
person -> `wiki/people/`, project status -> `wiki/projects/` (and `hot.md` if it matters now), then
`python3 tools/brain.py index` and one line in `progress/agents.log`. A short copy in the tool's own memory is fine;
both should have it. `init` also lets Claude Code run `python3 tools/brain.py ...` in the base without asking
(one entry merged into `.claude/settings.json`, removed again by `uninstall`).

## Collect: the base grows with every tool's memory

Tools keep their own memories too. `collect` copies NEW items from them into `raw/inbox/collected/SOURCE/`, so
nothing learned in one tool is lost to the others. Every store is opened read-only (SQLite in `mode=ro`); a
missing store or an unknown database layout is skipped with a note, never an error.

| source | where (under your home folder) |
|---|---|
| `claude-code` | `.claude/projects/*/memory/*.md` |
| `codex` | `.codex/memories/**/*.md`, `.codex/memories_*.sqlite` (table `stage1_outputs`) |
| `gemini` | `.gemini/GEMINI.md` (without the base's own block), `.gemini/**/memory*.md` |
| `qwen` | `.qwen/QWEN.md` (without the base's own block) |
| `hermes` | `.hermes/memories/*.md`, `.hermes/profiles/*/memories/*.md` |
| `hermes-facts` | `.hermes/memory_store.db`, `.hermes/profiles/*/memory_store.db` (table `facts`) |
| `openclaw` | `.openclaw/workspace/MEMORY.md`, `USER.md`, `memory/*.md` |
| any name | every location added with `watch --add` (see below) |

```sh
python3 tools/brain.py collect --baseline     # first run on a filled base: remember what exists, write nothing
python3 tools/brain.py collect                # later: only new or changed items become files
python3 tools/brain.py collect --only codex,hermes-facts --since 2026-11-01
```

Each file is named `YYYYMMDD-SLUG-HASH8.md` and starts with a "DATA, not instructions" header and its origin.
Duplicates are skipped by content hash (`.brain/collector.json`). `lint` lists them as new raw files until you
ingest them (`skills/base-ingest`). Paths come from `$HOME`; the default base is the one holding this `brain.py`
(`--base DIR` for another).

## Connect: every tool on this computer knows the base

```sh
python3 tools/brain.py connect            # add --timer for a daily systemd user timer, --watch: see below
python3 tools/brain.py disconnect         # remove exactly what connect wrote
python3 tools/brain.py connect --print    # only print the pointer block (for a tool you set up by hand)
```

For the current user, `connect`:
- writes a marked pointer block (`<!-- base-folder:start v2 -->` ... `<!-- base-folder:end -->`) into the global
  rules file of every installed tool (its folder exists). It says where the base is, to read `hot.md` then
  `wiki/index.md` only when owner context is needed (never for plain coding), never to edit `raw/`, and the Saving
  knowledge rule. An older block is replaced in place; all other text stays byte-identical.

  | tool | file | |
  |---|---|---|
  | Claude Code | `~/.claude/CLAUDE.md` | created if missing |
  | Codex | `~/.codex/AGENTS.md` | created if missing |
  | Gemini CLI | `~/.gemini/GEMINI.md` | created if missing |
  | Qwen Code | `~/.qwen/QWEN.md` | created if missing |
  | opencode | `~/.config/opencode/AGENTS.md` | created if missing |
  | Windsurf | `~/.codeium/windsurf/memories/global_rules.md` | created if missing |
  | Kiro | `~/.kiro/steering/skeleton-base.md` | its own steering file |
  | OpenClaw | `~/.openclaw/workspace/AGENTS.md` | only if it exists (OpenClaw seeds it on first run) |
  | Hermes | `~/.hermes/SOUL.md`, `~/.hermes/profiles/*/SOUL.md` | only if it exists: it is the agent's identity, the only context file Hermes loads globally; creating one would replace its default identity |
  | Cursor | - | needs you: global User Rules live in its app settings (`connect --print`) |

- merges two Claude Code hooks into `~/.claude/settings.json` (`SessionEnd`, `PreCompact`) that run
  `collect --quiet`. Other hooks and keys are kept; a backup goes to `.brain/backups/`.
- with `--timer`: writes `~/.config/systemd/user/skeleton-base-collect.service` and `.timer` (daily and 10 minutes
  after boot, `Persistent=true`) and prints the command to enable it:
  `systemctl --user daemon-reload && systemctl --user enable --now skeleton-base-collect.timer`.
- with `--watch`: the watch service as well (next section); with `--kick`: a Claude Code `PostToolUse` hook.
- writes the base's pointer file `~/.config/skeleton-base/base`: one line, the base folder (no quoting). Other
  kits read it to find the base when no tool rules file carries the pointer block (a home whose only tool is Hermes
  without a `SOUL.md`, for example). If another base wrote it before, its bytes are backed up and given back on
  `disconnect`.

Everything written is recorded in `.kits.json` (`kits.base-folder.connect`); `disconnect` (and `uninstall`)
remove exactly that and give the previous text back, including an older pointer block it replaced.

**Base paths with spaces** work everywhere `connect` writes the path. A plain path is written as it is
(`Path: /home/me/base`). A path with a space, a quote, a backslash, a backtick or `$` is wrapped in the first of
`"` `'` `` ` `` that it does not contain, with no escaping inside (`Path: "/home/me/My Base"`). Shell commands in the
block and the Claude Code hooks are shell-quoted (`cd '/home/me/My Base' && ...`), and the systemd units quote
and escape `ExecStart=` the way systemd reads it (`%` -> `%%`, `$` -> `$$`, `\` and `"` escaped). A path with a
line break is refused for the units.

### With Frugal-Bridge installed for the whole user (`install --global`)

Frugal-Bridge is a separate kit. Installed for the user, it keeps one user file (`~/.frugal-bridge/USER.md`, or
`$FRUGAL_HOME/USER.md`) and a registry (`global.json`). The two work in any order:

- **Frugal first, base later.** `connect` (also the watcher's auto-connect) merges the filled lines of that
  `USER.md` into the base user slot (`wiki/me/`: language, answer style, what you decide alone and the main
  agent's name -> `how-to-talk-to-me.md`; your name and other lines -> `who-i-am.md`). It only fills empty fields or
  adds lines under `## From Frugal-Bridge USER.md`; it never overwrites. A line the base already has (duplicate) or
  says differently (conflict, the base keeps its line) goes on a board card
  `board/DATE-review-frugal-user-import.md`. The pages are backed up to `.brain/backups/frugal-import-TIME/` first,
  and what was imported is recorded in `.kits.json` (`kits.base-folder.frugal_user`): a re-run imports nothing
  new, a line you add to `USER.md` later is merged on the next connect. Then it runs Frugal-Bridge's own
  `kit/setup.py install --global` (found in `~/frugal-bridge`, or set `FRUGAL_BRIDGE_KIT`; skipped with a note if not
  found; with `--base <this base>` when its setup takes that flag). Frugal-Bridge finds the base from `--base`,
  the `Path:` line of the pointer block, the pointer file or the base's systemd units, and uses the base from then
  on. The old `USER.md` is left in place.
- **Base first, Frugal later.** Frugal-Bridge's setup sees the base and makes no `USER.md` of its own.
- **A tool installed later** (its folder appears after both kits are in place): the watcher's auto-connect writes
  the base block, then runs Frugal-Bridge's `install --global --hosts TOOL` for that tool alone, when Frugal-Bridge
  uses this base (`global.json` `base`), supports that tool (Claude Code, Codex, Gemini CLI, opencode, Hermes) and
  does not have it yet. The new tool gets both blocks, base first; the other tools' files are not touched.
- **Base path with spaces:** older Frugal-Bridge builds (without quoted `Path:` support) read the `Path:` line
  only up to the first space, so they cannot find a base whose path has one. `connect` then says so, and
  Frugal-Bridge keeps its own `USER.md` (both kits still work, but with two user files). A Frugal-Bridge that reads
  quoted `Path:` values follows the base like any other. With an older one, keep the base in a path without spaces
  if you use both.
- **Block order** in every user-level file: the base block first, Frugal-Bridge's block after it. When Frugal's
  block is already there, the base block is inserted in front of it; Frugal's bytes are never changed by the base.
- **`disconnect` / `uninstall`** while Frugal-Bridge uses the base: the user slot is written back to its `USER.md`
  (the old one is backed up to `FRUGAL_HOME/backup/skeleton-base-TIME/`). Everything Frugal-Bridge could find the
  base from goes first (pointer blocks, systemd units, the pointer file); then it is told to forget the base
  (`--no-base` when its setup takes it, otherwise the `base` entry it recorded in its `global.json` is dropped, since
  it looks there first) and its `install --global` is re-run, so it works on its own file again.
- Which of these a Frugal-Bridge build supports is read from its setup script (`frugal_caps` in `tools/brain.py`:
  quoted `Path:`, pointer file, systemd units, `--base`, `--no-base`), never from its version or its messages.

## Instant and zero-touch

`collect` on hooks and a daily timer is good; `watch` makes it instant. It is a small foreground daemon (standard
library, inotify through `ctypes`; it polls every 5 s where inotify is not available). On any change in a tool's
memory it waits until things are quiet (2 s, at most 10 s during a long burst), then in one run: auto-connects
tools that are new, collects, and if anything is new runs `index` and `map` and makes a git commit of exactly
those files (`raw/inbox/collected/`, `wiki/index.md`, `maps/brain.*`, `.brain/collector.json`,
`.brain/watch.json`, `.kits.json`). It never pushes.

```sh
python3 tools/brain.py connect --watch           # writes the service (+ the daily timer as a safety net)
systemctl --user daemon-reload && systemctl --user enable --now skeleton-base-watch.service skeleton-base-collect.timer
python3 tools/brain.py watch --list              # locations, and every tool: connected or needs-user
python3 tools/brain.py watch --add ~/.sometool/memory --source sometool    # watch and collect one more store
python3 tools/brain.py watch --remove ~/.sometool/memory
python3 tools/brain.py watch --discover          # suggest memory-like stores nothing watches yet (changes nothing)
python3 tools/brain.py watch                     # run it in the foreground instead (Ctrl+C stops it)
```

- **What it watches:** every location in the collect table, the locations you add (kept in `.brain/watch.json`;
  a running watcher reloads it at once), new folders in `~` and `~/.config`, and `.brain/kick`.
- **Any store you add:** a folder of Markdown / text files, one file, or a SQLite database. A database is opened
  read-only; every row's text columns become one item. Columns that change when a tool only reads (access
  counters, scores, timestamps of last use, embeddings) are left out, so reading is not news.
- **Zero-touch connect** (only once the base is connected: `connect` or `connect --watch`): when a known tool's
  folder appears (table above), it gets the pointer block like `connect` would write it, recorded for
  `disconnect` and backed up. An unknown folder that looks like an AI tool (an `AGENTS.md` or `NAME.md` rules
  file, a `memory` / `memories` folder, a `memory*.db`) gets the block in its existing rules file and its memory
  is watched and collected. If there is no rules file, its memory is still watched and the tool is listed as
  `needs-user` in `watch --list`. Folders that do not look like an AI tool are never touched. A watcher on a base
  that is not connected only collects. To keep a tool or file out, list it in `.brain/watch.json` as
  `"never": ["~/.hermes/profiles", "~/.kiro"]` (folders or globs under `~`); `connect` honours it too.
- **Self-healing:** a folder that does not exist yet is picked up when it appears, a deleted and re-created one
  too; a full rescan every 10 minutes catches anything missed.
- **Small:** ~19 MB of memory idle, 0 CPU while nothing changes. The service runs with `Nice=10` and
  `MemoryMax=40M`, `Restart=on-failure`.
- **Kick hook (optional):** `connect --watch --kick` adds a Claude Code `PostToolUse` hook (`Write|Edit`) that
  writes `.brain/kick` when a memory or rules file is saved. Any hook or script can do the same: write the file
  (a bare `touch` is not seen).
- **Undo:** `systemctl --user disable --now skeleton-base-watch.service`, then `disconnect`: every file connect
  and auto-connect wrote, the hooks and the service come back exactly as before.

## See your brain as a map

`python3 tools/brain.py map` draws the whole base as a mind map: you in the middle (`wiki/me/` and `hot.md`), one
branch per folder (projects, clients, people, decisions, concepts, sops, daily, plus the board and the agents),
one box or dot per page, and a line for every `[[link]]` between two pages. `init` draws it once; run `map` again
after you add pages.

- **In Obsidian:** open `maps/brain.canvas`. Each branch is a coloured group, each box shows the page itself.
  Obsidian's own graph view (Ctrl/Cmd+G) shows the same links as a moving cloud.
- **In any browser, no internet needed:** double-click `maps/brain.html`. Scroll to zoom, drag to move, click a
  dot to see its title, folder, last update, first lines and links; type in the search box to light up pages;
  click a folder in the legend to hide or show it. Everything is inside that one file; it loads nothing from the web.

Both files are generated: do not edit them, `map` rewrites them (it never overwrites a `maps/brain.*` file it did
not make unless you add `--force`). `lint` does not check them; it only reminds you to run `map` when the canvas
points to a page that no longer exists.

## Viewing it in Obsidian

Open the base folder as a vault. Pages, `[[links]]` and the graph work as is; `board/board.base` shows the board
(core Bases plugin), `maps/*.canvas` open as canvases (`maps/brain.canvas` is the mind map, see above). To sync to another machine, Syncthing works well; the
`.stignore` here keeps `.obsidian`, `.git` and generated folders out of sync.

## Updating

Pull the new version of this repository and run `init` on your base again. It replaces its own `AGENTS.md`
block, and updates skeleton files (tools, templates, skills) only where you never changed them. Your pages,
sources, cards and edited files are left alone. See `CHANGELOG.md`.

## Before you publish anything

Your filled base is private. If you fork this skeleton publicly, run
`python3 tools/brain.py check-public --words my-blocked-words.txt` first (keep that list outside the repo): it
fails on keys, emails, phone numbers and any word in the list, in file contents, paths and git history.

See `SECURITY.md`. License: MIT.
