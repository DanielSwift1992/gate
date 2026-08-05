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

// the veins, one argv prefix per line: the whole strangler ledger.
//
// A vein is a PREFIX, so a verb moves whole or not at all: claiming `stdlib`
// claims `stdlib materialize` with it. That is why this line grew from
// `stdlib show` to the verb: half a verb on the list would hand this binary an
// argv it does not answer, and the python side would never see it.
if args == ["--carries"] {
    out("stdlib\nexport\n")
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
        err("{\"error\": \"stdlib show takes a module name (gate stdlib lists them)\"}\n")
        exit(1)
    }
    let name = args[2]
    let page = root.appendingPathComponent("stdlib").appendingPathComponent(name + ".swift")
    guard let data = FileManager.default.contents(atPath: page.path),
          let text = String(data: data, encoding: .utf8) else {
        err("{\"error\": \"no such stdlib module: \(name) (gate stdlib lists them)\"}\n")
        exit(1)
    }
    out(text)
    out("\n")   // python prints the page with print(), which ends it with one more newline
    exit(0)
}

// ── stdlib materialize NAME: the page put into the caller's directory, and
// the sentence that says it is a printout ──
if args.count >= 2, args[0] == "stdlib", args[1] == "materialize" {
    guard args.count >= 3 else {
        err("{\"error\": \"stdlib materialize takes a module name (gate stdlib lists them)\"}\n")
        exit(1)
    }
    let name = args[2]
    guard let page = shelf().first(where: { $0.name == name }) else {
        err("{\"error\": \"no such stdlib module: \(name)\"}\n")
        exit(1)
    }
    let path = name + ".swift"
    do { try page.text.write(toFile: path, atomically: false, encoding: .utf8) } catch {
        err("{\"error\": \"could not write \(path)\"}\n")
        exit(1)
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
func matches(_ pattern: String, _ text: String, dotAll: Bool = false) -> [[String]] {
    var opts: NSRegularExpression.Options = []
    if dotAll { opts.insert(.dotMatchesLineSeparators) }
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
    for m in matches("public enum (\\w+): Employee, Person \\{(.*?)\\n\\}", text, dotAll: true) {
        var f: [String: String] = [:]
        for a in matches("public typealias (\\w+) = ([\\w.]+)", m[1]) where f[a[0]] == nil {
            f[a[0]] = a[1]
        }
        let given = f["Given"] ?? ""
        rows.append([m[0], f["Rank"] ?? "", f["Home"] ?? "", given,
                     f["Family"] ?? "", f["Born"] ?? "", f["Site"] ?? "", sexPool[given] ?? ""])
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

// an argv this binary never claimed: refuse loudly rather than guess. The
// python side forwards carried veins alone, so reaching here is a defect.
err("gate-cli: uncarried argv: " + args.joined(separator: " ") + "\n")
exit(66)
