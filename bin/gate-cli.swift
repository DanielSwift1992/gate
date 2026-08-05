// The Swift CLI, growing beside the python one vein by vein: the strangler.
//
// The contract with the python side is one question and one promise. Asked
// `--carries`, this binary prints the veins it carries, one per line, each a
// prefix of an argv; the python side asks once and forwards any argv that
// starts with a carried vein, whole, by exec. So the list of what moved
// lives here alone, next to the code that answers for it, and the python
// side never grows a second copy of it. The promise: on a carried vein this
// binary answers with the same bytes the python CLI answers with, and the
// battery holds the two to each other on every run.
//
// bin/build-cli.sh builds it. The binary is not committed: every executable
// line in the repository stays text, and a clone without a Swift toolchain
// runs the python side of every vein, unchanged.
import Foundation

let root = URL(fileURLWithPath: CommandLine.arguments[0])
    .resolvingSymlinksInPath()
    .deletingLastPathComponent()   // bin/
    .deletingLastPathComponent()   // the clone
let args = Array(CommandLine.arguments.dropFirst())

func out(_ text: String) {
    FileHandle.standardOutput.write(Data(text.utf8))
}
func err(_ text: String) {
    FileHandle.standardError.write(Data(text.utf8))
}

// the non-answer, in the python side's own canon: a sentence and a step on
// stderr for a person, the object for whoever asked for one with `--json`.
// This binary printed the raw object either way, and the two sides then said
// the same thing in two shapes on the one argv where they both answer.
func cannot(_ note: String, _ then: String) -> Never {
    if args.contains("--json") {
        err("{" + jsonString("error") + ": " + jsonString(note) + ", "
            + jsonString("next") + ": " + jsonString(then) + "}\n")
    } else {
        err("gate: " + note + "\n  next: " + then + "\n")
    }
    exit(1)
}

// the veins, one argv prefix per line: the whole strangler ledger.
//
// A vein is a PREFIX, so a verb moves whole or not at all: claiming `stdlib`
// claims `stdlib materialize` with it. That is why this line grew from
// `stdlib show` to the verb: half a verb on the list would hand this binary an
// argv it does not answer, and the python side would never see it.
if args == ["--carries"] {
    out("stdlib\nexport\nseam\n")
    exit(0)
}

// ── the shelf, read the way the python side reads it: the files next to the
// CLI, sorted by name, each page whole ──
func shelf() -> [(name: String, text: String)] {
    let dir = root.appendingPathComponent("stdlib")
    let names = ((try? FileManager.default.contentsOfDirectory(atPath: dir.path)) ?? [])
        .filter { $0.hasSuffix(".swift") }.sorted()
    var out: [(String, String)] = []
    for file in names {
        let path = dir.appendingPathComponent(file).path
        guard let data = FileManager.default.contents(atPath: path),
              let text = String(data: data, encoding: .utf8) else { continue }
        out.append((String(file.dropLast(6)), text))
    }
    return out
}

// a `//`-line of the page's head, by its opening word: the same first four
// lines the python side reads for `role` and `speaks-for`
func head(_ text: String, _ label: String) -> String? {
    for line in text.components(separatedBy: "\n").prefix(4) {
        let l = line.trimmingCharacters(in: .whitespaces)
        if l.hasPrefix(label) { return String(l.dropFirst(label.count)).trimmingCharacters(in: .whitespaces) }
    }
    return nil
}

// python prints its answers with json.dumps(..., ensure_ascii=False, indent=2);
// these two write the same bytes for the shapes this verb returns
func jsonString(_ s: String) -> String {
    var out = "\""
    for ch in s.unicodeScalars {
        switch ch {
        case "\"": out += "\\\""
        case "\\": out += "\\\\"
        case "\n": out += "\\n"
        case "\t": out += "\\t"
        case "\r": out += "\\r"
        default:
            if ch.value < 0x20 { out += String(format: "\\u%04x", ch.value) } else { out.unicodeScalars.append(ch) }
        }
    }
    return out + "\""
}
func jsonObject(_ pairs: [(String, String)], indent: Int) -> String {
    let pad = String(repeating: " ", count: indent)
    let inner = String(repeating: " ", count: indent + 2)
    if pairs.isEmpty { return "{}" }
    return "{\n" + pairs.map { inner + jsonString($0.0) + ": " + jsonString($0.1) }
        .joined(separator: ",\n") + "\n" + pad + "}"
}

// ── the court, carried in-process: the judge sources at the pin beside
// bin/gate-judge (bin/gate-judge.from) are compiled into this binary by
// bin/build-cli.sh, and this door is the corpus's own Judge.run verbatim:
// plain, where, diff, chain. Not a python vein and not on the carries
// list, because the python side has no judge verb. What holds the road is
// the battery's parity against bin/gate-judge itself: byte for byte on
// the where pages, clock stripped on the plain court.
if args.first == "judge" {
    Judge.run(Array(args.dropFirst()))
    exit(0)
}

// ── stdlib show NAME: a shelf page, printed byte for byte ──
if args.count >= 2, args[0] == "stdlib", args[1] == "show" {
    guard args.count >= 3 else {
        // the naked `show` is answered in words here; the parity vector
        // walks named veins, and the python side still tracebacks on this
        cannot("stdlib show takes a module name", "`gate stdlib` lists them")
    }
    let name = args[2]
    let page = root.appendingPathComponent("stdlib").appendingPathComponent(name + ".swift")
    guard let data = FileManager.default.contents(atPath: page.path),
          let text = String(data: data, encoding: .utf8) else {
        cannot("no such stdlib module: \(name)", "`gate stdlib` lists them")
    }
    out(text)
    out("\n")   // python prints the page with print(), which ends it with one more newline
    exit(0)
}

// ── stdlib materialize NAME: the page put into the caller's directory, and
// the sentence that says it is a printout ──
if args.count >= 2, args[0] == "stdlib", args[1] == "materialize" {
    guard args.count >= 3 else {
        cannot("stdlib materialize takes a module name", "`gate stdlib` lists them")
    }
    let name = args[2]
    guard let page = shelf().first(where: { $0.name == name }) else {
        cannot("no such stdlib module: \(name)", "`gate stdlib` lists them")
    }
    let path = name + ".swift"
    do { try page.text.write(toFile: path, atomically: false, encoding: .utf8) } catch {
        cannot("could not write \(path)", "check the folder you are in is writable")
    }
    out(jsonObject([
        ("command", "stdlib materialize"),
        ("wrote", path),
        ("note", "a printout, not a source. These words are carried by the judge we ship: "
               + "the world uses them with this file absent, and editing this copy "
               + "adds no word to the language. It is here to be READ"),
        ("next", "gate --version names the revision they were compiled from. That, and "
               + "not this file, is the thing your world depends on"),
    ], indent: 0) + "\n")
    exit(0)
}

// ── stdlib, bare: the shelf as a list, in words or as the same answer ──
if args.first == "stdlib" {
    let pages = shelf()
    let modules = pages.map { ($0.name, $0.text.components(separatedBy: "\n")[0]
        .replacingOccurrences(of: "// ", with: "")) }
    let roles = pages.map { ($0.name, head($0.text, "// role:") ?? "") }
    let speaks = pages.map { ($0.name, head($0.text, "// speaks-for:") ?? "") }
    if args.contains("--json") {
        out("{\n  " + jsonString("command") + ": " + jsonString("stdlib") + ",\n"
            + "  " + jsonString("modules") + ": " + jsonObject(modules, indent: 2) + ",\n"
            + "  " + jsonString("roles") + ": " + jsonObject(roles, indent: 2) + ",\n"
            + "  " + jsonString("speaks") + ": " + jsonObject(speaks, indent: 2) + ",\n"
            + "  " + jsonString("note") + ": "
            + jsonString("printouts of what the judge already carries, not files your world is made of")
            + "\n}\n")
        exit(0)
    }
    let roleOf = Dictionary(uniqueKeysWithValues: roles)
    let speak = modules.filter { roleOf[$0.0] == "forms" }.count
    var lines = ["stdlib: \(speak) you can speak, \(modules.count - speak) gate's own, all of it theirs"]
    for (name, note) in modules {
        let own = roleOf[name] == "forms" ? "" : "   (gate's own furniture)"
        let said = note.components(separatedBy: ":").last!.trimmingCharacters(in: .whitespaces)
        let cut = String(said.prefix(52))
        lines.append("  " + name.padding(toLength: max(20, name.count), withPad: " ", startingAt: 0)
                     + " " + cut + own)
    }
    lines.append("  these are theirs: read them, quote them, learn them, but they are not "
                 + "files your world is made of, and editing one adds no word to the language. "
                 + "`gate --version` names the revision they were compiled from")
    lines.append("  next: `gate stdlib show <name>` reads one as plain Swift · "
                 + "`gate mine FILE` / `gate theirs FILE` is how a file joins your world")
    out(lines.joined(separator: "\n") + "\n")
    exit(0)
}

// ── export WORLD -o people.csv grants.csv: the tables printed back out of a
// world, which is the round trip that proves the fact translation ──
func matches(_ pattern: String, _ text: String,
             dotAll: Bool = false, lines: Bool = false) -> [[String]] {
    var opts: NSRegularExpression.Options = []
    if dotAll { opts.insert(.dotMatchesLineSeparators) }
    if lines { opts.insert(.anchorsMatchLines) }   // python's re.M
    guard let re = try? NSRegularExpression(pattern: pattern, options: opts) else { return [] }
    let ns = text as NSString
    return re.matches(in: text, range: NSRange(location: 0, length: ns.length)).map { m in
        (1..<m.numberOfRanges).map { i in
            m.range(at: i).location == NSNotFound ? "" : ns.substring(with: m.range(at: i))
        }
    }
}

if args.first == "export" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    // asked for nothing, the verb answers with a sentence: the python side has
    // one branch for every `asks` answer, which prints the note as a usage line
    // and the next step under it. The JSON keeps `asks` as a bare true.
    let note = "export prints the org tables back from a world, for the round-trip diff"
    let next = "gate export gate.swift -o people.csv grants.csv, then diff each "
             + "printed table against the original you imported"
    guard let first = rest.first, !first.hasPrefix("-"),
          let dash = rest.firstIndex(of: "-o"), dash + 2 < rest.count else {
        if args.contains("--json") {
            out("{\n  \"command\": \"export\",\n  \"asks\": true,\n"
                + "  \"note\": " + jsonString(note) + ",\n"
                + "  \"next\": " + jsonString(next) + "\n}\n")
        } else {
            out("usage: " + note + "\n  next: " + next + "\n")
        }
        exit(0)
    }
    let world = first
    let peopleOut = rest[dash + 1], grantsOut = rest[dash + 2]
    guard let data = FileManager.default.contents(atPath: world),
          let text = String(data: data, encoding: .utf8) else {
        err("gate-cli: no such world: \(world)\n")
        exit(1)
    }
    // the same three readings the python side makes, in the same order
    let sexPool = Dictionary(matches("public enum (\\w+): GivenNameCycle \\{.*?Sex = (\\w+)",
                                     text, dotAll: true).map { ($0[0], $0[1]) },
                             uniquingKeysWith: { a, _ in a })
    var rows: [[String]] = []
    let ns = text as NSString
    let personRe = try! NSRegularExpression(
        pattern: "public enum (\\w+): Employee, Person \\{(.*?)\\n\\}",
        options: [.dotMatchesLineSeparators])
    for m in personRe.matches(in: text, range: NSRange(location: 0, length: ns.length)) {
        let name = ns.substring(with: m.range(at: 1))
        let body = ns.substring(with: m.range(at: 2))
        var f: [String: String] = [:]
        for a in matches("public typealias (\\w+) = ([\\w.]+)", body) where f[a[0]] == nil {
            f[a[0]] = a[1]
        }
        // a record missing a column is a refusal with an address, the same
        // answer the python side gives: neither side meets a person with a
        // stack trace, so neither side is excluded from the parity
        let missing = ["Rank", "Home", "Given", "Family", "Born", "Site"].filter { f[$0] == nil }
        if !missing.isEmpty {
            let at = ns.substring(to: m.range.location).components(separatedBy: "\n").count
            let claim = "`\(name)` states no \(missing.joined(separator: " and no ")): "
                      + "the tables have a column for each, and a record that "
                      + "does not say one cannot be printed back"
            let next = "add the line to the record, or drop the record from the world"
            if args.contains("--json") {
                out("{\n  \"command\": \"export\",\n  \"verdict\": \"refused\",\n"
                    + "  \"refusals\": [\n    {\n      \"address\": "
                    + jsonString("\(world):\(at)") + ",\n      \"claim\": "
                    + jsonString(claim) + "\n    }\n  ],\n  \"next\": "
                    + jsonString(next) + "\n}\n")
            } else {
                out("export: refused 1\n  \(world):\(at) · \(claim)\n  next: \(next)\n")
            }
            exit(1)
        }
        let given = f["Given"] ?? ""
        rows.append([name, f["Rank"]!, f["Home"]!, given,
                     f["Family"]!, f["Born"]!, f["Site"]!, sexPool[given] ?? ""])
    }
    let grants = matches("VerifiedView<\\s*(\\w+),\\s*(\\w+)\\s*>\\.self;?", text)
    let people = "id,rank,home,given,family,born,site,sex\n"
        + rows.map { $0.joined(separator: ",") + "\n" }.joined()
    let grantRows = "who,doc\n" + grants.map { "\($0[0]),\($0[1])\n" }.joined()
    do {
        try people.write(toFile: peopleOut, atomically: false, encoding: .utf8)
        try grantRows.write(toFile: grantsOut, atomically: false, encoding: .utf8)
    } catch {
        err("gate-cli: could not write the tables\n")
        exit(1)
    }
    if args.contains("--json") {
        out("{\n  \"command\": \"export\",\n  \"people\": \(rows.count),\n"
            + "  \"grants\": \(grants.count),\n  \"wrote\": [\n"
            + "    " + jsonString(peopleOut) + ",\n    " + jsonString(grantsOut)
            + "\n  ]\n}\n")
    } else {
        out("export: \(rows.count) people, \(grants.count) grants → "
            + peopleOut + ", " + grantsOut + "\n")
    }
    exit(0)
}

// ── seam CONTRACT.swift CARRIER.swift: two declarations, one world, one court.
// The only place anything here refuses a PAIR, and it can only do so because
// both sides are present by their own word.
//
// THE COURT IS ASKED FOR ITS WORDS, IN A CHILD OF THIS PROCESS. Its sources are
// compiled in and `judge where` is the door forty lines up, but Judge.run prints
// its verdict and exits(1) on a refusal: a verb that needs the TEXT of a verdict
// cannot call it in process and still be there to read what came back. So this
// asks the door this binary already answers. One court call, the same count the
// python side makes to bin/gate-judge, and the court is still the one at this
// binary's own pin.
// AND ON THE PLATFORM WHERE IT WAS MEASURED IT IS SPAWNED BY HAND, BECAUSE THE
// ONE IN THE BOX COSTS SIXTY MILLISECONDS. Foundation's `Process` was measured
// at 71 ms a call against 10 for the posix_spawn below, on a court that answers
// in 4: three rounds, byte-identical output, and a Pipe swapped for a temp file
// made no difference, so the cost is the wrapper. The verb the demo offers says
// "the court over the pair, in ms", and a wrapper costing fifteen courts is that
// sentence, not a detail.
//
// The split is by what could be MEASURED, not by taste. `posix_spawn_file_
// actions_t` is a pointer on Darwin and a struct on Linux, `environ` is exported
// on one and argued about on the other, and there is no Linux on this machine to
// answer either question: a portable hand spawn here would be a guess, and one
// went red on the linux job already. So the wrapper stays the road everywhere it
// has not been measured. Both roads are held to the python side's bytes by the
// parity walk, which runs wherever a toolchain stands, so neither can drift.
func courtSays(_ path: String) -> String {
    let bin = URL(fileURLWithPath: CommandLine.arguments[0]).resolvingSymlinksInPath().path
    let words: [String] = [bin, "judge", "where", path]
#if canImport(Darwin)
    var fds: [Int32] = [0, 0]
    guard pipe(&fds) == 0 else { return "" }
    var actions: posix_spawn_file_actions_t?
    posix_spawn_file_actions_init(&actions)
    posix_spawn_file_actions_adddup2(&actions, fds[1], 1)
    posix_spawn_file_actions_addclose(&actions, fds[0])
    var argv: [UnsafeMutablePointer<CChar>?] = words.map { strdup($0) }
    argv.append(nil)
    var child: pid_t = 0
    let started = posix_spawn(&child, bin, &actions, nil, &argv, environ)
    posix_spawn_file_actions_destroy(&actions)
    for word in argv where word != nil { free(word) }
    close(fds[1])
    // read to the end BEFORE waiting: a court with more to say than the pipe
    // holds would block on the write while this waited on the exit
    var said = Data()
    var chunk = [UInt8](repeating: 0, count: 8192)
    while true {
        let got = read(fds[0], &chunk, chunk.count)
        if got <= 0 { break }
        said.append(contentsOf: chunk[0..<got])
    }
    close(fds[0])
    guard started == 0 else { return "" }
    var status: Int32 = 0
    waitpid(child, &status, 0)
    return String(data: said, encoding: .utf8) ?? ""
#else
    let p = Process()
    p.executableURL = URL(fileURLWithPath: bin)
    p.arguments = Array(words.dropFirst())
    let pipe = Pipe()
    p.standardOutput = pipe
    guard (try? p.run()) != nil else { return "" }
    let said = String(data: pipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
    p.waitUntilExit()
    return said
#endif
}

if args.first == "seam" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    let note = "seam CONTRACT.swift CARRIER.swift  both sides, as each declared them"
    let nextAsked = "gate declare contract … and gate declare carrier … first"
    guard rest.count >= 2 else {
        if asJson {
            out("{\n  \"command\": \"seam\",\n  \"asks\": true,\n"
                + "  \"note\": " + jsonString(note) + ",\n"
                + "  \"next\": " + jsonString(nextAsked) + "\n}\n")
        } else {
            out("usage: " + note + "\n  next: " + nextAsked + "\n")
        }
        exit(0)
    }
    // a path that is not there is answered in one sentence here; the python side
    // still raises, the way `stdlib show` with no name does. Named cases are the
    // parity, and neither side meets a person with a stack trace on one.
    var side: [String] = []
    for p in rest.prefix(2) {
        guard let data = FileManager.default.contents(atPath: p),
              let text = String(data: data, encoding: .utf8) else {
            err("gate-cli: no such side: \(p)\n")
            exit(1)
        }
        side.append(text)
    }
    let left = side[0], right = side[1]
    let who = matches("public enum (\\w+): Carrier", right).first?[0] ?? "that library"
    // what the carrier claims, keyed by the certificate that carries the claim:
    // the route, the contract's word for the field, and the carrier's own word
    // for it when the two differ
    var claims: [String: (route: String, field: String, mine: String)] = [:]
    for m in matches("^// (\\S+) · (\\S+)(?: \\(it calls it (\\S+)\\))?\\npublic typealias (Carry_\\d+)",
                     right, lines: true) {
        claims[m[3]] = (m[0], m[1], m[2])
    }
    let dir = NSTemporaryDirectory() + "gate-seam-\(ProcessInfo.processInfo.processIdentifier)"
    try? FileManager.default.createDirectory(atPath: dir, withIntermediateDirectories: true)
    let path = dir + "/seam.swift"
    guard (try? (left + "\n" + right).write(toFile: path, atomically: false, encoding: .utf8)) != nil else {
        err("gate-cli: could not write the joined world\n")
        exit(1)
    }
    let started = Date()
    let said = courtSays(path)
    let ms = (Date().timeIntervalSince(started) * 10_000).rounded() / 10
    try? FileManager.default.removeItem(atPath: dir)
    var refusals: [(address: String, claim: String)] = []
    for m in matches("^✗ '(\\w+)[^']*' requires the types '[^']*' \\(aka '([^']+)'\\) and "
                     + "'[^']*' \\(aka '([^']+)'\\)", said, lines: true) {
        let it = claims[m[0]] ?? (route: "?", field: m[0], mine: "")
        refusals.append((address: "\(it.route) · \(it.field)",
                         claim: "the contract declares it \(m[1].lowercased()); \(who) declares "
                              + (it.mine.isEmpty ? "it " : "its own \(it.mine) as ")
                              + m[2].lowercased()))
    }
    // a field the contract declares and no carrier claims: not a disagreement,
    // since a claim never made cannot be refused, so it is named beside the verdict
    let claimed = Set(claims.values.map { $0.route + "\u{1}" + $0.field })
    var silent: [String] = []
    for m in matches("^// (\\S+) · (\\S+)$", left, lines: true)
    where !claimed.contains(m[0] + "\u{1}" + m[1]) {
        silent.append(m[0] + " · " + m[1])
    }
    var told = "\(claims.count) claims judged"
    if !silent.isEmpty {
        told += "; \(silent.count) field\(silent.count != 1 ? "s" : "") the contract declares "
              + (silent.count != 1 ? "are" : "is")
              + " claimed by nobody: a claim never made cannot be refused, so it stands "
              + "beside the judgement"
    }
    let nextSaid = refusals.isEmpty
        ? "wire it into CI: neither side can move without the other seeing"
        : "open the address above: two declarations, both signed, do not agree"
    let clock = String(format: "%.1f", ms)
    if asJson {
        var text = "{\n  \"command\": \"seam\",\n  \"verdict\": "
                 + jsonString(refusals.isEmpty ? "holds" : "refused") + ",\n  \"refusals\": "
        if refusals.isEmpty {
            text += "[]"
        } else {
            var each: [String] = []
            for r in refusals {
                var one = "    {\n      \"address\": "
                one += jsonString(r.address)
                one += ",\n      \"claim\": "
                one += jsonString(r.claim)
                one += "\n    }"
                each.append(one)
            }
            text += "[\n" + each.joined(separator: ",\n") + "\n  ]"
        }
        text += ",\n  \"judged\": \(claims.count),\n  \"unclaimed\": "
        if silent.isEmpty {
            text += "[]"
        } else {
            text += "[\n" + silent.map { "    " + jsonString($0) }.joined(separator: ",\n") + "\n  ]"
        }
        text += ",\n  \"judge_ms\": \(clock),\n  \"carrier\": "
        text += jsonString(who)
        text += ",\n  \"note\": "
        text += jsonString(told)
        text += ",\n  \"next\": "
        text += jsonString(nextSaid)
        text += ",\n  \"mutates\": false\n}\n"
        out(text)
    } else {
        var lines = ["seam: " + (refusals.isEmpty ? "holds" : "refused \(refusals.count)")
                     + " · \(clock) ms"]
        for r in refusals { lines.append("  \(r.address) · \(r.claim)") }
        lines.append("  note: " + told)
        lines.append("  next: " + nextSaid)
        out(lines.joined(separator: "\n") + "\n")
    }
    exit(refusals.isEmpty ? 0 : 1)
}

// an argv this binary never claimed: refuse loudly rather than guess. The
// python side forwards carried veins alone, so reaching here is a defect.
err("gate-cli: uncarried argv: " + args.joined(separator: " ") + "\n")
exit(66)
