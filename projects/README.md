# projects/

One code repository per folder (`projects/<slug>/`), each with its own git and remote. The base's git ignores
them (`.gitignore`); `projects.json` (tracked) lists each one's remote, branch and worktrees so a new machine gets
them back with `python3 tools/brain.py projects clone`. Linked worktrees go in `projects/.worktrees/<slug>/`.

Move a repository here with `python3 tools/brain.py projects move PATH` (refuses while a program works in it,
moves its worktrees with git, renames the Claude Code project folder, logs everything for `projects move --undo`).

Sync (1.7.4): with the default **notes** scope (`engine sync-scope notes`) nothing in this folder leaves the computer.
With **sync all** (`engine sync-all on`) the code repositories are shared to other computers, minus heavy folders
(`node_modules`, `.git`, `.venv`, databases, archives) and secret files. A repo is only registered when this folder
is its own git repo (`projects move`, `projects scan`); `doctor` flags any other entry in `projects.json`.
