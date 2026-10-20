"use strict";

// The company's plain court at bin/organization-court.from. Verdicts use the
// reference fragment and fixed company policy. The organization contracts v0.1
// and v0.2 bind finite observations, including refusals on foreign forms.
// Richer records for the bench are inspection only, outside that verdict.

const ranks = new Set(["IndividualContributor", "Lead", "Manager"]);
const departments = new Set(["Finance", "Engineering", "Sales", "People"]);
const workplaces = new Set(["OnSite", "Hybrid", "Remote"]);
const genders = new Set(["Male", "Female"]);
const shareHomes = new Map([
    ["FinanceShare", "Finance"], ["EngineeringShare", "Engineering"],
    ["SalesShare", "Sales"], ["PeopleShare", "People"],
]);
const nextInCycle = new Map([
    ["IndividualContributor", "Lead"], ["Lead", "Manager"],
    ["Manager", "IndividualContributor"],
    ["Finance", "Engineering"], ["Engineering", "Sales"],
    ["Sales", "People"], ["People", "Finance"],
    ["OnSite", "Hybrid"], ["Hybrid", "Remote"], ["Remote", "OnSite"],
]);
const conformanceRequirements = new Map([
    ["Employee", [["Rank", "rank"], ["Home", "department"]]],
    ["Person", [["Given", "givenName"], ["Family", "familyName"], ["Sex", "gender"],
        ["Born", "birthYear"], ["Site", "workplace"]]],
    ["GivenNameCycle", [["Next", "givenName"], ["Sex", "gender"]]],
    ["FamilyNameCycle", [["Next", "familyName"]]],
    ["BirthYearCycle", [["Next", "birthYear"]]],
]);
const gatePremises = new Map([
    ["VerifiedView", ["Home", "Home"]],
    ["VerifiedInDepartment", ["Home", null]],
    ["VerifiedAtRank", ["Rank", null]],
    ["VerifiedAtWorkplace", ["Site", null]],
]);


// a name is what it conforms to, walking the ladder a protocol refines
function conformsTo(name, form, declarations, seen) {
    if (name === form) return true;
    const declaration = declarations.get(name);
    if (!declaration) return false;
    seen = seen || new Set();
    if (seen.has(name)) return false;
    seen.add(name);
    for (const conformance of declaration.conformances) {
        if (conformsTo(conformance, form, declarations, seen)) return true;
    }
    return false;
}

function trimEntry(text) {
    return text.replace(/^[; \n\t]+/, "").replace(/[; \n\t]+$/, "");
}

// the length of the bracketed run that opens at `from`: past its matching close
// how many generic angles a piece of type text leaves open
function angleBalance(text) {
    let depth = 0;
    for (const character of text) {
        if (character === "<") depth += 1;
        if (character === ">") depth -= 1;
    }
    return depth;
}

function angleSpan(text, from) {
    let depth = 0;
    for (let index = from; index < text.length; index += 1) {
        if (text[index] === "<") depth += 1;
        if (text[index] === ">") {
            depth -= 1;
            if (depth === 0) return index - from + 1;
        }
    }
    return text.length - from;
}

// comma pieces at angle depth zero: `A<X, Y>, B` splits into two, not three
function splitTopLevel(text) {
    const pieces = [];
    let depth = 0;
    let start = 0;
    for (let index = 0; index < text.length; index += 1) {
        if (text[index] === "<") depth += 1;
        if (text[index] === ">") depth -= 1;
        if (text[index] === "," && depth === 0) {
            pieces.push(text.slice(start, index));
            start = index + 1;
        }
    }
    pieces.push(text.slice(start));
    return pieces.map((piece) => piece.trim()).filter((piece) => piece !== "");
}

function substituteWord(text, word, replacement) {
    return text.replace(new RegExp("\\b" + word + "\\b", "g"), replacement);
}

// ── pass 1: the dictionary ──

function parse(file, text, declarations, order, refusals, extras) {
    const stack = [];
    if (extras && !extras.drawingUnsupported) extras.drawingUnsupported = new Map();
    function markUnsupported(owner, reason) {
        if (!owner) return;
        if (extras) extras.drawingUnsupported.set(owner, reason);
        if (declarations.has(owner)) declarations.get(owner).drawingUnsupported = reason;
    }
    let bodyOwner = null;
    let extensionOwner = null;
    let pendingHead = null, pendingHeadLine = null;
    let pendingAlias = null;
    let buffer = "";
    let bufferLine = 0;

    function drainEntries(lineNumber, final) {
        let depth = 0;
        let current = "";
        const closed = [];
        for (const character of buffer) {
            current += character;
            if (character === "<") depth += 1;
            if (character === ">") depth -= 1;
            if (depth === 0 && current.endsWith(".self")) {
                closed.push(current);
                current = "";
            }
            if (depth === 0 && (character === ";" || character === " ")
                && current.trim() === "") {
                current = "";
            }
        }
        const rest = current;
        for (const closedEntry of closed) {
            let entry = closedEntry.slice(0, -5);
            entry = trimEntry(entry);
            let head;
            const args = [];
            const open = entry.indexOf("<");
            if (open >= 0) {
                head = entry.slice(0, open);
                const inner = entry.slice(open + 1, -1);
                let argumentDepth = 0;
                let piece = "";
                for (const character of inner) {
                    if (character === "<") argumentDepth += 1;
                    if (character === ">") argumentDepth -= 1;
                    if (character === "," && argumentDepth === 0) {
                        args.push(piece.trim());
                        piece = "";
                    } else {
                        piece += character;
                    }
                }
                args.push(piece.trim());
            } else {
                head = entry;
            }
            if (bodyOwner) bodyOwner.entries.push({ head, args, line: bufferLine });
        }
        if (final && rest.replaceAll(";", "").trim() && bodyOwner) bodyOwner.drawingUnsupported = "unread body entry";
        buffer = final ? "" : rest;
        if (closed.length > 0) bufferLine = lineNumber;
    }

    const lines = text.split("\n");
    for (let index = 0; index < lines.length; index += 1) {
        const number = index + 1;
        let line = lines[index].trim();
        if (line === "") continue;
        if (line.startsWith("//")) continue;
        // A TRAILING NOTE IS NOT PART OF A TYPE. `typealias Tight = Unit  // one
        // mark` was read as the type `Unit  // one mark`, so the alias matched
        // nothing anywhere: not the ladder it belongs to, not a comparison, not
        // a reading of its value. It went unnoticed because the names that wear
        // a note in these worlds happen to be the short ones. Quotes are
        // respected — a name may hold a `//` inside a string and mean it.
        {
            let quoted = false;
            for (let j = 0; j < line.length - 1; j += 1) {
                if (line[j] === "\\" && quoted) { j += 1; continue; }
                if (line[j] === '"') quoted = !quoted;
                else if (!quoted && line[j] === "/" && line[j + 1] === "/") {
                    line = line.slice(0, j).trim();
                    break;
                }
            }
        }
        if (line === "") continue;
        if (line.startsWith("import ")) continue;
        if (line.startsWith("@StructureBuilder")) continue;

        // A gate's own spelling: the reference reads `extension F: P` with its
        // `where` on the NEXT line — WhereJudge.swift's pattern spans the newline
        // and matches no other shape. The port joins the two into one logical
        // line, so what this judge reads is what the reference reads, gate for
        // gate. A `where` on the same line is read by neither, and guards.js
        // names it rather than let a claim stand unjudged by both.
        let gateJoined = false;
        if (/^(?:public\s+)?extension\s+\w+\s*:\s*\w+$/.test(line)
            && (lines[index + 1] || "").trim().startsWith("where ")) {
            line += " " + lines[index + 1].trim();
            index += 1;
            gateJoined = true;
        }

        if (pendingAlias !== null) {
            const settled = pendingAlias;
            const gathered = settled.buffer === undefined
                ? line : (settled.buffer + " " + line);
            if (settled.buffer !== undefined && angleBalance(gathered) > 0) {
                settled.buffer = gathered;
                continue;
            }
            pendingAlias = null;
            if (settled.owner) {
                settled.owner.aliases.set(settled.key, { target: gathered, line: settled.line });
            } else {
                extras.topAliases.set(settled.key,
                    { target: gathered, line: settled.line, params: settled.params });
            }
            continue;
        }

        if (/\bstatic\s+(?:var|let|func)\s+(?!body\b|typeName\b)/.test(line)) {
            const owner = extensionOwner !== null ? declarations.get(extensionOwner) : stack[stack.length - 1];
            markUnsupported(extensionOwner || (owner && owner.qualified), "executable member outside the drawing subset");
        }
        if (extensionOwner !== null) {
            const literal = line.match(/^(?:public )?static var typeName: String \{ "((?:[^"\\]|\\.)*)" \}$/);
            if (literal) {
                extras.literals.set(extensionOwner, { ...decodeSwiftLiteral(literal[1]), file, line: number });
                continue;
            }
            if (line === "}") {
                extensionOwner = null;
                continue;
            }
            const owner = declarations.get(extensionOwner);
            markUnsupported(extensionOwner, "extension outside the drawing subset");
            refusals.push({ file, line: number,
                premise: "outside the fragment: `" + line.slice(0, 60) + "`" });
            continue;
        }
        // AN EXTENSION WRITTEN ON ONE LINE IS AN EXTENSION. The manifest says
        // `extension TheContract { public static var typeName: String { "…" } }`
        // on a single line — the shape gate itself writes — and this only ever
        // looked for a line ENDING in `{`, so the name a row is about was never
        // read at all. Every record whose subject is a file went unnamed here.
        if (extras && (line.startsWith("extension ") || line.startsWith("public extension "))
            && line.endsWith("}")) {
            const open = line.indexOf("{");
            const head = line.slice(0, open).replace("public extension ", "")
                .replace("extension ", "").trim();
            const colon = head.indexOf(":");
            const owner = (colon >= 0 ? head.slice(0, colon) : head).trim();
            if (/\bstatic\s+(?:var|let|func)\s+(?!typeName\b)/.test(line) || (/\bstatic\s+(?:var|let|func)\b/.test(line) && !/static var typeName: String \{ "(?:[^"\\]|\\.)*" \}/.test(line))) {
                const standing = declarations.get(owner);
                markUnsupported(owner, "executable extension outside the drawing subset");
            }
            const literal = line.slice(open + 1).match(
                /(?:public )?static var typeName: String \{ "((?:[^"\\]|\\.)*)" \}/);
            // ── AND ONLY WHEN IT CARRIES ONE. This branch was written for the
            // one shape gate itself emits and swallowed every one-line extension
            // it saw, `continue`ing past a gated conformance joined from two
            // lines — `extension Enter: Entered where …` ends in a brace too.
            // Every where-gate in the shelf stopped being read the day this was
            // added, and nothing said a word: no check covered them.
            if (literal) {
                extras.literals.set(owner, { ...decodeSwiftLiteral(literal[1]), file, line: number });
                continue;
            }
        }
        if (extras && (line.startsWith("extension ") || line.startsWith("public extension "))
            && line.endsWith("{")) {
            const head = line.replace("public extension ", "").replace("extension ", "")
                .replaceAll(" {", "").trim();
            const colon = head.indexOf(":");
            extensionOwner = (colon >= 0 ? head.slice(0, colon) : head).trim();
            if (colon >= 0) {
                const standing = declarations.get(extensionOwner);
                if (standing) {
                    for (const piece of head.slice(colon + 1).split(",")) {
                        const conformance = piece.trim();
                        if (conformance !== "" && !standing.conformances.includes(conformance)) {
                            standing.conformances.push(conformance);
                        }
                    }
                }
            }
            continue;
        }
        // a conditional conformance: `extension F: P where A == B {}` gates the
        // form by equivalence. The gate is grammar, not domain: both sides are
        // normalized through the dictionary and compared at every use site.
        if (extras && gateJoined && line.includes(" where ") && /\{\s*\}$/.test(line)) {
            const head = line.replace("public extension ", "").replace("extension ", "")
                .replace(/\s*\{\s*\}$/, "").trim();
            const whereAt = head.indexOf(" where ");
            const beforeWhere = head.slice(0, whereAt);
            const colon = beforeWhere.indexOf(":");
            const owner = (colon >= 0 ? beforeWhere.slice(0, colon) : beforeWhere).trim();
            const conditions = [];
            for (const piece of splitTopLevel(head.slice(whereAt + 7))) {
                const equals = piece.indexOf("==");
                if (equals < 0) continue;
                conditions.push({ left: piece.slice(0, equals).trim(),
                    right: piece.slice(equals + 2).trim() });
            }
            const standing = declarations.get(owner);
            if (standing) {
                // the conformance this gate is conditional ON. The other
                // extension branch records one; this one never did, so a gated
                // form came back conforming to nothing and a view drawing what
                // it is had nothing to draw.
                const conf = colon >= 0 ? beforeWhere.slice(colon + 1).trim() : "";
                if (conf && !standing.conformances.includes(conf)) standing.conformances.push(conf);
                // and the clause as written, for whoever shows it rather than
                // checks it: the judge reads the equalities, a reader reads the
                // sentence, and dropping the rest would show less than was said
                standing.whereText = head.slice(whereAt + 7).replace(/\s+/g, " ").trim();
            }
            if (standing && conditions.length > 0) {
                if (!standing.whereGates) standing.whereGates = [];
                standing.whereGates.push({ conditions, line: number });
            }
            continue;
        }
        if (extras && (line.startsWith("extension ") || line.startsWith("public extension "))
            && /\{\s*\}$/.test(line)) {
            continue;
        }

        if (bodyOwner) {
            if (line === "}") {
                drainEntries(number, true);
                const leftover = buffer.trim();
                if (leftover !== "") {
                    refusals.push({ file, line: number,
                        premise: "a body entry did not close: `" + leftover.slice(0, 60) + "`" });
                }
                bodyOwner = null;
                continue;
            }
            if (buffer === "") bufferLine = number;
            buffer += line + " ";
            drainEntries(number, false);
            continue;
        }

        if (line.startsWith("public enum ") || line.startsWith("enum ")
            || pendingHead !== null) {
            // ── A HEAD THAT OPENS AN ANGLE ENDS WHERE THE ANGLE CLOSES, WHICH
            // NEED NOT BE THIS LINE. A gate written down the page —
            //
            //     public enum Enter<
            //         Who: Keeper,
            //         Into: Room
            //     > {}
            //
            // was read off its first line alone, so its parameters came back
            // empty: the two holes it opens were invisible to everything
            // downstream, and a view that shows what a form asks showed a name
            // with nothing in it. The file already buffers a multi-line alias
            // exactly this way; a declaration head had never been given the
            // same courtesy.
            let raw = line;
            if (pendingHead !== null) {
                raw = pendingHead.text + " " + line;
                pendingHead = null;
            }
            if (angleBalance(raw.replace(/\{[\s\S]*$/, "")) > 0) {
                pendingHead = { text: raw, line: pendingHeadLine || number };
                pendingHeadLine = pendingHead.line;
                continue;
            }
            pendingHeadLine = null;
            line = raw.replace(/\s+/g, " ");
            const afterKeyword = line.replaceAll("public enum ", "").replaceAll("enum ", "");
            // A DECLARATION WHOSE BODY IS ON ITS OWN LINE CLOSES ON THAT LINE.
            // The test asked whether the line ended in an empty `{}` — true for
            // `public enum Finance: Department {}` and false for
            // `public enum FinanceShare: Document { public typealias Home = Finance }`,
            // which then went on the stack and never came off. Present the forms
            // file and every record after the shares nested under them:
            // `FinanceShare.EngineeringShare.SalesShare.PeopleShare.Edsger`, and
            // fifty-eight names resolved to nothing. Braces balance on the line or
            // they do not; nothing else is being asked.
            const opens = (afterKeyword.match(/\{/g) || []).length;
            const closes = (afterKeyword.match(/\}/g) || []).length;
            const selfClosed = opens > 0 && opens === closes;
            // a body written on the head's own line ends the head: without this the
            // last conformance carries the body with it, and a kind spelled
            // `Document { public typealias Home = Finance }` is a kind nobody can
            // be offered — the shelf knew four documents and the bench saw none.
            const headAll = afterKeyword.replace(/\s*\{\s*\}$/, "").replace(/\s*\{$/, "");
            const brace = headAll.indexOf("{");
            const head = (brace >= 0 ? headAll.slice(0, brace) : headAll).trim();
            // a generic declaration names itself before its angles: `Wrap<T: Counting>`
            // declares Wrap, and the colon that matters is the one past the brackets
            const angle = head.indexOf("<");
            let nameEnd = head.indexOf(":");
            let restStart = nameEnd;
            let params = [], paramKinds = [];
            if (angle >= 0 && (nameEnd < 0 || angle < nameEnd)) {
                nameEnd = angle;
                const span = angleSpan(head, angle);
                restStart = head.indexOf(":", angle + span);
                const pieces = head.slice(angle + 1, angle + span - 1).split(",")
                    .map((piece) => piece.trim()).filter((piece) => piece !== "");
                params = pieces.map((piece) => piece.split(":")[0].trim());
                // additive: the kind each parameter takes, in order — the gate's
                // signature, read once by the judge's own parser (see axisKinds).
                paramKinds = pieces.map((piece) => {
                    const c = piece.indexOf(":");
                    return c >= 0 ? piece.slice(c + 1).trim() : null;
                });
            }
            const name = (nameEnd >= 0 ? head.slice(0, nameEnd) : head).trim();
            let conformances = [];
            if (restStart >= 0) {
                conformances = head.slice(restStart + 1).split(",").map((piece) => piece.trim());
            }
            const parent = stack.length > 0 ? stack[stack.length - 1].qualified : null;
            const qualified = parent ? parent + "." + name : name;
            const standing = declarations.get(qualified);
            if (standing) {
                refusals.push({ file, line: number,
                    premise: name + " is declared twice: line " + standing.line
                        + " already declares it" });
                if (!selfClosed) stack.push(standing);
                continue;
            }
            const declaration = { name, qualified, parent, conformances, params, paramKinds,
                file, line: number, aliases: new Map(), entries: [] };
            if (/\bstatic\s+(?:var|let|func)\b/.test(line)) declaration.drawingUnsupported = "inline executable member outside the drawing subset";
            if (extras && extras.drawingUnsupported.has(qualified)) declaration.drawingUnsupported = extras.drawingUnsupported.get(qualified);
            declarations.set(qualified, declaration);
            order.push(qualified);
            // what the head's own line said inside its braces is what it states
            if (selfClosed && brace >= 0) {
                const inner = headAll.slice(brace + 1);
                for (const piece of inner.split(";")) {
                    const alias = /(?:public\s+)?typealias\s+(\w+)\s*=\s*([^};]+)/.exec(piece);
                    if (alias) {
                        declaration.aliases.set(alias[1].trim(),
                            { target: alias[2].trim(), line: number });
                    }
                }
            }
            if (!selfClosed) stack.push(declaration);
            continue;
        }

        // a protocol names a form and states the axes a conformer owes. The
        // compiler needs one wherever a constraint or a gate stands: `<P: Counting>`
        // takes a protocol, and `extension F: G where …` inherits from one. The
        // judge registers the name so every reference to it settles, and reads
        // the axes the body states.
        if (line.startsWith("public protocol ") || line.startsWith("protocol ")) {
            // the plain court reads worlds of facts; a protocol is the shelf's
            // grammar and stands outside this fragment. The binary says so at
            // the line, and for a while this port registered the name in
            // silence: the first seeded parity walk found the two apart, a
            // bench green over a world CI refuses. The name is still
            // registered below, so scope and references settle the same way.
            if (!extras) {
                refusals.push({ file, line: number,
                    premise: "outside the fragment: `" + line.slice(0, 60) + "`" });
            }
            const afterKeyword = line.replace("public protocol ", "").replace("protocol ", "");
            const selfClosed = /\{\s*\}$/.test(afterKeyword);
            const head = afterKeyword.replace(/\s*\{\s*\}$/, "").replace(/\s*\{$/, "")
                .replace(/\s+where\s+.*$/, "").trim();
            const colon = head.indexOf(":");
            const name = (colon >= 0 ? head.slice(0, colon) : head).trim();
            const conformances = colon >= 0
                ? head.slice(colon + 1).split(",").map((piece) => piece.trim())
                : [];
            const standing = declarations.get(name);
            if (standing) {
                refusals.push({ file, line: number,
                    premise: name + " is declared twice: line " + standing.line
                        + " already declares it" });
                if (!selfClosed) stack.push(standing);
                continue;
            }
            const declaration = { name, qualified: name, parent: null, conformances,
                params: [], file, line: number, aliases: new Map(), entries: [], axes: [], axisKinds: {} };
            declarations.set(name, declaration);
            order.push(name);
            if (!selfClosed) stack.push(declaration);
            continue;
        }

        // an axis a protocol states: the name a conformer owes a value for
        if (line.startsWith("associatedtype ")) {
            const owner = stack.length > 0 ? stack[stack.length - 1] : null;
            if (owner && owner.axes) {
                const stated = line.replace("associatedtype ", "");
                const axis = stated.split(":")[0].trim();
                owner.axes.push(axis);
                // additive, for one reading of the grammar: the kind this axis
                // takes. Judgement never looks here — the parse only carries it,
                // so the bench reads `Employee.Home is a Department` from the very
                // parser that judges, not a second regex over the shelf.
                const colon = stated.indexOf(":");
                if (colon >= 0 && owner.axisKinds) owner.axisKinds[axis] = stated.slice(colon + 1).trim();
            }
            continue;
        }

        if (line.startsWith("public typealias ") || line.startsWith("typealias ")) {
            const body = line.replace("public typealias ", "").replace("typealias ", "");
            const equals = body.indexOf("=");
            if (equals >= 0 && stack.length > 0) {
                const key = body.slice(0, equals).trim();
                const target = body.slice(equals + 1).trim();
                const owner = stack[stack.length - 1];
                const stated = owner.aliases.get(key);
                if (stated) {
                    refusals.push({ file, line: number,
                        premise: owner.name + " states " + key + " twice: line "
                            + stated.line + " already states it" });
                }
                if (target === "") {
                    pendingAlias = { owner, key, line: number };
                } else if (angleBalance(target) > 0) {
                    pendingAlias = { owner, key, line: number, buffer: target };
                } else {
                    owner.aliases.set(key, { target, line: number });
                }
            } else if (equals >= 0 && extras) {
                const keySide = body.slice(0, equals).trim();
                const generic = keySide.indexOf("<");
                const bare = generic >= 0 ? keySide.slice(0, generic) : keySide;
                const params = generic >= 0
                    ? keySide.slice(generic + 1, keySide.lastIndexOf(">"))
                        .split(",").map((piece) => piece.split(":")[0].trim())
                    : [];
                const target = body.slice(equals + 1).trim();
                if (target === "") {
                    pendingAlias = { owner: null, key: bare, line: number, params };
                } else if (angleBalance(target) > 0) {
                    pendingAlias = { owner: null, key: bare, line: number, params,
                        buffer: target };
                } else {
                    extras.topAliases.set(bare, { target, line: number, params });
                }
            } else if (equals < 0) {
                const generic = body.indexOf("<");
                const bare = (generic >= 0 ? body.slice(0, generic) : body).trim();
                refusals.push({ file, line: number,
                    premise: bare === ""
                        ? "a typealias states no target yet: an alias reads `name = target`"
                        : "`" + bare + "` states no target yet: an alias reads `name = target`" });
            } else {
                refusals.push({ file, line: number,
                    premise: "a typealias stands outside every declaration" });
            }
            continue;
        }

        if ((line.startsWith("public static var body: some Structure")
            || line.startsWith("static var body: some Structure")) && line.endsWith("{")) {
            bodyOwner = stack.length > 0 ? stack[stack.length - 1] : null;
            buffer = "";
            continue;
        }

        if (line === "}") {
            if (stack.length === 0) {
                refusals.push({ file, line: number,
                    premise: "a closing brace with nothing open" });
            } else {
                stack.pop();
            }
            continue;
        }

        refusals.push({ file, line: number,
            premise: "outside the fragment: `" + line.slice(0, 60) + "`" });
    }
}

// The reference reader deliberately preserves the pinned Swift reader's
// narrow spelling and current limitations. In particular it does not read
// protocols, inline extensions, private aliases or trailing comments as syntax.
function parseCompany(file, text, declarations, order, refusals) {
    const stack = [];
    let bodyOwner = null;
    let buffer = "";
    let bufferLine = 0;
    function drainEntries(lineNumber, final) {
        let depth = 0;
        let current = "";
        const closed = [];
        for (const character of buffer) {
            current += character;
            if (character === "<") depth += 1;
            if (character === ">") depth -= 1;
            if (depth === 0 && current.endsWith(".self")) {
                closed.push(current);
                current = "";
            }
            if (depth === 0 && (character === ";" || character === " ")
                && current.trim() === "") {
                current = "";
            }
        }
        const rest = current;
        for (const closedEntry of closed) {
            let entry = closedEntry.slice(0, -5);
            entry = trimEntry(entry);
            let head;
            const args = [];
            const open = entry.indexOf("<");
            if (open >= 0) {
                head = entry.slice(0, open);
                const inner = entry.slice(open + 1, -1);
                let argumentDepth = 0;
                let piece = "";
                for (const character of inner) {
                    if (character === "<") argumentDepth += 1;
                    if (character === ">") argumentDepth -= 1;
                    if (character === "," && argumentDepth === 0) {
                        args.push(piece.trim());
                        piece = "";
                    } else {
                        piece += character;
                    }
                }
                args.push(piece.trim());
            } else {
                head = entry;
            }
            if (bodyOwner) bodyOwner.entries.push({ head, args, line: bufferLine });
        }
        buffer = final ? "" : rest;
        if (closed.length > 0) bufferLine = lineNumber;
    }


    for (const [index, raw] of text.split("\n").entries()) {
        const number = index + 1;
        const line = raw.trim();
        if (!line || line.startsWith("//") || line.startsWith("import ")
            || line.startsWith("@StructureBuilder")) continue;
        if (bodyOwner !== null) {
            if (line === "}") {
                drainEntries(number, true);
                bodyOwner = null;
            } else {
                if (!buffer) bufferLine = number;
                buffer += line + " ";
                drainEntries(number, false);
            }
            continue;
        }
        if (line.startsWith("public enum ") || line.startsWith("enum ")) {
            const head = line.replaceAll("public enum ", "").replaceAll("enum ", "")
                .replaceAll(" {", "");
            const colon = head.indexOf(":");
            const name = (colon < 0 ? head : head.slice(0, colon)).trim();
            const conformances = colon < 0 ? []
                : head.slice(colon + 1).split(",").filter(Boolean).map(x => x.trim());
            const parent = stack.length ? stack[stack.length - 1].qualified : null;
            const qualified = parent === null ? name : parent + "." + name;
            const declaration = { name, qualified, parent, conformances, line: number,
                aliases: new Map(), entries: [] };
            declarations.set(qualified, declaration);
            order.push(qualified);
            stack.push(declaration);
            continue;
        }
        if (line.startsWith("public typealias ")) {
            const body = line.replaceAll("public typealias ", "");
            const equals = body.indexOf("=");
            if (equals > 0 && equals < body.length - 1 && stack.length) {
                stack[stack.length - 1].aliases.set(body.slice(0, equals).trim(),
                    { target: body.slice(equals + 1).trim(), line: number });
            } else {
                refusals.push({ file, line: number,
                    premise: "a typealias stands outside every declaration" });
            }
            continue;
        }
        if (line.startsWith("public static var body: some Structure {")) {
            bodyOwner = stack.length ? stack[stack.length - 1] : null;
            buffer = "";
            continue;
        }
        if (line === "}") {
            if (stack.length) stack.pop();
            else refusals.push({ file, line: number,
                premise: "a closing brace with nothing open" });
            continue;
        }
        refusals.push({ file, line: number,
            premise: "outside the fragment: `" + Array.from(line).slice(0, 60).join("") + "`" });
    }
}

// ── the values: an explicit worklist and a memo, no call recursion ──

function isSeed(name) {
    return ranks.has(name) || departments.has(name) || workplaces.has(name)
        || genders.has(name) || shareHomes.has(name);
}

function slotKey(owner, key) {
    return owner + "\u0000" + key;
}

function recordReader(values, name, slot) {
    if (!values.readers.has(name)) values.readers.set(name, new Set());
    values.readers.get(name).add(slot);
}

function value(startOwner, startKey, declarations, values) {
    const startSlot = slotKey(startOwner, startKey);
    if (values.settled.has(startSlot)) return values.settled.get(startSlot);
    if (values.refused.has(startSlot)) return null;
    const pending = [{ owner: startOwner, key: startKey }];
    const inFlight = new Set([startSlot]);
    while (pending.length > 0) {
        const top = pending[pending.length - 1];
        const topSlot = slotKey(top.owner, top.key);
        if (values.settled.has(topSlot) || values.refused.has(topSlot)) {
            pending.pop();
            inFlight.delete(topSlot);
            continue;
        }
        const owner = declarations.get(top.owner);
        if (!owner) {
            values.refused.set(topSlot, top.owner + " resolves to nothing");
            continue;
        }
        const alias = owner.aliases.get(top.key);
        if (!alias) {
            values.refused.set(topSlot, top.owner + " states no " + top.key);
            continue;
        }
        const segments = alias.target.split(".");
        let cursor = null;
        let waiting = null;
        let reason = null;
        let index = 0;
        const headSegment = segments[0];
        values.lookups += 1;
        if (owner.aliases.has(headSegment)
            && (segments.length > 1 || headSegment !== top.key)) {
            waiting = { owner: top.owner, key: headSegment };
        } else if (declarations.has(headSegment) || isSeed(headSegment)) {
            if (declarations.has(headSegment)) recordReader(values, headSegment, topSlot);
            cursor = headSegment;
            index = 1;
        } else {
            reason = "the name " + headSegment + " resolves to nothing";
        }
        if (waiting) {
            const waitingSlot = slotKey(waiting.owner, waiting.key);
            if (values.settled.has(waitingSlot)) {
                cursor = values.settled.get(waitingSlot);
                waiting = null;
                index = 1;
            } else if (values.refused.has(waitingSlot)) {
                reason = values.refused.get(waitingSlot);
                waiting = null;
            }
        }
        while (reason === null && waiting === null && index < segments.length) {
            const member = segments[index];
            const base = cursor;
            values.lookups += 1;
            if (member === "Next" && nextInCycle.has(base)) {
                cursor = nextInCycle.get(base);
                index += 1;
                continue;
            }
            const carrier = declarations.get(base);
            if (carrier) recordReader(values, base, topSlot);
            if (carrier && carrier.aliases.has(member)) {
                const dependencySlot = slotKey(base, member);
                if (values.settled.has(dependencySlot)) {
                    cursor = values.settled.get(dependencySlot);
                    index += 1;
                    continue;
                }
                if (values.refused.has(dependencySlot)) {
                    reason = values.refused.get(dependencySlot);
                    continue;
                }
                waiting = { owner: base, key: member };
                continue;
            }
            reason = base + " carries no " + member;
        }
        if (reason !== null) {
            values.refused.set(topSlot, reason);
            continue;
        }
        if (waiting !== null) {
            const waitingSlot = slotKey(waiting.owner, waiting.key);
            if (inFlight.has(waitingSlot)) {
                values.refused.set(topSlot, top.owner + "." + top.key + " derives from itself");
                continue;
            }
            pending.push(waiting);
            inFlight.add(waitingSlot);
            continue;
        }
        values.settled.set(topSlot, cursor);
    }
    return values.settled.has(startSlot) ? values.settled.get(startSlot) : null;
}

function category(name, declarations) {
    if (ranks.has(name)) return "rank";
    if (departments.has(name)) return "department";
    if (workplaces.has(name)) return "workplace";
    if (genders.has(name)) return "gender";
    if (shareHomes.has(name)) return "share";
    const declaration = declarations.get(name);
    if (!declaration) return null;
    if (declaration.conformances.includes("GivenNameCycle")) return "givenName";
    if (declaration.conformances.includes("FamilyNameCycle")) return "familyName";
    if (declaration.conformances.includes("BirthYearCycle")) return "birthYear";
    if (declaration.conformances.includes("Employee")) return "person";
    return "declaration";
}

function coordinate(key, name, declarations, values) {
    if (key === "Home" && shareHomes.has(name)) return shareHomes.get(name);
    return value(name, key, declarations, values);
}

// ── pass 2: premises against the table ──

function check(file, declarations, order, values, refusals) {
    let premises = 0;
    const gateTouches = values.gateTouches;

    for (const qualified of order) {
        const declaration = declarations.get(qualified);

        for (const conformance of declaration.conformances) {
            const requirements = conformanceRequirements.get(conformance);
            if (!requirements) continue;
            for (const [key, wanted] of requirements) {
                premises += 1;
                const alias = declaration.aliases.get(key);
                if (!alias) {
                    refusals.push({ file, line: declaration.line,
                        premise: conformance + " requires " + key + ": "
                            + declaration.name + " states none" });
                    continue;
                }
                const settled = value(qualified, key, declarations, values);
                if (settled === null) {
                    const reason = values.refused.get(slotKey(qualified, key)) ?? "unresolved";
                    refusals.push({ file, line: alias.line,
                        premise: declaration.name + "." + key + ": " + reason });
                    continue;
                }
                const landed = category(settled, declarations);
                if (landed !== wanted) {
                    refusals.push({ file, line: alias.line,
                        premise: conformance + " requires " + key + " in " + wanted + ": "
                            + declaration.name + "." + key + " = " + settled
                            + " lands in " + (landed ?? "nothing") });
                }
            }
        }

        for (const entry of declaration.entries) {
            const premise = gatePremises.get(entry.head);
            if (premise) {
                premises += 1;
                if (entry.args.length !== 2) {
                    refusals.push({ file, line: entry.line,
                        premise: entry.head + " wants two arguments, "
                            + entry.args.length + " stand" });
                    continue;
                }
                const subject = entry.args[0];
                const object = entry.args[1];
                gateTouches.set(subject, (gateTouches.get(subject) ?? 0) + 1);
                gateTouches.set(object, (gateTouches.get(object) ?? 0) + 1);
                const left = coordinate(premise[0], subject, declarations, values);
                if (left === null) {
                    refusals.push({ file, line: entry.line,
                        premise: entry.head + ": " + subject + "." + premise[0]
                            + " resolves to nothing" });
                    continue;
                }
                let right = object;
                if (premise[1] !== null) {
                    const resolved = coordinate(premise[1], object, declarations, values);
                    if (resolved === null) {
                        refusals.push({ file, line: entry.line,
                            premise: entry.head + ": " + object + "." + premise[1]
                                + " resolves to nothing" });
                        continue;
                    }
                    right = resolved;
                }
                if (left !== right) {
                    const rightSpelled = premise[1] !== null
                        ? object + "." + premise[1] : object;
                    refusals.push({ file, line: entry.line,
                        premise: entry.head + " requires " + subject + "." + premise[0]
                            + " == " + rightSpelled + ": " + left + " against " + right });
                }
                continue;
            }
            if (entry.args.length === 0) {
                values.lookups += 1;
                let found = declarations.has(entry.head);
                if (!found && declaration.parent !== null) {
                    found = declarations.has(declaration.parent + "." + entry.head);
                }
                if (!found) {
                    found = declarations.has(declaration.qualified + "." + entry.head);
                }
                if (!found) {
                    found = isSeed(entry.head);
                }
                if (!found) {
                    refusals.push({ file, line: entry.line,
                        premise: "the entry " + entry.head + " resolves to nothing" });
                }
                continue;
            }
            refusals.push({ file, line: entry.line,
                premise: "an unknown gate: " + entry.head });
        }
    }
    return premises;
}

// ── The where court and the count court are not ported. gate carries the
// contract's Rust sample of both, a second implementation held to the Swift
// court by the suite, built for wasm32 (bin/court-wasm, bin/judge-wasm.js); the
// plain court here reads no `where` clause. A hand-written reading of the
// canon beside it would be a third one, held by nothing.

// Files share a dictionary and memo. The reference checks the accumulated
// order after each file, including earlier declarations, rather than summing
// independent judgments. The multi-file contract records that behavior.
function judgeFiles(files) {
    const started = performance.now();
    const declarations = new Map(), order = [], refusals = [];
    const values = { settled: new Map(), refused: new Map(), lookups: 0,
        readers: new Map(), gateTouches: new Map() };
    let premises = 0;
    for (const { file, text } of files) {
        parseCompany(file, text, declarations, order, refusals);
        premises += check(file, declarations, order, values, refusals);
    }
    return { declarations: order.length, lookups: values.lookups, premises,
        milliseconds: performance.now() - started, refusals,
        parsed: { declarations, order, literals: new Map(), topAliases: new Map(),
            readers: values.readers, gateTouches: values.gateTouches } };
}

function decodeSwiftLiteral(raw) {
    // Swift's ordinary escaped literals; interpolation and other escapes are
    // outside this reader, never left as invented literal text.
    try { return {value: raw.replace(/\\(u\{[0-9a-fA-F]+\}|[\s\S])/g, (_, escape) => {
        const simple = {"0":"\0", "n":"\n", "r":"\r", "t":"\t", '"':'"', "'":"'", "\\":"\\"};
        if (Object.hasOwn(simple, escape)) return simple[escape];
        if (/^u\{[0-9a-fA-F]+\}$/.test(escape)) {
            const code = parseInt(escape.slice(2, -1), 16);
            if (code <= 0x10ffff && !(code >= 0xd800 && code <= 0xdfff)) return String.fromCodePoint(code);
        }
        throw new Error("unsupported Swift string escape: " + escape);
    })}; } catch (error) { return {value: "", unsupported: error.message}; }
}
function drawingParse(files) {
    const declarations = new Map(), order = [], refusals = [];
    const extras = {literals: new Map(), topAliases: new Map()};
    for (const {file, text} of files) parse(file, text, declarations, order, refusals, extras);
    return {declarations, order, ...extras, parseRefusals: refusals};
}

function judge(file, text, vocabulary) {
    const result = judgeFiles([{ file, text }]);
    {
        // The bench needs records outside the company's fragment. These are
        // inspection data, never additional premises or a wider plain verdict.
        const declarations = new Map(), order = [];
        const extras = { literals: new Map(), topAliases: new Map() };
        parse(file, text, declarations, order, [], vocabulary ? extras : null);
        result.parsed = { ...result.parsed, declarations, order,
            literals: extras.literals, topAliases: extras.topAliases };
    }
    return result;
}

// The bench uses this walk for its offers over inspection records, not as
// a general conformance judgment by the company's plain court.
if (typeof module !== "undefined") { module.exports = { judge, judgeFiles, conformsTo, drawingParse }; }
