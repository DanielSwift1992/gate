#!/usr/bin/env python3
# The Windows measure: the reviewer's road, as asserts. The full battery
# leans on unix tools in places, so this file is the platform's own green:
# what a person on Windows does first, checked end to end under the node
# port, which serves both courts there. It is plain python and runs on any
# platform, so the road it walks is also walked by the mac battery's host
# in CI before Windows ever sees it.
# PAIR, held by hand: the cover's platform paragraph tells this road in one
# sentence ("it makes the demo, takes the kit, breaks a claim..."). No guard
# compares the sentence to these asserts; change the road here, change the
# sentence there. The battery anchors only the sentence's closing line.
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the shim this platform reads: `gate.cmd` speaks that platform's own
# spelling of the same ladder, and `gate` is the posix one
GATE = os.path.join(HERE, "gate.cmd" if sys.platform == "win32" else "gate")
S = []


def run(*args, cwd=None):
    # the tool is a binary and the shim finds it: running the shim under
    # python worked while the CLI itself was python, and finds nothing now
    return subprocess.run([GATE, *args], cwd=cwd,
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          env=dict(os.environ, PYTHONUTF8="1"))


def sh(*args, cwd=None):
    return subprocess.run(list(args), cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def voice(label, proc):
    # a FAIL on a machine nobody sits at must say what the tool said: the
    # exit code and both streams. The tail, not the head: a traceback names
    # its cause on its last lines, and the first cut of this printed the top
    # of one, which is a riddle with the answer trimmed off.
    print("  " + label + " exit=" + str(proc.returncode))
    for stream, text in (("out", proc.stdout), ("err", proc.stderr)):
        for line in (text or "").strip().split("\n")[-8:]:
            if line.strip():
                print("    " + stream + "| " + line)


with tempfile.TemporaryDirectory(prefix="gate-win-") as tmp:
    os.environ["GATE_ME"] = os.path.join(tmp, "me")

    # the version answers, and it names the court it was built with: this
    # platform builds the vein from the one Swift file, and the judge's
    # sources are compiled into it at the pin the manifest states. The
    # port used to answer here, on a machine the judge binary was not
    # built for; a binary built HERE has its own court and says which.
    v = run("--version")
    S.append(("gate answers on this machine", v.returncode == 0 and "gate " in v.stdout))
    S.append(("the version names the court this binary was built with",
              "judge built from verification-is-identification" in v.stdout))

    # the certificate court through the port: a shelf page holds
    w = sh("node", os.path.join(HERE, "bin", "judge-cli.js"), "judge", "where",
           os.path.join(HERE, "stdlib", "bench-metrics.swift"))
    S.append(("the certificate court sits here: the spacing page holds",
              w.returncode == 0 and "THE WHERE holds" in w.stdout))

    # the demo world: the first refusal a person sees, with its address
    demo = os.path.join(tmp, "demo")
    d = run("demo", demo)
    st = run("status", cwd=demo)
    demo_ok = (d.returncode == 0 and st.returncode == 1
               and "ownership.swift:" in st.stdout and "Owns_3_carol" in st.stdout)
    S.append(("the demo is born and the plain court refuses at the written line",
              demo_ok))
    if not demo_ok:
        voice("demo", d)
        voice("status", st)

    # entry: a fresh repository takes the kit, and the whole kit holds,
    # which needs the certificate court over the forms pages
    repo = os.path.join(tmp, "client")
    os.makedirs(repo)
    sh("git", "init", "-q", repo)
    sh("git", "config", "user.name", "A Fixture", cwd=repo)
    sh("git", "config", "user.email", "fixture@client", cwd=repo)
    took = run("init", ".", cwd=repo)
    held = run("status", cwd=repo)
    S.append(("entry lands and the kit holds under both courts",
              took.returncode == 0 and held.returncode == 0
              and "holds" in held.stdout))

    # break a claim in the kit and the judge refuses it by line
    verbs = os.path.join(repo, "verbs.swift")
    text = open(verbs, encoding="utf-8").read()
    open(verbs, "w", encoding="utf-8").write(
        text.replace("public typealias Does = Reads",
                     "public typealias Does = Writes", 1))
    red = run("status", cwd=repo)
    S.append(("a false claim in the kit goes red at its line",
              red.returncode == 1 and "verbs.swift:" in red.stdout))

failed = [name for name, ok in S if not ok]
for name, ok in S:
    print(("PASS " if ok else "FAIL ") + name)
print("ALL GREEN" if not failed else "RED")
sys.exit(1 if failed else 0)
