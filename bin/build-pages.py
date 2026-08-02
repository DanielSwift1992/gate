#!/usr/bin/env python3
# Publishes the bench as a static page over a fresh demo. The parts are the
# ones already shipped: the same ui.html, the same browser judges, and the
# server's own answers, recorded at build time from a live `gate serve` so
# the page carries no second reading of any endpoint. On a keystroke the
# open file is judged in the browser, the where court by judge-where.js and
# the plain court by judge.js; the full cross-file court and the write path
# belong to the clone, and the page says so on its face.
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(HERE, "gate")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "_site")


def get(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as r:
        return r.read().decode("utf-8")


def post(port, path, body):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
                                 data=body.encode("utf-8"), method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def main():
    tmp = tempfile.mkdtemp(prefix="gate-pages-")
    demo = os.path.join(tmp, "demo")
    subprocess.run([sys.executable, GATE, "demo", demo],
                   capture_output=True, check=True)
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
    serve = subprocess.Popen([sys.executable, GATE, "serve", str(port), "--no-open"],
                             cwd=demo, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                get(port, "/files")
                break
            except Exception:
                time.sleep(0.25)

        snap = {}
        for path in ("/files", "/language", "/version", "/status", "/shelf",
                     "/log?n=1&scope=world", "/attention"):
            snap[path] = get(port, path)

        files = json.loads(snap["/files"])
        everyone = list(files["files"]) + [files["layout"]]
        texts = {}
        for f in dict.fromkeys(everyone):
            snap[f"/world?f={f}"] = texts[f] = get(port, f"/world?f={f}")
            snap[f"/gitstatus?f={f}"] = get(port, f"/gitstatus?f={f}")
            snap[f"/verdict?f={f}"] = post(port, f"/verdict?f={f}", texts[f])

        shelf = json.loads(snap["/shelf"])
        for m in (shelf.get("modules") or []) if isinstance(shelf, dict) else []:
            snap[f"/shelf?m={m}"] = get(port, f"/shelf?m={m}")

        ladder_css = get(port, "/ladder.css")
        names = sorted(set(re.findall(r"(?:enum|protocol|typealias)\s+(\w+)",
                                      "\n".join(texts.values()))))
        for n in names:
            try:
                snap[f"/value?name={n}"] = get(port, f"/value?name={n}")
            except Exception:
                pass
    finally:
        serve.terminate()
        serve.wait()
        shutil.rmtree(tmp, ignore_errors=True)

    ui = open(os.path.join(HERE, "ui.html"), encoding="utf-8").read()
    for asset in ("codemirror.css", "ladder.css", "codemirror.js", "judge.js"):
        ui = ui.replace(f'"/{asset}"', f'"{asset}"')

    forms = set(files.get("forms") or [])
    layout = files.get("layout")
    shim = """
<script src="judge-where.js"></script>
<script>
/* THE PUBLISHED BENCH. Every answer below was recorded from a live `gate
   serve` over the demo at build time; on a keystroke the open file is
   judged here in the browser. The write path and the cross-file court
   belong to the clone. */
(function () {
    const SNAP = __SNAP__;
    const FORMS = new Set(__FORMS__);
    const LAYOUT = __LAYOUT__;
    const ALL = __ALL__;
    const real = window.fetch.bind(window);
    function reply(body, status) {
        return new Response(body, { status: status || 200,
            headers: { "Content-Type": "application/json" } });
    }
    function lineOf(text, name) {
        const lines = text.split("\\n");
        for (let i = 0; i < lines.length; i += 1) {
            if (lines[i].includes(name)) return i + 1;
        }
        return 1;
    }
    /* saved on green, in this browser: the panel is the arbiter of
       write-on-holds, exactly as it is over the real server, and a PUT that
       arrives is a holding file. localStorage stands where the working copy
       stood; reset below empties it and the demo is back. */
    function textOf(f) {
        try {
            const kept = localStorage.getItem("gate.pages." + f);
            if (kept !== null) return kept;
        } catch (e) { }
        return SNAP["/world?f=" + f] || "";
    }
    /* one court for every file, fed the way the server feeds it: forms in
       one stream per world, plain pages one by one, the layout judged for
       junk by neither side. The verdict over the world is the sum of this
       over every file, kept texts included, so the background is never a
       stale recording. */
    function refusalsFor(f, text) {
        const out = [];
        if (FORMS.has(f)) {
            let stream = text;
            for (const other of FORMS) {
                if (other !== f) stream += "\\n" + textOf(other);
            }
            for (const r of judgeWhereTexts(stream, []).refusals) {
                const m = r.match(/'(\\w+)/);
                if (!m || !text.includes(m[1])) continue;
                out.push({ address: f + ":" + lineOf(text, m[1]), claim: r });
            }
        } else if (f !== LAYOUT) {
            for (const r of judge(f, text).refusals) {
                out.push({ address: f + ":" + r.line, claim: r.premise });
            }
        }
        return out;
    }
    window.fetch = async function (url, opts) {
        const u = String(url);
        const method = (opts && opts.method) || "GET";
        if (method === "PUT" && u.startsWith("/world")) {
            const f = decodeURIComponent(u.split("f=")[1] || "");
            try { localStorage.setItem("gate.pages." + f,
                                       String((opts && opts.body) || "")); }
            catch (e) { }
            return reply("", 200);
        }
        if (method === "PUT") return reply("", 200);
        if (method === "POST" && u.startsWith("/verdict")) {
            const f = decodeURIComponent(u.split("f=")[1] || "");
            const text = opts && opts.body ? String(opts.body) : "";
            const said = JSON.parse(SNAP["/verdict?f=" + f] || "{}");
            let refusals = [];
            for (const g of ALL) {
                if (g !== f) refusals = refusals.concat(refusalsFor(g, textOf(g)));
            }
            refusals = refusals.concat(refusalsFor(f, text));
            said.verdict = refusals.length ? "refused" : "holds";
            said.refusals = refusals;
            return reply(JSON.stringify(said));
        }
        if (u.startsWith("/world?f=") && method === "GET") {
            const f = decodeURIComponent(u.split("f=")[1] || "");
            return new Response(textOf(f), { status: 200,
                headers: { "Content-Type": "text/plain; charset=utf-8" } });
        }
        if (u.startsWith("/") && SNAP[u] !== undefined) return reply(SNAP[u]);
        if (u.startsWith("/")) return reply("{}", 404);
        return real(url, opts);
    };
    /* THE ROAD TEST. Rules in the battery hold invariants; this walks the
       user's road on the published page itself: type, be offered, break,
       stay red off the disk, mend, be kept. Typing goes through the same
       entry the keyboard uses (an "+input" change), so an input path that
       falls over fails here, not on a person. CI runs this page headless
       with ?roadtest=1 and reads the report below. */
    if (location.search.includes("roadtest=1")) {
        window.addEventListener("load", async () => {
            const steps = [];
            const step = (name, ok) => steps.push((ok ? "ROADPASS " : "ROADFAIL ") + name);
            const settle = (ms) => new Promise(r => setTimeout(r, ms || 250));
            try {
                await settle(900);
                step("the door opens on the named file",
                     typeof cm !== "undefined" && active === "ownership.swift");
                const kept0 = Object.keys(localStorage).filter(
                    k => k.startsWith("gate.pages.")).length;
                const line = (() => {
                    for (let i = 0; i < cm.lineCount(); i += 1) {
                        if (cm.getLine(i).includes("Owns_3_carol")) return i;
                    }
                    return -1;
                })();
                step("the claim line is on the page", line >= 0);
                // edit the second argument the way a hand does: erase the
                // tail of the name and the offer completes what the world has
                const at = cm.getLine(line).indexOf("Path_3_src_db_");
                cm.focus();
                cm.replaceRange("", { line, ch: at + 10 },
                                { line, ch: at + 14 }, "+delete");
                cm.setCursor({ line, ch: at + 10 });
                offerCompletion();
                await settle();
                step("typing summons a closed offer",
                     !compEl.hidden && compItems && compItems.length > 0
                     && compItems.some(x => String(x).includes("Path_3_src_db_")));
                cm.replaceRange("_db_", { line, ch: at + 10 },
                                { line, ch: at + 10 }, "+input");
                await settle();
                // a note is not grammar: the same gate spelled after `//`
                // summons nothing, and the line comes back byte for byte
                const noteLine = cm.getLine(2);
                cm.replaceRange("// note: Owns<", { line: 2, ch: 0 },
                                { line: 2, ch: noteLine.length }, "+input");
                cm.setCursor({ line: 2, ch: 14 });
                offerCompletion();
                await settle();
                step("a note offers nothing", compEl.hidden);
                cm.replaceRange(noteLine, { line: 2, ch: 0 },
                                { line: 2, ch: cm.getLine(2).length }, "+input");
                await settle();
                // break the world with a real edit and judge it
                const kept = cm.getValue();
                cm.setValue(kept.replace("public typealias Post = Zone_docs",
                                         "public typealias Post = Zone_src"));
                await tick(true);
                step("a broken claim goes red",
                     lastRefusals && lastRefusals.some(r => r.file === "ownership.swift"
                         || !r.file));
                step("and red reaches no storage",
                     Object.keys(localStorage).filter(
                         k => k.startsWith("gate.pages.")).length === kept0);
                // mend the world: carol's one refusal is repaired for real
                cm.setValue(kept.replace(
                    "public typealias Place = Zone_src\\n}\\npublic typealias Owns_3_carol",
                    "public typealias Place = Zone_docs\\n}\\npublic typealias Owns_3_carol"));
                await tick(true);
                step("a mended world goes green and is kept",
                     document.getElementById("verdicts").textContent === "" ||
                     localStorage.getItem("gate.pages.ownership.swift") !== null);
                step("reset stands ready", typeof window.__resetDemo === "function");
            } catch (e) {
                steps.push("ROADFAIL crashed: " + e.message);
            }
            const report = document.createElement("pre");
            report.id = "roadtest-report";
            report.textContent = steps.join("\\n") + "\\n"
                + (steps.every(s => s.startsWith("ROADPASS"))
                    ? "ROAD ALL GREEN" : "ROAD RED");
            document.body.append(report);
            document.title = steps.every(s => s.startsWith("ROADPASS"))
                ? "ROAD ALL GREEN" : "ROAD RED";
        });
    }
    window.__resetDemo = function () {
        try {
            for (const key of Object.keys(localStorage)) {
                if (key.startsWith("gate.pages.") || key === "gate.theme.declared") {
                    localStorage.removeItem(key);
                }
            }
        } catch (e) { }
        location.reload();
    };
})();
</script>
<style>
/* the note takes its own strip: the body is one viewport high, so it is
   shortened by the strip's height and nothing of the bench is covered */
body { height: calc(100vh - 28px) !important; }
#published-note { position: fixed; bottom: 0; left: 0; right: 0; z-index: 99;
  height: 28px; box-sizing: border-box; overflow: hidden; white-space: nowrap;
  font: 12px/16px ui-monospace, monospace; padding: 6px 12px;
  background: #101010; color: #9a9a9a; border-top: 1px solid #2a2a2a; }
#published-note code { color: #c9c9c9; }
#published-note a { color: #c9c9c9; }
</style>
"""
    shim = (shim.replace("__SNAP__", json.dumps(snap))
                .replace("__FORMS__", json.dumps(sorted(forms)))
                .replace("__LAYOUT__", json.dumps(layout))
                .replace("__ALL__", json.dumps(list(dict.fromkeys(everyone)))))
    note = ('<div id="published-note">judged in your browser as you type · '
            'saved on green, in this browser · <a href="#" '
            'onclick="__resetDemo();return false">reset the demo</a> · '
            'the tool: <code>git clone '
            'https://github.com/DanielSwift1992/gate</code></div>')

    marker = '<link rel="stylesheet" href="codemirror.css">'
    if marker not in ui:
        raise SystemExit("build-pages: ui.html changed shape, the shim has no place to stand")
    ui = ui.replace(marker, shim + marker, 1)
    ui = ui + note

    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(ui)
    open(os.path.join(OUT, "ladder.css"), "w", encoding="utf-8").write(ladder_css)
    for asset in ("codemirror.css", "codemirror.js", "judge.js"):
        src = os.path.join(HERE, asset)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(OUT, asset))
    shutil.copy(os.path.join(HERE, "bin", "judge-where.js"),
                os.path.join(OUT, "judge-where.js"))
    print(f"published bench written to {OUT}: "
          f"{len(snap)} recorded answers, {len(names)} names")


if __name__ == "__main__":
    main()
