#!/usr/bin/env python3
# Publishes the bench over explicitly selected inputs. The parts are the
# ones already shipped: the same ui.html, the same browser judges, and the
# server's own answers, recorded at build time from a live `gate serve` so
# the page carries no second reading of any endpoint. On a keystroke the
# open file is judged in the browser, the where court by the corpus court built for wasm32 (bin/court-wasm) and
# the plain court by judge.js; the full cross-file court and the write path
# belong to the clone, and the page says so on its face.
import argparse
import hashlib
import html
import json
from bench_csp import stamp_csp, script_json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from urllib.parse import quote

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(HERE, "gate")
PUBLICATION_ROOT = None



def get(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=120) as r:
        return r.read().decode("utf-8")


def post(port, path, body):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
                                 data=body.encode("utf-8"), method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8")


def publish(source, out, context=None):
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
    serve = subprocess.Popen([GATE, "serve", str(port), "--no-open"],
                             cwd=source, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

        drawing_plan = json.loads(get(port, "/drawing-profile"))
        from drawing_profile import publish as publish_drawing
        drawing = publish_drawing(HERE, PUBLICATION_ROOT or out, out, drawing_plan, port)
        snap["/drawing-profile"] = json.dumps(drawing_plan)
        files = json.loads(snap["/files"])
        if context:
            context["carried"] = files.get("carried") or []
        everyone = list(files["files"]) + [files["layout"]]
        texts = {}
        for f in dict.fromkeys(everyone):
            snap[f"/world?f={f}"] = texts[f] = get(port, f"/world?f={f}")
            snap[f"/gitstatus?f={f}"] = get(port, f"/gitstatus?f={f}")
            snap[f"/verdict?f={f}"] = post(port, f"/verdict?f={f}", texts[f])

        if context and context.get("drawing"):
            # Bind the declared owner remainder to these exact initial bytes.
            hashes = sorted(hashlib.sha256(texts[f].encode()).hexdigest() for f in files.get("drawing_inputs", []))
            context["drawing"]["source_digest"] = hashlib.sha256(json.dumps(hashes, separators=(",", ":")).encode()).hexdigest()

        shelf = json.loads(snap["/shelf"])
        for m in (shelf.get("modules") or []) if isinstance(shelf, dict) else []:
            snap[f"/shelf?m={m}"] = get(port, f"/shelf?m={m}")

        if context:
            # A frozen input uses the shelf's ordinary read-only path. The same
            # declaration parse that orders the build records each name's door.
            context["definitions"] = [dict(name=f, text=texts[f]) for f in context.pop("definition_paths", [])]
            catalog = dict(context.pop("catalog"))
            declared_text = texts[catalog.pop("source")]
            if hashlib.sha256(declared_text.encode()).hexdigest() != catalog["sha256"]:
                raise ValueError("the declared catalog differs from the selected pinned input")
            catalog["text"] = declared_text
            mod = catalog["file"].removesuffix(".swift")
            snap[f"/shelf?m={mod}"] = catalog.pop("text")
            shelf.setdefault("modules", []).append(mod)
            shelf.setdefault("inputs", {})[mod] = catalog
            snap["/shelf"] = json.dumps(shelf)

        ladder_css = get(port, "/ladder.css")
        names = sorted(set(re.findall(r"(?:enum|protocol|typealias)\s+(\w+)",
                                      "\n".join(texts.values()))))
        for n in (names if not context else []):
            try:
                snap[f"/value?name={n}"] = get(port, f"/value?name={n}")
            except Exception:
                pass
    finally:
        serve.terminate()
        serve.wait()

    ui = open(os.path.join(HERE, "web", "ui.html"), encoding="utf-8").read()
    for asset in ("codemirror.css", "ladder.css", "codemirror.js", "judge.js", "renderer.js", "press.js", "drawing-profile.js"):
        ui = ui.replace(f'"/{asset}"', f'"{asset}"')

    if drawing:
        ui = ui.replace('<link rel="stylesheet" href="ladder.css">',
            '<link rel="stylesheet" href="ladder.css"><link rel="stylesheet" data-drawing-profile href="' + html.escape(drawing['href'], quote=True) + '">', 1)

    forms = set(files.get("forms") or [])
    layout = files.get("layout")
    shim = """
<script src="court/vi_court.js"></script>
<script src="court/vi_court_bytes.js"></script>
<script>
/* THE COURT ON THE PAGE. The certificate court is the corpus court built for
   wasm32 at the pin bin/court-wasm.from records (bin/build-court-wasm.sh).
   It travels inside the page as bytes, because a page opened from a file
   cannot fetch its neighbour, and it is instantiated here, synchronously,
   before any keystroke. judgeWhereTexts speaks the shape the bench reads:
   the court's own refusal lines, and its exit. */
wasm_bindgen.initSync({ module: Uint8Array.from(atob(VI_COURT_WASM_BASE64), (c) => c.charCodeAt(0)) });
function judgeWhereTexts(text, extraTexts) {
    const files = [{ name: "world.swift", text: text }];
    const args = ["where", "world.swift"];
    (extraTexts || []).forEach((t, i) => {
        files.push({ name: "definitions-" + i + ".swift", text: t });
        args.push("definitions-" + i + ".swift");
    });
    const a = JSON.parse(wasm_bindgen.judge(JSON.stringify({ arguments: args, files: files })));
    const refusals = (a.stdout + a.stderr).split("\\n").filter((l) => l.startsWith("\\u2717"));
    const m = a.stdout.match(/(\\d+) equalities and (\\d+) memberships judged across (\\d+) uses/);
    return { exit: a.exit, refusals: refusals, judged: m ? +m[1] : 0,
             members: m ? +m[2] : 0, uses: m ? +m[3] : 0 };
}
/* THE PUBLISHED BENCH. Every answer below was recorded from a live `gate
   serve` over the selected world at build time; on a keystroke the open file is
   judged here in the browser. The write path and the cross-file court
   belong to the clone. */
(function () {
    const SNAP = __SNAP__;
    const CONTEXT = __CONTEXT__;
    const STORAGE = __STORAGE__;
    const FORMS = new Set(__FORMS__);
    const WORLD_FILES = JSON.parse(SNAP["/files"]).world_files || [];
    const DOCUMENTS = JSON.parse(SNAP["/files"]).documents || [];
    const LAYOUT = __LAYOUT__;
    const THEIRS = JSON.parse(SNAP["/files"]).theirs || {};
    // A carried reading is not another input to the relation court.
    const ALL = __ALL__.filter(f => THEIRS[f]?.kind !== "CarriedFile");
    /* the forms are judged in worlds, and the worlds are the server's: it
       joins forms by the names they use and declare (worldsOf in the vein),
       and records the partition here at build time, so the page never grows
       a second rule over the same files. Until the server records one, a
       form is its own world. */
    const WORLDS = __WORLDS__;
    function worldOf(f) {
        for (const w of WORLDS) { if (w.includes(f)) return w; }
        return [f];
    }
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
    /* A published world stores reader text and its verdict, including red.
       An ordinary selected repository retains its on-green policy. A saved verdict is a
       receipt for that text, never a substitute for judging the reopened world. */
    function keptDraft(f) {
        if (THEIRS[f]) return null;
        try {
            const raw = localStorage.getItem(STORAGE + f);
            if (raw === null) return null;
            if (CONTEXT) {
                try {
                    const row = JSON.parse(raw);
                    if (row.format === 1 && typeof row.text === "string") return row;
                    if (row.format === 2 && Array.isArray(row.splices)) {
                        let text = SNAP["/world?f=" + f] || "";
                        for (const cut of row.splices) {
                            if (!Number.isInteger(cut.from) || !Number.isInteger(cut.to) || cut.from < 0
                                || cut.to < cut.from || cut.to > text.length || typeof cut.insert !== "string")
                                throw new Error("invalid reader splice");
                            text = text.slice(0, cut.from) + cut.insert + text.slice(cut.to);
                        }
                        return { text, verdict: row.verdict, splices: row.splices };
                    }
                } catch (e) { }
            }
            return { text: raw, verdict: null }; // old browser drafts remain readable
        } catch (e) { return null; }
    }
    function textOf(f) {
        const row = keptDraft(f);
        return row ? row.text : SNAP["/world?f=" + f] || "";
    }
    // A five-megabyte source is already pinned in SNAP. Keep the reader's
    // splice against those bytes, not a second full copy beyond localStorage's
    // quota. This is lossless text, including edits outside the visible page.
    function draftRecord(f, text, verdict) {
        const base = SNAP["/world?f=" + f] || "";
        if (base.length < 300000) return { format: 1, text, verdict };
        const splice = (base, text) => {
            let from = 0, tail = 0;
            while (from < base.length && from < text.length && base[from] === text[from]) from++;
            while (tail < base.length - from && tail < text.length - from
                && base[base.length - 1 - tail] === text[text.length - 1 - tail]) tail++;
            return { from, to: base.length - tail, insert: text.slice(from, text.length - tail) };
        };
        const direct = [splice(base, text)], previous = keptDraft(f);
        const chain = previous && previous.splices ? [...previous.splices, splice(previous.text, text)] : direct;
        const splices = JSON.stringify(chain).length < JSON.stringify(direct).length ? chain : direct;
        return { format: 2, splices, verdict };
    }
    const readings = new Map();
    function readDraft(f, text) {
        const texts = Object.fromEntries(ALL.map(g => [g, g === f ? text : textOf(g)]));
        const inputs = JSON.stringify(texts), previous = readings.get(f);
        if (previous && previous.inputs === inputs) return previous.answer;
        const answer = GateWorldCourt.verdict(wasm_bindgen, WORLDS, texts,
            CONTEXT.definitions, WORLD_FILES, CONTEXT.carried,
            LAYOUT, judge, (claim, stream) => plainly(claim, lawNotes(stream)), CONTEXT.plain_fragments,
            { lint, pageGuards, vocabulary: kitVocabulary, names: CONTEXT.guard_names }, DOCUMENTS);
        answer.compiler = "page bodies have not been checked by Swift";
        readings.set(f, { inputs, answer });
        return answer;
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
            /* the form is judged inside its world, the pieces in the server's
               order with this file's live text in its place; a refusal that
               names a line is read in this file's own numbering, and a line
               of another piece belongs to that piece's page */
            const world = worldOf(f);
            const pieces = world.map((g) => g === f ? text : textOf(g));
            const stream = pieces.join("\\n");
            let offset = 0;
            for (const g of world) { if (g === f) break; offset += pieces[world.indexOf(g)].split("\\n").length; }
            const mine = text.split("\\n").length;
            const notes = lawNotes(stream);
            const court = judgeWhereTexts(stream, []);
            /* a file with no gated claim is not refused, it has nothing to
               judge; any other form the court cannot read is refused at the
               line it names, never passed over */
            const nothingToJudge = court.exit === 2 && court.refusals.length === 1
                && court.refusals[0].includes("no equalities or memberships were judged");
            if (court.exit === 2 && !nothingToJudge) {
                for (const r of court.refusals) {
                    const ln = r.match(/line (\\d+)/);
                    /* a projection the court cannot read names its owner,
                       not a claim: every certificate that applies that owner
                       as an argument meets the same projection, so the
                       refusal lands on each of their lines; the court itself
                       stops at the first and the page cannot tell which */
                    const proj = r.match(/cannot read projection '(\\w+)\\./);
                    const claim = r.replace(/^\\s*\\u2717\\s*THE WHERE:\\s*/, "");
                    const applying = proj ? text.split("\\n").map((l, i) => [l, i + 1]).filter(
                        ([l]) => new RegExp("typealias \\\\w+ = \\\\w+<.*\\\\b" + proj[1] + "\\\\b").test(l))
                        .map(([, n]) => n) : [];
                    if (ln) {
                        const at = +ln[1] - offset;
                        if (at >= 1 && at <= mine) out.push({ address: f + ":" + at, claim });
                    } else if (applying.length) {
                        for (const n of applying) out.push({ address: f + ":" + n, claim });
                    } else if (world.length === 1 || world[0] === f) {
                        out.push({ address: f + ":1", claim });
                    }
                }
            }
            for (const r of court.exit === 2 ? [] : court.refusals) {
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
            if (THEIRS[f]) return reply(JSON.stringify({ address: THEIRS[f].address,
                reason: f + ": Theirs is read-only; change the owner and take a new pin" }), 409);
            const text = String((opts && opts.body) || "");
            const row = CONTEXT ? JSON.stringify(draftRecord(f, text, readDraft(f, text))) : text;
            try {
                localStorage.setItem(STORAGE + f, row);
            } catch (e) { return reply(JSON.stringify({ note: "browser storage unavailable" }), 507); }
            return reply("", 200);
        }
        if (method === "PUT") return reply("", 200);
        if (method === "POST" && u.startsWith("/verdict")) {
            const f = decodeURIComponent(u.split("f=")[1] || "");
            const text = opts && opts.body ? String(opts.body) : "";
            const said = JSON.parse(SNAP["/verdict?f=" + f] || "{}");
            if (THEIRS[f]) return reply(JSON.stringify(said));
            if (CONTEXT) return reply(JSON.stringify(readDraft(f, text)));
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
        if (CONTEXT && method === "GET" && u === "/version")
            return reply(JSON.stringify({ ...JSON.parse(SNAP["/version"]), playground: CONTEXT }));
        if (CONTEXT && method === "GET" && u === "/files")
            return reply(JSON.stringify({ ...JSON.parse(SNAP["/files"]), save_policy: "reader-draft" }));
        if (CONTEXT && method === "GET" && u.startsWith("/gitstatus?f=")) {
            const row = keptDraft(decodeURIComponent(u.split("f=")[1] || ""));
            return reply(JSON.stringify(row ? { git: "draft", verdict: row.verdict ? row.verdict.verdict : "not yet judged" }
                : { git: "source" }));
        }
        const recorded = u.replace(/%2F/gi, "/");
        if (u.startsWith("/") && SNAP[recorded] !== undefined) return reply(SNAP[recorded]);
        if (u.startsWith("/")) return reply("{}", 404);
        return real(url, opts);
    };
    /* the wipe and the reload are two acts: the wipe is the one logic of
       forgetting, the reload is a gesture over it. The road executes the
       wipe alone, so what it judges is what the reset button does. */
    window.__resetWipe = function () {
        try {
            for (const key of Object.keys(localStorage)) {
                if (CONTEXT ? key.startsWith(STORAGE)
                    : ALL.some(f => key === STORAGE + f) || key === "gate.theme.declared"
                        || key === "gate.bench.layout") {
                    localStorage.removeItem(key);
                }
            }
        } catch (e) { }
    };
    document.addEventListener("click", function (event) {
        if (!event.target.closest("#reset-copy")) return;
        event.preventDefault(); window.__resetCopy();
    });
    window.__resetCopy = function () {
        window.__resetWipe();
        location.reload();
    };
})();
</script>
"""
    shim = (shim.replace("__SNAP__", script_json(snap))
                .replace("__CONTEXT__", script_json(context))
                .replace("__STORAGE__", script_json("gate.pages." if not context else
                    "gate.pages." + context["pin"] + "." + context["world"] + "."))
                .replace("__FORMS__", script_json(sorted(forms)))
                .replace("__WORLDS__", script_json(files.get("worlds") or []))
                .replace("__LAYOUT__", script_json(layout))
                .replace("__ALL__", script_json(list(dict.fromkeys(everyone)))))
    note = ('<div id="published-note"><details><summary>browser copy</summary>'
            '<div>judged in your browser as you type · '
            'saved on green, in this browser · '
            'the tool: <code>git clone '
            'https://github.com/DanielSwift1992/gate</code></div></details>'
            '<a href="#" id="reset-copy">reset this browser copy</a></div>')

    if context:
        note = note.replace('saved on green, in this browser', 'draft and verdict saved in this browser, including refusals')

    marker = '<link rel="stylesheet" href="codemirror.css">'
    if marker not in ui:
        raise SystemExit("build-pages: ui.html changed shape, the shim has no place to stand")
    ui = ui.replace(marker, shim + marker, 1)
    if context:
        scope = "gate.pages." + context["pin"] + "." + context["world"] + "."
        ui = ui.replace('<title>gate · world bench</title>', '<title>gate · ' + html.escape(context['tab']['title']) + '</title>')
        ui = ui.replace('"gate.theme.declared"', script_json(scope + "theme"))
        ui = ui.replace('"gate.bench.layout"', script_json(scope + "layout"))
        ui = ui.replace('<script src="court/vi_court.js">',
            '<script src="playground-lint.js"></script><script src="playground-guards.js"></script>'
            '<script src="world-court.js"></script><script src="court/vi_court.js">', 1)


    marker = '</div>\n<script src="codemirror.js">'
    if ui.count(marker) != 1:
        raise ValueError("bench template has no unique main column boundary")
    ui = stamp_csp(ui.replace(marker, note + marker, 1))

    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(ui)
    open(os.path.join(out, "ladder.css"), "w", encoding="utf-8").write(ladder_css)
    for asset, home in (("codemirror.css", "web"), ("codemirror.js", "web"),
                        ("judge.js", "bin"), ("renderer.js", "bin"), ("press.js", "bin"),
                        ("drawing.from", "bin"), ("press-contract.from", "bin"), ("drawing-profile.js", "bin"), ("drawing-fonts.json", "bin")):
        src = os.path.join(HERE, home, asset)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(out, asset))
    os.makedirs(os.path.join(out, "court"), exist_ok=True)
    for asset in ("vi_court.js", "vi_court_bytes.js"):
        shutil.copy(os.path.join(HERE, "bin", "court-wasm", "web", asset),
                    os.path.join(out, "court", asset))
    shutil.copy(os.path.join(HERE, "bin", "court-wasm.from"),
                os.path.join(out, "court", "court-wasm.from"))
    if context:
        for asset in ("world-court.js", "playground-lint.js", "playground-guards.js"):
            shutil.copy(os.path.join(HERE, "bin", asset), os.path.join(out, asset))
        with open(os.path.join(out, "snapshots.json"), "w", encoding="utf-8") as f:
            json.dump(snap, f, indent=2)
        with open(os.path.join(out, "world.json"), "w", encoding="utf-8") as f:
            json.dump(context, f, indent=2)
    print(f"published bench written to {out}: "
          f"{len(snap)} recorded answers, {len(names)} names")
    return ladder_css


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", nargs="?", default=os.path.join(HERE, "_site"))
    parser.add_argument("--worlds", action="store_true", help="publish the pinned showcase catalog at playground/")
    parser.add_argument("--source", help="publish this explicitly selected repository at the site root")
    args = parser.parse_args()
    if not args.worlds and not args.source:
        parser.error("name --source <repository>, --worlds, or both")
    global PUBLICATION_ROOT
    PUBLICATION_ROOT = args.out
    from drawing_profile import begin, finish
    begin(args.out)
    if args.source:
        ladder = publish(os.path.abspath(args.source), args.out)
    if args.worlds:
        from playground_pages import build_worlds
        ladder = build_worlds(HERE, args.out, publish)
    finish(args.out)
    from bench_styles import audit_site
    print("interface tokens:", audit_site(args.out, ladder))


if __name__ == "__main__":
    main()
