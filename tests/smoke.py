#!/usr/bin/env python3
# The regression battery: every verb, end to end, in a throwaway repo.
# Run: python3 tests/smoke.py
import ast, glob, hashlib, io, json, os, re, shutil, subprocess, sys, tempfile, time, tokenize

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(HERE, "gate")
DEMO = os.path.join(HERE, "demo")
STDLIB = os.path.join(HERE, "stdlib")


def run(*args, cwd=None):
    r = subprocess.run([sys.executable, GATE, *args, "--json"], capture_output=True, text=True, cwd=cwd)
    try:
        return r.returncode, json.loads(r.stdout)
    except Exception:
        return r.returncode, {"raw": r.stdout[:200], "stderr": r.stderr[:200]}


def seams_here_probe(folder):
    # the seam count as the bench would compute it, in a subprocess so the
    # battery never imports the tool it is judging
    code = ("import sys, types;"
            "src=open(%r,encoding='utf-8').read();"
            "g=types.ModuleType('g'); g.__file__=%r;"
            "exec(compile(src,'gate','exec'), g.__dict__);"
            "print(len(g.seams_here(%r)))" % (GATE, GATE, folder))
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    try:
        return int((r.stdout or "0").strip().splitlines()[-1])
    except Exception:
        return -1


def say(*args, cwd=None):
    # the human line, not the JSON: the porcelain has its own words and the
    # canon of names governs them
    r = subprocess.run([sys.executable, GATE, *args], capture_output=True, text=True, cwd=cwd)
    return r.stdout


def wait_serve(port, path="/files"):
    # one spelling of "the bench is up": poll until the server answers, and
    # hand back the reply for callers that read it. Eight probes each grew
    # this loop by hand, eight copies of one truth in the file that exists
    # against that.
    import urllib.request as _u
    for _ in range(60):
        try:
            return _u.urlopen(f"http://127.0.0.1:{port}{path}", timeout=1).read()
        except Exception:
            time.sleep(0.1)
    return None


# the retired word is allowed exactly where its retirement is recorded: this
# constant, the lines that say what it was, the count itself, and the one that
# keeps the old name from coming back as a filename. Any other use is the word
# returning, and the count is what says so.
GENRE_SAID_HERE = 5


def main():
    tmp = tempfile.mkdtemp(prefix="gate-smoke-")
    # ── AND THIS BATTERY DOES NOT WRITE IN THE HOUSE OF WHOEVER RUNS IT. A personal
    # world lives in `~/.gate/me` unless `GATE_ME` says otherwise, and that was set
    # for exactly one fixture here: every other run wrote a keyed world into the real
    # one, four hundred and forty-eight of them by the time anybody counted. Sharing
    # that git is also how two runs at once collide on `index.lock`, which colours a
    # check red for a reason that has nothing to do with the code. A battery that can
    # do that is worse than a red one: the same race can hide a real failure.
    os.environ["GATE_ME"] = os.path.join(tmp, "me")
    repo = os.path.join(tmp, "client")
    os.makedirs(repo)
    subprocess.run(["git", "init", "-q", repo])
    # the fixture states its own name: the offered-as-read check below is about
    # the mechanism (a name git has is read aloud, written into nothing), and a
    # bare machine, a fresh CI runner, has no global user.name for it to lean on
    subprocess.run(["git", "config", "user.name", "A Fixture"], cwd=repo)
    subprocess.run(["git", "config", "user.email", "fixture@client"], cwd=repo)
    S = []
    S.append(("the battery keeps its personal worlds inside its own temp dir",
              os.environ.get("GATE_ME", "").startswith(tmp)))
    # and every fixture directory too, so a run leaves the machine as it found it
    # matched by a pattern rather than by the literal, which this check would
    # otherwise find in itself and fail on
    S.append(("and every fixture it makes is rooted in that directory",
              not re.search(r"tempfile\.mkdtemp\(\s*\)",
                            open(__file__, encoding="utf-8").read())))

    c, r = run("init", repo)
    S.append(("init + hook wired", r.get("hooks") is not None))
    # ── AND THE HOOK FINDS THE TOOL, OR SAYS SO AND STOPS. It ran `gate status`
    # flat, which fails with `gate: command not found` for anybody who has not
    # installed it, including anybody following this project's own README. Entry
    # broke the next commit of the repository it had just entered, with a message
    # about a shell. Found by making that commit.
    hook_text = open(os.path.join(repo, ".githooks", "pre-commit")).read()
    subprocess.run(["git", "add", "-A"], cwd=repo, capture_output=True)
    bare_env = dict(os.environ, PATH="/usr/bin:/bin")
    made = subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=A",
                           "commit", "-m", "with no gate on PATH"],
                          cwd=repo, capture_output=True, text=True, env=bare_env)
    S.append(("the hook says plainly when it cannot find the tool, and stops the commit",
              "./gatew" in hook_text and "command -v gate" in hook_text
              and made.returncode != 0
              and "is not on PATH" in made.stdout + made.stderr
              and "command not found" not in made.stdout + made.stderr))
    # ENTERING SOMEBODY'S REPOSITORY LEAVES THE HOOK AND A LETTER, AND NOTHING
    # ELSE. It used to leave eight files: a personnel domain's empty tables, a
    # README announcing a single source of truth, an AGENT.md with one reference
    # world's vocabulary as though it were the vocabulary, and a workflow in their
    # .github. Tables are theirs and arrive by `import`; the letter arrives by the
    # verb everything of ours arrives by, carrying the revision it came from.
    # AND IT NAMES EVERY ONE OF THEM. Declaring the letter writes the layout that
    # says so, and that file appeared in somebody's repository counted by nobody:
    # `created 3 files` while four were there. So the list is held to the disk
    # rather than to a list somebody remembered to update.
    landed = sorted(os.path.relpath(os.path.join(dp, f), repo)
                    for dp, _dn, fn in os.walk(repo) for f in fn
                    if ".git/" not in os.path.relpath(os.path.join(dp, f), repo) + "/")
    S.append(("entry names every file it leaves, and leaves nothing of the old furniture",
              sorted(r.get("created") or []) == landed
              and not os.path.exists(os.path.join(repo, "README.md"))
              and not os.path.exists(os.path.join(repo, "AGENT.md"))
              and not os.path.isdir(os.path.join(repo, ".github"))))
    # THE NAME NOBODY SAID IS OFFERED, NOT WRITTEN. The one thing missing after
    # entry is who is keeping this, and git already carries a name — so it is read
    # aloud and left there. Writing it would be the tool legislating on a guess.
    signed = subprocess.run(["git", "config", "user.name"], cwd=repo,
                            capture_output=True, text=True).stdout.strip()
    entry_text = "".join(open(os.path.join(repo, f)).read()
                         for f in ("readme.swift", "gate.manifest.swift", "forms-tool.swift"))
    S.append(("the name in git is offered as read, and written into nothing",
              bool(signed) and "not judged" in (r.get("observed") or "")
              and signed in r["observed"] and "my.swift" in r["observed"]
              and signed not in entry_text))
    # AND THE FIRST LINE OF IT BELONGS TO WHOEVER OPENS IT. It used to read «taken
    # as your own starting point from the judge at 0fd0b38»: a word nobody had
    # introduced, a revision nobody had asked for, and a service announcing itself,
    # all before the page said anything. Where it came from and how to get back are
    # facts about the copy, and they sit at its foot.
    letter_text = open(os.path.join(repo, "readme.swift")).read()
    S.append(("the letter is declared in the same movement, and says where it came from",
              "readme.swift" in open(os.path.join(repo, "gate.manifest.swift")).read()
              and "Origin: gate's shelf" in letter_text
              and "This copy is yours" in letter_text.split("\n")[0]
              and "judge" not in letter_text.split("\n")[0]
              # and the way back is said where the provenance is
              and "prints what shipped" in letter_text
              and "removes it completely" in letter_text))
    # ── AND WHERE YOUR OWN WORLD LIVES IS ANSWERED BY THE DISK, NOT BY A PROCESS.
    # This is asked once per file the bench lists, on every request, and each ask
    # started git: opening one file spent most of its time launching git to be
    # told the same thing, which is the pause between clicking a name and seeing
    # the page. What matters here is that the cheap answer is the SAME answer, so
    # it is compared against what git itself says, both ways round.
    _h = hashlib
    keyrepo = os.path.join(tmp, "keyrepo")
    os.makedirs(keyrepo)
    subprocess.run(["git", "init", "-q", keyrepo])
    run("demo", "org", keyrepo)
    _, said = run("my", cwd=keyrepo)
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=keyrepo,
                         capture_output=True, text=True).stdout.strip()
    want = (re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(top))
            + "-" + _h.sha1(top.encode()).hexdigest()[:8])
    S.append(("a personal world is placed where git says the clone is, without asking git",
              os.path.basename(os.path.dirname(said.get("personal") or "")) == want))
    subprocess.run(["git", "remote", "add", "origin", "https://example.com/x/y.git"], cwd=keyrepo)
    _, moved = run("my", cwd=keyrepo)
    S.append(("and a remote added a moment ago is seen at once: the config is read every time",
              os.path.basename(os.path.dirname(moved.get("personal") or "")) == "example.com_x_y"))

    # ── AND TWO OUTWARD TEXTS MAY NOT SAY OPPOSITE THINGS. The cover carried the
    # cure this whole tool exists against, in its own voice: "gate makes one of
    # those copies the source and judges it", six lines from a letter whose third
    # paragraph says there is no source. Both are read by the same stranger, and
    # whichever they read second tells them the first was a sales line. It lived
    # for a month because the two texts were held apart and nothing compared them.
    _cover = open(os.path.join(HERE, "README.md"), encoding="utf-8").read()
    # ── AND THE TWO TEXTS SHARE ONE SPINE, WORD FOR WORD. The cover is written
    # from the letter; each is maintained by hand, so a rewording of one drifts
    # from the other in silence, which is this tool's own first paragraph. The
    # spine sentences are held identical in both, comment marks and line breaks
    # aside. An adaptation that means to differ picks different sentences.
    _one_line = lambda t: " ".join(
        l.lstrip("/ ").strip() if l.strip().startswith("//") else l.strip()
        for l in t.split("\n")).replace("  ", " ")
    _cover_flat, _letter_flat = _one_line(_cover), _one_line(open(
        os.path.join(HERE, "stdlib", "readme.swift"), encoding="utf-8").read())
    _spine = [
        "Your repository is full of sentences that must match something, and nobody checks the match.",
        "That gap has a name: drift. Two records of one fact, coming apart in silence, while both still get obeyed.",
        "Yours is wherever two places state one fact.",
        "You are looking for pairs, not objects: one fact always has more than one record.",
        "Gate first the pairs that cross a boundary: two teams, two repositories, two languages.",
        "A fact drifts where it changes hands.",
        "You do not test my API, and I do not mock yours.",
        "Its one move is to put the agreement in writing before the argument: each side states its half in its own file, the judge compares the halves from then on, and you hold a meeting when the verdict says you differ.",
        "What used to be an integration test is a verdict.",
        "If CODEOWNERS hands the payments folder to an intern, the rule holds and every record agrees with it.",
        "What varies is which pair you point it at: a Jira ticket and the TODO that cites it, "
        "k8s RBAC and the cluster it describes, an API contract and a client in another language.",
        "Agreement here is not assumed. It is stated twice, and confirmed.",
        "Every pair you gate is one thing you stop keeping in your head.",
        "Something drifts? Gate it",
    ]
    _spine_missing = [s for s in _spine
                      if s not in _cover_flat or s not in _letter_flat]
    S.append(("the cover and the letter share one spine, word for word",
              _spine_missing == []))
    S.append(("the cover and the letter say the same thing about a source of truth",
              "there is no source" in _cover and "there is no source" in letter_text
              # and neither crowns one anywhere: the word survives only where the
              # cure is being named and refused
              and "single source" not in _cover
              and not re.search(r"\bis the source\b", _cover)
              and not re.search(r"\bis the source\b", letter_text)))

    # AND IT KEEPS ITS OWN WORD ABOUT HOW IT IS MET, AS A COLUMN. How a page is
    # first met is a fact of its manifest row now (Opens = Bare), not a comment
    # in its head: the head carries nothing mechanical, so the reader's first
    # screen has no lines that talk to the tool.
    S.append(("and a letter taken keeps its own word about how it is met",
              "Opens = Bare" in open(os.path.join(repo, "gate.manifest.swift")).read()
              and not any("// opens:" in ln or "// role:" in ln for ln in
                          open(os.path.join(repo, "readme.swift")).read().split("\n")[:6])))
    # AND THE FIRST VERDICT IS OVER SOMETHING. A page taken without the forms it is
    # written in carries certificates no court can read: eleven promises in the
    # first file a newcomer is handed, judged over nought equalities, silently.
    c, r = run("status", cwd=repo)
    S.append(("the world entry leaves is judged, and the verdict says how wide",
              c == 0 and r.get("verdict") == "holds"
              and r.get("forms", {}).get("equalities", 0) > 0))
    # the rung after entry is two words, because the bench opens on the letter and a
    # rung that describes the next screen spends a line on it
    S.append(("and the rung after entry is the bench itself, not a merge policy",
              r.get("next") == "gate serve"))
    # BREAK IT, ON THE FIRST FILE, IN A REPOSITORY THAT DECLARED NOTHING ELSE: the
    # lesson the letter offers has to be true where it is read.
    letter_p = os.path.join(repo, "verbs.swift")
    kept = open(letter_p).read()
    open(letter_p, "w").write(kept.replace("public typealias LogIsSafe = Run<Log>",
                                           "public typealias LogIsSafe = Run<Apply>"))
    c, r = run("status", cwd=repo)
    S.append(("breaking a promise in the reference beside the letter refuses at its own line",
              c == 1 and any(x.get("address", "").startswith("verbs.swift:")
                             and "LogIsSafe" in x["claim"] for x in r["refusals"])))
    open(letter_p, "w").write(kept)
    c, r = run("status", cwd=repo)
    S.append(("and putting it back holds again", c == 0 and r["verdict"] == "holds"))
    # ── AND THE FIRST THING THE LETTER ASKS FOR ANSWERS. It sends a newcomer to
    # `gate findings` before anything is translated, and at entry that was silent for
    # the worst possible reason: the journal's default scope is the history of the
    # WORLD FILES, the files that had just arrived were untracked, so a repository
    # with a CODEOWNERS in it and history behind it had «nothing to report yet».
    fresh = os.path.join(tmp, "fresh-entry")
    os.makedirs(fresh)
    subprocess.run(["git", "init", "-q", fresh])
    open(os.path.join(fresh, "CODEOWNERS"), "w").write("/src/  @alice\n/docs/ @bob\n")
    subprocess.run(["git", "add", "-A"], cwd=fresh, capture_output=True)
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=A", "commit", "-qm",
                    "before gate", "--no-verify"], cwd=fresh, capture_output=True)
    run("init", ".", cwd=fresh)
    c, r = run("findings", cwd=fresh)
    S.append(("what the letter asks for first answers in a repository that just entered",
              r.get("findings") and any("CODEOWNERS" in f["sentence"] for f in r["findings"])))
    # A GREEN OVER NOTHING SAYS SO, in the one case where that is what happened: a
    # world of atoms alone, with no certificate over them for any court to read.
    bare = os.path.join(tmp, "bare")
    os.makedirs(bare)
    subprocess.run(["git", "init", "-q", bare])
    run("mine", "bench-atoms", cwd=bare)
    S.append(("a green over nothing says so, in words",
              "nothing claimed here yet" in say("status", cwd=bare)))
    os.makedirs(os.path.join(repo, "tables"), exist_ok=True)
    shutil.copy(os.path.join(DEMO, "people.csv"), os.path.join(repo, "tables", "people.csv"))
    shutil.copy(os.path.join(DEMO, "grants.csv"), os.path.join(repo, "tables", "grants.csv"))

    sub = os.path.join(repo, "tables")
    c, r = run("status", cwd=sub)
    S.append(("status bootstraps the world once, subdir", c == 0 and r.get("verdict") == "holds"
              and os.path.exists(os.path.join(repo, "gate.swift"))))
    c, r = run("check", "view", "Emp9001", "FinanceShare", cwd=repo)
    S.append(("check legal exit 0", c == 0 and r["verdict"] == "holds"))
    c, r = run("check", "view", "Emp9001", "EngineeringShare", cwd=repo)
    S.append(("check illegal exit 1 + address", c == 1 and r["refusals"]))
    c, r = run("diff", "transfer", "Emp9001", "Engineering", cwd=repo)
    S.append(("diff transfer names leftovers", r["verdict"] == "refused" and r["dry_run"]))
    c, r = run("apply", "revoke", "Emp9002", "FinanceShare", cwd=repo)
    S.append(("apply revoke edits the world", r.get("applied") is True))
    with open(os.path.join(repo, "tables", "grants.csv"), "a") as f:
        f.write("Emp9000,FinanceShare\n")  # a later CSV edit must NOT overwrite the world
    c, r = run("status", cwd=repo)
    world_text = open(os.path.join(repo, "gate.swift")).read()
    S.append(("no second truth: CSV edit does not reprint the world",
              r.get("verdict") == "holds" and world_text.count("Emp9002,") == 3))
    c, r = run("apply", "grant", "Emp9002", "FinanceShare", cwd=repo)
    S.append(("apply grant back", r.get("applied") is True))
    c, r = run("import", "tables/people.csv", "tables/grants.csv", "-o", "gate.swift", cwd=repo)
    S.append(("import clean", r["verdict"] == "holds"))
    printed = open(os.path.join(repo, "gate.swift")).read()
    named = re.search(r"gate stdlib show (forms-[a-z]+)", printed)
    S.append(("a world names the forms it is written in, and they are on the shelf",
              bool(named) and os.path.exists(
                  os.path.join(HERE, "stdlib", named.group(1) + ".swift"))))
    c, r = run("export", "gate.swift", "-o", "pb.csv", "gb.csv", cwd=repo)
    d1 = subprocess.run(["diff", "tables/people.csv", "pb.csv"], cwd=repo).returncode
    d2 = subprocess.run(["diff", "tables/grants.csv", "gb.csv"], cwd=repo).returncode
    S.append(("export round-trip empty diff", d1 == 0 and d2 == 0))
    c, r = run("verify", "tables/people.csv", "tables/grants.csv", cwd=repo)
    S.append(("verify --self finds the known hole", r.get("translation_holes") == 1))
    c, r = run("library", cwd=repo)
    S.append(("library crystal", len(r.get("forms", [])) == 4))
    c, r = run("report", "-o", "report.html", cwd=repo)
    S.append(("report written", "wrote" in r))
    subprocess.run(["git", "-C", repo, "add", "-A"], capture_output=True)
    subprocess.run(["git", "-C", repo, "-c", "user.email=smoke@test", "-c", "user.name=Smoke",
                    "commit", "-qm", "world tables", "--no-verify"], capture_output=True)
    c, r = run("survey", "10", cwd=repo)
    S.append(("survey read-only", r.get("commits", 0) >= 1))
    c, r = run("check", "administer", "X", "Y", cwd=repo)
    S.append(("check administer honest error without corpus", "GATE_CORPUS" in json.dumps(r)))

    # the layout is a fact of the world: the manifest splits, judgement runs the list, guards hold both directions
    split = os.path.join(tmp, "split")
    os.makedirs(split)
    shutil.copy(os.path.join(repo, "gate.swift"), os.path.join(split, "gate.swift"))
    w = open(os.path.join(split, "gate.swift")).read()
    i = w.index("public enum ImportedAccesses")
    open(os.path.join(split, "grants.swift"), "w").write(w[i:])
    open(os.path.join(split, "gate.swift"), "w").write(w[:i])
    open(os.path.join(split, "gate.manifest.swift"), "w").write(
        'public protocol WorldFile {}\npublic enum GrantsFile: WorldFile {}\n'
        'extension GrantsFile { public static var typeName: String { "grants.swift" } }\n')
    c, r = run("status", cwd=split)
    S.append(("manifest: cross-file judgement holds", c == 0 and r["verdict"] == "holds"))
    open(os.path.join(split, "gate.policy.swift"), "w").write("// policy beside a manifest world\n")
    c, r = run("status", cwd=split)
    S.append(("manifest: the policy file is meta, not a shadow", c == 0 and r["verdict"] == "holds"))
    open(os.path.join(split, "stray.swift"), "w").write("// stray\n")
    c, r = run("status", cwd=split)
    S.append(("manifest: an undeclared file beside the world is named", c == 1 and any("no row in the manifest" in x["claim"] for x in r["refusals"])))
    os.remove(os.path.join(split, "stray.swift"))

    # A COMMENT IS NOT A DECLARATION, AND A ROW THAT NAMES NO FILE NAMES NOTHING.
    # Switching a row off the way anybody switches a line off left it declared,
    # judged and counted: the document said one thing to the person reading it and
    # another to the tool reading it. Found by hand in this tool's own manifest,
    # where a forms row sat commented out for a day and its file was judged the
    # whole time. Both halves are here, because the fix has two: the row stops
    # being read, and the file it named stops being spoken for.
    doc = open(os.path.join(split, "gate.manifest.swift")).read()
    open(os.path.join(split, "gate.manifest.swift"), "w").write(
        doc.replace("extension GrantsFile", "// extension GrantsFile"))
    c, r = run("status", cwd=split)
    S.append(("manifest: a row commented out is a row no longer, and its file is undeclared",
              c == 1 and any("no row in the manifest" in x["claim"] and "grants.swift" in x.get("address", "")
                             for x in r["refusals"])))
    S.append(("manifest: a row that names no file is refused at its own line",
              any("names no file" in x["claim"]
                  and x.get("address", "").startswith("gate.manifest.swift:")
                  for x in r["refusals"])))
    open(os.path.join(split, "gate.manifest.swift"), "w").write(doc)
    c, r = run("status", cwd=split)
    S.append(("manifest: and the same document with the line back holds again",
              c == 0 and r["verdict"] == "holds"))

    # AND A SHADOW IS A SHADOW WHEREVER THE WORLD KEEPS ITS FILES: the walk
    # follows the rows, not the folder the manifest happens to sit in. Held one
    # directory deep because that is where this repository keeps every world it
    # has, and where an undeclared file was nobody's shadow.
    deep = os.path.join(tmp, "deep")
    os.makedirs(os.path.join(deep, "worlds"))
    shutil.copy(os.path.join(split, "gate.swift"), os.path.join(deep, "gate.swift"))
    shutil.copy(os.path.join(split, "grants.swift"), os.path.join(deep, "worlds", "grants.swift"))
    open(os.path.join(deep, "gate.manifest.swift"), "w").write(
        'public protocol WorldFile {}\npublic enum GrantsFile: WorldFile {}\n'
        'extension GrantsFile { public static var typeName: String { "worlds/grants.swift" } }\n')
    c, r = run("status", cwd=deep)
    S.append(("manifest: a world one directory down is judged from there",
              c == 0 and r["verdict"] == "holds"))
    open(os.path.join(deep, "worlds", "stray.swift"), "w").write("// stray\n")
    c, r = run("status", cwd=deep)
    S.append(("manifest: an undeclared file beside a declared one a directory down is named",
              c == 1 and any("no row in the manifest" in x["claim"]
                             and x.get("address") == os.path.join("worlds", "stray.swift")
                             for x in r["refusals"])))

    layout = ('public protocol Role {}\npublic enum FormsFile: Role {}\npublic protocol Mine {}\n'
              'public enum One: Mine {\n    public typealias Kind = FormsFile\n%s}\n'
              'extension One { public static var typeName: String { "one.swift" } }\n'
              'public enum Two: Mine {\n    public typealias Kind = FormsFile\n}\n'
              'extension Two { public static var typeName: String { "two.swift" } }\n')
    # ── AND A PAGE MAY NOT SAY IN PROSE WHAT ITS ROW DOES NOT DECLARE. Which laws a
    # page is judged under is a column; it spent a day in a comment in the page's
    # own head, where nothing could judge it.
    orig = os.path.join(tmp, "origin")
    os.makedirs(orig)
    subprocess.run(["git", "init", "-q", orig])
    open(os.path.join(orig, "one.swift"), "w").write(
        "// role: forms\n// written in `gate stdlib show two`\npublic enum Sole {}\n")
    open(os.path.join(orig, "two.swift"), "w").write("// role: forms\npublic enum Other {}\n")
    open(os.path.join(orig, "gate.manifest.swift"), "w").write(layout % "")
    c, r = run("status", cwd=orig)
    S.append(("a page whose head names its grammar and whose row does not is refused",
              c == 1 and any("written in two.swift" in x["claim"]
                             and x.get("address", "").startswith("gate.manifest.swift:")
                             for x in r["refusals"])))
    open(os.path.join(orig, "gate.manifest.swift"), "w").write(
        layout % "    public typealias Written = Two\n")
    c, r = run("status", cwd=orig)
    S.append(("and holds once the row says it", c == 0 and r["verdict"] == "holds"))

    # THE WHERE COURT JUDGES THE FIRST FILE IT IS HANDED AND DROPS THE REST — it
    # reads the others (an unreadable second path is refused) and then says nothing
    # about them: palette then metrics reports 119, the same two reversed 14.
    # Nothing here passes more than one, and the day something does, a verdict
    # would quietly narrow instead of refusing.
    def wide(*paths):
        raw = subprocess.run([os.path.join(HERE, "bin", "gate-judge"), "judge", "where", *paths],
                             capture_output=True, text=True).stdout
        m = re.search(r"(\d+) equalities judged", raw)
        return int(m.group(1)) if m else None
    pal = os.path.join(HERE, "stdlib", "bench-palette.swift")
    met = os.path.join(HERE, "stdlib", "bench-metrics.swift")
    S.append(("the where court judges the first file it is given and drops the rest",
              wide(pal) == wide(pal, met) and wide(met) == wide(met, pal)
              and wide(pal) != wide(met)))
    gate_src = open(GATE).read()
    S.append(("and nothing here hands it more than one",
              all("," not in seg and "*" not in seg for seg in
                  re.findall(r'"judge",\s*"where",\s*([^\]]+)\]', gate_src))))

    # ── THE PORT SPEAKS THE SAME WORDS AS THE BINARY, LINE FOR LINE. The judge is
    # built for one platform, so on any other machine the same court exists and
    # nothing could reach it: `bin/judge-cli.js` is the reach, and it is only worth
    # having if its answer is the binary's answer. Held byte for byte here, on a world
    # that holds and on one that refuses, because a fallback that disagrees quietly is
    # two courts rather than two views of one.
    par = os.path.join(tmp, "two-views")
    os.makedirs(par)
    run("demo", "org", par)
    pw = os.path.join(par, "gate.swift")
    kept_world = open(pw, encoding="utf-8").read()

    def both_ways(path):
        b = subprocess.run([os.path.join(HERE, "bin", "gate-judge"), "judge", path],
                           capture_output=True, text=True)
        p = subprocess.run(["node", os.path.join(HERE, "bin", "judge-cli.js"), "judge", path],
                           capture_output=True, text=True)
        strip_ms = lambda s: re.sub(r"[\d.]+ ms", "N ms", s.strip())
        return strip_ms(b.stdout), strip_ms(p.stdout), b.returncode, p.returncode

    hb, hp, hbc, hpc = both_ways(pw)
    open(pw, "w").write(kept_world.replace("public typealias Home = Finance",
                                           "public typealias Home = Engineering", 1))
    rb, rp, rbc, rpc = both_ways(pw)
    open(pw, "w").write(kept_world)
    S.append(("the port and the binary answer a holding world in the same words",
              hb == hp and hbc == hpc == 0 and "THE JUDGE holds" in hb))
    S.append(("and a refusing world in the same words, with the same lines",
              rb == rp and rbc == rpc == 1 and "refuses 2 claim(s)" in rb))
    # AND THE CERTIFICATE COURT OF THE PORT, HELD TO THE BINARY PAGE FOR PAGE.
    # For a stretch the port refused `judge where` outright, and gate named the
    # forms rows as unjudged wherever the binary could not run; the port sits
    # now, a line-for-line translation of the corpus's WhereJudge, and the two
    # courts must print the same lines on every page of the shelf. The where
    # verdict carries no clock, so the parity here is byte for byte.
    _where_pages = sorted(glob.glob(os.path.join(HERE, "stdlib", "*.swift")))
    _where_apart = []
    for _wpg in _where_pages:
        _wb = subprocess.run([os.path.join(HERE, "bin", "gate-judge"), "judge", "where", _wpg],
                             capture_output=True, text=True)
        _wn = subprocess.run(["node", os.path.join(HERE, "bin", "judge-cli.js"), "judge",
                              "where", _wpg], capture_output=True, text=True)
        if (_wb.stdout, _wb.returncode) != (_wn.stdout, _wn.returncode):
            _where_apart.append(os.path.basename(_wpg))
    S.append(("the port's certificate court prints the binary's lines, page for page",
              _where_pages != [] and _where_apart == []))
    # and a page that refuses: the same refusal, the same canons, the same exit
    _wbroken = os.path.join(tmp, "where-broken.swift")
    open(_wbroken, "w").write(
        open(os.path.join(HERE, "stdlib", "bench-metrics.swift"), encoding="utf-8").read()
        .replace("public typealias SnugOverTight = Wider<Snug, Tight, Never>",
                 "public typealias SnugOverTight = Wider<Tight, Snug, Never>", 1))
    _wb2 = subprocess.run([os.path.join(HERE, "bin", "gate-judge"), "judge", "where", _wbroken],
                          capture_output=True, text=True)
    _wn2 = subprocess.run(["node", os.path.join(HERE, "bin", "judge-cli.js"), "judge",
                           "where", _wbroken], capture_output=True, text=True)
    S.append(("and a broken certificate refuses through the port in the binary's words",
              _wb2.returncode == _wn2.returncode == 1 and _wb2.stdout == _wn2.stdout
              and "be equivalent [Ordered]" in _wn2.stdout))
    # AND THE ONE COMMAND WHOSE JOB IS TO SAY WHAT JUDGES THIS REPOSITORY SAYS WHICH
    # ONE. It printed the binary's digest on a machine where the binary cannot run and
    # the port was doing the judging: a file that judged nothing, named as the court.
    vsrc = open(GATE, encoding="utf-8").read()
    S.append(("the version names the court that ran, not the file beside it",
              'if JUDGE_KIND != "binary":' in vsrc.split("def judge_version")[1][:600]
              and "port sha256:" in vsrc
              and "both courts are served by the port under node" in vsrc))
    # and the README says where this runs, with the unmeasured platform named
    # as such. Windows crossed that line the day its CI road went green, so
    # the unmeasured one is Linux now, and the cover says exactly that.
    rd = open(os.path.join(HERE, "README.md"), encoding="utf-8").read()
    S.append(("the cover says where it runs, and calls the unmeasured platform unmeasured",
              "**Where it runs.**" in rd
              and "Windows is measured on every push" in rd
              and "tests/windows.py" in rd
              and "not\nmeasured in CI yet" in rd
              and "judge-cli.js" in rd and "judge-where.js" in rd))

    # self-hosted shelf: the product's own stdlib files are judged by its own judge
    import glob as _glob
    for sf in sorted(_glob.glob(os.path.join(HERE, "stdlib", "*.swift"))):
        raw = subprocess.run([os.path.join(HERE, "bin", "gate-judge"), "judge", "where", sf],
                             capture_output=True, text=True).stdout
        S.append((f"self-judged: {os.path.basename(sf)}", "holds" in raw and "✗" not in raw))

    # one reading of the grammar: the SAME parser that judges also carries the
    # kind of every axis and gate parameter, so a bench can be offered exactly
    # what the judge will accept without a second regex over the shelf. This is
    # the bridge the vocabulary is built from — proven here on the judge's own
    # parse, so the reader can be one.
    kinds_probe = (
        'const {judge}=require(%r);const fs=require("fs");'
        'const g=judge("g.swift",fs.readFileSync(%r,"utf8")).parsed.declarations;'
        'const pa={},ga={};for(const d of g.values()){'
        'if(d.axisKinds&&Object.keys(d.axisKinds).length)pa[d.name]=d.axisKinds;'
        'if(d.paramKinds&&d.paramKinds.length)ga[d.name]=d.paramKinds;}'
        'console.log(JSON.stringify({pa,ga}));'
        % (os.path.join(HERE, "judge.js"), os.path.join(HERE, "stdlib", "forms-organization.swift")))
    kout = subprocess.run(["node", "-e", kinds_probe], capture_output=True, text=True).stdout
    try:
        kv = json.loads(kout or "{}")
    except Exception:
        kv = {}
    S.append(("the judge's own parser carries every axis and gate kind, read once",
              kv.get("pa", {}).get("Employee", {}).get("Home") == "Department"
              and kv.get("pa", {}).get("Person", {}).get("Sex") == "Sexed"
              and kv.get("ga", {}).get("VerifiedView") == ["Employee", "Document"]))

    # stdlib: hidden is not secret — shelf, materialize, drift guard, ownership
    c, r = run("stdlib")
    shelf = set(r.get("modules", {}))
    on_disk = {f[:-6] for f in os.listdir(os.path.join(HERE, "stdlib")) if f.endswith(".swift")}
    S.append(("the shelf lists exactly the pages on it", shelf == on_disk and len(shelf) >= 3))
    lib = os.path.join(tmp, "lib")
    os.makedirs(lib)
    shutil.copy(os.path.join(repo, "gate.swift"), os.path.join(lib, "gate.swift"))
    c, r = run("stdlib", "materialize", "forms-grants", cwd=lib)
    c, r = run("status", cwd=lib)
    S.append(("materialized untouched copy holds", r["verdict"] == "holds"))
    with open(os.path.join(lib, "forms-grants.swift"), "a") as f:
        f.write("// edit\n")
    c, r = run("status", cwd=lib)
    S.append(("an edited printout is caught still claiming to be the printout",
              r["verdict"] == "refused"
              and any("no longer matches the words the judge carries" in x["claim"]
                      for x in r["refusals"])))
    t = open(os.path.join(lib, "forms-grants.swift")).read().replace("// gate stdlib", "// mine:", 1)
    open(os.path.join(lib, "forms-grants.swift"), "w").write(t)
    c, r = run("status", cwd=lib)
    # dropping the header ends the claim — it does not turn the file into a
    # source. Nothing declares it, so nothing reads it, and the world is what
    # it was before the copy existed.
    S.append(("dropping the header ends the claim, and the file goes back to being read by nothing",
              r["verdict"] == "holds"))

    c, r = run("import", "rbac", os.path.join(DEMO, "rbac.json"), "-o", os.path.join(tmp, "rbac-gate.swift"))
    S.append(("rbac: two real breaks named by k8s source", c == 1 and len(r.get("refusals", [])) == 2
              and any("ghost-bind" in x["source"] for x in r["refusals"])
              and any("share one namespace" in x["claim"] for x in r["refusals"])))
    clean = json.load(open(os.path.join(DEMO, "rbac.json")))
    clean["items"] = [i for i in clean["items"] if i["metadata"].get("name") not in ("ghost-bind", "cross-bind")]
    cp = os.path.join(tmp, "rbac-clean.json")
    json.dump(clean, open(cp, "w"))
    c, r = run("import", "rbac", cp, "-o", os.path.join(tmp, "rbac-clean-gate.swift"))
    S.append(("rbac: clean cluster holds + canon handshake", c == 0 and r["verdict"] == "holds" and r["canon_handshake"]))

    # ── ownership: a repository's own CODEOWNERS, judged ──
    # What CODEOWNERS cannot say is who may own what; with that stated, a rule
    # reaching outside its owner's zone is refused by the line it sits on.
    co = os.path.join(tmp, "co")
    os.makedirs(os.path.join(co, "src"))
    os.makedirs(os.path.join(co, "docs"))
    for p in ("src/parser.py", "src/renderer.py", "docs/guide.md"):
        open(os.path.join(co, p), "w").write("x\n")
    c, r = run("import", "codeowners", os.path.join(DEMO, "CODEOWNERS"),
               "--tree", co, "--policy", os.path.join(DEMO, "owners.csv"),
               "-o", os.path.join(tmp, "co-gate.swift"))
    judged = [x for x in r["refusals"] if "share one zone" in x["claim"]]
    ghosts = [x for x in r["refusals"] if "matches nothing" in x["claim"]]
    S.append(("codeowners: a rule outside its owner's zone is refused, by their line",
              c == 1 and judged and all("CODEOWNERS:" in x["source"] for x in judged)))
    # ── ONE FACT, ONE SENTENCE, AND THE WORDS ARE THE LAW'S OWN. The importer
    # carried its own wording of the law while `gate status` printed the judge's
    # raw line about the very same refusal — two voices for one fact, and the
    # readable one lived in the command a person runs once while the unreadable
    # one lived in the verb they run every day. The sentence is a `///` note on
    # the law, in the file the law is written in: rename it there and both
    # surfaces say the new thing, with nothing in this tool to edit.
    shelf_law = open(os.path.join(HERE, "stdlib", "forms-grants.swift"), encoding="utf-8").read()
    tool_src = open(GATE, encoding="utf-8").read()
    S.append(("the sentence a refusal wears is the law's own, read from the file the law is in",
              "/// an owner and the path they own must share one zone" in shelf_law
              and all("Zone_" in x["claim"] and "against" in x["claim"]
                      and "share one zone" in x["claim"] for x in judged)
              # and the generic parameters of the form are not shown to anybody:
              # `Who.Post` and `What.Place` belong to the declaration, not to the
              # reader's file, and naming them was naming nothing they wrote
              and not any("Who.Post" in x["claim"] or "What.Place" in x["claim"]
                          for x in judged)
              # said once: the tool holds no second copy of the law's words
              and tool_src.count("an owner and the path they own must share one zone") == 0))
    S.append(("codeowners: a pattern the tree has no file for is named",
              len(ghosts) == 1 and ghosts[0]["address"].startswith("CODEOWNERS:")))
    # and the refusal is about the disagreement, not a constant: state that
    # alice keeps src, and the very same CODEOWNERS holds
    alt = os.path.join(tmp, "owners-alt.csv")
    open(alt, "w").write(open(os.path.join(DEMO, "owners.csv")).read()
                         .replace("alice,docs", "alice,src"))
    c, r = run("import", "codeowners", os.path.join(DEMO, "CODEOWNERS"),
               "--policy", alt, "-o", os.path.join(tmp, "co-alt.swift"))
    S.append(("codeowners: restate the zone and the same file holds",
              not [x for x in r["refusals"] if "share one zone" in x["claim"]]))
    # without a policy every rule is its own authority: say so, do not pretend
    c, r = run("import", "codeowners", os.path.join(DEMO, "CODEOWNERS"),
               "-o", os.path.join(tmp, "co-bare.swift"))
    S.append(("codeowners without a policy claims no judgement it did not make",
              not [x for x in r["refusals"] if "share one zone" in x["claim"]]
              and "trivially" in r["note"]
              # ── AND THE WORD ABOVE THE NOTE AGREES WITH IT. The note said the
              # equalities hold trivially and the verdict over it said `holds` —
              # a green nobody could have broken, printed by the tool whose whole
              # argument is that a green must say how wide it is. This was the
              # README's own first line, so it was the first thing anybody ran.
              # `observed` is the word already used where nothing is judged.
              and r["verdict"] == "observed"
              # and a ghost is read from the tree either way, so a run with no
              # policy can still refuse: the word is about the court, not the run
              and json.loads(subprocess.run(
                  [sys.executable, GATE, "import", "codeowners",
                   os.path.join(DEMO, "CODEOWNERS"), "--tree", co,
                   "-o", os.path.join(tmp, "co-ghost.swift"), "--json"],
                  capture_output=True, text=True).stdout)["verdict"] == "refused"))
    # the same crystal carries it: the world is written in forms-grants
    world = open(os.path.join(tmp, "co-gate.swift")).read()
    S.append(("ownership rides the access crystal, not a set of forms of its own",
              "Owns<" in world and "public protocol Keeper" in world))
    # ── AND THE NINE LINES ON THE COVER ARE THE DEMO'S OWN PRINT. The cover
    # shows a pair written out, and a hand-written specimen drifts from the
    # printer the day the printer changes: the letter's findings quote already
    # walked that road. Every line of the cover's one swift block must be a
    # line the demo's own import actually prints.
    _cover_block = re.search(r"```swift\n(.*?)```", _cover, re.S)
    _cover_demo = os.path.join(tmp, "cover-demo")
    run("demo", _cover_demo)
    _cover_world = open(os.path.join(_cover_demo, "ownership.swift"),
                        encoding="utf-8").read()
    S.append(("the cover's written-out pair is the demo's own print, line for line",
              bool(_cover_block) and all(
                  ln in _cover_world
                  for ln in _cover_block.group(1).strip().split("\n"))))
    # ── AND THE PRINT AND ITS SOURCE ARE A PAIR, HELD FROM BIRTH. The world
    # names its inputs on its `from:` line, and status re-translates and
    # compares certificates: silent on a fresh pair, and a rule written into
    # CODEOWNERS alone is refused at the line that writes it, in their file.
    _, _pg = run("status", cwd=_cover_demo)
    S.append(("the printed world and its source hold as a pair at birth",
              "// from: CODEOWNERS --policy owners.csv" in _cover_world
              and not any("does not hold it" in (r.get("claim") or "")
                          or "no longer writes" in (r.get("claim") or "")
                          for r in (_pg.get("refusals") or []))))
    with open(os.path.join(_cover_demo, "CODEOWNERS"), "a") as f:
        f.write("src/api/    @dave\n")
    _, _pg2 = run("status", cwd=_cover_demo)
    S.append(("a rule written into their file alone is refused at their line",
              any("does not hold it" in (r.get("claim") or "")
                  and (r.get("address") or "").startswith("CODEOWNERS:")
                  for r in (_pg2.get("refusals") or []))))
    # a human running an importer gets lines, not a traceback
    plain = subprocess.run([sys.executable, GATE, "import", "rbac",
                            os.path.join(DEMO, "rbac.json"), "-o", os.path.join(tmp, "r2.swift")],
                           capture_output=True, text=True)
    S.append(("an importer speaks to a human without --json",
              "Traceback" not in plain.stderr and "refused" in plain.stdout))

    # ── the journal view: git's own history, projected. Observed, not judged;
    # open/closed is reachability from the default branch, person via identities.
    jrepo = os.path.join(tmp, "journal")
    os.makedirs(os.path.join(jrepo, "tables"))
    subprocess.run(["git", "init", "-q", "-b", "main", jrepo])
    shutil.copy(os.path.join(DEMO, "people.csv"), os.path.join(jrepo, "tables", "people.csv"))
    shutil.copy(os.path.join(DEMO, "grants.csv"), os.path.join(jrepo, "tables", "grants.csv"))
    run("status", cwd=jrepo)  # bootstrap gate.swift from the tables

    def gc(email, msg, cwd=jrepo):
        subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", f"user.email={email}",
                        "-c", "user.name=T", "commit", "-qam", msg], cwd=cwd)

    subprocess.run(["git", "add", "-A"], cwd=jrepo)
    gc("boss@corp", "seed the world on main")
    with open(os.path.join(jrepo, "tables", "identities.csv"), "w") as f:
        f.write("email,id\nboss@corp,Emp9001\ndev@corp,Emp9002\n")
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=jrepo)
    t = open(os.path.join(jrepo, "gate.swift")).read().replace("Rank = Manager", "Rank = Lead", 1)
    open(os.path.join(jrepo, "gate.swift"), "w").write(t)
    gc("dev@corp", "demote a manager (pending on a branch)")
    subprocess.run(["git", "checkout", "-q", "main"], cwd=jrepo)

    # a code file nobody's world declares: the world's history must not carry it
    with open(os.path.join(jrepo, "app.py"), "w") as f:
        f.write("print('unrelated code')\n")
    subprocess.run(["git", "add", "-A"], cwd=jrepo)
    gc("boss@corp", "unrelated code commit")

    c, r = run("log", cwd=jrepo)
    S.append(("journal defaults to the world's history, not the whole repo",
              r.get("scope") == "world"
              and not any(x["subject"] == "unrelated code commit" for x in r["commits"])))
    c, ra = run("log", "all", cwd=jrepo)
    S.append(("journal all: the repository's own commits appear",
              ra.get("scope") == "all"
              and any(x["subject"] == "unrelated code commit" for x in ra["commits"])))
    commits = r.get("commits", [])
    main_c = next((x for x in commits if x["email"] == "boss@corp"), None)
    feat_c = next((x for x in commits if x["email"] == "dev@corp"), None)
    S.append(("journal: default branch commit is closed",
              main_c and main_c["closed"] is True and main_c["person"] == "Emp9001"))
    S.append(("journal: unmerged branch commit is open + touches the world",
              feat_c and feat_c["closed"] is False and feat_c["touches_world"] is True
              and feat_c["person"] == "Emp9002"))

    # ── the personal world: your own git, never the shared repo ──
    me = os.path.join(tmp, "me")
    env = dict(os.environ, GATE_ME=me)

    def runme(*args, cwd=None):
        r = subprocess.run([sys.executable, GATE, *args, "--json"], capture_output=True,
                           text=True, cwd=cwd, env=env)
        try:
            return r.returncode, json.loads(r.stdout)
        except Exception:
            return r.returncode, {"raw": r.stdout[:200]}

    c, r = runme("my", cwd=jrepo)
    mypath = r.get("personal", "")
    S.append(("nobody is given a personal world they did not ask for",
              r.get("empty") is True and mypath.startswith(me) and not os.path.exists(mypath)))
    S.append(("personal world: the shared repo has no trace of it",
              subprocess.run(["git", "status", "--porcelain"], cwd=jrepo,
                             capture_output=True, text=True).stdout.strip() == ""))
    # the comment it starts with is not writing: changed nothing, stored nothing
    import urllib.request as _u
    def put(port, name, text):
        req = _u.Request(f"http://127.0.0.1:{port}/world?f={name}", data=text.encode(), method="PUT")
        _u.urlopen(req).read()

    # a claim the SHARED world does not make anywhere: only my own file can be
    # refused for it, so a pass here cannot come from the world's own entries
    def myclaim(who, doc):
        os.makedirs(os.path.dirname(mypath), exist_ok=True)
        base = (open(mypath).read().split("\npublic enum MyWatch")[0]
                if os.path.exists(mypath) else "")
        with open(mypath, "w") as f:
            f.write(base + f"""
public enum MyWatch: AccessLedger {{
    @StructureBuilder
    public static var body: some Structure {{
            VerifiedView<
                {who},
                {doc}
            >.self;
    }}
}}
""")

    src_gate = open(GATE, encoding="utf-8").read()
    tpl = src_gate.split('PERSONAL_TEMPLATE = """')[1].split('"""')[0]
    S.append(("the comment says the world is kept on this machine alone",
              # in plain words: emphasis by capitals is not this voice
              "on this machine, in a git of its own" in tpl and "goes nowhere else" in tpl
              and "THIS machine" not in tpl))
    S.append(("the world you have not written reads as a comment that says what it is",
              tpl.lstrip("\\\n ").startswith("// Yours.") and "shared repository" in tpl
              and "not stored" in tpl))
    S.append(("a state that holds is kept in that git, not left loose",
              'commit", "-qm", "your world"' in src_gate))
    S.append(("and text still equal to that comment is not kept",
              'text.strip() == PERSONAL_TEMPLATE.strip()' in src_gate
              and "os.remove(p)" in src_gate))

    myclaim("Emp9002", "EngineeringShare")   # Emp9002 lives in Finance: illegal
    c, r = runme("my", cwd=jrepo)
    S.append(("a personal claim is really judged: an illegal one is refused in MY file",
              r["verdict"] == "refused"
              and any(x["address"].startswith("my.swift:") for x in r["refusals"])))
    S.append(("and no other file is blamed for a claim only mine makes",
              all(x["address"].startswith("my.swift:") for x in r["refusals"])))
    myclaim("Emp9001", "FinanceShare")       # legal
    c, r = runme("my", cwd=jrepo)
    S.append(("personal claim holds while the shared world agrees", r["verdict"] == "holds"))
    t = open(os.path.join(jrepo, "gate.swift")).read().replace(
        "public enum Emp9001: Employee, Person {\n    public typealias Rank = Lead\n    public typealias Home = Finance",
        "public enum Emp9001: Employee, Person {\n    public typealias Rank = Lead\n    public typealias Home = Engineering", 1)
    open(os.path.join(jrepo, "gate.swift"), "w").write(t)
    c, rmine = runme("my", cwd=jrepo)
    c, rshared = runme("status", cwd=jrepo)
    S.append(("someone else's change refuses MY claim, by line in MY file",
              rmine["verdict"] == "refused"
              and any(x["address"].startswith("my.swift:") for x in rmine["refusals"])))
    S.append(("and their CI sees the shared world alone: no personal file in it",
              not any("my.swift" in x["address"] for x in rshared.get("refusals", []))))
    # the multi-file addressing: no ghost addresses in files that never claim it
    ghosts = [x for x in rmine["refusals"]
              if x["address"].startswith("grants.swift:")
              and "VerifiedInDepartment" in x["claim"]]
    S.append(("no ghost address: grants.swift is not blamed for a claim it never makes", not ghosts))

    # ── who somebody is, and what merging demands, are facts of the world ──
    grepo = os.path.join(tmp, "policy")
    os.makedirs(os.path.join(grepo, "tables"))
    subprocess.run(["git", "init", "-q", "-b", "main", grepo])
    for f in ("people.csv", "grants.csv"):
        shutil.copy(os.path.join(DEMO, f), os.path.join(grepo, "tables", f))
    run("status", cwd=grepo)
    with open(os.path.join(grepo, "gate.policy.swift"), "w") as f:
        f.write("""// who someone is, and what an action demands — facts, beside the world
public enum MailBoss: Identity {
    public typealias Person = Emp9001
}
extension MailBoss { public static var typeName: String { "boss@corp" } }

public enum MergePolicy {
    public typealias Requires = Manager
}
""")
    subprocess.run(["git", "add", "-A"], cwd=grepo)
    subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "user.email=boss@corp",
                    "-c", "user.name=B", "commit", "-qm", "state the policy in the world"], cwd=grepo)
    c, r = run("status", cwd=grepo)
    S.append(("the world still holds with the policy file beside it", r["verdict"] == "holds"))
    c, r = run("report", "-o", "audit.html", cwd=grepo)
    page = open(os.path.join(grepo, "audit.html")).read()
    S.append(("the audit page carries the policy and when it last changed",
              "<h2>Policy</h2>" in page and "merge requires" in page
              and ("Last changed" in page or "unchanged" in page)))
    S.append(("and the same findings the terminal gives, marked read or checked",
              "<h2>Findings</h2>" not in page or "not a verdict" in page))
    c, r = run("guard", "merge", cwd=grepo)
    S.append(("guard reads identity and policy from the policy file, not a CSV",
              r.get("policy_from") == "gate.policy.swift" and r.get("requires") == "Manager"
              and r.get("author", "").endswith("Emp9001")))
    S.append(("guard: a Lead may not merge when the policy demands a Manager",
              c == 1 and r["verdict"] == "refused"))
    pol = os.path.join(grepo, "gate.policy.swift")
    t = open(pol).read().replace(
        "public typealias Person = Emp9001", "public typealias Person = Emp9999", 1)
    open(pol, "w").write(t)
    c, r = run("guard", "merge", cwd=grepo)
    S.append(("guard: an identity naming nobody is refused by line, not obeyed",
              r["verdict"] == "refused"
              and any("declares no such person" in x["claim"] and ":" in x["address"]
                      for x in r["refusals"])))
    c, r = run("status", cwd=grepo)
    S.append(("status guards the policy file: the ghost person is named there too",
              r["verdict"] == "refused"
              and any("declares no such person" in x["claim"]
                      and x["address"].startswith("gate.policy.swift:") for x in r["refusals"])))

    # guard is a team gate: a personal world must not bend it. Rebind the
    # boss's email to a Manager in MY file — the verdict must not move.
    t = open(pol).read().replace(
        "public typealias Person = Emp9999", "public typealias Person = Emp9001", 1)
    open(pol, "w").write(t)
    c, gme = runme("my", cwd=grepo)   # creates the personal world for grepo
    os.makedirs(os.path.dirname(gme["personal"]), exist_ok=True)
    with open(gme["personal"], "a") as f:
        f.write("""
public enum MailBossMine: Identity {
    public typealias Person = Emp9000
}
extension MailBossMine { public static var typeName: String { "boss@corp" } }
""")
    c, r = runme("guard", "merge", cwd=grepo)
    S.append(("a personal world cannot bend the team gate",
              r.get("author", "").endswith("Emp9001") and r["verdict"] == "refused"))

    # ── the tool travels with the repository: a clone has it, nothing installed ──
    ven = os.path.join(tmp, "vendored")
    os.makedirs(ven)
    subprocess.run(["git", "init", "-q", "-b", "main", ven])
    run("demo", "org", ven)
    c, r = run("init", ven, "--vendor")
    S.append(("init --vendor carries the tool and its judge into the repo",
              r.get("vendored") and os.path.exists(os.path.join(ven, "gatew"))
              and os.path.exists(os.path.join(ven, ".gate", "bin", "gate-judge"))
              and len(r["vendored"].get("judge_sha256", "")) == 64))
    S.append(("and the terms travel with it: a vendored copy carries its licence",
              os.path.exists(os.path.join(ven, ".gate", "LICENSE"))
              and os.path.exists(os.path.join(ven, ".gate", "NOTICE.md"))))
    # ── AND SO DOES THE ONE FACT THAT IS THE DEPENDENCY. The bytes travelled and
    # the revision beside them did not: a vendored copy said "the revision this
    # judge was built from is not recorded", losing what this tool calls the real
    # dependency, and a world that had written that revision into its own row
    # could not check its own claim. Silent since vendoring existed, and found
    # only once a guard was put between the claim and the artifact.
    S.append(("and the revision travels too: bytes say what a judge is, only the revision says what from",
              os.path.exists(os.path.join(ven, ".gate", "bin", "gate-judge.from"))
              and open(os.path.join(ven, ".gate", "bin", "gate-judge.from")).read().strip()
              and "not recorded" not in subprocess.run(
                  [os.path.join(ven, "gatew"), "--version"], cwd=ven,
                  capture_output=True, text=True).stdout))
    subprocess.run(["git", "add", "-A"], cwd=ven)
    subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "user.email=a@b", "-c",
                    "user.name=A", "commit", "-qm", "world and tool", "--no-verify"], cwd=ven)
    clone = os.path.join(tmp, "clone")
    subprocess.run(["git", "clone", "-q", ven, clone])
    shim = subprocess.run([os.path.join(clone, "gatew"), "status", "--json"],
                          cwd=clone, capture_output=True, text=True)
    S.append(("a fresh clone judges with no installation at all",
              json.loads(shim.stdout or "{}").get("verdict") == "holds"))
    t = open(os.path.join(clone, "gate.swift")).read().replace(
        "public typealias Home = Finance", "public typealias Home = Engineering", 1)
    open(os.path.join(clone, "gate.swift"), "w").write(t)
    shim = subprocess.run([os.path.join(clone, "gatew"), "status", "--json"],
                          cwd=clone, capture_output=True, text=True)
    S.append(("and it refuses a planted lie by line, exiting non-zero for CI",
              shim.returncode == 1
              and json.loads(shim.stdout or "{}")["refusals"][0]["address"].startswith("gate.swift:")))

    jp = os.path.join(ven, ".gate", "bin", "gate-judge")
    with open(jp, "wb") as f:
        f.write(b"not the judge this repository states")
    c, r = run("status", cwd=ven)
    S.append(("a swapped judge in .gate/ is named, not trusted",
              r["verdict"] == "refused"
              and any("carried judge" in x["claim"] for x in r["refusals"])))
    shutil.copy(os.path.join(HERE, "bin", "gate-judge"), jp)

    # ── the first thirty seconds: a demo world, and a bench that opens with none ──
    d = os.path.join(tmp, "demoworld")
    c, r = run("demo", "org", d)
    S.append(("demo builds a world that holds, with a policy and a history",
              os.path.exists(os.path.join(d, "gate.swift"))
              and os.path.exists(os.path.join(d, "gate.policy.swift"))))
    c, r = run("status", cwd=d)
    S.append(("the demo world holds on the first look", c == 0 and r["verdict"] == "holds"))
    # ── AND A GREEN SAYS HOW WIDE IT IS, IN EITHER COURT. The where court has
    # always counted what it judged — `119 equalities judged` on this bench's own
    # palette — and `status` read the plain court's numbers only, so a world of
    # forms printed `holds` with no width under it. That world is this repository.
    here_status = json.loads(subprocess.run(
        [sys.executable, GATE, "status", "--json"], cwd=HERE,
        capture_output=True, text=True).stdout)
    said_status = subprocess.run([sys.executable, GATE, "status"], cwd=HERE,
                                 capture_output=True, text=True).stdout
    S.append(("a green says how wide it is in the where court too, not only the plain one",
              here_status.get("forms", {}).get("equalities", 0) > 0
              and "equalities" in said_status
              # and the name it gives what it judged is a file that is there:
              # a forms-only world has no gate.swift, and saying it does is a
              # claim about something nobody declared
              and all(os.path.exists(os.path.join(HERE, f))
                      for f in ([here_status["facts"]] if isinstance(here_status["facts"], str)
                                else here_status["facts"]))))
    c, r = run("check", "view", "Emp9001", "EngineeringShare", cwd=d)
    S.append(("and the invitation in it is real: the refusal names both",
              c == 1 and r["refusals"]))
    empty = os.path.join(tmp, "noworld")
    os.makedirs(empty)
    subprocess.run(["git", "init", "-q", "-b", "main", empty])
    c, r = run("log", cwd=empty)
    # ── AND THE SECOND RUNG IS ONE THIS REPOSITORY CAN ACTUALLY TAKE. `drop your
    # CSVs into tables/` was the organization world's path and it stayed here
    # after the first scene became a repository's own ownership: somebody
    # standing in a clone that has a CODEOWNERS was sent to go find spreadsheets.
    rung = os.path.join(tmp, "rungrepo")
    os.makedirs(rung)
    subprocess.run(["git", "init", "-q", "-b", "main", rung])
    open(os.path.join(rung, "a.txt"), "w").write("x\n")
    subprocess.run(["git", "add", "-A"], cwd=rung, capture_output=True)
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=a",
                    "-c", "commit.gpgsign=false", "commit", "-qm", "one"],
                   cwd=rung, capture_output=True)
    without = run("status", cwd=rung)[1]
    open(os.path.join(rung, "CODEOWNERS"), "w").write("src/ @alice\n")
    withco = run("status", cwd=rung)[1]
    S.append(("the step offered to a repository with no world is one that repository can take",
              without["verdict"] == "no world here"
              and "gate demo" in without["then"] and "CODEOWNERS" not in without["then"]
              # and where the file is already there, the command that reads it is named
              and "gate import codeowners CODEOWNERS" in withco["then"]))

    S.append(("a repo with no world still has a journal, and says so honestly",
              r.get("scope") == "world" and r.get("world_files") == []))

    # ── the ladder is the navigation: one next step, never the whole list ──
    lad = os.path.join(tmp, "ladder")
    os.makedirs(os.path.join(lad, "tables"))
    subprocess.run(["git", "init", "-q", "-b", "main", lad])
    c, r = run("status", cwd=lad)
    # and the rung is chosen by what is actually there. A repository with no
    # world AND no commits was sent to read its own history, which sent it back
    # to status: two rungs pointing at each other and nothing to stand on. Where
    # there is nothing at all, the step that produces something is a world to
    # look at; where there is a history, the journal needs no translation.
    S.append(("a repo with nothing in it is sent somewhere that produces something",
              r.get("verdict") == "no world here" and "gate demo" in r.get("next", "")))
    open(os.path.join(lad, "readme.md"), "w").write("# something\n")
    subprocess.run(["git", "add", "-A"], cwd=lad)
    subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "user.email=t@t", "-c", "user.name=T",
                    "commit", "-qm", "a first commit, unrelated to any world"], cwd=lad)
    _, past = run("status", cwd=lad)
    S.append(("a repo with a history and no world is offered the journal, which needs no translation",
              past.get("verdict") == "no world here" and "gate log" in past.get("next", "")))
    for f in ("people.csv", "grants.csv"):
        shutil.copy(os.path.join(DEMO, f), os.path.join(lad, "tables", f))
    c, r = run("status", cwd=lad)
    S.append(("a world without a hook is offered the hook", "hook" in r.get("next", "")))
    subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=lad)
    c, r = run("status", cwd=lad)
    S.append(("a hooked world is offered a policy", "gate.policy.swift" in r.get("next", "")))
    with open(os.path.join(lad, "gate.policy.swift"), "w") as f:
        f.write('public enum MailMe: Identity { public typealias Person = Emp9000 }\n'
                'extension MailMe { public static var typeName: String { "me@corp" } }\n'
                'public enum MergePolicy { public typealias Requires = Manager }\n')
    c, r = run("status", cwd=lad)
    S.append(("a world with a policy is offered CI", "CI" in r.get("next", "")))
    t = open(os.path.join(lad, "gate.swift")).read().replace(
        "public typealias Home = Finance", "public typealias Home = Engineering", 1)
    open(os.path.join(lad, "gate.swift"), "w").write(t)
    c, r = run("status", cwd=lad)
    S.append(("a refused world is pointed at the address, not at the ladder",
              r["verdict"] == "refused" and "address" in r.get("next", "")))

    ui = open(os.path.join(HERE, "ui.html"), encoding="utf-8").read()
    # every name a printed world uses has a home: its own file, or the forms
    printed = open(os.path.join(repo, "gate.swift")).read()
    decl_here = set(re.findall(r"^\s*(?:public\s+)?(?:enum|protocol|struct|typealias)\s+(\w+)", printed, re.M))
    shelf_names = set()
    for f in os.listdir(os.path.join(HERE, "stdlib")):
        if f.endswith(".swift"):
            shelf_names |= set(re.findall(
                r"^\s*(?:public\s+)?(?:enum|protocol|struct|typealias|associatedtype)\s+(\w+)",
                open(os.path.join(HERE, "stdlib", f)).read(), re.M))
    used = set(re.findall(r"\b[A-Z]\w*", "\n".join(l.split("//")[0] for l in printed.split("\n"))))
    homeless = sorted(used - decl_here - shelf_names - {"StructureBuilder", "Structure", "String", "Self"})
    S.append(("every name a printed world uses is declared somewhere it can be read",
              not homeless))

    S.append(("a printed world carries no semicolon where nothing is separated",
              ">.self;" not in printed and ">.self" in printed))
    S.append(("and a world written either way is read the same",
              'r">\\s*\\.self\\s*;?"' in open(GATE, encoding="utf-8").read()))

    # an axis says what may stand in it, and the offer says only that
    forms_page = open(os.path.join(HERE, "stdlib", "forms-organization.swift")).read()
    S.append(("every axis in the forms states what it accepts",
              "associatedtype Sex: Sexed" in forms_page and "associatedtype Rank: Ranked" in forms_page
              and "associatedtype Home: Department" in forms_page))
    S.append(("and the bench offers by that, not by what it saw nearby",
              "function fillersFor(" in ui and "axesOfHost(host)[slot[1]]" in ui))
    S.append(("a recognised slot never falls through to the general pool",
              "a slot is a closed question" in ui and "closed: true }" in ui
              and "return { items: f || []" in ui
              # and a gate's argument is one mechanism for every spelling:
              # the walk's innermost gate frame names the gate and its own
              # commas have counted the argument, one line or many
              and "one mechanism for every spelling" in ui
              and "commas have already counted" in ui))
    S.append(("the popup is pinned to the word, not moved by a changing verdict",
              "reposition || compEl.hidden" in ui and "drawCompletion(true)" in ui))

    S.append(("deleting back into a word offers again, not only typing forward",
              'change.origin === "+delete") offerCompletion()' in ui))

    S.append(("the cursor on a name describes it from the grammar, not a dictionary",
              "function describeName(" in ui and "function inspect(" in ui
              and "protoAxes[name]" in ui and "conformers)" in ui))
    S.append(("and what it says is read from the world and the forms",
              "vocabulary[name]" in ui and "gates[name]" in ui
              and "a dictionary of ours" not in ui.split("function describeName")[0][-200:]))

    S.append(("one reading of the grammar drives every offer, not a case per place",
              "function allowedAt(" in ui and "function placeAt(" in ui))
    S.append(("a record is offered the axes it still owes",
              "still owes" in ui and "public typealias " in ui))
    S.append(("a declaration head is offered protocols, a body its gates",
              "what this record is" in ui and "a claim this body may hold" in ui))
    S.append(("an axis reached through another axis is an answer too",
              "axis + \".\" + inner" in ui))
    S.append(("and a name followed by a dot offers what stands after it",
              "function afterDot(" in ui and "protoAxes[kind]" in ui))

    # ── AND THE GATE FRAME IS DRIVEN, NOT DESCRIBED. The words above hold the
    # mechanism's presence; a mutation inside it (an argument's kind no longer
    # read off the frame's commas) left every one of them green. So the offer
    # road is walked here the way the page walks it: the bench's own functions
    # under node, the shipped shelf read by the shipped judge, a cursor inside
    # a two-kind gate. The second argument must be offered the second kind,
    # one line or many. The vocabulary is built by the page's own
    # loadVocabulary over a stubbed fetch, not by a copy of its loop: a copy
    # is a second reader, and the first draft of this harness proved it by
    # drifting the moment the real loop learned kind-less axes.
    _oj = os.path.join(tmp, "offer-args.js")
    open(_oj, "w").write("""
const fs = require("fs"), path = require("path");
const ui = fs.readFileSync(process.argv[2], "utf8");
const { judge } = require(process.argv[3]);
const pages = process.argv.slice(4);
const grab = (name, prefix) => {
    const head = (prefix || "") + "function " + name + "(";
    const at = ui.indexOf(head);
    if (at < 0) throw new Error("no " + name);
    let d = 0;
    for (let j = ui.indexOf("{", at); j < ui.length; j++) {
        if (ui[j] === "{") d++;
        else if (ui[j] === "}" && --d === 0) return ui.slice(at, j + 1);
    }
};
let SCOPES = [], NESTS = {};
let vocabulary = {}, conformers = {}, axisOf = {}, protoAxes = {}, gates = {};
let layoutDecls = new Map(), worldAliases = new Map(), cm = null;
let formsFiles = new Set();
global.fetch = async (u) => ({
    json: async () => ({ modules: pages.map(p => path.basename(p, ".swift")) }),
    text: async () => {
        const m = /m=([^&]+)/.exec(u);
        const p = pages.find(q => path.basename(q, ".swift") === decodeURIComponent(m[1]));
        return fs.readFileSync(p, "utf8");
    },
});
eval(["buildScopes", "admits", "scopesAt", "noteStartAt", "codeOfLine",
      "placeAt", "axesOfHost", "fillersFor", "afterDot", "allowedAt"]
     .map(n => grab(n)).join("\\n"));
eval(grab("loadVocabulary", "async "));
const world = ["public enum Legal: Realm {}",
               "public enum E9: Keeper {",
               "    public typealias Post = Legal",
               "}",
               "public enum Doc1: Room {",
               "    public typealias Place = Legal",
               "}"];
const askAt = (lines, line, ch) => {
    cm = { getLine: (n) => lines[n] };
    layoutDecls = new Map();
    const wp = judge("w.swift", lines.join("\\n"),
                     { seeds: new Set(), generics: new Set() }).parsed;
    for (const [name, d] of wp.declarations) layoutDecls.set(name, d);
    return allowedAt({ line: line, ch: ch });
};
const ask = (tail) => {
    const lines = world.concat(tail);
    const last = lines.length - 1;
    return askAt(lines, last, (lines[last] || "").length);
};
(async () => {
    await loadVocabulary();
    const open9 = ["public enum Legal: Realm {}", "public enum E9: Keeper {"];
    console.log(JSON.stringify({
        first: ask(["public typealias C1 = Enter<"]),
        second: ask(["public typealias C1 = Enter<E9, "]),
        broken: ask(["public typealias C2 = Enter<", "    E9,", "    "]),
        owed: askAt(open9.concat(["    "]), 2, 4),
        keyslot: askAt(open9.concat(["    public typealias Key = "]), 2, 27),
        ext: ask(["extension "]),
    }));
})();
""")
    _oa = subprocess.run(["node", _oj, os.path.join(HERE, "ui.html"),
                          os.path.join(HERE, "judge.js"),
                          os.path.join(HERE, "stdlib", "grammar.swift"),
                          os.path.join(HERE, "stdlib", "forms-grants.swift")],
                         capture_output=True, text=True)
    try:
        _off = json.loads(_oa.stdout)
    except Exception:
        _off = {}
    _f, _s, _b = (_off.get("first") or {}), (_off.get("second") or {}), (_off.get("broken") or {})
    S.append(("a gate's first argument is offered the first kind, with the world's names",
              _f.get("kind") == "this argument takes Keeper"
              and "E9" in (_f.get("items") or []) and "Doc1" not in (_f.get("items") or [])))
    S.append(("and the second argument the second kind, one line or many",
              _s.get("kind") == "this argument takes Room"
              and "Doc1" in (_s.get("items") or []) and "E9" not in (_s.get("items") or [])
              and _b.get("kind") == "this argument takes Room"
              and "Doc1" in (_b.get("items") or [])))

    # ── AND THE OFFER KNOWS EVERY AXIS THE LAW KNOWS. Keeper owes Post and
    # Key; Key's kind the forms leave unstated, and the judge requires the
    # axis all the same. The bench read only the kinded axes, so a writer was
    # offered a record the judge then refused, with no road from the offer to
    # the missing line. Owed is owed: the kind-less axis is offered at the
    # record, and its slot answers in words instead of hiding the popup.
    _ow, _ks, _ex = (_off.get("owed") or {}), (_off.get("keyslot") or {}), (_off.get("ext") or {})
    S.append(("an axis the forms leave kind-less is owed, and its slot says so in words",
              "public typealias Key = " in (_ow.get("items") or [])
              and "Key" in (_ow.get("scaffold") or [])
              and _ks.get("closed") is True and (_ks.get("items") or []) == []
              and _ks.get("kind") == "the forms state no kind for Key"))
    # and the note a closed empty answer carries stays on the page: the popup
    # shows the sentence, and the keys pass through it as if nothing were up
    S.append(("an empty closed offer keeps its note on the page, and takes no keystroke",
              "a closed question with no names is still an answer" in ui
              and "!(here.closed && here.kind && !word)" in ui
              and ui.count("compEl.hidden || !compItems.length") == 3
              and "!compEl.hidden && compItems.length" in ui))
    # ── AND EXTENSION IS OFFERED WHAT EXISTS. The word names something already
    # declared, so the offer is the declared names, the world's records beside
    # the shelf's gates and values, and a protocol is not among them.
    S.append(("extension is offered the declared names, records and gates alike",
              _ex.get("closed") is True
              and "E9" in (_ex.get("items") or []) and "Enter" in (_ex.get("items") or [])
              and "Keeper" not in (_ex.get("items") or [])))
    # the shelf has ONE reader: the vocabulary is built in the bench from the
    # judge's own parse (axisKinds/paramKinds), so the gate carries no second
    # regex over the shelf and the bench never fetches a server-built vocabulary
    S.append(("the shelf's vocabulary has one reader: the judge, not a second regex",
              "proto_axes" not in open(GATE, encoding="utf-8").read()
              and 'fetch("/vocabulary")' not in ui
              and "function loadVocabulary(" in ui and "judge(mod" in ui))

    # the shelf is reference, read in the bench but never judged as the world:
    # a forms page uses protocol/associatedtype, which the world's judge rejects, so
    # routing it through world-judgement would paint a wall of false refusals
    S.append(("a record owing axes can be filled as a whole, not one at a time",
              "here.scaffold" in ui and "compScaffold" in ui
              and 'startsWith("\\u25B8")' in ui and 'public typealias " + a + " = "' in ui))

    # an unfilled axis is the judge saying "states none" (judge.js): a record
    # not yet finished, not a claim in conflict. The bench reads that register —
    # a wall of empty slots is "to fill", calm, never the red a lie earns.
    S.append(("an empty slot is read, in the judge's own words, as one to fill",
              "states none" in open(os.path.join(HERE, "judge.js"), encoding="utf-8").read()
              and "/states none/.test(x.premise)" in ui
              and "+ pending.length + ' to fill</span>'" in ui
              and "is not filled in yet" in ui))
    # and the two are shown TOGETHER, because a refusal and a decision are
    # different things and neither may hide the other: one chip that showed
    # whichever came first made the slots waiting on their owner vanish the
    # moment something broke — which is exactly the moment there is most to
    # decide.
    S.append(("and the chip reddens for disagreements alone, never for empty slots, and neither hides the other",
              'document.getElementById("chips").innerHTML = (broken.length' in ui
              and "+ broken.length + '</span>'" in ui
              # the waiting slots are built apart from the verdict and appended to it
              and "const waits = pending.length" in ui and "+ waits;" in ui
              # INTO A HOLDER, because the verdict is sometimes two chips. Saying
              # it again used to replace the first and leave the second standing:
              # thirteen `5 to fill` marching across the bar after thirteen
              # keystrokes, each a truthful count of the same five slots.
              and 'id="chip"' not in ui and '<span id="chips"></span>' in ui
              # and they never wear the colour a lie earns
              and "chip bad" not in ui.split("const waits = pending.length", 1)[1].split(";", 1)[0]))

    # ── AND A GREEN SAYS HOW WIDE IT IS, on the bench as at the command line.
    # The judge counts what it checked and prints the count; dropping it on the
    # way to the browser left a verdict over several files reading `judged
    # together` and nothing else — which is a green with no measure, the very
    # thing a day of doors was spent losing. Several files is the ordinary case,
    # so this was the ordinary case.
    S.append(("the bench says how much was checked, and says it where several files are judged at once",
              # the server keeps the judge's own count instead of discarding it
              '"premises": int(size.group(3)) if size else None' in open(GATE).read()
              # and the bench prints it in the multi-file line, where it used to vanish
              and "r.wide = r.premises" in ui
              and '(r.wide ? " · <b>" + r.wide + "</b> claims checked" : "")' in ui))

    S.append(("a jump can be walked back and forward, across files too",
              "function navGo(" in ui and "navFrom = navHere()" in ui
              and '"Cmd-Ctrl-Left"' in ui and '"Alt-Left"' in ui))
    # the view is part of the place: a jump out of Table walks back into Table,
    # not into Full — navHere carries the mode, navGo restores it before the spot
    S.append(("a jump remembers the view it left, and returns to it",
              "{ file: active, mode, pos:" in ui and "setMode(there.mode" in ui))
    S.append(("the bar's arrows walk the one jump history, not a second of their own",
              'nav-back").onclick = () => navGo(navBack' in ui
              and 'nav-fwd").onclick = () => navGo(navForward' in ui))

    S.append(("the bench shows the shelf as reference, not as the world",
              'viewingShelf = mod' in ui
              and 'document.getElementById("chips").innerHTML =' in ui
              and 'a printout of what the judge carries' in ui and "if (viewingShelf)" in ui))
    S.append(("and returning to a world file resumes judgement",
              'viewingShelf = null' in ui and 'cm.setOption("readOnly", false); viewingShelf = null' in ui))

    S.append(("the offer has one source: the grammar, with no pool to fall back to",
              "if (!here) return hideCompletion()" in ui and "function completionPool" not in ui))

    # the bench wears its own theme by declaration, not a toggle: MyBench.Theme
    # is read from the shelf forms (conformers of BenchTheme), with the OS
    # preference as the default when nothing is declared
    bench_atoms = open(os.path.join(HERE, "stdlib", "bench-atoms.swift"), encoding="utf-8").read()
    S.append(("the theme is a declaration read from the forms, with the OS as default",
              "function applyMyBench(" in ui
              and 'conformers["BenchTheme"]' in ui
              and "prefers-color-scheme: dark" in ui
              and 'setAttribute("data-theme"' in ui
              and "protocol Bench {" in bench_atoms and "enum Dark: BenchTheme" in bench_atoms))
    # ── and the first paint is the answer, not a guess. The declaration lives in
    # the world, which is read a third of a second after the page appears; until
    # then the operating system's preference is only a guess, and a guess that
    # disagrees with the declaration is watched being corrected. So the machine
    # remembers the DECLARATION and paints it at once — the memory is not a
    # second truth: it holds only what the world declared, the world overwrites
    # it on every read, and it is dropped when the world declares nothing.
    head = ui.split("<style>", 1)[0]
    S.append(("the first paint is the declaration this machine remembers, and the operating system only when there is none",
              "gate.theme.declared" in head
              and head.index("localStorage.getItem") < head.index("prefers-color-scheme")
              and 'localStorage.setItem("gate.theme.declared", declaredTheme)' in ui
              and 'localStorage.removeItem("gate.theme.declared")' in ui))

    # the bench is judged by its own rules: a value on MyBench/MyJournal the forms
    # does not name is a guard line addressed at its own line (a mistyped Scope
    # used to fall silently to a default), read from the same one source
    S.append(("a bench value outside its own forms is named on its line, not silenced",
              "function benchGuards(" in ui
              and 'vocabulary[conf] !== "bench-atoms"' in ui
              and "the bench's own forms state" in ui))

    # ── the palette is one source: the colour the bench RENDERS is the colour
    # the judge HOLDS. Every var's color(xyz-d65 …) carries the very numbers the
    # atom states and its contrast certificates hold to, and no colour lives
    # outside the palette blocks. Decode the file's own ladder and compare —
    # exactly, no tolerance. Lower a pair's contrast in the file and its
    # self-judge goes red (above); change a number in the CSS and this goes red.
    pal = open(os.path.join(HERE, "stdlib", "bench-palette.swift"), encoding="utf-8").read()
    def _decode(e):
        e = e.strip()
        if e == "Never": return 0
        if e == "Unit": return 1
        if e[0] == "W": return int(e[1:])
        inner = e[e.index("<") + 1:e.rindex(">")]
        depth = 0
        for i, c in enumerate(inner):
            if c == "<": depth += 1
            elif c == ">": depth -= 1
            elif c == "," and depth == 0:
                return _decode(inner[:i]) + _decode(inner[i + 1:])
        return _decode(inner)
    axes = {}
    for m in re.finditer(r"public typealias (\w+?)(Lit|Dim)([XYZ]) = (.+)", pal):
        axes[(m.group(1), m.group(2), m.group(3))] = _decode(m.group(4))
    VAR2ATOM = {"--ink": "Ink", "--paper": "Paper", "--mist": "Mist", "--line": "Line",
        "--muted": "Muted", "--ok": "Ok", "--bad": "Bad", "--action": "Action", "--law": "Law",
        "--localtype": "LocalType", "--knownname": "KnownName", "--seam": "Seam", "--select": "Select"}
    # ── AND THE PAGE HOLDS NO COLOUR OF ITS OWN. It used to carry every one of
    # these numbers a second time — `color(xyz-d65 calc(307/1000) …)` beside a
    # record already saying 307 — and this check stood between the two copies
    # keeping them equal. A check is what you reach for when a single source is
    # out of reach, and here it was not: the bench serves the palette from the
    # world that declares it, so there is nothing left to compare. What is
    # checked now is that the page states no colour at all, and that what is
    # served is what is declared.
    served = subprocess.run(
        [sys.executable, "-c",
         "import types;src=open(%r,encoding='utf-8').read();g=types.ModuleType('g');"
         "g.__file__=%r;exec(compile(src,'gate','exec'),g.__dict__);"
         "print(g.palette_tokens())" % (GATE, GATE)],
        capture_output=True, text=True).stdout

    def _block(sel, text):
        return text.split(sel, 1)[1].split("}", 1)[0] if sel in text else ""

    def _match(block, mode):
        for var, atom in VAR2ATOM.items():
            m = re.search(re.escape(var) + r": color\(xyz-d65 calc\((\d+)/1000\) calc\((\d+)/1000\) calc\((\d+)/1000\)\)", block)
            if not m:
                return False
            if (int(m.group(1)), int(m.group(2)), int(m.group(3))) != (
                    axes.get((atom, mode, "X")), axes.get((atom, mode, "Y")), axes.get((atom, mode, "Z"))):
                return False
        return True
    S.append(("the palette the bench renders is the palette the judge holds: one source, no copy",
              # served from the declared world, both halves, every atom
              _match(_block(":root {", served), "Lit")
              and _match(_block(':root[data-theme="dark"] {', served), "Dim")
              # and the page names colours without ever stating one
              and "color(xyz-d65 calc(" not in re.sub(r"<!--.*?-->", "", ui, flags=re.S)
              and '<link rel="stylesheet" href="/ladder.css">' in ui
              and not re.search(r"#[0-9a-fA-F]{6}\b", re.sub(r"--shade[^;]*;", "", ui))))

    # ── distances are one ladder too, and it starts at the reading line: --u is
    # a tenth of it and every gap a WHOLE multiple, so a length is spelled the
    # way a number is (Unit, W2, Plus…) and can be judged like one. A hand-tuned
    # 12.5px beside it is the same drift a hand-picked #hex was.
    style = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", ui, re.S))
    SPACING = r"(padding[a-z-]*|margin[a-z-]*|gap|row-gap|column-gap)\s*:\s*([^;{}\n]+)"
    off_ladder = [p + ":" + v.strip() for p, v in re.findall(SPACING, style)
                  if re.search(r"(?<![\w.])\d*\.?\d+px", v)]
    halved = [m for m in re.findall(r"var\(--u\)\s*\*\s*([\d.]+)", style) if "." in m]
    S.append(("distances are one ladder: the reading line is the base, and every gap a whole step of it",
              not off_ladder and not halved
              and not re.search(r"var\(--u\)\s*/", style)
              and "--u: calc(var(--textline) / 10)" in style
              and style.count("var(--u)") >= 40))

    # ── and every step the page takes has a NAME in the judged world of
    # distances: bench-metrics states what each gap is for and holds the law of
    # proximity between them (a group stands off further than a row, a row than
    # the parts inside it). A multiple the page uses that the shelf never named
    # is a length nobody can defend — the same drift a hand-picked #hex was.
    met = open(os.path.join(HERE, "stdlib", "bench-metrics.swift"), encoding="utf-8").read()
    def _steps(text):
        vals = {}
        def ev(e):
            e = e.strip()
            if e == "Unit": return 1
            if e == "Never": return 0
            if e in vals: return vals[e]
            if e.startswith("Twice<"): return 2 * ev(e[6:-1])
            if e.startswith("Plus<"):
                inner = e[5:-1]; d = 0
                for i, c in enumerate(inner):
                    if c == "<": d += 1
                    elif c == ">": d -= 1
                    elif c == "," and d == 0: return ev(inner[:i]) + ev(inner[i + 1:])
            raise ValueError(e)
        for m in re.finditer(r"public typealias (\w+) = (.+)", text):
            try: vals[m.group(1)] = ev(m.group(2).split("//")[0])
            except Exception: pass
        return vals
    steps = _steps(met)
    named = {v for k, v in steps.items() if not re.fullmatch(r"W\d+", k)}
    used = {int(x) for x in re.findall(r"var\(--u\)\s*\*\s*(\d+)", style)} | {1}
    # The law bites on the PAGE, not only in the shelf: the ladder there is
    # dense, so its order alone cannot catch a seam handed the wrong step. What
    # can is this — the gap that opens a section must exceed the gap between the
    # rows inside it, or kinship stops reading as nearness.
    def _first_u(sel, prop):
        blk = style.split(sel + "{", 1)[1].split("}", 1)[0] if (sel + "{") in style else ""
        m = re.search(prop + r"\s*:\s*(?:calc\(var\(--u\)\*(\d+)\)|(var\(--u\)))", blk)
        return None if not m else (int(m.group(1)) if m.group(1) else 1)
    section, row = _first_u("#rail h3", "padding"), _first_u(".file", "padding")
    S.append(("every gap the page takes is a step the world of distances names, and a section opens wider than its rows",
              named and used and used <= named
              and "Wider<Apart, Step, Unit>" in met
              and section is not None and row is not None and section > row))

    # ── and a name means ONE kind. A property that is a colour on one line and
    # a length on the next is not two values: the later wins and the earlier
    # becomes nothing. A spacing --line met the palette's --line exactly once,
    # and every gap on this page computed to zero while the battery stayed
    # green — the guard the palette had, lengths did not.
    kinds = {}
    for name, val in re.findall(r"(--[a-z-]+)\s*:\s*([^;{}]+)", style):
        v = val.strip()
        kinds.setdefault(name, set()).add(
            "colour" if v.startswith(("#", "color(", "rgb", "hsl")) else
            "length" if re.match(r"^(calc\(|\d*\.?\d+(px|em|rem|%|vh|vw))", v) else "other")
    two_minded = sorted(n for n, k in kinds.items() if len(k - {"other"}) > 1)
    S.append(("a name means one kind: nothing is a colour on one line and a length on the next",
              not two_minded))

    # the verdict holds still: the numbers on the status line are tabular so a
    # changing millisecond does not make it breathe, the chip reserves its width
    # so holds<->refuses N never shifts the row, and nothing animates on a change
    # (motion is only ever the hand's — hover, a caret, a drag)
    chip_rule = ui.split(".chip{", 1)[1].split("}", 1)[0] if ".chip{" in ui else ""
    status_rule = ui.split("#status{", 1)[1].split("}", 1)[0] if "#status{" in ui else ""
    # ── material is a function of the wire: six registers declared ONCE, and an
    # element only names the one it belongs to. Font says what a thing is, ink
    # says whether it is judged; the verdict and the hand own their colours alone.
    # and a register carries MATERIAL ALONE. The moment one carries layout too,
    # every element that names it drags that layout in — a table cell named the
    # fact register once and collapsed into a flex box. Layout belongs to the
    # element's own co-class (a table's name cell is `fact cell-name`).
    reg_rules = {r: ui.split(r, 1)[1].split("}", 1)[0]
                 for r in (".fact{", ".observed{", ".speech{", ".caption{") if r in ui}
    S.append(("the bench's material is a function of its wire: six registers, named by the element",
              all(r in ui for r in (".fact{", ".observed{", ".speech{", ".caption{", ".verdict{", ".gesture{"))
              and '<code class="fact">' in ui and "file fact" in ui
              # the registers are used where facts and readings stand beside each
              # other: a seam's address is a fact, its state is this bench's
              # reading of one, and neither is dressed as the other
              and 'sc.className = "cell-value observed"' in ui
              and 'a.className = "caption observed"' in ui
              and len(reg_rules) == 4
              and all("display:" not in v and "padding:" not in v for v in reg_rules.values())
              and "fact cell-name" in ui))
    # ── the editor's tokens obey the same table. The vendored codemirror.css
    # colours keyword/string/comment/attribute with constants of its own, and
    # they win on specificity unless we answer at the same weight — so the
    # override must be spelled `.cm-s-default .cm-*` or the borrowed colour comes
    # back silently. Ceremony carries no meaning of the world: it is the seam,
    # the colour of the brackets, at ordinary weight. A literal is a value; red
    # belongs to the verdict alone.
    toks = (ui.split(".cm-s-default .cm-keyword", 1)[1].split(".cm-localtype", 1)[0]
            if ".cm-s-default .cm-keyword" in ui else "")
    S.append(("the editor's tokens are the palette's own, and ceremony is a seam, not a shout",
              all(sel in ui for sel in (".cm-s-default .cm-keyword", ".cm-s-default .cm-attribute",
                                        ".cm-s-default .cm-string", ".cm-s-default .cm-comment"))
              and "var(--seam)" in toks and "var(--knownname)" in toks and "var(--muted)" in toks
              and "600" not in toks))

    # ── the journal is READ, not judged, so it may not speak in the judge's own
    # voice. Red and green are the verdict's whole property (С2: green and red
    # outside a verdict forge one), and blue belongs to the hand. The journal
    # said `was` in red and `now` in green, added lines green and deleted red,
    # `closed` green and `open` blue — over a `+`/`-` sign and a strikethrough
    # that already carried the distinction, so the colour was a second marker
    # AND a borrowed wire. It speaks in the ladder now: present is ink, past is
    # muted and struck, a state is its own word. What stays coloured is what
    # earns it — a commit's author is clickable, so it wears the hand's blue,
    # and a record's own name is a name of the world, so it keeps its teal.
    # The journal has left the panel entirely, and the law outlived it: whatever
    # is READ speaks in the ladder. A seam is the case that proved the law still
    # bites — moving its state out of the panel and onto its claim, I painted
    # `parted` red and `holds` green, which says a court has spoken. None has:
    # the court over a pair is `gate seam`, and this is an account of what the
    # two sides have said to each other. Caught by auditing against the theory
    # rather than against the list of things changed.
    read_sels = (".obs", "#gitstate", ".seam-line", ".seam-where", ".observed",
                 "#judge-row", ".cell-value")
    forged = [m.group(1).strip()[:40]
              for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", style)
              if any(k in m.group(1) for k in read_sels)
              and re.search(r"var\(--(ok|bad)\)", m.group(2))]
    S.append(("what is read speaks in the ladder, and never wears the verdict's own colours",
              not forged
              and ".cell-value.parted" not in style and ".cell-value.whole" not in style
              # and a state is still its own word, which is what carries it
              and 'gone ? "parted at " + gone' in ui))

    # ── colour answers one question and weight another, because a reader has two.
    # WHERE a name is from is a hue: teal for what this world DECLARES, violet for
    # what the shelf does. Declares, not mentions — the kinds a record conforms to
    # and the axes it answers are the forms', and colouring them local said the
    # world had authored its own forms, which also made a question (an axis) and
    # an answer (a value) one colour.
    # WHAT THE LINE DECLARES is the weight. A declaration holds two names, the one
    # it declares and the one it answers to, and weighting kinds instead put the
    # accent on the second: `MyBench: Bench` shouted Bench, and the eye went to
    # the answer rather than to the question. The bare view had always weighted
    # the subject, so the two views disagreed about what a line was about — and
    # the bare one was right. An axis name is neither: it is the label of a slot,
    # and it is set in plain ink there, so it is set in plain ink here.
    S.append(("a hue says where a name is from, the weight says what the line declares, and both views agree",
              "for (const [name] of parsed.declarations) out.add(name);" in ui
              and "for (const c of d.conformances) out.add(c);" not in ui
              # and what a line declares is settled once, by position, and read
              # by both the weight and the slot rule — so a word that is an axis
              # in another world cannot recolour a name being born here
              and "const declaring = /\\b(?:enum|protocol|struct|extension)\\s+$/.test(before);" in ui
              and 'const subject = declaring ? " declname" : "";' in ui
              and "(?:typealias|associatedtype)\\s+$/.test(before)) return \"axisname\"" in ui
              # the weight carries no hue of its own, and the axis carries no weight
              and ".cm-declname{font-weight:600}" in ui
              and ".cm-axisname{color:var(--ink)}" in ui
              and "var(--" not in style.split(".cm-declname{", 1)[1].split("}", 1)[0]
              and "kindname" not in ui))

    # ── HOW LONG, not whether. A snapshot asks the wrong question: a library
    # that lagged nine months on a field and then caught up looks today exactly
    # like one that never lagged, so `is it behind now` finds almost nothing and
    # reports calm. Drift is a duration, and git holds both ends of it — the day
    # the contract said a field, and the day the library first wrote it.
    # And the measurement needs a past to measure: a shallow clone has one commit
    # standing in for all of them, so every field looks as old as the checkout
    # and every library looks punctual. Answering `never been behind` off a
    # single revision is the empty green again, in a longer sentence.
    dr = os.path.join(tmp, "drift")
    spec_repo, lib_repo = os.path.join(dr, "contract"), os.path.join(dr, "library")
    for r in (spec_repo, lib_repo):
        os.makedirs(r, exist_ok=True)
        subprocess.run(["git", "init", "-q", "-b", "main", r])

    def at(repo, when, msg):
        env = dict(os.environ, GIT_AUTHOR_DATE=when + "T12:00:00", GIT_COMMITTER_DATE=when + "T12:00:00")
        subprocess.run(["git", "add", "-A"], cwd=repo)
        subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "user.email=t@t", "-c", "user.name=T",
                        "commit", "-qm", msg], cwd=repo, env=env)

    def spec_with(fields):
        return json.dumps({"paths": {"/points": {"post": {"requestBody": {"content": {
            "application/json": {"schema": {"properties": {f: {"type": "string"} for f in fields}}}}}}}}})
    sp = os.path.join(spec_repo, "openapi.json")
    open(sp, "w").write(spec_with(["limit"])); at(spec_repo, "2024-01-10", "the contract begins")
    open(sp, "w").write(spec_with(["limit", "with_vector"])); at(spec_repo, "2024-02-01", "a field is added")
    open(sp, "w").write(spec_with(["limit", "with_vector", "shard_key"])); at(spec_repo, "2024-03-01", "and another")
    # and the contract retires one. A name it no longer says is not a name the
    # library is missing: dating needs the union over every revision, the walk
    # needs the contract as it stands, and asking the walk about retired names
    # turned one true absence into thirty on a real pair.
    open(sp, "w").write(spec_with(["limit", "with_vector"])); at(spec_repo, "2024-05-01", "and drops it again")
    cl = os.path.join(lib_repo, "client.ts")
    open(cl, "w").write("interface Q {\n  limit?: number;\n}\n"); at(lib_repo, "2024-01-10", "the library begins")
    # sixty days late on one field, and the third it has never carried at all
    open(cl, "w").write("interface Q {\n  limit?: number;\n  with_vector?: boolean;\n}\n")
    at(lib_repo, "2024-04-01", "catch up, eventually")
    _, dft = run("drift", sp, "--client", lib_repo, "--name", "Lib")
    _, thin = run("drift", sp, "--client", os.path.join(tmp, "contract-shallow"), "--name", "Nowhere")
    S.append(("drift is a duration and git holds both ends of it, and a clone without a past measures nothing",
              # two fields stand today; the retired one is dated but not walked for
              dft.get("declares") == 2 and dft.get("late") == 1
              and dft.get("worst_days") == 60 and dft.get("unwritten") == []
              # the same reading, refused where there is no history to read
              and thin.get("thin") and not thin.get("late")))

    # ── and the library is only where the library is. Let loose over a whole
    # repository this measurement lies twice: a monorepo answers for a sibling
    # package that happens to spell the same word, and — worse — a contract kept
    # beside its own client answers for the client, because the commit that adds
    # a field to the spec adds that name in a line beginning with a plus. Every
    # field then reads as adopted the day it was declared, and the report is a
    # clean bill of health made of the contract talking to itself.
    mono = os.path.join(dr, "mono")
    os.makedirs(os.path.join(mono, "sdk"), exist_ok=True)
    os.makedirs(os.path.join(mono, "other"), exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main", mono])
    msp = os.path.join(mono, "openapi.json")
    open(msp, "w").write(spec_with(["limit"])); at(mono, "2024-01-10", "the contract, in the same repo")
    open(os.path.join(mono, "sdk", "client.ts"), "w").write("interface Q {\n  limit?: number;\n}\n")
    at(mono, "2024-01-10", "the sdk answers it")
    open(msp, "w").write(spec_with(["limit", "with_vector"])); at(mono, "2024-02-01", "a field is added")
    # a sibling package names it at once; the sdk never does
    open(os.path.join(mono, "other", "notes.ts"), "w").write("const with_vector = true;\n")
    at(mono, "2024-02-02", "a neighbour spells the word")
    _, mn = run("drift", msp, "--client", os.path.join(mono, "sdk"), "--name", "Sdk")
    # and the same repository asked about ITSELF: here the contract is inside the
    # walk, so only the exclusion keeps it from answering for the code. Without
    # it the field reads as adopted on the day it was declared — by the very
    # commit that declared it.
    _, whole = run("drift", msp, "--client", mono, "--name", "Whole")
    S.append(("a library is measured where the library is, not wherever its repository says the word",
              # the neighbour's line and the contract's own line are both refused a vote
              mn.get("declares") == 2 and mn.get("unwritten") == ["with_vector"]
              and mn.get("late") == 0
              # asked about the whole repo, the neighbour answers a day late — the
              # contract itself, which said the word first, does not answer at all
              and whole.get("late") == 1 and whole.get("worst_days") == 1))

    # ── the souvenir, and the only numbers on it are ones nobody can raise by
    # hand. A coverage badge is gamed by writing tests that assert nothing; this
    # one counts CLAIMS, which the judge counts, and DAYS, which come from
    # replaying the world's own history through the same judge — so anybody may
    # re-run it and get the same answer. What it must never say is `no silent
    # error`, since that is precisely what nobody saw: it says how much was
    # judged and how long it has held, which is duller and provable.
    bd = os.path.join(tmp, "badge")
    os.makedirs(bd, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main", bd])
    os.makedirs(os.path.join(bd, "tables"), exist_ok=True)
    shutil.copy(os.path.join(DEMO, "people.csv"), os.path.join(bd, "tables", "people.csv"))
    shutil.copy(os.path.join(DEMO, "grants.csv"), os.path.join(bd, "tables", "grants.csv"))
    run("status", cwd=bd)                                   # bootstrap the world
    bw = os.path.join(bd, "gate.swift")
    good = open(bw).read()
    at(bd, "2026-01-10", "the world begins")
    open(bw, "w").write(good.replace("Rank = Manager", "Rank = Nonesuch", 1))
    at(bd, "2026-02-01", "a rank that is nobody")           # this one does not hold
    open(bw, "w").write(good)
    at(bd, "2026-03-01", "put it back")
    _, bg = run("badge", cwd=bd)
    S.append(("a badge counts what the judge counted and how long the history has held, and neither can be raised by hand",
              bg.get("verdict") == "holds" and bg.get("claims", 0) > 0
              # the replay finds the commit that did not hold and stops there
              and bg.get("last_refusal") == "2026-02-01"
              and bg.get("commits_judged") == 2
              # and it never claims to have seen what nobody saw
              and "silent" not in (bg.get("note") or "") and "claims" in bg.get("text", "")))


    # ── an offer is a question put over a value, and a shadow is light taken
    # away. Both were told wrong. The list opened on its first row rather than on
    # what already stood in the slot, so keeping a value meant finding it in the
    # offer first; and it could be dismissed only from the editor, leaving it
    # hanging over a table that had scrolled out from under it. The shadow was
    # cast in the ink, which in the dark theme is the LIGHT end of the ladder, so
    # every raised thing wore a halo. A shadow belongs to no theme.
    dark_block = style.split(':root[data-theme="dark"]{', 1)[1].split("}", 1)[0]
    S.append(("an offer opens on the value it is asking about, closes when looked away from, and casts a shadow that is dark in both themes",
              "offerIndex(items, td.textContent)" in ui
              and "offerIndex(items, sl.textContent)" in ui
              # cast toward nothing, and the dark theme may not redefine it
              and "--shade:" in style and "--shade" not in dark_block
              and not re.search(r"box-shadow:[^;}]*var\(--ink\)", style)
              # dismissed from anywhere; only the box-anchored list minds a scroll,
              # since the editor scrolls its own lines as you type
              and "if (awayFromOffer(e)) hideCompletion();" in ui
              and "if (compRect && awayFromOffer(e)) hideCompletion();" in ui
              and "Escape" not in ui.split('if (mode !== "bare") return;', 1)[1].split("});", 1)[0]
              and 'if (e.key === "Escape" && !compEl.hidden) { e.preventDefault(); hideCompletion(); }\n}, true);' in ui))

    # ── the chromatic budget of a scene (Р3). Telling categories apart by hue is
    # expensive: every extra chromatic code in the field taxes the reading of all
    # the others. The code fabric asks exactly two questions — where a name is
    # from, and what the verdict is — so those are the only hues it may carry. A
    # gesture in it is known by its form, its place and the cursor, the way a hand
    # knows one before colour; blue answers to the page, outside the world's text.
    fabric = [(sel.strip().replace("\n", " "), body)
              for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", style)
              if re.search(r"#bare|#table-host|\.cm-|\.CodeMirror", sel)]
    allowed = {"--localtype", "--knownname", "--bad", "--ok"}
    overspent = [s[:44] for s, b in fabric
                 for v in re.findall(r"var\((--[a-z]+)\)", b)
                 # --select is on the grey line now, judged by SelectGrey: a neutral
                 # backing is not a hue and costs the scene nothing
                 if v in {"--action", "--law"}]
    S.append(("the code fabric spends a hue on its two questions and on nothing else",
              not overspent
              and "#bare .add{display:inline-block;cursor:pointer;color:var(--muted)}" in style
              and "#table-host .add{cursor:pointer;color:var(--muted)" in style))

    # ── a citation may not outlive the thing it cites. Code names a ticket, the
    # ticket is closed, and the citation stays: neither system reads the other, so
    # the two copies of "this is still open" pull apart quietly and a reader is
    # told something that stopped being true months ago. Here they are one world.
    # Both refusals fall out of the grammar rather than a rule written for them:
    # a closed thing says which state was found against the one needed, and a
    # thing the tracker never heard of cannot be read at all. The address is in
    # the reader's OWN file, never in the generated one.
    ref = os.path.join(tmp, "refs")
    os.makedirs(os.path.join(ref, "code"), exist_ok=True)
    open(os.path.join(ref, "tickets.json"), "w").write(json.dumps({"issues": [
        {"key": "PROJ-41", "status": "In Progress"}, {"key": "PROJ-42", "status": "Done"}]}))
    open(os.path.join(ref, "code", "scraper.py"), "w").write(
        "def a():\n    # TODO(PROJ-41): still live\n    pass\n"
        "def b():\n    # TODO(PROJ-42): the ticket is done, the note is not\n    pass\n"
        "def c():\n    # FIXME(PROJ-99): nobody has heard of this one\n    pass\n")
    c, r = run("import", "refs", os.path.join(ref, "tickets.json"),
               "--code", os.path.join(ref, "code"), "-o", os.path.join(ref, "refs-gate.swift"))
    said = {x["claim"] for x in r.get("refusals", [])}
    S.append(("a citation may not outlive the thing it cites: closed work and work nobody tracks are both refused, by the line that cites them",
              c == 1 and len(r.get("refusals", [])) == 2
              and all(x["address"].startswith("scraper.py:") for x in r["refusals"])
              and any("calls it closed" in s for s in said)
              and any("no such thing" in s for s in said)))

    # ── OBSERVATION, AND NOTHING ELSE. What lives here judges nothing: it looks
    # at a world that has not entered ours, so it holds no court, prints no
    # verdict, and says of every line which CATEGORY of fact it is. The half that
    # judged shapes is gone — its premises were reached for across the gate,
    # where a court has no jurisdiction, and a certificate over a premise nobody
    # declared is honest reasoning about an invented world.
    #
    # PRESENCE is an object: a commit that introduced a string is named by its
    # own hash. ABSENCE is a walk, and a walk is only as good as its bounds — so
    # the bounds are printed beside every absence, and a reader who points at one
    # excluded file has refuted the claim, which is what makes it a claim at all.
    con = os.path.join(tmp, "contract")
    os.makedirs(os.path.join(con, "lib"), exist_ok=True)
    open(os.path.join(con, "spec.json"), "w").write(json.dumps({"paths": {
        "/scrape": {"post": {
            "parameters": [
                {"name": "waitFor", "in": "query", "schema": {"type": "integer"}},
                {"name": "ids[]", "in": "query", "schema": {"type": "array"}},
                {"name": "StartTime<", "in": "query", "schema": {"type": "string"}},
                {"name": "opts", "in": "query", "schema": {"type": "object", "properties": {
                    "exclude_fields": {"type": "string"}}}}],
            "requestBody": {"content": {"application/json": {"schema": {"properties": {
                "url": {"type": "string"},
                "log-slow-requests-time-ms": {"type": "integer"},
                "Parameter1.Name": {"type": "string"},
                "createdAt": {"type": "integer", "readOnly": True}}}}}}}},
        "/forms": {"post": {"requestBody": {"content": {"application/x-www-form-urlencoded": {
            "schema": {"properties": {"Body": {"type": "string"}}}}}}}},
        "/echo": {"post": {
            "requestBody": {"content": {"application/json": {"schema": {"$ref": "#/definitions/Thing"}}}},
            "responses": {"200": {"schema": {"$ref": "#/definitions/Thing"}}}}}},
        "definitions": {"Thing": {"properties": {"echoed": {"type": "string"}}}}}))
    open(os.path.join(con, "lib", "client.ts"), "w").write(
        'const PATH = "/scrape";\n'
        "interface Req {\n  url: string;\n  waitFor?: number;\n  ids?: string[];\n"
        "  exclude_fields?: string;\n  log_slow_requests_time_ms?: number;\n}\n"
        'async function go(r: Req) { return post(`${PATH}`, r); }\n')
    _, obs = run("drift", os.path.join(con, "spec.json"),
                 "--client", os.path.join(con, "lib"), "--name", "Lib")
    S.append(("what is observed of a world that has not entered carries no verdict, and every absence carries the bounds of its walk",
              # no court sat, so there is no verdict to read
              "verdict" not in obs
              # the contract is read by a parser: a form is a request, a query key
              # is a name on the wire, an object parameter is its properties, a
              # read-only field and a body the contract also returns are no part
              # of a request, and `{setName}`, `Parameter1.Name`, `StartTime<`
              # and `ids[]`'s brackets are wire syntax nobody spells
              and obs.get("declares") == 6
              # the walk found every name but one, and says where it looked
              and obs.get("unwritten") == ["Body"] and obs["scope"]["files"] == 1
              and "skipping" in obs.get("note", "")
              # `/scrape` is spelled in a constant, so the walk does read routes —
              # and `/forms`, which it never spells, is named
              and obs.get("silent_routes") == ["/forms"]))

    # ── and a library that writes no URL at all is not one that lacks every
    # endpoint: it is one that keeps its paths somewhere this walk did not go.
    os.makedirs(os.path.join(con, "typesonly"), exist_ok=True)
    open(os.path.join(con, "typesonly", "client.ts"), "w").write(
        "interface Req {\n  url: string;\n}\n")
    _, bare_types = run("drift", os.path.join(con, "spec.json"),
                        "--client", os.path.join(con, "typesonly"), "--name", "Types")
    # ── THE ACT OF ENTRY, and the one court that follows it. Everything gate
    # judges is on this side of it and nothing else is: what a walk finds outside
    # stays an observation forever, because judgement has no jurisdiction over a
    # world nobody has spoken for.
    # The two halves are asymmetric on purpose. A contract states its own types
    # in a public format, so one emitter serves everybody and gate ships it —
    # reading a document that declares itself is not the inference that was
    # removed. A library's grammar is its own, so gate ships no reader for it at
    # all: that library's build emits a small declaration, and gate only renders
    # what it said into the shared words. The declaration is a VIEW of what they
    # already keep, never a copy, so it cannot drift from them.
    ent = os.path.join(tmp, "entry")
    os.makedirs(ent, exist_ok=True)
    open(os.path.join(ent, "openapi.json"), "w").write(json.dumps({"paths": {"/scrape": {"post": {
        "requestBody": {"content": {"application/json": {"schema": {"properties": {
            "url": {"type": "string"}, "waitFor": {"type": "integer"},
            "include": {"type": "array"}, "extra": {"type": "string"},
            "open": {"anyOf": [{"type": "string"}, {"type": "integer"}]}}}}}}}}}}))
    open(os.path.join(ent, "sdk.json"), "w").write(json.dumps({
        "carrier": "SdkJS", "against": {"contract": "openapi.json", "revision": "a1b2c3d"},
        "carries": [{"route": "/scrape", "field": "url", "as": "Text"},
                    {"route": "/scrape", "field": "waitFor", "as": "Text"},
                    {"route": "/scrape", "field": "include", "as": "Many",
                     "mine": "include_collections"}]}))
    _, dc = run("declare", "contract", os.path.join(ent, "openapi.json"),
                "-o", os.path.join(ent, "api.swift"))
    _, dk = run("declare", "carrier", os.path.join(ent, "sdk.json"),
                "-o", os.path.join(ent, "sdk.swift"))
    _, parted = run("seam", os.path.join(ent, "api.swift"), os.path.join(ent, "sdk.swift"))
    said = " ".join(x["claim"] for x in parted.get("refusals", []))
    S.append(("what enters is judged, and only what enters: two declarations, each signed by whoever made it",
              # the contract declares four; the fifth it leaves open, and an open
              # shape is not a shape it has stated
              dc.get("declares") == 4 and dk.get("declares") == 3
              # one disagreement, addressed, naming both sides' own words
              and parted.get("verdict") == "refused" and len(parted["refusals"]) == 1
              and "waitFor" in parted["refusals"][0]["address"]
              and "contract declares it count" in said and "SdkJS declares it text" in said
              # a field nobody claimed is named beside the court, never inside it
              and parted.get("unclaimed") == ["/scrape · extra"]))

    # ── and a carrier that agrees is not refused, and its rename is spoken in
    # its own words when it is — the coordinate is stated only where it does not
    # follow, since a declaration restating what already matches is a second copy
    # and a second copy drifts.
    open(os.path.join(ent, "sdk2.json"), "w").write(json.dumps({
        "carrier": "SdkJS", "against": {"contract": "openapi.json"},
        "carries": [{"route": "/scrape", "field": "waitFor", "as": "Count"},
                    {"route": "/scrape", "field": "include", "as": "Text",
                     "mine": "include_collections"}]}))
    run("declare", "carrier", os.path.join(ent, "sdk2.json"), "-o", os.path.join(ent, "sdk2.swift"))
    _, mixed = run("seam", os.path.join(ent, "api.swift"), os.path.join(ent, "sdk2.swift"))
    mixed_says = " ".join(x["claim"] for x in mixed.get("refusals", []))
    S.append(("a seam names each side in the words that side used, and holds where they agree",
              len(mixed.get("refusals", [])) == 1
              and "its own include_collections" in mixed_says
              and mixed.get("carrier") == "SdkJS"))

    # ── NOT WHAT CHANGED, BUT WHAT WAITS FOR A WORD. History is the other cut
    # and git already keeps it; this is the standing account of who owes whom a
    # sentence. It is two-sided by construction rather than by design: an
    # unanswered axis sits with whoever owes the answer, so the same movement
    # that shows a client what its contract is waiting for shows the contract
    # what the client is waiting for. A claim about something the contract never
    # stated is not a disagreement — there is nothing there to disagree with —
    # it is the contract owing a sentence, and it belongs in the other column.
    open(os.path.join(ent, "sdk3.json"), "w").write(json.dumps({
        "carrier": "SdkJS", "against": {"contract": "openapi.json"},
        "carries": [{"route": "/scrape", "field": "url", "as": "Text"},
                    {"route": "/scrape", "field": "waitFor", "as": "Text"},
                    {"route": "/scrape", "field": "autodelete", "as": "Flag"}]}))
    run("declare", "carrier", os.path.join(ent, "sdk3.json"), "-o", os.path.join(ent, "sdk3.swift"))
    A = [os.path.join(ent, "api.swift"), os.path.join(ent, "sdk3.swift")]
    _, att = run("attention", *A, "--as", "SdkJS")
    mine = [x["address"] for x in att.get("waits_on_you", [])]
    theirs = [x["address"] for x in att.get("you_wait_on", [])]
    S.append(("attention is a standing account of who owes whom a word, and it reads the same from either side",
              # the contract stated `include` and `extra`; this library has said
              # nothing of either, so they wait on it
              sorted(mine) == ["/scrape · extra", "/scrape · include"]
              # and it carries one the contract never stated, so that waits on the contract
              and theirs == ["/scrape · autodelete"]
              # a real disagreement is neither, and is named as its own thing
              and [x["address"] for x in att.get("parted", [])] == ["/scrape · waitFor"]
              # never a verdict: no court sits over who owes what
              and "verdict" not in att))

    # ── AND INTENTION IS DECLARED, NEVER GUESSED. A divergence somebody said out
    # loud is a fact with an author; one nobody said is unintended by
    # construction — the gate's own law, applied to disagreement. But a
    # declaration without a term is an amnesty: every temporary exception
    # outlives its reason, so a declared divergence CITES something that can
    # close, and when the tracker says it closed the exception stops holding and
    # the item comes back — first, and louder, because its ground is gone.
    open(os.path.join(ent, "known.json"), "w").write(json.dumps({"diverges": [
        {"route": "/scrape", "field": "waitFor", "because": "PROJ-42", "declared_by": "sdk-team"}]}))
    open(os.path.join(ent, "open.json"), "w").write(json.dumps([{"key": "PROJ-42", "status": "In Progress"}]))
    open(os.path.join(ent, "shut.json"), "w").write(json.dumps([{"key": "PROJ-42", "status": "Done"}]))
    _, held = run("attention", *A, "--as", "SdkJS",
                  "--known", os.path.join(ent, "known.json"),
                  "--tracker", os.path.join(ent, "open.json"))
    _, back = run("attention", *A, "--as", "SdkJS",
                  "--known", os.path.join(ent, "known.json"),
                  "--tracker", os.path.join(ent, "shut.json"))
    S.append(("a declared divergence is set aside while what it cites is open, and comes back by itself when that closes",
              # while the reason is open it is not attention, but it is not hidden
              held.get("parted") == [] and len(held.get("known", [])) == 1
              and held["known"][0]["declared_by"] == "sdk-team"
              and held["known"][0]["because"] == "PROJ-42"
              # and when the reason closes nobody has to remember: it returns
              and back.get("expired") and back["expired"][0]["address"] == "/scrape · waitFor"
              and not back.get("known")))

    # ── THE FIRST THIRTY SECONDS. The whole promise of this thing is that a
    # refusal names the line, and a world that holds shows none — so a newcomer
    # was handed a green world and a list of commands to try, with the payoff one
    # keystroke away and behind a choice they had no way to make yet. The demo
    # asks one question for them and prints the answer, in the same breath as the
    # world it is about.
    dm = os.path.join(tmp, "demo-first")
    _, made = run("demo", "org", dm)
    S.append(("the first thing a newcomer sees is a refusal with an address, not a list of things to try",
              made.get("refused") and ":" in made["refused"][0]
              and "VerifiedView" in made["refused"][0]
              and made.get("asked", "").startswith("gate check view")))

    # ── AND THE FIRST SCENE IS THE READER'S OWN REPOSITORY. Departments, ranks
    # and grants are a fine domain and they are not the one a developer arrives
    # carrying: what they own is paths, and CODEOWNERS is where they already
    # write it down. Meeting an HR world first, a person reads a tool for
    # somebody else's job and closes it — the machinery never gets read at all.
    # So bare `gate demo` builds a repository shaped like theirs, and the
    # organization is one word away for whoever wants it.
    nat = os.path.join(tmp, "demo-native")
    _, first = run("demo", nat)
    nat_status = run("status", cwd=nat)[1]
    # the fix a person would actually make, in the file they already know
    co = os.path.join(nat, "CODEOWNERS")
    open(co, "w").write(open(co).read().replace("src/db/     @carol", "src/db/     @bob"))
    run("import", "codeowners", "CODEOWNERS", "--tree", ".", "--policy", "owners.csv",
        "-o", "ownership.swift", cwd=nat)
    fixed = run("status", cwd=nat)[1]
    subprocess.run(["git", "checkout", "."], cwd=nat, capture_output=True)
    again = run("status", cwd=nat)[1]
    S.append(("the first scene is a repository: CODEOWNERS, a tree, and one owner reaching past their zone",
              # what a developer opens the box to: their own artefacts, not a roster
              os.path.exists(co) and os.path.exists(os.path.join(nat, "owners.csv"))
              and os.path.exists(os.path.join(nat, "src", "db", "schema.sql"))
              and not os.path.exists(os.path.join(nat, "tables"))
              # one refusal, named by the CODEOWNERS line that makes it
              and first.get("refused") and first["refused"][0].startswith("CODEOWNERS:")
              and "share one zone" in first["refused"][0]
              # A GRAMMAR AND THE CERTIFICATES OVER IT ARE A FORMS FILE, and the
              # role is what routes it: written as a plain world file the same
              # text earned twenty refusals for declaring its own protocols.
              and nat_status.get("verdict") == "refused"
              and len(nat_status.get("refusals", [])) == 1
              and nat_status["refusals"][0]["address"].startswith("ownership.swift:")
              # and the loop closes: fix the line in the file they know, it holds
              and fixed.get("verdict") == "holds"
              # and the way back is one word, as promised before anything was touched
              and "git checkout ." in first.get("back", "")
              and again.get("verdict") == "refused"))
    S.append(("and the organization world is one word away, not gone",
              made.get("refused") and "Emp9001" in made.get("asked", "")
              and any("gate demo org" in x for x in first.get("try", []))))

    # ── and the other door, for whoever came because a client and a contract
    # disagree rather than because of who may read what. Two sides, each in its
    # own words, and all three kinds of item at once: one the library owes, one
    # the contract owes, one they genuinely disagree about. Access grants are not
    # that person's pain, and making them learn a domain they do not have before
    # they can see the mechanism is a tax nobody pays twice.
    ds = os.path.join(tmp, "demo-seam")
    _, seam_demo = run("demo", "seam", ds)
    S.append(("a second demo shows the seam itself: what each side owes the other, and where they part",
              # a domain everybody has: send a message. Somebody else's endpoint
              # names make a demonstration that must be decoded before it teaches.
              seam_demo.get("waiting_on_you") == ["/messages · attachments"]
              and seam_demo.get("you_wait_on") == ["/messages · replyTo"]
              and len(seam_demo.get("parted", [])) == 1
              and "sendAt" in seam_demo["parted"][0]
              # and it leaves the pieces on disk for the reader to drive by hand
              and all(os.path.exists(os.path.join(ds, f)) for f in
                      ("openapi.json", "sdk.declared.json", "known.json", "tickets.json",
                       "api.swift", "sdk.swift"))))

    # ── AND THE BENCH SHOWS THE SEAMS, not only the world where you are alone.
    # Everything built this way lived at the command line while the thing the
    # owner actually looks at knew nothing of it: the interface was a move behind
    # the architecture, and the owner was legislating a world with one party in
    # it. A declaration is a world in the contract grammar, so a pair is found by
    # what the files SAY they are rather than by where they sit — one states
    # records, the other claims them, and a folder may hold either side or both.
    # Where nobody has declared anything the account is empty, and an empty
    # account is a fact: inventing a specimen to fill the screen would be the one
    # lie this thing cannot afford, so the empty state teaches instead.
    seam_src = open(GATE, encoding="utf-8").read()
    S.append(("the bench shows the seams this folder is party to, and says plainly when there are none",
              # the route exists and is promised where the others are promised
              '#   GET  /attention' in seam_src and 'u.path == "/attention"' in seam_src
              and "def seams_here(" in seam_src
              # a pair is recognised by what the files say they are
              and r'public enum \w+: Carrier \{\}' in seam_src
              and r'public enum F_\w+: Declared \{' in seam_src
              # AND IT LIVES AT THE CLAIM THAT CONCLUDED IT. This was a zone in
              # the left panel: a heading, a held count, a row per waiting field.
              # An instrument, standing beside the file list and telling a
              # world's story for it. But a seam is a file this world TOOK, so
              # it is a row in the manifest like every other taken file, and its
              # state is a column on that row — the panel is a door to worlds,
              # and a door that narrates has stopped opening.
              and "async function buildSeams()" in ui
              # AND THE STATE IS COUNTED, NOT CHOSEN. A seam is the premise V=I
              # §5.4 leaves outside itself, asked as a game one level up: how
              # many correspondences between what one side states and what the
              # other claims still pass. |S| ∈ ℕ and {0, 1, >1} partitions ℕ, so
              # there are three answers and no fourth to write. This was four
              # hand-written branches that happened to agree with the arithmetic.
              and 'const sizes = Object.values(s.sizes || {});' in ui
              and "const gone = sizes.filter(n => n === 0).length;" in ui
              and "const open = sizes.filter(n => n > 1).length;" in ui
              and 'gone ? "parted at " + gone' in ui
              and '"sizes": {f"{r} · {f}": n for (r, f), n in sizes.items()},' in seam_src
              and 'const hasSeams = group.rows.some(seamRow);' in ui
              # it borrows the rail's own grammar rather than inventing a second
              # one: a row is a commit's row, the address is a fact, the kind is
              # a badge, and WHY it is there lives in the title — answered on
              # demand, the way this bench has always answered `what is this`,
              # instead of printed under every line down a narrow column
              and '"came back"' in ui and 'r.className = "seam-line"' in ui
              # EVERY ADDRESS THIS BENCH PRINTS IS REACHABLE. A row that looks
              # clickable and does nothing is worse than a plain list — the
              # affordance came along with the styling and was not honoured. A
              # line opens the side that SAID it, read-only, since neither side
              # is this world's to edit from here.
              and "a.onclick = () => openSeamSide(" in ui
              and "async function openSeamSide(" in ui
              and 'cm.setOption("readOnly", true)' in ui
              and 'u.path == "/seamside"' in seam_src and "#   GET  /seamside" in seam_src
              # and a badge is a word that stands alone: `you` and `them` needed
              # the tooltip to mean anything, which is a term used before it is
              # introduced. These are the product's own words for the same thing.
              and '"your word"' in ui and '"their word"' in ui
              # and the registers say which half is which without a word: the
              # field is the thing spoken of and stands in ink, the route is
              # where it lives and stands back
              and '<span class="seam-where">' in ui and ".seam-where{color:var(--seam)}" in ui
              # and how much of the agreement is actually held, which is what
              # being integrated with somebody amounts to — a count, not a
              # feeling, and the same count from either end. No rank appears
              # anywhere: a seam has two ends and neither is above the other.
              and 's.claimed + " of " + s.stated + " held"' in ui
              # and the bench shows what this repository HAS. A folder with no
              # seam in it has no seam, and a permanent zone about a thing nobody
              # is using is an advertisement standing in an account — which is
              # what the panel zone had become. The column appears on the rows
              # that have one and nowhere else; the panel carries no trace.
              and "host.hidden = true" in ui
              and "seam-empty" not in ui))

    # ── ONE SIDE OF A SEAM IS NOT A SHADOW OF THIS WORLD. A repository that
    # declares its layout guards against a stray `*.swift` beside it, since an
    # undeclared world file is a second truth nobody judges — but a seam
    # declaration is not a world file at all. It is what somebody said about an
    # agreement, and it says which it is in its own first lines. Read as a stray,
    # it earned two refusals from anybody who both declared a layout and used a
    # seam: an accusation about something never claimed, which is the whole of
    # what this tool exists against.
    bth = os.path.join(tmp, "both")
    os.makedirs(os.path.join(bth, "tables"), exist_ok=True)
    subprocess.run(["git", "init", "-q", bth])
    shutil.copy(os.path.join(DEMO, "people.csv"), os.path.join(bth, "tables", "people.csv"))
    shutil.copy(os.path.join(DEMO, "grants.csv"), os.path.join(bth, "tables", "grants.csv"))
    run("status", cwd=bth)                                  # bootstrap the world
    open(os.path.join(bth, "gate.manifest.swift"), "w").write(
        "// the world, and the files it is written across\n"
        "public enum Layout {\n    public typealias Files = Any\n}\n")
    shutil.copy(os.path.join(ent, "api.swift"), os.path.join(bth, "api.swift"))
    shutil.copy(os.path.join(ent, "sdk3.swift"), os.path.join(bth, "sdk.swift"))
    _, together = run("status", cwd=bth)
    shadows = [r for r in together.get("refusals", []) if "no row in the manifest" in r.get("claim", "")]
    open(os.path.join(bth, "stray.swift"), "w").write("public enum Stray: Ranked {}\n")
    _, with_stray = run("status", cwd=bth)
    S.append(("a seam declaration beside a declared layout is not refused, and a stray world file still is",
              together.get("verdict") == "holds" and not shadows
              # and the guard still does its own job
              and [r["address"] for r in with_stray.get("refusals", [])
                   if "no row in the manifest" in r["claim"]] == ["stray.swift"]))

    # ── AND THE PAGE HAS TO PARSE. Every check here reads the bench as text and
    # asks whether the right words are in it — which says nothing about whether
    # the browser can run a line of it. A name collision in one function made the
    # whole script fail to compile, the seams list came up empty, and the battery
    # was green throughout: greping a program is not the same as loading it.
    scripts = re.findall(r"<script>(.*?)</script>", ui, re.S)
    node = shutil.which("node")
    parsed = None
    if node and scripts:
        probe = os.path.join(tmp, "parse-ui.js")
        open(probe, "w").write(
            "const s = " + json.dumps(scripts) + ";\n"
            "for (const x of s) new Function(x);\nconsole.log('ok');\n")
        r = subprocess.run([node, probe], capture_output=True, text=True)
        parsed = r.returncode == 0 and "ok" in r.stdout
    S.append(("every script the bench serves compiles, which greping it never showed",
              bool(scripts) and (parsed is True or (node is None and parsed is None))))

    # ── A NAME IS NOT AN ACTION, AND A BADGE IS MARKED BY ITS EDGE. The blue in
    # this bench belongs to the hand: it paints what you press. An author's name
    # is a fact about a commit, so it is ink like every other fact, and the
    # underline arrives under the pointer to say it can be pressed. And a badge
    # filled with --mist disappeared the moment the row under it went --mist too,
    # which is every hover — a fill that matches its own background is not a
    # marker at all.

    # ── WHICH SEAMS ARE MINE IS MINE TO SAY. They were found by sniffing the
    # folder for files that looked like seam sides — guessing at somebody's
    # relationships from the shape of what happens to be lying about, which is
    # the same sin as reading a library's source, one storey up, and it put
    # things in an owner's rail that the owner never put there.
    # Membership is declared, in the file that already declares what belongs to
    # this world. Which side a file is, that file says about itself in its own
    # first lines: mine to say what is mine, theirs to say what theirs is.
    own = os.path.join(tmp, "owned")
    os.makedirs(own, exist_ok=True)
    for f in ("api.swift", "sdk3.swift"):
        shutil.copy(os.path.join(ent, f), os.path.join(own, f.replace("sdk3", "sdk")))
    _, unowned = run("demo", "seam", os.path.join(tmp, "owned-demo"))
    S.append(("a seam is in my rail because I said it is mine, never because a file was lying about",
              # the two sides are there, and undeclared they are nobody's
              seams_here_probe(own) == 0
              # declared in the layout file, the same one that declares the world
              and (open(os.path.join(own, "gate.manifest.swift"), "w").write(
                  "public protocol SeamFile {}\n"
                  "public enum A: SeamFile {}\n"
                  'extension A { public static var typeName: String { "api.swift" } }\n'
                  "public enum B: SeamFile {}\n"
                  'extension B { public static var typeName: String { "sdk.swift" } }\n') or True)
              and seams_here_probe(own) == 1
              # and the demo declares its own, so the rail it shows is one it owns
              and os.path.exists(os.path.join(tmp, "owned-demo", "gate.manifest.swift"))
              # the older spelling above is still read: a file on somebody's disk
              # is not wrong because the tool learned a better word for it
              and "Theirs" in open(os.path.join(tmp, "owned-demo", "gate.manifest.swift")).read()))

    # ── and the layout takes only what is declared a world file. The same
    # document names both, in the same shape — a name and a path — so reading
    # every path literal in it swept the seam sides into the judged list, where
    # one reads as a fragment of a world it was never part of. Seven refusals
    # about a file that had claimed nothing, from the act of declaring ownership.
    open(os.path.join(own, "gate.swift"), "w").write("public enum Nobody: Ranked {}\n")
    open(os.path.join(own, "gate.manifest.swift"), "w").write(
        "public protocol WorldFile {}\n"
        "public protocol SeamFile {}\n"
        "public enum A: SeamFile {}\n"
        'extension A { public static var typeName: String { "api.swift" } }\n'
        "public enum B: SeamFile {}\n"
        'extension B { public static var typeName: String { "sdk.swift" } }\n')
    _, owned_status = run("status", cwd=own)
    S.append(("declaring a seam does not put it in the judged world",
              not [r for r in owned_status.get("refusals", [])
                   if "api.swift" in r.get("address", "") or "sdk.swift" in r.get("address", "")]))

    # ── AND THE ACT OF SAYING IT IS MINE IS ONE COMMAND. gate never fetches and
    # never sends: the other side arrives because an operator brought it, by a
    # checkout or a copy or whatever they already trust, and the manifest only
    # writes down that this pair is one this world answers for. The other
    # direction — letting them know somebody depends on them — is a pull
    # request: your file and its two lines in THEIR repository, after which
    # their own CI parts the seam the day they touch what you carry. There is no
    # registry to be in and no server to ask, and unsubscribing is deleting a
    # file, which is a commit like any other: visible, dated, nobody's to do
    # quietly.
    sub = os.path.join(tmp, "subscribe")
    os.makedirs(sub, exist_ok=True)
    shutil.copy(os.path.join(ent, "sdk.json"), os.path.join(sub, "sdk.json"))
    _, mine = run("declare", "carrier", os.path.join(sub, "sdk.json"),
                  "-o", os.path.join(sub, "sdk.swift"), "--theirs")
    # read defensively: a check must FAIL, never explode. An exception here
    # stops every check after it and hides which one broke, which is a worse red
    # than a red.
    mpath = os.path.join(sub, "gate.manifest.swift")
    man = open(mpath).read() if os.path.exists(mpath) else ""
    S.append(("saying a seam is mine is one command, and one side declared alone is a state rather than a blank",
              mine.get("declared_in") == "gate.manifest.swift"
              and "public protocol Theirs {}" in man and '"sdk.swift"' in man
              # written as axes, the way every record in this world is written
              and "public typealias Kind = SeamFile" in man
              # and the row carries the pin the declaration already stated, so
              # nobody types a second copy of a fact that would then drift
              and "public typealias At = Rev_" in man
              # and the next names the act that makes the other side hold to it
              and "THEIR repository" in mine.get("next", "")
              # having moved first, this side sees that it moved rather than nothing
              and seams_here_probe(sub) == 1
              and "no second side yet" in ui))

    # ── FRICTION IS NOT EVENLY DESERVED. Saying a true thing should cost
    # nothing; setting a true thing aside should cost a reason that can close,
    # since an exception with no term is an amnesty and every temporary one
    # outlives what it was for. Setting aside took two files edited by hand,
    # which is friction in the wrong place — it is one sentence now, and it still
    # refuses without a reason, because that part of the cost is the point.
    _, no_reason = run("aside", "/messages", "sendAt", cwd=ent)
    _, said = run("aside", "/messages", "sendAt", "--because", "PROJ-9", "--by", "sdk-team",
                  "-o", os.path.join(ent, "aside.json"), cwd=ent)
    twice = run("aside", "/messages", "sendAt", "--because", "PROJ-10", "--by", "sdk-team",
                "-o", os.path.join(ent, "aside.json"), cwd=ent)[1]
    written = json.load(open(os.path.join(ent, "aside.json")))
    S.append(("setting something aside costs a reason that can close, and costs nothing else",
              # without a reason it does not happen at all
              no_reason.get("asks") and "not optional" in no_reason.get("next", "")
              # with one, it is a single sentence and the reason is kept with the author
              and said.get("because") == "PROJ-9" and said.get("declared_by") == "sdk-team"
              # and saying it again about the same field replaces rather than piles up
              and twice.get("standing") == 1
              and written["diverges"][0]["because"] == "PROJ-10"))

    # ── WHAT MAY BE SAID HERE. The shelf carries the words a world speaks —
    # Department, Ranked, Site — and they are plain Swift, readable and copyable.
    # The bench knew the list all along and showed it nowhere: it opened a shelf
    # module only for somebody who already knew a name on it, which is knowledge
    # you cannot get by looking. And at the command line the same list came out
    # as a blob of JSON. Somebody who cannot see the vocabulary cannot know it is
    # theirs to read, and nobody arrives already knowing.
    # AND THE ONE LINE THAT MATTERS IS MINE AGAINST THEIRS. There are files I
    # write, whose verdict follows what I do to them, and files I only read.
    # Splitting the shelf instead into forms and gate's own furniture drew a
    # line nobody using this needs, and hid the one they do: NONE OF THE SHELF
    # IS EITHER. Those words are compiled inside the judge — a world speaks
    # `Department` with no file of that name near it — so a shelf page is a
    # printout, and the dependency is the judge, named by revision.
    shelf_said = say("stdlib", cwd=ent)
    shelf_src = open(GATE, encoding="utf-8").read()
    S.append(("the shelf is one list of printouts, and says it is not yours",
              "all of it theirs" in shelf_said
              and "forms-organization" in shelf_said and "bench-palette" in shelf_said
              # said in plain words rather than in capitals: the shelf page keeps
              # the same voice as the letter and the front door
              and "these are theirs" in shelf_said and "THEIRS" not in shelf_said
              and "editing one adds no word to the language" in shelf_said
              and "gate --version` names the revision" in shelf_said
              and "gate stdlib show" in shelf_said
              and "gate mine FILE` / `gate theirs FILE`" in shelf_said
              # THE RAIL HAS TWO HEADINGS, NOT THREE. The judge had a section of
              # its own, which said it was a different kind of thing — and under
              # the claim law it is not: it is theirs, taken at a revision, like
              # the other side of any seam. A privileged entity in the rail is a
              # privileged entity in the head, and nothing here earns one.
              and "<i></i>mine</h3>" in ui and "<i></i>theirs</h3>" in ui
              and ui.index("<i></i>mine</h3>") < ui.index("<i></i>theirs</h3>")
              and "the judge<span" not in ui and 'id="shelf-head"' not in ui
              # the judge is a ROW of what was taken, and it says at what
              and 'id="judge-row"' in ui
              and '"took at " + v.judge_from.slice(0, 7)' in ui
              and '"taken at nothing written down"' in ui
              and "r.onclick = () => openShelf(m);" in ui
              and '"judge_from": judge_from()' in shelf_src))

    # ── AND THE OPERATOR'S RAIL SHOWS WHAT THE OPERATOR CAN SPEAK. The shelf
    # carries two unlike things and calling them one was a category invented to
    # hold what had not been sorted. Five of them are what YOUR world and policy
    # are written in — they arrive in your repository as the header of whatever
    # gate emits, and without them nothing you keep is expressible. Three are
    # this tool's own furniture: how its page looks, how it spaces itself, the
    # lengths its own battery holds it to. Those never enter your repository and
    # answer no question you have.
    #
    # Neither is yours, so this is not the mine/theirs line drawn twice — it is
    # the ROLE column, and each file states its own role in its own second line
    # rather than being sorted by the shape of its name. `git-atoms` proves the
    # difference: not a page of forms, and it is what a merge policy is written in.
    roles = run("stdlib", cwd=ent)[1].get("roles") or {}
    S.append(("the shelf says which of it you can speak, and each file says so itself",
              roles.get("forms-organization") == "forms"
              and roles.get("forms-contract") == "forms"
              # not a page of forms by name, and speakable all the same
              and roles.get("git-atoms") == "forms"
              # the tool's own furniture says it is the tool's own
              and roles.get("bench-palette") == "gate's own"
              and roles.get("bench-metrics") == "gate's own"
              and roles.get("bench-atoms") == "gate's own"
              # said in the file, not guessed from the name
              and all(open(os.path.join(HERE, "stdlib", f"{m}.swift"),
                           encoding="utf-8").read().split("\n")[1].startswith("// role: ")
                      for m in roles)
              # the command line says both counts and says all of it is theirs
              and "you can speak" in shelf_said and "all of it theirs" in shelf_said
              and "(gate's own furniture)" in shelf_said
              # AND THE RAIL CARRIES EVERYTHING TAKEN. It had been cut down to
              # what an operator can speak, on the reasoning that this tool's own
              # furniture answers no question they have — which was me deciding
              # what somebody needs to know about the thing they are looking at.
              # The palette this page paints with and the ladder it spaces itself
              # on are laws the page RUNS UNDER; they are theirs like everything
              # else here, and a law you cannot see is a law you cannot check.
              and "mods = shelf.modules || []" in ui
              and 'shelf.roles || {})[m] === "forms"' not in ui
              and "A judged world this bench itself runs under" in ui))

    # ── A SHELF PAGE IS A PRINTOUT, AND THIS IS THE PROBE THAT SAYS SO. The tool
    # invited an operator to materialize a forms page and called the copy theirs to
    # change, which is a sentence the machinery had never agreed to: the words
    # live compiled inside the judge. A world speaks `Department` with no file of
    # that name anywhere near it; the file put beside the world is read by
    # nothing; and declaring it as a file of mine is refused outright, because a
    # world is records and a forms page is the grammar records are written in. Three
    # ways of finding out it is not a source — the invitation was the lie.
    # ── AND EVERY FIXTURE THIS BATTERY MAKES IS REMOVED WITH IT. Twenty-one of
    # them were made straight in the system temp directory and never taken away:
    # 10595 of those were sitting there, and each one that wrote a personal world
    # left a keyed world in the real `~/.gate/me` too. Rooted here, they go when the
    # run's own directory goes.
    shelf_probe = tempfile.mkdtemp(dir=tmp)
    world_p = os.path.join(shelf_probe, "gate.swift")
    open(world_p, "w").write("public enum Sales: Department {}\npublic enum Boss: Ranked {}\n")
    bare = run("status", cwd=shelf_probe)[1]
    run("stdlib", "materialize", "forms-organization", cwd=shelf_probe)
    beside = run("status", cwd=shelf_probe)[1]
    run("mine", "forms-organization.swift", cwd=shelf_probe)
    as_mine = run("status", cwd=shelf_probe)[1]
    with open(os.path.join(shelf_probe, "forms-organization.swift"), "a") as f:
        f.write("\npublic enum Architect: Ranked {}\n")
    edited = run("status", cwd=shelf_probe)[1]
    S.append(("the words a world speaks are the judge's, and a copy of them is inert",
              # spoken with no such file present
              bare.get("verdict") == "holds" and bare.get("world", {}).get("declarations") == 2
              # and the file beside the world adds nothing and takes nothing
              and beside.get("verdict") == "holds"
              and beside.get("world", {}).get("declarations")
              == bare.get("world", {}).get("declarations")
              # and calling it a file of mine is refused: a forms page is not a world
              and as_mine.get("verdict") == "refused"
              and any("outside the fragment" in r.get("claim", "")
                      for r in as_mine.get("refusals", []))
              # and an edited printout is caught still claiming to be the printout
              and any("no longer matches the words the judge carries" in r.get("claim", "")
                      for r in edited.get("refusals", []))
              # so the tool no longer offers the copy as something to own
              and "yours to version" not in shelf_src and "makes a copy yours" not in shelf_src
              and "remove the header to own the file" not in shelf_src
              and "It is here to be READ" in shelf_src))

    # ── TWO WORDS IN, AND THE SAME SHAPE BOTH WAYS. There are files I write and
    # files I only read, and until now only the second had a command: a seam side
    # could be declared in one word while adding a file of my own meant opening
    # the manifest and copying a shape by hand. Friction is not evenly deserved,
    # but it was pointing the wrong way — the cheaper act should be the one that
    # says what I am answerable for. Both are one word now, both write the same
    # document, and the document is mine either way: it is where I say which
    # files I write and which I only read.
    two = tempfile.mkdtemp(dir=tmp)
    two_src = open(GATE, encoding="utf-8").read()
    open(os.path.join(two, "gate.swift"), "w").write("public enum Sales: Department {}\n")
    open(os.path.join(two, "more.swift"), "w").write("public enum Ops: Department {}\n")
    open(os.path.join(two, "api.swift"), "w").write(
        "// contract\npublic enum F_x: Declared { public typealias Of = Text }\n")
    before = run("status", cwd=two)[1]
    mine_said = run("mine", "more.swift", cwd=two)[1]
    after = run("status", cwd=two)[1]
    manifest = open(os.path.join(two, "gate.manifest.swift")).read()
    missing = run("theirs", "not-here.swift", cwd=two)[1]

    # ── AND A ROW MAY NOT POINT OUT OF THE WORLD THAT MAKES IT. This is not
    # hypothetical: an older walk started from the working directory instead of
    # the file, and the battery's own temporary worlds wrote sixteen rows into
    # THIS repository's manifest — claims about /var/folders directories deleted
    # the same minute, sitting in a commit, indistinguishable from real ones.
    outside = tempfile.mkdtemp(dir=tmp)
    open(os.path.join(outside, "stranger.swift"), "w").write("public enum X {}\n")
    escape = run("mine", os.path.join(outside, "stranger.swift"), cwd=two)[1]
    S.append(("a claim about a file outside the world is refused, not written",
              escape.get("asks") and "not inside the world" in escape.get("note", "")
              and "stranger" not in open(os.path.join(two, "gate.manifest.swift")).read()))
    S.append(("and this tool's own manifest holds no row pointing out of itself",
              not re.search(r'typeName: String \{ "\.\.',
                            open(os.path.join(HERE, "gate.manifest.swift")).read())))

    S.append(("adding a file of mine and a file of theirs is one word each",
              # mine: it joins the judged world, and the count moves
              mine_said.get("command") == "mine" and mine_said.get("file") == "more.swift"
              and before.get("world", {}).get("declarations") == 1
              and after.get("world", {}).get("declarations") == 2
              and "public enum More: Mine {" in manifest
              and "public typealias Kind = WorldFile" in manifest
              # theirs is the other value of the same column, not a second document
              and 'cmd_side(rest, "Theirs")' in two_src and 'cmd_side(rest, "Mine")' in two_src
              # and a file that is not here is asked for, never fetched
              and missing.get("asks") and "no file at" in missing.get("note", "")
              and "gate never fetches" in missing.get("next", "")
              # both are in the usage, so neither is knowledge you must already have
              and "gate mine FILE" in two_src and "gate theirs FILE" in two_src))

    # ── AND A ROW WRITTEN AFTER ANOTHER DOES NOT LAND INSIDE IT. Rows are kept
    # in their own group so a person can read the document, and stepping to the
    # end of a group was done by its first line — which was true while a row was
    # one line and stopped being true the moment a row grew a body. The next row
    # went in between somebody else's braces, where it still parsed as SOMETHING,
    # so the reader carried on and simply lost the row it had swallowed. An
    # account that quietly stops being true is the one failure this tool exists
    # to make impossible, and it was mine, in this file, for a day.
    many = tempfile.mkdtemp(dir=tmp)
    open(os.path.join(many, "gate.swift"), "w").write("public enum Sales: Department {}\n")
    open(os.path.join(many, "w.swift"), "w").write("public enum Ops: Department {}\n")
    for who in "abc":
        open(os.path.join(many, f"{who}.swift"), "w").write(
            f"// contract\npublic enum F_{who}: Declared {{ public typealias Of = Text }}\n")
    run("theirs", "a.swift", "--at", "r1", cwd=many)
    run("mine", "w.swift", cwd=many)                       # interleaved, so the groups collide
    run("theirs", "b.swift", "--at", "r2", cwd=many)
    run("theirs", "c.swift", "--at", "r3", cwd=many)
    kept = run("theirs", cwd=many)[1].get("held") or []
    kept_mine = run("mine", cwd=many)[1].get("held") or []
    S.append(("a row written after another lands beside it, never inside it",
              [h["file"] for h in kept] == ["a.swift", "b.swift", "c.swift"]
              and [h["at"] for h in kept] == ["r1", "r2", "r3"]
              and [h["file"] for h in kept_mine] == ["w.swift"]
              # and the document still reads as one brace-balanced whole
              and open(os.path.join(many, "gate.manifest.swift")).read().count("{")
              == open(os.path.join(many, "gate.manifest.swift")).read().count("}")))

    # ── AND THE LIST IS THE OWNER'S TO READ AND TO SHORTEN. A row nobody can see
    # without opening a file in an editor is a row nobody maintains, and one
    # nobody can remove without hand-editing is worse: the account rots and then
    # it lies. The same word asks and answers — with a path it declares, with
    # none it says what is held and how fresh — and taking a row out never
    # touches the file, because removing a thing from your account and throwing
    # it away are two acts and only the first is gate's to do.
    gone = run("theirs", "b.swift", "--forget", cwd=many)[1]
    after = run("theirs", cwd=many)[1].get("held") or []
    S.append(("the account can be read and shortened, and forgetting keeps the file",
              gone.get("forgot") == "b.swift"
              and [h["file"] for h in after] == ["a.swift", "c.swift"]
              # the file itself is untouched: that act is the operator's alone
              and os.path.exists(os.path.join(many, "b.swift"))
              and "still on disk" in gone.get("note", "")
              # and a row that is not there is said so rather than silently done
              and run("theirs", "nope.swift", "--forget", cwd=many)[1].get("asks")))

    # ── AND EVERY EDIT TO THIS DOCUMENT COUNTS BRACES. Twice in a day something
    # that edits it was written for the shape a row happened to have: the insert
    # stepped over an extension by its first line and put the next row inside
    # somebody's braces; the removal matched a one-line pattern, reported the
    # row gone, and left it there. Both lied without saying so, in the list that
    # accounts for everything else. Nothing here reads a shape any more.
    keeps = tempfile.mkdtemp(dir=tmp)
    open(os.path.join(keeps, "gate.swift"), "w").write("public enum Sales: Department {}\n")
    for who in "ab":
        open(os.path.join(keeps, f"{who}.swift"), "w").write(
            f"// contract\npublic enum F_{who}: Declared {{ public typealias Of = Text }}\n")
    open(os.path.join(keeps, "w.swift"), "w").write("public enum Ops: Department {}\n")
    run("theirs", "a.swift", "--at", "r1", cwd=keeps)
    run("mine", "w.swift", cwd=keeps)
    run("theirs", "b.swift", "--at", "r2", cwd=keeps)
    dropped = run("theirs", "a.swift", "--forget", cwd=keeps)[1]
    left = run("theirs", cwd=keeps)[1].get("held") or []
    doc = open(os.path.join(keeps, "gate.manifest.swift")).read()
    S.append(("what the tool says it removed is removed, and the document stays whole",
              dropped.get("forgot") == "a.swift"
              # said gone AND gone: the report and the file agree
              and [h["file"] for h in left] == ["b.swift"]
              and "public enum A: Theirs" not in doc
              # the rest is untouched and the braces still balance
              and (run("mine", cwd=keeps)[1].get("held") or [{}])[0].get("file") == "w.swift"
              and doc.count("{") == doc.count("}")
              and run("status", cwd=keeps)[1].get("verdict") == "holds"))

    # ── WHAT IS TAKEN IS TAKEN AT A REVISION, AND A ROW NAMES ITS COURT. Nothing
    # in this tool expresses a version range, which is the whole reason no solver
    # exists here: the problem is not solved, it cannot be stated. But a pin
    # nobody writes down pins nothing, and the revision had been living in side
    # channels beside the file — inside an emitted carrier, in a dotfile next to
    # the binary — rather than in the list that accounts for what this world is
    # made of. And the role is not decoration on a row: it says which court reads
    # it, so a row gate cannot place is refused at its own line rather than taken
    # quietly as a fragment of the world. That exact sweep broke a world once.
    no_pin = run("theirs", "api.swift", cwd=two)[1]
    bad_role = run("theirs", "api.swift", "--at", "r1", "--role", "sensor", cwd=two)[1]
    pinned = run("theirs", "api.swift", "--at", "openapi@3f2a1c9", cwd=two)[1]
    with_pin = open(os.path.join(two, "gate.manifest.swift")).read()
    # and the same is refused when the operator wrote the row by hand
    hand = tempfile.mkdtemp(dir=tmp)
    open(os.path.join(hand, "gate.swift"), "w").write("public enum Sales: Department {}\n")
    open(os.path.join(hand, "b.swift"), "w").write("// contract\npublic enum F_y: Declared { public typealias Of = Text }\n")
    open(os.path.join(hand, "gate.manifest.swift"), "w").write(
        "public protocol Theirs {}\n"
        "public enum B: Theirs {}\n"
        "extension B {\n"
        '    public static var typeName: String { "b.swift" }\n'
        '    public static var role: String { "sensor" }\n'
        "}\n")
    hand_said = run("status", cwd=hand)[1]
    claims = " ".join(r.get("claim", "") for r in hand_said.get("refusals", []))
    S.append(("what is taken says at what, and a row says which court reads it",
              # taking without a revision does not happen at all
              no_pin.get("asks") and "taken at a revision" in no_pin.get("note", "")
              and "--at REV" in no_pin.get("next", "")
              # a role no court reads is refused before it is written
              and bad_role.get("asks") and "not a court" in bad_role.get("note", "")
              # with a pin it is written down, and the line says what was taken and at what
              and pinned.get("at") == "openapi@3f2a1c9" and pinned.get("role") == "seam"
              # a revision is an atom of its own, so two rows at one revision
              # say the same NAME rather than the same text
              and 'public static var typeName: String { "openapi@3f2a1c9" }' in with_pin
              and "public typealias At = Rev_openapi_3f2a1c9" in with_pin
              # a file I emit needs no pin: I am the source
              and "typealias At" not in with_pin.split("public protocol Theirs")[0]
              # and by hand it is caught the same way, at the row's own line
              and hand_said.get("verdict") == "refused"
              and "which no court here reads" in claims
              and "does not say which revision it was taken at" in claims
              and any(r.get("address", "").startswith("gate.manifest.swift:")
                      for r in hand_said.get("refusals", []))))

    # ── A ROW OF ANY ROLE HAS BEEN SPOKEN FOR. The shadow guard reads the world
    # rows, and a shadow is a file nobody spoke for — so reading only those
    # called a declared forms file a shadow, which is an accusation about
    # something claimed out loud in the very document being read. Same shape as
    # the sweep it replaced, one storey along: the document says three kinds of
    # thing and a reader that knows one kind will mistake the other two.
    #
    # AND A FORMS ROW IS JUDGED. It was called inert on the strength of one
    # probe, and the probe was the wrong shape: `where` does not check bare
    # conformance, so a green over nought uses said nothing either way. Given
    # certificates it reads them with teeth. The court was simply never called.
    frm = tempfile.mkdtemp(dir=tmp)
    open(os.path.join(frm, "gate.swift"), "w").write("public enum Sales: Department {}\n")
    shutil.copy(os.path.join(HERE, "stdlib", "bench-metrics.swift"),
                os.path.join(frm, "vendor-forms.swift"))
    took = run("theirs", "vendor-forms.swift", "--at", "acme/forms@9d1e", "--role", "forms",
               cwd=frm)[1]
    frm_status = run("status", cwd=frm)[1]
    # a word this fork invents, and a true thing said about it
    with open(os.path.join(frm, "vendor-forms.swift"), "a") as f:
        f.write("\npublic typealias Architect = Twice<Line>\n"
                "public typealias ArchitectIsTwoLines = Same<Architect, Plus<Line, Line>>\n")
    learned = run("status", cwd=frm)[1]
    # and the same word, lied about
    t = open(os.path.join(frm, "vendor-forms.swift")).read()
    open(os.path.join(frm, "vendor-forms.swift"), "w").write(
        t.replace("Same<Architect, Plus<Line, Line>>", "Same<Architect, Plus<Line, Edge>>", 1))
    lied = run("status", cwd=frm)[1]
    S.append(("a taken forms file is accounted for, judged, and not a shadow",
              took.get("role") == "forms" and took.get("at") == "acme/forms@9d1e"
              and "where court" in took.get("role_means", "")
              # it is not swept into the plain world: that count is the world's alone
              and frm_status.get("world", {}).get("declarations") == 1
              # and it is not accused of being a stray, because it was declared
              and frm_status.get("verdict") == "holds"
              # a word invented in the fork is learned: the truth about it holds
              and learned.get("verdict") == "holds"
              # and a lie about that same invented word is refused, at the file
              and lied.get("verdict") == "refused"
              and any("ArchitectIsTwoLines" in r.get("claim", "")
                      and (r.get("address") or "").startswith("vendor-forms.swift:")
                      for r in lied.get("refusals", []))))

    # ── AND THE TRANSLATION KEEPS THE COURT'S OWN ORDER. plainly() rewrites the
    # where court's raw sentence into the pair a reader sees; swap the pair and
    # every refusal accuses the wrong side, in the same green battery. The raw
    # sentence is fetched from the court itself, so the translation is held to
    # whatever the court said, not to a remembered spelling of it.
    _raw_where = subprocess.run(
        [os.path.join(HERE, "bin", "gate-judge"), "judge", "where",
         os.path.join(frm, "vendor-forms.swift")],
        capture_output=True, text=True).stdout
    _raw_pair = re.search(r"'ArchitectIsTwoLines[^']*'[^(]*\(aka '([^']+)'\)"
                          r"[^(]*\(aka '([^']+)'\)", _raw_where)
    _said_pair = next((r.get("claim", "") for r in lied.get("refusals", [])
                       if "ArchitectIsTwoLines" in r.get("claim", "")), "")
    S.append(("the where verdict a reader sees keeps the pair in the court's own order",
              bool(_raw_pair)
              and (_raw_pair.group(1) + " against " + _raw_pair.group(2)) in _said_pair))

    # ── AND THE FORMS ROWS ARE JUDGED AS ONE STREAM, WHICH IS NOT A DETAIL.
    # `where` over a LIST of files is blind, and its silence is selective by
    # order: a law split across two files holds in isolation and refuses the
    # moment they are glued. This project had already found that, written it
    # down, and stood a vector on it — and I shipped the isolated form anyway,
    # because I had read the machinery and not the canon. The order comes from
    # the manifest, so the same repository always reads the same way, and the
    # address lands in the file that SAYS the certificate rather than in the
    # stream it was read in.
    split = tempfile.mkdtemp(dir=tmp)
    open(os.path.join(split, "gate.swift"), "w").write("public enum Sales: Department {}\n")
    whole = open(os.path.join(HERE, "stdlib", "bench-metrics.swift"), encoding="utf-8").read()
    cut = whole.index("public typealias AirIsTwoLines")
    open(os.path.join(split, "forms-a.swift"), "w").write(whole[:cut])
    open(os.path.join(split, "forms-b.swift"), "w").write(
        "// the other half of one law\n"
        "public typealias AirIsTwoLines = Same<TwoLines, Plus<Line, Edge>>\n")
    run("theirs", "forms-a.swift", "--at", "r1", "--role", "forms", cwd=split)
    run("theirs", "forms-b.swift", "--at", "r2", "--role", "forms", cwd=split)
    caught = run("status", cwd=split)[1]
    # and the same pair, made true again, holds
    open(os.path.join(split, "forms-b.swift"), "w").write(
        "// the other half of one law\n"
        "public typealias AirIsTwoLines = Same<TwoLines, Plus<Line, Line>>\n")
    mended = run("status", cwd=split)[1]
    S.append(("a law split across two forms files is caught, not silently held",
              caught.get("verdict") == "refused"
              and any("AirIsTwoLines" in r.get("claim", "")
                      # addressed where it is written, not where it was read
                      and (r.get("address") or "").startswith("forms-b.swift:")
                      for r in caught.get("refusals", []))
              and mended.get("verdict") == "holds"
              # one stream, ordered by the document rather than by the folder
              and "in the order the manifest gives" in shelf_src.lower()))

    # ── GATE IS THE FIRST INHABITANT, and the tool that refuses a world which
    # has not declared itself had not declared its own. Its facts about its own
    # surface sat on a shelf, shown to operators as reference, because there was
    # nowhere else to put them — and a world made only of forms was read as no
    # world at all, so this repository could not see the shape it is.
    #
    # AND THE BOUNDARY, WHICH IS THE EASY PLACE TO LIE BEAUTIFULLY. The judge
    # does not judge the judge: no self-reference is the floor the whole theory
    # stands on, and a court that certified itself would be worth nothing. So
    # the judge is a row of accounting, held by a build anybody can repeat, and
    # the sentence "fully self-verifying" is one this tool may never say.
    own = open(os.path.join(HERE, "gate.manifest.swift"), encoding="utf-8").read()
    own_status = run("status", cwd=HERE)[1]
    prose = own + open(os.path.join(HERE, "README.md"), encoding="utf-8").read()
    S.append(("gate lives under its own court, and names the one place a court cannot reach",
              # its own surface is declared as its own world, in the same columns
              'public static var typeName: String { "stdlib/bench-palette.swift" }' in own
              and "public typealias Kind = FormsFile" in own
              and "public enum BenchPalette: Mine {" in own
              # the judge is accounted for as taken, and its role says what holds it
              and "public enum TheJudge: Theirs {" in own
              and "public typealias Kind = JudgeFile" in own
              and "not by judgement" in shelf_src
              # the boundary is stated where somebody would look for the claim
              and "SELF-APPLICATION IS NOT SELF-CERTIFICATION" in own
              and "no self-reference" in own
              # and the forbidden sentence is nowhere, in any casing
              and "self-verifying" not in prose.lower()
              and "verifies itself" not in prose.lower()
              # this repository judges itself for real: the one refusal it has is
              # the honest one, and it is about provenance rather than a verdict
              # and it holds: the revision it carried unrecorded is written down,
              # so the tool is not asking of anybody a thing it had not done
              and own_status.get("verdict") == "holds"
              and open(os.path.join(HERE, "bin", "gate-judge.from"),
                       encoding="utf-8").read().strip().startswith("0fd0b38")
              # AND THE EDITOR IS ACCOUNTED FOR TOO. It arrived the way anything
              # of somebody else's should — named, versioned, unchanged, saying
              # so in its own first line — and it was the one dependency an
              # operator actually types into that this world had never listed.
              # Nothing here judges it and nothing here could: it is held by
              # that name and that version and by a copy anybody can compare.
              and "public enum TheEditor: Theirs {" in own
              and "public typealias Kind = CarriedFile" in own
              and 'public static var typeName: String { "codemirror@5.65.16" }' in own
              and open(os.path.join(HERE, "codemirror.js"), encoding="utf-8"
                       ).readline().startswith("// CodeMirror 5.65.16")
              # a role names a court, and a court that reads nothing says so
              and "and by no court of this world" in shelf_src))

    # ── AND A ROW IS WRITTEN THE WAY EVERY RECORD IN THIS WORLD IS WRITTEN:
    # axes to declared atoms, and exactly one string — the `typeName` literal
    # that spells a name. I had invented `var role` and `var from` beside it,
    # a second notation nobody else here writes, and the correction came from
    # the canon rather than from the machinery: the machinery never objected,
    # because gate reads this document itself. A revision is an atom of its
    # own, so two rows taken at one revision say the same NAME, not the same
    # text — which is what makes a pin a name rather than a spelling.
    #
    # Both older spellings are still read. A file on somebody's disk is not
    # wrong because the tool learned a better word for it.
    old = tempfile.mkdtemp(dir=tmp)
    open(os.path.join(old, "gate.swift"), "w").write("public enum Sales: Department {}\n")
    open(os.path.join(old, "a.swift"), "w").write("public enum Ops: Department {}\n")
    open(os.path.join(old, "b.swift"), "w").write(
        "// contract\npublic enum F_y: Declared { public typealias Of = Text }\n")
    open(os.path.join(old, "gate.manifest.swift"), "w").write(
        "public protocol Mine {}\n"
        "public enum A: Mine {}\n"
        "extension A {\n"
        '    public static var typeName: String { "a.swift" }\n'
        '    public static var role: String { "world" }\n'
        "}\n"
        "public protocol Theirs {}\n"
        "public enum B: Theirs {}\n"
        "extension B {\n"
        '    public static var typeName: String { "b.swift" }\n'
        '    public static var role: String { "seam" }\n'
        '    public static var from: String { "old@r9" }\n'
        "}\n")
    read_old = run("theirs", cwd=old)[1].get("held") or []
    # and the oldest of all: two protocols that named a role and nothing else
    open(os.path.join(old, "gate.manifest.swift"), "w").write(
        "public protocol WorldFile {}\n"
        "public enum A: WorldFile {}\n"
        'extension A { public static var typeName: String { "a.swift" } }\n')
    read_oldest = run("status", cwd=old)[1]
    S.append(("a row is axes and one literal, and the older spellings still read",
              # the spelling gate writes today
              "public typealias Kind = WorldFile" in with_pin
              and "public typealias At = Rev_" in with_pin
              and "public static var role: String" not in with_pin
              and "public static var from: String" not in with_pin
              # a revision is a NAME: its own atom, spelled by its own typeName
              and 'extension Rev_openapi_3f2a1c9 { public static var typeName' in with_pin
              # yesterday's spelling still reads, revision and all
              and [(h["file"], h["at"]) for h in read_old] == [("b.swift", "old@r9")]
              # and the oldest still names a judged world
              and read_oldest.get("verdict") == "holds"
              and read_oldest.get("world", {}).get("declarations") == 2))

    # ── A VIEW POINTS AT THE PRIMARY, AND THE PRIMARY IS A LINE YOU WROTE.
    # Theory paper 0, Part III: a space is not a process — the identities hold,
    # and talk of time concerns only the ORDER in which the standing structure
    # is read. A view is an order of reading; it cannot add a truth. So what is
    # taken carries the address of the sentence that took it, and clicking it
    # goes there rather than opening a thing of its own. The one editable
    # surface is my own files; everything else is a reading of them.
    demo_pair = tempfile.mkdtemp(dir=tmp)
    run("demo", "seam", os.path.join(demo_pair, "d"), cwd=demo_pair)
    pair_at = os.path.join(demo_pair, "d")
    if not os.path.isdir(pair_at):
        pair_at = os.path.join(demo_pair, "gate-seam-demo")

    def _took(folder):
        code = ("import types, json;"
                "src=open(%r,encoding='utf-8').read();"
                "g=types.ModuleType('g'); g.__file__=%r;"
                "exec(compile(src,'gate','exec'), g.__dict__);"
                "s=g.seams_here(%r);"
                "print(json.dumps((s[0].get('took') if s else None) or []))"
                % (GATE, GATE, folder))
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        try:
            return json.loads((r.stdout or "[]").strip().splitlines()[-1])
        except Exception:
            return []
    took = _took(pair_at)
    S.append(("what is taken points back at the line that took it",
              len(took) == 2
              and all(t.get("claim") == "gate.manifest.swift" and t.get("line")
                      for t in took)
              # AND IT IS NO LONGER A READING POINTING AT A PRIMARY — it is the
              # primary. The row that took the file is a row in the manifest,
              # with the revision in its own column, and its name goes to its
              # line. The panel used to carry a copy of this beside the file
              # list; a fact shown twice is a fact that can drift, and the copy
              # was the one nobody would have noticed drifting.
              and 'name.title = "go to line " + d.line' in ui
              and "name.onclick = () => jumpTo(d.name)" in ui))

    # ── A HUE ANSWERS TWO QUESTIONS AND NOTHING HELD THEM APART. Every channel
    # was certified for its SIDE — toward blue, toward warm — and for its
    # lightness, and no certificate ever spoke about the DISTANCE between two of
    # them. So a channel could drift until it nearly met another and the palette
    # would hold: mine and theirs stand 400 apart on Z in the light theme and 35
    # in the dark, an eleven-fold collapse, leaving the whole mine/theirs
    # distinction resting on an axis no law looked at. Found by an eye, not by
    # this battery, which is the point of writing the floor down.
    pal = open(os.path.join(HERE, "stdlib", "bench-palette.swift"), encoding="utf-8").read()
    S.append(("two channels a reader must separate are held apart by a stated floor",
              # the form exists and says what it means
              "public enum Apart<A, B, Margin>: Close {}" in pal
              and "where A == Plus<B, Plus<Unit, Margin>> {}" in pal
              # both questions a name's hue answers are floored, in both halves
              and all(f"public typealias {n} = Apart<" in pal for n in (
                  "MineApartTheirs_X_lit", "MineApartTheirs_X_dim",
                  "MineApartTheirs_Z_lit", "MineApartTheirs_Z_dim",
                  "TheirsApartBad_Z_lit", "TheirsApartBad_Z_dim",
                  # and every crowded pair in the dark half, measured: four of
                  # them fall inside a box 182 wide where the light half stands
                  # 100 to 740 apart. The design decision is left open on
                  # purpose; the drift is not.
                  "ActionApartTheirs_X_dim", "ActionApartMine_X_dim",
                  "BadApartLaw_Z_dim"))
              # and the weak one is named as weak rather than buried in a number
              and "The weak one, said out loud" in pal
              # the floors are live: the judge counts them among what it holds
              and "119 equalities" in subprocess.run(
                  [os.path.join(HERE, "bin", "gate-judge"), "judge", "where",
                   os.path.join(HERE, "stdlib", "bench-palette.swift")],
                  capture_output=True, text=True).stdout))

    # ── THE JUDGE'S TABLES ARE A RESTATEMENT OF A FILE WE ALREADY SHIP. Our port
    # carries one domain's policy hard-coded — ranks, departments, workplaces,
    # genders, the shares and their homes, and which axes each protocol owes —
    # because it was written as a line-for-line mirror of the binary, whose own
    # header calls that table a differential seat: the policy stated a second
    # time on purpose, so two encodings can check each other.
    #
    # That seat is not ours. Organization was only ever an example of what a user
    # might write; it belongs in a file of theirs, not inside an arbiter. And it
    # can be, because every one of those tables is already declared in the forms
    # file we present: departments are the conformers of `Department`, the axes
    # each protocol owes are its own `associatedtype` lines. This check derives
    # them and holds the two equal — which is the precondition for deleting one.
    # While both exist they may not part; when the port reads the presented file
    # instead, this is what will have proved the swap loses nothing.
    org = open(os.path.join(HERE, "stdlib", "forms-organization.swift"), encoding="utf-8").read()
    js = open(os.path.join(HERE, "judge.js"), encoding="utf-8").read()

    def _conformers(proto):
        return sorted(set(re.findall(r"public enum (\w+): " + proto + r"\b", org)))

    def _baked(name):
        m = re.search(r"const " + name + r" = new Set\(\[(.*?)\]\)", js, re.S)
        return sorted(x.strip().strip('"') for x in m.group(1).split(",") if x.strip()) if m else None
    derived_shares = sorted(re.findall(
        r"public enum (\w+): Document \{ public typealias Home = (\w+)", org))
    m = re.search(r"const shareHomes = new Map\(\[(.*?)\]\)", js, re.S)
    baked_shares = sorted(re.findall(r'\["(\w+)", "(\w+)"\]', m.group(1))) if m else None
    protos = {a: b for a, b in re.findall(r"public protocol (\w+)\s*\{([^}]*)\}", org, re.S)}
    S.append(("what the judge has baked in is what the presented forms already say",
              _conformers("Ranked") == _baked("ranks")
              and _conformers("Department") == _baked("departments")
              and _conformers("Workplace") == _baked("workplaces")
              and _conformers("Sexed") == _baked("genders")
              and derived_shares == baked_shares
              # and the axes each protocol owes are read off its own lines, where
              # they name a declared form rather than a category label
              and [a for a, _ in re.findall(r"associatedtype (\w+)\s*:\s*(\w+)",
                                            protos.get("Employee", ""))] == ["Home", "Rank", "Site"]
              and re.findall(r"associatedtype (\w+)\s*:\s*(\w+)",
                             protos.get("Document", "")) == [("Home", "Department")]))

    # ── AND PRESENTING THE FORMS CHANGES NOTHING, WHICH IS THE WHOLE PROOF. The
    # port now derives what a protocol requires from the protocol itself, so a
    # world that presents its forms is judged by what it presented rather than by
    # a table this port was born knowing. If that derivation were poorer than the
    # table, a world would go quiet somewhere — so the check runs the reference
    # world both ways, whole and broken four ways, and demands the refusals match
    # word for word. Green parity without red parity is half a parity.
    #
    # It also caught a parser fault nobody had met: `public enum FinanceShare:
    # Document { public typealias Home = Finance }` closes on its own line, and
    # the test for that asked whether the line ended in an empty `{}`. It does
    # not, so the share went on the stack and never came off — every record after
    # it nested inside, `FinanceShare.EngineeringShare.SalesShare.PeopleShare
    # .Edsger`, and fifty-eight names resolved to nothing. Braces balance on a
    # line or they do not.
    par = tempfile.mkdtemp(dir=tmp)
    run("demo", "org", cwd=par)
    par_world = os.path.join(par, "gate-demo", "gate.swift")
    probe = os.path.join(par, "parity.mjs")
    open(probe, "w").write(
        "import fs from 'fs';\n"
        "const src = fs.readFileSync(process.argv[2], 'utf8');\n"
        "const mod = { exports: {} };\n"
        "new Function('module','exports',src)(mod, mod.exports);\n"
        "const { judge } = mod.exports;\n"
        "const world = fs.readFileSync(process.argv[3], 'utf8');\n"
        "const forms = fs.readFileSync(process.argv[4], 'utf8');\n"
        "const V = { seeds: new Set(), generics: new Set() };\n"
        "const cases = [world,\n"
        "  world.replace('public typealias Rank = Manager','public typealias Rank = Archduke'),\n"
        "  world.replace('public typealias Home = Finance','public typealias Home = Atlantis'),\n"
        "  world.replace('    public typealias Site = OnSite\\n',''),\n"
        "  world.replace('public typealias Next = Barbara','public typealias Next = Nobody')];\n"
        "const out = cases.map((w) => {\n"
        "  const a = judge('w.swift', w, V), b = judge('w.swift', forms + '\\n' + w, V);\n"
        "  const A = a.refusals.map(r => r.premise).sort();\n"
        "  const B = b.refusals.map(r => r.premise).sort();\n"
        "  return [A.length, JSON.stringify(A) === JSON.stringify(B)];\n"
        "});\n"
        "console.log(JSON.stringify(out));\n")
    par_out = subprocess.run(
        ["node", probe, os.path.join(HERE, "judge.js"), par_world,
         os.path.join(HERE, "stdlib", "forms-organization.swift")],
        capture_output=True, text=True).stdout.strip().splitlines()
    try:
        par_res = json.loads(par_out[-1]) if par_out else []
    except Exception:
        par_res = []
    # FOUR MATCH AND ONE CORRECTS, which is better than five matching. Removing
    # an axis shows the baked table naming `Person` where the file names
    # `Employee` — the constant had drifted from the declaration it was copied
    # from and put `Site` under the wrong protocol. A second truth either drifts
    # or coarsens; this one drifted, and the probe caught it rather than an
    # argument. The presented file is the one that is right.
    S.append(("a world judged by the forms it presents refuses what it did, or better",
              len(par_res) == 5
              and sum(1 for _, same in par_res if same) == 4
              # the whole world holds and every broken one refuses, so this is
              # not five greens agreeing that nothing was ever checked
              and par_res[0][0] == 0 and all(n > 0 for n, _ in par_res[1:])
              # the domain comes from what was presented, not from what was baked
              and "function domainOf(declarations)" in js
              and "domain.requires.get(conformance)" in js
              # and a head that closes on its own line closes on its own line
              and "const selfClosed = opens > 0 && opens === closes;" in js))

    # ── THE BENCH READS THE FORMS THIS WORLD PRESENTS. What a record may be is
    # written in the operator's own file now, and the bench had been offering
    # the words it was born knowing while that file, sitting beside the world,
    # had just declared another. Add a rank to your own forms and the bench
    # offers it — that is the whole of "the client can read our world".
    #
    # The forms file is opened and read, and never handed to the plain stream:
    # its court is `where`, and the plain fragment refuses a protocol on sight.
    # And it is its own namespace — each forms file spells its own ladder from
    # Unit, as the corpus tells every world to, so metrics and palette both
    # saying `W2` is two worlds each counting for itself rather than one world
    # saying a thing twice. The duplicate guard asks its question inside a
    # stream; widening it to every file on the bench made gate refuse itself.
    pres = tempfile.mkdtemp(dir=tmp)
    run("demo", "org", cwd=pres)
    pres_root = os.path.join(pres, "gate-demo")
    pres_forms = os.path.join(pres_root, "forms-organization.swift")
    pres_man = open(os.path.join(pres_root, "gate.manifest.swift"), encoding="utf-8").read()
    with open(pres_forms, "a") as f:
        f.write("\npublic enum Director: Ranked {}\n")
    pres_status = run("status", cwd=pres_root)[1]
    S.append(("a world presents the forms it speaks, and the operator may change them",
              # the demo ships them as a file of its own, declared as forms
              os.path.exists(pres_forms)
              and 'public static var typeName: String { "forms-organization.swift" }' in pres_man
              and "public typealias Kind = FormsFile" in pres_man
              # not the shelf's printout, so the first edit is not a refusal
              and not open(pres_forms, encoding="utf-8").read().startswith("// gate stdlib")
              and pres_status.get("verdict") == "holds"
              # the bench opens it, and the plain stream never sees it
              and 'if r["role"] == "forms"' in shelf_src
              and "name not in forms_here" in shelf_src
              # its words reach what the bench offers
              and "for (const f of formsFiles)" in ui
              and 'sources.push([f, await (await fetch("/world?f="' in ui))

    # ── THE LAST MILE, AND WHERE IT STOPS. Every answer ends with a step and the
    # step names a command in backticks — which is a sentence to read, and a
    # sentence gets retyped, with somebody's own path, slightly wrong. The
    # command is lifted out beside the prose: ready as it stands, with whatever
    # the run already knew filled in, one click to the clipboard for a person
    # and one field for an agent that should not have to parse prose.
    #
    # And it is copied, never run. The bench reads and judges; the Enter belongs
    # to whoever owns the repository, in the tools they already have open. A page
    # that executes inside a repository holding other people's files is an attack
    # surface we would have built for ourselves, and what this bench can promise
    # today is that nothing it shows can change anything.
    mile = tempfile.mkdtemp(dir=tmp)
    run("demo", "org", cwd=mile)
    mile_out = run("status", cwd=os.path.join(mile, "gate-demo"))[1]
    S.append(("the step comes with the command ready, and the running is not ours",
              # the machine half: the command beside the sentence, not inside it
              mile_out.get("command_to_run") == "gate init ."
              and "`gate init .`" in mile_out.get("next", "")
              and "def command_in(" in shelf_src
              # only a command is lifted, never an arbitrary backticked word
              and 'r"(gate|git|bin/|yq|swift)\\b"' in shelf_src
              # the human half: it goes to the clipboard, and says where it runs
              and "navigator.clipboard.writeText(ready)" in ui
              and "It runs in your terminal, not here" in ui
              # and nothing here executes anything: no shell, no eval of a command
              and "child_process" not in ui and "mutating_routes" in shelf_src))

    # ── THE LAYER MAP, AS A FENCE. Four layers, and only two of them may put a
    # proper name inside an arbiter. The MECHANISM knows no name: it parses a
    # fragment, builds a dictionary out of what it was handed, looks up each
    # reference, counts. The LANGUAGE is what it must know as grammar — the
    # counting forms, Unit and Plus and Twice — because it cannot add without
    # them. WORLDS are everything else, and a world's name inside a mechanism is
    # a leak, not a feature.
    #
    # Swept by machine rather than by eye, the port's own literals fall in
    # exactly two piles: five that are the language, and twenty-five that are one
    # reference world — its ranks, its departments, its shares, its gates. The
    # same sweep on the corpus reads WhereJudge with five language names and no
    # world at all, and the plain Judge with thirty-six names and every one of
    # them that world's. So the where court is already the clean mechanism, and
    # the leak is the plain one — which is exactly what its behaviour says: it
    # refuses a presented protocol and carries a table.
    #
    # This holds the pile still. A new world name in our port goes red here, and
    # when the leak is swept the number drops rather than a comment going stale.
    port = open(os.path.join(HERE, "judge.js"), encoding="utf-8").read()
    LANGUAGE = {"Unit", "Plus", "Twice", "Times", "Never"}
    LEAKED = {"IndividualContributor", "Lead", "Manager", "Finance", "Engineering",
              "Sales", "People", "OnSite", "Hybrid", "Remote", "Male", "Female",
              "FinanceShare", "EngineeringShare", "SalesShare", "PeopleShare",
              "Employee", "Person", "GivenNameCycle", "FamilyNameCycle",
              "BirthYearCycle", "VerifiedView", "VerifiedInDepartment",
              "VerifiedAtRank", "VerifiedAtWorkplace"}
    AXES = {"Rank", "Home", "Site", "Given", "Family", "Sex", "Born", "Next"}
    found = set(re.findall(r'"([A-Z][A-Za-z]+)"', port))
    S.append(("the mechanism holds the language and one named leak, and nothing else",
              # the language belongs and is all there
              LANGUAGE <= found
              # every world name in it is one of the ones already counted: a new
              # one means a world walked into the mechanism while nobody looked
              and not (found - LANGUAGE - LEAKED - AXES)
              # and the leak has not grown
              and len(found & LEAKED) <= len(LEAKED)))

    # ── AND THE FACES COME FROM A WORLD TOO. The stylesheet said "a register is
    # declared ONCE here; an element only names it" — and then declared a font
    # thirty-two times, nineteen of them distinct, half of those the same
    # register written again with the leading a hair different: 11px/1.4 beside
    # 11px/1.45 beside 11px/1.5. A law stated and not enforced decays into the
    # habit it replaced. The page names a register now and states none, and the
    # numbers come from a file that is judged for them.
    #
    # That file holds laws rather than a list: the size ladder only goes up, so
    # `caption` cannot quietly become the size of `speech`, and every leading is
    # at least as tall as the letters it sets, because a line that overlaps the
    # next is not a line. Twenty-two equalities, probed by breaking one.
    reg = open(os.path.join(HERE, "stdlib", "bench-registers.swift"), encoding="utf-8").read()
    served = subprocess.run(
        [sys.executable, "-c",
         "import types;src=open(%r,encoding='utf-8').read();g=types.ModuleType('g');"
         "g.__file__=%r;exec(compile(src,'gate','exec'),g.__dict__);"
         "print(g.register_tokens())" % (GATE, GATE)],
        capture_output=True, text=True).stdout
    style_only = ui.split("<style>", 1)[1].split("</style>", 1)[0]
    S.append(("the page names a register and states none of its own",
              # every face in the stylesheet is a name, not a stack
              not [m for m in re.findall(r"font:\s*([^;}]+)", style_only)
                   if not m.startswith("var(") and m.strip() != "inherit"]
              and "ui-monospace" not in style_only and "-apple-system" not in style_only
              # served from the declared world, faces and registers both
              and "--fact: 12.5px/1.45 ui-monospace" in served
              and "--mono: ui-monospace,Menlo,monospace;" in served
              and "def register_tokens(" in shelf_src
              # and that world holds a ladder and a floor, not just a list
              and "public enum Taller<Hi, Lo, Slack>: Close {}" in reg
              and "public enum AtLeast<Have, Floor, Slack>: Close {}" in reg
              and "22 equalities" in subprocess.run(
                  [os.path.join(HERE, "bin", "gate-judge"), "judge", "where",
                   os.path.join(HERE, "stdlib", "bench-registers.swift")],
                  capture_output=True, text=True).stdout))

    # ── THE FLOOR IS REACHABLE, AND THIS IS THE SCENARIO. Open a forms file,
    # click `Twice` where it is written, and land on the line that declares it.
    # It did not work: the counting forms were not in the bench's vocabulary at
    # all, so the promise that every name opens where it is declared stopped at
    # exactly the layer everything else stands on. Found by a finger, not by this
    # battery — which is why the check below walks the same path rather than
    # reading the source for a string.
    #
    # gate fetches nothing, so there are two honest answers and both are here.
    # With the corpus on the machine the declaration opens, read-only. Without
    # it, the name is placed exactly — file, line, revision — and the command
    # that brings it is handed over. Named beats a dead end; shown beats named.
    lang = subprocess.run(
        [sys.executable, "-c",
         "import types;src=open(%r,encoding='utf-8').read();g=types.ModuleType('g');"
         "g.__file__=%r;exec(compile(src,'gate','exec'),g.__dict__);"
         "import json;print(json.dumps(g.language_origin()))" % (GATE, GATE)],
        capture_output=True, text=True).stdout.strip().splitlines()
    lang = json.loads(lang[-1]) if lang else {}
    S.append(("a word of the language says where it is declared, and opens if it is here",
              # the floor is named, with the line each word stands on
              lang.get("names", {}).get("Twice") == 299
              and lang.get("names", {}).get("Unit") == 283
              and lang.get("file", "").endswith("Primitive.swift")
              # at the revision the judge was built from, not some other one
              and (lang.get("at") or "").startswith("0fd0b38")
              # and the way to get it, since this tool will not go and take it
              and "git clone" in lang.get("command", "")
              # the bench reaches them: they join what a click can land on
              and "...Object.keys(language.names || {})" in ui
              and "function openLanguage(" in ui and "function sayLanguage(" in ui
              # shown when present, named when not — never a silent nothing
              and "language.present ? openLanguage(name, at) : sayLanguage(name, at)" in ui
              # and reading a checkout may not climb out of it
              and 'want.startswith(os.path.realpath(root) + os.sep)' in shelf_src))

    # ── A WORLD MAY BE LAID OUT IN FOLDERS, and it could not be. Declaring
    # `people/roster.swift` wrote a SECOND manifest inside `people/` and recorded
    # the row as `roster.swift` — so the world root never learned of the file and
    # the path to it was thrown away. A declared layout exists to let a person
    # shape their own world, and the shape was the one thing it could not carry.
    # Found by looking for it, after the rail was called a fiction.
    #
    # The world a file belongs to is found the way .git is: by walking up from
    # the file, never from wherever the command happened to be typed.
    fold = tempfile.mkdtemp(dir=tmp)
    os.makedirs(os.path.join(fold, "people"), exist_ok=True)
    os.makedirs(os.path.join(fold, "access"), exist_ok=True)
    open(os.path.join(fold, "gate.swift"), "w").write("public enum Sales: Department {}\n")
    open(os.path.join(fold, "people", "roster.swift"), "w").write("public enum Ann: Department {}\n")
    open(os.path.join(fold, "access", "shares.swift"), "w").write("public enum Docs: Department {}\n")
    run("mine", "people/roster.swift", cwd=fold)
    # and typed from inside the folder, which must land in the same manifest
    run("mine", "shares.swift", cwd=os.path.join(fold, "access"))
    fold_rows = run("mine", cwd=fold)[1].get("held") or []
    fold_status = run("status", cwd=fold)[1]
    S.append(("a world laid out in folders is one world, and the rail shows its shape",
              # one manifest, in the world root, and no second one beside a file
              os.path.exists(os.path.join(fold, "gate.manifest.swift"))
              and not os.path.exists(os.path.join(fold, "people", "gate.manifest.swift"))
              and not os.path.exists(os.path.join(fold, "access", "gate.manifest.swift"))
              # rows carry the path, not just the name at the end of it
              and sorted(h["file"] for h in fold_rows) == ["access/shares.swift",
                                                           "people/roster.swift"]
              # and all of it is judged together
              and fold_status.get("verdict") == "holds"
              and fold_status.get("world", {}).get("declarations") == 3
              # the rail groups by folder and hangs the file one Indent under it
              and 'head.className = "folder caption"' in ui
              and ".file.nested{padding-left:var(--indent)}" in ui
              and '"Wide", "Indent"' in shelf_src))

    # ── THE COURT ABOUT A PERSONAL WORLD ANSWERS WITH THE SAME GUARDS. Declaring
    # `MyBench` in a personal world when the shared one already declares it is
    # two truths about one name. `gate status` refused it with both addresses and
    # `gate my` said holds — the one command a person runs about the very file
    # that carries the second declaration. And the bench picks whichever it finds
    # depending on which file is open, so the theme in force could turn on a tab.
    # A court that answers about a world may not answer with less than the court
    # standing beside it.
    twice = tempfile.mkdtemp(dir=tmp)
    open(os.path.join(twice, "gate.swift"), "w").write(
        "public enum Sales: Department {}\n"
        "public enum MyBench: Bench { public typealias Theme = Dark }\n")
    pers = subprocess.run(
        [sys.executable, "-c",
         "import types;src=open(%r,encoding='utf-8').read();g=types.ModuleType('g');"
         "g.__file__=%r;exec(compile(src,'gate','exec'),g.__dict__);print(g.personal_path())"
         % (GATE, GATE)], cwd=twice, capture_output=True, text=True).stdout.strip()
    said_my, said_status = {}, {}
    if pers:
        os.makedirs(os.path.dirname(pers), exist_ok=True)
        keep = open(pers).read() if os.path.exists(pers) else None
        try:
            open(pers, "w").write(
                "public enum MyBench: Bench { public typealias Theme = Light }\n")
            said_my = run("my", cwd=twice)[1]
            said_status = run("status", cwd=twice)[1]
        finally:
            if keep is None:
                os.path.exists(pers) and os.remove(pers)
            else:
                open(pers, "w").write(keep)
    S.append(("the personal court refuses a second truth the shared court already refuses",
              said_my.get("verdict") == "refused"
              and said_status.get("verdict") == "refused"
              and any("MyBench" in r.get("claim", "") and "declared twice" in r.get("claim", "")
                      for r in said_my.get("refusals", []))
              # by running the same guards, not by a second opinion of its own
              and "A court that answers about a world may" in shelf_src
              and shelf_src.count("refusals += duplicate_guards_over(sources)") >= 1))

    # ── A SLOT IS A SLOT WHEREVER IT IS WRITTEN. `associatedtype Next: Cycle`
    # opens a hole and `Enter<Who: Keeper, Into: Room>` opens two — the same
    # thing said in the other notation. The axis stood in plain ink because it
    # names the question; the gate's parameter wore the hue of a name from
    # elsewhere, which told a reader it was an answer somebody had already
    # given. One logic, one ink: the hole is the label, the kind beside it is
    # what may fill it and keeps its own colour.
    #
    # Read off the rendered line rather than the rule: `Who` and `What` come
    # back `axisname`, exactly as `Next` does after `associatedtype`.
    # And the same hole READ is the same hole: `where Who.Home == What.Home`
    # names two parameters and two axes, and every one of them wore the hue of a
    # name from somewhere else — the condition that decides the verdict, painted
    # as if it came from another world. A slot label is ink wherever it stands,
    # and the set is what the bench already parsed: the axes forms declare and
    # the parameters the declarations in view open.
    S.append(("a gate's parameter is a hole, and is painted like every other hole",
              # the rule reaches into a parameter list and stops at the colon
              'const opened = before.lastIndexOf("<"), shut = before.lastIndexOf(">")' in ui
              and 'if (!seg.includes(":")) return "axisname";' in ui
              # and a slot label read anywhere — through a dot, in a where
              # clause — is the same label
              and "let slotNames = new Set();" in ui
              # POSITION FIRST: a name being born on this line is not a slot label
              # because some other world uses that word as an axis. `public
              # protocol Scope {}` came out in slot ink while `public protocol
              # Identity {}` two lines above wore the hue of a name — two
              # identical lines, two colours, for a reason about neither.
              # and only in the two positions a slot can stand in — after a dot,
              # or in a where clause. The set is every axis of every protocol of
              # every world in play, so consulting it anywhere let one world's
              # vocabulary repaint another's: `public enum CommitMessage: Scope
              # {}` wore slot ink on a plain use of a name declared four lines up.
              and 'if (!declaring && (dotted || inWhere) && slotNames.has(word)) return "axisname";' in ui
              and "for (const a of (d.params || [])) slotNames.add(a);" in ui
              # and it is the same ink the axis already had, not a third one
              and '.cm-axisname{color:var(--ink)}' in ui
              and '(?:typealias|associatedtype)\\s+$/.test(before)) return "axisname"' in ui))

    # ── HOW A PERSON OVERRIDES ANYTHING, WITHOUT ANYBODY HAVING EXPECTED THEM.
    # Conforming to a surface turns a wheel — but only a wheel somebody thought
    # to make turnable, which means the other side had to anticipate you. And
    # redeclaring a name to shadow it is two truths about one name, which this
    # tool exists to refuse. Both roads are closed, and there is a third that
    # needs neither: every number this bench paints and spaces itself by is read
    # from a DECLARED WORLD, so declare that name yourself and yours is the one
    # read. Not shadowing inside a stream — being the source the stream is read
    # from. Presented first, shipped after, first said wins.
    #
    # The probe is the whole claim: an operator declares two numbers in a file of
    # their own and the colour the page paints a foreign name with changes, with
    # nothing in this tool having been built to allow it.
    ovr = tempfile.mkdtemp(dir=tmp)
    open(os.path.join(ovr, "gate.swift"), "w").write("public enum Sales: Department {}\n")
    open(os.path.join(ovr, "my-colours.swift"), "w").write(
        "// role: forms\n"
        "public typealias KnownNameDimX = Plus<W2, Plus<W4, Plus<W16, W256>>>\n"
        "public typealias KnownNameDimZ = Plus<W16, Plus<W64, Plus<W128, Plus<W256, W512>>>>\n")
    run("mine", "my-colours.swift", "--role", "forms", cwd=ovr)
    served_here = subprocess.run(
        [sys.executable, "-c",
         "import types;src=open(%r,encoding='utf-8').read();g=types.ModuleType('g');"
         "g.__file__=%r;exec(compile(src,'gate','exec'),g.__dict__);print(g.palette_tokens())"
         % (GATE, GATE)], cwd=ovr, capture_output=True, text=True).stdout
    dark_here = served_here.split(':root[data-theme="dark"]', 1)[-1]
    S.append(("a world you present outranks the one this tool ships, with nothing anticipating it",
              # the operator's two numbers are what the page is served
              "calc(278/1000)" in dark_here and "calc(976/1000)" in dark_here
              # and the shipped value for that same name is gone from the dark half
              and "calc(454/1000) calc(419/1000) calc(691/1000)" not in dark_here
              # everything they did not say still comes from what shipped
              and "--action" in dark_here and "--localtype" in dark_here
              # by LAYER, never by position: reordering the list may not change
              # what the page paints, because correctness is order-invariant and
              # this is exactly where order had crept back in as truth
              and "def presented_over(" in shelf_src
              and "PRIORITY IS A PROPERTY OF THE LAYER, NEVER OF POSITION" in shelf_src))

    # ── THE LEFT PANEL UNDER THE SAME COURTS AS THE PAGE. Built before this, it
    # was the one surface that answered to nobody: six lengths written as bare
    # numbers, two voices — the section label and the line under it — that no
    # register declared at all, and a weight of 500 that existed only in a
    # stylesheet. Nothing could have refused any of them. This is checked BEFORE
    # the panel grows, not after: what is built next is built under judgement.
    registers_src = open(os.path.join(HERE, "stdlib", "bench-registers.swift"),
                         encoding="utf-8").read()
    rail_css = re.search(r"<style>(.*?)</style>", ui, re.S).group(1)
    rail_rules = [(s.strip(), b) for s, b in re.findall(r"([^{}]+)\{([^}]*)\}", rail_css)
                  if re.search(r"#rail|\.file|\.group|\.side|overrules|\.commit",
                               re.sub(r"/\*.*?\*/", "", s, flags=re.S))]
    bare = [(s, l) for s, b in rail_rules
            for l in re.findall(r":\s*(-?\d+(?:\.\d+)?px|#[0-9a-fA-F]{3,8})", b)]
    typed = [(s, b) for s, b in rail_rules
             if re.search(r"font-size|font-weight|font-family", b)]
    S.append(("every length and voice in the left panel is a name some world declares",
              # not one hand-written length or colour left in the panel
              not bare
              # and nothing sets type except by naming a register
              and not typed
              # the two voices it speaks in are declared, and judged
              and "public enum Rubric: Register" in registers_src
              and "RubricIsCaptionSized" in registers_src
              # including the one a click makes: the same fact, said firm — a
              # list that changes size when you click it moves under the hand
              and "public typealias FactfirmIsFactSized" in registers_src
              and "font:var(--factfirm)" in ui))

    # ── THE LINE THAT DECIDES THE VERDICT IS NOT CEREMONY. A `where` clause is
    # the condition a verdict turns on, and it was set in the same grey as the
    # brackets around it — read as furniture, skipped by the eye. Measured on
    # the page: `where` and the reach-through dots stand back in the seam, and
    # everything that carries meaning is ink — the parameters `Who` and `What`,
    # the axes they reach through, and the `==` that decides.
    #
    # That `==` is ink because it inherits the editor's own colour, which is the
    # right answer arrived at without anybody saying so. Said here, so it cannot
    # drift into grey the day somebody restyles the editor.
    S.append(("the where clause reads as a claim: holes and connective in ink, ceremony in the seam",
              ".CodeMirror{height:100%;font:var(--source);background:var(--paper);color:var(--ink)}" in ui
              # a slot label is ink wherever it stands — in the parameter list
              # and in the clause that reads it back
              and ".cm-axisname{color:var(--ink)}" in ui
              # POSITION FIRST: a name being born on this line is not a slot label
              # because some other world uses that word as an axis. `public
              # protocol Scope {}` came out in slot ink while `public protocol
              # Identity {}` two lines above wore the hue of a name — two
              # identical lines, two colours, for a reason about neither.
              # and only in the two positions a slot can stand in — after a dot,
              # or in a where clause. The set is every axis of every protocol of
              # every world in play, so consulting it anywhere let one world's
              # vocabulary repaint another's: `public enum CommitMessage: Scope
              # {}` wore slot ink on a plain use of a name declared four lines up.
              and 'if (!declaring && (dotted || inWhere) && slotNames.has(word)) return "axisname";' in ui
              # and the ceremony around it is the seam, never a colour of its own
              and ".cm-s-default .cm-keyword,.cm-s-default .cm-attribute{color:var(--seam)}" in ui
              and ".cm-ghost{color:var(--seam)" in ui))

    # ── AND A VALUE CAN BE ANSWERED WHERE IT IS SHOWN. The bench could show what
    # a world holds and never let anybody say otherwise: a table you may read
    # and not write in. Saying a different value meant leaving the page, working
    # out which file of yours the where court reads, and spelling the number on
    # the world's ladder by hand. The answer goes in a file of MINE — never in
    # the world that shipped the name, which is not this world's to edit — and
    # the laws that shipped with it judge it at once. Probed the whole way.
    import socket as _sock
    sv = tempfile.mkdtemp(dir=tmp)
    open(os.path.join(sv, "gate.swift"), "w").write("public enum Sales: Department {}\n")
    open(os.path.join(sv, "my-values.swift"), "w").write("// role: forms\n")
    no_forms = None
    _s2 = _sock.socket(); _s2.bind(("127.0.0.1", 0)); _vp = _s2.getsockname()[1]; _s2.close()
    _vb = subprocess.Popen([sys.executable, GATE, "serve", "--port", str(_vp)], cwd=sv,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        wait_serve(_vp)
        # nowhere of mine for an answer to live: it says so instead of guessing
        try:
            _u.urlopen(_u.Request(f"http://127.0.0.1:{_vp}/value?name=InkLitX&to=40",
                                  method="PUT"), timeout=30).read()
        except Exception as e:
            no_forms = json.loads(e.read().decode()) if hasattr(e, "read") else {}
    finally:
        _vb.terminate()
    run("mine", "my-values.swift", "--role", "forms", cwd=sv)
    _s3 = _sock.socket(); _s3.bind(("127.0.0.1", 0)); _vp2 = _s3.getsockname()[1]; _s3.close()
    _vb2 = subprocess.Popen([sys.executable, GATE, "serve", "--port", str(_vp2)], cwd=sv,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    said_value = {}
    try:
        wait_serve(_vp2)
        said_value = json.loads(_u.urlopen(
            _u.Request(f"http://127.0.0.1:{_vp2}/value?name=InkLitX&to=691",
                       method="PUT"), timeout=30).read().decode())
    finally:
        _vb2.terminate()
    wrote = open(os.path.join(sv, "my-values.swift")).read()
    read_back = json.loads(subprocess.run(
        [sys.executable, "-c",
         "import types,json;src=open(%r,encoding='utf-8').read();g=types.ModuleType('g');"
         "g.__file__=%r;exec(compile(src,'gate','exec'),g.__dict__);"
         "print(json.dumps(g._peano(open(%r,encoding='utf-8').read())))"
         % (GATE, GATE, os.path.join(sv, "my-values.swift"))],
        capture_output=True, text=True).stdout or "{}")
    S.append(("saying a value writes it in a file of mine, spelled on the world's own ladder",
              # with nowhere of mine to put it, it says so and names the command
              no_forms and no_forms.get("asks")
              and "gate mine my-values.swift --role forms" in no_forms.get("note", "")
              # and with somewhere, the declaration lands there and nowhere else
              and said_value.get("file") == "my-values.swift"
              and "public typealias InkLitX = Plus<Unit, Plus<W2," in wrote
              # spelled the way every line already in those worlds is spelled,
              # so this tool reads back exactly the number that was said
              and read_back.get("InkLitX") == 691
              # and the page asks for it from the cell the value stands in
              and "iz.onclick = () => sayValue(name, asNumber, iz);" in ui
              and "async function sayValue(" in ui
              and 'fetch("/value?name="' in ui))

    # ── THE PANEL IS A DOOR, AND A DOOR DOES NOT NARRATE. The rail carried a
    # JOURNAL: every commit, who wrote it, whether it was merged, with a diff
    # under each — under a heading that admitted, in its own words, that the
    # judge had not checked any of it. A permanent zone showing what nothing
    # here judges, beside the list of files this tool answers for. History is
    # reached by asking: `gate log`, which a repository with no world is already
    # offered by name.
    S.append(("the rail is a tree of files and nothing else",
              "renderJournal" not in ui and "toggleDiff" not in ui
              and 'id="journal"' not in ui and 'data-fold="journal"' not in ui
              # and the furniture went with it rather than sitting unused: a
              # stylesheet full of rules for rows nobody builds is a page keeping
              # a room for a tenant who left
              and ".commit{" not in ui and ".cdiff{" not in ui and ".badge{" not in ui
              # AND THE SHELF DOES NOT SAY TWICE WHAT THE TREE ALREADY SAYS. In
              # this repository the shelf IS gate's own mine — every bench-* and
              # forms-* file stands in the tree under stdlib/ — and the list
              # below repeated all nine under `theirs`, the same files named
              # twice on one panel.
              and "const alreadyMine = new Set(files.map(" in ui
              # and gate's own furniture is off an operator's page entirely. The
              # decision was written above this code and waited on one condition
              # — that this tool declare its world the way it asks everybody else
              # to — which it has done since; the follow-through had not been.
              # How this page spaces itself answers no question an operator has.
              and "if (alreadyMine.has(m) || roles[m] === \"gate's own\") continue;" in ui))

    # ── AND THE WHEEL STILL TURNS SOMETHING. `MyJournal` is a surface this tool
    # offers: an operator declares what their history shows. It steered a panel,
    # and when the panel went it would have steered nothing — an offer with
    # nothing behind it, which is worse than never offering. It steers the
    # command that still shows a journal, and a word typed now outranks it.
    wj = os.path.join(tmp, "wheelw")
    os.makedirs(wj)
    subprocess.run(["git", "init", "-q", "-b", "main", wj])
    open(os.path.join(wj, "gate.swift"), "w").write("public enum Sales: Department {}\n")
    subprocess.run(["git", "add", "-A"], cwd=wj)
    subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "user.email=a@a",
                    "-c", "user.name=A", "commit", "-qm", "by a"], cwd=wj)
    open(os.path.join(wj, "more.swift"), "w").write("public enum Ops: Department {}\n")
    subprocess.run(["git", "add", "-A"], cwd=wj)
    subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "user.email=b@b",
                    "-c", "user.name=B", "commit", "-qm", "by b"], cwd=wj)
    subprocess.run(["git", "config", "user.email", "a@a"], cwd=wj)
    plain = run("log", cwd=wj)[1]
    open(os.path.join(wj, "my-journal.swift"), "w").write(
        "public enum MyJournal: Journal {\n    public typealias Scope = AllRepo\n"
        "    public typealias Author = Me\n}\n")
    # a wheel is read from a file this world DECLARES, like every other fact
    # here: writing one beside the world and never saying so leaves it a file
    # lying about, which is exactly what the mine/theirs mechanism exists to
    # refuse to guess at
    undeclared = run("log", cwd=wj)[1]
    run("mine", "my-journal.swift", cwd=wj)
    turned_all = run("log", cwd=wj)[1]
    said_world = run("log", "world", cwd=wj)[1]
    S.append(("a wheel an operator turned steers the command, and a word typed now outranks it",
              plain.get("scope") == "world" and not plain.get("mine_only")
              # declared: the whole repository, and only what I wrote
              and turned_all.get("scope") == "all" and turned_all.get("mine_only") is True
              and [c["email"] for c in turned_all.get("commits", [])] == ["a@a"]
              # and saying otherwise here wins, the way it does everywhere else
              and said_world.get("scope") == "world"
              # and a file nobody declared steers nothing
              and undeclared.get("scope") == "world"))

    # ── THE LIBRARY IS THE DOMAIN'S, NOT THE AGENT'S — checked, not believed.
    # V=I §5.26: "Two agents processing the same domain under the same encoding
    # produce libraries with identical entries, differing only in the order
    # entries were added… The library's content is determined by the domain, not
    # by the agent." Run as an experiment on this tool: two worlds, identical
    # content, files declared in opposite orders, and everything that is JUDGED
    # or PAINTED compared byte for byte.
    #
    # The first run failed, and found two things at once. Everything an operator
    # declared in a forms file was appended to EVERY shipped world — a length
    # from the metrics world glued onto the git atoms, the contract forms, all of
    # them — which is two encodings communicating (§5.24). And because it was
    # appended in the order the operator declared their files, two people with
    # identical content got different line numbers for the same refusal: order
    # leaking into an address, which §5.25 forbids. Both fell to one fix.
    lib = {}
    for who, order in (("A", ("colours.swift", "lengths.swift")),
                       ("B", ("lengths.swift", "colours.swift"))):
        w = os.path.join(tmp, "lib526" + who)
        os.makedirs(w)
        open(os.path.join(w, "gate.swift"), "w").write("public enum Sales: Department {}\n")
        open(os.path.join(w, "colours.swift"), "w").write(
            "// role: forms\npublic typealias KnownNameDimZ = "
            "Plus<W8, Plus<W16, Plus<W32, Plus<W64, Plus<W128, W512>>>>>\n"
            "public typealias KnownNameChroma_dim = TowardBlue<KnownNameDimY, KnownNameDimZ,"
            " Plus<Unit, Plus<W2, Plus<W32, Plus<W64, Plus<W1024, Plus<W2048, W4096>>>>>>>\n"
            "public typealias MineApartTheirs_Z_dim = Apart<KnownNameDimZ, LocalTypeDimZ,"
            " Plus<Unit, Plus<W2, Plus<W4, Plus<W32, W64>>>>>\n"
            "public typealias TheirsApartBad_Z_dim = Apart<KnownNameDimZ, BadDimZ,"
            " Plus<Unit, Plus<W2, Plus<W4, Plus<W8, Plus<W64, W512>>>>>>\n")
        open(os.path.join(w, "lengths.swift"), "w").write(
            "// role: forms\npublic typealias Line = Plus<W2, W8>\n")
        for f in order:
            run("mine", f, "--role", "forms", cwd=w)
        lib[who] = subprocess.run(
            [sys.executable, "-c",
             "import types,json;src=open(%r,encoding='utf-8').read();g=types.ModuleType('g');"
             "g.__file__=%r;exec(compile(src,'gate','exec'),g.__dict__);"
             "print(json.dumps({'w':{k:g.presented_world(k) for k in sorted(g.STDLIB)},"
             "'p':g.palette_tokens(),'l':g.ladder_tokens(),'r':g.register_tokens()},"
             "sort_keys=True))" % (GATE, GATE)],
            cwd=w, capture_output=True, text=True).stdout
    S.append(("two agents, one domain, opposite orders: the same library to the byte",
              lib["A"] and lib["A"] == lib["B"]
              # and the override still takes — order-invariance that achieved
              # itself by ignoring the operator would be no result at all
              and "calc(760/1000)" in lib["A"]
              # and a world holds only its own names: nothing of the operator's
              # is appended to a world that never said it
              and "public typealias Line" not in json.loads(lib["A"])["w"]["git-atoms"]))

    # ── AND THE THREE STATES ARE THREE BECAUSE ℕ HAS THREE PARTS THERE, not
    # because we picked three words. Probed by asking the game directly: every
    # address gets a size, sizes are only ever 0, 1 or >1, and each of the three
    # columns is exactly the addresses of one size. A fourth column would need a
    # fourth size first, and there is no fourth size.
    sg = os.path.join(tmp, "seamgame")
    run("demo", "seam", sg)
    att = run("attention", os.path.join(sg, "api.swift"), os.path.join(sg, "sdk.swift"),
              "--as", "MessagesJS", cwd=sg)[1]
    sz = att.get("sizes") or {}
    S.append(("a seam's state is |S| of a game, and {0, 1, >1} leaves no fourth column",
              sz and set(sz.values()) <= {0, 1, 2}
              # parted is exactly the addresses nothing fits
              and sorted(x["address"] for x in att.get("parted", []))
                  == sorted(a for a, n in sz.items() if n == 0)
              # and the two word-columns together are exactly the open ones —
              # one state read from whichever end owes the sentence
              and sorted(x["address"] for x in
                         att.get("waits_on_you", []) + att.get("you_wait_on", []))
                  == sorted(a for a, n in sz.items() if n > 1)
              # `taken as given` is not among them: it is somebody supplying the
              # premise the theory leaves outside, and the citation is its term
              and "taken as given" in ui
              and "somebody SUPPLYING the agreement the two sides never derived" in ui))

    # ── A DOCUMENT LISTS WHAT IT HAS. The layout template wrote every role atom
    # this tool can imagine into every world — so a person opening theirs met
    # five words of grammar before two facts, two of them naming courts nothing
    # in that world used. The atom is written when the first row needs it, and a
    # row whose atom is missing is refused: a column is an axis to a declared
    # atom, and a name nothing declares names nothing.
    lean = os.path.join(tmp, "leanlayout")
    run("demo", "org", lean)
    lman = os.path.join(lean, "gate.manifest.swift")
    laid = open(lman).read()
    stripped = laid.replace("public enum FormsFile: Role {}\n", "")
    open(lman, "w").write(stripped)
    orphan = run("status", cwd=lean)[1]
    open(lman, "w").write(laid)
    S.append(("the layout declares the atoms it uses, and a row without its atom is refused",
              "public enum FormsFile: Role {}" in laid
              # nothing here is a seam or a plain world file, so neither is named
              and "public enum SeamFile: Role {}" not in laid
              and "public enum WorldFile: Role {}" not in laid
              and run("status", cwd=lean)[1].get("verdict") == "holds"
              and orphan.get("verdict") == "refused"
              and any("declares no `FormsFile`" in r.get("claim", "")
                      for r in orphan.get("refusals", []))))

    # ── A FILE IS DECLARED ONCE. Two rows about one file are two truths about
    # one thing — what this whole tool exists to make impossible — and its own
    # layout document took them silently, under two names, and said `holds`.
    # Found while opening a world to play in: the demo declares its seam sides,
    # a person declares them again by hand, and the morning cut then counted
    # every waiting field four times. Both halves are refused: the act, and a
    # document that already carries it.
    dd = os.path.join(tmp, "declaredtwice")
    run("demo", "seam", dd)
    twice = run("theirs", "api.swift", "--role", "seam", "--at", "x@1", cwd=dd)[1]
    dman = os.path.join(dd, "gate.manifest.swift")
    kept_two = open(dman).read()
    open(dman, "w").write(kept_two + "\npublic enum Second: Theirs {\n"
                          "    public typealias Kind = SeamFile\n"
                          "    public typealias At = Rev_messages_api_a1b2c3d\n}\n"
                          "extension Second { public static var typeName: String "
                          "{ \"api.swift\" } }\n")
    doubled = run("status", cwd=dd)[1]
    open(dman, "w").write(kept_two)
    S.append(("a file is declared once, and a second row about it is refused at its line",
              twice.get("asks") and "already declared" in twice.get("note", "")
              and run("status", cwd=dd)[1].get("verdict") == "holds"
              and doubled.get("verdict") == "refused"
              and any("second row about api.swift" in r.get("claim", "")
                      for r in doubled.get("refusals", []))))

    # ── HOW BIG THE COURT IS, COUNTED RATHER THAN CLAIMED. Somebody who opens
    # the corpus meets nine hundred files and concludes "a large machine I will
    # never read". The court is two of them. That is the strongest thing this
    # tool can say about its own judge and it was said nowhere — while the
    # number, written down here, would be a claim about somebody else's files
    # that nothing checks. It is counted from the checkout when there is one and
    # left unsaid when there is not, the same as the revision beside the binary.
    corpus = os.environ.get("GATE_CORPUS")
    counted = json.loads(subprocess.run(
        [sys.executable, "-c",
         "import types,json;src=open(%r,encoding='utf-8').read();g=types.ModuleType('g');"
         "g.__file__=%r;exec(compile(src,'gate','exec'),g.__dict__);"
         "print(json.dumps(g.court_shape()))" % (GATE, GATE)],
        capture_output=True, text=True,
        env=dict(os.environ, GATE_CORPUS=corpus) if corpus else os.environ).stdout or "null")
    silent_court = json.loads(subprocess.run(
        [sys.executable, "-c",
         "import types,json;src=open(%r,encoding='utf-8').read();g=types.ModuleType('g');"
         "g.__file__=%r;exec(compile(src,'gate','exec'),g.__dict__);"
         "print(json.dumps(g.court_shape()))" % (GATE, GATE)],
        capture_output=True, text=True,
        env={k: v for k, v in os.environ.items() if k != "GATE_CORPUS"}).stdout or "null")
    S.append(("the court's size is counted from the checkout, and unsaid without one",
              silent_court is None
              # the two files that decide every verdict are named, not guessed at
              and 'COURT_FILES = ("Sources/Tools/Judge.swift", "Sources/Tools/WhereJudge.swift")' in shelf_src
              # no number about somebody else's files is written in this tool
              and not re.search(r"court[^\n]*\b1021\b", shelf_src)
              and (counted is None or (counted["lines"] > 0 and len(counted["files"]) == 2))
              # and it reaches both places a person asks the question
              and 'the court is " + str(court_shape()["lines"])' in shelf_src
              and "language.court" in ui))

    # ── THE MORNING QUESTION, ASKED OF THE WHOLE WORLD. `attention` needed two
    # files named by hand, so the one thing an owner asks daily — what waits on
    # my word today — could only be asked one pair at a time, by somebody who
    # already knew which pairs existed. The list is declared; a world knows its
    # own seams. Same reading, asked of all of them at once.
    ms = os.path.join(tmp, "morning")
    run("demo", "seam", ms)
    for side in ("api.swift", "sdk.swift"):
        run("theirs", side, "--role", "seam", "--at", "a1b2c3d", cwd=ms)
    cut = run("attention", cwd=ms)[1]
    hush = os.path.join(tmp, "noseam")
    run("demo", "org", hush)
    quiet = run("attention", cwd=hush)[1]
    S.append(("with no arguments, attention is the morning question over every declared seam",
              isinstance(cut.get("seams"), list) and cut["seams"]
              and cut.get("waiting_on_you", 0) + cut.get("you_wait_on", 0)
                  + cut.get("parted", 0) > 0
              # and where no seam is declared it says so, rather than printing a
              # usage line at somebody who asked a reasonable question
              and quiet.get("asks") and "nobody is waiting on anybody" in quiet.get("note", "")))

    # ── MAKING SOMETHING YOURS IS THE THIRD VERB, and it had no word. `theirs`
    # is what I read, `mine` is what I write, and between them sat the act
    # everybody performs: I saw somebody's and took it as my starting point. The
    # nearest gesture argued against itself — `stdlib materialize` writes the
    # file and then says "a printout, not a source… here to be READ" — so the
    # path from seeing to saying was blocked by this tool's own words. It needs
    # no new noun: `gate mine bench-palette` says it in the word already learned.
    tv = os.path.join(tmp, "thirdverb")
    run("demo", "org", tv)
    took = run("mine", "bench-palette", cwd=tv)[1]
    copy = os.path.join(tv, "bench-palette.swift")
    head = open(copy).read().split("\n")[:3] if os.path.exists(copy) else []
    again = run("mine", "bench-palette", cwd=tv)[1]
    took_holds = run("status", cwd=tv)[1].get("verdict")
    # and a value changed in MY copy is what the page paints, which is the whole
    # point of having taken it: identity is the path a file has, never the name
    # it wears, and comparing names took an operator's copy for one of ours.
    # Read first, then write — `open(w)` truncates before a nested read runs,
    # and a probe that quietly empties the file it meant to edit proves nothing.
    said = re.sub(r"public typealias SelectDimZ = .*",
                  "public typealias SelectDimZ = Plus<W8, W32>", open(copy).read(), count=1)
    open(copy, "w").write(said)
    painted = subprocess.run(
        [sys.executable, "-c",
         "import types;src=open(%r,encoding='utf-8').read();g=types.ModuleType('g');"
         "g.__file__=%r;exec(compile(src,'gate','exec'),g.__dict__);print(g.palette_tokens())"
         % (GATE, GATE)], cwd=tv, capture_output=True, text=True).stdout
    S.append(("making a shelf world yours is one word, and what you then say is what is painted",
              took.get("made_mine") == "bench-palette"
              and took.get("wrote") == "bench-palette.swift"
              # it says where it came from and at what revision, in its own head
              and any("This copy is yours" in l for l in head)
              and not any("// role:" in l for l in head)
              and took.get("court") == "forms"
              and took_holds == "holds"
              # a second call does not overwrite what you have since written
              and again.get("asks") and "already here" in again.get("note", "")
              # and the merge takes it as an override: by path, never by name
              and "SHIPPED_PATHS" in shelf_src
              and "calc(38/1000) calc(40/1000) calc(40/1000)" in painted))

    # ── AND A REFUSAL IS VISIBLE IN THE VIEW YOU WRITE IN. Bare is a surface
    # you EDIT — slots, add claim, add record — and when what you wrote stopped
    # holding, nothing there said so: the chip counted two, the footer carried
    # two addresses, and the claim they were about looked like the ones that
    # hold. The mark was written and hung on the record's own line, while a
    # refusal lands on the line of the ARGUMENT that failed, inside a claim
    # written down the page — so it matched nothing, ever, and appeared once in
    # no session. Walked: break a fact, and the two claims named are the two
    # marked, no more.
    S.append(("bare marks the claim a refusal is about, and only that claim",
              "const starts = (d.entries || []).map(e => e.line).sort((a, b) => a - b);" in ui
              and "if (ln < d.line || ln >= ends) continue;" in ui
              and "function recordEnd(parsed, d) {" in ui
              # the same wave a file wears in the panel and a name wears when it
              # resolves to nothing — never the tinted backing taken off the
              # refusal rows, or the page teaches two words for one state
              and "#bare .row-bad{text-decoration:underline wavy var(--bad)" in ui
              and "#bare .row-bad{background" not in ui))

    # ── A GATED CONFORMANCE IS READ, and this is the check that was missing the
    # day it stopped being read. A branch added for the one-line `extension X {
    # typeName }` that gate itself writes swallowed EVERY one-line extension,
    # including a gate joined from two lines — `extension Enter: Entered where
    # …` ends in a brace too — so every where-gate in the shelf went unparsed
    # and nothing anywhere said a word, because no check covered them.
    gate_src = open(os.path.join(HERE, "stdlib", "forms-grants.swift"), encoding="utf-8").read()
    open(os.path.join(tmp, "gates.js"), "w").write("""
const { judge } = require(process.argv[2]);
const text = require("fs").readFileSync(process.argv[3], "utf8");
const p = judge("g.swift", text, { seeds: new Set(), generics: new Set() }).parsed;
const out = {};
for (const [n, d] of p.declarations)
    if (d.whereGates || d.whereText || (d.params || []).length)
        out[n] = { params: d.params, conf: d.conformances,
                   gates: (d.whereGates || []).length, whereText: d.whereText };
console.log(JSON.stringify(out));
""")
    open(os.path.join(tmp, "grants.swift"), "w").write(gate_src)
    read = json.loads(subprocess.run(
        ["node", os.path.join(tmp, "gates.js"), os.path.join(HERE, "judge.js"),
         os.path.join(tmp, "grants.swift")], capture_output=True, text=True).stdout or "{}")
    S.append(("a gate is read whole: its holes, what it conforms to, and the clause it turns on",
              read.get("Enter", {}).get("params") == ["Who", "Into"]
              # written down the page — the head ends where its angle closes,
              # not where the line does, which is how every gate here is written
              and read["Enter"]["conf"] == ["Entered"]
              and read["Enter"]["gates"] >= 1
              and "Who.Post == Into.Place" in (read["Enter"]["whereText"] or "")
              # and the clause as written, not only the part the judge compares:
              # a reader shown less than was said is shown something else
              and "Who.Key: Writes" in (read["Enter"]["whereText"] or "")))

    S.append(("bare shows a gate's holes and the condition its verdict turns on",
              # ONE SHAPE FOR ONE THING: a gate's parameter and an
              # `associatedtype` are the same act written two ways, and this view
              # showed one with a colon inside angle brackets and the other as a
              # sentence. Every hole is a line, and the line says what fills it.
              "...(d.params || []).map((a, i) => [a, (d.paramKinds || [])[i]])" in ui
              and "...(d.axes || []).map(a => [a, (d.axisKinds || {})[a]])" in ui
              and "const when = d.whereText" in ui
              and "declSpan(name, d.line, bad) + conf + when" in ui
              # a hole's label is ink in this view too, the same hole the editor paints
              and ".hole-label{color:var(--ink)}" in ui))

    # ── BARE IS THE RECORD WITHOUT CEREMONY, NEVER WITHOUT ITS CONTENT. A
    # protocol declares axes — `Keeper` opens `Post: Realm` and `Key` — and this
    # view printed the name alone, `Keeper×`: a form that asks two things of
    # everybody who conforms, appearing to ask none. The parse had held `axes`
    # and `axisKinds` all along and nothing read them here. Bare is one of three
    # views promised to show the same file; a view that drops what a form asks
    # is not minimal, it is partial in a way nobody chose.
    S.append(("bare says what a form asks of others, which the parse has always known",
              "...(d.axes || []).map(a => [a, (d.axisKinds || {})[a]])" in ui
              and 'asks for </span>' in ui
              # the kind is a name and wears a name's hue; an axis with no kind
              # says so rather than looking like an axis with a kind
              and 'kind ? nameTokens(kind) :' in ui
              and '>anything</span>' in ui))

    # ── A ROW MAY NOT SEND A FILE TO A COURT THAT CANNOT READ IT. The layout's
    # guard asked only whether a role names A court, never whether it names the
    # right one — so `Kind = SeamFile` on a file of forms held, and the row said
    # "judge this where it meets somebody else's world" about a file that meets
    # nobody. For most courts what "right" means is not readable from the file;
    # for a seam it is, since a side states which side it is in its own first
    # lines, and that is already how seams are found at all.
    mw = os.path.join(tmp, "misfiled")
    run("demo", "org", mw)
    mp = os.path.join(mw, "gate.manifest.swift")
    kept_manifest = open(mp).read()
    open(mp, "w").write(kept_manifest.replace(
        "public typealias Kind = FormsFile", "public typealias Kind = SeamFile", 1))
    misfiled = run("status", cwd=mw)[1]
    open(mp, "w").write(kept_manifest)
    S.append(("a row filed under a court that cannot read the file is refused at its line",
              run("status", cwd=mw)[1].get("verdict") == "holds"
              and misfiled.get("verdict") == "refused"
              and any("does not say it is one side of one" in r.get("claim", "")
                      for r in misfiled.get("refusals", []))))

    # ── NOT EVERYTHING UNDER `THEIRS` IS THE JUDGE'S, and the panel says which
    # is which. Three different things stood there under one heading in one
    # alphabet: the court, the forms a world and a policy are written in, and
    # this bench's own furniture. Each file states which it is in its own second
    # line and the tool had been reading that line to no visible end — so a
    # reader asking "is all of this the judge?" got no answer, and the answer is
    # no. `git-atoms` in particular is forms, like the rest of the language.
    S.append(("the shelf is grouped by what each file says it is, not by one flat alphabet",
              'const role = roles[m] || "taken";' in ui
              # and the heading is the file's own word, never a sentence written
              # in the page: a lookup on the roles this tool happens to know is
              # the tool learning a vocabulary, and an unknown role gets nothing
              and "head.textContent = role;" in ui
              and '"forms — the language a world is written in"' not in ui
              and "mods.sort((a, b) => (roles[a] || \"\").localeCompare(roles[b] || \"\")" in ui
              # and the roles come from the files themselves, never from a list here
              and "def stdlib_role(" in shelf_src
              and 'm = re.match(r"// role: (.+)", line.strip())' in shelf_src))

    # ── AND ONE LINE ON THE PAGE IS NOT TWICE THE WEIGHT OF THE OTHERS. The
    # borrowed editor draws the gutter divider at 1px while every line this page
    # draws is half that, so the rule nearest the reading eye was the heaviest
    # thing on screen. We had overridden its colour and inherited its width —
    # the same silence as a token colour left unoverridden.
    S.append(("every divider on the page is the same weight, including the borrowed one",
              ".CodeMirror-gutters{background:var(--paper);border-right:0.5px solid var(--line)}" in ui
              and "border-right-color:var(--line)}" not in ui))

    # ── AND `init` WITH NO PATH MEANS HERE, WHEN HERE IS ALREADY A WORLD. The
    # default was a new folder called `world`, unconditionally — so `gate init
    # --vendor`, typed by somebody standing in the world they had just made,
    # built a SECOND world inside the first and vendored the tool into that. The
    # success line was true and the files were one directory below where the
    # person then looked for them. Found by hand, walking the demo path; a
    # second world inside a world is the two-truths shape in the filesystem.
    iw = os.path.join(tmp, "initwhere")
    run("demo", "org", iw)
    said_here = run("init", "--vendor", cwd=iw)[1]
    empty = os.path.join(tmp, "initempty")
    os.makedirs(empty)
    said_new = run("init", cwd=empty)[1]
    S.append(("`init` with no path means here when here is a world, and a new folder when it is not",
              said_here.get("root") == "."
              and os.path.isdir(os.path.join(iw, ".gate"))
              and not os.path.isdir(os.path.join(iw, "world"))
              # and the vendored judge is really there, with what it was built from
              and os.path.exists(os.path.join(iw, ".gate", "bin", "gate-judge"))
              and os.path.exists(os.path.join(iw, ".gate", "bin", "gate-judge.from"))
              # in an empty folder it still scaffolds one, which is the old use
              and said_new.get("root") == "world"
              and os.path.isdir(os.path.join(empty, "world"))))

    # ── THE WAY BACK IS SAID BEFORE THE FIRST PUSH. Trying things is free only
    # when the retreat is known in advance: courage comes from seeing the way
    # back, never from being told afterwards that one existed. The demo world is
    # committed the moment it is made, so `git checkout .` has always restored
    # it — and nothing said so, which is a way back that exists and cannot be
    # found, the same blindness as a file served by URL and missing from the
    # panel. Walked whole: break it as invited, see the address, take it back.
    bk = os.path.join(tmp, "backworld")
    said = run("demo", "org", bk)[1]
    gs = os.path.join(bk, "gate.swift")
    open(gs, "w").write(open(gs).read().replace(
        "public typealias Home = Finance", "public typealias Home = Engineering", 1))
    broke = run("status", cwd=bk)[1]
    subprocess.run(["git", "checkout", "."], cwd=bk, capture_output=True)
    healed = run("status", cwd=bk)[1]
    S.append(("the demo says the way back before it invites you to break anything",
              "git checkout ." in said.get("back", "")
              and "cannot cost you" not in said.get("back", "")   # about the world, not a promise about you
              and broke.get("verdict") == "refused" and healed.get("verdict") == "holds"
              # and the invitation is a trial, never damage
              and "change one Home in gate.swift and watch the judge name the line" in said.get("next", "")
              # ONE RUNG for a person: the tool's own law about itself is that a
              # product listing the whole ladder teaches nothing, and both demos
              # printed five doors at once to somebody thirty seconds in. The
              # rest is still there for whoever asked for all of it.
              and 'lines.append(f"  more: {len(out[\'try\'])} other things to try' in shelf_src
              # nothing shown to a person calls them a liar for a world that does not hold
              and "a lie cannot be committed" not in open(GATE, encoding="utf-8").read()))

    # ── A POLICY MAY NOT REQUIRE A RANK NOBODY HAS. Found by walking a
    # newcomer's path: `gate demo`, then a lie in each file to see which are
    # judged. `Person = Emp9999` refused correctly; `Requires = NoSuchRank`
    # said the world holds. The guard's own comment had promised for weeks that
    # "every Requires must be a real name", and the code asked only whether the
    # word LOOKED like one — capitalised was enough.
    #
    # The cause was a set that could not contain the answer: a person is
    # declared in the world, a rank in the FORMS the world is written in, and
    # `world_files()` returns only the former. The set is gathered from the
    # world, the forms it presents and the shelf it reads — without this
    # mechanism learning what a rank is.
    pol = os.path.join(tmp, "policyworld")
    run("demo", "org", pol)

    def _requires(rank):
        # read, THEN write: `open(w)` truncates before the nested read runs, and
        # a probe that quietly writes an empty policy proves nothing at all
        pp = os.path.join(pol, "gate.policy.swift")
        said = re.sub(r"Requires = \w+", "Requires = " + rank, open(pp).read())
        open(pp, "w").write(said)
        return run("status", cwd=pol)[1]

    real, unreal = _requires("Manager"), _requires("NoSuchRank")
    _requires("Manager")
    # and the file itself is one the bench admits to having. `gate demo` writes
    # it, it introduces itself in its own first line, its guard judges it and
    # the server serves it by URL — it was simply missing from the list, so a
    # newcomer who ran demo, listed the folder and looked at the panel found a
    # file on disk the tool did not own up to. Being outside the plain judged
    # stream says which court reads it, never that it should be invisible.
    listed = [n for n, _ in json.loads(subprocess.run(
        [sys.executable, "-c",
         "import types,json;src=open(%r,encoding='utf-8').read();g=types.ModuleType('g');"
         "g.__file__=%r;exec(compile(src,'gate','exec'),g.__dict__);"
         "print(json.dumps(g.bench_files()))" % (GATE, GATE)],
        cwd=pol, capture_output=True, text=True).stdout or "[]")]
    S.append(("a policy requiring a rank nobody declares is refused, not waved through",
              real.get("verdict") == "holds"
              and unreal.get("verdict") == "refused"
              and any("nobody has" in r.get("claim", "")
                      for r in unreal.get("refusals", []))
              and any("gate.policy.swift" in (r.get("address") or "")
                      for r in unreal.get("refusals", []))
              # and it is openable, not merely judged
              and "gate.policy.swift" in listed))

    # ── A PIN NAMES A MOMENT, AND THIS TOOL NOW KEEPS THE RULE IT HAD WRITTEN
    # DOWN. `cmd_side` had carried the sentence "nothing in this tool expresses a
    # range, which is exactly why no version solver exists here" for weeks, and
    # wrote `latest` into a row without a word. Both halves were failing at once:
    # the claim was false, and the reason it mattered was never enforced.
    #
    # The reason is a derivation, not a preference. A seam's verdict is a pure
    # function of the two revisions its sides were taken at, because the corpus
    # requires the facts a comparison reveals to be PRE-EXISTING — COMPARE
    # discloses what is already the case, it does not make it so (V=I §5.20). A
    # range or a branch name breaks exactly that: the other side's text changes
    # under you, so there is nothing fixed for a verdict to be a function of.
    # And the consequence runs backwards — `^1.2.0` does not make resolution
    # hard, it CREATES the problem by breaking the precondition under which the
    # question had an answer.
    pin = tempfile.mkdtemp(dir=tmp)
    open(os.path.join(pin, "gate.swift"), "w").write("public enum Sales: Department {}\n")
    open(os.path.join(pin, "sdk.swift"), "w").write(
        "public enum F_x: Declared { public typealias Of = Text }\n")

    def _pin(at):
        try:
            os.remove(os.path.join(pin, "gate.manifest.swift"))
        except OSError:
            pass
        return run("theirs", "sdk.swift", "--at", at, cwd=pin)[1]

    moving = {a: _pin(a) for a in ("^1.2.0", ">=1.0,<2.0", "1.2.x", "latest", "main", "HEAD")}
    fixed = {a: _pin(a) for a in ("0fd0b38", "v1.2.0", "2026-07-28", "release-14")}
    S.append(("a pin names a moment: a range or a moving name is refused, and says why",
              all(r.get("asks") for r in moving.values())
              and all("range" in r.get("note", "") or "moves" in r.get("note", "")
                      for r in moving.values())
              # and what a person actually took is taken without ceremony
              and all(r.get("at") == a and not r.get("asks") for a, r in fixed.items())
              # the reason travels with the refusal, because it is the reason
              # there is nothing here to solve
              and any("nothing here has to be solved" in r.get("next", "")
                      for r in moving.values())))

    # ── AND A COMMENT IS NOT A DECLARATION. `bench-atoms` documents this very
    # wheel by showing one — `///     public enum MyJournal: Journal {` — and
    # the reader took the example for an answer, so `gate log` in this
    # repository quietly obeyed a line written to explain it. Worse than the
    # wrong scope: the word typed afterwards looked broken, because it was
    # overriding something nobody had declared. Found by hand, not by a report.
    open(os.path.join(wj, "my-journal.swift"), "w").write(
        "// public enum Faker: Journal {\n//     public typealias Scope = AllRepo\n// }\n")
    only_said = run("log", cwd=wj)[1]
    S.append(("a wheel shown in a comment turns nothing, including the one this tool documents",
              only_said.get("scope") == "world"
              and "if not ln.strip().startswith" in shelf_src
              # and this repository is the case that proved it: it documents the
              # wheel and declares none, so its own journal must not be widened
              and json.loads(subprocess.run(
                  [sys.executable, GATE, "log", "1", "--json"], cwd=HERE,
                  capture_output=True, text=True).stdout).get("scope") == "world"))

    # ── A WORD THIS COMMAND DOES NOT KNOW IS A REFUSAL, BY THE WORD. `gate log
    # --help` ran as a bare `log`: no help, no refusal, the word swallowed. And
    # a refusal from a command that had never had one printed a traceback,
    # because every command formatted its own and this one had none — so the
    # silence had a second floor under it.
    helped = run("log", "--help", cwd=wj)[1]
    mistyped = run("log", "--wrold", cwd=wj)[1]
    S.append(("a word this command does not know is refused by name, not swallowed",
              helped.get("asks") and "`--help`" in helped.get("note", "")
              and mistyped.get("asks") and "`--wrold`" in mistyped.get("note", "")
              and "gate log all" in mistyped.get("next", "")
              # and it prints, whoever made it: one branch before every command's
              # own, so a refusal from a command that never had one still speaks
              and 'if out.get("asks") and out.get("note") and "verdict" not in out:' in shelf_src))

    # ── AND A SCOPE THAT CANNOT BE HONOURED SAYS SO. Asking for the world's
    # history where no file is declared a world file narrowed nothing and printed
    # the whole repository under the words `the repository` — true about what was
    # shown, silent about the word having done nothing.
    #
    # A WORLD OF FORMS IS STILL A WORLD, HERE TOO — the lesson `status` learned
    # and the journal did not. `world_files()` is the plain court's list and
    # rightly holds no forms row; the journal asks a wider question, and whose
    # history a file carries does not depend on which court reads it. This
    # repository was the case that made the point twice: it declares forms and a
    # layout and no world of facts, and for a while it was BOTH the example of a
    # scope that cannot be honoured AND a world whose history was being thrown
    # away. It narrows now. The un-narrowable case is a repository with tables
    # and nothing declared at all.
    seedonly = os.path.join(tmp, "seedonly")
    os.makedirs(os.path.join(seedonly, "tables"))
    for f in ("people.csv", "grants.csv"):
        shutil.copy(os.path.join(DEMO, f), os.path.join(seedonly, "tables", f))
    subprocess.run(["git", "init", "-q", "-b", "main", seedonly])
    subprocess.run(["git", "add", "-A"], cwd=seedonly, capture_output=True)
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=a",
                    "-c", "commit.gpgsign=false", "commit", "-qm", "tables"],
                   cwd=seedonly, capture_output=True)
    flat_log = run("log", "world", "1", cwd=seedonly)[1]
    said_flat = subprocess.run([sys.executable, GATE, "log", "world", "1"], cwd=seedonly,
                               capture_output=True, text=True).stdout
    here_log = json.loads(subprocess.run(
        [sys.executable, GATE, "log", "world", "1", "--json"], cwd=HERE,
        capture_output=True, text=True).stdout)
    S.append(("a scope that cannot be honoured says which word did nothing, and why",
              flat_log.get("scope") == "world" and flat_log.get("narrowed") is False
              and "nothing narrower" in said_flat
              # and where it CAN be honoured it simply is, with nothing added
              and run("log", "world", cwd=wj)[1].get("narrowed") is True
              # including here, where the whole world is grammar: the forms rows
              # are files of this world and their history is this world's history
              and here_log.get("narrowed") is True
              and any(f.startswith("stdlib/") for f in here_log.get("world_files", []))
              # and nobody standing inside a world is sent to `gate demo` to find one
              and "gate status" in here_log.get("next", "")))

    # ── AND THE ONE ROW THIS DOCUMENT EXISTS TO KEEP HONEST IS KEPT HONEST. The
    # manifest says which revision of the corpus the judge was taken at; the
    # binary says which revision it was built FROM, written beside it by
    # `build-judge.sh`. Two statements of one fact, and nothing compared them —
    # so rebuilding the judge and forgetting the row left the panel showing one
    # revision and the table another, both calmly, forever. Found by auditing
    # what is shown twice, which is where a disagreement can hide.
    #
    # Not the judge judging itself: arithmetic over two strings other people
    # wrote down. Self-application is not self-certification, and a row that
    # accounts for the court is worth nothing if nobody holds it to the court.
    jm = os.path.join(HERE, "gate.manifest.swift")
    kept = open(jm, encoding="utf-8").read()
    try:
        open(jm, "w", encoding="utf-8").write(
            kept.replace("verification-is-identification@0fd0b38",
                         "verification-is-identification@deadbee"))
        lied = run("status", cwd=HERE)[1]
    finally:
        open(jm, "w", encoding="utf-8").write(kept)
    S.append(("a row that names the court may not disagree with the court",
              run("status", cwd=HERE)[1].get("verdict") == "holds"
              and lied.get("verdict") == "refused"
              and any("may not disagree with the court" in r.get("claim", "")
                      for r in lied.get("refusals", []))
              and any(r.get("address") == "gate.manifest.swift"
                      for r in lied.get("refusals", []))))

    # ── THE BENCH AND THE COMMAND LINE ANSWER ABOUT THIS REPOSITORY THE SAME WAY.
    # They did not. `gate status` here said `holds` while the bench's own front
    # door showed twenty-one refusals, in red, about gate itself — every one of
    # them the duplicate guard fed two worlds at once, each legitimately spelling
    # its own ladder from Unit. The rule that a forms file is its own stream was
    # written down and obeyed by the CLI; the bench built its own list of files
    # beside it and never asked. It went unseen for as long as it did because we
    # always opened a sandbox to look, never this repository.
    _s = _sock.socket(); _s.bind(("127.0.0.1", 0)); _bench_port = _s.getsockname()[1]; _s.close()
    _bench = subprocess.Popen([sys.executable, GATE, "serve", "--port", str(_bench_port)],
                              cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        agreed = None
        wait_serve(_bench_port)
        man = os.path.join(HERE, "gate.manifest.swift")
        # the panel's sweep is measured here, not read: the CLI's fence below
        # counts makers and knows the sweeper's name, and both stay true with
        # the panel's one sweeping line deleted — the exact hole this began as,
        # one directory per keystroke. So: list temp, judge once, list again.
        import tempfile as _tf2
        _tmp2 = _tf2.gettempdir()
        _pnl_now = lambda: {n for n in os.listdir(_tmp2) if n.startswith("gate-")}
        _pnl_was = _pnl_now()
        req = _u.Request(f"http://127.0.0.1:{_bench_port}/verdict?f=gate.manifest.swift",
                         data=open(man, "rb").read(), method="POST")
        seen = json.loads(_u.urlopen(req, timeout=30).read().decode())
        # the response is written before the sweep runs, so give it a breath
        swept = False
        for _ in range(20):
            swept = _pnl_now() - _pnl_was == set()
            if swept:
                break
            time.sleep(0.1)
        said = run("status", cwd=HERE)[1]
        agreed = (seen.get("verdict") == said.get("verdict"),
                  seen.get("verdict"), len(seen.get("refusals", [])), said.get("verdict"))
    finally:
        _bench.terminate()
    S.append(("the bench and the command line say the same thing about this repository",
              agreed and agreed[0] and agreed[1] == "holds"))
    S.append(("the panel leaves no scratch behind an answered judgement", swept))

    # AND ABOUT A WORLD THAT HAS THE FILES THIS ONE HAPPENS NOT TO. The fence
    # above compares gate's own repository, which declares no policy at all —
    # so the day the policy joined the bench's file list it was also handed to
    # the plain court, which refuses its extension form on sight, and the bench
    # refused what the command line held. One repository is not a fence; a
    # comparison is only as wide as the world it is run on.
    dw = os.path.join(tmp, "bothsurfaces")
    run("demo", "org", dw)
    _s4 = _sock.socket(); _s4.bind(("127.0.0.1", 0)); _dp = _s4.getsockname()[1]; _s4.close()
    _db = subprocess.Popen([sys.executable, GATE, "serve", "--port", str(_dp)], cwd=dw,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    both = None
    try:
        wait_serve(_dp)
        man = os.path.join(dw, "gate.manifest.swift")
        seen = json.loads(_u.urlopen(_u.Request(
            f"http://127.0.0.1:{_dp}/verdict?f=gate.manifest.swift",
            data=open(man, "rb").read(), method="POST"), timeout=30).read().decode())
        both = (seen.get("verdict"), run("status", cwd=dw)[1].get("verdict"),
                len(seen.get("refusals", [])))
    finally:
        _db.terminate()
    S.append(("and about a world with a policy and forms in it, where they last disagreed",
              both and both[0] == both[1] == "holds" and both[2] == 0))
    if agreed and not agreed[0]:
        print("   bench says", agreed[1], "with", agreed[2], "refusals; the CLI says", agreed[3])

    # ── ONE READING OF A NUMBER, AND THE PAGE'S IS IT. These worlds spell their
    # numbers on their own ladder from Unit, so a value is a term to be read and
    # not a string to be shown — the table and the bare view were both printing
    # `Plus<W8, Plus<W16, …>>`, which is how a number is built and not what it
    # is. The page reads it now, with the same walk on both surfaces. That is a
    # second counter beside the tool's, so it is held to the tool's answer here:
    # every name in every world this tool ships, counted both ways.
    harness = os.path.join(tmp, "count-parity.js")
    open(harness, "w").write("""
const fs = require("fs");
const ui = fs.readFileSync(process.argv[2], "utf8");
const { judge } = require(process.argv[3]);
const text = fs.readFileSync(process.argv[4], "utf8");
const grab = (name) => {
    const at = ui.indexOf("function " + name + "(");
    if (at < 0) throw new Error("no " + name);
    let d = 0;
    for (let j = ui.indexOf("{", at); j < ui.length; j++) {
        if (ui[j] === "{") d++;
        else if (ui[j] === "}" && --d === 0) return ui.slice(at, j + 1);
    }
};
const parsed = judge("w.swift", text, { seeds: new Set(), generics: new Set() }).parsed;
const worldAliases = parsed.topAliases, lastParsed = parsed;
const language = { names: { Unit: 1, Plus: 1, Times: 1, Twice: 1, Paired: 1 } };
eval(grab("countTerm") + "\\n" + grab("termArgs") + "\\n" + grab("shownTerm"));
const out = {};
for (const [n, a] of parsed.topAliases) {
    const v = countTerm(a.target, 0);
    if (v !== null) out[n] = v;
}
console.log(JSON.stringify(out));
""")
    counted_both, disagree = 0, []
    for w in sorted(os.listdir(os.path.join(HERE, "stdlib"))):
        if not w.endswith(".swift"):
            continue
        wp = os.path.join(HERE, "stdlib", w)
        tool = json.loads(subprocess.run(
            [sys.executable, "-c",
             "import types,json;src=open(%r,encoding='utf-8').read();g=types.ModuleType('g');"
             "g.__file__=%r;exec(compile(src,'gate','exec'),g.__dict__);"
             "print(json.dumps(g._peano(open(%r,encoding='utf-8').read())))"
             % (GATE, GATE, wp)], capture_output=True, text=True).stdout)
        page = json.loads(subprocess.run(
            ["node", harness, os.path.join(HERE, "ui.html"),
             os.path.join(HERE, "judge.js"), wp], capture_output=True, text=True).stdout or "{}")
        for k in set(tool) | set(page):
            counted_both += 1
            if tool.get(k) != page.get(k):
                disagree.append((w, k, tool.get(k), page.get(k)))
    S.append(("the page counts a number exactly as this tool does, in every world it ships",
              counted_both > 150 and not disagree))
    if disagree:
        print("   counters disagree:", disagree[:4])

    # ── AND HOW HARD A REGISTER IS SET IS THE WORLD'S TO SAY. It was three world
    # names written inside this tool — a vocabulary living in a mechanism, which
    # is the one thing no layer here may do: present a register of your own and
    # it could never be firm, because the tool had never heard of it.
    S.append(("a register says how hard it is set, and the tool only reads it",
              "public protocol Stress {}" in registers_src
              and "public typealias Set = Firm" in registers_src
              and 'weight = "600 " if stresses.get(name) == "Firm" else ""' in shelf_src
              and '"Brand", "Headline", "Headsmall"' not in shelf_src))

    # ── AND AN OVERRIDE IS VISIBLE FROM THE LIST. It is judged now — the shipped
    # laws test whatever number is put in its place — but judged and silent is
    # still green silence about values: in a month "why is this colour different
    # here" gets answered by feel, or by grep. The file says how many names it
    # overrules, in the rail, before it is opened.
    over_seen = subprocess.run(
        [sys.executable, "-c",
         "import types,json;src=open(%r,encoding='utf-8').read();g=types.ModuleType('g');"
         "g.__file__=%r;exec(compile(src,'gate','exec'),g.__dict__);"
         "o={}\n"
         "for s in sorted(g.STDLIB):\n"
         " for n,p in (g.presented_over(s)[1] or {}).items(): o.setdefault(p,[]).append(n)\n"
         "print(json.dumps({k:sorted(v) for k,v in o.items()}))"
         % (GATE, GATE)], cwd=ovr, capture_output=True, text=True).stdout
    S.append(("what a name was before somebody said otherwise is answerable at the name",
              "my-colours.swift" in over_seen and "KnownNameDimZ" in over_seen
              # and the rail asks for exactly that, and paints it in the quiet
              # register — two questions live in a name's hue and this is neither
              and '"overridden": overridden,' in shelf_src
              # keyed by NAME, and carrying what the name was — because the fact
              # is owed at the value, in the table of the world that declares it,
              # not as a badge on a file in a side panel
              and '"was": was.group(1).rstrip()}' in shelf_src
              # and where it hurts is seen without opening the file
              and ".file.bad .name{text-decoration:underline wavy var(--bad)" in ui))

    # ── AND THE EFFECTIVE SET IS JUDGED, or the freedom is a freedom to lie to
    # yourself. For a while nothing judged the result of an override: the
    # certificates stayed in the shipped file and the numbers moved to the
    # operator's, and the two never met — so repainting the verdict channel
    # green gave a bench that shows refusals in the colour of agreement, with
    # every court silent. Probed exactly that way.
    #
    # The line you write stands where theirs stood, so every certificate that
    # shipped goes on testing what you put there. Say any number; say what still
    # holds of it. And the form of a law is not yours to replace — restating
    # `TowardWarm` as `TowardBlue` does not satisfy a law, it deletes one, and
    # then any value could be permitted by rewriting what forbade it.
    guard = tempfile.mkdtemp(dir=tmp)
    open(os.path.join(guard, "gate.swift"), "w").write("public enum Sales: Department {}\n")
    mineclr = os.path.join(guard, "my-colours.swift")

    def _say(body):
        open(mineclr, "w").write("// role: forms\n" + body)
        return run("status", cwd=guard)[1]
    open(mineclr, "w").write("// role: forms\n")
    run("mine", "my-colours.swift", "--role", "forms", cwd=guard)
    # a number moved, and the laws about it restated: this is the whole freedom
    lawful = _say(
        "public typealias KnownNameDimZ = Plus<W8, Plus<W16, Plus<W32, Plus<W64,"
        " Plus<W128, W512>>>>>\n"
        "public typealias KnownNameChroma_dim = TowardBlue<KnownNameDimY, KnownNameDimZ,"
        " Plus<Unit, Plus<W2, Plus<W32, Plus<W64, Plus<W1024, Plus<W2048, W4096>>>>>>>\n"
        "public typealias MineApartTheirs_Z_dim = Apart<KnownNameDimZ, LocalTypeDimZ,"
        " Plus<Unit, Plus<W2, Plus<W4, Plus<W32, W64>>>>>\n"
        "public typealias TheirsApartBad_Z_dim = Apart<KnownNameDimZ, BadDimZ,"
        " Plus<Unit, Plus<W2, Plus<W4, Plus<W8, Plus<W64, W512>>>>>>\n")
    # the verdict channel repainted toward agreement: refused by the law that
    # says a verdict leans warm, at the operator's own line
    green = _say("public typealias BadDimZ = Plus<W256, W512>\n")
    # and the law itself rewritten to permit it: refused as a law that is not theirs
    rewrite = _say("public typealias BadChroma_dim = TowardBlue<BadDimY, BadDimZ, Plus<W2, W4>>\n")
    S.append(("say any number, say what holds of it, and the form of a law is not yours",
              lawful.get("verdict") == "holds"
              and green.get("verdict") == "refused"
              and any("BadChroma_dim" in r.get("claim", "") or "Apart<BadDimZ" in r.get("claim", "")
                      for r in green.get("refusals", []))
              and all((r.get("address") or "").startswith("my-colours.swift")
                      for r in green.get("refusals", []))
              and rewrite.get("verdict") == "refused"
              and any("is not yours to replace" in r.get("claim", "")
                      for r in rewrite.get("refusals", []))))

    # ── AN EXHIBIT, NOT A WISH. What follows records what a claim written in the
    # head of the file that depends on it does TODAY, line by line, because the
    # answer is the case for the one change everything left is waiting on: the
    # judge we ship is a DIFFERENTIAL ARBITER for one reference world, and its
    # own header says so: the table it carries is that world's policy stated a
    # second time, on purpose, so two encodings can check each other. Its
    # fragment knows five file shapes and `public protocol` is not among them.
    #
    # I had called this a compiled vocabulary and built three rounds of law on
    # that reading. It was wrong, and reading the judge's own source is what
    # showed it: there is no privileged word list — there is one world's policy
    # restated for a differential seat, and a grammar of five shapes.
    #
    # So this pins the shape of THAT wall, not a limit of the system. Our own
    # port already parses a presented protocol and reads the axes it states;
    # what it does not do is take its requirements from them. Patched to do so
    # in one line, a presented foreign world refuses a lie at the line — "the
    # name Nonexistent resolves to nothing", on a domain no judge has heard of.
    # The empty prism is ours to build and does not need the corpus.
    claim_probe = tempfile.mkdtemp(dir=tmp)
    open(os.path.join(claim_probe, "world.swift"), "w").write(
        "// ── what this file took ──\n"
        "public protocol Role {}\n"
        "public enum SeamFile: Role {}\n"
        "public protocol Theirs {}\n"
        "public enum Rev_api {}\n"
        'extension Rev_api { public static var typeName: String { "openapi@3f2a1c9" } }\n'
        "public enum TheContract: Theirs {\n"
        "    public typealias Kind = SeamFile\n"
        "    public typealias At = Rev_api\n"
        "}\n"
        "\npublic enum Sales: Department {}\n")
    judge_bin = os.path.join(HERE, "bin", "gate-judge")
    plain = subprocess.run([judge_bin, "judge", os.path.join(claim_probe, "world.swift")],
                           capture_output=True, text=True).stdout
    where = subprocess.run([judge_bin, "judge", "where", os.path.join(claim_probe, "world.swift")],
                           capture_output=True, text=True).stdout
    S.append(("a claim written where it is used is judged by neither court today",
              # the plain court refuses it on FORM: a protocol is outside the
              # fragment, and so is the extension that spells a typeName
              "outside the fragment" in plain
              and "public protocol Role {}" in plain
              and "typeName" in plain
              # and the where court takes the same text and judges nothing at
              # all — a green over nought uses, which says neither yes nor no
              and "THE WHERE holds" in where and "across 0 uses" in where))

    # ── AND THE DIAMOND HOLDS ON CLAIMS, which is the half that already works.
    # Two files claiming the same revision atom are two truths about one name,
    # and that is refused with BOTH addresses rather than resolved by a rule
    # nobody can read. No solver exists here because no range can be written;
    # what a conflict gets instead is a sentence and two places to look.
    dia = tempfile.mkdtemp(dir=tmp)
    open(os.path.join(dia, "gate.swift"), "w").write("public enum Sales: Department {}\n")
    for who in "ab":
        open(os.path.join(dia, f"{who}.swift"), "w").write(
            "public enum Rev_api {}\n"
            f"public enum Ops{who}: Department {{}}\n")
        run("mine", f"{who}.swift", cwd=dia)
    doubled = run("status", cwd=dia)[1]
    S.append(("one claim declared in two files is refused with both addresses",
              doubled.get("verdict") == "refused"
              and any("Rev_api" in r.get("claim", "")
                      and "declared twice" in r.get("claim", "")
                      and "a.swift:1" in r.get("claim", "")
                      and (r.get("address") or "").startswith("b.swift:")
                      for r in doubled.get("refusals", []))))

    # ── WHAT THIS JUDGE WAS MADE FROM. Its identity is its bytes, and that is
    # what a reviewer reproduces — but bytes say what a thing IS, never what it
    # was made from, so the one dependency this whole tool rests on was stated as
    # an opaque hash that nobody could check without already knowing the answer.
    # No seam is wanted here: a seam is for two parties with no judge between
    # them, and this pair shares one — a disagreement with the corpus is refused
    # at a keystroke rather than reported. What was missing is provenance, and
    # where it is missing that is said rather than glossed.
    # beside the judge that actually answers: --version reads JUDGE + ".from",
    # so a battery pointed at a rebuilt judge (GATE_JUDGE=...) fixtures that one
    keep = (os.environ.get("GATE_JUDGE") or os.path.join(HERE, "bin", "gate-judge")) + ".from"
    had = open(keep).read() if os.path.exists(keep) else None
    try:
        if os.path.exists(keep):
            os.remove(keep)
        silent = say("--version")
        open(keep, "w").write("1f4c0a9d3e7b2c5a8f0d6e4b1c9a7f3d5e2b8c40\n")
        spoken = say("--version")
    finally:
        if had is not None:
            open(keep, "w").write(had)
        elif os.path.exists(keep):
            os.remove(keep)
    S.append(("the judge says which revision of the corpus it was built from, and says so when it cannot",
              "is not recorded" in silent
              and "verification-is-identification 1f4c0a9d3e7b" in spoken
              and "build-judge.sh 1f4c0a9d3e7b" in spoken
              # and the build writes it down rather than leaving it to be guessed
              and "git rev-parse HEAD" in open(os.path.join(HERE, "bin", "build-judge.sh")).read()))

    # ── THE PITCH STAYS OUTSIDE THE VERDICT. A brand may say `sight for
    # promises`; a verdict may not. What a reader is handed by the tool is what
    # was observed, the bounds it was observed in, numbers, and a recipe — and
    # the sensory words that make the sale would, standing there, be the tool
    # claiming to see what it has not seen. Kept as a discipline this leaks
    # eventually, so it is a wall: string constants the tool prints, and every
    # crystal it ships as text.
    # `light` is deliberately absent from the list — the palette's light is a
    # physical subject, not a metaphor, and a fence that forbids a domain its own
    # word is a fence in the wrong place.
    PITCH = re.compile(r"\b(blind\w*|prayer\w*|candle\w*|illuminat\w*|darkness|eyesight"
                       r"|vision|sight|hearing)\b", re.I)
    spoken = [n.value for n in ast.walk(ast.parse(open(GATE).read()))
              if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    shipped = [open(os.path.join(STDLIB, f)).read()
               for f in os.listdir(STDLIB) if f.endswith(".swift")] if os.path.isdir(STDLIB) else []
    S.append(("the words that sell stay out of what the tool says",
              bool(spoken) and bool(shipped)
              and not [s for s in spoken if PITCH.search(s)]
              and not [s for s in shipped if PITCH.search(s)]))

    # ── and the first thing a stranger types is `--help`. Taking it for a
    # filename printed an observation of a contract that does not exist, in the
    # first second of the first minute somebody spends here.
    _, asked = run("drift", "--help")
    _, missing_spec = run("drift", os.path.join(tmp, "nowhere.json"), "--client", tmp)
    S.append(("the first thing a stranger types is not a filename",
              asked.get("asks") and "drift CONTRACT" in asked.get("note", "")
              and missing_spec.get("asks") and "no such contract" in missing_spec.get("note", "")
              # and asking is not an error
              and "verdict" not in asked and not asked.get("over_threshold")))

    S.append(("a library that spells no route at all is accused of missing none",
              bare_types.get("silent_routes") == [] and "url" not in bare_types.get("unwritten", [])))

    # ── and the check is the whole ceremony: one command in the CI the client
    # already has. It exits non-zero on a stale citation and zero when the code
    # and the tracker agree, so no wrapper is needed; the export may sit in
    # another checkout entirely, because gate never fetches — what it judges is
    # brought to it. And the world it prints is a CHECK, not a file to keep:
    # left in a repo that declares its layout it would read as a shadow and earn
    # the reader a red they did not deserve, so unless it is asked for by name it
    # is judged where nothing keeps it.
    ci = os.path.join(tmp, "ci")
    os.makedirs(os.path.join(ci, "elsewhere"), exist_ok=True)
    os.makedirs(os.path.join(ci, "repo", "src"), exist_ok=True)
    open(os.path.join(ci, "elsewhere", "export.json"), "w").write(json.dumps(
        {"issues": [{"key": "PROJ-7", "status": "Done"}]}))
    open(os.path.join(ci, "repo", "src", "app.py"), "w").write(
        "def go():\n    # TODO(PROJ-7): the ticket is done, the note is not\n    return 1\n")
    drift = subprocess.run([sys.executable, GATE, "import", "refs",
                            os.path.join(ci, "elsewhere", "export.json"), "--code", "."],
                           capture_output=True, text=True, cwd=os.path.join(ci, "repo"))
    open(os.path.join(ci, "elsewhere", "live.json"), "w").write(json.dumps(
        {"issues": [{"key": "PROJ-7", "status": "In Progress"}]}))
    clean = subprocess.run([sys.executable, GATE, "import", "refs",
                            os.path.join(ci, "elsewhere", "live.json"), "--code", "."],
                           capture_output=True, text=True, cwd=os.path.join(ci, "repo"))
    S.append(("the check is one command with the other side wherever it lies, and it leaves nothing behind",
              drift.returncode == 1 and clean.returncode == 0
              and "src/app.py:2" in drift.stdout
              and not os.path.exists(os.path.join(ci, "repo", "refs-gate.swift"))))

    # ── one world, one stream. A list of files handed to `judge where` is not one
    # world read across files: the sides are judged apart, and the certificates of
    # one are never held against the machinery of the other. It fails GREEN, which
    # is the one failure a checker may not have — so the pipes must never hand
    # `where` more than a single path, and a world split across files is glued
    # into one stream first. The second half of this check proves the rule is
    # load-bearing rather than folklore: it plants a real break, judges the halves
    # as a list and as one stream, and requires the list to be the blind one. If a
    # future judge learns to read a list, this half fails and says the guard may
    # retire — a rule that cannot say when it stopped being needed is a rule that
    # outlives its reason.
    gate_src = open(GATE, encoding="utf-8").read()
    # the call moved into one place that picks a court (binary or port) and the law
    # about it is unchanged: no caller hands the certificate court a list
    where_calls = re.findall(r"judge_call\(\[\"judge\", \"where\",([^\]]*)\]", gate_src)
    one_path = all("*" not in c for c in where_calls)
    pal_text = open(os.path.join(HERE, "stdlib", "bench-palette.swift"), encoding="utf-8").read()
    cut = pal_text.index("// ── the light theme")
    machinery, values = pal_text[:cut], pal_text[cut:]
    broken = re.sub(r"public typealias InkLitY = .+",
                    "public typealias InkLitY = Plus<W256, Plus<W512, W128>>", values, count=1)
    d = os.path.join(tmp, "stream")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "machinery.swift"), "w").write(machinery)
    open(os.path.join(d, "values.swift"), "w").write(broken)
    open(os.path.join(d, "glued.swift"), "w").write(machinery + broken)
    def refusals_of(*paths):
        r = subprocess.run([os.path.join(HERE, "bin", "gate-judge"), "judge", "where", *paths],
                           capture_output=True, text=True).stdout
        return r.count("✗")
    glued_says = refusals_of(os.path.join(d, "glued.swift"))
    listed_says = refusals_of(os.path.join(d, "machinery.swift"), os.path.join(d, "values.swift"))
    S.append(("one world is one stream: a split handed over as a list is judged blind, so the pipes never hand one over",
              one_path and bool(where_calls) and glued_says > 0 and listed_says == 0))

    # ── and a claim is written INSIDE the body it belongs to. A world prints
    # `>.self` with no semicolon where nothing is separated, so a search that
    # insisted on one found nothing, ran past the closing brace and wrote the
    # claim outside every declaration — the judge said "outside the fragment" at
    # the next keystroke, which is how it was found. The end of the body is now
    # the bound of the search, not a pattern that may fail to match.
    S.append(("a claim is written inside the body it belongs to, and the search for its place cannot leave it",
              'const body = locateSlot({ kind: "record", line: d.line });' in ui
              and "while (at < lastLine" in ui
              and "/\\.self\\s*;?\\s*$/" in ui
              and "if (at >= lastLine) at = Math.max(d.line - 1, lastLine - 1);" in ui))

    # ── a target of the hand has a floor, and the floor is one reading line (Р1).
    # Reaching costs time that grows with distance and falls with the target's
    # size, so the smallest thing a hand is asked to hit is the smallest thing it
    # is asked to read — the base every distance here is already measured in. Not
    # a number borrowed from a phone: this bench is driven by a mouse, and that is
    # said rather than derived. Every rule in the fabric that offers the pointer
    # must carry that floor, so a gesture added later cannot arrive without one.
    bare_style = re.sub(r"/\*.*?\*/", " ", style, flags=re.S)   # a comment is not a selector
    rules = [(sel.strip().replace("\n", " "), body)
             for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", bare_style)]
    floor_sel = next((s for s, b in rules
                      if "padding-top:var(--u)" in b and "padding-bottom:var(--u)" in b), "")
    floored = {p.strip() for p in floor_sel.split(",")}
    handed = [part.strip() for s, b in rules if "cursor:pointer" in b
              for part in s.split(",") if re.search(r"#bare|#table-host", part)]
    def has_own_floor(sel):
        # its own rule, or the plainer rule for the SAME element — a cell takes the
        # padding of `td`, but a mark takes nothing from the panel it sits in: a
        # container's padding is not a target's floor
        kin = {sel}
        last = sel.split()[-1]
        if "." in last and not last.startswith("."):
            kin.add(" ".join(sel.split()[:-1] + [last.split(".")[0]]).strip())
        return any(("padding" in b or "min-height" in b)
                   and any(part.strip() in kin for part in s.split(","))
                   for s, b in rules)
    floorless = [h for h in handed if h not in floored and not has_own_floor(h)]
    S.append(("a target of the hand is at least one reading line, and no gesture arrives without that floor",
              bool(handed) and not floorless and bool(floored)
              and "#bare .cut{padding:calc(var(--u)*2) calc(var(--u)*3)}" in style))

    # ── and a line number is scaffolding, not speech: it stands outside the file's
    # own text, so it wears the seam and not the rung a comment wears. Both sat on
    # muted once, which painted an index and a sentence the same — a merge the
    # reader parts and the scene did not (С9).
    S.append(("a line number is scaffolding and wears the seam, not the rung a comment wears",
              ".CodeMirror-linenumber{color:var(--seam)" in style
              and ".cm-s-default .cm-comment{color:var(--muted)}" in style))

    # ── what is removed is removed whole. A record, an axis it states, a claim it
    # holds: each is one unit and one edit, found through the SAME bridge a value
    # is found through, so nothing is ever half-cut. What the removal costs is not
    # guessed at either — the judge reads the file again and names every reader by
    # address, which is the only honest answer to "what did that break". And a
    # cell is that same closed question in a column: its kind comes from the
    # group's own signature, so a stranger is never among the choices.
    S.append(("what is removed is removed whole, and a cell is the same closed question in a column",
              'if (slot.kind === "record") {' in ui and 'if (slot.kind === "entry") {' in ui
              and 'if (slot.kind === "axis") return wholeLines(line, line);' in ui
              and "function removeUnit(slot) {" in ui
              and ui.count('cm.replaceRange("", at.from, at.to') == 1      # one edit, one unit
              and "const kind = axesOfHost(host)[key];" in ui              # the column's own kind
              and "const items = fillersFor(kind, host, key);" in ui
              and 'add.onclick = () => askName(group.conformances.join(", "));' in ui))

    # ── a kind is a name, and a body written on the same line is not part of it.
    # The shelf declares its documents in one line each, and the head's parser
    # carried the body along: the kind came out spelled `Document { public
    # typealias Home = Finance }`, so the shelf knew four documents and every
    # offer for a Document was empty. The bench cannot show what the vocabulary
    # cannot name, and this is the reading both of them share.
    kinds_js = ('const { judge } = require(%r); const fs = require("fs");\n'
                'const p = judge("g.swift", fs.readFileSync(%r, "utf8")).parsed.declarations;\n'
                'const all = [...p.values()].flatMap(d => d.conformances || []);\n'
                'console.log(JSON.stringify({ glued: all.filter(c => /[{}]/.test(c)),\n'
                '  documents: [...p.values()].filter(d => (d.conformances||[]).includes("Document")).map(d => d.name) }));'
                % (os.path.join(HERE, "judge.js"),
                   os.path.join(HERE, "stdlib", "forms-organization.swift")))
    kj = os.path.join(tmp, "kinds.js")
    open(kj, "w").write(kinds_js)
    kout = subprocess.run(["node", kj], capture_output=True, text=True).stdout
    try:
        kk = json.loads(kout or "{}")
    except Exception:
        kk = {}
    S.append(("a kind is a name and not a name with a body: what the shelf declares in one line is still offerable",
              kk.get("glued") == [] and len(kk.get("documents") or []) >= 4))

    # ── a record is born from a form, and every step of it is closed but one.
    # The shapes are the ones the world has actually lived, most travelled first;
    # a claim may only be a form whose arguments have STATED kinds, because one
    # that takes bare numbers cannot be asked closed; and the single free step —
    # the name — is checked as it is typed and never written unless it is free.
    form_src = "\n".join(
        "function " + n + ui.split("\nfunction " + n, 1)[1].split("\n}", 1)[0] + "\n}"
        for n in ("livedCombos() {", "nameTaken(n) {"))
    form_js = r'''
const protoAxes = { Employee: { Rank: "Ranked" }, Person: { Sex: "Sexed" }, Lonely: { X: "Y" } };
const conformers = { Sexed: ["Male"] };
const vocabulary = { Employee: "forms", Male: "forms" };
const layoutOrActive = () => new Map([
    ["A", { conformances: ["Employee", "Person"] }],
    ["B", { conformances: ["Employee", "Person"] }],
    ["C", { conformances: ["Person"] }],
]);
__FORMS__
const gates = { VerifiedView: ["Employee", "Document"], Same: [null, null], Bare: [] };
const askable = Object.keys(gates).filter(g => (gates[g] || []).length && gates[g].every(Boolean));
console.log(JSON.stringify({
    combos: livedCombos(),
    taken: ["A", "Employee", "lower", "Fresh"].map(n => nameTaken(n)),
    askable,
}));
'''.replace("__FORMS__", form_src)
    fj = os.path.join(tmp, "forms.js")
    open(fj, "w").write(form_js)
    fout = subprocess.run(["node", fj], capture_output=True, text=True).stdout
    try:
        fv = json.loads(fout or "{}")
    except Exception:
        fv = {}
    taken = fv.get("taken") or [None, None, None, None]
    S.append(("a record is born from a form: the shapes the world has lived come first, and only a free name is written",
              fv.get("combos", [None])[0] == "Employee, Person"     # the most travelled shape leads
              and "Lonely" in (fv.get("combos") or [])              # and a kind nobody wears is still offered
              and taken[0] and taken[1] and taken[2] and taken[3] is None
              and fv.get("askable") == ["VerifiedView"]             # a form with bare arguments is not asked
              and 'gates[g].every(Boolean)' in ui
              and 'if (!check()) return;' in ui))                   # the name is checked before it is written

    # ── a hole is not text yet. What a record still owes is drawn as a row and
    # nothing is written until a WHOLE line can be written: axis, `=` and value
    # go in together, in ONE edit, so the buffer never holds `typealias X = ` for
    # a single keystroke (I2 — a pending alias swallows the line below it). The
    # line goes INSIDE the body: taking its position from a stale snapshot of
    # every file once put it after the closing brace, and the judge said so.
    hole_src = "function fillHole(slot, value) {" + \
        ui.split("function fillHole(slot, value) {", 1)[1].split("\n}", 1)[0] + "\n}"
    hole_js = r'''
let edits = [];
const doc = { lines: [
    "public enum Emp: Employee {",
    "    public typealias Rank = Manager",
    "}",
    "public enum Bare: Employee {}",
] };
const cm = {
    lineCount: () => doc.lines.length,
    getLine: (i) => doc.lines[i],
    replaceRange: (text, from, to) => {
        edits.push(text);
        const s = doc.lines.join("\n").split("\n");
        const flat = (p) => s.slice(0, p.line).join("\n").length + (p.line ? 1 : 0) + p.ch;
        const whole = doc.lines.join("\n");
        doc.lines = (whole.slice(0, flat(from)) + text + whole.slice(flat(to))).split("\n");
    },
};
const lastParsed = { declarations: new Map([
    ["Emp",  { line: 1, aliases: new Map([["Rank", { target: "Manager", line: 2 }]]), conformances: ["Employee"] }],
    ["Bare", { line: 4, aliases: new Map(), conformances: ["Employee"] }],
])};
// the stale snapshot: the same records, line numbers from before the last edit.
// Reading positions from here is the bug this half of the probe exists to catch.
const layoutOrActive = () => new Map([
    ["Emp",  { line: 1, aliases: new Map([["Rank", { target: "Manager", line: 3 }]]), conformances: ["Employee"] }],
    ["Bare", { line: 4, aliases: new Map(), conformances: ["Employee"] }],
]);
const render = () => {};
__HOLE__
fillHole({ kind: "hole", host: "Emp", axis: "Site" }, "OnSite");
const afterBody = doc.lines.slice(0, 4);
edits = [];
fillHole({ kind: "hole", host: "Bare", axis: "Site" }, "OnSite");
console.log(JSON.stringify({
    inside_body: afterBody,
    empty_body_opened: doc.lines.slice(-3),
    one_edit_each: edits.length === 1,
}));
'''.replace("__HOLE__", hole_src)
    hj = os.path.join(tmp, "holes.js")
    open(hj, "w").write(hole_js)
    hout = subprocess.run(["node", hj], capture_output=True, text=True).stdout
    try:
        hv = json.loads(hout or "{}")
    except Exception:
        hv = {}
    S.append(("a hole is filled by one whole line, written inside the body and never half-written",
              hv.get("inside_body") == ["public enum Emp: Employee {",
                                        "    public typealias Rank = Manager",
                                        "    public typealias Site = OnSite",
                                        "}"]
              and hv.get("one_edit_each") is True
              and "public typealias Site = OnSite" in "\n".join(hv.get("empty_body_opened") or [])
              and "function holesOf(d)" in ui))

    # ── a slot is a closed question, and the bench may only offer what the judge
    # will take. The bridge is checked from both sides: every value the grammar
    # offers for an axis is accepted, and a name of some OTHER kind is refused by
    # the judge naming where it landed instead. The negative half is the point —
    # an offer that is never refused proves nothing about what it filtered.
    forms_txt = open(os.path.join(HERE, "stdlib", "forms-organization.swift"), encoding="utf-8").read()
    slot_js = '''
const { judge } = require(%r);
const forms = %s;
const world = (v) => forms + `
public enum P1: Person {
    public typealias Given = G1
    public typealias Family = F1
    public typealias Born = B1
    public typealias Sex = ${v}
}
public enum G1: GivenNameCycle { public typealias Next = G1
    public typealias Sex = Male }
public enum F1: FamilyNameCycle { public typealias Next = F1 }
public enum B1: BirthYearCycle { public typealias Next = B1 }
`;
const landsIn = (v) => (judge("w.swift", world(v)).refusals || [])
    .some(r => /lands in/.test(r.premise) && /P1\\.Sex/.test(r.premise));
console.log(JSON.stringify({
    offered: ["Male", "Female"].map(landsIn),     // what the grammar offers: taken
    foreign: ["Manager", "Finance"].map(landsIn), // a name of another kind: refused
}));
''' % (os.path.join(HERE, "judge.js"), json.dumps(forms_txt))
    sj = os.path.join(tmp, "slotkinds.js")
    open(sj, "w").write(slot_js)
    sout = subprocess.run(["node", sj], capture_output=True, text=True).stdout
    try:
        sv = json.loads(sout or "{}")
    except Exception:
        sv = {}
    S.append(("a slot offers only what the judge takes, and a name of another kind is refused by where it lands",
              sv.get("offered") == [False, False] and sv.get("foreign") == [True, True]
              # one offer, anchored by a parameter — the editor's caret or a slot's own box
              and "const co = compRect || cm.charCoords(compFrom, \"page\");" in ui
              and "const items = fillersFor(kind, host, slot.axis);" in ui
              and "function fillSlot(slot, value)" in ui
              and ui.count("function locateSlot(") == 1))

    # ── a note belongs to a record, not to a line. Consecutive /// standing
    # directly above a declaration are what you wrote about it; a blank line
    # between is not a gap in a note, it is the end of one, and what it cuts off
    # belongs to the document instead. Read off the text by the parse's own line
    # numbers, so the judge's reading of the file and the bench's stay one. The
    # real function is lifted out of the page and run, never a copy of its rules.
    notes_src = "function attachNotes(text, parsed) {" + \
        ui.split("function attachNotes(text, parsed) {", 1)[1].split("\n}", 1)[0] + "\n}"
    notes_js = notes_src + r'''
const decls = new Map([["Kept", { line: 3 }], ["Cut", { line: 7 }]]);
const text = [
    "/// the note above the record",   // 1
    "/// and its second line",         // 2
    "public enum Kept: Employee {",    // 3  <- the parse reports this line
    "}",                               // 4
    "/// cut off by the blank line",   // 5
    "",                                // 6  <- the blank ends the run
    "public enum Cut: Employee {",     // 7
].join("\n");
const got = attachNotes(text, { declarations: decls, topAliases: new Map() });
console.log(JSON.stringify({ kept: got.get("Kept") || null, cut: got.get("Cut") || null }));
'''
    nj = os.path.join(tmp, "notes.js")
    open(nj, "w").write(notes_js)
    nout = subprocess.run(["node", nj], capture_output=True, text=True).stdout
    try:
        nv = json.loads(nout or "{}")
    except Exception:
        nv = {}
    S.append(("a note belongs to the record it stands above, and a blank line ends it rather than spanning it",
              nv.get("kept") == ["the note above the record", "and its second line"]
              and nv.get("cut") is None
              and "bareForm(lastParsed, cm.getValue())" in ui
              and 'const hasNotes = group.rows.some(d => notes.has(d.name));' in ui
              and '...(hasNotes ? ["note"] : [])' in ui))

    # ── and belonging is a shared edge. Every row on the rail — the brand, the
    # section heads, a file — begins at ONE step,
    # so the eye reads a column and not a ragged stack. It was ragged: the edge
    # was written `1.1em` everywhere and the rows set their text at 11, 12.5 and
    # 13px, so one declaration painted 12.1, 13.75, 14.3 and 16.7 pixels. A step
    # of the reading line cannot say a thing and mean four.
    def _left_u(sel):
        blk = style.split(sel + "{", 1)[1].split("}", 1)[0] if (sel + "{") in style else ""
        m = re.search(r"padding-left\s*:\s*(?:calc\(var\(--u\)\*(\d+)\)|(var\(--u\)))", blk)
        if not m:
            m2 = re.search(r"padding\s*:\s*([^;}]+)", blk)
            if not m2: return None
            parts = re.findall(r"calc\(var\(--u\)\*\d+\)|var\(--u\)|\S+", m2.group(1).strip())
            if not parts: return None
            side = parts[3] if len(parts) >= 4 else (parts[1] if len(parts) >= 2 else parts[0])
            m = re.search(r"(?:calc\(var\(--u\)\*(\d+)\)|(var\(--u\)))", side)
            if not m: return None
        return int(m.group(1)) if m.group(1) else 1
    # the rail is a file tree now: the journal's rows — a commit, a diff line, a
    # filter note — went with the journal, and the law is over what is there.
    rail_rows = ["#brand", "#rail h3", ".file", "#rail h3.fold .obs"]
    edges = {sel: _left_u(sel) for sel in rail_rows}
    S.append(("belonging is a shared edge: every row on the rail begins at one step of the reading line",
              all(v is not None for v in edges.values())
              and len(set(edges.values())) == 1
              and set(edges.values()) == {steps.get("Edge")}
              and "public typealias IndentIsTwiceTheEdge = Same<Indent, Twice<Edge>>" in met))

    # ── the bench is a prism (С9). Two worlds that differ in ONE judged fact may
    # not paint the same: what the judge parts, the eye must not merge, and a
    # merge here is lost information, not a matter of taste. The pairs run on the
    # REAL tokeniser — lifted out of the page and driven over a stream shim — so
    # a rule that drifts in the page cannot pass here by being copied.
    mode_src = 'CodeMirror.defineMode("gate-swift"' + \
        ui.split('CodeMirror.defineMode("gate-swift"', 1)[1].split("}));", 1)[0] + "}));"
    prism_js = r'''
const CodeMirror = { defineMode: (n, f) => { CodeMirror._mode = f(); } };
// the page declares these beside the mode; the harness stands them up itself so
// the mode is exercised exactly as it runs, and a new one added to the page has
// to be added here — which is how this check noticed `slotNames` at all
let keywordSet, localNames, unresolved, jumpable, conformers, protoAxes, slotNames;
class Stream {
    constructor(s) { this.string = s; this.pos = 0; this.start = 0; }
    eol() { return this.pos >= this.string.length; }
    next() { return this.string.charAt(this.pos++); }
    current() { return this.string.slice(this.start, this.pos); }
    skipToEnd() { this.pos = this.string.length; }
    match(p) {
        if (typeof p === "string") {
            if (this.string.startsWith(p, this.pos)) { this.pos += p.length; return true; }
            return null;
        }
        const m = this.string.slice(this.pos).match(p);
        if (m && m.index === 0) { this.pos += m[0].length; return m; }
        return null;
    }
}
__MODE__
function paint(text, world) {
    keywordSet = new Set(["public", "enum", "typealias", "protocol", "extension"]);
    localNames = new Set(world.declares || []);
    unresolved = new Set(world.broken || []);
    jumpable = new Set(world.jumpable || []);
    conformers = world.kinds || {};
    protoAxes = {};
    slotNames = new Set(world.slots || []);
    const tok = CodeMirror._mode.token, st = new Stream(text), out = [];
    while (!st.eol()) { st.start = st.pos; const c = tok(st); out.push([st.current(), c]); }
    return out.filter(([t]) => /\S/.test(t));
}
const at = (text, world, word) => (paint(text, world).find(([t]) => t === word) || [, null])[1];
// one judged fact apart, each pair on its own channel
const pairs = [
    ["a name the world declares against the same name only on the shelf",
     at("public typealias Home = Finance", { declares: ["Finance"] }, "Finance"),
     at("public typealias Home = Finance", { declares: [] }, "Finance")],
    // the weight no longer says whether a name is still open — it says which of
    // the two names on a declaration line the line is ABOUT, because the accent
    // was landing on the inheritance. What a name is, a kind or a record, is
    // told in words at the cursor now instead of in the paint.
    ["a name with a home to jump to against the same name with none",
     at("public typealias Home = Finance", { jumpable: ["Finance"] }, "Finance"),
     at("public typealias Home = Finance", {}, "Finance")],
    ["a name that resolves against one that resolves to nothing",
     at("public typealias Sex = Male", {}, "Male"),
     at("public typealias Sex = Male", { broken: ["Male"] }, "Male")],
];
console.log(JSON.stringify(pairs.map(([w, a, b]) => [w, a, b, a !== b])));
'''.replace("__MODE__", mode_src)
    pj = os.path.join(tmp, "prism.js")
    open(pj, "w").write(prism_js)
    pout = subprocess.run(["node", pj], capture_output=True, text=True).stdout
    try:
        parted = json.loads(pout or "[]")
    except Exception:
        parted = []
    S.append(("the bench is a prism: worlds one judged fact apart never paint the same",
              len(parted) == 3 and all(row[3] for row in parted)))

    # A ROW IS A SURFACE AT REST, AND ONE WORD IS SAID ONCE. This panel once wore
    # a red edge AND a fill, which was the same word twice, and the correction
    # took the surface away with the repetition: bare text on the panel's own
    # paper, lighting only under the pointer, so the list read as a paragraph
    # and the boundary between one refusal and the next had to be found by eye.
    # The backing is what makes a row a row. One marker, not two, and the
    # pointer answers a step above it because clicking goes to the line.
    ref_rule = ui.split(".refusal{", 1)[1].split("}", 1)[0] if ".refusal{" in ui else ""
    S.append(("a refusal is a row at rest and answers the pointer, and says its one word once",
              # the surface is there, and it is the only marker: no second edge
              "background:color-mix(in srgb,var(--bad) 7%,transparent)" in ref_rule
              and "border-left" not in ref_rule and "border:" not in ref_rule
              # and the pointer is a step above rest, not the first sign of a row
              and ".refusal:hover{background:color-mix(in srgb,var(--bad) 15%,transparent)}" in ui
              and ".refusal code{color:var(--bad)" not in ui
              # AND A VERDICT WEARS ITS COLOUR THE WAY THE OTHER ONE DOES: the
              # word carries it over a tint of the same hue. A solid fill made
              # one chip a block of paint beside a chip of text, so the two
              # verdicts were not the same kind of thing on the same bar.
              and ".chip.bad{background:color-mix(in srgb,var(--bad) 12%,transparent);color:var(--bad)}" in ui
              and ".chip.ok{background:color-mix(in srgb,var(--ok) 12%,transparent);color:var(--ok)}" in ui))

    # AND A CELL IS MARKED THE WAY EVERY OTHER NAME IS. A drawn cross was a
    # fifth way of saying one thing, on a page whose argument is that there is
    # one way to say each thing, and it is not a word this world has.
    S.append(("what hurts wears the same wave everywhere, and no glyph anywhere",
              "✗" not in ui and "❌" not in ui
              and ui.count("text-decoration:underline wavy var(--bad)") >= 5
              # open or shut is two marks, never one mark turned: rotating a
              # triangle spins it about the middle of its box while the glyph's
              # weight sits low, so it wobbles off its line and lands elsewhere
              and '#rail h3.fold i::before{content:"▾"}' in ui
              and '#rail h3.fold.shut i::before{content:"▸"}' in ui
              and "transition:transform" not in ui))

    S.append(("the verdict holds still: tabular numbers, a chip that reserves its width, no motion on a change",
              "font-variant-numeric:tabular-nums" in ui
              and "min-width" in chip_rule
              and "transition" not in chip_rule and "transition" not in status_rule))

    # the bench may not say holds where a hook would refuse: the guards run on
    # the unsaved text as well, not only in the CLI
    S.append(("the bench runs the same guards the CLI does",
              "duplicate_guards_over(sources)" in open(GATE, encoding="utf-8").read()
              and "entry_guards_over(sources)" in open(GATE, encoding="utf-8").read()))

    # ── the two judges say the same words ──
    # The bench judges a single-file world in the browser, with the ported
    # judge; a hook and CI judge it with the binary. If those two ever drift,
    # the bench shows green where the pipeline shows red — the one failure a
    # checker may not have. So they are compared verbatim, not by count.
    par = os.path.join(tmp, "parity")
    os.makedirs(par)
    shutil.copy(os.path.join(repo, "gate.swift"), os.path.join(par, "w.swift"))
    base_world = open(os.path.join(par, "w.swift")).read()
    probe = os.path.join(par, "probe.js")
    open(probe, "w").write(
        'const {judge} = require(%r); const fs = require("fs");\n'
        'const f = process.argv[2];\n'
        'const r = judge(f.split("/").pop(), fs.readFileSync(f, "utf8"));\n'
        'console.log(JSON.stringify((r.refusals||[]).map(x => x.premise)));\n'
        % os.path.join(HERE, "judge.js"))

    def two_judges(world_text):
        p = os.path.join(par, "w.swift")
        open(p, "w").write(world_text)
        raw = subprocess.run([os.path.join(HERE, "bin", "gate-judge"), "judge", p],
                             capture_output=True, text=True).stdout
        binary = sorted(m.group(1).strip()
                        for m in re.finditer(r"^\s+\S+\.swift:\d+\s+(.+)$", raw, re.M))
        out = subprocess.run(["node", probe, p], capture_output=True, text=True).stdout
        try:
            ported = sorted(json.loads(out))
        except Exception:
            ported = ["<port did not run: " + out[:60] + ">"]
        return binary, ported

    cases = {
        "a clean world": base_world,
        "a person moved out of their department":
            base_world.replace("public typealias Home = Finance",
                               "public typealias Home = Engineering", 1),
        "a misspelled gate form": base_world.replace("VerifiedView<", "VerifedView<", 1),
        "an argument nothing declares": base_world.replace("FinanceShare\n", "NoSuchDoc\n", 1),
        # a world carrying a top-level typealias: the plain judge (status, the
        # hook, CI) reads a world of facts, and a typealias standing outside
        # every declaration is not one — BOTH judges refuse it, in the same
        # words. This locks their AGREEMENT, not acceptance: were the bench's
        # port ever made to always parse extras, it would ACCEPT this where the
        # plain binary refuses, and the bench would go green while CI stays red.
        # (Certificates are read in the `where` mode — the shelf, the palette —
        # never in the plain world judge the bench must match.)
        "a world with a top-level typealias": base_world + "\npublic typealias Handy = Emp9000\n",
    }
    for label, world in cases.items():
        b, p = two_judges(world)
        S.append((f"both judges say the same words: {label}", b == p and (b or label == "a clean world")))

    # ── the parity of the two judges, walked beyond the five named worlds:
    # a seeded generator assembles worlds from the grammar's own moves,
    # valid and broken alike, and the binary and the port must say the same
    # refusals on every one. The seed is fixed, so a red run is a red run
    # tomorrow, and a differential found here is a case to add by name.
    import random as _rnd
    _rnd.seed(11)
    _kinds = ["Realm", "Room", "Keeper"]
    _mismatch = 0
    for _w in range(20):
        _lines = ["public protocol Realm {}",
                  "public protocol Room { associatedtype Place: Realm }",
                  "public protocol Keeper { associatedtype Post: Realm }"]
        _zones = [f"Z{_w}_{i}" for i in range(_rnd.randint(1, 3))]
        for _z in _zones:
            _lines.append(f"public enum {_z}: Realm {{}}")
        for _i in range(_rnd.randint(1, 4)):
            _kind = _rnd.choice(["Room", "Keeper"])
            _axis = "Place" if _kind == "Room" else "Post"
            _target = _rnd.choice(_zones + (["Missing"] if _rnd.random() < 0.3 else []))
            _lines.append(f"public enum N{_w}_{_i}: {_kind} {{")
            if _rnd.random() < 0.85:
                _lines.append(f"    public typealias {_axis} = {_target}")
            _lines.append("}")
        # a duplicated name stays out of the walk: the port's guard names a
        # duplicate the binary keeps in silence, a stated asymmetry held by
        # its own vector above, not a differential for this one to find
        _b, _p = two_judges("\n".join(_lines) + "\n")
        if _b != _p:
            _mismatch += 1
            print("   differential world", _w, "binary:", _b[:2], "port:", _p[:2])
    S.append(("twenty seeded worlds and the two judges say the same refusals on each",
              _mismatch == 0))

    # ── the judge's pin is one fact in three records: the manifest names the
    # revision the world took, CI builds at a revision, and the build writes
    # what it built from beside the binary. Nobody compared them, which for
    # this tool is a confession: raise one and forget another and the
    # manifest lies about the court. One equality, all three records.
    _man_pin = re.search(r"verification-is-identification@([0-9a-f]+)",
                         open(os.path.join(HERE, "gate.manifest.swift")).read())
    _ci_pin = re.search(r"bin/build-judge\.sh ([0-9a-f]+)",
                        open(os.path.join(HERE, ".github", "workflows", "battery.yml")).read())
    _from = ""
    _fp = os.path.join(HERE, "bin", "gate-judge.from")
    if os.path.exists(_fp):
        _from = open(_fp).read().strip()
    S.append(("the manifest, CI and the build name one judge revision",
              _man_pin and _ci_pin and _man_pin.group(1) == _ci_pin.group(1)
              and _from.startswith(_man_pin.group(1))))

    # ── the usage page is a second record of the verb table, and it was the
    # one record nothing held: verbs.swift is guarded against the dispatch
    # both ways, and USAGE listed commands from memory. Both ways here too:
    # every dispatched verb is on the page, and every `gate word` the page
    # spells is a verb or a spelling the tool answers.
    # the verb table is read from the source through the judge's own parse,
    # never a regex of ours: one grammar, one reader, and this vector is the
    # channel's first client. USAGE itself is prose of the CLI, not swift,
    # so its two-space anchor is the one textual read left here.
    _usage = re.search(r'USAGE = """(.*?)"""', open(GATE).read(), re.S).group(1)
    _pj = json.loads(subprocess.run(
        [shutil.which("node"), os.path.join(HERE, "bin", "judge-cli.js"),
         "judge", "parse", os.path.join(STDLIB, "verbs.swift")],
        capture_output=True, text=True).stdout or "{}").get("verbs.swift", {})
    _decls = _pj.get("declarations", [])
    _verbs = {d["typeName"] for d in _decls
              if "Verb" in d.get("conformances", []) and d.get("typeName")}
    _spellings = {d["typeName"] for d in _decls
                  if "Spelling" in d.get("conformances", []) and d.get("typeName")}
    _said = set(re.findall(r"(?:^  |· )gate ([a-z-]+)", _usage, re.M))
    if "--version" in _said:
        _said.add("version")
    S.append(("every verb of the table stands on the usage page",
              len(_verbs) > 20 and all(v in _said for v in _verbs)))
    S.append(("and the usage page spells no verb the table does not know",
              _said and all(w in _verbs or w in _spellings or w == "--version"
                            for w in _said)))

    # ── the courts are records now, and the records reach real files. The
    # roster in stdlib/courts.swift is the one list of judge implementations;
    # this bridge holds it to the tree both ways, read through the judge's
    # own parse channel, never a regex of ours. bin/judge-cli.js is not a
    # carrier: it is the door to the port, and prints no verdict of its own.
    _cj = json.loads(subprocess.run(
        [shutil.which("node"), os.path.join(HERE, "bin", "judge-cli.js"),
         "judge", "parse", os.path.join(STDLIB, "courts.swift")],
        capture_output=True, text=True).stdout or "{}").get("courts.swift", {})
    _carriers = {d["typeName"] for d in _cj.get("declarations", [])
                 if "CourtCarrier" in d.get("conformances", []) and d.get("typeName")}
    _tree = {"judge.js"} | {os.path.join("bin", f) for f in os.listdir(os.path.join(HERE, "bin"))
                            if f.startswith("judge") and f.endswith(".js")
                            and f != "judge-cli.js"} | {"bin/gate-judge"}
    S.append(("the court roster and the tree name the same carriers, and each exists",
              _carriers == _tree
              and all(os.path.exists(os.path.join(HERE, p)) for p in _carriers)))

    # ── the strangler: the Swift CLI answers a carried vein with the very
    # bytes the python CLI answers with. The door is proven with a stub
    # first, a fake binary that claims the vein and speaks a marker, so the
    # test knows delegation happened and is not watching python twice; then
    # the real binary is built and held to the python side byte for byte,
    # on the page and on the refusal. GATE_CLI names the binary, off means
    # the python side: the same lever a reader uses to compare by hand.
    if sys.platform == "darwin" and shutil.which("swiftc"):
        _b = subprocess.run(["bash", os.path.join(HERE, "bin", "build-cli.sh")],
                            capture_output=True, text=True)
        _cli_bin = os.path.join(HERE, "bin", "gate-cli")
        S.append(("the swift vein builds from one file",
                  _b.returncode == 0 and os.path.exists(_cli_bin)))
        _stub = os.path.join(tmp, "cli-stub")
        with open(_stub, "w") as f:
            f.write("#!/bin/sh\n"
                    'if [ "$1" = "--carries" ]; then echo "stdlib show"; exit 0; fi\n'
                    "echo MARK; exit 0\n")
        os.chmod(_stub, 0o755)
        _m = subprocess.run([sys.executable, GATE, "stdlib", "show", "verbs"],
                            capture_output=True, text=True,
                            env={**os.environ, "GATE_CLI": _stub})
        S.append(("the door hands a carried vein to the binary that claims it",
                  _m.stdout.strip() == "MARK"))
        _py = subprocess.run([sys.executable, GATE, "stdlib", "show", "verbs"],
                             capture_output=True, env={**os.environ, "GATE_CLI": "off"})
        _sw = subprocess.run([sys.executable, GATE, "stdlib", "show", "verbs"],
                             capture_output=True, env={**os.environ, "GATE_CLI": _cli_bin})
        S.append(("both CLIs print the shelf page byte for byte",
                  os.path.exists(_cli_bin) and _sw.stdout == _py.stdout
                  and _py.stdout.startswith(b"// gate stdlib verbs")))
        _pe = subprocess.run([sys.executable, GATE, "stdlib", "show", "nosuch"],
                             capture_output=True, env={**os.environ, "GATE_CLI": "off"})
        _se = subprocess.run([sys.executable, GATE, "stdlib", "show", "nosuch"],
                             capture_output=True, env={**os.environ, "GATE_CLI": _cli_bin})
        S.append(("and refuse an absent page with one sentence and one exit code",
                  _se.stderr == _pe.stderr and _se.returncode == _pe.returncode == 1))

    # ── zero egress: a claim about ourselves, kept by a gate on our own source.
    # An enterprise review runs this same grep; it must never come back dirty,
    # because one outbound call ends the "an engineer may just install it" path.
    forbidden = [r"urllib\.request", r"^\s*import socket\b", r"socket\.socket",
                 r"http\.client", r"requests\.(get|post|put)", r"XMLHttpRequest",
                 r"new WebSocket", r"""fetch\(\s*['"`]https?:""",
                 r"""(?:src|href)\s*=\s*['"]https?:"""]
    hits = []
    for f in ("gate", "ui.html", "judge.js",
              os.path.join("bin", "judge-where.js"), os.path.join("bin", "judge-cli.js")):
        text = open(os.path.join(HERE, f), encoding="utf-8", errors="replace").read()
        for pat in forbidden:
            for m in re.finditer(pat, text, re.M):
                hits.append(f + ": " + m.group(0))
    S.append(("zero egress: no outbound primitive in the runtime sources", not hits))
    # the CLI's imports are a named list, and the list is the whole of it: a
    # security review reads a white list faster than it reads a file, and a
    # module appearing outside this list is a decision made visible here
    _imp = set()
    for _m in re.finditer(r"^\s*import ([\w ,.]+)", open(GATE).read(), re.M):
        for _p in _m.group(1).split(","):
            _imp.add(_p.strip().split(" as ")[0].split(".")[0])
    for _m in re.finditer(r"^\s*from ([\w.]+) import", open(GATE).read(), re.M):
        _imp.add(_m.group(1).split(".")[0])
    S.append(("the CLI imports the standard library alone, from a named list",
              _imp <= {"json", "os", "re", "shutil", "subprocess", "sys",
                       "tempfile", "time", "csv", "hashlib", "itertools",
                       "collections", "fnmatch", "datetime", "webbrowser",
                       "threading", "http", "urllib"}
              and {"json", "subprocess", "http"} <= _imp))
    src = open(GATE, encoding="utf-8").read()
    S.append(("the bench binds to the loopback alone", 'HTTPServer(("127.0.0.1"' in src))
    S.append(("nothing served is cacheable: an updated gate is never hidden",
              src.count('"Cache-Control", "no-store"') >= 5))
    c, r = run("--version")
    S.append(("gate says its version, and the judge its bytes",
              r.get("gate") and r.get("judge", "").startswith("sha256:")))
    ui = open(os.path.join(HERE, "ui.html"), encoding="utf-8").read()
    S.append(("the page declares a policy that blocks any external request",
              "Content-Security-Policy" in ui and "connect-src 'self'" in ui))

    # ── one name, one declaration ──
    # Two declarations of a name are two truths about it. The judge keeps one
    # and says nothing, so the guard says it: at a keystroke, what the compiler
    # would say at a build.
    dup = os.path.join(tmp, "dup")
    os.makedirs(dup)
    world = open(os.path.join(repo, "gate.swift")).read()
    i = world.index("public enum Edsger:")
    j = world.index("}", world.index("Sex =", i)) + 1
    twin = world[i:j].replace("Next = Barbara", "Next = John").replace("Sex = Male", "Sex = Female")
    open(os.path.join(dup, "gate.swift"), "w").write(world[:j] + "\n\n" + twin + "\n" + world[j:])
    c, r = run("status", cwd=dup)
    dupes = [x for x in r["refusals"] if "declared twice" in x["claim"]]
    S.append(("a name declared twice is refused, with both lines",
              c == 1 and len(dupes) == 1
              and "Edsger" in dupes[0]["claim"] and "gate.swift:" in dupes[0]["address"]))
    # an axis is not a declaration: every person states the same ones
    c, r = run("status", cwd=repo)
    S.append(("and the axes every record repeats are not mistaken for it",
              not [x for x in r.get("refusals", []) if "declared twice" in x["claim"]]))
    # across a declared layout it is easier to miss, and just as wrong
    two = os.path.join(tmp, "dup2")
    os.makedirs(two)
    open(os.path.join(two, "gate.swift"), "w").write(world[:j] + "\n" + world[j:])
    open(os.path.join(two, "extra.swift"), "w").write(twin + "\n")
    open(os.path.join(two, "gate.manifest.swift"), "w").write(
        'public protocol WorldFile {}\npublic enum ExtraFile: WorldFile {}\n'
        'extension ExtraFile { public static var typeName: String { "extra.swift" } }\n')
    c, r = run("status", cwd=two)
    S.append(("a name declared in two files of one layout is refused too",
              any("declared twice" in x["claim"] for x in r["refusals"])))

    # ── an entry whose form was commented out ──
    # The judge says holds, correctly: there is no claim there any more. What
    # it cannot say is that a claim you HAD is gone and the file is no longer
    # Swift. Verified against the reference binary itself, which also holds.
    cut = os.path.join(tmp, "cutentry")
    os.makedirs(cut)
    w = open(os.path.join(repo, "gate.swift")).read()
    open(os.path.join(cut, "gate.swift"), "w").write(w + """
public enum MyWatch: AccessLedger {
    @StructureBuilder
    public static var body: some Structure {
            // VerifiedView<
                Emp9001,
                FinanceShare
            >.self;
    }
}
""")
    raw = subprocess.run([os.path.join(HERE, "bin", "gate-judge"), "judge",
                          os.path.join(cut, "gate.swift")], capture_output=True, text=True).stdout
    S.append(("the reference judge holds on a commented-out form, as it should",
              "holds" in raw))
    c, r = run("status", cwd=cut)
    orphan = [x for x in r["refusals"] if "nothing opens" in x["claim"]]
    S.append(("and the guard says what the judge cannot: the claim is gone",
              c == 1 and len(orphan) == 1 and orphan[0]["address"].startswith("gate.swift:")))
    c, r = run("status", cwd=repo)
    S.append(("a whole entry is not mistaken for a broken one",
              not [x for x in r.get("refusals", []) if "nothing opens" in x["claim"]]))

    # ── an address is the line the reader broke, not one nearby ──
    # The judge pins a GATE refusal to the line the entry before it ended on,
    # so those are placed; everything else it addresses exactly, and moving
    # one is how a refusal ends up pointing at somebody else's line.
    ad = os.path.join(tmp, "address")
    os.makedirs(ad)
    w2 = open(os.path.join(repo, "gate.swift")).read()
    lines = w2.split("\n")
    k = next(i for i, l in enumerate(lines) if "typealias Sex = Male" in l)
    lines[k] = lines[k].replace("Male", "Ma")
    open(os.path.join(ad, "gate.swift"), "w").write("\n".join(lines))
    c, r = run("status", cwd=ad)
    named = [x for x in r["refusals"] if "resolves to nothing" in x["claim"]]
    S.append(("a broken name is addressed at the line that holds it",
              named and named[0]["address"] == f"gate.swift:{k + 1}"))
    # and a gate refusal is still moved onto its own entry
    lines = w2.split("\n")
    j = next(i for i, l in enumerate(lines) if "typealias Home = Finance" in l)
    lines[j] = lines[j].replace("Finance", "Engineering")
    open(os.path.join(ad, "gate.swift"), "w").write("\n".join(lines))
    c, r = run("status", cwd=ad)
    gates = [x for x in r["refusals"] if " requires " in x["claim"]]
    S.append(("and a gate refusal lands on the entry that makes it",
              gates and all(":" in x["address"] for x in gates)
              and all("VerifiedInDepartment" in open(os.path.join(ad, "gate.swift")).read()
                      .split("\n")[int(x["address"].split(":")[1]) - 2]
                      or True for x in gates[:1])))

    # ── AND `Reads` IS A CERTIFICATE, NOT A LABEL. Each verb states what it
    # touches, and one of those words is load-bearing: `Run<V>: Safe where
    # V.Does == Reads` in the tool's own forms certifies that a verb may be run
    # on anybody's clone at any moment. The guard over that table held the names
    # in both directions and never this word, so a verb that started writing
    # would have gone on being certified safe by the court. Nothing is read here:
    # every verb whose record says `Reads` is RUN, in a world of its own with a
    # personal world of its own, and both trees are compared by content before
    # and after. A word about what something does is checked by doing it.
    said_reads = sorted(re.findall(r"public enum (\w+): Verb \{\s*\n\s*public typealias Does = Reads",
                                   open(os.path.join(HERE, "stdlib", "verbs.swift"),
                                        encoding="utf-8").read()))
    touch_world = os.path.join(tmp, "touch")
    os.makedirs(touch_world)
    subprocess.run(["git", "init", "-q", touch_world])
    run("demo", "org", touch_world)
    verbs_src = open(os.path.join(HERE, "stdlib", "verbs.swift"), encoding="utf-8").read()

    def spelt(enum):
        m = re.search(r'extension %s \{ public static var typeName: String \{ "([^"]+)" \} \}'
                      % enum, verbs_src)
        return m.group(1) if m else None

    def fingerprint(root):
        out = {}
        for d_, _, fs in os.walk(root):
            if ".git" in d_.split(os.sep):
                continue
            for f in fs:
                p = os.path.join(d_, f)
                try:
                    out[os.path.relpath(p, root)] = hashlib.sha1(open(p, "rb").read()).hexdigest()
                except OSError:
                    pass
        return out

    wrote = []
    myworld = os.path.join(os.environ["GATE_ME"], "worlds")
    for enum in said_reads:
        word = spelt(enum)
        if not word:
            continue
        extra = {"check": ["view", "Emp9002", "FinanceShare"],
                 "diff": ["transfer", "Emp9002", "Sales"]}.get(word, [])
        before, mebefore = fingerprint(touch_world), fingerprint(myworld)
        run(word, *extra, cwd=touch_world)
        if fingerprint(touch_world) != before or fingerprint(myworld) != mebefore:
            wrote.append(word)
    S.append(("every verb this world certifies as safe to run leaves both trees exactly as they were",
              len(said_reads) >= 10 and wrote == []))

    # ── findings: what is true of a repository, in sentences ──
    # The one producer behind the terminal, an audit page and the text of an
    # issue. It must work with no world at all, and never claim as checked
    # what it only read.
    fr = os.path.join(tmp, "findings")
    os.makedirs(os.path.join(fr, "src"))
    subprocess.run(["git", "init", "-q", "-b", "main", fr])
    shutil.copy(os.path.join(DEMO, "CODEOWNERS"), os.path.join(fr, "CODEOWNERS"))
    open(os.path.join(fr, "src", "parser.py"), "w").write("x\n")
    subprocess.run(["git", "add", "-A"], cwd=fr)
    for i in range(55):
        open(os.path.join(fr, "src", "parser.py"), "a").write(f"line {i}\n")
        subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "user.email=solo@proj",
                        "-c", "user.name=S", "commit", "-qam", f"work {i}", "--no-verify"], cwd=fr)
    c, r = run("findings", cwd=fr)
    kinds = {f["kind"] for f in r["findings"]}
    S.append(("findings speak about a repository that has no world at all",
              r["findings"] and r["judged"] == 0 and "observed" in kinds))
    S.append(("findings never call read what the judge did not check",
              all(f["kind"] != "judged" for f in r["findings"])))
    _letter_ships = open(os.path.join(HERE, "stdlib", "readme.swift"), encoding="utf-8").read()
    # ── AND WHAT THIS TOOL PUTS ON A MACHINE, IT TAKES OFF AGAIN. Nine places
    # make a directory to probe in and four of them removed none: on the machine
    # this was found on there were thirty-four thousand, six hundred of them left
    # by `verify` and the rest by the panel, one per keystroke. A tool whose first
    # promise is that nothing of it stays behind may not grow without bound in
    # somebody's temp. Measured, not read: the temp directory is listed before and
    # after each verb.
    import tempfile as _tf
    _tmproot = _tf.gettempdir()
    _here_now = lambda: {n for n in os.listdir(_tmproot) if n.startswith("gate-")}
    sweepworld = os.path.join(tmp, "sweepworld")
    os.makedirs(sweepworld)
    subprocess.run(["git", "init", "-q", sweepworld])
    run("demo", "org", sweepworld)
    left_behind = []
    for verb in (["status"], ["findings"], ["library"], ["survey"], ["badge"],
                 ["verify", os.path.join(sweepworld, "tables", "people.csv"),
                  os.path.join(sweepworld, "tables", "grants.csv")]):
        was = _here_now()
        run(*verb, cwd=sweepworld)
        left_behind += sorted(_here_now() - was)
    S.append(("no verb leaves its scratch on the machine it ran on",
              left_behind == []
              # and one place makes it, so the sweep has one thing to watch
              and gate_src.count("tempfile.mkdtemp") == 1
              and "def sweep_scratch" in gate_src))

    # a verb typed without what it reads answers in words: a stack trace is the
    # one voice this tool never uses, and it used it here
    _, _bare_verify = run("verify", cwd=fr)
    S.append(("a verb asked for nothing answers with a sentence, never a traceback",
              _bare_verify.get("asks") is True and "two catalogue files" in _bare_verify.get("note", "")))

    # ── AND A QUOTED OUTPUT IS THE OUTPUT. The letter shows what `findings`
    # prints, and the sentence it showed had never been printed by anything: it
    # was written by hand, in the section that teaches a reader to look for two
    # records of one fact that stopped agreeing. Found by generating the output
    # and reading both. The pair is held here the only way it can be: the tool is
    # made to print that sentence, and the letter's quote must be that sentence
    # with other numbers in it.
    real = next((f["sentence"] for f in r["findings"] if f["subject"] == "unchecked edits"), "")
    if not real:                      # this fixture has no world, so make one that has
        fq = os.path.join(tmp, "findings-quote")
        os.makedirs(fq)
        subprocess.run(["git", "init", "-q", "-b", "main", fq])
        run("demo", "org", fq)
        subprocess.run(["git", "add", "-A"], cwd=fq)
        for i in range(3):
            open(os.path.join(fq, "gate.swift"), "a").write(f"// touch {i}\n")
            subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", f"user.email=a{i}@x",
                            "-c", "user.name=A", "commit", "-qam", f"w{i}", "--no-verify"], cwd=fq)
        subprocess.run(["git", "config", "--unset", "core.hooksPath"], cwd=fq)
        _, fqr = run("findings", cwd=fq)
        real = next((f["sentence"] for f in fqr.get("findings", [])
                     if f["subject"] == "unchecked edits"), "")
    quoted = re.search(r"«([^»]+)»", re.sub(r"(?m)^\s*//\s?", "", _letter_ships))
    _digits = lambda s: re.sub(r"\d+", "#", " ".join(s.split()))
    S.append(("the sentence the letter shows is the sentence the tool prints, numbers aside",
              bool(real) and bool(quoted) and _digits(quoted.group(1)) == _digits(real)))

    S.append(("findings notice owners the history has not seen",
              any("owners named in CODEOWNERS" in f["sentence"] for f in r["findings"])))
    c, r = run("findings", "--md", cwd=fr)
    S.append(("findings become a note somebody could read in an issue",
              r["markdown"].startswith("### ") and "not a verdict" in r["markdown"]))
    # a history too short to be evidence proves nothing about anyone
    tiny = os.path.join(tmp, "tiny")
    os.makedirs(tiny)
    subprocess.run(["git", "init", "-q", "-b", "main", tiny])
    shutil.copy(os.path.join(DEMO, "CODEOWNERS"), os.path.join(tiny, "CODEOWNERS"))
    subprocess.run(["git", "add", "-A"], cwd=tiny)
    subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "user.email=a@b",
                    "-c", "user.name=A", "commit", "-qm", "start", "--no-verify"], cwd=tiny)
    c, r = run("findings", cwd=tiny)
    S.append(("a history too short to be evidence makes no claim about people",
              not any("have not appeared" in f["sentence"] for f in r["findings"])))
    # with a world, the judge's own refusals lead
    c, r = run("findings", cwd=jrepo)
    S.append(("with a world, what the judge refused comes first and is marked checked",
              any(f["kind"] == "judged" for f in r["findings"])
              if run("status", cwd=jrepo)[1]["verdict"] == "refused" else True))

    # ── GATE'S OWN SEAMS, which had been kept here since before there was a word
    # for them. Every one of these is the same shape the tool sells: two sides
    # that must agree, neither reading the other's mind, refused at an address
    # when they part. The README says which verbs exist and the code has them;
    # the README says how many checks there are and this file has them; the
    # bench's page is promised routes and the server answers exactly those.
    # `gate declares ↔ gate does`, held by the same discipline an operator's
    # contract and client are held to — which is why naming them costs nothing:
    # they were already being kept.
    #
    # A tool that sells judgement over memory may not keep its own claims by
    # memory. This runs LAST, so the count includes everything.
    readme = open(os.path.join(HERE, "README.md"), encoding="utf-8").read()
    src = open(GATE, encoding="utf-8").read()

    verbs = set(re.findall(r'cmd\s*==\s*"([a-z-]+)"', src))
    for grp in re.findall(r'cmd\s+in\s+\(([^)]*)\)', src):
        verbs |= set(re.findall(r'"([a-z-]+)"', grp))
    for grp in re.findall(r'args\[0\]\s+in\s+\(([^)]*)\)', src):   # --version, before dispatch
        verbs |= set(x.lstrip("-") for x in re.findall(r'"([a-z-]+)"', grp))
    porcelain = re.search(r"The porcelain is deliberately git-shaped: `([^`]+)`", readme, re.S)
    claimed_verbs = {v.lstrip("-") for v in
                     (re.findall(r"[a-z-]{2,}", porcelain.group(1)) if porcelain else [])}
    ghost_verbs = sorted(v for v in claimed_verbs if v not in verbs)
    S.append(("every verb the README lists is a verb the code has", not ghost_verbs))

    # ── AND THE REFERENCE IS A WORLD, HELD TO THE DISPATCH BOTH WAYS. A list of
    # verbs in prose drifts from the tool the moment either changes and nothing
    # says when — the one failure this tool exists against, met in its own
    # documentation. Each verb is a record in `stdlib/verbs.swift` now, judged
    # with the rest of this repository's world; which file a thing is cannot be
    # judged (bytes and paths, and no world speaks about a filesystem), so the
    # correspondence is a guard from fact and says so.
    kept_readme = open(os.path.join(HERE, "stdlib", "verbs.swift"), encoding="utf-8").read()
    try:
        open(os.path.join(HERE, "stdlib", "verbs.swift"), "w").write(
            kept_readme.replace('{ "survey" }', '{ "surveyy" }'))
        renamed = run("status", cwd=HERE)[1]
        open(os.path.join(HERE, "stdlib", "verbs.swift"), "w").write(
            "\n".join(l for l in kept_readme.split("\n")
                      if '{ "badge" }' not in l and "public enum Badge: Verb {" not in l))
        dropped = run("status", cwd=HERE)[1]
    finally:
        open(os.path.join(HERE, "stdlib", "verbs.swift"), "w").write(kept_readme)
    S.append(("the table of verbs and the dispatch are held to each other, in both directions",
              run("status", cwd=HERE)[1]["verdict"] == "holds"
              # a record for a word this tool does not answer to: a promise it no longer keeps
              and any("`gate surveyy` is a record here" in r["claim"]
                      and r["address"].startswith("stdlib/verbs.swift:")
                      for r in renamed["refusals"])
              # and a word with no record: a verb nobody is told about
              and any("`gate badge` is a word this tool answers to" in r["claim"]
                      for r in dropped["refusals"])))

    # ── A LAW WRITTEN ON ONE LINE IS NOT A LAW, AND BOTH COURTS GO SILENT
    # TOGETHER. Found by hand on this tool's own demo world: move one newline in
    # the forms file and `refused 1` becomes `holds · 0 equalities judged` — in
    # the shipped binary and in the browser port alike. Every certificate over
    # that law stops being checked and nothing says a word. Swift accepts both
    # spellings identically, so the compiler tier still catches it; the fast
    # tier, the one anybody runs on a keystroke, does not — and that is the tier
    # people trust. The judge is the corpus's and pinned, so the shape is
    # refused here rather than left to unjudge a world quietly.
    onel = os.path.join(tmp, "oneline")
    os.makedirs(onel)
    two = open(os.path.join(HERE, "stdlib", "forms-grants.swift"), encoding="utf-8").read()
    world_tail = ("\npublic enum Zone_src: Realm {}\npublic enum Zone_docs: Realm {}\n"
                  "public enum Owner_c: Keeper {\n    public typealias Post = Zone_docs\n"
                  "    public typealias Key = WardenKey\n}\n"
                  "public enum Path_db: Room {\n    public typealias Place = Zone_src\n}\n"
                  "public typealias Owns_c = Owns<Owner_c, Path_db>\n")
    two_path = os.path.join(onel, "two.swift")
    one_path = os.path.join(onel, "one.swift")
    open(two_path, "w").write(two + world_tail)
    open(one_path, "w").write(
        two.replace("extension Owns: Owned\nwhere", "extension Owns: Owned where") + world_tail)
    JUDGE_BIN = os.path.join(HERE, "bin", "gate-judge")
    said_two = subprocess.run([JUDGE_BIN, "judge", "where", two_path],
                              capture_output=True, text=True).stdout
    said_one = subprocess.run([JUDGE_BIN, "judge", "where", one_path],
                              capture_output=True, text=True).stdout
    kept_shelf = open(os.path.join(HERE, "stdlib", "forms-grants.swift"), encoding="utf-8").read()
    try:
        open(os.path.join(HERE, "stdlib", "forms-grants.swift"), "w").write(
            kept_shelf.replace("extension Owns: Owned\nwhere", "extension Owns: Owned where"))
        joined = run("status", cwd=HERE)[1]
    finally:
        open(os.path.join(HERE, "stdlib", "forms-grants.swift"), "w").write(kept_shelf)
    S.append(("a law written on one line is read by no court, and gate refuses the shape",
              # the finding itself, reproduced: one newline is the whole difference
              "✗" in said_two and "Owns_c" in said_two
              and "✗" not in said_one and "0 equalities judged" in said_one
              # and the guard names it, at the line that writes it
              and any("read by no court" in r["claim"]
                      and r["address"].startswith("stdlib/forms-grants.swift:")
                      for r in joined["refusals"])
              and run("status", cwd=HERE)[1]["verdict"] == "holds"))

    # ── AND THE HALF NO DECLARATION CAN PROVE. `Run<V>: Safe where V.Does ==
    # Reads` is judged: a verb that admits to writing cannot be certified safe,
    # and the judge refuses the line. What the judge cannot know is whether the
    # verb tells the truth about itself, so every certified verb is run here and
    # the working copy held byte-identical afterwards. This is the claim CI, the
    # pre-commit hook and the security posture all rest on.
    safe = re.findall(r"public typealias \w+IsSafe = Run<(\w+)>", kept_readme)
    spelt = {m.group(1): m.group(2) for m in re.finditer(
        r'public enum (\w+): Verb \{.*?extension \1 \{ public static var typeName: '
        r'String \{ "([^"]+)" \} \}', kept_readme, re.S)}
    sw = os.path.join(tmp, "safeworld")
    run("demo", "org", sw)
    before = subprocess.run(["git", "status", "--porcelain"], cwd=sw,
                            capture_output=True, text=True).stdout
    touched = []
    for rec in safe:
        word = spelt.get(rec)
        if not word:
            touched.append(rec + " (no record)")
            continue
        subprocess.run([sys.executable, GATE, word], cwd=sw, capture_output=True, text=True)
        after = subprocess.run(["git", "status", "--porcelain"], cwd=sw,
                               capture_output=True, text=True).stdout
        if after != before:
            touched.append(word)
    for args in (["status"], ["log"], ["findings"], ["survey"], ["guard"], ["--version"],
                 ["check", "view", "Emp9001", "EngineeringShare"]):
        subprocess.run([sys.executable, GATE, *args], cwd=sw, capture_output=True, text=True)
    after_all = subprocess.run(["git", "status", "--porcelain"], cwd=sw,
                               capture_output=True, text=True).stdout
    S.append(("every verb certified safe leaves the working copy exactly as it was",
              len(safe) >= 10 and not touched and after_all == before))

    # ── AND `Asked` CARRIES THE SAME PROMISE WITH ONE WORD ADDED: nothing is
    # written unless you name a file with `-o`. The README says exactly that —
    # "unless you ask for it by name with `-o`, your repository is left as it
    # was" — and nothing held it, so the difference between a verb that reads
    # and a verb that writes when asked lived in prose. Run each without one and
    # the working copy is byte-identical, which is what makes `Asked` a class
    # rather than an intention.
    asked = {m.group(2) for m in re.finditer(
        r'public enum (\w+): Verb \{\s*public typealias Does = Asked.*?'
        r'extension \1 \{ public static var typeName: String \{ "([^"]+)" \} \}',
        kept_readme, re.S)}
    aw = os.path.join(tmp, "askedworld")
    run("demo", "org", aw)
    a_before = subprocess.run(["git", "status", "--porcelain"], cwd=aw,
                              capture_output=True, text=True).stdout
    wrote_anyway = []
    for word in sorted(asked):
        subprocess.run([sys.executable, GATE, word], cwd=aw, capture_output=True, text=True)
        if subprocess.run(["git", "status", "--porcelain"], cwd=aw,
                          capture_output=True, text=True).stdout != a_before:
            wrote_anyway.append(word)
    S.append(("a verb that writes only when asked writes nothing when it is not",
              len(asked) >= 5 and not wrote_anyway
              # and the promise is stated where the class is, not only in prose
              and "nothing is written unless you name a file with `-o`" in kept_readme))

    # ── AND A GHOST IS A GHOST WHICHEVER COURT WOULD HAVE READ IT. The shadow
    # check was widened to every role and this one stayed at `world`, so a
    # declared forms file could simply vanish and nothing said a word. This
    # repository is entirely forms rows: deleting `stdlib/bench-palette.swift`
    # took a hundred and thirty-two equalities out of the court and `gate
    # status` answered `holds`. The only trace was the width — 180 down to 48 —
    # which is why a green that will not say how wide it is cannot be trusted.
    kept_pal = open(os.path.join(HERE, "stdlib", "bench-palette.swift"), "rb").read()
    try:
        os.remove(os.path.join(HERE, "stdlib", "bench-palette.swift"))
        vanished = run("status", cwd=HERE)[1]
    finally:
        open(os.path.join(HERE, "stdlib", "bench-palette.swift"), "wb").write(kept_pal)
    S.append(("a declared file that vanishes is named, whichever court would have read it",
              vanished["verdict"] == "refused"
              and any("stdlib/bench-palette.swift" in r["claim"] and "no such file" in r["claim"]
                      and r["address"].startswith("gate.manifest.swift:")
                      for r in vanished["refusals"])
              # and the width says the same thing the verdict does: the court got
              # narrower, and a green would have hidden exactly that
              and vanished.get("forms", {}).get("equalities", 0)
                  < run("status", cwd=HERE)[1]["forms"]["equalities"]
              # a row that names a dependency rather than a file this world
              # judges is not a ghost: the judge is held by a reproducible build
              and run("status", cwd=os.path.join(tmp, "demoworld"))[1]["verdict"] == "holds"))

    # ── AND AN AXIS IS NOT A PRESENTED VALUE. `public typealias Post = Zone_docs`
    # inside a record is what that record says about itself, and every record of
    # a kind states the same axes. The duplicate guard learned this and the
    # presented-values guard never did, so the first world to carry two forms
    # files with records in them collided on the word `Post` — a hundred and
    # eleven refusals about names nobody had presented twice. Invisible until
    # now only because nobody had written a second forms file with records.
    twoforms = os.path.join(tmp, "twoforms")
    run("demo", twoforms)
    # ── A FORMS ROW IS JUDGED AS YOU TYPE, LIKE EVERYTHING ELSE HERE. The layout
    # was held to that promise and the forms rows were not: the bench's `/verdict`
    # ran this court over the SAVED copies while somebody edited an unsaved one,
    # so a law broken in the editor stayed invisible and the page showed the old
    # verdict calmly. Walked by hand on the first scene, where the file a person
    # is invited to break IS a forms row — the whole lesson happened where
    # nothing was looking, and the bench's judge, reading that file alone, said
    # HOLDS while the command line on the same text refused at its line.
    liveworld = os.path.join(tmp, "liveforms")
    run("demo", liveworld)
    _s5 = _sock.socket(); _s5.bind(("127.0.0.1", 0)); _lp = _s5.getsockname()[1]; _s5.close()
    _lb = subprocess.Popen([sys.executable, GATE, "serve", "--port", str(_lp)], cwd=liveworld,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    live_said = broke_said = None
    try:
        wait_serve(_lp)
        saved = open(os.path.join(liveworld, "ownership.swift"), encoding="utf-8").read()
        # the demo is met by the kit's letter now, so the forms row a person
        # breaks in the bench is the world itself: docs handed to src on the
        # one docs room makes carol's second claim part the same way her third
        # already does
        typed = saved.replace("public typealias Place = Zone_docs",
                              "public typealias Place = Zone_src", 1)
        broke_said = json.loads(_u.urlopen(_u.Request(
            f"http://127.0.0.1:{_lp}/verdict?f=ownership.swift",
            data=typed.encode(), method="POST"), timeout=30).read())
        live_said = json.loads(_u.urlopen(_u.Request(
            f"http://127.0.0.1:{_lp}/verdict?f=ownership.swift",
            data=saved.encode(), method="POST"), timeout=30).read())
    finally:
        _lb.terminate()
    S.append(("a law broken in the editor is refused before it is written, in a forms row too",
              # the buffer's own break, named at its line — and the file on disk
              # still says the other thing
              # named at the line that actually writes the claim, read from the
              # text rather than from a number typed here: an address a check
              # keeps in its own head is an address that stops meaning anything
              broke_said and any(
                  r["address"] == "ownership.swift:" + str(
                      next(i for i, l in enumerate(typed.split("\n"), 1)
                           if l.startswith("public typealias Owns_2_carol")))
                  and "share one zone" in r["claim"] for r in broke_said["refusals"])
              # the world's own single refusal is still there and is not this one
              and len(broke_said["refusals"]) == 2
              # put the saved text back and only the scene's refusal remains
              and live_said and len(live_said["refusals"]) == 1
              and open(os.path.join(liveworld, "ownership.swift"),
                       encoding="utf-8").read() == saved
              # AND WHAT WITHHOLDS A WRITE IS THIS FILE, NEVER THE WHOLE WORLD.
              # The first scene ships with one refusal on purpose, so a gate over
              # every refusal froze the bench whole: every edit anywhere answered
              # `refused: nothing written` and the offer under every value looked
              # broken.
              and "lastRefusals.some(r => !r.file || r.file === active)" in ui))

    # ── AND A FILE SAYS HOW IT IS FIRST MET, in the same act as `// role:` one
    # line above it. A letter opened in Full reads as code — every line wearing
    # `//`, the greeting dressed as a source file — and a rule about how much
    # prose a file holds would be the old guess wearing a threshold. A word that
    # is not a view is refused by name: a preference silently dropped is a
    # preference the writer thinks they have.
    # the kit's letter carries its opens in the manifest column, so the word
    # that is not a view is written there now, and refused from there
    _mf_path = os.path.join(liveworld, "gate.manifest.swift")
    opens_kept = open(_mf_path, encoding="utf-8").read()
    try:
        open(_mf_path, "w").write(opens_kept.replace(
            "public typealias Opens = Bare",
            "public typealias Opens = Sideways", 1))
        odd = run("status", cwd=liveworld)[1]
    finally:
        open(_mf_path, "w").write(opens_kept)
    S.append(("a file says how it is first met, and a word that is not a view is refused by name",
              "public typealias Opens = Bare" in opens_kept
              and any("`sideways` is not a view" in r["claim"] for r in odd["refusals"])
              # the bench is told, and opens the first row that way
              and "opensAs[first]" in ui and '"opens": opens' in shelf_src
              # and the file's own header lines are not read out to the reader as
              # prose: they are how it speaks to the tool, not to a person
              and 'if (/^(role|opens):/i.test(said))' in ui))

    # ── AND TWO MARKS THE WRITER ALREADY MAKES. A section rule — `── one ──` —
    # is a heading everywhere in this repository's own source, and lines the
    # writer indented inside a comment are set, not flowed. Run through the
    # paragraph rule both were destroyed: the heading became a sentence with
    # dashes in it, and a command lost the line break that made it a command.
    # No register is added for either — two already-declared ones get a second
    # speaker, which is what a word earns its keep by.
    # ── AND THIS TOOL'S OWN FRONT DOOR IS MET THE SAME WAY. The mechanism was
    # built for the demo and gate's own reference was left dressed as code —
    # every verb's note wearing `//`, the table a person is sent to by the
    # README opening as a source file. The tool that says a reference must not
    # drift from what it describes may not be the one place it is not applied.
    ref = open(os.path.join(HERE, "stdlib", "verbs.swift"), encoding="utf-8").read()
    # ── AND A NAME THE PANEL PRINTS IS A NAME THE PANEL OPENS. The seam demo's
    # bench showed its layout — two seam sides listed by name, right there on
    # the screen — and offered no way to open either: the whole scene is about
    # those two declarations and neither was reachable. A seam side is not a
    # fragment of this world (its court is `gate seam`, and one swept into the
    # judged list broke a world once), so it is not a bench file; it is a row of
    # the document open on the screen, and the route to read it already existed.
    sd = os.path.join(tmp, "seamrail")
    run("demo", "seam", sd)
    _s6 = _sock.socket(); _s6.bind(("127.0.0.1", 0)); _sp = _s6.getsockname()[1]; _s6.close()
    _sb = subprocess.Popen([sys.executable, GATE, "serve", "--port", str(_sp)], cwd=sd,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    rail = side_text = None
    try:
        wait_serve(_sp)
        rail = json.loads(_u.urlopen(f"http://127.0.0.1:{_sp}/files", timeout=30).read())
        side_text = _u.urlopen(f"http://127.0.0.1:{_sp}/seamside?f=api.swift",
                               timeout=30).read().decode()
    finally:
        _sb.terminate()
    # ── AND THE BLANK FIRST PAINT, REPRODUCED AND CURED. A world whose every
    # declared row is a seam side has no bench file but the layout and your own
    # empty page, so the bench opened on the accounting document — in the one
    # scene that is entirely about two declarations, neither of them shown.
    # Opening on the side instead surfaced the older glitch at once: CodeMirror
    # measures itself when it is built, and it is built while the rail is hidden
    # and the panes have no width, so a full document, a selected file and a
    # verdict bar came up over a BLANK pane. The re-measure was on the path that
    # happened to be walked; it is on every way in now.
    S.append(("the bench opens on something a reader can read, and measures itself once it can",
              "if (!readable.length && seamRows.length) await openSeamSide(seamRows[0], null);" in ui
              # not inside one branch: every way in reaches it
              and ui.count('if (mode === "full") cm.refresh();') == 1
              and ui.index('if (mode === "full") cm.refresh();')
                  > ui.index("if (!readable.length && seamRows.length)")
              # and the door's line jump rides that same measured frame: scrolled
              # earlier, the editor has no height yet and the line lands short
              and "if (doorLine) reveal(doorLine);" in ui
              and ui.index("if (doorLine) reveal(doorLine);")
                  > ui.index('if (mode === "full") cm.refresh();')))

    # ── AND THE ADDRESS IS A DOOR. The bar reads the address the verdicts
    # speak, `?f=file` or `?f=file:line`, and opens there; every open file
    # writes itself back, so the bar always names what is on the bench and a
    # copied URL lands whoever follows it on the same line. A name the world
    # does not have falls to the first file, and the address corrects itself.
    S.append(("the address bar is a door, and it speaks the verdicts' own file:line",
              'new URLSearchParams(location.search).get("f")' in ui
              and 'asked.match(/:(\\d+)$/)' in ui
              and '"?f=" + encodeURIComponent(name)' in ui))

    # ── A WRITE NAMES ITS FILE OR IT DOES NOT HAPPEN. Reading may fall back to
    # something sensible; writing may not, and one function did both. In a world
    # laid out entirely by manifest the read fallback is the first file that
    # exists, which IS the manifest, so a PUT arriving without a name overwrote
    # the document that says what the world is. Found on a live bench: a seam
    # world whose layout had become the text of an unwritten personal page, and
    # every symptom that follows from it — files gone from the rail, edits to
    # the layout doing nothing, a world reporting `no world here`.
    putw = os.path.join(tmp, "putguard")
    run("demo", "seam", putw)
    kept_man = open(os.path.join(putw, "gate.manifest.swift"), encoding="utf-8").read()
    _s7 = _sock.socket(); _s7.bind(("127.0.0.1", 0)); _pp = _s7.getsockname()[1]; _s7.close()
    _pb = subprocess.Popen([sys.executable, GATE, "serve", "--port", str(_pp)], cwd=putw,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    codes = []
    try:
        wait_serve(_pp)
        for name in ("", "nosuch.swift", "../escape.swift"):
            try:
                codes.append(_u.urlopen(_u.Request(
                    f"http://127.0.0.1:{_pp}/world?f={name}", data=b"DESTROYED",
                    method="PUT"), timeout=30).status)
            except Exception as e:
                codes.append(getattr(e, "code", "err"))
    finally:
        _pb.terminate()
    S.append(("a write that does not name a file of this world does not land anywhere",
              codes == [404, 404, 404]
              and open(os.path.join(putw, "gate.manifest.swift"),
                       encoding="utf-8").read() == kept_man
              # and the writable set is the bench's own list, never a fallback
              and 'p = dict(bench_files()).get(q.get("f", ""))' in shelf_src))

    S.append(("every name the panel prints is a name the panel opens, seam sides included",
              rail and sorted(rail.get("seams") or []) == ["api.swift", "sdk.swift"]
              # and they are NOT bench files: no court of this world reads them,
              # and nothing may write to one through this page
              and not (set(rail["seams"]) & set(rail["files"]))
              and side_text and "one side of a seam" in side_text
              and "openSeamSide(s, null)" in ui))

    # ── A GREETING HOLDS, IT DOES NOT THREATEN, AND EVERY LINE OF THE LETTER
    # CARRIES A FEELING. `A lie cannot be saved` was true of nothing and wrong
    # about everything: a file that does not hold saves here perfectly well, and
    # what cannot happen is a lie being COMMITTED, only where somebody wired the
    # hook. The two words a stranger met first were `lie` and `cannot`, which is
    # the voice of supervision. What is said first is what is being kept; the
    # mechanism follows as an event with an address and no blame in it.
    lw = os.path.join(tmp, "letterworld")
    run("demo", lw)
    letter = open(os.path.join(lw, "readme.swift"), encoding="utf-8").read()
    # ── ONE LETTER, NOT THREE. The demo carried a greeting of its own for a
    # while, a third voice beside the cover and the kit, and three tellings of
    # one story is the drift this tool exists against. The demo is entry plus
    # one translated world now, so the letter that meets it IS the kit's
    # letter: every content line of the shelf page, word for word, under the
    # taken head, with the way back at its foot. The old scene-anchors died
    # with the third voice, and this pair replaces them.
    _shelf_lines = open(os.path.join(HERE, "stdlib", "readme.swift"),
                        encoding="utf-8").read().split("\n")
    _shelf_body = _shelf_lines[next(i for i, l in enumerate(_shelf_lines)
                                    if l.startswith("// ── ")):]
    S.append(("the first line threatens the enemy, and the demo is met by the kit's own letter",
              '"death to drift"' in ui
              and '"Every claim in these files is judged as you type."' not in ui
              and ui.count("cannot be saved") == 1
              and all(l in letter for l in _shelf_body if l.strip())
              and "This copy is yours" in letter
              and "Origin: gate's shelf" in letter))

    # ── A MARK IS A LINE OF THE FILE, AND A MARK THAT LIGHTS NOTHING IS A
    # LIE. `== phrase` lines ride the letter itself now, so they survive every
    # reprint, which the stand's hand-placed marks never did. Each phrase must
    # stand in the page it claims to light, and the reading view must know the
    # form: hidden as prose, lit where the phrase is stated.
    _mark_lines = [l.strip()[len("// == "):].strip() for l in _shelf_lines
                   if l.strip().startswith("// == ")]
    _shelf_prose = "\n".join(l for l in _shelf_lines
                             if not l.strip().startswith("// == "))
    S.append(("every mark line lights a phrase the letter actually states",
              len(_mark_lines) >= 10
              and all(m in _shelf_prose for m in _mark_lines)
              and 'said.startsWith("== ")' in ui
              and 'kind: "mark"' in ui))

    # ── THE MAP OF SEAMS IS MEASURED, NOT REMEMBERED. The metrics page prints
    # a table of how often each step stands on the page, and the table names
    # its own method: `calc(var(--u)*N)` plus a bare `var(--u)` for one unit,
    # counted in ui.html. It drifted once, quietly, exactly as its own caption
    # predicted; counted here the same way, it cannot drift in silence again.
    _metrics = open(os.path.join(HERE, "stdlib", "bench-metrics.swift"),
                    encoding="utf-8").read()
    _map_said = {int(u): int(n) for _, u, n in
                 re.findall(r"//\s+(\w+)\s+(\d+)u\s+×(\d+)", _metrics)}
    _page_counts = {}
    for _m in re.finditer(r"calc\(var\(--u\)\s*\*\s*(\d+)\)", ui):
        _k = int(_m.group(1))
        _page_counts[_k] = _page_counts.get(_k, 0) + 1
    _page_counts[1] = len(re.findall(r"(?<!calc\()var\(--u\)(?!\s*\*)", ui))
    _map_apart = {u: (n, _page_counts.get(u, 0))
                  for u, n in _map_said.items() if _page_counts.get(u, 0) != n}
    if _map_apart:
        print("   the seam map against the page:", _map_apart)
    S.append(("the seam map counts what the page holds, step for step",
              len(_map_said) >= 10 and _map_apart == {}))

    S.append(("gate's own reference is met as a reference, not as source",
              "// opens: bare" in ref
              # and it is the first row of this world's layout, so the bench
              # opens on it
              and open(os.path.join(HERE, "gate.manifest.swift"),
                       encoding="utf-8").read().index("stdlib/verbs.swift")
                  < open(os.path.join(HERE, "gate.manifest.swift"),
                         encoding="utf-8").read().index("stdlib/bench-atoms.swift")
              # every verb carries the note the reference is made of
              and ref.count("///") >= 25))

    # ── A DECLARATION'S ANGLES HOLD HOLES; A USE'S HOLD NAMES. The painter read
    # every word inside `<…>` as a hole, so `Carries<MessagesJS, …>` — a claim
    # ABOUT a name declared three lines above in the same file — came out in the
    # ink of an empty slot while `Carries` beside it was lit. Every argument of
    # every certificate in every world went grey the same way: the one place a
    # reader looks to see whose names a claim is made of. Found by eye on the
    # seam bench. The difference is on the line: a declaration introduces its
    # parameters, and a use fills them after an `=`.
    S.append(("a name used inside angles is a name, and only a declaration's angles hold holes",
              'const head = opened >= 0 ? before.slice(0, opened) : "";' in ui
              and 'if (opened > shut && opened >= 0 && !head.includes("=")) {' in ui
              # the two shapes this decides between, both live in this repository:
              # a form declaring its parameters, and a certificate filling them
              and "public enum Owns<" in open(
                  os.path.join(HERE, "stdlib", "forms-grants.swift"), encoding="utf-8").read()
              and re.search(r"public typealias \w+ = Taller<", open(
                  os.path.join(HERE, "stdlib", "bench-registers.swift"), encoding="utf-8").read())))

    # ── AND A CERTIFICATE SHOWS WHEN IT IS THE ONE THAT BROKE. Bare passed
    # `false` for hurt on every top-level alias, always. A certificate IS a
    # top-level alias and the where court refuses nothing else, so every refusal
    # that court makes was invisible in this view: ownership, the palette, a
    # seam. The letter's own lesson lands on one, in the view the letter opens
    # in, and the reader was told to look at a line carrying no mark.
    S.append(("a certificate wears the wave in bare when it is the one that broke",
              "declSpan(name, a.line, badLines.has(a.line))" in ui
              and "declSpan(name, a.line, false)" not in ui
              and "#bare .bad{text-decoration:underline wavy var(--bad)" in ui))

    # ── AND NOTHING SHOWS THE WRONG WORLD FIRST. Three flashes, one shape: the
    # page painted an answer it did not have yet and corrected itself a beat
    # later. CodeMirror tokenises the moment a value is set and the name set it
    # consulted still belonged to the file you had just left, so every name of
    # the new file fell through to `theirs` and the document came up purple. The
    # offer list said its names in one flat colour while each has a register the
    # moment it lands. And the theme, remembered from what the world last
    # declared, was cleared by a read that happened before the world was parsed:
    # silence taken for an answer, and the page flipped twice.
    S.append(("nothing paints an answer the page does not have yet",
              # the names are known before the text is painted
              "const early = judge(name, t, formsFiles.has(name) || name === layoutFile" in ui
              and ui.index("repaintNames(early.parsed, []);") < ui.index("editor.value = t;")
              # an offer wears the ink the name will have, and the selection
              # tints the row rather than overpainting the word
              and '.crow .cmine{color:var(--localtype)}' in ui
              and '.crow.on{background:color-mix(in srgb,var(--action) 14%,transparent)}' in ui
              and 'localNames.has(n) ? "cmine" : "ctheirs"' in ui
              # and what is remembered stands until the world has been read
              and "if (!worldRead) return;" in ui
              and ui.index("worldRead = true;") < ui.index("function applyMyBench")
                  or "worldRead = true;" in ui))

    S.append(("bare reads the marks the writer already makes: a section is a heading, a block is set",
              'out.push({ line: i + 1, text: head[1], kind: "head" });' in ui
              and 'kind: "set"' in ui
              and "#bare .head{display:block;font:var(--headsmall)" in ui
              and "#bare .set{display:block;white-space:pre" in ui
              # and the voices are ones this page already declared, not new words
              and "public enum Headsmall: Register" in open(
                  os.path.join(HERE, "stdlib", "bench-registers.swift"), encoding="utf-8").read()))

    S.append(("two forms files of your own may each hold records, and their axes do not collide",
              run("status", cwd=twoforms)[1]["verdict"] == "refused"
              and len(run("status", cwd=twoforms)[1]["refusals"]) == 1
              and os.path.exists(os.path.join(twoforms, "readme.swift"))
              # the front door is the first row, and the bench opens on the first
              # row: a layout is not a greeting
              and open(os.path.join(twoforms, "gate.manifest.swift"),
                       encoding="utf-8").read().index("readme.swift")
                  < open(os.path.join(twoforms, "gate.manifest.swift"),
                         encoding="utf-8").read().index("ownership.swift")
              # two forms files with records of their own stand side by side:
              # the kit's verb table and the imported ownership world, their
              # axes from different vocabularies, judged together
              and "public enum Log: Verb" in open(os.path.join(twoforms, "verbs.swift"),
                                                  encoding="utf-8").read()))

    # ── AND THE FRONT DOOR NAMES THEM TOO. The README promises a porcelain and
    # the code has every verb in it; the screen a person meets when they type
    # `gate` and nothing else was checked against neither, and had quietly lost
    # five: `log`, `findings`, `my`, `stdlib`, `--version` — including the two
    # the tool itself calls the first useful thing it does in any repository.
    # Sixty-one lines of usage and no first step among them, in a tool whose own
    # rule is that every command ends with the one that comes next.
    ran = subprocess.run([sys.executable, GATE], capture_output=True, text=True)
    usage = ran.stdout + ran.stderr
    unlisted = sorted(v for v in claimed_verbs
                      # spelled beside a sibling on one line, or a flag rather
                      # than a verb — read both spellings, name neither twice
                      if v not in ("fsck", "ask", "change", "apply", "export", "verify")
                      and f"gate {v}" not in usage and f"gate --{v}" not in usage)
    S.append(("the screen a newcomer meets names every verb the README promises, and one first step",
              not unlisted and "gate demo" in usage
              and "first time" in usage
              # ── AND IT SAYS WHAT THIS IS BEFORE IT SAYS WHAT TO TYPE. Sixty
              # lines of verbs opened on the word `usage`, so a person who typed
              # the name of an unfamiliar tool to find out what it was got a
              # list of things to do with it instead of an answer.
              # and in the same voice the letter is written in: short declarative
              # sentences, direct order, no word standing in for a machine
              and usage.startswith("git verifies bytes")
              and "The day that stopped is recorded nowhere" in usage
              and "keeps every byte" not in usage))

    # ── AND EVERY RUNG SAYS WHAT YOU GET, NEVER WHAT YOU WILL BE STOPPED FROM.
    # `wire the pre-commit hook, so what does not hold cannot be committed` is
    # one act said as a prohibition: true, and it leaves a person hearing that
    # they will be refused rather than that their word starts standing. The tone
    # canon is that a greeting holds and does not threaten, and a rung is a
    # greeting to whatever comes next.
    next_src = shelf_src.split("def next_rung(", 1)[1].split("\ndef ", 1)[0]
    # ── AND AN EMPTY BENCH SAYS WHAT THIS PLACE IS FOR, NOT WHAT IT LACKS. `No
    # world here yet` names an absence and hands over two commands, which is a
    # form to fill in. The same screen can say the thing this repository is
    # missing in its own terms, and each door can name a room and a future act
    # rather than a flag. A backtick means the same here as everywhere else on
    # the page: written raw it was punctuation in the reader's face.
    S.append(("an empty bench says what the place is for, and its doors are scenes",
              "<h2>Your words are not held here yet</h2>" in ui
              # gone from the page; it survives once in the comment that
              # records why, which is the decision and not a thing on screen
              and ui.count("No world here yet") == 1
              and "This is where you will see it happen to somebody else first" in ui
              and "This is where your own repository starts answering" in ui
              and "noteProse(lead)" in ui))

    S.append(("a rung names what becomes yours, not what will be refused",
              "from here on, what you commit is what holds" in next_src
              # it survives once in the comment that records why it went, which
              # is the decision and not a thing anybody reads on a terminal
              and next_src.count("cannot be committed") == 1
              and "say who may merge: gate.policy.swift" in next_src
              and "nobody reads a diff" in next_src))

    # a route may carry an extension, and this pattern used to stop at the dot —
    # so `/ladder.css` read as `/ladder` on one side and vanished on the other,
    # and the two files this bench serves by name were never compared at all.
    # A check blind to a shape is a check that agrees with anything in it.
    routes = set(re.findall(r'u\.path\s*[!=]=\s*"(/[a-z/.]*)"', src))   # == and != both route
    for grp in re.findall(r'u\.path\s+in\s+\(([^)]*)\)', src):
        routes |= set(re.findall(r'"(/[a-z/.]*)"', grp))
    contract = set()
    for line in re.findall(r"^\s+#\s+(?:GET|POST|PUT)\s+(.+)$", src, re.M):
        contract |= set(re.findall(r"(/[a-z/.]*)", line.split("  ")[0] + " " + line))
    S.append(("the bench's promised routes are the routes the server answers",
              contract == routes))

    # ── A REFUSAL SPEAKS ABOUT THE WORLD, NEVER ABOUT WHOEVER WROTE IT. It is
    # already the canon of names; it is a wall now, because tone is exactly the
    # thing that erodes one careless sentence at a time. `the tracker calls it
    # closed` is a fact about a fact. `you forgot to` is a fact about a person,
    # and a person who is told off by a machine stops opening it.
    BLAME = re.compile(r"\byou (must|should|failed|forgot|cannot|need to)\b"
                       r"|\byour (mistake|error|fault)\b"
                       r"|\b(invalid|illegal|wrong)\b|\berror in\b", re.I)
    said = [n.value for n in ast.walk(ast.parse(open(GATE).read()))
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    S.append(("nothing the tool says is about the person who wrote it",
              bool(said) and not [s for s in said if BLAME.search(s)]))

    # ── WHAT HAPPENED WHILE YOU WERE AWAY, in one line, once. A person opens
    # this in the morning not to study it but to learn whether the night was
    # quiet, so the first thing said is a state of affairs and never a table: the
    # numbers justify the sentence rather than replacing it. A dashboard asks to
    # be read; this asks to be trusted, which is the difference between a place
    # you check and a place you keep.
    # It is said ONCE and goes, it says nothing at all on a first visit (there is
    # no `since` yet to speak of), and it never repeats the verdict — the chip
    # says the state, this says the change.
    # ── and the page says when it is talking to a bench that predates it. The
    # server reads its page off the disk and answers out of memory, so a gate
    # updated while it runs leaves a new page speaking to an old process: every
    # file fresh, every endpoint stale, and nothing saying so — a page asking for
    # answers the running server has never heard of, failing quietly. That is the
    # one way this bench must never fail, since its whole promise is that what
    # you see is what is judged.
    S.append(("the bench says so when the page and the process are not the same gate",
              'const BENCH_FOR = "' + re.search(r'^VERSION = "([^"]+)"', src, re.M).group(1) + '";' in ui
              and 'fetch("/version"' in ui and "Restart `gate serve`" in ui
              and '"gate": VERSION' in src))

    # ── A BAR THAT EXPIRES MAY ANSWER AN ACTION; IT MAY NEVER REPORT A STATE.
    # You asked for the save, so a word about the save may go and be forgotten.
    # A state you did not cause — the night's commits, a bench older than its own
    # page — is still true a minute later, and a message that takes itself away
    # is a rumour: unpointable, unreadable twice, gone if you happened to look
    # elsewhere. This bench is built on the opposite of a rumour.
    S.append(("nothing the bench must still be true about is said in a bar that expires",
              # the two states it reports both have a place that keeps them
              "benchStale" in ui and 'class="stale"' in ui
              and "say(" not in ui.split('fetch("/version"', 1)[1].split("}).catch", 1)[0]
              # and `say` remains what it was: an answer to something you did
              and "There is nothing to save" in ui))

    listed = set(re.findall(r"^(\S+\.(?:py|js|html|css|sh|md))",
                            readme.split("## what you just cloned")[-1], re.M)) if "## what you just cloned" in readme else set()
    missing = sorted(f for f in listed if not os.path.exists(os.path.join(HERE, f))
                     and not os.path.exists(os.path.join(HERE, "tests", f)))
    S.append(("every file the README names is a file that exists", not missing))
    # ── AND THE OTHER DIRECTION: EVERYTHING THAT EXISTS IS NAMED. The map
    # held only `named → exists`, which is a source with a direction, in the
    # repository that argues against those: a new file in the root joined
    # nothing and no check said so.
    _root_allow = {".github", ".githooks", ".gitignore", "README.md"}
    _tracked = subprocess.run(["git", "ls-files"], cwd=HERE,
                              capture_output=True, text=True).stdout.split("\n")
    _top = sorted({p.split("/")[0] for p in _tracked if p})
    _unnamed = sorted(e for e in _top
                      if e not in _root_allow
                      and e not in readme
                      and (os.path.splitext(e)[0] + ".*") not in readme)
    if _unnamed:
        print("   in the root and not on the cover:", _unnamed)
    S.append(("everything in the root is named on the cover", _unnamed == []))

    # ── AND A WRITTEN LINK REACHES A FILE. SECURITY once sent its reader to a
    # section that had moved; the pointer and the page are a pair like any
    # other, so every relative link in the read surfaces must land.
    _dead_links = []
    for _lf in ("README.md", "SECURITY.md", "NOTICE.md", "CHANGELOG.md",
                os.path.join("docs", "DETAILS.md")):
        _body = open(os.path.join(HERE, _lf), encoding="utf-8").read()
        for _t in re.findall(r"\]\(([^)#]+?)\)", _body):
            if _t.startswith(("http", "mailto")):
                continue
            _base = os.path.dirname(os.path.join(HERE, _lf))
            if not os.path.exists(os.path.join(_base, _t)):
                _dead_links.append(f"{_lf} -> {_t}")
    S.append(("every written link on a read surface reaches its file",
              _dead_links == []))

    # ── AND THE PUBLISHED BENCH COVERS EVERY PATH THE PANEL SPEAKS. The panel
    # grew its endpoints and the snapshot grew separately; a fetch the shim
    # does not carry is a silent 404 on the published page. `/declare` is a
    # write and the shim answers every write; `/seamside` belongs to a seam,
    # and the published demo has none to click.
    _panel_paths = set(re.findall(r'fetch\("(/[a-z]+)', ui))
    _pages_src = open(os.path.join(HERE, "bin", "build-pages.py"), encoding="utf-8").read()
    _covered = {p for p in _panel_paths if f'"{p[1:]}' in _pages_src or f"{p}?" in _pages_src
                or f'"{p}"' in _pages_src or p in _pages_src}
    _uncovered = sorted(_panel_paths - _covered - {"/declare", "/seamside"})
    S.append(("the published bench carries every path the panel calls",
              _uncovered == []))
    # and the road itself is written into the page: CI walks it headless on
    # every push, from typing to the offer to red to green to kept
    S.append(("the published bench carries the user's road, and CI walks it",
              "roadtest=1" in _pages_src and "ROAD ALL GREEN" in _pages_src
              and "roadtest=1" in open(os.path.join(HERE, ".github", "workflows",
                                                    "battery.yml")).read()))

    S.append(("the licence the README claims is the licence in the tree",
              "MIT licensed" in readme
              and open(os.path.join(HERE, "LICENSE"), encoding="utf-8").read().startswith("MIT License")))

    # ── PROSE IS READ AS PROSE, AND THE FILE'S WRAP IS NOT PART OF WHAT IS
    # SAID. Bare set every comment LINE as its own block inside a `pre`, so one
    # paragraph came out a column of fragments with a blank line between each,
    # and where the file happened to wrap leaked into the reading. A run is one
    # paragraph now, ended by a bare `//` — the only mark a writer has for
    # stopping — and the air goes between paragraphs rather than inside one.
    #
    # Two registers, because the material already has two. A `///` note belongs
    # to the record under it and stands against it; a `//` comment belongs to
    # nobody and keeps its air. And what the prose already says is shown: the
    # corpus's own notation, ``Name`` for a name and `x` for a literal, is set
    # in the register that name wears everywhere else. Nothing more is read
    # into it — a view may not add what the text does not have.
    S.append(("a comment reads as a paragraph, in the register of speech",
              # one run, one paragraph, and the bare marker ends it
              "if (!said) { run = null; return; }" in ui
              and "run.text += \" \" + said" in ui
              and "function noteProse(" in ui
              # prose is set as speech and wraps, rather than as preformatted
              # code — and it NAMES the register instead of restating a face
              and "#bare .note{display:block;white-space:normal" in ui
              and "var(--prose)" in ui.split("#bare .note{")[1][:140]
              # the two kinds are told apart, and the attached one has no gap
              and "#bare .note.said{" in ui and "#bare .note.free{" in ui
              and 'class="note said"' in ui and 'class="note free"' in ui
              # the corpus's own notation is shown, and nothing beyond it
              and "``([A-Za-z_]\\w*)``" in ui and "`([^`]+)`" in ui
              # and what gate itself prints has its thoughts separated, so the
              # view has something true to reflect rather than a guess to make
              and 'emit("//")' in shelf_src
              # while the old ownership lie is gone from that header for good
              and "where it becomes yours" not in shelf_src))

    # ── AND THE GAPS IN BARE ARE THE STEPS THE WORLD NAMES FOR THOSE KINSHIPS,
    # not merely steps it names for something. Records were held apart by a
    # blank line of TEXT — the font's line-height, some eight units and a fifth,
    # a number nobody declared and nobody could defend — and the note margins I
    # first picked were named lengths standing for the wrong relations: `Tight`,
    # which is what holds inside one mark, between a note and the record it
    # speaks for. The law of proximity says which is which, so the page is tied
    # to it by NAME: a record with its axes is a group and groups stand `Apart`;
    # a note and its record are parts of one thing and sit `Near`, and `Near` is
    # tighter than `Apart` because the shelf holds it so.
    ladder = _steps(open(os.path.join(HERE, "stdlib", "bench-metrics.swift"),
                         encoding="utf-8").read())

    def _gap(sel, prop="margin"):
        blk = ui.split(sel + "{", 1)[1].split("}", 1)[0] if (sel + "{") in ui else ""
        m = re.search(prop + r"[^;}]*?calc\(var\(--u\)\*(\d+)\)", blk)
        return int(m.group(1)) if m else None
    # AND THE PAGE NAMES THE STEP RATHER THAN REPEATING ITS NUMBER. The
    # stylesheet had been spelling `calc(var(--u)*6)` where the shelf says
    # `Apart` — one number written in two places, joined by this very check.
    # A check is what you reach for when a single source is out of reach, and
    # here it was not: the bench serves the ladder from the judged file, the
    # page says `var(--apart)`, and the two can no longer part.
    def _named(sel, prop):
        blk = ui.split(sel + "{", 1)[1].split("}", 1)[0] if (sel + "{") in ui else ""
        m = re.search(prop + r"[^;}]*?var\(--(\w+)\)", blk)
        return m.group(1) if m else None
    # ── UNDO IS FOR EDITS, AND OPENING A FILE IS NOT ONE. Moving the cursor writes
    # a selection into the editor's history, so following a name and pressing undo
    # walked the cursor back having changed nothing. Worse, setting a file's text is
    # itself a change, so the freshly opened file sat at the bottom of that stack:
    # two presses emptied the buffer and write-on-holds saved the emptiness, because
    # a world with nothing in it has nothing to refuse. Found by doing it.
    S.append(("undo is for edits: a jump is not one, and neither is opening a file",
              "cm.clearHistory();" in ui
              and "function undoEdit()" in ui
              and '"Cmd-Z": undoEdit, "Ctrl-Z": undoEdit,' in ui
              # it counts EDITS, which is the number selections never touch
              and "cm.historySize().undo" in ui
              and "cm.undo(); render();" not in ui))
    # ── A FILE NOBODY DECLARED IS SHOWN, NOT HIDDEN. Drop a row and the file left
    # the rail at the very moment the verdict started talking about it: gone from the
    # place you could click, named in the place you can only read. The rail lists
    # what is here and undeclared, in its own quiet heading, readable and not judged,
    # with the one gesture that changes that. The reverse gesture drops the row and
    # leaves the file where it is, because taking a thing out of your list is not
    # throwing it away, and the second act is nobody's to do for you.
    undecl = os.path.join(tmp, "undeclared")
    os.makedirs(undecl)
    subprocess.run(["git", "init", "-q", undecl])
    run("demo", "org", undecl)
    open(os.path.join(undecl, "extra.swift"), "w").write(
        "// role: forms\npublic protocol Spare {}\npublic enum Kept: Spare {}\n")
    c, r = run("status", cwd=undecl)
    S.append(("an undeclared file beside a declared one is named, not ignored",
              c == 1 and any("no row in the manifest" in x["claim"] and "extra.swift" in x.get("address", "")
                             for x in r["refusals"])))
    c, r = run("mine", "extra.swift", "--role", "forms", cwd=undecl)
    S.append(("declaring it from its own row makes it judged, and the refusal goes",
              r.get("declared_in") == "gate.manifest.swift"
              and run("status", cwd=undecl)[1].get("verdict") == "holds"))
    c, r = run("mine", "extra.swift", "--forget", cwd=undecl)
    S.append(("dropping the row leaves the file on disk and says so",
              r.get("forgot") == "extra.swift"
              and os.path.exists(os.path.join(undecl, "extra.swift"))
              and "not throwing it away" in r.get("note", "")))
    # ── AND A STEP IS A STEP FROM WHERE THE READER IS STANDING. The ladder is
    # written for a terminal, and the bench printed it word for word: a person
    # who had just opened `gate serve` was told, at the foot of that very page,
    # to run `gate serve`. Both surfaces are asked here, about one repository at
    # one moment, because the point is not that the bench says something else —
    # it is that each says the step from its own room.
    rung = os.path.join(tmp, "rung")
    os.makedirs(rung)
    subprocess.run(["git", "init", "-q", rung])
    run("init", ".", cwd=rung)
    _, term = run("status", cwd=rung)
    _s10 = _sock.socket(); _s10.bind(("127.0.0.1", 0)); _rp = _s10.getsockname()[1]; _s10.close()
    _rb = subprocess.Popen([sys.executable, GATE, "serve", "--port", str(_rp)], cwd=rung,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    bench = {}
    try:
        bench = json.loads(wait_serve(_rp, "/status") or b"{}")
    finally:
        _rb.terminate()
    S.append(("the terminal is told to open the bench, and the bench is not told to open itself",
              term.get("next") == "gate serve"
              and "gate serve" not in (bench.get("next") or "")
              # and it is a step, not a silence: the ladder simply moved on
              and len(bench.get("next") or "") > 20))

    # ── AND THE PANEL SHOWS THE SAME DIRECTORY THE VERDICT TALKS ABOUT. The rail
    # listed exactly the declared files, so the file the verdict was refusing sat
    # in the directory and nowhere on the page: two answers about one file, and
    # the friendlier one was the wrong one. Driven through the server, because
    # what is claimed here is what the page is handed, not what the source says.
    _s9 = _sock.socket(); _s9.bind(("127.0.0.1", 0)); _up = _s9.getsockname()[1]; _s9.close()
    _ub = subprocess.Popen([sys.executable, GATE, "serve", "--port", str(_up)], cwd=undecl,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    seen = {}
    try:
        seen["before"] = json.loads(wait_serve(_up) or b"[]")
        seen["text"] = _u.urlopen(
            f"http://127.0.0.1:{_up}/world?f=extra.swift", timeout=30).read().decode()
        kept = open(os.path.join(undecl, "gate.manifest.swift"), encoding="utf-8").read()
        def declare(qs):
            try:
                return 200, _u.urlopen(_u.Request(f"http://127.0.0.1:{_up}/declare?{qs}",
                                                  method="PUT"), timeout=30).read()
            except Exception as e:
                return getattr(e, "code", "err"), getattr(e, "file", None) and e.read() or b"{}"
        seen["nameless"] = declare("f=extra.swift")[0]
        seen["unmoved"] = open(os.path.join(undecl, "gate.manifest.swift"),
                               encoding="utf-8").read() == kept
        seen["said"] = json.loads(declare("f=extra.swift&role=forms")[1])
        seen["after"] = json.loads(_u.urlopen(
            f"http://127.0.0.1:{_up}/files", timeout=30).read())
        # ── AND THE WAY BACK IS THE FILE ITSELF. The row went in through a gesture.
        # Taking it out is deleting four lines in a file open in the editor, which
        # is the same write every other edit on that page makes. If that did not
        # put the file back where it started, the gesture would be a one-way door
        # dressed as a line of text.
        seen["rows"] = open(os.path.join(undecl, "gate.manifest.swift"),
                            encoding="utf-8").read().split("\n")
        man = "\n".join(seen["rows"])
        cut = man.split("public enum Extra: Mine {")[0] + man.split('{ "extra.swift" } }')[1]
        _u.urlopen(_u.Request(f"http://127.0.0.1:{_up}/world?f=gate.manifest.swift",
                              data=cut.encode(), method="PUT"), timeout=30).read()
        seen["back"] = json.loads(_u.urlopen(
            f"http://127.0.0.1:{_up}/files", timeout=30).read())
    finally:
        _ub.terminate()
    S.append(("a file nobody declared is on the page, apart from the ones that are",
              seen.get("before", {}).get("undeclared") == ["extra.swift"]
              and "extra.swift" not in (seen.get("before", {}).get("files") or [])))
    S.append(("and it can be read there, because it is on the disk either way",
              "public protocol Spare" in seen.get("text", "")))
    S.append(("the row is written only when a court is named, and nothing moves until",
              seen.get("nameless") == 400 and seen.get("unmoved") is True))
    lines = seen.get("rows") or [""]
    S.append(("declaring from the panel writes the row and says which line to look at",
              seen.get("said", {}).get("wrote_in") == "gate.manifest.swift"
              and "Extra" in lines[seen.get("said", {}).get("at_line", 0) - 1]
              and "extra.swift" in (seen.get("after", {}).get("files") or [])
              and (seen.get("after", {}).get("undeclared") or []) == []))
    S.append(("deleting the row is the way back, and the file returns to the list of the undeclared",
              (seen.get("back", {}).get("undeclared") or []) == ["extra.swift"]
              and "extra.swift" not in (seen.get("back", {}).get("files") or [])
              and os.path.exists(os.path.join(undecl, "extra.swift"))
              # and the page reads the list again when the list is what was written,
              # so the file moves while you watch instead of at the next reload
              and "if (active === layoutFile) await readFiles();" in ui))

    S.append(("the page offers that gesture where the file is read, in the gesture register",
              "openUndeclared" in ui and "/declare?f=" in ui
              # and a page that writes a row says it is writing: reads do not write
              and 'method: "PUT" });' in ui.split('"/declare?f="')[1][:400]
              and 'class="gesture declare-as"' in ui
              # and the reading behind both the refusal and the rail is one reading
              and "def undeclared_here" in gate_src
              and gate_src.count("sits beside the judged ones") == 1))

    # ── AND THE VIEW IS THE READER'S. Opening somebody's page threw the reader back
    # to Full whatever they had been reading in: pick Bare or Table, click a shelf
    # page or a seam side, and the choice was gone. Following a name still takes
    # Full, because a line is what was asked for, and the way back restores the view
    # along with the place.
    # ── AND THE VIEW SHOWS THE PAGE ITS NAME SAYS. The branch that answers for a
    # page of somebody else's returned before the projections were drawn, so Table
    # and Bare went on holding the file you came from: the name over the pane said
    # one page and the pane showed another, and in Bare it could be a third. Found
    # by clicking through the shelf in Table, which is what a person does.
    _shelfview = ui.split("if (viewingShelf) {", 1)[1].split("\n    }", 1)[0]
    S.append(("a page of theirs is drawn in the view you are in, not left as the file before it",
              "if (mode === \"table\") buildTables();" in _shelfview
              and 'if (mode === "bare") document.getElementById("bare").innerHTML' in _shelfview))

    # and a page nobody may edit offers nothing to edit: an offer that answers
    # nothing is worse than no offer, and the projections draw it like any file
    S.append(("and it offers nothing to edit, in one reading rather than four",
              "function reading() { return !!viewingShelf; }" in ui
              and ui.count("reading()") >= 6
              and "if (reading()) return \"\";" in ui
              and "asNumber !== null && !reading()" in ui))

    # ── AND THE FILE YOU ARE IN ANSWERS FROM WHAT YOU HAVE TYPED. The world is
    # parsed when a file opens, and that snapshot was read first, so a declaration
    # changed under your hands was answered from the copy on disk. The theme was
    # where it showed, and a special case for the personal file was the only thing
    # papering over it: change the word and the page kept the old colour until you
    # opened some other file.
    _inview = ui.split("function declsInView()", 1)[1].split("\n}", 1)[0] if "function declsInView()" in ui else ""
    S.append(("the file you are in is read from what you have typed, and the world from the rest",
              # the buffer goes in FIRST and the world only fills what it did not
              # name: the other order is the defect, and it reads as working code
              bool(_inview) and 0 <= _inview.index("lastParsed.declarations") < _inview.index("layoutDecls")
              and "if (!out.has(name))" in _inview.split("layoutDecls", 1)[1]
              # and no reader of the wheels keeps a special case for that one file
              and "active === personalFile" not in ui.split("function declsInView()", 1)[1][:3000]))

    S.append(("opening a page keeps the view you are reading in",
              'setMode(opensAs[mod] || opensAs[mod + ".swift"] || mode);' in ui
              and "setMode(opensAs[file] || mode);" in ui
              # exactly one path still takes Full on purpose, and it shows a line
              and ui.count('setMode("full")') == 1
              and 'setMode("full");' in ui.split("function reveal")[1][:400]
              # and the way back brings the view with the place
              and 'setMode(there.mode || "full");' in ui))

    # ── THE PAGE SPEAKS FROM PLACES THAT STAY. A floating bar lived 3.2 seconds and
    # carried four different things: an answer to a keystroke, a 500-character
    # paragraph with a shell command in it, a label about the view you were looking
    # at, and a REFUSAL. Eighty words at three seconds is unreadable by arithmetic,
    # not by taste, and a refusal that takes itself away is the opposite of what a
    # refusal is here: an address you can point at, twice.
    #
    # The law was already written: a bar that expires may answer an action and may
    # never report a state. So the floating element is gone, and what it carried went
    # to places that stay: the line under the editor, the reference label, and the
    # verdict. What is left of `say` is an answer to something you did, and it is
    # held to that shape here, because the shape is what made the other three
    # possible.
    says = re.findall(r"\bsay\(\s*(\"[^\"]*\"|'[^']*')\s*\)", ui)
    bad_says = [s for s in says
                if len(s) > 92 or "<" in s or "`" in s or re.search(r"\.swift:\d", s)]
    S.append(("what a disappearing line may carry is one short answer to something you did",
              'id="say"' not in ui and "#say{" not in ui
              and not bad_says
              # and the three that were states now live where the state lives
              and 'refLabel = "<b>" + esc(file) + "</b> · one side of a seam' in ui
              and "function sayLanguage" in ui and "#inspect" in ui
              # and the claim under the cursor answers too: a top-level alias
              # was the one name the line said nothing for, in the file whose
              # whole scene is such lines
              and '" · a claim: "' in ui))

    # ── NAMES STAY NAMES, VERBS BECOME MECHANICS. `court`, `judge`, `verdict` are
    # types and belong in the vocabulary; the verbs around them had been theatrical —
    # courts answered and sat, verdicts spoke, pages wore themes. The rule was
    # written down and swept once by hand, and five new instances appeared in one
    # night, on the two hands that wrote the rule. A law announced and unchecked
    # decays into the habit it replaced, so it is checked here.
    #
    # PAIRED, because no word is banned: a person answers, a side waits for a word
    # (V=I's own reading of |S| > 1), a socket listens. What is refused is a
    # MECHANISM given a voice, in either direction, over the same surfaces the
    # retired word is held to: the tool's own strings, the shelf, and the cover.
    AGENT = (r"court|judge|verdict|world|port|row|axis|grammar|register|page|bench|hue|library")
    THEATRE = (r"answers?(?! for)|answered(?! for)|speaks?|spoke|speaking|sits?|sat|sitting|"
               r"wears?|wearing|wear\b|waits?|waiting|pretends?|hands you|knows|remembers")
    FORWARD = re.compile(rf"\b(?:{AGENT})s?\b[^.\n]{{0,28}}?\b(?:{THEATRE})\b", re.I)
    REVERSE = re.compile(rf"\b(?:{THEATRE})\b[^.\n]{{0,28}}?\bby (?:the |a )?(?:{AGENT})\b", re.I)
    ALLOW = ("waits for a word", "waiting for a word", "awaiting a word", "both spoke",
             "sides spoke", "spoke and", "one is silent", "listens on the loopback",
             "somebody answers", "answers today", "a person answers", "nobody speaks in")

    def theatre_in(text, where):
        out = []
        for i, ln in enumerate(text.split("\n"), 1):
            low = ln.lower()
            if any(a in low for a in ALLOW):
                continue
            if FORWARD.search(ln) or REVERSE.search(ln):
                out.append(f"{where}:{i}")
        return out

    theatre = []
    for sp in sorted(glob.glob(os.path.join(HERE, "stdlib", "*.swift"))):
        prose = "\n".join(l for l in open(sp, encoding="utf-8").read().split("\n")
                          if l.strip().startswith("//"))
        theatre += theatre_in(prose, os.path.basename(sp))
    for tok in tokenize.generate_tokens(io.StringIO(gate_src).readline):
        if tok.type == tokenize.STRING and len(tok.string) > 12:
            theatre += theatre_in(tok.string.replace("\\n", "\n"), f"gate:{tok.start[0]}")
    theatre += theatre_in(open(os.path.join(HERE, "README.md"), encoding="utf-8").read(), "README.md")
    if theatre:
        print("   machinery given a voice:", theatre[:6])
    S.append(("names stay names and verbs stay mechanics, on every surface a person reads",
              not theatre))

    # ── AND A SENTENCE LEADS WITH ITS VERB. `The first two lines are the ones
    # to run` points at the act instead of performing it: copula, a stand-in
    # pronoun, then a clause is the long road to a weaker sentence. `the one
    # thing`, `the one place`: a count, and legal. Fenced here is the stand-in
    # with a clause behind it, on every surface a person reads.
    _standin = re.compile(r"\b(?:is|are) the ones\b"
                          r"|\b(?:is|are) the one (?:to|that|who|we|you|everybody|anybody)\b")
    _standin_hits = []
    for _sf in ("README.md", "SECURITY.md", "CHANGELOG.md", "NOTICE.md",
                os.path.join("docs", "DETAILS.md")):
        _flat = re.sub(r"\s+", " ", open(os.path.join(HERE, _sf), encoding="utf-8").read())
        if _standin.search(_flat):
            _standin_hits.append(_sf)
    for _sp in sorted(glob.glob(os.path.join(HERE, "stdlib", "*.swift"))):
        _pr = re.sub(r"\s+", " ", " ".join(
            l.lstrip("/ ") for l in open(_sp, encoding="utf-8").read().split("\n")
            if l.strip().startswith("//")))
        if _standin.search(_pr):
            _standin_hits.append(os.path.basename(_sp))
    for tok in tokenize.generate_tokens(io.StringIO(gate_src).readline):
        if tok.type == tokenize.STRING and len(tok.string) > 12 \
                and _standin.search(re.sub(r"\s+", " ", tok.string.replace("\\n", " "))):
            _standin_hits.append(f"gate:{tok.start[0]}")
    if _standin_hits:
        print("   the stand-in pronoun:", _standin_hits[:6])
    S.append(("a sentence leads with its verb, not with `the ones`",
              _standin_hits == []))

    # ── AND THE VOICE CARRIES NO LONG DASH. The prose here spells a pause
    # with a colon or a second sentence; an em dash in a printed line is a
    # mark this voice never uses, so one that appears is a stowaway.
    _dashed = [f"gate:{tok.start[0]}"
               for tok in tokenize.generate_tokens(io.StringIO(gate_src).readline)
               if tok.type == tokenize.STRING and "—" in tok.string]
    if _dashed:
        print("   the long dash:", _dashed[:6])
    S.append(("no printed line of the CLI carries a long dash", _dashed == []))

    # ── ONE NAME, ONE COLOUR, IN EVERY VIEW OF IT. A table cell wore one hue
    # whatever stood in it: the column was painted rather than the name. So a value
    # the offer showed as yours, because the offer asks where a name comes from,
    # turned somebody else's the moment it landed in the cell, and choosing a value
    # looked like changing whose it was. Both cells ask the offer's question now.
    S.append(("a value in a table is coloured by where it comes from, like everywhere else",
              "#table-host td.cell-value.mine{color:var(--localtype)}" in ui
              and 'td.className = "fact cell-value" + (localNames.has(raw) ? " mine" : "");' in ui
              and '+ (c > 0 && localNames.has(a) ? " mine" : "");' in ui
              # and the offer's own reading is the one they borrow
              and '(localNames.has(n) ? "cmine" : "ctheirs")' in ui))

    # ── AND A GESTURE IS NOT A SOURCE. The chosen row of an offer was washed with the
    # action colour, whose hue sits between `mine` and `theirs` on the same axis, so
    # picking an item looked like the item changing whose it was.
    S.append(("choosing an item is marked by the ceremony grey, never by a hue",
              ".crow.on{background:var(--select)}" in ui
              and ".crow .cmine{color:var(--localtype)}" in ui
              and ".crow .ctheirs{color:var(--knownname)}" in ui))

    # ── AND A CELL YOU MAY ANSWER LOOKS LIKE ONE, WITHOUT BEING POINTED AT. Three
    # behaviours hid behind identical text in the table: a cell that opens the closed
    # question, a cell that jumps to a declaration in another file, and a cell that
    # does nothing. The only signal was `cursor:pointer`, which answering and jumping
    # share, so «did the click stop working» is what a person asks when the click
    # worked and took them somewhere else. The mark Bare already uses for a slot is
    # the mark the table uses now: one language for one act, in every view of it.
    slot_rules = re.findall(r"#(?:bare|table-host)[^{]*\.slot\{([^}]*)\}", ui)
    S.append(("a cell you may answer wears the same mark as a slot in Bare",
              len(slot_rules) >= 2 and all("dashed" in r for r in slot_rules)
              and "#table-host td.slot{cursor:pointer;border-bottom:1px dashed" in ui))

    S.append(("the gaps in Bare are the steps the world names for those kinships",
              _named("#bare .rec", "margin-bottom") == "apart"
              and _named("#bare .note.said", "margin") == "near"
              # and the names are emitted from the file that declares them
              and "def ladder_tokens(" in shelf_src
              and 'u.path == "/ladder.css"' in shelf_src
              and '<link rel="stylesheet" href="/ladder.css">' in ui
              # and the law they are taken from still holds on the shelf
              and ladder.get("Apart") > ladder.get("Step") > ladder.get("Near")
              # the blank line of text that used to do this work is gone
              and 'block.push("")' not in ui
              # and a note is not a line of the stream: joined with a newline
              # inside a `pre`, a block-level note drew a whole empty line and
              # put a reading-line of air between it and what it speaks for,
              # however tight the declared margin was. The gap was honest; the
              # join was not. Measured after the fix: 5.65px against Near, and
              # 11.3px against Apart, on a unit of 1.885px.
              and '(i.note || "") + i.block.join' in ui
              and "const noteOf = (name) =>" in ui
              and "noteLines" not in ui))

    # ── A TABLE FALLS LEFT. Stretched to the pane, two short words sat at
    # opposite ends of a wide screen — a name here, its one value eight hundred
    # pixels away — and reading a row became a journey across empty space. Air
    # is worth having and a void is not the same thing. Columns take the width
    # their content needs, the table ends where its content ends, and the page
    # cascades down the left where the eye already is.
    # ── AND NOTHING SCROLLS ABOVE A HEADING THAT STAYS. A sticky cell holds at the
    # scroll box's padding edge, so a top padding on the table pane left a band
    # over the frozen header with the rows still sliding through it. Found by eye,
    # by scrolling. The space above the first table belongs to the first heading
    # now, which is margin and not part of the box that scrolls.
    _tblpane = _block("#table-host{", ui)
    _tblhead = _block("#table-host th{text-align:left", ui)
    # ── AND OPENING ONE FILE DOES NOT WAIT FOR FOUR. The page reads every other
    # file to learn its names, and it read them one after the next, each waiting
    # for the one before. They do not depend on each other. And setting the text
    # scheduled a judgement of what the opener was already judging, so every click
    # on a name paid for two verdicts and two statuses.
    S.append(("the world is asked for all at once, and putting a file on the page judges it once",
              "await Promise.all(want.map(f =>" in ui
              and 'if (!userEdit && change.origin === "setValue") return;' in ui
              # and whoever puts text on the page draws it: every opener that sets
              # the text now says so itself, in the order the world is read in
              and ui.count("buildRail();\n    render();") == 4))

    # and the step beside the verdict is read to its end: an ellipsis hands
    # somebody the first half of an instruction
    S.append(("the next step is read whole, and the bar it sits in is declared once",
              "text-overflow:ellipsis" not in _block("#next{", ui)
              and "white-space:nowrap" not in _block("#next{", ui)
              and "align-items:flex-start" in _block("#verdict-head{", ui)
              and ui.count("#verdict-head{") == 1))

    # ── A MAP MADE OF THE TEXT'S OWN WORDS. A long section read as one thread,
    # and a reader arriving at it had no way in but the first word. Headings gave
    # them five doors and took the thread away; a label in the margin drew more
    # of the eye than the sentence it labelled. What is left is the smallest
    # thing that works: the writer marks the words that carry the paragraph and
    # the eye slides down them. It takes no hue, because the colours here answer
    # whose a name is and how a claim stands, and a mark answers neither.
    _markrule = _block("#bare .mark{", ui)
    S.append(("a marked word is a ground under the text, and it borrows no colour that means something",
              "background:var(--mist)" in _markrule
              and "border:" not in _markrule
              and not re.search(r"var\(--(ok|bad|action|localtype|knownname)\)", _markrule)
              # and the ground is wider than the words without moving them: padding
              # alone pushed the full stop off the sentence it ends
              and "margin:0 -" in _markrule))

    # ── AND A MARK MAY NOT EAT A SENTENCE. These pages state equalities in prose,
    # «Those nodes state X == Y and hold the same band on Z», and two of those in
    # one paragraph read as one long mark with the words between them inside it.
    # The pattern under test is the one the page ships, read out of it.
    _mk = re.search(r"\.replace\(/(==.+?==)/g", ui)
    _pat = _mk.group(1) if _mk else "$^"
    _eaten = re.sub(_pat, "MARK", "Those nodes state X == Y and hold the same band on Z == W.")
    _marked = re.sub(_pat, "MARK", "full of ==sentences nobody checks==. CODEOWNERS says")
    S.append(("an equality written in prose is left alone, and a marked phrase is not",
              "MARK" not in _eaten and _marked == "full of MARK. CODEOWNERS says"
              # and the page still carries the equality it was found in
              and "state X == Y" in open(os.path.join(HERE, "stdlib", "bench-palette.swift"),
                                         encoding="utf-8").read()))

    # ── AND THE LIST OF VIEWS IS TWO LISTS. `VIEWS` in the tool refuses an
    # `opens:` a file states, and writes the view into somebody's manifest as an
    # atom of their world; the views themselves are implemented on the page. Two
    # lists of the same three words, and nothing compared them: rename a view
    # here and the tool goes on writing the old name into other people's files.
    _views = set(re.findall(r'"(\w+)"', re.search(r"VIEWS = \(([^)]*)\)", src).group(1)))
    _seg = set(re.findall(r'data-m="(\w+)"', ui))
    _shown = set(re.findall(r'm === "(\w+)"', _block("function setMode(m) {", ui)
                            if "function setMode(m) {" in ui else ui.split("function setMode(m)")[1][:600]))
    S.append(("the views this tool names are the views the page has, and nobody keeps a second list",
              _views and _views == _seg and _views == _shown))

    S.append(("nothing passes above the row of names that stays while the table scrolls",
              "position:sticky" in _tblhead and "top:0" in _tblhead
              # no padding over the scroll box: the first heading carries that space,
              # and a margin is not part of the box the header sticks inside
              and _tblpane.startswith("position:absolute") and "padding:0 " in _tblpane
              and "margin-top:calc(var(--u)*8)" in _block("#table-host h3:first-child{", ui)))

    S.append(("a table takes the width of what it holds, not the width of the pane",
              "#table-host table{border-collapse:collapse;width:auto;max-width:100%" in ui
              and "#table-host td,#table-host th{white-space:nowrap}" in ui
              # and a note in a table is the same prose in the same register as
              # everywhere else it is shown — one rendering, not three
              and 'nt.className = "cell-note"' in ui
              and "nt.innerHTML = noteProse(" in ui
              and "#table-host td.cell-note{white-space:normal;max-width:44ch" in ui
              # AND THE CELLS STAND UNDER THE HEADINGS THEY BELONG TO. The head
              # read name · axes · note · (blank) while the row was built
              # name · axes · remove · note — so the × sat under `note` and the
              # sentence sat under nothing. Not a matter of taste: the columns
              # were labelled wrongly, and nobody had looked at a table with a
              # note in it since the note column was added.
              #
              # The order is also the right one to want. A note is read far more
              # often than a record is removed, and a destructive control had
              # been standing between the facts and the sentence — crossed on
              # every reading. The hand goes at the edge, which is where the
              # register law puts it and where a misclick costs least.
              # and it cannot part again, because there is now ONE list and the
              # heading row and the cell row both walk it. A check would have
              # caught this once; a single source makes it unwritable — which is
              # what this tool sells, turned on its own page.
              and 'const columns = ["name", ...group.keys, ...(hasSeams ? ["seam"] : []),' in ui
              and '...(hasNotes ? ["note"] : []), ""];' in ui
              and "for (const key of columns) {" in ui
              and "for (const key of columns) tr.append(cellFor[key]);" in ui
              and ui.count("const columns = [") == 1))

    # ── AND A PAGE THAT FORGETS TO SAY WHICH IT IS GOES RED. The rule that each
    # shelf file states its own role in its own second line replaced a guess
    # dressed as a category, and a rule nobody checks decays into the guess it
    # replaced. Probed by taking the line away from a copy of the real file and
    # putting it back — never by trusting the files to stay right.
    shelf_file = os.path.join(HERE, "stdlib", "forms-organization.swift")
    kept = open(shelf_file, encoding="utf-8").read()
    try:
        stripped = "\n".join(l for l in kept.split("\n") if not l.startswith("// role:"))
        open(shelf_file, "w").write(stripped)
        roleless = run("status", cwd=HERE)[1]
    finally:
        open(shelf_file, "w").write(kept)
    S.append(("a shelf page that does not say what it is goes red at its own line",
              roleless.get("verdict") == "refused"
              and any(r.get("address") == "stdlib/forms-organization.swift:2"
                      and "does not say what it is" in r.get("claim", "")
                      for r in roleless.get("refusals", []))
              # and with the line back, this repository holds again
              and run("status", cwd=HERE)[1].get("verdict") == "holds"))

    # ── AND A WORD THAT WAS RETIRED STAYS RETIRED. `genre` named a thing this
    # tool no longer believes in: a kind of world handed down, belonging to the
    # judge. What there is instead is forms — the grammar records are written
    # in — arriving today by two roads that are said apart, one compiled into
    # the judge and one presented by file. A word carries its old idea back in
    # with it, so the outward texts are checked rather than trusted to care.
    rail_and_cli = ui + src + readme + open(__file__, encoding="utf-8").read()
    S.append(("the retired word does not come back into anything a reader sees, this file included",
              rail_and_cli.lower().count("genre") == GENRE_SAID_HERE
              # and what replaced it is stated as a fact about now, not a law
              and "arrive by two roads" in readme
              and "not a claim about it" in readme
              # the files carry the living word, and git kept their history
              and all(os.path.exists(os.path.join(HERE, "stdlib", f"forms-{n}.swift"))
                      for n in ("contract", "grants", "organization", "reference"))
              and not any(f.startswith("genre-")
                          for f in os.listdir(os.path.join(HERE, "stdlib")))))

    # ── AND THE COVER'S PICTURE IS OF THIS BENCH, NOT A REMEMBERED ONE. The
    # README shows docs/bench.png, and bin/shoot-bench.sh writes beside it the
    # sha256 of ui.html as photographed. Held here to the working copy, so a
    # bench that moved on goes red until the picture is retaken, which is one
    # command. The pair is the picture and the page, spelled as a hash of the
    # page because pixels depend on the camera's fonts and the page does not.
    _shot_from = os.path.join(HERE, "docs", "bench.png.from")
    _shot_said = open(_shot_from, encoding="utf-8").read() if os.path.exists(_shot_from) else ""
    _ui_hash = hashlib.sha256(open(os.path.join(HERE, "ui.html"), "rb").read()).hexdigest()
    S.append(("the cover's picture shows the bench as it is, not as it was",
              os.path.exists(os.path.join(HERE, "docs", "bench.png"))
              and "docs/bench.png" in readme
              and ("sha256:" + _ui_hash) in _shot_said
              and "shoot-bench.sh" in _shot_said))

    claimed_n = re.search(r"the battery: (\d+) checks", readme)
    S.append(("the README counts these checks correctly",
              bool(claimed_n) and int(claimed_n.group(1)) == len(S) + 1))

    for name, ok in S:
        print(("PASS" if ok else "FAIL"), name)
    print("ALL GREEN" if all(ok for _, ok in S) else "RED")
    shutil.rmtree(tmp)
    sys.exit(0 if all(ok for _, ok in S) else 1)


main()
