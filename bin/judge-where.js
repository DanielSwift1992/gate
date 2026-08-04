#!/usr/bin/env node
// THE WHERE, ported. A line-for-line translation of the corpus's
// WhereJudge.swift, the way judge.js translates the plain judge: same
// arguments in, same lines out, and the battery holds the two courts to one
// verdict on every shelf page. The reference's own comment is the contract:
// «The port's judge and this one must always agree, and the compiler stays
// the standard both answer to.» It is deliberately self-contained, because
// the reference is: WhereJudge shares no code with the plain judge, so this
// file shares none with judge.js, and a drift in one canon cannot hide
// behind the other.

const fs = typeof require !== "undefined" ? require("fs") : null;

const CANON_VERSION = 2;

function fail(message) {
    if (typeof process !== "undefined" && process.stderr) {
        process.stderr.write("✗ THE WHERE: " + message + "\n");
        process.exit(2);
    }
    throw new Error("THE WHERE: " + message);
}

// ── reading the world ──

function stripComments(text) {
    let inFlagged = false;
    const kept = [];
    for (const line of text.split("\n")) {
        const bare = line.trim();
        if (bare.startsWith("#if")) { inFlagged = true; continue; }
        if (bare.startsWith("#endif")) { inFlagged = false; continue; }
        if (inFlagged) continue;
        const cut = line.indexOf("//");
        kept.push(cut >= 0 ? line.slice(0, cut) : line);
    }
    return kept.join("\n");
}

function captures(pattern, text) {
    const regex = new RegExp(pattern, "gs");
    const out = [];
    let match;
    while ((match = regex.exec(text)) !== null) {
        out.push(match.slice(1).map(piece => piece === undefined ? "" : piece));
    }
    return out;
}

function splitTopLevel(list) {
    const names = [];
    let depth = 0;
    let piece = "";
    for (const character of list) {
        if (character === "<") depth += 1;
        if (character === ">") depth -= 1;
        if (character === "," && depth === 0) {
            names.push(piece);
            piece = "";
        } else {
            piece += character;
        }
    }
    names.push(piece);
    return names;
}

function parameterNames(list) {
    if (!list) return [];
    return splitTopLevel(list).map(piece =>
        piece.split(":")[0].trim());
}

// A gate's where carries three kinds of conjunct: an equality, judged
// against the canon; a membership (a colon and a bare protocol name),
// judged against the conformer's protocols closed over the presented
// refinements; and anything else, refused at its gate by name. Mirrors
// the binary's splitConjuncts, word for word in the refusals.
function splitConjuncts(clause) {
    const equalities = [];
    const memberships = [];
    const unjudged = [];
    for (const part of splitTopLevel(clause)) {
        const bare = part.trim();
        if (!bare) continue;
        const sides = part.split("==");
        if (sides.length === 2) {
            equalities.push([sides[0].trim(), sides[1].trim()]);
            continue;
        }
        const claim = bare.split(":");
        if (claim.length === 2) {
            const lhs = claim[0].trim();
            const proto = claim[1].trim();
            if (lhs && /^\w+$/.test(proto)) {
                memberships.push([lhs, proto]);
                continue;
            }
        }
        unjudged.push(bare);
    }
    return { equalities, memberships, unjudged };
}

function readWorld(text) {
    const clean = stripComments(text);
    const world = { conformers: new Map(), aliases: new Map(), gates: [],
        gatedProtocols: new Map(), protocolParents: new Map(),
        parameters: new Map(), uses: [] };

    for (const hit of captures(
        "enum\\s+(\\w+)\\s*(?:<([^>]*)>)?\\s*:\\s*([\\w,\\s]+?)\\s*\\{([^{}]*)\\}", clean
    )) {
        const name = hit[0];
        const parameters = parameterNames(hit[1]);
        const protocols = hit[2].split(",").map(piece => piece.trim()).filter(Boolean);
        const table = new Map();
        for (const aliasHit of captures("typealias\\s+(\\w+)\\s*=\\s*([^\\n]+)", hit[3])) {
            table.set(aliasHit[0], aliasHit[1].trim());
        }
        world.conformers.set(name, { name, parameters, protocols, table });
    }

    for (const hit of captures("enum\\s+(\\w+)\\s*<([^>]*)>", clean)) {
        world.parameters.set(hit[0], parameterNames(hit[1]));
    }

    for (const hit of captures(
        "extension\\s+(\\w+)\\s*\\{[^{}]*?typealias\\s+(\\w+)\\s*=\\s*([^\\n]+)", clean
    )) {
        const conformer = world.conformers.get(hit[0]);
        if (conformer) conformer.table.set(hit[1], hit[2].trim());
    }

    for (const hit of captures(
        "typealias\\s+(\\w+)\\s*(?:<([^>]*)>)?\\s*=\\s*([^\\n]+)", clean
    )) {
        world.aliases.set(hit[0], {
            parameters: parameterNames(hit[1]), body: hit[2].trim() });
    }

    for (const hit of captures(
        "extension\\s+(\\w+)\\s*:\\s*(\\w+)\\s*\\n\\s*where\\s+([^{]+)\\{", clean
    )) {
        const conjuncts = splitConjuncts(hit[2]);
        world.gates.push({ head: hit[0], proto: hit[1],
            equalities: conjuncts.equalities,
            memberships: conjuncts.memberships,
            unjudged: conjuncts.unjudged });
    }

    for (const hit of captures(
        "protocol\\s+(\\w+)\\s*:\\s*[\\w,\\s]+?\\n\\s*where\\s+([^{]+)\\{", clean
    )) {
        const conjuncts = splitConjuncts(hit[1]);
        world.gatedProtocols.set(hit[0], { name: hit[0],
            equalities: conjuncts.equalities,
            memberships: conjuncts.memberships,
            unjudged: conjuncts.unjudged });
    }

    // the refinement ladder, read from what is presented: a protocol's
    // parents are the material the membership walk closes over
    for (const hit of captures(
        "protocol\\s+(\\w+)\\s*:\\s*([\\w,\\s]+?)\\s*(?:\\n\\s*where|\\{)", clean
    )) {
        world.protocolParents.set(hit[0],
            hit[1].split(",").map(piece => piece.trim()).filter(Boolean));
    }
    for (const hit of captures("protocol\\s+(\\w+)\\s*\\{", clean)) {
        if (!world.protocolParents.has(hit[0])) {
            world.protocolParents.set(hit[0], []);
        }
    }

    for (const hit of captures("([\\w<>,\\. ]+?)\\s*\\.self", clean)) {
        const use = hit[0].trim();
        if (use.includes("<")) world.uses.push(use);
    }
    return world;
}

// ── terms ──

function parseTerm(text) {
    text = text.trim();
    const angle = text.indexOf("<");
    if (angle < 0) return { head: text, args: [] };
    const head = text.slice(0, angle).trim();
    const inner = text.slice(angle + 1, text.lastIndexOf(">"));
    return { head, args: splitTopLevel(inner).map(parseTerm) };
}

function serialize(term) {
    if (term.args.length === 0) return term.head;
    return term.head + "<" + term.args.map(serialize).join(", ") + ">";
}

// ── the canon: one normal form for every term ──

function substitute(term, bindings) {
    if (term.args.length === 0 && bindings.has(term.head)) {
        return bindings.get(term.head);
    }
    const dot = term.head.indexOf(".");
    if (dot >= 0 && term.args.length === 0) {
        const owner = term.head.slice(0, dot);
        const axis = term.head.slice(dot + 1);
        if (bindings.has(owner)) {
            return { head: serialize(bindings.get(owner)) + "." + axis, args: [] };
        }
    }
    return { head: term.head,
        args: term.args.map(piece => substitute(piece, bindings)) };
}

function normalize(term, world, depth) {
    depth = depth || 0;
    if (depth > 64) fail("normalization runs away on '" + serialize(term) + "'");

    if (term.head === "Twice" && term.args.length === 1) {
        const inner = term.args[0];
        return normalize({ head: "Plus", args: [inner, inner] }, world, depth + 1);
    }

    const dot = term.head.indexOf(".");
    if (dot >= 0 && term.args.length === 0) {
        const ownerText = term.head.slice(0, dot);
        const tail = term.head.slice(dot + 1);
        const split = tail.indexOf(".");
        const axis = split >= 0 ? tail.slice(0, split) : tail;
        const rest = split >= 0 ? tail.slice(split + 1) : "";
        const owner = normalize(parseTerm(ownerText), world, depth + 1);
        const conformer = world.conformers.get(owner.head);
        const stated = conformer ? conformer.table.get(axis) : undefined;
        if (conformer && stated !== undefined) {
            const bindings = new Map();
            const names = world.parameters.get(owner.head) || [];
            names.forEach((name, index) => {
                if (index < owner.args.length) bindings.set(name, owner.args[index]);
            });
            const body = substitute(parseTerm(stated), bindings);
            const resolved = normalize(body, world, depth + 1);
            if (!rest) return resolved;
            return normalize(
                { head: serialize(resolved) + "." + rest, args: [] },
                world, depth + 1);
        }
        const stuck = serialize(owner) + "." + axis;
        if (!rest) return { head: stuck, args: [] };
        return { head: stuck + "." + rest, args: [] };
    }

    const alias = world.aliases.get(term.head);
    if (alias && alias.parameters.length === term.args.length) {
        const bindings = new Map();
        alias.parameters.forEach((name, index) => {
            bindings.set(name, term.args[index]);
        });
        const body = substitute(parseTerm(alias.body), bindings);
        return normalize(body, world, depth + 1);
    }

    return { head: term.head,
        args: term.args.map(piece => normalize(piece, world, depth + 1)) };
}

// ── the counting canon: two spellings of one number are one term ──

function counted(term) {
    if (term.args.length > 0) return null;
    if (term.head === "Unit") return 1;
    if (term.head === "Never") return 0;
    if (term.head.startsWith("#")) return parseInt(term.head.slice(1), 10);
    return null;
}

function numeral(count) { return { head: "#" + count, args: [] }; }

function arithmetic(term) {
    const folded = { head: term.head, args: term.args.map(arithmetic) };
    const whole = counted(folded);
    if (whole !== null) return numeral(whole);
    if (folded.head === "Times" && folded.args.length === 2) {
        const left = counted(folded.args[0]);
        const right = counted(folded.args[1]);
        if (left !== null && right !== null) return numeral(left * right);
    }
    if (folded.head !== "Plus" || folded.args.length !== 2) return folded;
    const leaves = [];
    let count = 0;
    const pile = [...folded.args];
    while (pile.length > 0) {
        const piece = pile.pop();
        if (piece.head === "Plus" && piece.args.length === 2) {
            pile.push(...piece.args);
            continue;
        }
        const n = counted(piece);
        if (n !== null) count += n; else leaves.push(piece);
    }
    leaves.sort((a, b) => serialize(a) < serialize(b) ? -1 : 1);
    if (leaves.length === 0) return numeral(count);
    if (count > 0) leaves.push(numeral(count));
    let result = leaves.pop();
    while (leaves.length > 0) {
        result = { head: "Plus", args: [leaves.pop(), result] };
    }
    return result;
}

function canon(text, world) {
    return serialize(arithmetic(normalize(parseTerm(text), world)));
}

// does the conformer wear the protocol: its declared list, closed over
// the refinement ladder the file presents
function wears(conformer, proto, world) {
    const seen = new Set();
    const pile = [...conformer.protocols];
    while (pile.length > 0) {
        const name = pile.pop();
        if (name === proto) return true;
        if (!seen.has(name)) {
            seen.add(name);
            pile.push(...(world.protocolParents.get(name) || []));
        }
    }
    return false;
}

// one membership judged, mirroring the binary word for word: the left
// side resolves through the same canon the equalities use, the resolved
// name must be a presented conformer, and the conformer must wear the
// protocol through the ladder.
function judgeMemberships(memberships, site, tag, bindings, world, state) {
    const mark = tag ? " [" + tag + "]" : "";
    for (const [lhs, proto] of memberships) {
        state.members += 1;
        const resolved = arithmetic(normalize(
            substitute(parseTerm(lhs), bindings), world));
        const spelled = serialize(resolved);
        const wearer = resolved.args.length === 0
            ? world.conformers.get(resolved.head) : undefined;
        if (wearer === undefined) {
            state.refusals.push(
                "'" + site + "' requires the type '" + lhs + "' (aka '" + spelled
                + "') conform to '" + proto
                + "', and no conformer of that name is presented" + mark);
            continue;
        }
        if (!wears(wearer, proto, world)) {
            const worn = wearer.protocols.join(", ");
            state.refusals.push(
                "'" + site + "' requires the type '" + lhs + "' (aka '" + resolved.head
                + "') conform to '" + proto + "', and '" + resolved.head + ": " + worn
                + "' does not carry it" + mark);
        }
    }
}

// ── the judgement ──
// The core takes texts and returns the verdict's parts; the CLI below reads
// files and prints. Split so the same court can sit where there is no file
// system at all, a browser over a published demo, without a second reading
// of the law.

function judgeWhereTexts(text, extraTexts) {
    const world = readWorld(text);
    const ownAliases = new Map(world.aliases);
    // A name's meaning is its written definition, and the definition may be
    // written in another file: each extra text contributes its typealiases,
    // and the world's own spelling wins a collision, the same shadowing the
    // compiler reads.
    for (const more of extraTexts || []) {
        for (const [name, rule] of readWorld(more).aliases) {
            if (!world.aliases.has(name)) world.aliases.set(name, rule);
        }
    }
    const refusals = [];
    let judged = 0;
    const state = { members: 0, refusals };

    // a gate that carries what no court here judges is named at once:
    // the defect is the law's own spelling, not any use of it
    for (const gate of world.gates) {
        for (const part of gate.unjudged) {
            refusals.push(
                "the gate '" + gate.head + ": " + gate.proto + "' carries '" + part
                + "', a conjunct this court does not judge");
        }
    }
    for (const gated of [...world.gatedProtocols.values()]
        .sort((a, b) => (a.name < b.name ? -1 : 1))) {
        for (const part of gated.unjudged) {
            refusals.push(
                "the gated protocol '" + gated.name + "' carries '" + part
                + "', a conjunct this court does not judge");
        }
    }

    // A typealias certificate is a judged point: a parameterless alias in the
    // world whose right side names a gated head states the gate's equalities
    // for those arguments, and the refusal names the certificate.
    for (const name of [...ownAliases.keys()].sort()) {
        const rule = ownAliases.get(name);
        if (rule.parameters.length > 0) continue;
        const term = parseTerm(rule.body);
        const matching = world.gates.filter(gate => gate.head === term.head);
        if (matching.length === 0) continue;
        const parameters = world.parameters.get(term.head);
        if (parameters === undefined) continue;
        const bindings = new Map();
        parameters.forEach((parameter, index) => {
            if (index < term.args.length) bindings.set(parameter, term.args[index]);
        });
        for (const gate of matching) {
            for (const [left, right] of gate.equalities) {
                judged += 1;
                const leftCanon = serialize(arithmetic(normalize(
                    substitute(parseTerm(left), bindings), world)));
                const rightCanon = serialize(arithmetic(normalize(
                    substitute(parseTerm(right), bindings), world)));
                if (leftCanon !== rightCanon) {
                    refusals.push(
                        "'" + name + " = " + rule.body + "' requires the types '"
                        + left + "' (aka '" + leftCanon + "') and '"
                        + right + "' (aka '" + rightCanon + "') be equivalent ["
                        + gate.proto + "]");
                }
            }
            judgeMemberships(gate.memberships, name + " = " + rule.body,
                gate.proto, bindings, world, state);
        }
    }

    for (const use of world.uses) {
        const term = parseTerm(use);
        const matching = world.gates.filter(gate => gate.head === term.head);
        if (matching.length === 0) continue;
        const parameters = world.parameters.get(term.head);
        if (parameters === undefined) continue;
        const bindings = new Map();
        parameters.forEach((name, index) => {
            if (index < term.args.length) bindings.set(name, term.args[index]);
        });
        for (const gate of matching) {
            for (const [left, right] of gate.equalities) {
                judged += 1;
                const leftCanon = serialize(arithmetic(normalize(
                    substitute(parseTerm(left), bindings), world)));
                const rightCanon = serialize(arithmetic(normalize(
                    substitute(parseTerm(right), bindings), world)));
                if (leftCanon !== rightCanon) {
                    refusals.push(
                        "'" + use + "' requires the types '"
                        + left + "' (aka '" + leftCanon + "') and '"
                        + right + "' (aka '" + rightCanon + "') be equivalent ["
                        + gate.proto + "]");
                }
            }
            judgeMemberships(gate.memberships, use, gate.proto,
                bindings, world, state);
        }
    }

    for (const conformer of world.conformers.values()) {
        for (const protoName of conformer.protocols) {
            const gated = world.gatedProtocols.get(protoName);
            if (gated === undefined) continue;
            for (const [left, right] of gated.equalities) {
                judged += 1;
                const leftText = left.includes(".") ? left : conformer.name + "." + left;
                const rightText = right.includes(".") || world.conformers.has(right) || right === "Never"
                    ? right
                    : conformer.name + "." + right;
                const leftCanon = canon(leftText, world);
                const rightCanon = canon(rightText, world);
                if (leftCanon !== rightCanon) {
                    refusals.push(
                        "'" + conformer.name + ": " + protoName + "' requires the types '"
                        + left + "' (aka '" + leftCanon + "') and '"
                        + right + "' (aka '" + rightCanon + "') be equivalent");
                }
            }
            const owned = gated.memberships.map(pair =>
                [pair[0].includes(".") ? pair[0] : conformer.name + "." + pair[0], pair[1]]);
            judgeMemberships(owned, conformer.name + ": " + protoName, null,
                new Map(), world, state);
        }
    }

    return { judged, members: state.members, uses: world.uses.length, refusals };
}

function runWhere(args) {
    if (args.length === 0) {
        fail("usage: judge where <world.swift> [definitions.swift ...]");
    }
    let text;
    try { text = fs.readFileSync(args[0], "utf8"); }
    catch (e) { fail("cannot read " + args[0]); }
    const extras = [];
    for (const extra of args.slice(1)) {
        try { extras.push(fs.readFileSync(extra, "utf8")); }
        catch (e) { fail("cannot read " + extra); }
    }
    const { judged, members, uses, refusals } = judgeWhereTexts(text, extras);
    if (refusals.length === 0) {
        console.log("✓ THE WHERE holds: " + judged + " equalities and " + members
            + " memberships judged across "
            + uses + " uses, the certificates, and the gated "
            + "conformers, one canon each side (canon v" + CANON_VERSION + ").");
        return 0;
    }
    for (const refusal of refusals) console.log("✗ " + refusal);
    return 1;
}

if (typeof module !== "undefined") { module.exports = { runWhere, judgeWhereTexts }; }
if (typeof window !== "undefined") { window.judgeWhereTexts = judgeWhereTexts; }
