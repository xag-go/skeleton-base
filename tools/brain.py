#!/usr/bin/env python3
"""brain.py - Skeleton Base tools. Python 3.10+ standard library only, no AI, no network.

Setup
  init DIR [--frugal=yes|no]   install the full skeleton into DIR (new or existing; idempotent; never
                               overwrites your files; imports Frugal-Bridge files if it is installed there)
  uninstall DIR                remove what init added and you did not change (exports slots back to
                               Frugal-Bridge files if Frugal-Bridge is installed)

Daily use (run inside a base, or pass --root DIR)
  status                       NEW / CHANGED / DELETED files in raw/ since the last ingest
  done RAW PAGE...             record that RAW was ingested into PAGE(s)
  lint                         check the wiki, board, maps and skills (exit 2 on problems)
  index                        rebuild the page list in wiki/index.md
  brief [--short]              print one paste-able bundle for chat apps (default: full)
  search QUERY                 full-text search (SQLite FTS5 index in .brain/)
  check                        AGENTS.md size, pointer files, settings, registry
  check-public --words FILE [DIR]
                               before a public push: fail on secrets, emails, phone numbers and any
                               word listed in FILE (file contents, paths and git history)
"""
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import shutil
import sqlite3
import subprocess
import sys

VERSION = "1"
SRC = pathlib.Path(__file__).resolve().parent.parent          # the skeleton this script came with
START = f"<!-- base-folder:start v{VERSION} -->"
END = "<!-- base-folder:end -->"
START_RE = re.compile(r"<!-- base-folder:start v[^>]*-->")
FRUGAL_START_RE = re.compile(r"<!-- frugal-bridge:start v[^>]*-->")
GI_START = f"# base-folder:start v{VERSION}"
GI_END = "# base-folder:end"
GI_START_RE = re.compile(r"# base-folder:start v\S*")
POINTER = "@AGENTS.md"
SOFT_LIMIT, HARD_LIMIT = 24 * 1024, 32 * 1024
GEMINI_NAMES = ["AGENTS.md", "GEMINI.md"]
BASE_SLOTS = {"user": "wiki/me/", "now": "hot.md", "decisions": "wiki/decisions/",
              "map": "wiki/index.md", "sources": "raw/"}
FRUGAL_DEFAULT = {"user": "USER.md", "now": "PROGRESS.md", "decisions": "DECISIONS.md",
                  "map": "MAP.md", "sources": "sources/"}

# what init installs (plain files are copied only when missing)
DIRS = ["wiki/projects", "wiki/clients", "wiki/people", "wiki/decisions", "wiki/concepts", "wiki/daily",
        "wiki/sops", "raw/inbox", "raw/docs", "raw/references", "raw/clients", "raw/videos", "raw/exports"]
FILES = ["README.md", "SECURITY.md", "hot.md", "wiki/index.md", "wiki/log.md", "wiki/glossary.md",
         "wiki/me/who-i-am.md", "wiki/me/goals.md", "wiki/me/how-to-talk-to-me.md",
         "board/README.md", "board/board.base", "board/2026-01-01-fill-in-your-profile.md",
         "agents/assistant.md", "agents/twin.md", "progress/agents.log",
         "maps/README.md", "maps/start-here.canvas",
         "templates/person.md", "templates/client.md", "templates/project.md", "templates/decision.md",
         "templates/daily.md", "templates/source.md", "templates/card.md",
         "skills/base-ingest/SKILL.md", "skills/base-lint/SKILL.md", "tools/brain.py", ".stignore"]

SPECIAL = ("index.md", "log.md")
SCOPES = ("private", "workspaces")
STATUSES = ("todo", "doing", "waiting", "done")
LINK = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
QUOTE = re.compile(r'^>[ \t]*"(.+?)"[ \t]*[\u2014\u2013-]+[ \t]*(raw/\S+)[ \t]*$', re.M)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
IDX_START, IDX_END = "<!-- brain:index:start -->", "<!-- brain:index:end -->"

SECRETS = [
    ("anthropic key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{4,}")),
    ("openai-style key", re.compile(r"\bsk-[A-Za-z0-9]{20,}")),
    ("aws key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}")),
    ("slack token", re.compile(r"\bxox[abpr]-[A-Za-z0-9\-]{10,}")),
    ("google key", re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("credential assignment", re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-+/]{12,}")),
]
EMAIL = re.compile(r"(?<![\w.%+\-])[A-Za-z0-9][A-Za-z0-9._%+\-]*@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}")
SAFE_EMAIL_DOMAINS = re.compile(r"(?i)@(?:[\w\-]+\.)*(?:example\.(?:com|org|net)|[\w\-]+\.(?:invalid|test|example))$")
FILE_EXTS = {"md", "py", "json", "txt", "yml", "yaml", "js", "ts", "sh", "toml", "canvas", "base"}
PHONE = re.compile(r"(?<![\w.\-])(?:\+\d{1,3}[ .\-]?\(?\d{1,4}\)?(?:[ .\-]?\d{2,4}){2,4}|0\d(?:[ .\-]?\d{2}){4})(?![\w\-])")


# ---------------------------------------------------------------- small helpers
def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()


def read(p):
    p = pathlib.Path(p)
    return p.read_text(encoding="utf-8") if p.is_file() else None


def write(p, text):
    p = pathlib.Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def today():
    return os.environ.get("BRAIN_TODAY") or dt.date.today().isoformat()


def frontmatter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    fm = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            a, b = line.split(":", 1)
            fm[a.strip()] = b.split(" #")[0].strip()
    return fm


def is_fact_line(line):
    """A line worth copying into hot.md: not a heading, not an empty template field or placeholder."""
    t = line.strip()
    if not t or t.startswith("#") or t.endswith("...") or t == "-":
        return False
    if re.fullmatch(r"(?:[-*] )?(?:\[[ x]\] )?<[^>]*>|(?:[-*] )?[^:]{1,80}:\s*(?:\.\.\.)?", t):
        return False
    return True


def body_of(text):
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end >= 0:
            nl = text.find("\n", end + 4)
            return text[nl + 1:] if nl >= 0 else ""
    return text


def find_block(text, start_re=START_RE, end=END):
    if not text:
        return None
    m = start_re.search(text)
    if not m:
        return None
    e = text.find(end, m.end())
    return (m.start(), e + len(end)) if e >= 0 else None


def block_body(rel, start_re=START_RE, end=END):
    """Body of the Base block in the skeleton's own copy of rel (between the markers)."""
    t = read(SRC / rel)
    r = find_block(t, start_re, end)
    if not r:
        raise SystemExit(f"skeleton file {rel} has no base-folder block: broken install source")
    inner = t[r[0]:r[1]]
    return inner[inner.index("\n") + 1:inner.rindex("\n")]


def load_json(p, what):
    t = read(p)
    if t is None or not t.strip():
        return {}
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        raise SystemExit(f"{what} is not valid JSON; fix it by hand first (nothing changed).")


def dump_json(d):
    return json.dumps(d, indent=2, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------- install
class Installer:
    def __init__(self, target):
        self.d = pathlib.Path(target).resolve()
        self.log = []
        self.backup_dir = None

    def p(self, rel):
        return self.d / rel

    def backup(self, rel):
        src = self.p(rel)
        if not src.exists():
            return
        if not self.backup_dir:
            self.backup_dir = self.p(f".base-folder/backup/{dt.datetime.now():%Y%m%d-%H%M%S-%f}")
        dst = self.backup_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)

    def change(self, rel, new, backup=True):
        if read(self.p(rel)) == new:
            return False
        if backup:
            self.backup(rel)
        write(self.p(rel), new)
        self.log.append(f"wrote {rel}")
        return True

    # -- marked blocks
    def put_block(self, rel, body, modes, start=START, end=END, start_re=START_RE, before_frugal=False):
        old = read(self.p(rel))
        core = f"{start}\n{body}\n{end}"
        r = find_block(old, start_re, end)
        if r:
            self.change(rel, old[:r[0]] + core + old[r[1]:])
            return modes.get(rel, "append")
        fr = FRUGAL_START_RE.search(old or "") if before_frugal else None
        if not old:
            mode, new = "new", core + "\n"
        elif fr:   # fixed order: base block first, other kit's block after it
            mode, new = "before-frugal", old[:fr.start()] + core + "\n\n" + old[fr.start():]
        elif old.endswith("\n"):
            mode, new = "append", old + "\n" + core + "\n"
        else:
            mode, new = "append-noeol", old + "\n\n" + core + "\n"
        self.change(rel, new)
        return mode

    @staticmethod
    def strip_block(text, mode, start_re=START_RE, end=END):
        r = find_block(text, start_re, end)
        if not r:
            return text, False
        a, b = r
        if mode in ("new", "before-frugal"):
            for _ in range(2):
                if text[b:b + 1] == "\n":
                    b += 1
        else:
            if text[b:b + 1] == "\n":
                b += 1
            if text[a - 1:a] == "\n":
                a -= 1
            if mode == "append-noeol" and text[a - 1:a] == "\n":
                a -= 1
        return text[:a] + text[b:], True

    # -- init
    def init(self, frugal_answer=None):
        if self.d == SRC:
            raise SystemExit("init: target is the skeleton itself; give another folder")
        self.d.mkdir(parents=True, exist_ok=True)
        k = load_json(self.p(".kits.json"), ".kits.json")
        gem = load_json(self.p(".gemini/settings.json"), ".gemini/settings.json")   # validate before writing
        kits = k.setdefault("kits", {})
        prev = kits.get("base-folder", {})
        created = dict(prev.get("created", {}))
        modes = dict(prev.get("placement", {}))
        json_added = {key: list(v) for key, v in prev.get("json_added", {}).items()}

        for d in DIRS:
            if not self.p(d).is_dir():
                self.p(d).mkdir(parents=True)
                created.setdefault(d + "/", "")
        for rel in FILES:
            src, dst = SRC / rel, self.p(rel)
            if rel in created and dst.is_file() \
                    and sha(dst.read_bytes()) == created[rel] and dst.read_bytes() != src.read_bytes():
                shutil.copy2(src, dst); created[rel] = sha(dst.read_bytes())   # upgrade a file you never changed
                self.log.append(f"updated {rel}")
                continue
            if dst.exists():
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            created[rel] = sha(dst.read_bytes())
            self.log.append(f"created {rel}")

        # AGENTS.md: our block only
        existed = self.p("AGENTS.md").exists()
        modes["AGENTS.md"] = self.put_block("AGENTS.md", block_body("AGENTS.md"), modes, before_frugal=True)
        if not existed:
            created["AGENTS.md"] = "block"

        # pointer files: exactly '@AGENTS.md' (an import line)
        for rel in ("CLAUDE.md", "GEMINI.md"):
            t = read(self.p(rel))
            if t is None:
                write(self.p(rel), POINTER + "\n"); created[rel] = sha(POINTER + "\n")
                self.log.append(f"created {rel}")
            elif find_block(t) or not any(l.strip() == POINTER for l in t.splitlines()):
                modes[rel] = self.put_block(rel, POINTER, modes)

        # .gemini/settings.json: merge by key
        rel = ".gemini/settings.json"
        if not self.p(rel).exists():
            created[rel] = "json"
        ctx = gem.setdefault("context", {})
        names = ctx.get("fileName", [])
        names = [names] if isinstance(names, str) else list(names)
        added = json_added.setdefault(rel, [])
        for n in GEMINI_NAMES:
            if n not in names:
                names.append(n)
                if n not in added:
                    added.append(n)
        ctx["fileName"] = names
        if not added:
            json_added.pop(rel)
        self.change(rel, dump_json(gem))

        # .gitignore block
        existed = self.p(".gitignore").exists()
        body = block_body(".gitignore", GI_START_RE, GI_END)
        modes[".gitignore"] = self.put_block(".gitignore", body, modes, GI_START, GI_END, GI_START_RE)
        if not existed:
            created[".gitignore"] = "block"

        # Frugal-Bridge already here: import its slot files (contract case 4)
        imported = prev.get("imported")
        if "frugal-bridge" in kits and not imported:
            imported = self.import_frugal(k.get("slots") or dict(FRUGAL_DEFAULT), created)

        entry = {"version": VERSION, "installed": prev.get("installed") or today(),
                 "created": dict(sorted(created.items())), "placement": dict(sorted(modes.items()))}
        if json_added:
            entry["json_added"] = json_added
        if imported:
            entry["imported"] = imported
        kits["base-folder"] = entry
        k["slots"] = dict(BASE_SLOTS)
        new = dump_json(k)
        if read(self.p(".kits.json")) != new:
            write(self.p(".kits.json"), new)
            self.log.append("wrote .kits.json")

        if "frugal-bridge" not in kits:
            self.offer_frugal(frugal_answer)
        rep = check(self.d)
        return rep

    def offer_frugal(self, answer):
        if answer is None:
            if sys.stdin.isatty():
                answer = input("Also install Frugal-Bridge? [y/N] ").strip().lower()
            else:
                answer = "no"
        if answer in ("y", "yes"):
            self.log.append("Frugal-Bridge is a separate product with its own setup. Get it from its own "
                            "repository, then run:\n"
                            f"  python3 <frugal-bridge>/kit/setup.py install \"{self.d}\"")
        else:
            self.log.append("Frugal-Bridge: skipped (run init again with --frugal=yes for the command)")

    def import_frugal(self, slots, created):
        day = today()
        exp = f"raw/exports/frugal-{day}"
        rec = {"date": day, "export": exp + "/", "from": {}, "stubs": {}, "pages": {}}
        dest = {"user": "wiki/me/frugal-user.md", "now": "progress/frugal-progress.md",
                "decisions": "wiki/decisions/frugal-decisions.md"}
        titles = {"user": "About the user (imported from Frugal-Bridge)",
                  "decisions": "Decisions (imported from Frugal-Bridge)"}
        for slot in ("user", "now", "decisions", "map"):
            rel = slots.get(slot) or FRUGAL_DEFAULT[slot]
            if rel.endswith("/") or rel in BASE_SLOTS.values() or not self.p(rel).is_file():
                continue
            text = read(self.p(rel))
            write(self.p(f"{exp}/{rel}"), text)
            rec["from"][slot] = rel
            src_ref = f"{exp}/{rel}"
            if slot in ("user", "decisions"):
                page = (f"---\ntitle: {titles[slot]}\nsources: [{src_ref}]\nupdated: {day}\nscope: private\n---\n\n"
                        + text.rstrip() + "\n")
                write(self.p(dest[slot]), page); rec["pages"][slot] = dest[slot]
                target = dest[slot]
            elif slot == "now":
                write(self.p(dest["now"]), text); rec["pages"]["now"] = dest["now"]
                lines = [l for l in body_of(text).splitlines() if is_fact_line(l)][:10]
                hot = read(self.p("hot.md")) or ""
                hot = hot.rstrip("\n") + f"\n\n## From Frugal-Bridge (imported {day})\n" \
                    + f"Full text: {dest['now']}\n" + "\n".join(lines) + "\n"
                write(self.p("hot.md"), hot)
                target = "hot.md"
            else:
                idx = read(self.p("wiki/index.md")) or index_text(None, self.d)
                idx = idx.rstrip("\n") + f"\n\n## Imported map (Frugal-Bridge, {day})\n\n" + body_of(text).rstrip() + "\n"
                write(self.p("wiki/index.md"), idx)
                target = "wiki/index.md"
            stub = (f"# Moved\n\nThis file moved into the base on {day}: see `{target}`.\n"
                    f"Original copy: `{src_ref}`. Paths are listed in `.kits.json` (slots).\n")
            write(self.p(rel), stub); rec["stubs"][rel] = sha(stub)
            self.log.append(f"imported {rel} -> {target} (original in {src_ref})")
        srcdir = slots.get("sources") or FRUGAL_DEFAULT["sources"]
        if srcdir not in BASE_SLOTS.values() and self.p(srcdir).is_dir() \
                and any(f.is_file() for f in self.p(srcdir).rglob("*")):
            moved = []
            for f in sorted(self.p(srcdir).rglob("*")):
                if not f.is_file():
                    continue
                r = f.relative_to(self.p(srcdir)).as_posix()
                data = f.read_bytes()
                for dst in (self.p(f"{exp}/{srcdir}{r}"), self.p(f"raw/inbox/frugal-sources/{r}")):
                    dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(data)
                f.unlink(); moved.append(r)
            for sub in sorted((x for x in self.p(srcdir).rglob("*") if x.is_dir()), reverse=True):
                if not any(sub.iterdir()):
                    sub.rmdir()
            stub = (f"# Moved\n\nFiles from this folder moved into the base on {day}: see "
                    f"`raw/inbox/frugal-sources/`. Original copies: `{exp}/{srcdir}`.\n")
            write(self.p(srcdir + "MOVED.md"), stub)
            rec["stubs"][srcdir + "MOVED.md"] = sha(stub)
            rec["from"]["sources"] = srcdir
            rec["sources"] = moved
            self.log.append(f"imported {srcdir} ({len(moved)} files) -> raw/inbox/frugal-sources/")
        if rec["pages"] or rec["from"]:
            build_index(self.d, quiet=True)
            return rec
        return None

    # -- uninstall
    def uninstall(self):
        k = load_json(self.p(".kits.json"), ".kits.json")
        kits = k.get("kits", {})
        me = kits.get("base-folder")
        if not me:
            return ["base-folder is not installed here (nothing changed)"]
        frugal = "frugal-bridge" in kits
        created = me.get("created", {})
        modes = me.get("placement", {})
        kept = []

        new_slots = self.export_slots(me) if frugal else None

        for rel, sr, en in (("AGENTS.md", START_RE, END), ("CLAUDE.md", START_RE, END),
                            ("GEMINI.md", START_RE, END), (".gitignore", GI_START_RE, GI_END)):
            t = read(self.p(rel))
            if t is None:
                continue
            if created.get(rel) == sha(t) and t.strip() == POINTER:
                if frugal:
                    kept.append(rel + " (Frugal-Bridge uses it)")
                else:
                    self.p(rel).unlink(); self.log.append(f"removed {rel}")
                continue
            new, had = self.strip_block(t, modes.get(rel, "append"), sr, en)
            if not had:
                continue
            if rel in created and not new.strip():
                self.p(rel).unlink(); self.log.append(f"removed {rel}")
            else:
                self.change(rel, new)

        rel = ".gemini/settings.json"
        if self.p(rel).exists() and not frugal:
            data = load_json(self.p(rel), rel)
            ctx = data.get("context", {})
            names = ctx.get("fileName")
            if isinstance(names, list):
                names = [n for n in names if n not in me.get("json_added", {}).get(rel, [])]
                if names:
                    ctx["fileName"] = names
                else:
                    ctx.pop("fileName")
                if not ctx:
                    data.pop("context", None)
            if not data and created.get(rel) == "json":
                self.p(rel).unlink(); self.log.append(f"removed {rel}")
                if self.p(".gemini").is_dir() and not any(self.p(".gemini").iterdir()):
                    self.p(".gemini").rmdir()
            else:
                self.change(rel, dump_json(data))
        elif self.p(rel).exists():
            kept.append(rel + " (Frugal-Bridge hosts use it)")

        for rel, h in sorted(created.items()):
            if rel.endswith("/") or h in ("block", "json") or rel in ("CLAUDE.md", "GEMINI.md"):
                continue
            f = self.p(rel)
            if not f.is_file():
                continue
            if sha(f.read_bytes()) == h:
                f.unlink()
            else:
                kept.append(rel)
        for d in sorted({str(pathlib.Path(r).parent) for r in created if not r.endswith("/")}
                        | {r.rstrip("/") for r in created if r.endswith("/")}, key=lambda x: -x.count("/")):
            self._rmdir_up(d)
        for extra in (".brain/search.db", ".brain"):
            p = self.p(extra)
            if p.is_file():
                p.unlink()
            elif p.is_dir() and not any(p.iterdir()):
                p.rmdir()

        del kits["base-folder"]
        if frugal:
            if not self.p(new_slots["sources"]).is_dir():
                new_slots["sources"] = FRUGAL_DEFAULT["sources"]
                self.p(new_slots["sources"]).mkdir(exist_ok=True)
            k["slots"] = new_slots
        else:
            k.pop("slots", None)
        if not kits and set(k) <= {"kits"}:
            self.p(".kits.json").unlink()
        else:
            write(self.p(".kits.json"), dump_json(k))
        if kept:
            self.log.append("kept (has your content): " + ", ".join(kept))
        return self.log

    def _rmdir_up(self, rel):
        p = self.p(rel)
        while p != self.d and p.is_dir() and not any(p.iterdir()):
            p.rmdir()
            p = p.parent

    def export_slots(self, me):
        """Case 8: write plain USER / PROGRESS / DECISIONS / MAP files back for Frugal-Bridge."""
        imp = me.get("imported") or {}
        frm = imp.get("from", {})
        stubs = imp.get("stubs", {})
        day = today()
        head = f"<!-- exported from Skeleton Base on {day} -->\n"

        def pages(folder):
            out = []
            for f in sorted(self.p(folder).glob("*.md")):
                out.append(f"\n<!-- from {f.relative_to(self.d).as_posix()} -->\n" + body_of(read(f)).strip() + "\n")
            return "".join(out)

        progress_hist = read(self.p("progress/frugal-progress.md"))
        content = {
            "user": head + "# USER.md\n" + pages("wiki/me"),
            "now": head + (read(self.p("hot.md")) or "").rstrip() + "\n"
                   + (f"\n<!-- history -->\n{progress_hist.rstrip()}\n" if progress_hist else ""),
            "decisions": head + "# DECISIONS.md\n" + pages("wiki/decisions"),
            "map": head + (read(self.p("wiki/index.md")) or "# MAP.md\n").rstrip() + "\n",
        }
        slots = {}
        for slot, text in content.items():
            rel = frm.get(slot) or FRUGAL_DEFAULT[slot]
            cur = read(self.p(rel))
            if cur is not None and stubs.get(rel) != sha(cur) and cur != text:
                self.backup(rel)
            write(self.p(rel), text)
            slots[slot] = rel
            self.log.append(f"exported {slot} -> {rel}")
        srcdir = frm.get("sources") or FRUGAL_DEFAULT["sources"]
        moved = imp.get("sources", [])
        if moved:
            for r in moved:
                f = self.p(f"raw/inbox/frugal-sources/{r}")
                if f.is_file():
                    dst = self.p(srcdir + r); dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dst)
            stub = self.p(srcdir + "MOVED.md")
            if stub.is_file() and sha(stub.read_bytes()) == stubs.get(srcdir + "MOVED.md"):
                stub.unlink()
            slots["sources"] = srcdir
            self.log.append(f"exported sources -> {srcdir} ({len(moved)} files)")
        else:
            slots["sources"] = "raw/"
        return slots


# ---------------------------------------------------------------- base commands
ROOT_ARG = None


def root_of():
    return pathlib.Path(ROOT_ARG or os.environ.get("BRAIN_ROOT") or SRC).resolve()


def rel(p, root):
    return pathlib.Path(p).relative_to(root).as_posix()


def manifest_path(root):
    return root / ".brain" / "manifest.json"


def load_manifest(root):
    t = read(manifest_path(root))
    return json.loads(t) if t else {}


def raw_files(root):
    r = root / "raw"
    if not r.is_dir():
        return []
    return sorted(p for p in r.rglob("*") if p.is_file() and not p.name.startswith("."))


def wiki_pages(root):
    w = root / "wiki"
    return sorted(w.rglob("*.md")) if w.is_dir() else []


def board_cards(root):
    b = root / "board"
    return sorted(p for p in b.glob("*.md") if p.name != "README.md") if b.is_dir() else []


def roles(root):
    a = root / "agents"
    return {p.stem for p in a.glob("*.md")} if a.is_dir() else set()


def status(root):
    m, todo = load_manifest(root), []
    for p in raw_files(root):
        k = rel(p, root)
        if k not in m:
            todo.append(("NEW", k))
        elif m[k]["sha"] != sha(p.read_bytes()):
            todo.append(("CHANGED", k))
    for k in m:
        if not (root / k).exists():
            todo.append(("DELETED", k))
    for s, k in todo:
        print(s, k)
    print(f"pending: {len(todo)}", file=sys.stderr)
    return 0


def done(root, raw, pages):
    p = root / raw
    if not raw.startswith("raw/") or not p.is_file():
        print("no such raw file:", raw); return 1
    if not pages:
        print("usage: done RAW PAGE..."); return 1
    for w in pages:
        if not (root / w).is_file():
            print("no such page:", w); return 1
    m = load_manifest(root)
    m[raw] = {"sha": sha(p.read_bytes()), "pages": pages, "date": today()}
    write(manifest_path(root), json.dumps(m, indent=2, sort_keys=True) + "\n")
    print(f"done: {raw} -> {', '.join(pages)}")
    return 0


FENCE = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.M | re.S)
CODESPAN = re.compile(r"`[^`\n]+`")
TODO_MARK = re.compile(r"(^|\n)\s*(?:[-*]\s*(?:\[ \]\s*)?)?TODO\b|\bTODO:")


def prose(t):
    """Text with fenced code blocks and inline code removed (examples in code are not checked)."""
    return CODESPAN.sub("", FENCE.sub("", t))


def lint(root):
    errs, warns = [], []
    names, texts = {}, {}
    for p in wiki_pages(root):
        if p.stem in names:
            errs.append(f"{rel(p, root)}: duplicate page name (also {rel(names[p.stem], root)})")
        names[p.stem] = p
        texts[p] = p.read_text(encoding="utf-8")
    cards = board_cards(root)
    card_texts = {c: c.read_text(encoding="utf-8") for c in cards}
    link_targets = set(names) | {c.stem for c in cards} | {"hot"} | {f"agents/{r}" for r in roles(root)} | roles(root)
    inbound = {n: 0 for n in names}
    src_cache = {}

    def check_links(p, t):
        for l in LINK.findall(t):
            l = l.strip()
            stem = l.split("/")[-1].removesuffix(".md")
            if l in link_targets or stem in link_targets:
                if stem in inbound and names.get(stem) != p:
                    inbound[stem] += 1
            else:
                errs.append(f"{rel(p, root)}: broken link [[{l}]]")

    def check_fm(p, fm, need):
        for k in need:
            if not fm.get(k):
                errs.append(f"{rel(p, root)}: frontmatter lacks '{k}'")
        if fm.get("scope") and fm["scope"] not in SCOPES:
            errs.append(f"{rel(p, root)}: bad scope '{fm['scope']}' (use {' | '.join(SCOPES)})")
        if fm.get("updated") and not DATE.match(fm["updated"]):
            errs.append(f"{rel(p, root)}: 'updated' is not YYYY-MM-DD")

    for p, t in texts.items():
        t = prose(t)
        check_links(p, t)
        if p.name in SPECIAL and p.parent == root / "wiki":
            continue
        fm = frontmatter(t)
        if fm is None:
            errs.append(f"{rel(p, root)}: missing frontmatter"); continue
        check_fm(p, fm, ("title", "sources", "updated", "scope"))
        for src in re.findall(r"raw/[^\s,\]\[]+", fm.get("sources", "")):
            if not (root / src).exists():
                errs.append(f"{rel(p, root)}: source {src} does not exist")
        for q, src in QUOTE.findall(t):
            f = root / src
            if not f.is_file():
                errs.append(f"{rel(p, root)}: quote cites missing {src}")
            elif " ".join(q.split()) not in src_cache.setdefault(src, " ".join(f.read_text(errors="replace").split())):
                errs.append(f"{rel(p, root)}: QUOTE NOT IN SOURCE -> \"{q[:50]}\" ({src})")
        if TODO_MARK.search(t):
            errs.append(f"{rel(p, root)}: unresolved TODO")
        if p.stem != p.stem.lower() or " " in p.stem or "_" in p.stem:
            errs.append(f"{rel(p, root)}: file name must be lowercase with hyphens")

    hot = root / "hot.md"
    if hot.is_file():
        check_links(hot, prose(hot.read_text(encoding="utf-8")))
    else:
        errs.append("hot.md: missing")

    # board
    rs = roles(root)
    for c, t in card_texts.items():
        check_links(c, t)
        fm = frontmatter(t)
        if fm is None:
            errs.append(f"{rel(c, root)}: missing frontmatter"); continue
        check_fm(c, fm, ("title", "status", "owner", "project", "updated", "scope"))
        if fm.get("status") and fm["status"] not in STATUSES:
            errs.append(f"{rel(c, root)}: bad status '{fm['status']}' (use {' | '.join(STATUSES)})")
        if fm.get("owner") and fm["owner"] != "me" and fm["owner"] not in rs:
            errs.append(f"{rel(c, root)}: owner '{fm['owner']}' is not 'me' or a role in agents/ ({', '.join(sorted(rs))})")
        pj = fm.get("project")
        if pj and pj != "none" and not (root / "wiki" / "projects" / f"{pj}.md").is_file() \
                and not (root / "wiki" / "projects" / pj / "README.md").is_file():
            errs.append(f"{rel(c, root)}: project '{pj}' has no page in wiki/projects/")
        if fm.get("due") and not DATE.match(fm["due"]):
            errs.append(f"{rel(c, root)}: 'due' is not YYYY-MM-DD")
        if not re.match(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9\-]*$", c.stem):
            errs.append(f"{rel(c, root)}: card name must be YYYY-MM-DD-slug.md")
        if fm.get("status") == "doing" and fm.get("updated") and DATE.match(fm["updated"]):
            age = (dt.date.fromisoformat(today()) - dt.date.fromisoformat(fm["updated"])).days
            if age > 14:
                warns.append(f"{rel(c, root)}: in 'doing' for {age} days")

    for n, c in inbound.items():
        p = names[n]
        if c == 0 and not (p.name in SPECIAL and p.parent == root / "wiki"):
            errs.append(f"{rel(p, root)}: orphan (no inbound links; link it or run index)")

    # raw changed since ingest / new raw
    m = load_manifest(root)
    for k, v in m.items():
        f = root / k
        if f.is_file() and sha(f.read_bytes()) != v["sha"]:
            errs.append(f"{k}: changed since ingest, pages stale: {', '.join(v['pages'])}")
    new = [rel(p, root) for p in raw_files(root) if rel(p, root) not in m]
    if new:
        warns.append(f"{len(new)} NEW raw file(s) not ingested yet: {', '.join(new[:5])}{' ...' if len(new) > 5 else ''}")

    # maps (JSON Canvas) and skills (Agent Skills)
    for cv in sorted((root / "maps").glob("*.canvas")) if (root / "maps").is_dir() else []:
        errs += canvas_errors(cv, root)
    for sk in sorted((root / "skills").glob("*/SKILL.md")) if (root / "skills").is_dir() else []:
        fm = frontmatter(sk.read_text(encoding="utf-8")) or {}
        if fm.get("name") != sk.parent.name or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", fm.get("name", "")):
            errs.append(f"{rel(sk, root)}: 'name' must equal the folder name (lowercase-hyphen)")
        if not fm.get("description") or len(fm["description"]) > 1024:
            errs.append(f"{rel(sk, root)}: 'description' missing or over 1024 characters")

    for w in warns:
        print("warning:", w, file=sys.stderr)
    for e in errs:
        print(e, file=sys.stderr)
    print(f"lint ({len(texts)} pages, {len(cards)} cards): {len(errs)} problem(s), {len(warns)} warning(s)",
          file=sys.stderr)
    return 2 if errs else 0


def canvas_errors(cv, root):
    r = rel(cv, root)
    try:
        data = json.loads(cv.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"{r}: invalid JSON ({e})"]
    out, ids = [], set()
    for n in data.get("nodes", []):
        for k in ("id", "type", "x", "y", "width", "height"):
            if k not in n:
                out.append(f"{r}: node lacks '{k}'")
        if n.get("id") in ids:
            out.append(f"{r}: duplicate node id {n.get('id')}")
        ids.add(n.get("id"))
        if n.get("type") not in ("text", "file", "link", "group"):
            out.append(f"{r}: bad node type {n.get('type')}")
        if n.get("type") == "file" and not (root / n.get("file", "")).exists():
            out.append(f"{r}: file node points to missing {n.get('file')}")
    for e in data.get("edges", []):
        if e.get("fromNode") not in ids or e.get("toNode") not in ids:
            out.append(f"{r}: edge {e.get('id')} points to a missing node")
    return out


def index_rows(root):
    groups = {}
    for p in wiki_pages(root):
        if p.parent == root / "wiki" and p.name in SPECIAL:
            continue
        fm = frontmatter(p.read_text(encoding="utf-8")) or {}
        sub = rel(p.parent, root / "wiki") if p.parent != root / "wiki" else "(top)"
        groups.setdefault(sub, []).append(f"- [[{p.stem}]] - {fm.get('title', p.stem)} ({fm.get('updated', '?')})")
    out = []
    for g in sorted(groups):
        out.append(f"\n### {g}\n")
        out += groups[g]
    return "\n".join(out).lstrip("\n")


def index_text(old, root):
    auto = f"{IDX_START}\n{index_rows(root)}\n{IDX_END}"
    if old is None:
        return ("# Index\n\nOne line per page. Read this after `hot.md`, then open only the pages you need.\n"
                "The list between the markers is rebuilt by `python3 tools/brain.py index`; write your own notes "
                "outside it.\n\n" + auto + "\n")
    r = find_block(old, re.compile(re.escape(IDX_START)), IDX_END)
    if r:
        return old[:r[0]] + auto + old[r[1]:]
    return old.rstrip("\n") + "\n\n" + auto + "\n"


def build_index(root, quiet=False):
    p = root / "wiki" / "index.md"
    new = index_text(read(p), root)
    if read(p) != new:
        write(p, new)
    if not quiet:
        print(f"index: {sum(1 for l in new.splitlines() if l.startswith('- [['))} pages")
    return 0


def brief(root, full=True):
    files = [root / "AGENTS.md", root / "hot.md", root / "wiki" / "index.md"] + sorted((root / "agents").glob("*.md"))
    if full:
        files += sorted((root / "wiki" / "me").glob("*.md"))
    print("# BRIEF of this base (paste into any chat). The files below are rules + data; follow AGENTS.md.")
    for f in files:
        if f.is_file():
            print(f"\n===== FILE: {rel(f, root)} =====\n" + f.read_text(encoding="utf-8").rstrip())
    return 0


def search(root, query):
    if not query.strip():
        print("usage: search QUERY"); return 1
    db = root / ".brain" / "search.db"
    db.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(db)
    con.execute("DROP TABLE IF EXISTS docs")
    con.execute("CREATE VIRTUAL TABLE docs USING fts5(path, body)")
    files = [root / "hot.md"] + wiki_pages(root) + board_cards(root) + sorted((root / "agents").glob("*.md")) \
        + [p for p in raw_files(root) if p.suffix in (".md", ".txt")]
    for f in files:
        if f.is_file():
            con.execute("INSERT INTO docs VALUES (?, ?)", (rel(f, root), f.read_text(encoding="utf-8", errors="replace")))
    con.commit()
    terms = [t.replace('"', '""') for t in query.split()]
    q = " ".join(f'"{t}"' for t in terms)       # each word a phrase: hyphenated names work
    rows = con.execute("SELECT path, snippet(docs, 1, '**', '**', ' ... ', 12) FROM docs WHERE docs MATCH ? "
                       "ORDER BY rank LIMIT 20", (q,)).fetchall()
    con.close()
    for path, snip in rows:
        print(f"{path}: {' '.join(snip.split())}")
    print(f"search: {len(rows)} hit(s) in {len(files)} files", file=sys.stderr)
    return 0 if rows else 1


def check(root):
    out, ok = [], True
    t = read(root / "AGENTS.md") or ""
    n = len(START_RE.findall(t))
    out.append(f"AGENTS.md base block: {n}"); ok &= n == 1
    size = len(t.encode())
    if size > HARD_LIMIT:
        out.append(f"AGENTS.md is {size} bytes > {HARD_LIMIT} (some engines read only the first 32 KiB): FAIL"); ok = False
    elif size > SOFT_LIMIT:
        out.append(f"AGENTS.md is {size} bytes: WARNING, over {SOFT_LIMIT} (shorten a block)")
    else:
        out.append(f"AGENTS.md is {size} bytes (warn {SOFT_LIMIT}, fail {HARD_LIMIT})")
    fr = FRUGAL_START_RE.search(t)
    if fr and n and START_RE.search(t).start() > fr.start():
        out.append("order: base block must come before the frugal-bridge block"); ok = False
    for p in ("CLAUDE.md", "GEMINI.md"):
        c = read(root / p)
        if c is None:
            out.append(f"{p}: missing"); ok = False
        else:
            has = any(l.strip() == POINTER for l in c.splitlines())
            out.append(f"{p} imports AGENTS.md: {has}"); ok &= has
    s = read(root / ".gemini/settings.json")
    try:
        names = json.loads(s or "{}").get("context", {}).get("fileName", [])
        good = "AGENTS.md" in (names if isinstance(names, list) else [names])
        out.append(f".gemini/settings.json loads AGENTS.md: {good}"); ok &= good
    except (json.JSONDecodeError, AttributeError):
        out.append(".gemini/settings.json: invalid JSON"); ok = False
    try:
        k = json.loads(read(root / ".kits.json") or "{}")
        v = k.get("kits", {}).get("base-folder", {}).get("version")
        out.append(f".kits.json base-folder version: {v}"); ok &= v is not None
        for slot, path in (k.get("slots") or {}).items():
            if not (root / path).exists():
                out.append(f"slot {slot} -> {path}: missing"); ok = False
    except json.JSONDecodeError:
        out.append(".kits.json: invalid JSON"); ok = False
    print(("OK" if ok else "PROBLEMS") + "\n" + "\n".join(out))
    return 0 if ok else 1


# ---------------------------------------------------------------- check-public
def scan_text(label, text, words):
    hits = []
    for kind, rx in SECRETS:
        m = rx.search(text)
        if m:
            hits.append(f"{label}: secret? ({kind}) '{m.group(0)[:10]}...'")
    for m in EMAIL.finditer(text):
        if not SAFE_EMAIL_DOMAINS.search(m.group(0)) and m.group(0).rsplit(".", 1)[1].lower() not in FILE_EXTS:
            hits.append(f"{label}: email address '{m.group(0)}'")
    for m in PHONE.finditer(text):
        if sum(ch.isdigit() for ch in m.group(0)) >= 9:
            hits.append(f"{label}: phone number? '{m.group(0)}'")
    for w, rx in words:
        if rx.search(text):
            hits.append(f"{label}: blocked word '{w}'")
    return hits


def word_rx(w):
    return re.compile(r"(?i)(?<![A-Za-z0-9])" + re.escape(w).replace(r"\ ", r"[\s_\-]+") + r"(?![A-Za-z0-9])")


def check_public(target, words_file):
    target = pathlib.Path(target).resolve()
    words = []
    if words_file:
        for line in pathlib.Path(words_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                words.append((line, word_rx(line)))
    hits, n = [], 0
    skip_dirs = {".git", ".brain", "__pycache__", ".base-folder"}
    for dirpath, dirnames, filenames in os.walk(target):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in filenames:
            f = pathlib.Path(dirpath) / fn
            r = rel(f, target)
            n += 1
            hits += scan_text(f"path {r}", r, words)
            try:
                data = f.read_bytes()
            except OSError:
                continue
            if b"\0" in data[:4096]:
                continue
            hits += scan_text(r, data.decode("utf-8", errors="replace"), words)
    if (target / ".git").exists():
        try:
            log = subprocess.run(["git", "-C", str(target), "log", "--all", "-p", "--no-color",
                                  "--format=commit %H%nauthor %an <%ae>%ncommitter %cn <%ce>%n%B"],
                                 capture_output=True, text=True, errors="replace", check=True).stdout
            names = subprocess.run(["git", "-C", str(target), "log", "--all", "--name-only", "--format="],
                                   capture_output=True, text=True, check=True).stdout
            hits += scan_text("git history", log, words)
            hits += scan_text("git history paths", names, words)
        except (OSError, subprocess.CalledProcessError) as e:
            hits.append(f"git history: could not read ({e})")
    seen = []
    for h in hits:
        if h not in seen:
            seen.append(h)
    for h in seen:
        print(h)
    print(f"check-public: {n} files, {len(words)} blocked word(s): {'FAIL' if seen else 'PASS'} ({len(seen)} hit(s))",
          file=sys.stderr)
    return 1 if seen else 0


# ---------------------------------------------------------------- main
def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help", "help"):
        print(__doc__); return 0 if len(argv) >= 2 else 1
    global ROOT_ARG
    cmd, args = argv[1], list(argv[2:])
    if "--root" in args:
        i = args.index("--root"); ROOT_ARG = args[i + 1]; del args[i:i + 2]
    if cmd == "init":
        if not args:
            print("usage: init DIR [--frugal=yes|no]"); return 1
        ans = next((a.split("=", 1)[1].lower() for a in args if a.startswith("--frugal=")), None)
        inst = Installer(args[0])
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = inst.init(ans)
        print("\n".join(inst.log) or "nothing to change")
        print(buf.getvalue().rstrip())
        print(f"Skeleton Base v{VERSION} installed in {inst.d}")
        return rc
    if cmd == "uninstall":
        if not args:
            print("usage: uninstall DIR"); return 1
        print("\n".join(Installer(args[0]).uninstall()) or "nothing to change")
        return 0
    if cmd == "check-public":
        wf = None
        if "--words" in args:
            i = args.index("--words"); wf = args[i + 1]; del args[i:i + 2]
        return check_public(args[0] if args else root_of(), wf)
    root = root_of()
    if cmd == "status":
        return status(root)
    if cmd == "done":
        return done(root, args[0], args[1:]) if args else (print("usage: done RAW PAGE...") or 1)
    if cmd == "lint":
        return lint(root)
    if cmd == "index":
        return build_index(root)
    if cmd == "brief":
        return brief(root, full="--short" not in args)
    if cmd == "search":
        return search(root, " ".join(args))
    if cmd == "check":
        return check(root)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
