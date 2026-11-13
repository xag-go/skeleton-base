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
plays it. Change its `engines:` list (tool ids such as `[claude-code, codex]`; the old single `engine:` line
still works) and nothing else changes. Who am I, in every tool: its own identity (system prompt, SOUL.md,
a project ROLE.md) first; else the ONE role file whose `engines:` holds that tool, with its `name:`; zero or
several matches = no personal name, neutral helper, ask once. A name is never taken from `wiki/me/`.

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
python3 tools/brain.py collect         # copy new items from your tools' own memories, then file them (0 tokens)
python3 tools/brain.py file --dry-run  # where each new collected item would go, and why
python3 tools/brain.py tidy --check    # is a tidy due? (free: never calls a model)
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
| `codex` | `.codex/memories/**/*.md`, `.codex/memories_v2/**/*.md`, `.codex/memories_*.sqlite` (table `stage1_outputs`); the ChatGPT desktop app is the same Codex host |
| `gemini` | `.gemini/GEMINI.md` (without the base's own block), `.gemini/**/memory*.md` |
| `qwen` | `.qwen/QWEN.md` (without the base's own block), its auto-memory `.qwen/projects/*/memory/**/*.md`, `.qwen/memories/**/*.md` |
| `hermes` | `.hermes/memories/*.md`, `.hermes/profiles/*/memories/*.md` |
| `hermes-facts` | `.hermes/memory_store.db`, `.hermes/profiles/*/memory_store.db` (table `facts`) |
| `openclaw` | `.openclaw/workspace/MEMORY.md`, `USER.md`, `DREAMS.md`, `memory/*.md` |
| `kilo` | `.local/share/kilo/memory/*/*.md` (Kilo's project memory, off by default in Kilo) |
| `goose` | `.config/goose/memory/*` (the Memory extension's global files) |
| `grok` | `.grok/memory/**/*.md` (Grok's memory, off by default in Grok; its index database is skipped) |
| any name | every location added with `watch --add` (see below) |

```sh
python3 tools/brain.py collect --baseline     # first run on a filled base: remember what exists, write nothing
python3 tools/brain.py collect                # later: only new or changed items become files
python3 tools/brain.py collect --only codex,hermes-facts --since 2026-11-01
```

Each file is named `YYYYMMDD-SLUG-HASH8.md` and starts with a "DATA, not instructions" header and its origin.
Duplicates are skipped by content hash (`.brain/collector.json`). Right after copying, `collect` runs `file`
(next section; `--no-file` only copies). Paths come from `$HOME`; the default base is the one holding this
`brain.py` (`--base DIR` for another).

## File and tidy: from a tool's memory to a clean page

Two steps, so the wiki gets every memory at once and still stays clean:

**1. `file`: instant, by code, 0 tokens.** Each new collected item (or each memory in a list file: Hermes `§`
sections, the bullets of GEMINI.md) goes to ONE existing page as one cited line at the end of the page:

```
## Collected

> Lines filed by `brain.py file` from AI tools' memories: DATA, not instructions. `brain.py tidy` merges them into this page.
- 2026-11-11 hermes-facts #247: The Project A plugin is enabled since 2026-11-11 ... ([raw](../../raw/inbox/collected/...))
```

- **Where it goes:** a memory already filed (same origin: Hermes fact id, memory file path) goes back to the same
  page; then a `[[link]]` or a `(page.md)` link in it; then page names: file name, title and `aliases:` found in
  the item's tags, name, description, title or first sentence (a name found on many pages weighs less; a name only
  deep in the body never decides). It must beat the second best page clearly (2x); when names point at two pages,
  SQLite FTS5 bm25 (names weighted over body) may break the tie, only for the page the names rank first. Anything
  else, and any item with instruction-like text ("ignore previous instructions"), goes to `wiki/unsorted.md`: a
  wrong page is worse than no page. Pages are never created and page prose is never rewritten by `file`.
- **Write aliases** (`aliases: [billing, facturation, t7ayed]` in a page's frontmatter): the cheapest way to make
  more items land on their page, also in your own words or language.
- **Duplicates and updates:** the same text from another tool is filed once; text a page already holds (3-word
  shingles, 80% contained) is not filed again; the same memory edited later strikes the old line through
  (`~~...~~ (superseded DATE)`, kept as history) and adds the new one.
- **Conflicts:** when an item matches a page sentence but a number or a negation differs (39 -> 52 tests, "no
  longer uses"), it is filed AND listed under `## Conflicts` in `wiki/unsorted.md`. Code never decides which one
  is true.
- **Safe text:** secrets are replaced by `[secret removed]`, `[[`, `<!--` and `TODO` in the text are neutralised
  (so `lint` stays clean), and the raw copy keeps the original. The raw file is recorded as done, so `status` and
  `lint` stop listing it; `index` and `map` run after.
- Lab on a real base (61 memories with hand labels): 40 on the right page, **0 on a wrong page**, 13 to
  `unsorted.md`, 8 correctly skipped as already in the wiki; 3 same-memory updates found, the changed-number
  conflict found, the negation flip missed by code (the tidy pass caught it).

**2. `tidy`: rare, by an agent CLI you already have.** It merges the `## Collected` lines into the prose, one page
per call, and settles the conflicts.

```sh
python3 tools/brain.py tidy --check                 # triggers only; never calls a model
python3 tools/brain.py tidy                         # runs only when a trigger is hit
python3 tools/brain.py tidy --force --dry-run       # which tool, which model, which pages; calls nothing
python3 tools/brain.py tidy --harness codex --save  # always use this tool (also --model M --tier cheap|mid)
python3 tools/brain.py tidy --harnesses             # the command used for each tool
```

- **When:** 10 lines waiting in total, or 5 on one page, or a line older than 7 days, a conflict older than 2 days,
  an unsorted line older than 3 days. Never when nothing waits; at most once per 24 h unless `--force`. `connect
  --timer` (and `--watch`) installs `skeleton-base-tidy.timer`, a check every 6 hours (free when nothing is due),
  and the watcher starts the tidy service after filing when a tidy is due (at most once an hour).
- **Which tool:** your choice (`--harness`, or saved with `--save` in `.brain/tidy.json`), else the first one
  installed in the table below. It runs in the base folder, headless, with writes limited to the base where the
  tool allows it (never a global "yolo" switch), stdin closed, a 15-minute timeout and the nesting markers of the
  calling agent removed from its environment. Rows marked UNVERIFIED are used only when you pick them.
- **Which model:** the mid model by default (the lab below: the cheap model left more contradictions unsettled);
  pages with a conflict and `wiki/unsorted.md` (moving lines, new pages) always use mid. `--tier cheap` or a
  saved tier uses the cheap model for plain merges.
- **Checked by code after each call:** only `wiki/` changed (and only that page, for a page job), frontmatter
  `title` and `scope` kept, `lint` has no new problem, no secret written, and every line that left `## Collected`
  either was already said on a page or has its words on the page now. A failed check puts the page back exactly
  as it was, then retries once on the mid model; a page that fails on both is skipped until its lines change
  (`tidy --check` shows it as NEEDS YOU). Each call is logged in `.brain/tidy.log` (tool, model, page, result,
  tokens and cost when the tool reports them), a line goes to `progress/agents.log`, and in a git base the merged
  pages are committed (never pushed).

<!-- tidy-harnesses:start -->
| Harness | Program | Auto-pick | Cheap / mid model | Command (scoped writes) |
|---|---|---|---|---|
| claude | `claude` | yes | haiku / sonnet | `claude -p PROMPT --permission-mode acceptEdits --allowedTools=Read,Edit,Write,Glob,Grep --disallowedTools=Bash --output-format json --no-session-persistence` (file tools only (no shell), edits auto-accepted in the base) |
| codex | `codex` | yes | its default / its default | `codex exec -C BASE -s workspace-write --skip-git-repo-check --ephemeral PROMPT` (sandbox: writes only inside the base) |
| gemini | `gemini` | yes | its default / its default | `gemini -p PROMPT --approval-mode auto_edit --skip-trust -o json` (edits auto-approved, shell still asks (so it is refused headless); model names change often, so it uses the model you set in Gemini CLI) |
| qwen | `qwen` | yes | its default / its default | `qwen PROMPT --approval-mode auto-edit -o json` (edits auto-approved, shell refused headless) |
| kilo | `kilo` | no (UNVERIFIED) | its default / its default | `kilo run PROMPT --auto --dir BASE` (UNVERIFIED (docs only): --auto runs only what its config allows) |
| opencode | `opencode` | no (UNVERIFIED) | its default / its default | `opencode run PROMPT` (UNVERIFIED: permissions come from its config) |
| droid | `droid` | no (UNVERIFIED) | its default / its default | `droid exec --auto low --cwd BASE PROMPT` (UNVERIFIED (docs only): --auto low = file edits + safe commands) |
| copilot | `copilot` | no (UNVERIFIED) | its default / its default | `copilot -p PROMPT -s --allow-tool=write --no-ask-user` (UNVERIFIED (docs only): writes limited to the working folder) |
| hermes | `hermes` | yes | its default / its default | `hermes chat -q PROMPT -Q -t file --in BASE --max-turns 60` (file toolset only; Hermes has no folder sandbox, so it is lower in the list) |
| openclaw | `openclaw` | no (UNVERIFIED) | its default / its default | `openclaw agent exec PROMPT --cwd BASE --json` (UNVERIFIED (docs only): permissions come from its config) |
| cursor-agent | `cursor-agent` | no (UNVERIFIED) | its default / its default | `cursor-agent -p PROMPT --workspace BASE --sandbox enabled --trust` (UNVERIFIED (docs only)) |
| kiro-cli | `kiro-cli` | no (UNVERIFIED) | its default / its default | `kiro-cli chat --no-interactive --trust-tools fs_read,fs_write PROMPT` (UNVERIFIED (docs only)) |
| cn | `cn` | no (UNVERIFIED) | its default / its default | `cn -p PROMPT --allow Write --allow Edit` (UNVERIFIED (docs only)) |
| junie | `junie` | no (UNVERIFIED) | its default / its default | `junie --project BASE PROMPT` (UNVERIFIED (docs only)) |
<!-- tidy-harnesses:end -->

**Lab (one real base, 49 collected items, a blind judge: Claude Opus scoring two results named X and Y in random
order, 0-10 on placement, no lost facts, no duplicates, conflicts, readability):**

<!-- tidy-lab:start -->
| result (same 49 items) | judge total /50 | tokens in / out | cost |
|---|---|---|---|
| one LLM ingest of everything (a nightly job, Sonnet) | 25, 29, 31 | 1.67 M / 22 k | 0.84 USD |
| `file` + `tidy`, cheap model for plain merges | 33, 35 | 2.90 M / 58 k (17 calls) | 1.67 USD |
| `file` + `tidy`, mid model (the default) | 36, 38, 38, 39 | 2.07 M / 37 k (17 calls) | 2.27 USD |
| `file` alone | - | 0 | 0 |

The one-run ingest appended "Update" blocks and repeated facts on several pages; `file` + `tidy` put the facts in
the right sections with fewer duplicates. Its weak point: an old sentence that says something else than a new
line (not a number or a negation) can stay next to it; `--check`, `lint` and `wiki/unsorted.md` show what waits.
Real runs: Claude Code and Hermes merged and passed every check; Codex and Gemini CLI were not run (usage limit,
daily quota): their failed calls changed nothing.
<!-- tidy-lab:end -->

## Connect: every tool on this computer knows the base

```sh
python3 tools/brain.py connect            # add --timer for a daily systemd user timer, --watch: see below
python3 tools/brain.py disconnect         # remove exactly what connect wrote
python3 tools/brain.py connect --print    # only print the pointer block (for a tool you set up by hand)
```

For the current user, `connect`:
- finds every installed tool it knows (the table below) and writes a marked pointer block
  (`<!-- base-folder:start v2 -->` ... `<!-- base-folder:end -->`) into ONE global rules file that tool loads in
  every session. It says where the base is, to read `hot.md` then `wiki/index.md` only when owner context is
  needed (never for plain coding), never to edit `raw/`, and the Saving knowledge rule. An older block is replaced
  in place; all other text stays byte-identical. Where a tool has a rules folder, the block gets its own file
  there (`~/.kiro/steering/skeleton-base.md`, `~/.grok/rules/`, `~/.continue/rules/`, `~/Documents/Cline/Rules/`,
  `~/.copilot/instructions/`), so no file of yours is edited.
- **Installed** means: the tool's own config file exists (one we did not create ourselves), or its program is on
  `PATH` and its config folder exists. A folder that another tool also makes is never enough on its own:
  `~/.gemini` is also made by Antigravity, so Gemini CLI needs the `gemini` program or its `settings.json`.
- **Loaded once per tool.** Some files are read by several tools: `~/.agents/AGENTS.md` (Warp Agent CLI, Factory
  Droid, Cline), `~/.config/AGENTS.md` (Crush, Amp) and `~/.claude/CLAUDE.md` (also loaded by Kilo when it has no
  `AGENTS.md` of its own, and by Devin unless `read_config_from.claude` is false). When the shared file is used
  (it exists, or Warp needs it), the block goes there once and not into the members' own files; a block written
  before into a member's own file is taken out again. Kilo and Devin get no second copy next to the one in
  `~/.claude/CLAUDE.md`. Codex: when `~/.codex/AGENTS.override.md` has text it hides `AGENTS.md`, so the block
  goes into the override file.
- **Size check.** Codex loads at most 32 KiB of AGENTS.md (its global file and the project's together), Hermes
  cuts a context file at 20,000 characters, OpenClaw at 20,000 per bootstrap file, Droid at 80,000: `connect`
  prints a `WARNING` when a file is over (for Codex: over half). Hermes `SOUL.md` and OpenClaw's workspace
  `AGENTS.md` are only added to when they exist (never created: SOUL.md is the agent's identity).
- adds the base to each tool's own user-level allow list, so its agent can read **and write** the base from any
  folder (column (b) below). JSON settings are edited as JSONC (comments, trailing commas and layout kept), TOML
  by a checked text insert, YAML only by safe line edits (one line under a top-level key; anything else gets a
  note telling you what to add by hand). Each entry is merged by key, recorded, and `disconnect` gives the exact
  old bytes back when nothing else changed in the file, or takes out only our entries when it did.
- installs the base's skills (`skills/base-*`) **once** in `~/.agents/skills/`, plus a `base-home` skill that says
  where the base is (Cursor has no rules file: it finds the base this way). Most tools read that folder (see the
  notes); a skill folder you already have under the same name is never overwritten.
- merges two Claude Code hooks into `~/.claude/settings.json` (`SessionEnd`, `PreCompact`) that run
  `collect --quiet`. Other hooks and keys are kept; a backup goes to `.brain/backups/`.
- with `--timer`: writes `~/.config/systemd/user/skeleton-base-collect.service` and `.timer` (daily and 10 minutes
  after boot, `Persistent=true`), plus `skeleton-base-tidy.service` and `.timer` (the tidy check every 6 hours),
  and prints the command to enable them:
  `systemctl --user daemon-reload && systemctl --user enable --now skeleton-base-collect.timer skeleton-base-tidy.timer`.
- with `--watch`: the watch service as well (next section); with `--kick`: a Claude Code `PostToolUse` hook.
- with `--mcp`: registers the base's MCP server (`brain.py mcp`, see below) in each tool's MCP config (column
  "MCP"). Once asked for, later connects and the watcher keep it; `disconnect` removes it.
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
loads in every session), (b) it can read and write the base (its own allow list, where it has a wall), (c) what it
remembers on its own is collected into the base, and, for apps that cannot read files, (d) the MCP server. One row
per tool; "needs you" says exactly what you set by hand, and `connect --print` prints the same list with your
base path in it. This table is generated (`python3 tools/brain.py connect --matrix`; a test checks it):

<!-- tools-matrix:start -->
| tool | (a) finds the base | (b) read + write | (c) memory collected | MCP (`connect --mcp`) | notes | source |
|---|---|---|---|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` | `permissions.additionalDirectories` + `Bash(python3 BASE/tools/brain.py *)` in `~/.claude/settings.json` | `~/.claude/projects/*/memory/*.md` | `mcpServers` in `~/.claude.json` (user scope) | its own: SessionEnd, PreCompact (+ PostToolUse with --kick); skills: reads only `~/.claude/skills`, not `~/.agents/skills` (not copied there: other tools read `~/.claude/skills` too and would load them twice); the base's AGENTS.md points to its `skills/` | code.claude.com/docs/en/memory, /permissions, /mcp, /hooks |
| Codex (CLI, IDE and the ChatGPT desktop app, one Codex host) | `~/.codex/AGENTS.override.md` if it has text, else `~/.codex/AGENTS.md` | `[sandbox_workspace_write] writable_roots` in `~/.codex/config.toml` | `~/.codex/memories/**/*.md`, `memories_v2/**/*.md`, `memories_*.sqlite` (off by default in Codex) | `[mcp_servers.skeleton-base]` in `~/.codex/config.toml` (shared by the desktop app) | none written (Codex hooks need your trust by hash); size check: Codex loads at most 32 KiB of AGENTS.md text, this file and the project's together (project_doc_max_bytes); skills: `~/.agents/skills` | learn.chatgpt.com/docs/agent-configuration/agents-md, /config-file/config-reference, /extend/mcp, /customization/memories |
| Gemini CLI | `~/.gemini/GEMINI.md` | `context.includeDirectories` in `~/.gemini/settings.json` | `~/.gemini/GEMINI.md` (its saved memories) | `mcpServers` in `~/.gemini/settings.json` | `~/.gemini` alone is not proof (Antigravity makes it too): the `gemini` program or its settings file must be there; skills: `~/.agents/skills` | github.com/google-gemini/gemini-cli docs/cli/gemini-md.md, docs/reference/configuration.md |
| Qwen Code | `~/.qwen/QWEN.md` | `context.includeDirectories` in `~/.qwen/settings.json` | `~/.qwen/QWEN.md`, auto-memory `~/.qwen/projects/*/memory/**/*.md`, `~/.qwen/memories/**/*.md` | `mcpServers` in `~/.qwen/settings.json` | the block goes in QWEN.md, not `~/.qwen/rules/` (rules files lose HTML comments, so the marked block could not be found again); skills: `~/.agents/skills` | github.com/QwenLM/qwen-code docs/users/features/memory.md, rules.md, configuration/settings.md |
| opencode (v1 and v2) | `~/.config/opencode/AGENTS.md` | v2: an `external_directory` allow rule in `permissions` (only where it has rules: v2 lets agents out by default); v1: `permission.external_directory` (its default asks) | none of its own | v2 `mcp.servers`, v1 `mcp` in `~/.config/opencode/opencode.json(c)` | skills: `~/.agents/skills` | opencode.ai/docs/permissions, /mcp-servers, /migrate-v1; opencode.ai/v1/docs |
| Kilo Code CLI | `~/.config/kilo/AGENTS.md`; else the block in `~/.claude/CLAUDE.md` (it loads that file) | `permission.external_directory` in `~/.config/kilo/kilo.jsonc` (its default asks) | `~/.local/share/kilo/memory/*/*.md` (off by default in Kilo) | `mcp` in `~/.config/kilo/kilo.jsonc` | without its own `~/.config/kilo/AGENTS.md` it loads `~/.claude/CLAUDE.md`: the block there reaches it; skills: `~/.agents/skills` | kilo.ai/docs (llms.txt: global rules, permissions, memory, MCP) |
| Grok Build | `~/.grok/rules/skeleton-base.md` | sandbox off by default (no wall); with a custom profile (`[sandbox] profile` in `~/.grok/config.toml`): its `read_write` in `~/.grok/sandbox.toml` | `~/.grok/memory/**/*.md` (off by default in Grok) | loads `~/.claude.json` servers; else `[mcp_servers.skeleton-base]` in `~/.grok/config.toml` | also runs the hooks in `~/.claude/settings.json` (ours are safe to run twice); skills: `~/.agents/skills` | docs.x.ai/build (features/project-rules, sandbox, mcp-servers, settings reference) |
| GitHub Copilot CLI | `~/.copilot/instructions/skeleton-base.instructions.md` | needs you: only per project (`--add-dir`, `/add-dir` or `permissions-config.json`) | server-side (GitHub): not a local file, not collected | `mcpServers` in `~/.copilot/mcp-config.json` | runs a repo's `.claude/settings*.json` hooks (ours are safe to run twice); skills: `~/.agents/skills` | docs.github.com copilot-cli (custom instructions, config dir reference, hooks) |
| OpenClaw | `~/.openclaw/workspace/AGENTS.md` (if it exists) | no wall (its sandbox is off by default) | `workspace/MEMORY.md`, `USER.md`, `DREAMS.md`, `memory/*.md` | needs you: `openclaw mcp` (config format not verified) | size check: OpenClaw injects at most 20,000 characters per bootstrap file; skills: `~/.agents/skills` | docs.openclaw.ai (agent workspace, memory, sandboxing) |
| Hermes Agent | `~/.hermes/SOUL.md` (if it exists), `~/.hermes/profiles/*/SOUL.md` (if it exists) | no wall (its file tools reach any path you can) | `memories/*.md`, `memory_store.db` facts, the same in every profile | `mcp_servers` in `~/.hermes/config.yaml` | reads `~/.agents/skills` only when it is in `skills.external_dirs`; size check: Hermes cuts a context file at 20,000 characters | hermes-agent source (agent/prompt_builder.py, hermes_cli/config_defaults.py) |
| Crush | `~/.config/crush/CRUSH.md`; `~/.config/AGENTS.md` when it is used (Crush and Amp both read it) | needs you: it asks per tool; there is no folder setting | none of its own | needs you: `mcp add` in its crushrc (syntax not verified) | skills: `~/.agents/skills` | github.com/charmbracelet/crush README, docs/config |
| Goose | `~/.config/goose/.goosehints` | no wall | Memory extension files `~/.config/goose/memory/*` | an `extensions` entry (type stdio) in `~/.config/goose/config.yaml` | skills: `~/.agents/skills` | github.com/aaif-goose/goose documentation (config-files, goosehints, memory-mcp) |
| Amp | `~/.config/amp/AGENTS.md`; `~/.config/AGENTS.md` when it is used (Crush and Amp both read it) | no wall | none local (threads are server-side) | `amp.mcpServers` in `~/.config/amp/settings.json` | skills: `~/.agents/skills` | ampcode.com/docs (agents-md, mcp, skills) |
| Aider | `read:` in `~/.aider.conf.yml` -> `~/.config/skeleton-base/AGENTS.md` | needs you: it edits only files in its git repo (start it in the base to edit it) | none | none (Aider has no MCP) | no rules file: connect adds `~/.config/skeleton-base/AGENTS.md` to `read:` in `~/.aider.conf.yml` (a repo `.aider.conf.yml` with its own `read:` replaces it) | aider.chat/docs/usage/conventions.html, /config/aider_conf.html |
| Factory Droid | `~/.factory/AGENTS.md`; `~/.agents/AGENTS.md` when it is used (Warp Agent CLI, Factory Droid and Cline all read it) | reads anywhere; writes: `sandbox.filesystem.allowWrite` in `~/.factory/settings.json` (used when its sandbox is on) | none of its own | `mcpServers` in `~/.factory/mcp.json` | reads `~/.factory/skills` (not `~/.agents/skills` as far as documented); size check: Droid loads at most 80,000 characters of AGENTS.md at start | docs.factory.com (harness/agents-md, autonomy-and-safety/sandbox, harness/mcp) |
| Warp (Agent CLI; the app's rules live in Warp Drive) | `~/.agents/AGENTS.md` when it is used (Warp Agent CLI, Factory Droid and Cline all read it) | no wall | cloud (Agent Memory preview): not collected | reads the Claude Code and Codex MCP configs | the app's global rules are cloud settings: paste `connect --print` there by hand; skills: `~/.agents/skills` | docs.warp.dev (agents, warp-agent-cli, mcp) |
| Cursor (editor and cursor-agent) | the `base-home` skill in `~/.agents/skills`; always-on: needs you (User Rules) | `additionalReadwritePaths` and `additionalReadPaths` in `~/.cursor/sandbox.json`; `Read(BASE/**)`, `Write(BASE/**)` in `~/.cursor/cli-config.json` when it exists | none (Memories were removed) | `mcpServers` in `~/.cursor/mcp.json` | User Rules are app settings, not a file: it finds the base through the `base-home` skill; for an always-on rule paste `connect --print` into Settings > Rules; runs the hooks in `~/.claude/settings.json` by default (ours are safe to run twice); skills: `~/.agents/skills` | cursor.com/docs (rules, reference/sandbox, cli/reference/permissions, context/mcp, skills, reference/third-party-hooks) |
| Devin Local / Devin Desktop / Devin CLI (formerly Windsurf) | `~/.config/devin/AGENTS.md`; else the block in `~/.claude/CLAUDE.md` (it loads that file) | `permissions.allow` `Read(BASE/**)`, `Write(BASE/**)` in `~/.config/devin/config.json` | none (Cascade memories are legacy) | imports `~/.claude.json`; else `mcpServers` in `~/.config/devin/mcp_config.json` | it loads `~/.claude/CLAUDE.md` unless `read_config_from.claude` is false: the block there reaches it; imports the hooks in `~/.claude/settings.json` (ours are safe to run twice); skills: `~/.agents/skills` | docs.devin.ai (cli/extensibility/rules, cli/reference/permissions, read-config-from, mcp) |
| Windsurf Cascade (legacy, now Devin Desktop) | `~/.codeium/windsurf/memories/global_rules.md` | no file setting | internal, not collected | - | - | docs.devin.ai/desktop/cascade (Cascade is the legacy agent) |
| Kiro (IDE and kiro-cli) | `~/.kiro/steering/skeleton-base.md` | `fs_read` and `fs_write` allow rules in `~/.kiro/settings/permissions.yaml` | Kiro Memory is opaque: not collected | `mcpServers` in `~/.kiro/settings/mcp.json` | reads `~/.kiro/skills` (not `~/.agents/skills`) | kiro.dev/docs (steering, permissions, mcp/configuration, memory) |
| Cline (VS Code, JetBrains, CLI) | `~/Documents/Cline/Rules/skeleton-base.md`; `~/.agents/AGENTS.md` when it is used (Warp Agent CLI, Factory Droid and Cline all read it) | needs you: only the all-or-nothing "Read all files" / "Edit all files" auto-approve, or add the base as a workspace folder | none native | `mcpServers` in `~/.cline/data/settings/cline_mcp_settings.json` | skills: `~/.agents/skills` | docs.cline.bot (customization/cline-rules, getting-started/config, features/auto-approve) |
| Roo Code (discontinued 2026-05-15) | detected only, nothing written | - | - | - | - | github.com/RooCodeInc/Roo-Code-Docs docs/sunset.md |
| Continue (extension and cn) | `~/.continue/rules/skeleton-base.md` | `Read(BASE/**)`, `Write(BASE/**)` in `allow` of `~/.continue/permissions.yaml` (cn) | none native | needs you: `mcpServers` in its config.yaml (a user-level block folder is not documented) | cn runs the hooks in `~/.claude/settings.json` (ours are safe to run twice); reads `.claude/skills` in the workspace only | docs.continue.dev (rules, cli/tool-permissions, mcp); continuedev/continue source |
| Zed (its own agent) | `~/.config/zed/AGENTS.md` | needs you: no extra-folder setting (add the base as a project folder) | none | `context_servers` in `~/.config/zed/settings.json` (comments kept) | skills: `~/.agents/skills` | zed.dev/docs/ai (instructions, mcp, tools, skills) |
| JetBrains Junie (CLI and IDE) | `~/.junie/AGENTS.md` | `readOutsideProject` and `fileEditing` allow rules in `~/.junie/allowlist.json` | none native | `mcpServers` in `~/.junie/mcp/mcp.json` | skills: `~/.agents/skills` | junie.jetbrains.com/docs (guidelines-and-memory, action-allowlist, junie-cli-mcp-configuration) |
| Claude app (desktop) | needs you (account Instructions); MCP server | through the MCP server: reads the base, saves notes to `raw/inbox/mcp/` | server-side (your account): not collected | `mcpServers` in `~/.config/Claude/claude_desktop_config.json` | rules and memory live in your account: paste `brief --short` into Settings > Instructions; with `connect --mcp` it reaches the base through the MCP server | modelcontextprotocol.io/docs/develop/connect-local-servers; support.claude.com |
<!-- tools-matrix:end -->

Any other AI-like tool (a folder in your home with `AGENTS.md`/`NAME.md` rules or a `memory` store) is found by the
watcher: its rules file gets the block when it has one (else it is listed as needs-user), and its memory folder is
watched and collected. The block names the absolute base path and says: if your tool blocks it, ask the user to
allow it. Evidence: `EveryToolTests` (every row above at once in a fake home with fake programs on `PATH`: (a),
(b), (c), MCP, one block per file, comments kept, a second `connect` changes nothing, `disconnect` gives the home
back byte-identical), `SharedFileTests`, `DetectionTests`, `WriterTests`, `ZeroTouchTests`, `AccessTests`. Real
runs: Claude Code (`claude -p` from `/tmp` answered from the base and wrote to it), Codex (`codex sandbox` from
`/tmp` read and wrote the base), Hermes (`hermes chat -q` from `/tmp`). The other rows are checked against their
docs (sources in the table) and in tests, not with the real program.

**Hooks run by other tools.** Grok Build, Cursor, Devin, Continue `cn` and Copilot CLI also run the hooks in
`~/.claude/settings.json` (or a repo's `.claude/settings.json`), with their own payloads. Ours are safe to run
twice and by anyone: `collect` takes a lock and skips every item it already has (by content hash), prints nothing
(hosts that parse hook output as JSON are not disturbed), ignores its input and always exits 0 or 1, never 2
(which would block the tool). Test: `HookTwiceTests` runs the hook five times at once with Claude, Cursor and
Devin payloads from another folder: every item is collected once.

**Any provider.** Nothing in the base needs a model: `init`, `connect`, `collect`, `file`, `watch`, `map`, `lint`,
`index`, `check`, `mcp` are plain Python with no network call and no model or provider name. `tidy` is the one
step that uses a model, through whichever agent CLI you have, on its own login and provider. The pointer block and
`AGENTS.md` are plain instructions any model follows; the optional AI steps (`skills/base-ingest`,
`skills/base-lint`, the interview) work with whatever model your tool runs. So the same tool on another provider
loads the same rules file and the same settings: what the table says holds, because none of it depends on the
model. Tested here: Claude Code (Anthropic) and Hermes (its configured provider) for real; other providers are not
tested here, by design they change nothing above.

### The MCP server: the generic door for any agent

`brain.py mcp` is the one door that works for every agent, whatever the tool or the model provider: any MCP client
(Claude Code, Codex, Gemini CLI, Qwen Code, opencode, Kilo, Hermes, Goose, Cursor, Copilot, Zed, the Claude app, an
agent you write yourself) starts it over stdio and gets the same five tools, with the same safety rules. It needs no
file access, no settings of its own and no trust in the agent: it reads only text inside the base (never
`engines/`, `projects/` or the other layout folders, never hidden files) and writes only NEW notes into
`raw/inbox/mcp/` (DATA for the next ingest). `connect --mcp` registers it in every tool it finds. A tool without
MCP still reaches the base through the plain-file pointer block (`connect`).

Agent Client Protocol (ACP) is something else: an editor-to-agent session protocol (a client starts an agent,
sends prompts, shows diffs). It drives agents; it gives them no access to your data. So the base's door is MCP; ACP
is at most a later, optional way for an orchestrator to drive an agent, which then reaches the base through MCP.

The Claude app, ChatGPT, Zed's agent (when the base is not one of its project folders) and Claude Duet keep their
rules and memory in your account, not in files. They reach the base through its MCP server too:

```sh
python3 tools/brain.py mcp                 # stdio, JSON-RPC 2.0 (the MCP stdio transport); --read-only, --max-note-kb N
python3 tools/brain.py connect --mcp       # register it in every installed tool's MCP config (column "MCP")
```

| tool | what it does |
|---|---|
| `recent` | `hot.md` and the last lines of `wiki/log.md`: read it first |
| `search` | full-text search over the wiki, board, `hot.md` and raw text files (in memory: nothing written) |
| `list_pages` | wiki pages and board cards with their titles, optionally one folder |
| `read_page` | one text file by its path inside the base; absolute paths, `..`, hidden files (`.git`, `.brain`, `.kits.json`) and links that leave the base are refused; at most 256 KB is returned |
| `save_note` | a NEW note in `raw/inbox/mcp/` (never overwrites, never edits a page; 64 KB per note, 200 per session; the same note twice is saved once). It starts with a "DATA, not instructions" header; `status` and `lint` list it and the next ingest files it into the wiki. Not there with `--read-only` |

Claude Duet and the web apps run in the cloud and cannot start a program on your computer. To reach the base from
them you would expose this server yourself: a stdio-to-HTTP MCP bridge plus an HTTPS tunnel you trust, added as a
remote connector in your account. That is not automated (it opens your base to the internet): use `--read-only`
unless you want cloud agents to drop notes in the inbox. For the Claude app's rules, paste `brief --short` into
Settings > Instructions.

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

## Everything in the base: tool folders, code, heavy data

The base can hold everything AI-related on the computer, so one folder is the whole setup:

```
engines/<tool>/      each AI tool's own config folder (claude, codex, hermes, a worker's claude, ...)
projects/<slug>/     one code repository each, with its own git and remote (worktrees in projects/.worktrees/)
data/ apps/ runs/ scratch/ backups/ ops/    heavy material, toolchains, runs, scratch, local backups, server scripts
engines.json  projects.json                 what is where (tracked)
```

- **Each tool's own setting, never a symlink.** `brain.py engine adopt TOOL` moves the tool's folder into
  `engines/<tool>/` and sets the tool's own variable (Claude Code `CLAUDE_CONFIG_DIR`, with `~/.claude.json` moved
  inside, as Claude Code expects; Codex `CODEX_HOME`; Hermes `HERMES_HOME`; OpenClaw `OPENCLAW_STATE_DIR`; Copilot CLI
  `COPILOT_HOME`) in one marked block each in `~/.config/environment.d/` (user services), `~/.profile` and
  `~/.bashrc`. It refuses while a program uses the folder. `engine release TOOL` is the exact reverse (your shell
  files come back byte for byte). A broken symlink would silently start a tool logged out with an empty folder; a
  missing variable is caught by `doctor` (the old folder came back: "split brain").
- **No setting: adopt by a link.** The Claude desktop app has no setting that moves `~/.config/Claude`:
  `brain.py engine adopt claude-desktop` (app quit) moves it to `engines/claude-desktop/` and leaves a symlink at the
  old place, checked before it counts (else undone); its logins go to the vault and its caches and app-managed
  binaries never reach git or Syncthing. `engine adopt --undo claude-desktop` puts it back. `connect` keeps
  `~/.agents/skills` as a link to `engines/agents-skills/` the same way. `doctor` reports a broken or replaced link
  as an ERROR with the fix.
- **Share one more sub-folder** of a tool folder (say a worker's built team in `engines/claude-worker/team`):
  `brain.py engine share claude-worker team` (`--remove` undoes it). The secret rules still win inside it; names
  like `auth`, `token`, `sessions` or `.git` are refused.
- **Secrets out of the base**: `brain.py engine vault claude-worker` moves the logins of a tool folder (credentials,
  `.claude.json`, `auth.json`, `.env`, tokens, keys; not sessions or caches) to one vault folder outside the base
  (`~/.<base folder name>-secret`, mode 700, one sub-folder per tool; `brain.py vault root PATH` picks another) and
  leaves a symlink, so the tool keeps working. Close the tool first; `--dry-run` shows the list, `--undo` brings them
  back. `brain.py vault add data/<app>/x.token` does the same for any other secret file. `doctor` reports a secret
  file still in `engines/` or `data/` as an ERROR and keeps `wiki/secrets.md` (where each one is, never contents).
  A tool that rewrites its login (write a temp file, rename it over the link) puts a real file back in the base:
  `brain.py engine revault [NAME|--all]` moves the new bytes into the vault and puts the link back (the path is never
  missing), and `watch` does it on every pass. NAME is the folder (`claude`) or the tool id (`claude-code`).
- **Tools without such a setting** (Gemini CLI, Qwen, Kilo, Goose, Cursor, desktop apps, ...): `engine mirror TOOL`
  keeps a read-only copy of their rules, agents, skills, memories and hooks in `engines/<tool>/` (a `MIRROR` file
  says so; keys, logins and sessions are never copied; text that looks like a key is left out and listed in
  `SKIPPED.md`). `watch` refreshes it within a second of a change. Older `~/.config/my-setup/sources.d/*.json`
  registrations (`{"sources": [{"src", "dest"}]}`) are mirrored the same way.
- **Several folders of one tool** (your Claude Code folder plus a worker's): `connect --tool-dir claude-code=DIR`
  (or `--claude-config-dir DIR`, repeatable) wires each one like the default one. Any installer can instead drop a
  file into the shared registry `~/.config/ai-tool-dirs.d/NAME.json` (one object or a list:
  `{"tool": "claude-code", "dir": "/abs/path", "owner": "...", "purpose": "..."}`; `~/.config/claude-code-dirs.d/`
  works too, tool = claude-code): `connect`, `collect`, `watch` and Frugal-Bridge read it.
- **Code**: `projects move PATH` moves a repository into `projects/<slug>/` (a `git bundle` backup first, refuses
  while a program works in it, linked worktrees moved with `git worktree move` and repaired, the Claude Code project
  folder renamed so its sessions and memory follow, Codex trust paths updated, units/cron/tool configs that still name
  the old path listed); `projects move --undo` reverses the last move. `projects.json` (tracked) keeps each repo's
  remote, branch and worktrees: `projects clone` brings them back on a new machine.
- **What leaves this machine, per tool folder** (one table in `brain.py` makes the `.gitignore` and `.stignore`
  blocks, the mirror filter, the pre-commit guard and doctor's checks; `brain.py layout --print` shows them):
  git and Syncthing get only the safe files of `engines/<tool>/` (`*.md` at its top, `MIRROR`, `agents/`, `skills/`,
  `memories/`, `hooks/`, `scripts/`, `commands/`, `rules/`, `prompts/`, `output-styles/`; Hermes `cron/jobs.json` and
  its profiles' `SOUL.md`, memories, skills), so the Mac and GitHub see every skill change. Git also keeps Claude
  Code's `settings.json` and plugin manifests (content checked by the guard; never Syncthing). Secrets come first and
  always win: credentials, `.claude.json`, `.env`, keys, `auth.json`, token files, sessions, transcripts
  (`projects/`), databases, caches, logs, `node_modules` at any depth, and loose `auth*`/`*token*`/`*secret*` names at
  the top of a tool folder (a skill called `x-token-spend` is still shared). `projects/`, `data/`, `apps/`, `runs/`,
  `scratch/`, `backups/`, `ops/` never leave (README only). Checked with a real Syncthing 2.1 scan: only the safe
  files were indexed.
- **Sync all and Syncthing: our scan first, then Syncthing**. With `engine sync-all on`, the content scan (gitleaks)
  writes flagged files into `.stignore`. Syncthing must not offer a new file before that scan, so brain.py finds the
  Syncthing folder whose path is the base (its `config.xml`; the key is read at run time and never printed or
  stored), turns the folder watcher and the periodic rescan off (`fsWatcherEnabled=false`, `rescanIntervalS=0`;
  the old values are recorded and come back with `sync-all off` and `uninstall`), and asks Syncthing to scan the
  folder (`POST /rest/db/scan?folder=ID`) at the end of every sync-scan. Order: our scan, `.stignore`, Syncthing's
  scan. A user systemd drop-in (`~/.config/systemd/user/syncthing.service.d/skeleton-base-scan.conf`, then
  `systemctl --user daemon-reload`) runs the scan before Syncthing starts, so its start-up scan comes after ours.
  Cost: the other computer sees changes up to one watch cycle (10 min) later. If a scan fails (gitleaks missing, crash, timeout), brain.py writes a lockdown block at the top of the base's `.stignore` (`*`: nothing is shared) and `doctor` reports an ERROR; the next good scan removes the block (only that block; your lines and the denied lines stay), then asks Syncthing to scan. The drop-in's start-up scan uses `ExecStartPre=-`, so Syncthing always starts (it also syncs other folders) and the lockdown is already in `.stignore` when it reads it. Fallback: no Syncthing folder found,
  not reachable, or not a systemd user service: nothing breaks, sharing works as before, and `doctor` warns that new
  files can sync before the scan. A file created while our scan runs can still be offered before the next one
  (seconds to minutes on a huge base).
- **Pre-commit guard**: `init` writes `.git/hooks/pre-commit` in a base that is a git repo (your own hook is kept:
  rename it to `pre-commit.local` and it runs first). `brain.py guard` refuses gitlinks, `engines/` files off the
  allow list, anything in the closed folders, secret file names, files over 5 MB and key-like content (gitleaks too
  when installed), never printing the secret. The watcher's own commits skip hooks, so it runs the same check itself
  and leaves a refused `engines/` file out. `check` proves the ignore rules (fake secret paths must be ignored, safe
  ones kept, no tracked secret, no nested repo added as a gitlink). `projects move` backs up a partial clone as its
  `.git` folder (a `bundle --all` would download every missing blob).
- **Never walked**: backups (`uninstall`), tidy's snapshot, the MCP server, `check-public` (in a repo it reads only
  what git could publish) skip the layout folders; `collect` and `watch` find tool memories through each tool's own
  setting (a moved folder keeps its memories' names, so nothing is collected twice).
- **`doctor`** lists every AI tool folder (where, set by which setting, in or outside the base), folders configured
  in user services, profiles or the registry but not wired, unknown AI folders and code repositories outside the
  base (an allowed list: system folders, plus your own in `.brain/outside.json` `{"allow": ["~/vault"]}`), and the
  git checks above. `watch --discover` also names configured folders that are not wired yet.

## Instant and zero-touch

`collect` on hooks and a daily timer is good; `watch` makes it instant. It is a small foreground daemon (standard
library, inotify through `ctypes`; it polls every 5 s where inotify is not available). On any change in a tool's
memory it waits until things are quiet (2 s, at most 10 s during a long burst), then in one run: auto-connects
tools that are new, collects, files the new items on their pages, and if anything is new runs `index` and `map`
and makes a git commit of exactly those files (`raw/inbox/collected/`, the pages it filed on, `wiki/index.md`,
`maps/brain.*`, `.brain/collector.json`, `.brain/filed.json`, `.brain/manifest.json`, `.brain/watch.json`,
`.kits.json`). When a tidy is due it starts the tidy service. It never pushes.

```sh
python3 tools/brain.py connect --watch           # writes the service (+ the daily timer as a safety net)
systemctl --user daemon-reload && systemctl --user enable --now skeleton-base-watch.service skeleton-base-collect.timer skeleton-base-tidy.timer
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
