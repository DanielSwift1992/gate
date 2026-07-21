#!/usr/bin/env python3
# The regression battery: every verb, end to end, in a throwaway repo.
# Run: python3 tests/smoke.py
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(HERE, "gate")
DEMO = os.path.join(HERE, "demo")


def run(*args, cwd=None):
    r = subprocess.run([sys.executable, GATE, *args, "--json"], capture_output=True, text=True, cwd=cwd)
    try:
        return r.returncode, json.loads(r.stdout)
    except Exception:
        return r.returncode, {"raw": r.stdout[:200], "stderr": r.stderr[:200]}


def main():
    tmp = tempfile.mkdtemp(prefix="gate-smoke-")
    repo = os.path.join(tmp, "client")
    os.makedirs(repo)
    subprocess.run(["git", "init", "-q", repo])
    S = []

    c, r = run("init", repo)
    S.append(("init + hook wired", r.get("hooks") is not None))
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
    open(os.path.join(split, "stray.swift"), "w").write("// stray\n")
    c, r = run("status", cwd=split)
    S.append(("manifest: shadow file named", c == 1 and any("shadow" in x["claim"] for x in r["refusals"])))

    # self-hosted shelf: the product's own stdlib files are judged by its own judge
    import glob as _glob
    for sf in sorted(_glob.glob(os.path.join(HERE, "stdlib", "*.swift"))):
        raw = subprocess.run([os.path.join(HERE, "bin", "gate-judge"), "judge", "where", sf],
                             capture_output=True, text=True).stdout
        S.append((f"self-judged: {os.path.basename(sf)}", "holds" in raw and "✗" not in raw))

    # stdlib: hidden is not secret — shelf, materialize, drift guard, ownership
    c, r = run("stdlib")
    S.append(("stdlib shelf lists modules", len(r.get("modules", {})) == 2))
    lib = os.path.join(tmp, "lib")
    os.makedirs(lib)
    shutil.copy(os.path.join(repo, "gate.swift"), os.path.join(lib, "gate.swift"))
    c, r = run("stdlib", "materialize", "genre-grants", cwd=lib)
    c, r = run("status", cwd=lib)
    S.append(("materialized untouched copy holds", r["verdict"] == "holds"))
    with open(os.path.join(lib, "genre-grants.swift"), "a") as f:
        f.write("// edit\n")
    c, r = run("status", cwd=lib)
    S.append(("drifted stdlib copy named", r["verdict"] == "refused" and any("drifted" in x["claim"] for x in r["refusals"])))
    t = open(os.path.join(lib, "genre-grants.swift")).read().replace("// gate stdlib", "// mine:", 1)
    open(os.path.join(lib, "genre-grants.swift"), "w").write(t)
    c, r = run("status", cwd=lib)
    S.append(("header removed = the file is owned", r["verdict"] == "holds"))

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
    S.append(("personal world: created in its own git, holds",
              r.get("verdict") == "holds" and mypath.startswith(me)
              and os.path.isdir(os.path.join(me, ".git"))))
    S.append(("personal world: the shared repo has no trace of it",
              subprocess.run(["git", "status", "--porcelain"], cwd=jrepo,
                             capture_output=True, text=True).stdout.strip() == ""))
    # a claim the SHARED world does not make anywhere: only my own file can be
    # refused for it, so a pass here cannot come from the world's own entries
    def myclaim(who, doc):
        base = open(mypath).read().split("\npublic enum MyWatch")[0]
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

    # ── zero egress: a claim about ourselves, kept by a gate on our own source.
    # An enterprise review runs this same grep; it must never come back dirty,
    # because one outbound call ends the "an engineer may just install it" path.
    forbidden = [r"urllib\.request", r"^\s*import socket\b", r"socket\.socket",
                 r"http\.client", r"requests\.(get|post|put)", r"XMLHttpRequest",
                 r"new WebSocket", r"""fetch\(\s*['"`]https?:""",
                 r"""(?:src|href)\s*=\s*['"]https?:"""]
    hits = []
    for f in ("gate", "ui.html", "judge.js"):
        text = open(os.path.join(HERE, f), encoding="utf-8", errors="replace").read()
        for pat in forbidden:
            for m in re.finditer(pat, text, re.M):
                hits.append(f + ": " + m.group(0))
    S.append(("zero egress: no outbound primitive in the runtime sources", not hits))
    src = open(GATE, encoding="utf-8").read()
    S.append(("the bench binds to the loopback alone", 'HTTPServer(("127.0.0.1"' in src))
    ui = open(os.path.join(HERE, "ui.html"), encoding="utf-8").read()
    S.append(("the page declares a policy that blocks any external request",
              "Content-Security-Policy" in ui and "connect-src 'self'" in ui))

    for name, ok in S:
        print(("PASS" if ok else "FAIL"), name)
    print("ALL GREEN" if all(ok for _, ok in S) else "RED")
    shutil.rmtree(tmp)
    sys.exit(0 if all(ok for _, ok in S) else 1)


main()
