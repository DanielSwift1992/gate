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
import re
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
    # python worked while the CLI itself was python, and finds nothing now.
    # That platform's door is a .cmd, and the interpreter for one is cmd
    # itself: named through it, the door is entered the way a person on
    # that platform enters it, and its exit code comes back whole.
    _door = (["cmd", "/c", GATE] if sys.platform == "win32" else [GATE])
    # ── AND A ROAD THAT LOST ITS GROUND SAYS SO. A step that did not make the
    # world the next one works in leaves this pointing at a directory that is
    # not there, and subprocess RAISES where this file is meant to answer: on a
    # machine nobody sits at, one traceback replaced every sentence this walk
    # had to say, and the status that travels out carried its last line.
    if cwd is not None and not os.path.isdir(cwd):
        return subprocess.CompletedProcess(
            args, 127, "", "the step before this one never made " + cwd)
    return subprocess.run([*_door, *args], cwd=cwd,
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
    # one line first, short enough to travel as a commit status from a machine
    # whose log needs rights to read
    # ── AND THE LINE THAT TRAVELS IS THE ONE WITH AN ADDRESS IN IT. This took
    # the first non-empty line, and this tool's first line is a summary: the
    # windows job reported `status: refused 1 · 13 equalities` twice over,
    # which says a refusal happened and not one word about which. The address
    # is the whole product, so a line carrying one is preferred, and the
    # summary is the fallback it always was.
    _first = ""
    for _t in (proc.stderr, proc.stdout):
        _lines = [l.strip() for l in (_t or "").split("\n") if l.strip()]
        _first = next((l for l in _lines if re.search(r"\S+:\d+ ", l)), "")
        _first = _first or next(iter(_lines), "")
        if _first:
            break
    # ── AND THE CUT TAKES BOTH ENDS. Ninety letters from the front carried
    # "...and no such file exists at" four runs running and stopped one
    # character before the path, which was the whole question. A refusal's
    # head is an address already known and the thing being hunted sits at the
    # end, so both ends travel and the middle is what gives way.
    # ── AND WHAT TRAVELS IS THE PART NOBODY CAN GUESS. Cut at the front this
    # carried prose; cut at both ends it carried prose from both ends, and the
    # path sat in the middle of the sentence where the cut went. A refusal's
    # prose is written in this repository and can be read here; the only thing
    # in it that belongs to the machine is what it quotes. So a quoted part
    # goes first, and the sentence follows for as long as there is room.
    _mark = re.search(r"`([^`]+)`", _first)
    _said = _first if len(_first) <= 110 else (
        "«" + _mark.group(1)[-72:] + "» " + _first[:34] if _mark
        else _first[:44] + " … " + _first[-63:])
    print("FAIL " + label + ": exit=" + str(proc.returncode) + " said=" + _said)
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
        # ── AND WHEN A WORLD IS ACCUSED OF MISSING A FILE, THE FOLDER IS SHOWN.
        # Four runs were spent proving the path in that refusal is the right
        # one; what nobody here can see is whether the file is at the end of it.
        # The folder this world is says that in one line, from the machine that
        # made it, which no reading of the sources can.
        try:
            _here = sorted(os.listdir(demo))
        except OSError as _e:
            _here = ["the world's own folder cannot be listed: " + str(_e)]
        # ── AND IT IS SAID FIRST. Two sentences leave this machine, the first
        # two that look like a red, and the ones this pair already made are
        # known: the verb that stopped and the claim it made. What is not known
        # is the folder, so the folder speaks first.
        # ── AND A VERB THAT DIES IS ASKED AGAIN, SIMPLER EACH TIME. The child
        # this demo runs leaves with 1033, which is the low word of the fail
        # fast a swift trap raises on this platform: it does not exit, it
        # falls over, before it can print a character on either channel. Where
        # it falls is what these three ask, from the outside, on a world this
        # road makes for them: the whole shape first, then without the court's
        # own reading of the tree, then the bare read of somebody's file.
        _kit = os.path.join(tmp, "probe")
        os.makedirs(_kit, exist_ok=True)
        open(os.path.join(_kit, "CODEOWNERS"), "w").write("src/ @alice\n")
        open(os.path.join(_kit, "owners.csv"), "w").write("owner,zone\nalice,src\n")
        os.makedirs(os.path.join(_kit, "src"), exist_ok=True)
        open(os.path.join(_kit, "src", "a.txt"), "w").write("x\n")
        _shapes = [
            ("whole", ["import", "codeowners", "CODEOWNERS", "--tree", ".",
                       "--policy", "owners.csv", "-o", "out.swift", "--json"]),
            ("no policy, no out", ["import", "codeowners", "CODEOWNERS", "--tree", "."]),
            ("bare read", ["import", "codeowners", "CODEOWNERS"]),
            # ── AND TWO THAT SAY WHERE IT IS NOT. All three above die the same
            # way, so the trap is before the tree is judged and before anything
            # is written. A file that is not there must be REFUSED in words: if
            # that falls over too, nothing in this verb has run yet. And the
            # sibling adaptor says whether the ground is common to imports or
            # belongs to this one.
            ("missing file", ["import", "codeowners", "nosuchfile"]),
            ("sibling adaptor", ["import", "workflows", "--tree", "."]),
        ]
        _codes = []
        for _name, _argv in _shapes:
            _r = run(*_argv, cwd=_kit)
            _codes.append(_name + "=" + str(_r.returncode)
                          + ("/silent" if not (_r.stdout or _r.stderr).strip() else "/spoke"))
        print("FAIL demo: import dies as " + "; ".join(_codes))
        print("FAIL demo: the world holds " + ", ".join(_here)[:100])
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
