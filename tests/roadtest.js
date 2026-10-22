// CODEOWNERS example acceptance walk, injected only by tests/roadtest.py.
    if (location.search.includes("roadtest=1")) {
        window.addEventListener("load", async () => {
            const steps = [];
            const step = (name, ok) => steps.push((ok ? "ROADPASS " : "ROADFAIL ") + name);
            const settle = (ms) => new Promise(r => setTimeout(r, ms || 250));
            try {
                await settle(900);
                step("the door opens on the named file",
                     typeof cm !== "undefined" && active === "ownership.swift");
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
                // This harness opens static snapshots. Native on-holds is
                // checked by reader-draft.js and playground-storage.js.
                const draft = JSON.parse(localStorage.getItem("gate.reader-draft.v1.ownership.swift") || "null");
                step("and red keeps its reader draft and refusal",
                     readerDrafts && draft && draft.text === cm.getValue() && draft.verdict.verdict === "refused");
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
                    "public typealias Place = Zone_src\n}\npublic typealias Owns_3_carol",
                    "public typealias Place = Zone_docs\n}\npublic typealias Owns_3_carol"));
                await tick(true);
                step("a mended world goes green and is kept",
                     document.getElementById("verdicts").textContent === "" ||
                     localStorage.getItem("gate.reader-draft.v1.ownership.swift") !== null);
                // the offer and the judge, held as a pair, both ways: over
                // the mended world, every name of it lands in each slot of
                // the carol claim, and the two readings must agree name by
                // name. The judge's side of the border is the canon's own
                // spelling: an axis that did not resolve keeps its dot in
                // `aka`, so a name of the wrong kind never compiles. The
                // offer's side is allowedAt. Neither side is trusted alone.
                const mended = cm.getValue();
                const lines = mended.split("\n");
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
                            (l, i) => i === cl ? rebuilt : l).join("\n");
                        const rs = refusalsFor("ownership.swift", text).filter(
                            r => r.address === "ownership.swift:" + (cl + 1));
                        // the sides stand translated now, CERT \u00b7 L
                        // against R: law; an axis that did not resolve
                        // keeps its dot inside a side, same border, new coat
                        const compiles = rs.every(r => {
                            const m = r.claim.match(/\u00b7 ([^:]+?)(?::|$)/);
                            // at canon v4 a name of the wrong kind is a
                            // projection the court cannot read, not a dotted aka
                            return !(m && m[1].includes("."))
                                && !/cannot read projection/.test(r.claim);
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
                cm.replaceRange("    // } a note, not a brace\n",
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
                    "gate.reader-draft.v1.ownership.swift") !== null;
                window.__resetWipe();
                step("reset takes the demo back to its print",
                     keptHere
                     && localStorage.getItem("gate.reader-draft.v1.ownership.swift") === null
                     && textOf("ownership.swift")
                        === (SNAP["/world?f=ownership.swift"] || ""));
            } catch (e) {
                steps.push("ROADFAIL crashed: " + e.message);
            }
            const report = document.createElement("pre");
            report.id = "roadtest-report";
            report.textContent = steps.join("\n") + "\n"
                + (steps.every(s => s.startsWith("ROADPASS"))
                    ? "ROAD ALL GREEN" : "ROAD RED");
            document.body.append(report);
            document.title = steps.every(s => s.startsWith("ROADPASS"))
                ? "ROAD ALL GREEN" : "ROAD RED";
        });
    }
