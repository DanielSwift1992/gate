"use strict";
const assert = require("assert"), fs = require("fs"), path = require("path"), vm = require("vm");

function implementation(ui, name) {
    const at = ui.indexOf("function " + name + "("), end = ui.indexOf("\n}", at);
    assert(at >= 0 && end > at, name);
    return ui.slice(ui.slice(at - 6, at) === "async " ? at - 6 : at, end + 2);
}

async function check(ui) {
    const at = ui.indexOf('cm.on("change", (_, change) => {'), end = ui.indexOf("\n});", at);
    assert(at >= 0 && end > at, "the actual editor change handler");
    for (const origin of ["+input", "+delete", "undo", undefined, "setValue"]) {
        const nodes = Object.fromEntries(["canvas-host", "view-drawing", "status", "chips", "verdicts", "next"]
            .map(id => [id, {textContent:"old receipt", innerHTML:"old SVG", hidden:false}]));
        let onChange, delay, release, started, releaseDrawing, drawingCurrentCalls = 0;
        const waiting = new Promise(resolve => { started = resolve; });
        const deferred = new Promise(resolve => { release = resolve; });
        const c = vm.createContext({
            cm:{on:(_, callback)=>{onChange=callback;}}, timer:null, clearTimeout(){},
            setTimeout:(_,ms)=>{delay=ms;return 1;}, offerCompletion(){}, hideCompletion(){}, tick(){},
            editor:{value:"old buffer"}, active:"Facts.swift", layoutFile:"gate.manifest.swift", files:["Facts.swift","other.swift"],
            viewingShelf:null, theirsFiles:{}, carriedFiles:new Set(), formsFiles:new Set(["Facts.swift"]), renderGeneration:2,
            drawingGeneration:4, drawingNeighbors:{old:true}, drawingSnapshot:{buffer:"old buffer"},
            lastRefusals:[{file:"Facts.swift",premise:"old refusal"}], badFiles:new Set(["Facts.swift"]), flags:true,
            clearFlags(){c.flags=false;}, buildRail(){}, drawCanvases(){},
            judge(){return {parsed:{}};},
            fetch:async()=>{started();return {json:()=>deferred};},
            document:{getElementById:id=>nodes[id]}
        });
        for (const name of ["resetDrawing", "readingChanged", "render"])
            vm.runInContext(implementation(ui, name), c);
        vm.runInContext(ui.slice(at, end + 4), c);
        if (origin === "setValue") {
            onChange(null,{origin,text:["new"]});
            assert.equal(delay,undefined,"opening a file does not schedule a second reading");
            assert.equal(nodes["canvas-host"].innerHTML,"old SVG");
            continue;
        }
        const pending = c.render();
        await waiting;
        c.drawingWorld = () => new Promise(resolve => { releaseDrawing = resolve; });
        c.drawingCurrent = () => { drawingCurrentCalls++; return true; };
        vm.runInContext(implementation(ui, "drawCanvases"), c);
        const oldDrawing = c.drawCanvases();
        c.editor.value = "new buffer";
        onChange(null,{origin,text:["new"]});
        assert.equal(nodes["canvas-host"].innerHTML,"");
        assert(nodes["view-drawing"].hidden);
        assert.equal(c.drawingSnapshot,null);
        assert.equal(c.drawingNeighbors,null);
        assert(c.drawingGeneration > 4);
        assert.equal(c.lastRefusals.length,0);
        assert.equal(c.badFiles.size,0);
        assert.equal(c.flags,false);
        assert.equal(nodes.status.textContent,"Reading changed text…");
        for (const id of ["chips","verdicts","next"])assert.equal(nodes[id].textContent,"");
        assert.equal(delay,origin ? 400 : 150);
        release({verdict:"holds",refusals:[]});
        assert.equal(await pending,false,"the old court response is retired before the next tick");
        releaseDrawing({file:"Facts.swift",buffer:"old buffer"});
        await oldDrawing;
        assert.equal(drawingCurrentCalls,0,"the old drawing generation cannot resume painting");
        assert.equal(nodes.status.textContent,"Reading changed text…");
        assert.equal(nodes["canvas-host"].innerHTML,"");
    }
    return "EDIT PENDING GREEN: old SVG, verdict, flags and late court/drawing responses retired; opening unchanged";
}
module.exports = check;
if (require.main === module) {
    const files = process.argv.slice(2);
    if (!files.length) files.push(path.join(__dirname,"../web/ui.html"));
    (async()=>{for(const file of files)console.log(await check(fs.readFileSync(file,"utf8")));})()
        .catch(error=>{console.error(error);process.exitCode=1;});
}
