#!/usr/bin/env node
"use strict";
// Transport only; browser and contract both compute through bin/press.js.
const fs = require("fs");
const { apply } = require("./press.js");
try {
    const request = JSON.parse(fs.readFileSync(0, "utf8"));
    if (!Array.isArray(request.arguments) || !request.arguments.every(x => typeof x === "string")
        || !["state", "dictionary", "statePath", "dictionaryPath"].every(key => typeof request[key] === "string")) {
        throw new Error("invalid Press request");
    }
    console.log(JSON.stringify(apply(request.arguments, request.state, request.dictionary, request)));
} catch (error) {
    console.error("press contract transport: " + error.message);
    process.exitCode = 2;
}
