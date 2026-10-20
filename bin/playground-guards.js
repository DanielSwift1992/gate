"use strict";

// THE PAGE'S OWN GUARDS: the four objections the fast judge does not raise and
// the compiler would. The judge port is lenient where Swift is strict — it reads
// an extension whose owner is missing, a body without its builder attribute, an
// import of a module the package never names, a top alias naming nothing — so
// the page states these itself, in the compiler's place.
//
// One implementation, two readers: the page draws them as cards while you type,
// and check.js runs them over every world, so a guard that fires in the browser
// is a red vector in CI and never again a thing only an eye can catch.

// The three modules a world may name: the theory, the drawing kit, and the
// domain the company tabs are written against. Each world is a target of the
// package beside this page, so what the guard admits is what `swift build` reads.
const fixedImports = ["import VerificationIsIdentification", "import DocumentKit",
    "import Organization"];

// `parsed` is the judge's parse (declarations, topAliases, literals), `lines`
// the file's lines, `vocabulary` every name the dictionaries answer for.
// Returns [{ line, premise }], the same shape the page's findings carry.
function pageGuards(parsed, lines, vocabulary) {
    const objections = [];
    const say = (line, premise) => objections.push({ line, premise });
    // a name the file states: an extension's owner must be one of these. The
    // literals are NOT read here — the port registers an extension's own typeName
    // under the very name in question, so an orphan would find itself.
    const declared = (word) => parsed.declarations.has(word)
        || parsed.topAliases.has(word) || vocabulary.has(word);
    // a name a top alias may point at: the literals count, being declarations the
    // port keeps apart
    const known = (word) => declared(word) || parsed.literals.has(word);
    lines.forEach((line, index) => {
        const trimmed = line.trim();
        if (trimmed.startsWith("import ") && !fixedImports.includes(trimmed)) {
            say(index + 1, "the imports are fixed: only VerificationIsIdentification,"
                + " DocumentKit, and Organization are legal here");
        }
        if (/^(public\s+)?static var body: some Structure/.test(trimmed)) {
            const above = index > 0 ? lines[index - 1].trim() : "";
            if (above !== "@StructureBuilder") {
                say(index + 1, "a body states no @StructureBuilder on the line above:"
                    + " the builder attribute is required");
            }
        }
        // an extension stands on a declared name: the judge port reads the extension
        // either way, but Swift would refuse the orphan, so the page says it first
        const extended = trimmed.match(/^(?:public\s+)?extension\s+([A-Za-z_]\w*)/);
        if (extended && !declared(extended[1])) {
            say(index + 1, "an extension names `" + extended[1]
                + "`, and this file declares no `" + extended[1] + "`");
        }
    });
    // a dangling name inside a top alias is silent to the judge port (the port
    // reads the alias whole) and unreachable to the renderer when nothing draws
    // it, so every word of every target is looked up by name
    for (const [aliasName, alias] of parsed.topAliases) {
        for (const piece of alias.target.split(/[<>,\s]+/)) {
            // a dotted head reads an axis: only the owner before the dot is a name
            const word = piece.split(".")[0];
            if (word === "" || !/^[A-Z]/.test(word)) continue;
            if (known(word) || (alias.params || []).includes(word)) continue;
            say(alias.line, "`" + aliasName + "` names `" + word
                + "`, and nothing declares it");
        }
    }
    return objections;
}

if (typeof module !== "undefined") {
    module.exports = { pageGuards, fixedImports };
}
