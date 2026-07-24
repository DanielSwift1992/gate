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
    printed = open(os.path.join(repo, "gate.swift")).read()
    named = re.search(r"gate stdlib show (genre-[a-z]+)", printed)
    S.append(("a world names the genre it is written in, and that genre is on the shelf",
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
        % (os.path.join(HERE, "judge.js"), os.path.join(HERE, "stdlib", "genre-organization.swift")))
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
    # the same crystal carries it: the world is written in genre-grants
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
    S.append(("an empty repo is offered the journal, which needs no translation",
              r.get("verdict") == "no world here" and "gate log" in r.get("next", "")))
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
    genre = open(os.path.join(HERE, "stdlib", "genre-organization.swift")).read()
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
    S.append(("and the chip reddens for disagreements alone, not for empty slots",
              "outerHTML = broken.length" in ui
              and "+ broken.length + '</span>'" in ui))

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
              and 'on the shelf, judged by' in ui and "if (viewingShelf)" in ui))
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
    # the bench is judged by its own rules: a value on MyBench/MyJournal the genre
    # does not name is a guard line addressed at its own line (a mistyped Scope
    # used to fall silently to a default), read from the same one source
    S.append(("a bench value outside the genre is named on its line, not silenced",
              "function benchGuards(" in ui
              and 'vocabulary[conf] !== "bench-atoms"' in ui
              and "the bench genre states" in ui))

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
    def _block(sel): return ui.split(sel, 1)[1].split("}", 1)[0] if sel in ui else ""
    def _match(block, mode):
        for var, atom in VAR2ATOM.items():
            m = re.search(re.escape(var) + r": color\(xyz-d65 calc\((\d+)/100\) calc\((\d+)/100\) calc\((\d+)/100\)\)", block)
            if not m: return False
            if (int(m.group(1)), int(m.group(2)), int(m.group(3))) != (
                    axes.get((atom, mode, "X")), axes.get((atom, mode, "Y")), axes.get((atom, mode, "Z"))):
                return False
        return True
    stripped = re.sub(r':root(\[data-theme="dark"\])?\{.*?\n\}', "", ui, flags=re.S)
    no_stray = not re.search(r"#[0-9a-fA-F]{3,6}\b", stripped) and "rgb(" not in stripped
    S.append(("the palette the bench renders is the palette the judge holds: same numbers, no colour outside it",
              _match(_block(":root{"), "Lit")
              and _match(_block(':root[data-theme="dark"]{'), "Dim")
              and no_stray))

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

    # ── the claims about ourselves are judged too ──
    # A tool that sells judgement over memory may not keep its own claims by
    # memory. The README's count of these checks, the verbs it lists, the files
    # it names and the routes the bench is promised are all compared with what
    # the code actually does. This runs LAST, so the count includes everything.
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

    listed = set(re.findall(r"^(\S+\.(?:py|js|html|css|sh|md))",
                            readme.split("## Repository")[-1], re.M)) if "## Repository" in readme else set()
    missing = sorted(f for f in listed if not os.path.exists(os.path.join(HERE, f))
                     and not os.path.exists(os.path.join(HERE, "tests", f)))
    S.append(("every file the README names is a file that exists", not missing))

    S.append(("the licence the README claims is the licence in the tree",
              "MIT licensed" in readme
              and open(os.path.join(HERE, "LICENSE"), encoding="utf-8").read().startswith("MIT License")))

    claimed_n = re.search(r"the battery — (\d+) end-to-end checks", readme)
    S.append(("the README counts these checks correctly",
              bool(claimed_n) and int(claimed_n.group(1)) == len(S) + 1))

    for name, ok in S:
        print(("PASS" if ok else "FAIL"), name)
    print("ALL GREEN" if all(ok for _, ok in S) else "RED")
    shutil.rmtree(tmp)
    sys.exit(0 if all(ok for _, ok in S) else 1)


main()
