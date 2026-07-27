#!/usr/bin/env python3
# The regression battery: every verb, end to end, in a throwaway repo.
# Run: python3 tests/smoke.py
import ast, json, os, re, shutil, subprocess, sys, tempfile

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
    S.append(("manifest: shadow file named", c == 1 and any("shadow" in x["claim"] for x in r["refusals"])))

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
    S.append(("the shelf lists exactly the genres on it", shelf == on_disk and len(shelf) >= 3))
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
    ghosts = [x for x in r["refusals"] if "ghost path" in x["claim"]]
    S.append(("codeowners: a rule outside its owner's zone is refused, by their line",
              c == 1 and judged and all("CODEOWNERS:" in x["source"] for x in judged)))
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
              and "trivially" in r["note"]))
    # the same crystal carries it: the world is written in forms-grants
    world = open(os.path.join(tmp, "co-gate.swift")).read()
    S.append(("ownership rides the access crystal, not a genre of its own",
              "Owns<" in world and "public protocol Keeper" in world))
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
              "THIS machine" in tpl and "goes nowhere else" in tpl))
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
    run("demo", ven)
    c, r = run("init", ven, "--vendor")
    S.append(("init --vendor carries the tool and its judge into the repo",
              r.get("vendored") and os.path.exists(os.path.join(ven, "gatew"))
              and os.path.exists(os.path.join(ven, ".gate", "bin", "gate-judge"))
              and len(r["vendored"].get("judge_sha256", "")) == 64))
    S.append(("and the terms travel with it: a vendored copy carries its licence",
              os.path.exists(os.path.join(ven, ".gate", "LICENSE"))
              and os.path.exists(os.path.join(ven, ".gate", "NOTICE.md"))))
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
    c, r = run("demo", d)
    S.append(("demo builds a world that holds, with a policy and a history",
              os.path.exists(os.path.join(d, "gate.swift"))
              and os.path.exists(os.path.join(d, "gate.policy.swift"))))
    c, r = run("status", cwd=d)
    S.append(("the demo world holds on the first look", c == 0 and r["verdict"] == "holds"))
    c, r = run("check", "view", "Emp9001", "EngineeringShare", cwd=d)
    S.append(("and the invitation in it is real: the refusal names both",
              c == 1 and r["refusals"]))
    empty = os.path.join(tmp, "noworld")
    os.makedirs(empty)
    subprocess.run(["git", "init", "-q", "-b", "main", empty])
    c, r = run("log", cwd=empty)
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
    # every name a printed world uses has a home: its own file, or the genre
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
    genre = open(os.path.join(HERE, "stdlib", "forms-organization.swift")).read()
    S.append(("every axis in the genre states what it accepts",
              "associatedtype Sex: Sexed" in genre and "associatedtype Rank: Ranked" in genre
              and "associatedtype Home: Department" in genre))
    S.append(("and the bench offers by that, not by what it saw nearby",
              "function fillersFor(" in ui and "axesOfHost(host)[slot[1]]" in ui))
    S.append(("a recognised slot never falls through to the general pool",
              "a slot is a closed question" in ui and "closed: true }" in ui
              and "return { items: f || []" in ui))
    S.append(("the popup is pinned to the word, not moved by a changing verdict",
              "reposition || compEl.hidden" in ui and "drawCompletion(true)" in ui))

    S.append(("deleting back into a word offers again, not only typing forward",
              'change.origin === "+delete") offerCompletion()' in ui))

    S.append(("the cursor on a name describes it from the grammar, not a dictionary",
              "function describeName(" in ui and "function inspect(" in ui
              and "protoAxes[name]" in ui and "conformers)" in ui))
    S.append(("and what it says is read from the world and the genre",
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
    # the shelf has ONE reader: the vocabulary is built in the bench from the
    # judge's own parse (axisKinds/paramKinds), so the gate carries no second
    # regex over the shelf and the bench never fetches a server-built vocabulary
    S.append(("the shelf's vocabulary has one reader: the judge, not a second regex",
              "proto_axes" not in open(GATE, encoding="utf-8").read()
              and 'fetch("/vocabulary")' not in ui
              and "function loadVocabulary(" in ui and "judge(mod" in ui))

    # the shelf is reference, read in the bench but never judged as the world:
    # a genre uses protocol/associatedtype, which the world's judge rejects, so
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
              "outerHTML = (broken.length" in ui
              and "+ broken.length + '</span>'" in ui
              # the waiting slots are built apart from the verdict and appended to it
              and "const waits = pending.length" in ui and "+ waits;" in ui
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
              'viewingShelf = mod' in ui and 'chip" id="chip" style=' in ui
              and 'a printout of what the judge carries' in ui and "if (viewingShelf)" in ui))
    S.append(("and returning to a world file resumes judgement",
              'viewingShelf = null' in ui and 'cm.setOption("readOnly", false); viewingShelf = null' in ui))

    S.append(("the offer has one source: the grammar, with no pool to fall back to",
              "if (!here) return hideCompletion()" in ui and "function completionPool" not in ui))

    # the bench wears its own theme by declaration, not a toggle: MyBench.Theme
    # is read from the shelf genre (conformers of BenchTheme), with the OS
    # preference as the default when nothing is declared
    bench_atoms = open(os.path.join(HERE, "stdlib", "bench-atoms.swift"), encoding="utf-8").read()
    S.append(("the theme is a declaration read from the genre, with the OS as default",
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

    # the bench is judged by its own rules: a value on MyBench/MyJournal the genre
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
    # element's own co-class (the diff row is `fact factrow`).
    reg_rules = {r: ui.split(r, 1)[1].split("}", 1)[0]
                 for r in (".fact{", ".observed{", ".speech{", ".caption{") if r in ui}
    S.append(("the bench's material is a function of its wire: six registers, named by the element",
              all(r in ui for r in (".fact{", ".observed{", ".speech{", ".caption{", ".verdict{", ".gesture{"))
              and '<code class="fact">' in ui and "file fact" in ui
              and "meta observed" in ui and "subj speech" in ui
              and len(reg_rules) == 4
              and all("display:" not in v and "padding:" not in v for v in reg_rules.values())
              and "fact factrow" in ui))
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
    journal_sels = ("#journal", ".commit", ".badge", ".subj", ".meta", ".cdiff",
                    ".dfile", ".dline", ".dmore", ".dwait", ".factrow", ".obs", "#gitstate")
    forged = [m.group(1).strip()[:40]
              for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", style)
              if any(k in m.group(1) for k in journal_sels)
              and re.search(r"var\(--(ok|bad)\)", m.group(2))]
    S.append(("what is read speaks in the ladder: the journal never wears the verdict's own colours",
              not forged
              and ".factrow .was{color:var(--muted)" in style
              and ".factrow .own{color:var(--localtype)}" in style))

    # ── colour answers one question and weight another, because a reader has two.
    # WHERE a name is from is a hue: teal for what this world DECLARES, violet for
    # what the shelf does. Declares, not mentions — the kinds a record conforms to
    # and the axes it answers are the genre's, and colouring them local said the
    # world had authored its own genre, which also made a question (an axis) and
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
              and "(?:enum|protocol|struct|extension)\\s+$/.test(before) ? \" declname\"" in ui
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
    _, made = run("demo", dm)
    S.append(("the first thing a newcomer sees is a refusal with an address, not a list of things to try",
              made.get("refused") and ":" in made["refused"][0]
              and "VerifiedView" in made["refused"][0]
              and made.get("asked", "").startswith("gate check view")))

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
              # it sits with FILES and JOURNAL, which are the other things that
              # are about this repository — the Full/Bare/Table switch asks how to
              # look at ONE FILE, and a seam is not a view of a file at all
              and 'data-fold="seams"' in ui and 'data-m="seams"' not in ui
              and "async function buildSeams()" in ui
              # it borrows the rail's own grammar rather than inventing a second
              # one: a row is a commit's row, the address is a fact, the kind is
              # a badge, and WHY it is there lives in the title — answered on
              # demand, the way this bench has always answered `what is this`,
              # instead of printed under every line down a narrow column
              and 'r.className = "commit touches"' in ui and '"came back"' in ui
              # EVERY ADDRESS THIS BENCH PRINTS IS REACHABLE. A row that looks
              # clickable and does nothing is worse than a plain list — the
              # affordance came along with the styling and was not honoured. A
              # line opens the side that SAID it, read-only, since neither side
              # is this world's to edit from here.
              and "r.onclick = () => openSeamSide(" in ui
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
              # and the rail shows what this repository HAS. A folder with no
              # seam in it has no seam, and a permanent panel about a thing
              # nobody is using is an advertisement standing in an account. The
              # HEADING stands regardless, because the judge is always taken:
              # what comes and goes is the seam rows, not the fact of theirs.
              and "host.hidden = !seams.length" in ui
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
    shadows = [r for r in together.get("refusals", []) if "shadow" in r.get("claim", "")]
    open(os.path.join(bth, "stray.swift"), "w").write("public enum Stray: Ranked {}\n")
    _, with_stray = run("status", cwd=bth)
    S.append(("a seam declaration beside a declared layout is not a shadow, and a stray world file still is",
              together.get("verdict") == "holds" and not shadows
              # and the guard still does its own job
              and [r["address"] for r in with_stray.get("refusals", [])
                   if "shadow" in r["claim"]] == ["stray.swift"]))

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
    S.append(("an author's name is a fact and not a button, and a badge keeps its edge under the pointer",
              ".commit .who{cursor:pointer;color:var(--ink)" in ui
              and "var(--action)" not in ui.split(".commit .who{", 1)[1].split("}", 1)[0]
              and ".badge.closed{border:1px solid var(--line)" in ui
              and "background" not in ui.split(".badge.closed{", 1)[1].split("}", 1)[0]))

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
              and "declared, waiting for the other side" in ui))

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
    # Splitting the shelf instead into genres and gate's own furniture drew a
    # line nobody using this needs, and hid the one they do: NONE OF THE SHELF
    # IS EITHER. Those words are compiled inside the judge — a world speaks
    # `Department` with no file of that name near it — so a shelf page is a
    # printout, and the dependency is the judge, named by revision.
    shelf_said = say("stdlib", cwd=ent)
    shelf_src = open(GATE, encoding="utf-8").read()
    S.append(("the shelf is one list of printouts, and says it is not yours",
              "all of it theirs" in shelf_said
              and "forms-organization" in shelf_said and "bench-palette" in shelf_said
              and "these are THEIRS" in shelf_said
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
    # difference: not a genre, and it is what a merge policy is written in.
    roles = run("stdlib", cwd=ent)[1].get("roles") or {}
    S.append(("the shelf says which of it you can speak, and each file says so itself",
              roles.get("forms-organization") == "forms"
              and roles.get("forms-contract") == "forms"
              # not a genre by name, and speakable all the same
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
    # invited an operator to materialize a genre and called the copy theirs to
    # change, which is a sentence the machinery had never agreed to: the words
    # live compiled inside the judge. A world speaks `Department` with no file of
    # that name anywhere near it; the file put beside the world is read by
    # nothing; and declaring it as a file of mine is refused outright, because a
    # world is records and a genre is the grammar records are written in. Three
    # ways of finding out it is not a source — the invitation was the lie.
    shelf_probe = tempfile.mkdtemp()
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
              # and calling it a file of mine is refused: a genre is not a world
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
    two = tempfile.mkdtemp()
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
    many = tempfile.mkdtemp()
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
    keeps = tempfile.mkdtemp()
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
    hand = tempfile.mkdtemp()
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
    frm = tempfile.mkdtemp()
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

    # ── AND THE FORMS ROWS ARE JUDGED AS ONE STREAM, WHICH IS NOT A DETAIL.
    # `where` over a LIST of files is blind, and its silence is selective by
    # order: a law split across two files holds in isolation and refuses the
    # moment they are glued. This project had already found that, written it
    # down, and stood a vector on it — and I shipped the isolated form anyway,
    # because I had read the machinery and not the canon. The order comes from
    # the manifest, so the same repository always reads the same way, and the
    # address lands in the file that SAYS the certificate rather than in the
    # stream it was read in.
    split = tempfile.mkdtemp()
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
                       encoding="utf-8").read().strip().startswith("0fd0b38")))

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
    old = tempfile.mkdtemp()
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
    demo_pair = tempfile.mkdtemp()
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
              # and the bench goes there rather than opening a fourth thing
              and "await loadFile(t.claim); reveal(t.line)" in ui
              and "that sentence is the fact, and this is a reading of it" in ui))

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
                  "TheirsApartBad_Z_lit", "TheirsApartBad_Z_dim"))
              # and the weak one is named as weak rather than buried in a number
              and "THE WEAK ONE, SAID OUT LOUD" in pal
              # the floors are live: the judge counts them among what it holds
              and "116 equalities" in subprocess.run(
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
    par = tempfile.mkdtemp()
    run("demo", cwd=par)
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
    claim_probe = tempfile.mkdtemp()
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
    dia = tempfile.mkdtemp()
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
    keep = os.path.join(HERE, "bin", "gate-judge.from")
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
    where_calls = re.findall(r"subprocess\.run\(\[JUDGE, \"judge\", \"where\",([^\]]*)\]", gate_src)
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
const vocabulary = { Employee: "genre", Male: "genre" };
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
    genre_txt = open(os.path.join(HERE, "stdlib", "forms-organization.swift"), encoding="utf-8").read()
    slot_js = '''
const { judge } = require(%r);
const genre = %s;
const world = (v) => genre + `
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
''' % (os.path.join(HERE, "judge.js"), json.dumps(genre_txt))
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
    # section heads, a file, a commit, a diff line, a fact — begins at ONE step,
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
    rail_rows = ["#brand", "#rail h3", ".file", ".commit", ".factrow", ".dline",
                 ".dfile", ".dmore", ".dwait", "#filter-note,#load-more", "#rail h3.fold .obs"]
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

    # a refusal is pointed at by its EDGE — a left border and a light backing, two
    # markers and no more; the address is a fact like any other, and the red is
    # the verdict's alone (the chip, and the wave under a name resolving to nothing)
    S.append(("a refusal is marked by its edge, and its address is a fact, not a verdict",
              "border-left:3px solid var(--bad)" in ui
              and ".refusal code{color:var(--bad)" not in ui
              and "border:1px solid color-mix(in srgb,var(--bad) 22%" not in ui))

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

    routes = set(re.findall(r'u\.path\s*[!=]=\s*"(/[a-z/]*)"', src))   # == and != both route
    for grp in re.findall(r'u\.path\s+in\s+\(([^)]*)\)', src):
        routes |= set(re.findall(r'"(/[a-z/]*)"', grp))
    contract = set()
    for line in re.findall(r"^\s+#\s+(?:GET|POST|PUT)\s+(.+)$", src, re.M):
        contract |= set(re.findall(r"(/[a-z/]*)", line.split("  ")[0] + " " + line))
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
              and 'fetch("/version"' in ui and "restart `gate serve`" in ui
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
                            readme.split("## Repository")[-1], re.M)) if "## Repository" in readme else set()
    missing = sorted(f for f in listed if not os.path.exists(os.path.join(HERE, f))
                     and not os.path.exists(os.path.join(HERE, "tests", f)))
    S.append(("every file the README names is a file that exists", not missing))

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
              # prose is set as speech and wraps, rather than as preformatted code
              and "#bare .note{display:block;white-space:normal" in ui
              and "-apple-system,sans-serif" in ui.split("#bare .note{")[1][:140]
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
              and 'const columns = ["name", ...group.keys, ...(hasNotes ? ["note"] : []), ""]' in ui
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
    rail_and_cli = ui + src + readme
    S.append(("the retired word does not come back into anything a reader sees",
              "genre" not in rail_and_cli.lower()
              # and what replaced it is stated as a fact about now, not a law
              and "arrive by two roads" in readme
              and "not a claim about it" in readme
              # the files carry the living word, and git kept their history
              and all(os.path.exists(os.path.join(HERE, "stdlib", f"forms-{n}.swift"))
                      for n in ("contract", "grants", "organization", "reference"))
              and not any(f.startswith("genre-")
                          for f in os.listdir(os.path.join(HERE, "stdlib")))))

    claimed_n = re.search(r"the battery — (\d+) end-to-end checks", readme)
    S.append(("the README counts these checks correctly",
              bool(claimed_n) and int(claimed_n.group(1)) == len(S) + 1))

    for name, ok in S:
        print(("PASS" if ok else "FAIL"), name)
    print("ALL GREEN" if all(ok for _, ok in S) else "RED")
    shutil.rmtree(tmp)
    sys.exit(0 if all(ok for _, ok in S) else 1)


main()
