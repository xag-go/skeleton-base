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
- Remove: `python3 skeleton-base-kit/tools/brain.py uninstall ~/my-base` (see below: it keeps your data).

## Uninstall keeps your data

Removing Skeleton Base never deletes anything of yours.

1. **A full backup comes first.** `uninstall` writes the whole base (every file, dotfiles, `.git`) to
   `~/skeleton-base-backups/NAME-YYYYmmdd-HHMMSS.tar.gz` (mode 600, folder 700), outside the base, reads it
   back to check it, and prints its path plus a one-line restore command
   (`mkdir -p PARENT && tar -xpzf ARCHIVE -C PARENT`, file modes kept). If the backup cannot be written, nothing is uninstalled.
   `--backup-dir DIR` picks another folder (never inside the base); `--no-backup` skips it, only when you say so.
2. **Only unmodified kit files go.** A file init copied is removed only when it is still byte-identical to what
   init wrote. Everything else stays where it is: your wiki pages, `raw/` (also `raw/inbox/collected/`),
   board cards, agents, `hot.md`, `progress/agents.log`, templates and maps you edited, `.brain/` (collector
   state, `manifest.json`, `watch.json`, backups), the git repository with its history, and any file of a type
   the kit does not know.
3. **Shared files lose only our marked block.** `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.gitignore`: your text
   outside the block stays byte for byte; if you wrote inside our block, a copy of the file is kept in
   `.base-folder/backup/`. `.claude/settings.json` and `.gemini/settings.json` lose only the keys init added;
   when that leaves your original settings, your original bytes (layout too) are put back.
4. **Generated maps.** `maps/brain.canvas` / `maps/brain.html` are removed only when they are exactly what `map`
   last wrote (recorded in `.brain/map.json`). A map you changed (e.g. nodes moved in Obsidian) is yours: `map`
   and `init` leave it alone too, and `map --force` keeps a copy in `.brain/backups/` before replacing it.
5. **Only run-time files of the kit are deleted:** `.brain/search.db` (rebuilt from your files by `search`),
   lock files, `.brain/kick`, `.brain/pycache/`.
6. **At the end it prints what was kept and where** (per folder, with the number of git commits), and that the
   folder is plain Markdown: any AI tool can open it as it is, and `init` on it again adopts your files (never
   overwrites them, no duplicates: collected items are not collected twice, your edited map is left alone).

If Frugal-Bridge is installed, your profile, now, decisions and map are exported back to its plain files first.
`disconnect` only touches files in your home folder (its own pointer blocks, hooks, units, pointer file); in the
base it only updates its record in `.kits.json`.

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
- opens each tool's own folder wall for the base, so its agent can read **and write** the base from any folder
  (next section). One entry per tool, merged by key, recorded; `disconnect` removes only that entry and gives the
  exact old bytes back when nothing else changed in the file.
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
block and the Claude Code hooks are shell-quoted (`python3 '/home/me/My Base/tools/brain.py' index`), and the systemd units quote
and escape `ExecStart=` the way systemd reads it (`%` -> `%%`, `$` -> `$$`, `\` and `"` escaped). A path with a
line break is refused for the units.

### Any tool, any provider: what connect does for each

Four things must hold for a tool to use the base: (a) it finds the base (the pointer block is in a rules file it
loads in every session), (b) it can read the base, (c) it can write the base (the Saving knowledge rule: both its
own memory and the base), (d) what it remembers on its own is collected into the base. Tools that keep their agent
inside the folder it started in get the base added to their own user-level allow list:

| tool | (a) finds it | (b) read + (c) write | (d) memory collected | evidence |
|---|---|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` | `permissions.additionalDirectories: [BASE]` and `permissions.allow: ["Bash(python3 BASE/tools/brain.py *)"]` in `~/.claude/settings.json` [1] | `.claude/projects/*/memory/*.md` | tests `AccessTests.test_claude_*`, `FrugalGlobalTests.test_claude_access_entry_next_to_frugal_hooks_in_one_settings_file`; real `claude -p` from `/tmp`: answered from the base and wrote a page + ran `index` (acceptEdits) |
| Codex | `~/.codex/AGENTS.md` | reads anywhere in its sandbox; writes: `[sandbox_workspace_write] writable_roots = [BASE]` in `~/.codex/config.toml` (text insert, every other byte kept) [2]. With a permission profile (`default_permissions`) it prints the line to add instead | `.codex/memories/**/*.md`, `.codex/memories_*.sqlite` | `AccessTests.test_codex_*`; real `codex sandbox` from `/tmp` (workspace-write): read and wrote the base, a write next to it was refused |
| Gemini CLI | `~/.gemini/GEMINI.md` | `context.includeDirectories: [BASE]` in `~/.gemini/settings.json` [3] | `GEMINI.md` (its saved memories), `**/memory*.md` | `AccessTests.test_gemini_and_qwen_include_directories` |
| Qwen Code | `~/.qwen/QWEN.md` | `context.includeDirectories: [BASE]` in `~/.qwen/settings.json` [4] | `QWEN.md` | same test |
| opencode | `~/.config/opencode/AGENTS.md` | lets agents out by default; where `opencode.json` has rules: an `external_directory` allow rule for `BASE/**` (V2 `permissions` list, last rule wins; V1 `permission.external_directory` object) [5] | no memory store of its own: the block makes it save in the base | `AccessTests.test_opencode_*` |
| OpenClaw | `~/.openclaw/workspace/AGENTS.md` (when it exists) | no wall: its sandbox is off by default [6]; if you turn it on, bind the base into it | `MEMORY.md`, `USER.md`, `memory/*.md` | `CollectTests`, matrix test |
| Hermes | `~/.hermes/SOUL.md`, `profiles/*/SOUL.md` (when they exist) | no wall: its file tools reach any path you can | `memories/*.md`, `memory_store.db` (facts) | matrix test; real `hermes chat -q` from `/tmp` answered from the base |
| Windsurf | `~/.codeium/windsurf/memories/global_rules.md` | no file setting known: it asks, or add the base to the workspace | its memories are not plain files: not collected (the block makes it save in the base) | matrix test (a) |
| Kiro | `~/.kiro/steering/skeleton-base.md` | no file setting known: add the base to the workspace when it asks | none of its own | matrix test (a) |
| Cursor | needs you: paste `connect --print` into its User Rules | no file setting known: add the base to the workspace | not collected | listed as needs-user |
| any AI-like tool (a folder in your home with `AGENTS.md`/`NAME.md` rules or a `memory` store) | its rules file, when it has one (else listed as needs-user) | the block gives the absolute path and says: if your tool blocks it, ask the user to allow it (with the exact setting of each tool above) | its memory folder is watched and collected | `ZeroTouchTests`, `AccessTests.test_pointer_block_tells_any_tool_how_to_get_access` |

Matrix test: `AccessTests.test_every_known_tool_is_found_readable_writable_and_collected` (fake HOME, every tool
at once, then `disconnect` gives the home back byte-identical). `connect --print` prints the block and the notes.

**Any provider.** Nothing in the base needs a model: `init`, `connect`, `collect`, `watch`, `map`, `lint`,
`index`, `check` are plain Python with no network call and no model or provider name. The pointer block and
`AGENTS.md` are plain instructions any model follows; the optional AI steps (`skills/base-ingest`,
`skills/base-lint`, the interview) work with whatever model your tool runs. So the same tool on another provider
(Claude Code through another Anthropic-compatible endpoint, Hermes or opencode on OpenRouter or a local model)
loads the same rules file and the same settings: what the table says holds, because none of it depends on the
model. Tested here: Claude Code (Anthropic) and Hermes (its configured provider) for real; other providers are not
tested here, by design they change nothing above.

Sources: [1] code.claude.com/docs/en/permissions (Working directories, additionalDirectories);
[2] developers.openai.com/codex/config-reference (`sandbox_workspace_write.writable_roots`) and
developers.openai.com/codex/concepts/sandboxing; [3] github.com/google-gemini/gemini-cli
`docs/reference/configuration.md` (`context.includeDirectories`); [4] github.com/QwenLM/qwen-code
`docs/users/configuration/settings.md`; [5] opencode.ai/docs/permissions and opencode.ai/v1/docs/permissions
(`external_directory`); [6] docs.openclaw.ai/gateway/sandboxing ("Sandboxing is off by default").

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
  it looks there first) and its `install --global --hosts <its tools>` is re-run, so it works on its own file
  again. Every re-run names Frugal-Bridge's own tools (also those waiting for a rules file), never more.
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
