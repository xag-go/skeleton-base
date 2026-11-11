"""Tests for tools/brain.py. Run from the repo root: python3 -m unittest -v

Coexistence tests use a COPY of a Frugal-Bridge checkout (kit/ + adapters/) and run its own kit/setup.py from that
copy. Set FRUGAL_BRIDGE_SRC to its path (default: ~/frugal-bridge); they are skipped when it is not found.
All people, projects and facts in these tests are fake.
"""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
BRAIN = REPO / "tools" / "brain.py"
FRUGAL_SRC = pathlib.Path(os.environ.get("FRUGAL_BRIDGE_SRC") or os.path.expanduser("~/frugal-bridge"))
HAVE_FRUGAL = (FRUGAL_SRC / "kit" / "setup.py").is_file()
BASE_SLOTS = {"user": "wiki/me/", "now": "hot.md", "decisions": "wiki/decisions/",
              "map": "wiki/index.md", "sources": "raw/"}


def run(*args, cwd=None, env=None, inp=None):
    e = dict(os.environ, BRAIN_TODAY="2026-11-11")
    e.pop("BRAIN_ROOT", None)
    e.update(env or {})
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, cwd=cwd, env=e,
                          input=inp)


def tree(d, skip=(".base-folder",)):
    d = pathlib.Path(d)
    out = {}
    for p in sorted(d.rglob("*")):
        r = p.relative_to(d).as_posix()
        if r.split("/")[0] in skip:
            continue
        out[r] = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "dir"
    return out


def all_hashes(d):
    return {h for h in tree(d, skip=()).values() if h != "dir"}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="skb-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def init(self, d, *extra):
        r = run(BRAIN, "init", d, "--frugal=no", *extra)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r

    def brain(self, d, *args):
        return run(pathlib.Path(d) / "tools" / "brain.py", *args)

    def fresh(self, name="base"):
        d = self.tmp / name
        self.init(d)
        return d

    def write(self, d, rel, text):
        p = pathlib.Path(d) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p


PAGE = "---\ntitle: {t}\nsources: [{s}]\nupdated: 2026-11-11\nscope: private\n---\n\n# {t}\n\n{b}\n"


class LintTests(Base):
    def lint(self, d):
        return self.brain(d, "lint")

    def test_fresh_init_passes(self):
        d = self.fresh()
        r = self.lint(d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("0 problem(s)", r.stderr)

    def test_good_page_with_true_quote_passes(self):
        d = self.fresh()
        self.write(d, "raw/docs/brief-a.md", "Project A launches on 2026-12-01 in two cities.\n")
        self.write(d, "wiki/projects/project-a.md", PAGE.format(
            t="Project A", s="raw/docs/brief-a.md",
            b='> "Project A launches on 2026-12-01" - raw/docs/brief-a.md\n\nOwner: [[who-i-am]]'))
        self.assertEqual(self.brain(d, "index").returncode, 0)
        self.assertEqual(self.brain(d, "done", "raw/docs/brief-a.md", "wiki/projects/project-a.md").returncode, 0)
        r = self.lint(d)
        self.assertEqual(r.returncode, 0, r.stderr)

    def planted(self, setup, expect):
        d = self.fresh()
        setup(d)
        r = self.lint(d)
        self.assertEqual(r.returncode, 2, f"not caught: {expect}\n{r.stderr}")
        self.assertIn(expect, r.stderr)

    def linked(self, d, rel, text):
        self.write(d, rel, text)
        self.brain(d, "index")

    def test_missing_frontmatter(self):
        self.planted(lambda d: self.linked(d, "wiki/concepts/no-fm.md", "# No frontmatter\n"), "missing frontmatter")

    def test_missing_scope(self):
        self.planted(lambda d: self.linked(d, "wiki/concepts/no-scope.md",
                                           "---\ntitle: X\nsources: [interview]\nupdated: 2026-11-11\n---\n"),
                     "lacks 'scope'")

    def test_bad_scope(self):
        self.planted(lambda d: self.linked(d, "wiki/concepts/bad-scope.md",
                                           PAGE.format(t="X", s="interview", b="x").replace("private", "everyone")),
                     "bad scope")

    def test_missing_source(self):
        self.planted(lambda d: self.linked(d, "wiki/concepts/ghost.md", PAGE.format(t="G", s="raw/docs/nope.md", b="x")),
                     "source raw/docs/nope.md does not exist")

    def test_broken_link(self):
        self.planted(lambda d: self.linked(d, "wiki/concepts/a.md", PAGE.format(t="A", s="interview", b="[[nowhere]]")),
                     "broken link [[nowhere]]")

    def test_orphan(self):
        self.planted(lambda d: self.write(d, "wiki/concepts/lonely.md", PAGE.format(t="L", s="interview", b="x")),
                     "orphan")

    def test_todo(self):
        self.planted(lambda d: self.linked(d, "wiki/concepts/t.md", PAGE.format(t="T", s="interview", b="TODO fix")),
                     "unresolved TODO")

    def test_todo_marker_forms(self):
        for body in ("- TODO call back", "TODO: fix this", "- [ ] TODO send"):
            self.planted(lambda d, b=body: self.linked(d, "wiki/concepts/t.md", PAGE.format(t="T", s="interview", b=b)),
                         "unresolved TODO")

    def test_code_and_prose_mentions_are_not_errors(self):
        d = self.fresh()
        body = ("Lint catches a leftover `TODO`, a `[[link]]` that does not resolve, and orphan or TODO pages.\n\n"
                "```\n> \"exact text\" - raw/<file>\n[[example-page]]\n```\n\nSee [[who-i-am]].")
        self.linked(d, "wiki/concepts/docs-about-lint.md", PAGE.format(t="About lint", s="interview", b=body))
        r = self.lint(d)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_quote_not_in_source(self):
        def s(d):
            self.write(d, "raw/docs/brief-b.md", "Project B budget review is in March.\n")
            self.linked(d, "wiki/projects/project-b.md", PAGE.format(
                t="B", s="raw/docs/brief-b.md", b='> "Project B review is in April" - raw/docs/brief-b.md'))
        self.planted(s, "QUOTE NOT IN SOURCE")

    def test_raw_changed_since_ingest(self):
        def s(d):
            self.write(d, "raw/docs/brief-c.md", "v1\n")
            self.linked(d, "wiki/projects/project-c.md", PAGE.format(t="C", s="raw/docs/brief-c.md", b="x"))
            self.assertEqual(self.brain(d, "done", "raw/docs/brief-c.md", "wiki/projects/project-c.md").returncode, 0)
            self.write(d, "raw/docs/brief-c.md", "v2\n")
        self.planted(s, "changed since ingest")

    def test_new_raw_file_is_a_warning(self):
        d = self.fresh()
        self.write(d, "raw/inbox/new-note.md", "hello\n")
        r = self.lint(d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("NEW raw file", r.stderr)
        st = self.brain(d, "status")
        self.assertIn("NEW raw/inbox/new-note.md", st.stdout)

    def card(self, **kw):
        fm = {"title": "Call the accountant", "status": "todo", "owner": "assistant", "project": "none",
              "updated": "2026-11-11", "scope": "private"}
        fm.update(kw)
        return "---\n" + "".join(f"{k}: {v}\n" for k, v in fm.items()) + "---\n\n# Card\n"

    def test_good_card_passes(self):
        d = self.fresh()
        self.write(d, "wiki/projects/project-a.md", PAGE.format(t="Project A", s="interview", b="x"))
        self.brain(d, "index")
        self.write(d, "board/2026-11-11-call-accountant.md", self.card(project="project-a", owner="twin", due="2026-11-20"))
        r = self.lint(d)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_card_bad_status(self):
        self.planted(lambda d: self.write(d, "board/2026-11-11-x.md", self.card(status="maybe")), "bad status")

    def test_card_owner_not_a_role(self):
        self.planted(lambda d: self.write(d, "board/2026-11-11-x.md", self.card(owner="some-engine")),
                     "is not 'me' or a role")

    def test_card_project_missing(self):
        self.planted(lambda d: self.write(d, "board/2026-11-11-x.md", self.card(project="project-z")),
                     "project 'project-z' has no page")

    def test_card_missing_field(self):
        self.planted(lambda d: self.write(d, "board/2026-11-11-x.md", self.card(updated="")), "lacks 'updated'")

    def test_bad_canvas(self):
        self.planted(lambda d: self.write(d, "maps/bad.canvas", '{"nodes": [{"id": "a", "type": "file", "file": "gone.md",'
                                                                 '"x": 0, "y": 0, "width": 1, "height": 1}], "edges": []}'),
                     "missing gone.md")

    def test_skill_name_mismatch(self):
        self.planted(lambda d: self.write(d, "skills/base-x/SKILL.md", "---\nname: other\ndescription: d\n---\n"),
                     "'name' must equal the folder name")


class InitTests(Base):
    def test_init_empty_dir_has_full_structure(self):
        d = self.fresh()
        for rel in ["README.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md", ".gemini/settings.json", "hot.md",
                    "wiki/index.md", "wiki/log.md", "wiki/glossary.md", "wiki/me/who-i-am.md", "wiki/me/goals.md",
                    "wiki/me/how-to-talk-to-me.md", "board/README.md", "board/board.base", "agents/assistant.md",
                    "agents/twin.md", "progress/agents.log", "maps/README.md", "templates/card.md",
                    "skills/base-ingest/SKILL.md", "skills/base-lint/SKILL.md", "tools/brain.py", ".kits.json",
                    ".gitignore", ".stignore", "SECURITY.md"]:
            self.assertTrue((d / rel).is_file(), rel)
        for sub in ["projects", "clients", "people", "decisions", "concepts", "daily", "sops"]:
            self.assertTrue((d / "wiki" / sub).is_dir(), sub)
        for sub in ["inbox", "docs", "references", "clients", "videos", "exports"]:
            self.assertTrue((d / "raw" / sub).is_dir(), sub)
        self.assertEqual((d / "CLAUDE.md").read_text(), "@AGENTS.md\n")
        self.assertEqual((d / "GEMINI.md").read_text(), "@AGENTS.md\n")
        self.assertEqual(json.loads((d / ".gemini/settings.json").read_text()),
                         {"context": {"fileName": ["AGENTS.md", "GEMINI.md"]}})
        self.assertEqual((d / "AGENTS.md").read_text(), (REPO / "AGENTS.md").read_text())
        k = json.loads((d / ".kits.json").read_text())
        self.assertEqual(k["kits"]["base-folder"]["version"], "1")
        self.assertEqual(k["slots"], BASE_SLOTS)
        self.assertEqual(self.brain(d, "check").returncode, 0)

    def test_init_twice_is_byte_identical(self):
        d = self.fresh()
        before = tree(d, skip=())
        self.init(d)
        self.assertEqual(before, tree(d, skip=()))

    def test_existing_user_files_kept_byte_identical(self):
        d = self.tmp / "own"
        user_agents = "# My own rules\n\nAlways answer in short lines.\n"
        user_claude = "Use tabs, not spaces."           # no trailing newline on purpose
        user_hot = "# my hot\n- writing a book\n"
        self.write(d, "AGENTS.md", user_agents)
        self.write(d, "CLAUDE.md", user_claude)
        self.write(d, "hot.md", user_hot)
        self.write(d, ".gemini/settings.json", '{"theme": "dark", "context": {"fileName": "NOTES.md"}}')
        self.init(d)
        a = (d / "AGENTS.md").read_text()
        self.assertTrue(a.startswith(user_agents))
        self.assertEqual(a.count("<!-- base-folder:start v1 -->"), 1)
        c = (d / "CLAUDE.md").read_text()
        self.assertTrue(c.startswith(user_claude))
        self.assertIn("\n@AGENTS.md\n", c)
        self.assertEqual((d / "hot.md").read_text(), user_hot)
        g = json.loads((d / ".gemini/settings.json").read_text())
        self.assertEqual(g["theme"], "dark")
        self.assertEqual(g["context"]["fileName"], ["NOTES.md", "AGENTS.md", "GEMINI.md"])
        snap = tree(d)
        self.init(d)
        self.assertEqual(snap, tree(d))
        # uninstall gives the user's text back exactly
        r = run(BRAIN, "uninstall", d)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual((d / "AGENTS.md").read_text(), user_agents)
        self.assertEqual((d / "CLAUDE.md").read_text(), user_claude)
        self.assertEqual((d / "hot.md").read_text(), user_hot)
        self.assertEqual(json.loads((d / ".gemini/settings.json").read_text()),
                         {"theme": "dark", "context": {"fileName": ["NOTES.md"]}})

    def test_install_then_uninstall_restores_empty_dir(self):
        d = self.fresh()
        r = run(BRAIN, "uninstall", d)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(list(d.iterdir()), [])

    def test_uninstall_keeps_edited_files(self):
        d = self.fresh()
        (d / "wiki/me/who-i-am.md").write_text(PAGE.format(t="Who I am", s="interview", b="Name: Alex Example"))
        run(BRAIN, "uninstall", d)
        self.assertIn("Alex Example", (d / "wiki/me/who-i-am.md").read_text())
        self.assertFalse((d / "AGENTS.md").exists())
        self.assertFalse((d / "wiki/me/goals.md").exists())

    def test_update_replaces_only_untouched_files(self):
        d = self.fresh()
        old_tool = "# an older brain.py\n"
        (d / "tools/brain.py").write_text(old_tool)
        (d / "templates/card.md").write_text("my own card template\n")
        k = json.loads((d / ".kits.json").read_text())
        k["kits"]["base-folder"]["created"]["tools/brain.py"] = hashlib.sha256(old_tool.encode()).hexdigest()
        (d / ".kits.json").write_text(json.dumps(k, indent=2) + "\n")
        a = (d / "AGENTS.md").read_text()
        (d / "AGENTS.md").write_text(a.replace("start v1 -->", "start v0 -->").replace("# Skeleton Base", "# Old"))
        self.init(d)
        self.assertEqual((d / "tools/brain.py").read_bytes(), BRAIN.read_bytes())
        self.assertEqual((d / "templates/card.md").read_text(), "my own card template\n")
        self.assertEqual((d / "AGENTS.md").read_text(), (REPO / "AGENTS.md").read_text())

    def test_frugal_question(self):
        d = self.tmp / "q"
        r = run(BRAIN, "init", d, "--frugal=yes")
        self.assertIn("kit/setup.py install", r.stdout)
        r = run(BRAIN, "init", self.tmp / "q2", "--frugal=no")
        self.assertIn("Frugal-Bridge: skipped", r.stdout)


class ToolTests(Base):
    def test_search_finds_hyphenated_terms(self):
        d = self.fresh()
        self.write(d, "wiki/projects/project-a.md", PAGE.format(t="Project A", s="interview",
                                                                  b="The north-star metric is weekly-active-readers."))
        r = self.brain(d, "search", "weekly-active-readers")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("wiki/projects/project-a.md", r.stdout)
        self.assertTrue((d / ".brain/search.db").is_file())
        self.assertEqual(self.brain(d, "search", "zzzunfindable").returncode, 1)

    def test_brief_full_by_default(self):
        d = self.fresh()
        out = self.brain(d, "brief").stdout
        for rel in ["AGENTS.md", "hot.md", "wiki/index.md", "agents/assistant.md", "agents/twin.md",
                    "wiki/me/who-i-am.md", "wiki/me/goals.md", "wiki/me/how-to-talk-to-me.md"]:
            self.assertIn(f"===== FILE: {rel} =====", out)
        self.assertNotIn("wiki/me/goals.md =====", self.brain(d, "brief", "--short").stdout)

    def test_check_size_limits_and_pointer(self):
        d = self.fresh()
        a = (d / "AGENTS.md").read_text()
        (d / "AGENTS.md").write_text(a + "x" * 23000 + "\n")
        r = self.brain(d, "check")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("WARNING", r.stdout)
        (d / "AGENTS.md").write_text(a + "x" * 31000 + "\n")
        r = self.brain(d, "check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL", r.stdout)
        (d / "AGENTS.md").write_text(a)
        (d / "CLAUDE.md").write_text("Read AGENTS.md first.\n")
        self.assertEqual(self.brain(d, "check").returncode, 1)
        (d / "CLAUDE.md").write_text("@AGENTS.md\n")
        (d / ".gemini/settings.json").write_text("{not json")
        self.assertEqual(self.brain(d, "check").returncode, 1)


class CheckPublicTests(Base):
    def setUp(self):
        super().setUp()
        self.words = self.tmp / "words.txt"
        self.words.write_text("zebrafruit\nAcme Widgets\n")
        self.repo = self.tmp / "pub"
        self.write(self.repo, "README.md", "A clean public readme. Contact: noreply@skeleton-base.invalid\n"
                                           "Dates like 2026-11-11 are fine.\n"
                                           "+@unittest.skipUnless(ok) and \\n@AGENTS.md are not emails.\n")

    def cp(self, d=None):
        return run(BRAIN, "check-public", "--words", self.words, d or self.repo)

    def test_clean_passes(self):
        r = self.cp()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_catches_key(self):
        self.write(self.repo, "notes.md", "key = " + "sk-" + "ant-" + "xxxx\n")
        r = self.cp()
        self.assertEqual(r.returncode, 1)
        self.assertIn("anthropic key", r.stdout)

    def test_catches_email(self):
        self.write(self.repo, "notes.md", "mail me: alex.example" + "@" + "corpmail.net\n")
        r = self.cp()
        self.assertEqual(r.returncode, 1)
        self.assertIn("email address", r.stdout)

    def test_catches_phone(self):
        self.write(self.repo, "notes.md", "call +44 20 " + "7946 0958\n")
        r = self.cp()
        self.assertEqual(r.returncode, 1)
        self.assertIn("phone number", r.stdout)

    def test_catches_blocked_word_in_content_path_and_history(self):
        self.write(self.repo, "notes.md", "made for ZebraFruit only\n")
        r = self.cp()
        self.assertEqual(r.returncode, 1)
        self.assertIn("blocked word 'zebrafruit'", r.stdout)
        (self.repo / "notes.md").unlink()
        self.write(self.repo, "acme-widgets/plan.md", "clean\n")
        r = self.cp()
        self.assertIn("path acme-widgets/plan.md: blocked word 'Acme Widgets'", r.stdout)
        shutil.rmtree(self.repo / "acme-widgets")
        self.assertEqual(self.cp().returncode, 0)
        g = ["git", "-C", str(self.repo)]
        subprocess.run(g + ["init", "-q"], check=True)
        subprocess.run(g + ["add", "."], check=True)
        subprocess.run(g + ["-c", "user.name=T", "-c", "user.email=t@x.invalid", "commit", "-qm",
                            "first draft for zebrafruit"], check=True)
        r = self.cp()
        self.assertEqual(r.returncode, 1)
        self.assertIn("git history: blocked word 'zebrafruit'", r.stdout)


@unittest.skipUnless(HAVE_FRUGAL, f"Frugal-Bridge not found at {FRUGAL_SRC} (set FRUGAL_BRIDGE_SRC)")
class FrugalCoexistenceTests(Base):
    def setUp(self):
        super().setUp()
        self.fb = self.tmp / "frugal-copy"
        ign = shutil.ignore_patterns("__pycache__", "*.pyc")
        for part in ("kit", "adapter", "adapters"):        # its layout changed over time: copy what exists
            if (FRUGAL_SRC / part).is_dir():
                shutil.copytree(FRUGAL_SRC / part, self.fb / part, ignore=ign)
        self.fake_home = self.tmp / "home"                 # never touch the real user's tool configs
        self.fake_home.mkdir()

    def frugal(self, cmd, d):
        extra = ["--hosts", "claude-code,gemini"] if cmd == "install" else []
        r = run(self.fb / "kit" / "setup.py", cmd, d, *extra, env={"HOME": str(self.fake_home)})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r

    def frugal_check(self, d):
        return run(self.fb / "kit" / "setup.py", "check", d, env={"HOME": str(self.fake_home)})

    def blocks_once(self, d, frugal=True):
        a = (d / "AGENTS.md").read_text()
        self.assertEqual(a.count("<!-- base-folder:start"), 1)
        self.assertEqual(a.count("<!-- base-folder:end -->"), 1)
        if frugal:
            self.assertEqual(a.count("<!-- frugal-bridge:start"), 1)
            self.assertEqual(a.count("<!-- frugal-bridge:end -->"), 1)
            self.assertLess(a.index("<!-- base-folder:start"), a.index("<!-- frugal-bridge:start"))

    def base_then_frugal(self):
        d = self.fresh()
        self.frugal("install", d)
        return d

    def frugal_then_base(self):
        d = self.tmp / "fb-first"
        self.frugal("install", d)
        self.write(d, "USER.md", "# USER.md\n\n- Name: Alex Example\n- Language: English, short answers\n")
        self.write(d, "PROGRESS.md", "# PROGRESS.md\n\n## Current task\nShip the project-a landing page by 2026-12-01\n")
        self.write(d, "DECISIONS.md", "# DECISIONS.md\n\n| id | decision |\n|---|---|\n| D1 | Use plain files |\n")
        self.write(d, "MAP.md", "# MAP.md\n\n- Projects: project-a -> ./project-a\n")
        self.write(d, "sources/market-notes.md", "Fake market notes for project-a.\n")
        before = {r: h for r, h in tree(d, skip=()).items() if h != "dir"}
        self.frugal_block = (d / "AGENTS.md").read_text()
        self.frugal_entry = json.loads((d / ".kits.json").read_text())["kits"]["frugal-bridge"]
        self.init(d)
        return d, before

    def test_a_base_first_then_frugal(self):
        d = self.base_then_frugal()
        self.blocks_once(d)
        for f in ("USER.md", "PROGRESS.md", "DECISIONS.md"):
            self.assertFalse((d / f).exists(), f"Frugal created {f} although the base owns the slots")
        k = json.loads((d / ".kits.json").read_text())
        self.assertIn("frugal-bridge", k["kits"])
        self.assertEqual(k["slots"], BASE_SLOTS)
        self.assertEqual((d / "CLAUDE.md").read_text(), "@AGENTS.md\n")
        self.assertTrue(self.frugal_check(d).stdout.startswith("OK"))
        self.assertEqual(self.brain(d, "check").returncode, 0)
        self.assertEqual(self.brain(d, "lint").returncode, 0)
        snap = tree(d)
        self.init(d)                    # re-run both: no change
        self.frugal("install", d)
        self.assertEqual(snap, tree(d))
        self.blocks_once(d)

    def test_b_frugal_first_then_base_imports(self):
        d, before = self.frugal_then_base()
        self.blocks_once(d)
        after = all_hashes(d)
        # every original file is still present by hash (in place or in raw/exports/); the two shared files
        # are edited in place: AGENTS.md keeps Frugal's text byte-identical, .kits.json keeps Frugal's entry
        lost = [r for r, h in before.items() if h not in after and r not in ("AGENTS.md", ".kits.json")]
        self.assertEqual(lost, [], "files lost by hash")
        self.assertIn(self.frugal_block.rstrip("\n"), (d / "AGENTS.md").read_text())
        k = json.loads((d / ".kits.json").read_text())
        self.assertEqual(k["slots"], BASE_SLOTS)
        self.assertEqual(k["kits"]["frugal-bridge"], self.frugal_entry)
        self.assertIn("Alex Example", (d / "wiki/me/frugal-user.md").read_text())
        self.assertIn("project-a landing page", (d / "hot.md").read_text())
        self.assertIn("Use plain files", (d / "wiki/decisions/frugal-decisions.md").read_text())
        self.assertIn("project-a -> ./project-a", (d / "wiki/index.md").read_text())
        self.assertTrue((d / "raw/inbox/frugal-sources/market-notes.md").is_file())
        self.assertTrue((d / "raw/exports/frugal-2026-11-11/USER.md").is_file())
        for stub in ("USER.md", "PROGRESS.md", "DECISIONS.md", "MAP.md", "sources/MOVED.md"):
            self.assertTrue((d / stub).read_text().startswith("# Moved"), stub)
        self.assertTrue(self.frugal_check(d).stdout.startswith("OK"))
        self.assertEqual(self.brain(d, "check").returncode, 0)
        r = self.brain(d, "lint")
        self.assertEqual(r.returncode, 0, r.stderr)
        snap = tree(d)
        self.init(d)
        self.assertEqual(snap, tree(d))

    def test_c_uninstall_frugal_leaves_base_intact(self):
        d = self.base_then_frugal()
        self.frugal("uninstall", d)
        ref = self.tmp / "ref"
        self.init(ref)
        self.assertEqual((d / "AGENTS.md").read_text(), (ref / "AGENTS.md").read_text())
        k = json.loads((d / ".kits.json").read_text())
        self.assertNotIn("frugal-bridge", k["kits"])
        self.assertEqual(k["slots"], BASE_SLOTS)
        self.assertEqual(self.brain(d, "check").returncode, 0)
        self.assertEqual(self.brain(d, "lint").returncode, 0)
        self.assertEqual(tree(d, skip=(".base-folder", ".frugal-bridge")), tree(ref))

    def test_d_uninstall_base_exports_slots_back(self):
        d, _ = self.frugal_then_base()
        (d / "wiki/me/who-i-am.md").write_text(PAGE.format(t="Who I am", s="interview", b="- Name: Alex Example"))
        r = run(BRAIN, "uninstall", d)
        self.assertEqual(r.returncode, 0, r.stdout)
        a = (d / "AGENTS.md").read_text()
        self.assertNotIn("base-folder:start", a)
        self.assertEqual(a.count("<!-- frugal-bridge:start"), 1)
        k = json.loads((d / ".kits.json").read_text())
        self.assertNotIn("base-folder", k["kits"])
        self.assertIn("frugal-bridge", k["kits"])
        self.assertEqual(k["slots"]["user"], "USER.md")
        self.assertEqual(k["slots"]["now"], "PROGRESS.md")
        self.assertIn("Alex Example", (d / "USER.md").read_text())
        self.assertIn("project-a landing page", (d / "PROGRESS.md").read_text())
        self.assertIn("Use plain files", (d / "DECISIONS.md").read_text())
        self.assertIn("project-a -> ./project-a", (d / "MAP.md").read_text())
        self.assertTrue((d / "sources/market-notes.md").is_file())
        c = self.frugal_check(d)
        self.assertTrue(c.stdout.startswith("OK"), c.stdout)
        self.frugal("install", d)       # Frugal still works on its own after the base left
        self.assertTrue(self.frugal_check(d).stdout.startswith("OK"))

    def test_brief_contains_frugal_core(self):
        d = self.base_then_frugal()
        out = self.brain(d, "brief").stdout
        self.assertIn("<!-- frugal-bridge:start", out)
        core_first_line = (self.fb / "kit" / "AGENTS.md").read_text().splitlines()[0]
        self.assertIn(core_first_line, out)


if __name__ == "__main__":
    unittest.main()
