"use strict";

// THE APPLIER, ported: a line-for-line reading of `Press` from the theory's
// Sources/Tools/Press.swift (the triples-2 matcher), over one file instead of
// two. A button over a state file is a rewrite triple, not a program: find the
// rule's slot alias, unify the slot's term with the rule's pattern, substitute
// the template. One match or none, and a mismatch leaves the file byte-identical.
// No domain logic stands here or ever will: a system's behaviour is its triples,
// written in the same file.

// Reads one rule's triple out of the file's text: the enum's generic parameter
// names, and its Slot/From/Into aliases. A rule body holding anything else is
// refused whole: §S28, a rule is one substitution.
function readRule(name, text) {
    let variables = [];
    let slot = "";
    let from = "";
    let into = "";
    let inside = false;
    for (const raw of text.split("\n")) {
        const line = raw.trim();
        if (!inside) {
            if (!line.startsWith("public enum " + name) && !line.startsWith("enum " + name)) {
                continue;
            }
            const open = line.indexOf("<");
            const close = line.indexOf(">");
            if (open >= 0 && close > open) {
                for (const piece of line.slice(open + 1, close).split(",")) {
                    const variable = piece.split(":")[0].trim();
                    if (variable !== "") variables.push(variable);
                }
            }
            inside = true;
            continue;
        }
        if (line.startsWith("}")) break;
        let carried = line === "" || line.startsWith("//");
        for (const key of ["Slot", "From", "Into"]) {
            const marker = "typealias " + key + " = ";
            const at = line.indexOf(marker);
            if (at < 0) continue;
            const value = line.slice(at + marker.length).trim();
            if (key === "Slot") slot = value;
            else if (key === "From") from = value;
            else into = value;
            carried = true;
        }
        if (!carried) {
            return { error: name + " is not a triple: " + line };
        }
    }
    if (!inside) return { error: "no rule named " + name + " in this file" };
    if (slot === "" || from === "" || into === "") {
        return { error: name + " states no full Slot/From/Into triple" };
    }
    return { name, variables, slot, from, into };
}

// Substitutes bound variables into a template by whole-word replacement.
function fillTemplate(template, bindings) {
    let out = "";
    let word = "";
    for (const ch of template + " ") {
        if (/[A-Za-z0-9]/.test(ch)) {
            word += ch;
        } else {
            out += bindings.has(word) ? bindings.get(word) : word;
            word = "";
            if (ch !== " " || out.endsWith(",")) out += ch;
        }
    }
    return out.endsWith(" ") ? out.slice(0, -1) : out;
}

// ── terms: the one shape every pattern, slot term, and instance argument shares ──

function parseTerm(text) {
    const trimmed = text.trim();
    const open = trimmed.indexOf("<");
    if (open < 0 || !trimmed.endsWith(">")) {
        return { head: trimmed, args: [] };
    }
    const head = trimmed.slice(0, open);
    const inner = trimmed.slice(open + 1, -1);
    const args = [];
    let depth = 0;
    let piece = "";
    for (const ch of inner) {
        if (ch === "<") depth += 1;
        if (ch === ">") depth -= 1;
        if (ch === "," && depth === 0) {
            args.push(parseTerm(piece));
            piece = "";
        } else {
            piece += ch;
        }
    }
    if (piece.trim() !== "") args.push(parseTerm(piece));
    return { head, args };
}

function serializeTerm(term) {
    return term.args.length === 0
        ? term.head
        : term.head + "<" + term.args.map(serializeTerm).join(", ") + ">";
}

// Collects each variable's occurrence count across a pattern: linearity is the
// theorem's premise (one occurrence keeps the match unique), so a repeated
// variable refuses the rule before any state is touched.
function occurrences(pattern, variables, counts) {
    if (pattern.args.length === 0 && variables.includes(pattern.head)) {
        counts.set(pattern.head, (counts.get(pattern.head) || 0) + 1);
        return;
    }
    for (const argument of pattern.args) {
        occurrences(argument, variables, counts);
    }
}

// Structural unification of a linear pattern against a term: a variable node
// binds whole (or agrees with its instance pre-binding), a constant node demands
// the same head and unifies its arguments. One match or none.
function unify(pattern, term, variables, bindings) {
    if (pattern.args.length === 0 && variables.includes(pattern.head)) {
        const value = serializeTerm(term);
        if (bindings.has(pattern.head)) {
            return bindings.get(pattern.head) === value;
        }
        bindings.set(pattern.head, value);
        return true;
    }
    if (pattern.head !== term.head || pattern.args.length !== term.args.length) {
        return false;
    }
    for (let index = 0; index < pattern.args.length; index += 1) {
        if (!unify(pattern.args[index], term.args[index], variables, bindings)) {
            return false;
        }
    }
    return true;
}

// The literal alphabet: what free text may carry into a typeName. Everything
// that could escape the literal (quotes, slashes, angles) is outside it, so the
// literal's FORM survives every press and the judge only ever sees a well-formed
// file. The refusal names the character.
function vetLiteral(text) {
    for (const ch of text) {
        const allowed = /[\p{L}\p{N}]/u.test(ch) || ch === " " || ch === "."
            || ch === "," || ch === "!" || ch === "?" || ch === "-";
        if (!allowed) {
            return '"' + ch + '" is outside the literal\'s alphabet'
                + " (letters, digits, space, .,!?-)";
        }
    }
    return null;
}

// The literal slot's three movements: append, rubout, clear. Free text lives in
// a typeName (the prose genre), a label draws it with no reader between, and
// the judge vets the file's form, never the words.
function pressLiteral(text, operation, slotName, payload) {
    const lines = text.split("\n");
    let insideExtension = false;
    for (let number = 0; number < lines.length; number += 1) {
        const trimmed = lines[number].trim();
        if (trimmed.startsWith("extension " + slotName + " ")
            || trimmed.startsWith("extension " + slotName + "{")) {
            insideExtension = true;
            continue;
        }
        if (!insideExtension) continue;
        if (trimmed.startsWith("}")) break;
        const shape = lines[number].match(/\{ "([^"]*)" \}/);
        if (!shape) continue;
        const current = shape[1];
        let next = current;
        if (operation === "append") {
            const objection = vetLiteral(payload);
            if (objection !== null) return { text, applied: false, error: objection };
            next = current + payload;
        } else if (operation === "rubout") {
            next = current.slice(0, -1);
        } else {
            next = "";
        }
        lines[number] = lines[number].replace('{ "' + current + '" }', '{ "' + next + '" }');
        return { text: lines.join("\n"), applied: true, line: number + 1 };
    }
    return { text, applied: false, error: "no literal slot " + slotName + " in this file" };
}

// One press: unify, substitute, or stand. A comma at depth zero spells a chord:
// several rules of ONE slot behind one face (§S30). An angle bracket spells an
// instance: `TypeGlyph<Letter.h>` hands the rule the arguments its pattern
// cannot bind — the judge of the NEXT state is what vets them. At any state at
// most one member may match; two matches name an unlawful chord and refuse.
function press(text, ruleArgument) {
    // the literal genre first: "append <Slot> <raw text>", "rubout <Slot>",
    // "clear <Slot>" are the applier's own movements, not dictionary rules
    const literal = ruleArgument.match(/^(append|rubout|clear) (\S+)(?: ([\s\S]*))?$/);
    if (literal) {
        return pressLiteral(text, literal[1], literal[2], literal[3] ?? "");
    }
    const memberTexts = [];
    let depth = 0;
    let piece = "";
    for (const ch of ruleArgument) {
        if (ch === "<") depth += 1;
        if (ch === ">") depth -= 1;
        if (ch === "," && depth === 0) {
            memberTexts.push(piece);
            piece = "";
        } else {
            piece += ch;
        }
    }
    memberTexts.push(piece);
    const members = [];
    for (const memberText of memberTexts) {
        const spelled = parseTerm(memberText);
        const rule = readRule(spelled.head, text);
        if (rule.error) return { text, applied: false, error: rule.error };
        members.push({ rule, instance: spelled.args });
    }
    const slots = new Set(members.map((member) => member.rule.slot));
    if (slots.size !== 1) {
        return { text, applied: false, error: "a chord holds one slot: "
            + ruleArgument + " mixes " + [...slots].sort().join(", ") };
    }

    // the slot marker drops its `Slot` suffix to name the alias in the state lines
    let aliasName = members[0].rule.slot;
    if (aliasName.endsWith("Slot")) aliasName = aliasName.slice(0, -4);
    const marker = "typealias " + aliasName + " = ";
    const lines = text.split("\n");
    let slotLine = -1;
    for (let index = 0; index < lines.length; index += 1) {
        if (lines[index].trim().replace(/^public /, "").startsWith(marker)) {
            if (slotLine >= 0) {
                return { text, applied: false,
                    error: "slot " + aliasName + " appears twice in this file" };
            }
            slotLine = index;
        }
    }
    if (slotLine < 0) {
        return { text, applied: false, error: "no slot " + aliasName + " in this file" };
    }
    const found = lines[slotLine];
    const current = found.slice(found.indexOf(marker) + marker.length).trim();

    // the match: a variable node binds whole, a constant node demands its head,
    // and the pattern is LINEAR (each variable once) so the match is unique or
    // absent. A parameter the pattern never mentions is instance-bound: it must
    // arrive with the press. One match or none, across the whole chord.
    const currentTerm = parseTerm(current);
    let matched = null;
    for (const { rule, instance } of members) {
        const pattern = parseTerm(rule.from);
        const counts = new Map();
        occurrences(pattern, rule.variables, counts);
        for (const [variable, count] of counts) {
            if (count > 1) {
                return { text, applied: false, error: rule.name + " repeats "
                    + variable
                    + " in its pattern: linearity is the premise of the unique match" };
            }
        }
        const bindings = new Map();
        const instanceBound = rule.variables.filter((variable) => !counts.has(variable));
        if (instance.length > instanceBound.length) {
            return { text, applied: false, error: rule.name + " takes "
                + instanceBound.length + " instance argument(s), "
                + instance.length + " given" };
        }
        if (instance.length < instanceBound.length) {
            return { text, applied: false, error: rule.name
                + " needs its instance argument(s) " + instanceBound.join(", ")
                + ": press " + rule.name + "<…>" };
        }
        instanceBound.forEach((variable, index) => {
            bindings.set(variable, serializeTerm(instance[index]));
        });
        // A rule whose pattern IS its slot states no shape to match: whatever
        // term the slot holds is the match, and every parameter it declares is
        // information the press carries. The kit writes this form (`From =
        // PlateSlot` beside `Slot = PlateSlot`), and a mixed rule — a pattern
        // variable beside an instance parameter — has no spelling at all: a key
        // is bare when its parameters are spelling, Exactly when they are the
        // atom, and the two kinds are told apart by statement.
        const slotIsPattern = rule.from === rule.slot;
        if (!slotIsPattern && !unify(pattern, currentTerm, rule.variables, bindings)) {
            continue;
        }
        if (matched !== null) {
            return { text, applied: false, error: "ambiguous chord: "
                + matched.rule.name + " and " + rule.name + " both match "
                + aliasName + " = " + current };
        }
        matched = { rule, bindings };
    }
    if (matched === null) {
        return { text, applied: false, noop: aliasName + " is " + current + ", "
            + ruleArgument + " expects "
            + members.map((member) => member.rule.from).join(" or ") };
    }
    const next = fillTemplate(matched.rule.into, matched.bindings);
    lines[slotLine] = found.slice(0, found.indexOf(marker)) + marker + next;
    return { text: lines.join("\n"), applied: true, line: slotLine + 1 };
}

if (typeof module !== "undefined") {
    module.exports = { press, readRule, fillTemplate, parseTerm, serializeTerm,
        pressLiteral, vetLiteral };
}
