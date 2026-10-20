"use strict";

// THE RENDERER, ported: a reading of DocumentKit's span engine (Sources/DocumentKit/
// Vector.swift) over the same parsed dictionary the judge reads. One parser, two
// readers: the judge checks the premises, this file draws the artifact. The vocabulary
// is a stated subset of the kit — a form outside it is reported by name, never absorbed.
//
// The Swift engine stays the reference: the layout arithmetic (SpanPx rounding, the
// HFlow division of a given width, MidOf's midpoint) is ported operation for operation,
// and the emitted markup mirrors the kit's format strings character for character.

// ── the kit vocabulary the reader tolerates on a drawing world: the seeds and
//    generics of DocumentKit this engine draws. The page, the checks and the gate
//    bench pass it to the plain court's port when they read a world to draw it,
//    so the parse that feeds this engine is one parse everywhere. ──
const kitVocabulary = {
    seeds: new Set(["SpanNothing", "SurfaceCard", "SurfaceTrack", "TextPrimary",
        "TextSecondary", "AccentRole", "ActionRole", "LineRole", "OnAccent", "OnActionRole",
        "Paper", "Mist", "Ink", "Accent", "Action", "Muted",
        "TextXXS", "TextXS", "TextS", "TextM", "TextL", "TitleT", "DisplayS", "Display",
        "WeightRegular", "WeightBold", "R12", "R20", "HairlineWidth", "FontStack",
        "U1", "U2", "U4", "U8", "U16", "U32", "U64", "U128", "U256", "U512",
        "EdgeMargin", "Breath", "HairBreath", "WideSurface", "FilmStripTall", "RestAir",
        // the dynamics medium, ported from the theory's triples branch
        "SlotRule", "R10", "TrackHeight", "DotSlot", "KeySide",
        // the spectral bridge: the weights axis, seven stated weights, the ladder
        "CanonicalWeights", "HAlphaGlow", "HBetaGlow", "PaschenGlow",
        "NeonYellowGlow", "NeonRedGlow", "SodiumDGlow", "SodiumIRGlow",
        "Rung0", "Rung1", "Rung2", "Rung3", "Rung4", "Rung5", "Rung6",
        "Rung7", "Rung8", "Unit",
        // the count question's encoding, a lattice name a judged world states
        "UnaryArithmeticEncoding",
        "SRGBRedPrimary", "SRGBGreenPrimary", "SRGBBluePrimary",
        "P3RedPrimary", "P3GreenPrimary", "P3BluePrimary",
        "Rec2020RedPrimary", "Rec2020GreenPrimary", "Rec2020BluePrimary"]),
    generics: new Set(["Air", "Flexible", "Layered", "TimedReveal", "FrozenReveal",
        "Tally", "CanvasSize", "Plus", "Times", "Twice", "Half", "Rest", "Seconds",
        "Fixed", "SpanHosted", "SpanLink", "Halfway", "Under", "Paired",
        "RuleKey", "TermText", "CenteredBaseline", "Chord",
        "LineTally", "TextWidth", "SpanLabelMidWrapped", "SpanLabelWrapped", "Succ",
        "XYZWrite", "PouredCoordinate", "Exactly", "EdgeSame", "EdgeEven", "EdgeOdd",
        "EdgeAtLeast", "PerceptualRung"]),
    bareSeeds: new Set(["RestAir"]),
};

// ── the dictionary's rungs, mirrored from Design.swift (values, not walks) ──

const seedText = new Map([
    ["SurfaceCard", "var(--vi-surface-card, #FFFFFF)"],
    ["SurfaceTrack", "var(--vi-surface-track, #F6F7F8)"],
    ["TextPrimary", "var(--vi-text-primary, rgba(0,0,0,0.80))"],
    ["TextSecondary", "var(--vi-text-secondary, rgba(0,0,0,0.54))"],
    ["AccentRole", "var(--vi-accent, #FFDD2D)"],
    ["ActionRole", "var(--vi-action, #336FEE)"],
    ["LineRole", "var(--vi-line, #EAECEE)"],
    ["OnAccent", "var(--vi-on-accent, #1C1C1E)"],
    ["OnActionRole", "var(--vi-on-action, #FFFFFF)"],
    ["Paper", "#FFFFFF"], ["Mist", "#F6F7F8"], ["Ink", "#1C1C1E"],
    ["Accent", "#FFDD2D"], ["Action", "#336FEE"], ["Muted", "#8A8A8E"],
    ["TextXXS", "10"], ["TextXS", "11"], ["TextS", "13"], ["TextM", "15"],
    ["TextL", "17"], ["TitleT", "21"], ["DisplayS", "28"], ["Display", "40"],
    ["WeightRegular", "400"], ["WeightBold", "700"],
    ["R10", "10"], ["R12", "12"], ["R20", "20"],
    ["HairlineWidth", "1"],
    ["FontStack", "Inter, Roboto, system-ui, sans-serif"],
    ["SoftShadow", '<filter id="soft-shadow" x="-20%" y="-20%" width="140%" height="140%">\n'
        + '<feDropShadow dx="0" dy="5" stdDeviation="10" flood-color="#000000" flood-opacity="0.10"/>\n'
        + "</filter>\n"],
]);

const seedCount = new Map([
    ["U1", 1], ["U2", 2], ["U4", 4], ["U8", 8], ["U16", 16], ["U32", 32],
    ["U64", 64], ["U128", 128], ["U256", 256], ["U512", 512],
    ["EdgeMargin", 16], ["Breath", 16], ["HairBreath", 8],
    ["WideSurface", 960], ["FilmStripTall", 150], ["Never", 0],
    ["Unit", 1],
    ["Rung0", 0], ["Rung1", 1], ["Rung2", 2], ["Rung3", 3], ["Rung4", 4],
    ["Rung5", 5], ["Rung6", 6], ["Rung7", 7], ["Rung8", 8],
    ["TrackHeight", 32], ["DotSlot", 12], ["KeySide", 80], ["PanelWide", 440],
]);

const spanShapes = new Set(["SpanTrack", "SpanTrackOutlined", "SpanHeroFace",
    "SpanLabel", "SpanLabelMid", "SpanLabelEnd", "SpanLabelMidWrapped",
    "SpanLabelWrapped", "SpanDot", "SpanBreathingDot"]);

// the stated font's own metrics, mirrored from GeneratedFontMetrics.swift
// (spelled from Assets' Inter file by `swift run Tools generate font`):
// codepoint:advance pairs in font units, TextWidth's one table
const fontUnitsPerEm = 2048;
const fontCapHeight = 1490;
const fontAdvances = new Map("32:576 33:589 34:954 35:1297 36:1314 37:2011 38:1319 39:614 40:747 41:747 42:1026 43:1355 44:590 45:942 46:590 47:738 48:1292 49:833 50:1249 51:1265 52:1323 53:1215 54:1270 55:1159 56:1267 57:1270 58:590 59:618 60:1355 61:1355 62:1355 63:1047 64:1978 65:1413 66:1340 67:1496 68:1478 69:1231 70:1209 71:1528 72:1522 73:550 74:1169 75:1376 76:1158 77:1850 78:1543 79:1566 80:1308 81:1566 82:1318 83:1314 84:1322 85:1524 86:1413 87:2018 88:1397 89:1390 90:1288 91:747 92:738 93:747 94:965 95:934 96:661 97:1150 98:1254 99:1170 100:1254 101:1194 102:758 103:1256 104:1211 105:496 106:496 107:1124 108:496 109:1794 110:1210 111:1228 112:1254 113:1254 114:771 115:1081 116:670 117:1211 118:1151 119:1676 120:1118 121:1151 122:1131 123:873 124:681 125:873 126:1355 160:576 161:589 162:1170 163:1251 164:1484 165:1126 166:553 167:1164 168:1210 169:1872 170:929 171:1193 172:1355 174:1364 175:978 176:933 177:1355 178:905 179:913 180:661 181:1200 182:1234 183:590 184:549 185:623 186:988 187:1193 188:1643 189:1735 190:1806 191:1047 192:1413 193:1413 194:1413 195:1413 196:1413 197:1413 198:2035 199:1496 200:1231 201:1231 202:1231 203:1231 204:550 205:550 206:550 207:550 208:1505 209:1543 210:1566 211:1566 212:1566 213:1566 214:1566 215:1355 216:1566 217:1524 218:1524 219:1524 220:1524 221:1390 222:1302 223:1262 224:1150 225:1150 226:1150 227:1150 228:1150 229:1150 230:1879 231:1170 232:1194 233:1194 234:1194 235:1194 236:496 237:496 238:496 239:496 240:1193 241:1210 242:1228 243:1228 244:1228 245:1228 246:1228 247:1355 248:1228 249:1211 250:1211 251:1211 252:1211 253:1151 254:1254 255:1151 8211:1024 8212:2048 8216:534 8217:534 8220:902 8221:902 8230:1770 8594:1954"
    .split(" ").map((pair) => pair.split(":").map(Number)));

// the measure TextWidth reads: advances summed in font units, ceiled to pixels;
// a character outside the table measures as an "m" (over-provides, never under)
function textWidthPx(text, sizePx) {
    const fallback = fontAdvances.get(109) || fontUnitsPerEm / 2;
    let total = 0;
    for (const ch of text) {
        total += fontAdvances.get(ch.codePointAt(0)) ?? fallback;
    }
    return Math.floor((total * sizePx + fontUnitsPerEm - 1) / fontUnitsPerEm);
}
const countsAsOne = new Set(["VerifiedView", "VerifiedInDepartment", "VerifiedAtRank",
    "VerifiedAtWorkplace"]);

// ── type expressions: `Name` or `Name<A, B<C>>`, the grammar entries already use ──

// the length of the angle run opening at `from`, matching close included
function angleSpanText(text, from) {
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

function parseType(source) {
    const text = source.trim();
    const open = text.indexOf("<");
    if (open < 0) return { head: text, args: [] };
    const head = text.slice(0, open);
    const inner = text.slice(open + 1, text.lastIndexOf(">"));
    const args = [];
    let depth = 0;
    let piece = "";
    for (const character of inner) {
        if (character === "<") depth += 1;
        if (character === ">") depth -= 1;
        if (character === "," && depth === 0) {
            args.push(parseType(piece));
            piece = "";
        } else {
            piece += character;
        }
    }
    if (piece.trim() !== "") args.push(parseType(piece));
    return { head, args };
}

// a node spelled back to its source form, for re-queuing a walked chain
function spellNode(node) {
    return node.args.length > 0
        ? node.head + "<" + node.args.map(spellNode).join(", ") + ">"
        : node.head;
}

// ── the fraction arithmetic, ported from the Frac readings ──

function exactInteger(value) {
    if (!Number.isSafeInteger(value)) refuse("unsupported", "arithmetic exceeds the port's exact integer range");
    return value;
}
function px(fraction) {
    return Math.floor(exactInteger(2 * fraction.n + fraction.d) / exactInteger(2 * fraction.d));
}
function sumFrac(a, b) {
    return { n: exactInteger(a.n * b.d + b.n * a.d), d: exactInteger(a.d * b.d) };
}
function midPx(x, w) {
    return Math.floor(exactInteger(2 * (2 * x.n * w.d + w.n * x.d) + 2 * x.d * w.d)
        / exactInteger(2 * 2 * x.d * w.d));
}
function endPx(x, w) {
    return px(sumFrac(x, w));
}

// ── the environment: one parse, two readers ──

function makeEnvironment(declarations, literals, topAliases) {
    return { declarations, literals, topAliases, errors: [],
        reads: new Map(), currentCanvas: null };
}

class DrawingRefusal extends Error {
    constructor(code, message) { super(message); this.code = code; }
}
function refuse(code, message) { throw new DrawingRefusal(code, message); }
function complain(env, message) { refuse("unsupported", message); }
function remainder(given, taken) {
    if (taken > given) refuse("rest-underflow", "Rest: taken exceeds given");
    return given - taken;
}
function wrappedLines(content, given, size) {
    const lines = []; let line = "";
    for (const word of content.split(" ").filter(Boolean)) {
        if (textWidthPx(word, size) > given) refuse("text-overflow", "word exceeds the given width");
        const candidate = line === "" ? word : line + " " + word;
        if (textWidthPx(candidate, size) <= given) line = candidate;
        else { lines.push(line); line = word; }
    }
    if (line !== "") lines.push(line);
    return lines;
}

function aliasNode(declaration, key) {
    const alias = declaration.aliases.get(key);
    return alias ? parseType(alias.target) : null;
}

function recordRead(env, name) {
    if (!env.currentCanvas) return;
    if (!env.declarations.has(name) && !env.literals.has(name)
        && !env.topAliases.has(name)) return;
    if (!env.reads.has(name)) env.reads.set(name, new Set());
    env.reads.get(name).add(env.currentCanvas);
}

function substitute(node, bindings) {
    if (node.args.length === 0 && bindings.has(node.head)) return bindings.get(node.head);
    // a dotted head whose owner is a bound parameter reads the axis of the
    // binding: `P.Vertical` under P = LampH is `LampH.Vertical`
    if (node.head.includes(".")) {
        const dot = node.head.indexOf(".");
        const owner = node.head.slice(0, dot);
        if (bindings.has(owner)) {
            const bound = bindings.get(owner);
            const spelled = bound.args.length > 0
                ? bound.head + "<" + bound.args.map(spellNode).join(", ") + ">"
                : bound.head;
            return { head: spelled + node.head.slice(dot),
                args: node.args.map((argument) => substitute(argument, bindings)) };
        }
    }
    return { head: node.head,
        args: node.args.map((argument) => substitute(argument, bindings)) };
}

const portArity = new Map([
    ...["Air", "Flexible", "Tally", "Twice", "Half", "Succ", "Tick", "TermText", "SpanHosted", "PerceptualRung"].map(n => [n,1]),
    ...["Plus", "Times", "Rest", "Seconds", "CanvasSize", "Fixed", "Layered", "FrozenReveal", "SpanLink", "RuleKey", "Chord", "Halfway", "Under", "CenteredBaseline", "TextWidth", "Paired", "EdgeEven", "EdgeOdd"].map(n => [n,2]),
    ...["TimedReveal", "LineTally", "XYZWrite", "EdgeSame", "EdgeAtLeast"].map(n => [n,3]),
    ["PouredCoordinate",6]
]);
function executableOverride(env, declaration, seen = new Set()) {
    if (!declaration || seen.has(declaration.qualified)) return null;
    seen.add(declaration.qualified);
    if (declaration.drawingUnsupported) return declaration.drawingUnsupported;
    for (const name of declaration.conformances) {
        const reason = executableOverride(env, env.declarations.get(name), seen);
        if (reason) return reason;
    }
    return null;
}
function resolveHead(env, node) {
    if (!node) complain(env, "missing type");
    let cursor = node;
    for (let step = 0; step < 32; step += 1) {
        recordRead(env, cursor.head);
        if (portArity.has(cursor.head) && cursor.args.length !== portArity.get(cursor.head)) complain(env, cursor.head + ": unsupported argument count");
        const stated = env.declarations.get(cursor.head);
        if (stated && (seedCount.has(cursor.head) || seedText.has(cursor.head) || portArity.has(cursor.head))) complain(env, cursor.head + ": a local definition shadows the kit");
        const override = executableOverride(env, stated);
        if (override) complain(env, cursor.head + ": " + override);
        const alias = env.topAliases.get(cursor.head);
        // a dotted head reads an axis off a resolved owner: `LampMode.Ink` is the
        // Ink alias of whatever term LampMode stands for
        if (!alias && cursor.head.includes(".")) {
            const angleAt = cursor.head.indexOf("<");
            const dot = cursor.head.indexOf(".",
                angleAt >= 0 ? angleAt + angleSpanText(cursor.head, angleAt) - 1 : 0);
            if (dot < 0) return cursor;
            // the chain is walked segment by segment, the way the reference
            // judge walks it: one axis per step, the remainder re-queued
            const tail = cursor.head.slice(dot + 1);
            const nextDot = tail.indexOf(".");
            const axisName = nextDot < 0 ? tail : tail.slice(0, nextDot);
            const rest = nextDot < 0 ? "" : tail.slice(nextDot + 1);
            const base = resolveHead(env, parseType(cursor.head.slice(0, dot)));
            const owner = env.declarations.get(base.head);
            const slot = owner ? owner.aliases.get(axisName) : null;
            if (slot) {
                let target = parseType(slot.target);
                // the owner may stand as a generic instance: its arguments bind
                // the declaration's parameters inside the axis being read
                if (owner.params && owner.params.length > 0
                    && base.args.length === owner.params.length) {
                    const bindings = new Map();
                    owner.params.forEach((parameter, index) => {
                        bindings.set(parameter, base.args[index]);
                    });
                    target = substitute(target, bindings);
                }
                cursor = rest === ""
                    ? target
                    : parseType(spellNode(target) + "." + rest);
                continue;
            }
            complain(env, "`" + cursor.head + "` reads no declared axis");
            return cursor;
        }
        if (!alias) return cursor;
        if (alias.params && alias.params.length > 0) {
            if (cursor.args.length !== alias.params.length) return cursor;
            const bindings = new Map();
            for (let index = 0; index < alias.params.length; index += 1) {
                bindings.set(alias.params[index], cursor.args[index]);
            }
            cursor = substitute(parseType(alias.target), bindings);
            continue;
        }
        if (cursor.args.length > 0) return cursor;
        cursor = parseType(alias.target);
    }
    complain(env, "alias expansion exceeds the supported budget");
}

// Named aliases in the pinned kit matter to Swift's runtime type spelling,
// including RuleKey's data attributes. Counts alone do not determine a name.
const kitTypeAliases = new Map([
    ["Rung0", "Never"], ["Rung1", "Unit"], ["Rung2", "Twice<Unit>"],
    ["Rung3", "Plus<Twice<Unit>, Unit>"], ["Rung4", "Twice<Twice<Unit>>"],
    ["Rung5", "Plus<Twice<Twice<Unit>>, Unit>"], ["Rung6", "Twice<Plus<Twice<Unit>, Unit>>"],
    ["Rung7", "Plus<Twice<Twice<Unit>>, Plus<Twice<Unit>, Unit>>"],
    ["Rung8", "Twice<Twice<Twice<Unit>>>"]
]);
function runtimeType(env, raw) {
    let node = resolveHead(env, raw);
    if (kitTypeAliases.has(node.head) && !env.declarations.has(node.head)) return runtimeType(env, parseType(kitTypeAliases.get(node.head)));
    if (node.head === "Twice" && node.args.length === 1) node = {head: "Plus", args: [node.args[0], node.args[0]]};
    if (!env.declarations.has(node.head) && !["Never", "Unit", "Succ", "Plus", "Times", "Half", "Rest", "Tick"].includes(node.head)) complain(env, node.head + ": runtime type name outside this subset");
    return {head: node.head, args: node.args.map(n => runtimeType(env, n))};
}
for (const width of [1,2,4,8,16,32,64,128,256,512]) kitTypeAliases.set("U" + width, width === 1 ? "Unit" : "Twice<U" + width / 2 + ">");
const leafCountBases = new Set(["Structure", "Close", "Open", "Pair", "Employee", "Roster", "Team", "AccessLedger"]);
function supportedCount(env, declaration, seen = new Set()) {
    if (seen.has(declaration.name) || declaration.drawingUnsupported) return false;
    seen.add(declaration.name);
    return declaration.conformances.some(c => leafCountBases.has(c)
        || (env.declarations.has(c) && supportedCount(env, env.declarations.get(c), seen)));
}

// ── counts: the unit trees a canvas and an Air measure by ──

const canonicalShares = new Map([
    // the line weights (Spectrum.swift at ff6c51d): each reads the CIE 1931
    // 2-degree table at its wavelength, rounded as the nearest lattice pair
    // that preserves chromaticity; sodium's blind row is measured, not assumed
    ["HAlphaGlow", [8, 3, 0]], ["HBetaGlow", [3, 10, 33]],
    ["PaschenGlow", [0, 0, 0]], ["NeonYellowGlow", [31, 26, 0]],
    ["NeonRedGlow", [13, 5, 0]], ["SodiumDGlow", [33, 25, 0]],
    ["SodiumIRGlow", [0, 0, 0]],
    // the stated displays: every primary is the column of its standard's
    // published matrix — IEC 61966-2-1, SMPTE EG 432-1, ITU-R BT.2020 —
    // rounded once onto the lattice, a thirty-second per rung.
    ["SRGBRedPrimary", [13, 7, 1]], ["SRGBGreenPrimary", [11, 23, 4]],
    ["SRGBBluePrimary", [6, 2, 30]], ["P3RedPrimary", [16, 7, 0]],
    ["P3GreenPrimary", [9, 22, 1]], ["P3BluePrimary", [6, 3, 33]],
    ["Rec2020RedPrimary", [20, 8, 0]], ["Rec2020GreenPrimary", [5, 22, 1]],
    ["Rec2020BluePrimary", [5, 2, 34]],
]);
const shareIndex = new Map([["XShare", 0], ["YShare", 1], ["ZShare", 2]]);

function countOf(env, rawNode) {
    const value = readCount(env, rawNode);
    if (!Number.isSafeInteger(value) || value < 0) complain(env, "count outside the supported integer range");
    return value;
}
function readCount(env, rawNode) {
    if (!rawNode) {
        complain(env, "a count is missing where a member expects one");
        return 0;
    }
    // a canonical weight's axis is a stated magnitude of the kit: the settled
    // reading of its composed rungs (Spectrum.swift, CanonicalWeights). The
    // owner may itself be an alias or a dotted chain (a world's gas slot):
    // it settles to a name first, the way every axis walk settles its owner
    if (rawNode.head.includes(".")) {
        const lastDot = rawNode.head.lastIndexOf(".");
        const ownerSpelled = rawNode.head.slice(0, lastDot);
        const axis = rawNode.head.slice(lastDot + 1);
        if (shareIndex.has(axis)) {
            const owner = canonicalShares.has(ownerSpelled)
                ? ownerSpelled
                : resolveHead(env, { head: ownerSpelled, args: [] }).head;
            if (canonicalShares.has(owner)) {
                return canonicalShares.get(owner)[shareIndex.get(axis)];
            }
        }
    }
    const node = resolveHead(env, rawNode);
    // one canonical coordinate of a pour, unfolded to its own definition:
    // Plus<Times<A, ShareA>, Plus<Times<B, ShareB>, Times<C, ShareC>>>
    if (node.head === "PouredCoordinate" && node.args.length === 6) {
        return countOf(env, node.args[0]) * countOf(env, node.args[1])
            + countOf(env, node.args[2]) * countOf(env, node.args[3])
            + countOf(env, node.args[4]) * countOf(env, node.args[5]);
    }
    if (seedCount.has(node.head)) return seedCount.get(node.head);
    if (countsAsOne.has(node.head)) return 1;
    if (node.head === "Plus") return countOf(env, node.args[0]) + countOf(env, node.args[1]);
    if (node.head === "Times") return countOf(env, node.args[0]) * countOf(env, node.args[1]);
    if (node.head === "Twice") return 2 * countOf(env, node.args[0]);
    if (node.head === "Half") {
        const whole = countOf(env, node.args[0]);
        if (whole % 2) refuse("half-odd", "Half: count is not even");
        return whole / 2;
    }
    if (node.head === "Rest") return remainder(countOf(env, node.args[0]), countOf(env, node.args[1]));
    // the counter's constructor counts itself: one more than what it wraps
    // (Tick.count = Previous.count + 1, the floor Never counts 0)
    if (node.head === "Tick") return 1 + countOf(env, node.args[0]);
    // Succ inherits Structure.count = 1; it does not count its predecessor.
    if (node.head === "Succ") return 1;
    // the wrapped line tally, mirrored from Vector.swift: how many lines a
    // literal earns under the same greedy measure the wrapped labels draw
    // with, over a stated dictionary width. A band's height is then a type:
    // Times over LineTally. Keep the drawing's slice the same rung, or the
    // measure lies.
    if (node.head === "LineTally") {
        const content = textOf(env, node.args[0]);
        const given = countOf(env, node.args[1]);
        const size = parseInt(textOf(env, node.args[2]), 10) || 0;
        return wrappedLines(content, given, size).length;
    }
    // the measured width of a word, mirrored from Vector.swift (TextWidth): the
    // advances of its characters summed at a stated size, the same reader the
    // wrapped labels draw with. A slot sized by its own words: no stated width.
    if (node.head === "TextWidth") {
        const content = textOf(env, node.args[0]);
        const size = parseInt(textOf(env, node.args[1]), 10) || 0;
        return textWidthPx(content, size);
    }
    const declaration = env.declarations.get(node.head);
    if (declaration && supportedCount(env, declaration) && declaration.entries.length > 0) {
        let total = 0;
        for (const entry of declaration.entries) {
            total += countOf(env, { head: entry.head, args: entry.args.map(parseType) });
        }
        return total;
    }
    if (declaration && supportedCount(env, declaration)) return 1;
    complain(env, "no count for `" + node.head + "`");
    return 0;
}

// ── texts: an atom's reading ──

// A term name before XML serialization; Swift names resolved runtime types.
function spellTerm(env, node) {
    const settled = runtimeType(env, node);
    if (settled.args.length === 0) return settled.head;
    return settled.head + "<"
        + settled.args.map((argument) => spellTerm(env, argument)).join(", ")
        + ">";
}

function textOf(env, rawNode) {
    if (!rawNode) {
        complain(env, "a reading is missing where a coordinate expects one");
        return "";
    }
    const node = resolveHead(env, rawNode);
    if (node.head === "Tally") return String(countOf(env, node.args[0]));
    if (node.head === "Seconds") {
        const frequency = countOf(env, node.args[1]);
        if (frequency === 0 || frequency > 65536 || (frequency & (frequency - 1)) !== 0
            || countOf(env, node.args[0]) > 1e9) complain(env, "Seconds outside the port's exact binary fraction range");
        const seconds = countOf(env, node.args[0]) / frequency;
        // Swift Double.description includes .0 for integral seconds.
        return Number.isInteger(seconds) ? seconds + ".0" : String(seconds);
    }
    // the perceptual rung of a band (Spectrum.swift, PerceptualRung): the
    // position of the highest lit door, zero for a quenched band — a halving
    // is one felt ratio, so felt distance is a difference of rungs. The walks
    // are the kit's own, mirrored as their eight marks.
    if (node.head === "PerceptualRung" && node.args.length === 1) {
        const marks = textOf(env, node.args[0]);
        if (typeof marks !== "string" || marks.length !== 8) {
            complain(env, "a band settles in eight cuts, not "
                + (typeof marks === "string" ? marks.length : 0));
            return "0";
        }
        const lit = marks.indexOf("1");
        return lit < 0 ? "0" : String(8 - lit);
    }
    // the chart-neutral edge write (Spectrum.swift, XYZWrite): three
    // canonical sums printed as the browser's device-independent form,
    // color(xyz-d65 ...) in 256ths. The canon computes nothing and clamps
    // nothing: the device maps the value onto whatever it can reach.
    if (node.head === "XYZWrite" && node.args.length === 3) {
        const thousandths = (value) => {
            const scaled = Math.floor(value * 1000 / 256);
            const whole = Math.floor(scaled / 1000);
            const rest = scaled % 1000;
            const padded = rest < 10 ? "00" + rest : rest < 100 ? "0" + rest : String(rest);
            return whole + "." + padded;
        };
        return "color(xyz-d65 " + thousandths(countOf(env, node.args[0]))
            + " " + thousandths(countOf(env, node.args[1]))
            + " " + thousandths(countOf(env, node.args[2])) + ")";
    }
    // the centred baseline of the kit: the zone's middle plus half the font's
    // own capital height (units 2048, cap 1490), ported from CenteredBaseline
    if (node.head === "CenteredBaseline") {
        const zone = countOf(env, node.args[0]);
        const size = parseInt(textOf(env, node.args[1]), 10) || 0;
        return String(Math.floor((zone * fontUnitsPerEm + fontCapHeight * size
            + fontUnitsPerEm) / (2 * fontUnitsPerEm)));
    }
    // the dynamics medium's term label: the slot's current term, spelled as written
    if (node.head === "TermText") return spellTerm(env, node.args[0]);
    if (node.head === "Halfway") {
        return String(Math.floor((countOf(env, node.args[0])
            + countOf(env, node.args[1])) / 2));
    }
    if (node.head === "Under") {
        return String(countOf(env, node.args[0])
            + (parseInt(textOf(env, node.args[1]), 10) || 0));
    }
    if (node.head === "CanvasSize") {
        return "0 0 " + countOf(env, node.args[0]) + " " + countOf(env, node.args[1]);
    }
    if (env.literals.has(node.head)) {
        if (!env.declarations.has(node.head)) complain(env, node.head + ": literal has no declared owner");
        const literal = env.literals.get(node.head);
        if (literal.unsupported) complain(env, literal.unsupported);
        return literal.value;
    }
    if (seedText.has(node.head)) return seedText.get(node.head);
    complain(env, "no reading for `" + node.head + "`");
    return "";
}

// Escape at the XML boundary, once, exactly as DocumentKit.XMLEscaped.
function svgText(text) {
    if (/[\u0000-\u0008\u000b\u000c\u000e-\u001f\ufffe\uffff]/u.test(String(text))) refuse("unsupported", "text outside the XML character subset");
    return String(text).replaceAll("&", "&amp;").replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&apos;");
}
const svgAttr = svgText;
function spanHref(text) {
    try {
        const protocol = new URL(text, "https://gate.invalid/").protocol;
        if (["http:", "https:", "mailto:"].includes(protocol)) return text;
    } catch (_) { /* unsupported URL */ }
    refuse("unsupported", "link scheme outside the browser drawing subset");
}

// ── spannings: content that draws itself into a handed slice ──

function spanningOf(env, rawNode) {
    if (!rawNode) {
        complain(env, "a span is missing where a slot expects one");
        return () => "";
    }
    const node = resolveHead(env, rawNode);
    if (node.head === "SpanHosted") {
        return () => nodeString(env, node.args[0]);
    }
    if (node.head === "SpanLink") {
        const inner = spanningOf(env, node.args[1]);
        return (x, w) => '<a href="' + svgAttr(spanHref(textOf(env, node.args[0]))) + '">\n'
            + inner(x, w) + "</a>\n";
    }
    if (node.head === "Layered") {
        const a = spanningOf(env, node.args[0]);
        const b = spanningOf(env, node.args[1]);
        return (x, w) => a(x, w) + b(x, w);
    }
    // the dynamics medium's drawn button: a face that names its rules, so a host
    // can press what it reads. A `Chord` cons lists several rules of one slot
    // behind one face; the leaves are gathered in declaration order. Every leaf
    // must stand in the file: the drawn key of an undeclared rule is refused
    // here, the page's copy of RuleKey's bound.
    if (node.head === "RuleKey") {
        const leaves = [];
        const spellWhole = (term) => term.args.length === 0 ? term.head
            : term.head + "<" + term.args.map(spellWhole).join(",") + ">";
        const gather = (term) => {
            const settled = resolveHead(env, term);
            // an Exactly leaf is spelled whole, spaces shed: the press supplies
            // the atom and the atom travels with the press (Dynamics, Exactly)
            if (settled.head === "Exactly" && settled.args.length === 1) {
                leaves.push({ spelled: spellWhole(runtimeType(env, settled.args[0])),
                    bare: settled.args[0].head });
                return;
            }
            if (settled.head === "Chord" && settled.args.length === 2) {
                gather(settled.args[0]);
                gather(settled.args[1]);
            } else {
                // any other leaf is named bare, its placeholder tail dropped
                leaves.push({ spelled: settled.head, bare: settled.head });
            }
        };
        gather(node.args[0]);
        let slot = null;
        for (const leaf of leaves) {
            const declared = env.declarations.get(leaf.bare);
            if (!declared) {
                complain(env, "RuleKey names `" + leaf.bare
                    + "`, and the file declares no such rule");
                return () => "";
            }
            const current = declared.aliases.get("Slot");
            if (!current) complain(env, leaf.bare + " states no Slot");
            const spelling = spellTerm(env, parseType(current.target));
            if (slot && slot !== spelling) complain(env, "Chord names different slots");
            slot = spelling;
        }
        const face = spanningOf(env, node.args[1]);
        return (x, w) => '<g class="vi-rule" data-vi-rules="' + svgAttr(leaves.map((leaf) => leaf.spelled).join(" "))
            + '" data-vi-slot="' + svgAttr(slot) + '" cursor="pointer">\n'
            + face(x, w) + "</g>\n";
    }
    // equality of two magnitudes, read at the edge (Vector.swift, EdgeSame):
    // when the counts agree the face renders, when they differ nothing does;
    // a conjunction of equalities is the nesting of this form in itself
    if (node.head === "EdgeSame" && node.args.length === 3) {
        if (countOf(env, node.args[0]) !== countOf(env, node.args[1])) {
            return () => "";
        }
        return spanningOf(env, node.args[2]);
    }
    // the order of two magnitudes, read at the same edge (EdgeAtLeast): when
    // the first count reaches the second the face renders; short of it, nothing
    if (node.head === "EdgeAtLeast" && node.args.length === 3) {
        if (countOf(env, node.args[0]) < countOf(env, node.args[1])) {
            return () => "";
        }
        return spanningOf(env, node.args[2]);
    }
    // a magnitude's parity, read at the edge (EdgeEven / EdgeOdd): the count
    // splits into pairs or it does not, and the face follows the split — a
    // fringe is a living reader of its gap, no certificate to go stale
    if (node.head === "EdgeEven" && node.args.length === 2) {
        if (countOf(env, node.args[0]) % 2 !== 0) return () => "";
        return spanningOf(env, node.args[1]);
    }
    if (node.head === "EdgeOdd" && node.args.length === 2) {
        if (countOf(env, node.args[0]) % 2 !== 1) return () => "";
        return spanningOf(env, node.args[1]);
    }
    if (node.head === "SpanNothing") return () => "";
    const declaration = env.declarations.get(node.head);
    if (!declaration) {
        complain(env, "`" + node.head + "` is not a declared span");
        return () => "";
    }
    const shape = declaration.conformances.find((name) => spanShapes.has(name));
    if (!shape) {
        complain(env, "`" + node.head + "` conforms to no span the renderer carries");
        return () => "";
    }
    let bindings = null;
    if (declaration.params && declaration.params.length > 0
        && node.args.length === declaration.params.length) {
        bindings = new Map();
        declaration.params.forEach((parameter, index) => {
            bindings.set(parameter, node.args[index]);
        });
    }
    const read = (key) => {
        let slotNode = aliasNode(declaration, key);
        if (!slotNode) {
            complain(env, node.head + " states no " + key);
            slotNode = { head: "?", args: [] };
        }
        if (bindings) slotNode = substitute(slotNode, bindings);
        return textOf(env, slotNode);
    };
    const readAttr = (key) => svgAttr(read(key));
    if (shape === "SpanTrack") {
        return (x, w) => '<rect x="' + px(x) + '" width="' + px(w) + '" height="'
            + readAttr("H") + '" rx="' + readAttr("Radius") + '" fill="' + readAttr("Fill") + '"/>\n';
    }
    if (shape === "SpanTrackOutlined") {
        return (x, w) => '<rect x="' + px(x) + '" width="' + px(w) + '" height="'
            + readAttr("H") + '" rx="' + readAttr("Radius") + '" fill="' + readAttr("Fill")
            + '" stroke="' + readAttr("Stroke") + '" stroke-width="'
            + seedText.get("HairlineWidth") + '"/>\n';
    }
    if (shape === "SpanHeroFace") {
        return (x, w) => '<g filter="url(#soft-shadow)">\n<rect x="' + px(x)
            + '" width="' + px(w) + '" height="' + readAttr("H") + '" rx="' + readAttr("Radius")
            + '" fill="' + readAttr("Fill") + '"/>\n</g>\n';
    }
    if (shape === "SpanLabel") {
        return (x, w) => '<text x="' + px(x) + '" y="' + readAttr("Y")
            + '" text-anchor="start" fill="' + readAttr("FillColor") + '" font-weight="'
            + readAttr("Weight") + '" font-size="' + readAttr("Size") + '">'
            + svgText(read("Content")) + "</text>\n";
    }
    if (shape === "SpanLabelMidWrapped" || shape === "SpanLabelWrapped") {
        // mirrored from Vector.swift: the words fill measured lines within the
        // width the slice hands over, breaking greedily by the fitted gate's
        // measure, each line one stated pitch below the last. Wrapping earns
        // lines, never truncation: a word wider than the slice refuses, loudly.
        const size = parseInt(readAttr("Size"), 10) || 0;
        const base = parseInt(readAttr("Y"), 10) || 0;
        const pitch = parseInt(readAttr("LinePitch"), 10) || 0;
        const content = read("Content");
        return (x, w) => {
            const given = px(w);
            const lines = wrappedLines(content, given, size);
            const anchored = shape === "SpanLabelMidWrapped"
                ? (piece, index) => '<text x="' + midPx(x, w) + '" y="'
                    + (base + pitch * index) + '" text-anchor="middle" fill="'
                    + readAttr("FillColor") + '" font-weight="' + readAttr("Weight")
                    + '" font-size="' + readAttr("Size") + '">' + svgText(piece) + "</text>\n"
                : (piece, index) => '<text x="' + px(x) + '" y="'
                    + (base + pitch * index) + '" text-anchor="start" fill="' + readAttr("FillColor")
                    + '" font-weight="' + readAttr("Weight") + '" font-size="'
                    + readAttr("Size") + '">' + svgText(piece) + "</text>\n";
            return lines.map(anchored).join("");
        };
    }
    if (shape === "SpanLabelMid") {
        return (x, w) => '<text x="' + midPx(x, w) + '" y="' + readAttr("Y")
            + '" text-anchor="middle" fill="' + readAttr("FillColor") + '" font-weight="'
            + readAttr("Weight") + '" font-size="' + readAttr("Size") + '">'
            + svgText(read("Content")) + "</text>\n";
    }
    if (shape === "SpanLabelEnd") {
        return (x, w) => '<text x="' + endPx(x, w) + '" y="' + readAttr("Y")
            + '" text-anchor="end" fill="' + readAttr("FillColor") + '" font-weight="'
            + readAttr("Weight") + '" font-size="' + readAttr("Size") + '">'
            + svgText(read("Content")) + "</text>\n";
    }
    if (shape === "SpanDot") {
        return (x, w) => '<circle cx="' + midPx(x, w) + '" cy="' + readAttr("CY")
            + '" r="' + readAttr("R") + '" fill="' + readAttr("Fill") + '"/>\n';
    }
    if (shape === "SpanBreathingDot") {
        return (x, w) => '<circle cx="' + midPx(x, w) + '" cy="' + readAttr("CY")
            + '" r="' + readAttr("R") + '" fill="' + readAttr("Fill")
            + '"><animate attributeName="opacity" values="1;0.55;1" dur="4s" '
            + 'repeatCount="indefinite"/></circle>\n';
    }
    return () => "";
}

// ── the row: HFlow's division of a given width, ported member for member ──

function rowString(env, declaration) {
    const givenNode = aliasNode(declaration, "Given");
    if (!givenNode) {
        complain(env, declaration.name + " states no Given");
        return "";
    }
    const given = countOf(env, givenNode);
    const members = [];
    for (const entry of declaration.entries) {
        const entryNode = { head: entry.head, args: entry.args.map(parseType) };
        for (const node of memberNodes(env, entryNode)) {
        if (node.head === "Air") {
            members.push({ taken: countOf(env, node.args[0]), stretch: 0, draw: null });
            continue;
        }
        if (node.head === "Flexible") {
            members.push({ taken: 0, stretch: 1, draw: spanningOf(env, node.args[0]) });
            continue;
        }
        if (node.head === "Fixed") {
            const width = countOf(env, node.args[0]);
            const drawn = spanningOf(env, node.args[1]);
            members.push({ taken: width, stretch: 0,
                draw: (x) => drawn(x, { n: width, d: 1 }), fixed: true });
            continue;
        }
        if (node.head === "RestAir") {
            members.push({ taken: 0, stretch: 1, draw: null });
            continue;
        }
        complain(env, "`" + node.head
            + "` is not a member the row carries (Air, Flexible, Fixed, RestAir)");
        }
    }
    const taken = members.reduce((sum, member) => sum + member.taken, 0);
    const stretch = members.reduce((sum, member) => sum + member.stretch, 0);
    if (stretch === 0) {
        complain(env, declaration.name
            + ": an axis under a given owes its remainder to someone — end it with a flexible member");
        return "";
    }
    const free = { n: remainder(given, taken), d: stretch };
    let markup = "";
    let x = { n: 0, d: 1 };
    for (const member of members) {
        if (member.draw) {
            markup += '<g transform="translate(' + px(x) + ', 0)">\n'
                + member.draw({ n: 0, d: 1 }, free) + "</g>\n";
        }
        const advance = { n: member.taken * free.d + free.n * member.stretch, d: free.d };
        x = sumFrac(x, advance);
    }
    return markup;
}

// ── the vertical axis: members take their extents down the page ──

function memberNodes(env, node) {
    const resolved = resolveHead(env, node);
    if (resolved.head === "Paired" && resolved.args.length === 2) {
        return [...memberNodes(env, resolved.args[0]),
            ...memberNodes(env, resolved.args[1])];
    }
    return [resolved];
}

function verticalMembers(env, declaration) {
    const members = [];
    for (const entry of declaration.entries) {
        const entryNode = { head: entry.head, args: entry.args.map(parseType) };
        for (const node of memberNodes(env, entryNode)) {
        if (node.head === "Air") {
            members.push({ taken: countOf(env, node.args[0]), stretch: 0, draw: null });
            continue;
        }
        if (node.head === "RestAir") {
            members.push({ taken: 0, stretch: 1, draw: null });
            continue;
        }
        if (node.head === "Fixed") {
            members.push({ taken: countOf(env, node.args[0]), stretch: 0,
                draw: spanningOf(env, node.args[1]) });
            continue;
        }
        if (node.head === "Flexible") {
            members.push({ taken: 0, stretch: 1, draw: spanningOf(env, node.args[0]) });
            continue;
        }
        complain(env, "`" + node.head
            + "` is not a member the axis carries (Air, Fixed, Flexible, RestAir)");
        }
    }
    return members;
}

function verticalString(env, members, across, free) {
    let markup = "";
    let y = { n: 0, d: 1 };
    for (const member of members) {
        if (member.draw) {
            markup += '<g transform="translate(0, ' + px(y) + ')">\n'
                + member.draw({ n: 0, d: 1 }, { n: across, d: 1 }) + "</g>\n";
        }
        const advance = { n: member.taken * free.d + free.n * member.stretch, d: free.d };
        y = sumFrac(y, advance);
    }
    return markup;
}

// ── nodes: groups, reveals, rows, and the canvas itself ──

function nodeString(env, rawNode) {
    if (!rawNode) {
        complain(env, "content is missing where a band expects it");
        return "";
    }
    const node = resolveHead(env, rawNode);
    if (node.head === "TimedReveal") {
        return '<g opacity="0"><set attributeName="opacity" to="1" begin="'
            + svgAttr(textOf(env, node.args[0])) + 's" dur="' + svgAttr(textOf(env, node.args[1])) + 's"/>\n'
            + nodeString(env, node.args[2]) + "</g>\n";
    }
    if (node.head === "FrozenReveal") {
        return '<g opacity="0"><set attributeName="opacity" to="1" begin="'
            + svgAttr(textOf(env, node.args[0])) + 's" fill="freeze"/>\n'
            + nodeString(env, node.args[1]) + "</g>\n";
    }
    if (node.head === "Never") return "";
    const declaration = env.declarations.get(node.head);
    if (!declaration) {
        complain(env, "`" + node.head + "` resolves to no drawable declaration");
        return "";
    }
    if (declaration.conformances.includes("HFlow")) return rowString(env, declaration);
    if (declaration.conformances.includes("VFlow")) {
        const givenNode = aliasNode(declaration, "Given");
        const acrossNode = aliasNode(declaration, "Across");
        if (!givenNode || !acrossNode) {
            complain(env, declaration.name + " states no Given or Across yet");
            return "";
        }
        const given = countOf(env, givenNode);
        const across = countOf(env, acrossNode);
        const members = verticalMembers(env, declaration);
        const taken = members.reduce((sum, member) => sum + member.taken, 0);
        const stretch = members.reduce((sum, member) => sum + member.stretch, 0);
        if (stretch === 0) {
            complain(env, declaration.name
                + ": an axis under a given owes its remainder to someone — end it with a flexible member");
            return "";
        }
        return verticalString(env, members, across, { n: remainder(given, taken), d: stretch });
    }
    if (declaration.conformances.includes("Group")) {
        let markup = "";
        for (const entry of declaration.entries) {
            markup += nodeString(env, { head: entry.head, args: entry.args.map(parseType) });
        }
        return markup;
    }
    complain(env, "`" + node.head + "` is not a form the renderer carries");
    return "";
}

// ── every canvas in the file, drawn ──

function renderAll(declarations, order, literals, topAliases) {
    const env = makeEnvironment(declarations, literals, topAliases);
    const canvases = [], refusals = [];
    for (const qualified of order) {
        const declaration = declarations.get(qualified);
        env.currentCanvas = declaration.name;
        if (!declaration.conformances.some(c => c === "GrownDiagram" || c === "Diagram")) continue;
        try {
        resolveHead(env, {head: qualified, args: []});
        if (declaration.conformances.includes("GrownDiagram")) {
            const acrossNode = aliasNode(declaration, "Across");
            const aria = aliasNode(declaration, "AriaLabel");
            if (!acrossNode) {
                complain(env, declaration.name + " states no Across yet");
                continue;
            }
            const across = countOf(env, acrossNode);
            const members = verticalMembers(env, declaration);
            const stretch = members.reduce((sum, member) => sum + member.stretch, 0);
            if (stretch > 0) {
                complain(env, declaration.name
                    + ": a grown axis has no remainder to share — a flexible member cannot stand here");
                continue;
            }
            const taken = members.reduce((sum, member) => sum + member.taken, 0);
            const backdrop = aliasNode(declaration, "Backdrop");
            if (backdrop && resolveHead(env, backdrop).head !== "Never") complain(env, "Backdrop is outside this drawing subset");
            const defs = aliasNode(declaration, "Defs");
            const svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + across
                + " " + taken + '" role="img" data-vi-canvas="1" font-family="'
                + seedText.get("FontStack") + '" aria-label="' + svgAttr(textOf(env, aria)) + '">\n'
                + (defs ? (seedText.has(defs.head) ? seedText.get(defs.head)
                    : nodeString(env, defs)) : "")
                + verticalString(env, members, across, { n: 0, d: 1 })
                + "</svg>\n";
            canvases.push({ name: declaration.name, svg });
            continue;
        }
        if (!declaration.conformances.includes("Diagram")) continue;
        const size = aliasNode(declaration, "Size");
        const aria = aliasNode(declaration, "AriaLabel");
        const content = aliasNode(declaration, "Content");
        if (!size || !aria || !content) {
            complain(env, declaration.name + " states no Size, AriaLabel, or Content");
            continue;
        }
        const svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="' + svgAttr(textOf(env, size))
            + '" role="img" data-vi-canvas="1" font-family="' + seedText.get("FontStack")
            + '" aria-label="' + svgAttr(textOf(env, aria)) + '">\n'
            + nodeString(env, content) + "\n</svg>\n";
        canvases.push({ name: declaration.name, svg });
        } catch (error) {
            if (!(error instanceof DrawingRefusal) && !(error instanceof RangeError)) throw error;
            const address = (declaration.file || "world.swift") + "#" + qualified;
            const code = error.code || "unsupported";
            refusals.push({name: declaration.name, status: "refused", code, address});
            env.errors.push(address + ": " + code + " — " + error.message);
        }
    }
    return { canvases, refusals, errors: env.errors, reads: env.reads };
}

// textOf and makeEnvironment travel with the engine so the build can read a
// stated colour through the same door the canvas reads it through: the palette
// is printed by this reader, never by a second copy of it.
if (typeof module !== "undefined") {
    module.exports = { renderAll, parseType, canonicalShares, seedCount,
        textOf, makeEnvironment, kitVocabulary };
}
