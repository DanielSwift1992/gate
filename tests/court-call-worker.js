// One isolated call to the same pinned wasm used by the bench. Test cases
// share neither a mutable wasm instance nor source files with another call.
'use strict';
const {parentPort, workerData} = require('node:worker_threads');
const court = require('../bin/court-wasm/node/vi_court.js');
if (!['judge', 'source_notation'].includes(workerData.operation))
    throw Error('unrecognized Court operation');
parentPort.postMessage(court[workerData.operation](workerData.input));
