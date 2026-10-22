#!/usr/bin/env node
// The contract's Rust sample, carried as wasm: a second implementation of
// the certificate court (`judge where`) and the count court (`judge count`),
// built from Contracts/Court/rust-sample of the theory corpus at the pin
// bin/court-wasm.from records, by bin/build-court-wasm.sh. This file is
// the door to it for node: it speaks the words the binary speaks, reads the
// named files itself, hands their texts to the module in bin/court-wasm/node
// and writes back what the court answered, stdout, stderr and the exit code,
// so nothing downstream has to know which carrier answered. In the browser
// the same module answers through bin/court-wasm/web.
//
// It is a second implementation, not the corpus's Swift court: the contract
// driver of the corpus (Checks/court-contract.py) holds both carriers to the
// finite suites named by bin/court-contract.from.
const fs = require("fs");
const path = require("path");
const { TextDecoder } = require("util");
// Decode the same UTF-8 byte domain as Rust read_to_string; keep a supplied BOM.
const sourceDecoder = new TextDecoder("utf-8", { fatal: true, ignoreBOM: true });

const OPTIONS_WITH_VALUE = new Set(["--predicate", "--encoding", "--sigma", "--document"]);

// Node lowercases the system message of an I/O error ("ENOENT: no such file or
// directory, open '…'"); the court's line keeps the platform's own text, so the
// common codes are given back their POSIX spelling. Other errors pass as node says them.
const POSIX_TEXT = {
    ENOENT: "No such file or directory",
    EACCES: "Permission denied",
    EISDIR: "Is a directory",
    ENOTDIR: "Not a directory",
};

function sourceArguments(argv) {
    const names = [];
    for (let i = 1; i < argv.length; i++) {
        if (OPTIONS_WITH_VALUE.has(argv[i])) { i++; continue; }
        if (argv[i].startsWith("--")) continue;
        names.push(argv[i]);
    }
    return names;
}

function readSources(names) {
    return names.map((name) => {
        try {
            return { name, text: sourceDecoder.decode(fs.readFileSync(name)) };
        } catch (error) {
            if (error.code === "ERR_ENCODING_INVALID_ENCODED_DATA") {
                return { name, error: "stream did not contain valid UTF-8" };
            }
            const text = POSIX_TEXT[error.code];
            return { name, error: text ? `${text} (${error.code})` : String(error.message) };
        }
    });
}

let courtModule;
function court() {
    if (!courtModule) courtModule = require(path.join(__dirname, "court-wasm", "node", "vi_court.js"));
    return courtModule;
}

/** Judge with CLI-shaped arguments over files given as {name, text} or {name, error}. */
function judge(argumentsList, files) {
    const args = argumentsList.slice();
    if (args[0] === "judge") args.shift();
    return JSON.parse(court().judge(JSON.stringify({ arguments: args, files })));
}

/** The CLI road: read the named files, judge, write the answer, return the exit code. */
function main(argv) {
    const args = argv.slice();
    if (args[0] === "judge") args.shift();
    const answer = judge(args, readSources(sourceArguments(args)));
    process.stdout.write(answer.stdout);
    process.stderr.write(answer.stderr);
    return answer.exit;
}

module.exports = { judge, main, readSources, sourceArguments, version: () => court().version() };

if (require.main === module) {
    process.exitCode = main(process.argv.slice(2));
}
