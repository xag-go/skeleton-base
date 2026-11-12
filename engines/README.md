# engines/

Each AI tool's own config folder can live here (`engines/<tool>/`), pointed to by the tool's OWN setting
(no symlinks): Claude Code `CLAUDE_CONFIG_DIR`, Codex `CODEX_HOME`, Hermes `HERMES_HOME`, OpenClaw
`OPENCLAW_STATE_DIR`, Copilot CLI `COPILOT_HOME`. `python3 tools/brain.py engine adopt TOOL` moves a tool's
folder here and sets the variable for shells and user services; `engine release TOOL` puts it back.

A tool without such a setting gets a read-only copy here instead (`engine mirror TOOL`, folder with a `MIRROR`
file), kept current by `brain.py watch`. Edit the original, never the copy.

Git keeps only rules, agents, skills, memories, hooks and scripts of each folder (deny by default, see
`.gitignore`); logins, keys, sessions, databases, logs and caches stay on this machine only. Syncthing skips the
whole folder (`.stignore`). `engines.json` lists what is here.
