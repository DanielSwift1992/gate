// Execute the recorded page's own fetch path with its shipped readers.
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm"), assert = require("assert");
const court = require("../bin/court-wasm/node/vi_court.js"), {judge} = require("../bin/judge.js");
const GateWorldCourt = require("../bin/world-court.js");
const GateCourtContexts = require("../bin/court-contexts.js");

const {kitVocabulary} = require("../bin/renderer.js");

function open(root, id, storage) {
    const folder = id === "demo" ? root : path.join(root, "playground", id);
    const {lint} = fs.existsSync(path.join(folder, "playground-lint.js")) ? require(path.join(folder, "playground-lint.js")) : {};
    const {pageGuards} = fs.existsSync(path.join(folder, "playground-guards.js")) ? require(path.join(folder, "playground-guards.js")) : {};
    const page = fs.readFileSync(path.join(folder, "index.html"), "utf8");
    const at = page.indexOf("wasm_bindgen.initSync("), start = page.lastIndexOf("<script>", at) + 8, end = page.indexOf("</script>", at);
    assert(at >= 0 && end > start);
    const scope = {localStorage: storage, wasm_bindgen: {...court, initSync() {}}, VI_COURT_WASM_BASE64: "",
        Uint8Array, atob, Response, Map, GateWorldCourt, GateCourtContexts, judge, lint, pageGuards, kitVocabulary,
        location: {search: "", pathname: "/playground/" + id + "/index.html"},
        fetch: async () => {throw Error("unexpected network");}, document: {addEventListener() {}}};
    scope.window = scope;
    vm.runInNewContext(page.slice(start, end), scope);
    return scope;
}
module.exports = {open};
