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
    window.fetch = async function (url, opts) {
        const u = String(url);
        const method = (opts && opts.method) || "GET";
        if (method === "PUT") {
            return reply(JSON.stringify({ refused:
                "the published bench keeps no files: edits live in the editor "
                + "here, and saving belongs to the clone" }), 403);
        }
        if (method === "POST" && u.startsWith("/verdict")) {
            /* the file judges itself, and the rest of the world stands as the
               server judged it at build time: the recorded verdict minus the
               open file's own lines is the background, and the open file's
               fresh refusals join it. A page the server does not judge for
               junk, a form's prose, the layout, is not judged for junk here
               either: the same court, never a stricter or a kinder one. */
            const f = decodeURIComponent(u.split("f=")[1] || "");
            const text = opts && opts.body ? String(opts.body) : "";
            const said = JSON.parse(SNAP["/verdict?f=" + f] || "{}");
            const background = (said.refusals || []).filter(
                r => !String(r.address || "").startsWith(f + ":"));
            let fresh = [];
            if (FORMS.has(f)) {
                /* the certificate court reads one stream per world, the way
                   the server feeds it: a form's gates may be declared on a
                   sibling page, so the open text is judged together with the
                   other form pages, and only the refusals whose certificate
                   is written in the open text are fresh here; the others are
                   the background's to carry. */
                let stream = text;
                for (const other of FORMS) {
                    if (other !== f) stream += "\\n" + (SNAP["/world?f=" + other] || "");
                }
                for (const r of judgeWhereTexts(stream, []).refusals) {
                    const m = r.match(/'(\\w+)/);
                    if (!m || !text.includes(m[1])) continue;
                    fresh.push({ address: f + ":" + lineOf(text, m[1]),
                                 claim: r });
                }
            } else if (f !== LAYOUT) {
                for (const r of judge(f, text).refusals) {
                    fresh.push({ address: f + ":" + r.line, claim: r.premise });
                }
            }
            const refusals = background.concat(fresh);
            said.verdict = refusals.length ? "refused" : "holds";
            said.refusals = refusals;
            return reply(JSON.stringify(said));
        }
        if (u.startsWith("/") && SNAP[u] !== undefined) return reply(SNAP[u]);
        if (u.startsWith("/")) return reply("{}", 404);
        return real(url, opts);
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
</style>
"""
    shim = (shim.replace("__SNAP__", json.dumps(snap))
                .replace("__FORMS__", json.dumps(sorted(forms)))
                .replace("__LAYOUT__", json.dumps(layout)))
    note = ('<div id="published-note">the demo, judged in your browser as you '
            'type · nothing is saved here · the tool: '
            '<code>git clone https://github.com/DanielSwift1992/gate</code></div>')

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
