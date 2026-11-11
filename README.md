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
| `hermes` | `.hermes/memories/*.md` |
| `hermes-facts` | `.hermes/memory_store.db` (table `facts`) |
| `openclaw` | `.openclaw/workspace/MEMORY.md`, `USER.md`, `memory/*.md` |

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
python3 tools/brain.py connect            # add --timer for a daily systemd user timer
python3 tools/brain.py disconnect         # remove exactly what connect wrote
```

For the current user, `connect`:
- writes a marked pointer block (`<!-- base-folder:start v2 -->` ... `<!-- base-folder:end -->`) into
  `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` and `~/.gemini/GEMINI.md`, only for tools that are installed (their
  folder exists). It says where the base is, to read `hot.md` then `wiki/index.md` only when owner context is
  needed (never for plain coding), never to edit `raw/`, and the Saving knowledge rule. An older block is
  replaced in place; all other text stays byte-identical.
- merges two Claude Code hooks into `~/.claude/settings.json` (`SessionEnd`, `PreCompact`) that run
  `collect --quiet`. Other hooks and keys are kept; a backup goes to `.brain/backups/`.
- with `--timer`: writes `~/.config/systemd/user/skeleton-base-collect.service` and `.timer` (daily and 10 minutes
  after boot, `Persistent=true`) and prints the command to enable it:
  `systemctl --user daemon-reload && systemctl --user enable --now skeleton-base-collect.timer`.

Everything written is recorded in `.kits.json` (`kits.base-folder.connect`); `disconnect` (and `uninstall`)
remove exactly that and give the previous text back, including an older pointer block it replaced.

## Viewing it in Obsidian

Open the base folder as a vault. Pages, `[[links]]` and the graph work as is; `board/board.base` shows the board
(core Bases plugin), `maps/*.canvas` open as canvases. To sync to another machine, Syncthing works well; the
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
