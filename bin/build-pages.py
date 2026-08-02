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
    /* the verdict a person reads is a translation of the canon line, and
       the show has two surfaces by right: the terminal translates in the
       CLI, this page translates here. Two spellings of one small formula
       over one set of data, the world's own /// notes; what gates the
       pair is the road, which holds this page's sentence to the server's
       recorded one word for word. */
    function lawNotes(text) {
        const out = {};
        const lines = (text || "").split("\\n");
        for (let i = 0; i < lines.length; i++) {
            const m = lines[i].trim().match(
                /^public (?:protocol|enum|typealias) (\\w+)/);
            if (!m || out[m[1]] !== undefined) continue;
            const said = [];
            for (let j = i - 1; j >= 0; j--) {
                const s = lines[j].trim();
                if (!s.startsWith("///")) break;
                said.unshift(s.slice(3).trim());
            }
            if (said.length) out[m[1]] = said.join(" ").trim();
        }
        return out;
    }
    function plainly(claim, notes) {
        const m = claim.match(/^'(\\w+)[^']*' requires the types '[^']*' \\(aka '([^']+)'\\) and '[^']*' \\(aka '([^']+)'\\) be equivalent(?: \\[(\\w+)\\])?/);
        if (!m) return claim;
        const said = notes[m[4] || ""];
        return m[1] + " \\u00b7 " + m[2] + " against " + m[3]
            + (said ? ": " + said : "");
    }
    function refusalsFor(f, text) {
        const out = [];
        if (FORMS.has(f)) {
            let stream = text;
            for (const other of FORMS) {
                if (other !== f) stream += "\\n" + textOf(other);
            }
            const notes = lawNotes(stream);
            for (const r of judgeWhereTexts(stream, []).refusals) {
                const m = r.match(/'(\\w+)/);
                if (!m || !text.includes(m[1])) continue;
                const bare = r.replace(/^\\s*\\u2717\\s*/, "");
                out.push({ address: f + ":" + lineOf(text, m[1]),
                           claim: plainly(bare, notes) });
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
                // the page's own court against the server's recorded
                // one, on the untouched world: two translators, one
                // formula, and the sentence must match word for word.
                const snapV = JSON.parse(
                    SNAP["/verdict?f=ownership.swift"] || "{}");
                const liveV = await (await fetch("/verdict?f=ownership.swift",
                    { method: "POST",
                      body: textOf("ownership.swift") })).json();
                const rkey = rs => (rs || []).map(
                    r => r.address + " :: " + r.claim).sort().join(" || ");
                step("the shim court and the server court say one sentence",
                     snapV.refusals !== undefined
                     && rkey(liveV.refusals) === rkey(snapV.refusals));
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
                // the refusal is a door: a click on the row lands the hand
                // on the claim's own line, in Full, selected
                const row = document.querySelector("#verdicts .refusal");
                const said = row ? (row.querySelector("code") || {}).textContent || "" : "";
                const saidLine = parseInt(said.split(":")[1], 10);
                if (row) row.click();
                await settle();
                const sel = cm.listSelections()[0];
                step("a refusal click lands on its own line",
                     !!row && mode === "full" && Number.isFinite(saidLine)
                     && sel && sel.head.line === saidLine - 1);
                // mend the world: carol's one refusal is repaired for real
                cm.setValue(kept.replace(
                    "public typealias Place = Zone_src\\n}\\npublic typealias Owns_3_carol",
                    "public typealias Place = Zone_docs\\n}\\npublic typealias Owns_3_carol"));
                await tick(true);
                step("a mended world goes green and is kept",
                     document.getElementById("verdicts").textContent === "" ||
                     localStorage.getItem("gate.pages.ownership.swift") !== null);
                // the offer and the judge, held as a pair, both ways: over
                // the mended world, every name of it lands in each slot of
                // the carol claim, and the two readings must agree name by
                // name. The judge's side of the border is the canon's own
                // spelling: an axis that did not resolve keeps its dot in
                // `aka`, so a name of the wrong kind never compiles. The
                // offer's side is allowedAt. Neither side is trusted alone.
                const mended = cm.getValue();
                const lines = mended.split("\\n");
                const cl = lines.findIndex(l => l.includes("Owns_3_carol"));
                const claim = lines[cl];
                const lt = claim.indexOf("<");
                const args = claim.slice(lt + 1, claim.lastIndexOf(">"))
                    .split(",").map(s => s.trim());
                const names = [...new Set(Object.values(conformers).flat())]
                    .concat(["Wombat"]);
                let pairOk = true, judged = 0;
                for (let slot = 0; slot < args.length && pairOk; slot++) {
                    const here = allowedAt({ line: cl,
                        ch: claim.indexOf(args[slot], lt) + args[slot].length });
                    const offered = new Set((here && here.items) || []);
                    for (const name of names) {
                        const rebuilt = claim.slice(0, lt + 1) + args.map(
                            (a, i) => i === slot ? name : a).join(", ") + ">";
                        const text = lines.map(
                            (l, i) => i === cl ? rebuilt : l).join("\\n");
                        const rs = refusalsFor("ownership.swift", text).filter(
                            r => r.address === "ownership.swift:" + (cl + 1));
                        // the sides stand translated now, CERT \u00b7 L
                        // against R: law; an axis that did not resolve
                        // keeps its dot inside a side, same border, new coat
                        const compiles = rs.every(r => {
                            const m = r.claim.match(/\u00b7 ([^:]+?)(?::|$)/);
                            return !(m && m[1].includes("."));
                        });
                        judged += 1;
                        if (compiles !== offered.has(name)) { pairOk = false; break; }
                    }
                }
                step("the offer and the judge agree at every slot ("
                     + judged + " names judged)", pairOk && judged > 20);
                // a note keeps no grammar in Bare either: a brace spelled in
                // a comment inside a record must not shorten the record's
                // span, or removing it through Bare would cut the body in
                // half and leave the world unparseable
                const ownerAt = lines.findIndex(
                    l => l.includes("enum Owner_carol"));
                cm.replaceRange("    // } a note, not a brace\\n",
                    { line: ownerAt + 1, ch: 0 },
                    { line: ownerAt + 1, ch: 0 }, "+input");
                await settle();
                const span = locateSlot({ kind: "record", line: ownerAt + 1 });
                const spanned = span
                    ? cm.getRange(span.from, span.to) : "";
                step("a note holds no brace for Bare",
                     spanned.includes("WardenKey") && spanned.trim().endsWith("}"));
                cm.replaceRange("", { line: ownerAt + 1, ch: 0 },
                    { line: ownerAt + 2, ch: 0 }, "+delete");
                await settle();
                // Bare draws the same world as slots a hand can fill: the
                // door from a verdict to an edit is one view away
                setMode("bare");
                await settle();
                const placeable = document.querySelectorAll(
                    "#bare .slot:not(.elsewhere)").length;
                setMode("full");
                step("Bare offers placeable slots", placeable > 0);
                // the rail is a door too: a click on a file's name opens
                // it, and the letter's marks are lit lines of the file
                // itself, worn in Bare
                const lrow = [...document.querySelectorAll("#filelist .file")]
                    .find(r => r.textContent.includes("readme.swift"));
                if (lrow) lrow.click();
                await settle(); await settle();
                setMode("bare");
                await settle();
                const lit = document.querySelectorAll("#bare .mark").length;
                setMode("full");
                step("the rail opens the letter and its marks are lit",
                     !!lrow && active === "readme.swift" && lit >= 5);
                const orow = [...document.querySelectorAll("#filelist .file")]
                    .find(r => r.textContent.includes("ownership.swift"));
                if (orow) orow.click();
                await settle(); await settle();
                step("and the rail leads back", active === "ownership.swift");
                // reset executed for real: what was kept is forgotten and
                // the world is the print again; the reload is a gesture
                const keptHere = localStorage.getItem(
                    "gate.pages.ownership.swift") !== null;
                window.__resetWipe();
                step("reset takes the demo back to its print",
                     keptHere
                     && localStorage.getItem("gate.pages.ownership.swift") === null
                     && textOf("ownership.swift")
                        === (SNAP["/world?f=ownership.swift"] || ""));
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
    /* the wipe and the reload are two acts: the wipe is the one logic of
       forgetting, the reload is a gesture over it. The road executes the
       wipe alone, so what it judges is what the reset button does. */
    window.__resetWipe = function () {
        try {
            for (const key of Object.keys(localStorage)) {
                if (key.startsWith("gate.pages.") || key === "gate.theme.declared") {
                    localStorage.removeItem(key);
                }
            }
        } catch (e) { }
    };
    window.__resetDemo = function () {
        window.__resetWipe();
        location.reload();
    };
})();
</script>
<style>
/* the note takes its own strip: the body is one viewport high, so it is
   shortened by the strip's height and nothing of the bench is covered.
   One height, spelled once: the body's cut and the strip wear the same
   variable, so the two numbers cannot part. */
:root { --strip: 28px; }
body { height: calc(100vh - var(--strip)) !important; }
#published-note { position: fixed; bottom: 0; left: 0; right: 0; z-index: 99;
  height: var(--strip); box-sizing: border-box; overflow: hidden; white-space: nowrap;
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
