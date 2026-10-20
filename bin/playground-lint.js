"use strict";

// THE LAW, ported: a reading of Sources/Tools/Lint.swift over the playground's fragment.
// One rule fits this page's language and travels here: §0′ PURE TYPES — no runtime,
// no values, types only. (§1 NO RENAME and §2 OPEN AXIS weigh `protocol` and
// `associatedtype`, forms the judge refuses before any law could reach them.)
// The Swift lint stays the reference: the same exemptions, read in the same order.

// §0′: a value form is a binding, a routine, or an operator
const purityPattern = /\b(func|var|let|init|subscript|deinit|operator)\b/;
// the witness set: each is a pure function of the type it stands on, admitted by the law
const witnessPattern = /\bstatic\s+(var|let)\s+(typeName|count|labels|body|spelled)\b/;
const renderedWitnessPattern = /\bstatic\s+func\s+rendered\s*</;
const builderDoorPattern = /\binit\s*\(@StructureBuilder.*\{\s*fatalError\(\)\s*\}\s*$/;
const metatypeDoorPattern = /\bfunc\s+[A-Z]/;
const stringFence = '"""';

// the law reads code, never comments
function lawCodeOf(line) {
    const marker = line.indexOf("//");
    return marker < 0 ? line : line.slice(0, marker);
}

// and never a single-line literal's content: prose carries `let` the way a binding does not
function lawStripQuoted(line) {
    let out = "";
    let inside = false;
    for (const character of line) {
        if (character === '"') { inside = !inside; continue; }
        if (!inside) out += character;
    }
    return out;
}

function lawBraceBalance(line) {
    let balance = 0;
    for (const character of line) {
        if (character === "{") balance += 1;
        if (character === "}") balance -= 1;
    }
    return balance;
}

// §S28's mechanical edge: a SlotRule conformer is one substitution, so its body may
// hold nothing but the three aliases. Anything else is an engine trying to enter
// through a rule's door, refused by name.
const slotRuleMemberPattern = /^\s*(?:public\s+)?typealias\s+(?:Slot|From|Into)\s*=/;

// One pass over one file: every objection carries the rule, the line, and the line's text.
function lint(file, text) {
    const objections = [];
    let insideStringLiteral = false;
    let witnessDepth = 0;      // a witness body is the function's spelling, not runtime
    let witnessSignature = false;
    let insideSlotRule = false;
    const lines = text.split("\n");
    for (let index = 0; index < lines.length; index += 1) {
        const raw = lines[index];
        const number = index + 1;
        let source = lawCodeOf(raw);
        if (insideStringLiteral) {
            if (raw.includes(stringFence)) insideStringLiteral = false;
            continue;
        }
        const fence = source.indexOf(stringFence);
        if (fence >= 0) {
            const fences = source.split(stringFence).length - 1;
            if (fences % 2 === 1) insideStringLiteral = true;
            source = source.slice(0, fence);
        }
        const bare = lawStripQuoted(source);
        if (witnessDepth > 0) {
            witnessDepth += lawBraceBalance(bare);
            continue;
        }
        if (witnessSignature) {
            if (bare.includes("{")) {
                witnessSignature = false;
                witnessDepth = Math.max(lawBraceBalance(bare), 0);
            }
            continue;
        }
        if (witnessPattern.test(source) || renderedWitnessPattern.test(source)) {
            if (bare.includes("{")) {
                witnessDepth = Math.max(lawBraceBalance(bare), 0);
            } else {
                witnessSignature = true;
            }
        }
        if (!witnessPattern.test(source)
            && !renderedWitnessPattern.test(source)
            && !builderDoorPattern.test(source)
            && !metatypeDoorPattern.test(source)
            && purityPattern.test(bare)) {
            objections.push({ file, line: number, rule: "rule 0, pure types",
                premise: "the law admits types only, and this line declares a value form: `"
                    + raw.trim().slice(0, 60) + "`" });
        }
        const trimmed = source.trim();
        if (insideSlotRule) {
            if (trimmed.startsWith("}")) {
                insideSlotRule = false;
            } else if (trimmed !== "" && !slotRuleMemberPattern.test(source)) {
                objections.push({ file, line: number, rule: "rule S28, one substitution",
                    premise: "a rule is one substitution, three aliases only: `"
                        + raw.trim().slice(0, 60) + "`" });
            }
        } else if (source.includes(": SlotRule") && bare.includes("{")) {
            insideSlotRule = true;
        }
    }
    return objections;
}

if (typeof module !== "undefined") { module.exports = { lint }; }
