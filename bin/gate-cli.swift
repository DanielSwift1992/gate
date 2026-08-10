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

// the world being founded right now, if any: set by entry for the length of
// its own writes, so the row walk does not climb past a root being born.
// Declared here because top-level order is execution order, and the walk is
// called from verbs that stand above the entry section in this file.
var FOUNDING: String? = nil

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
// ── ONE IS NOT MANY, AND THE NOUN CARRIES IT. The python side prints every
// count through its own `many`, and this vein carries three of them: a verb
// that says `1 people` on one carrier and `1 person` on the other is not the
// same verb, and the battery holds these two byte for byte.
func many(_ n: Int, _ one: String, _ more: String? = nil) -> String {
    return "\(n) " + (n == 1 ? one : (more ?? one + "s"))
}

func cannot(_ note: String, _ then: String) -> Never {
    if args.contains("--json") {
        err("{" + jsonString("error") + ": " + jsonString(note) + ", "
            + jsonString("next") + ": " + jsonString(then) + "}\n")
    } else {
        err("gate: " + note + "\n  next: " + then + "\n")
    }
    exit(1)
}

// ── AND THE FLAG THIS TOOL DOES NOT READ IS SAID HERE TOO. Every verb writes
// with `-o`; `--out` is the guess anybody makes, and swallowing it wrote nothing
// and said nothing. The python side refuses it in `main`, before any verb reads
// its argv, and the verbs this vein carries never reach that line.
if args.contains("--out") && !args.contains("-o") {
    cannot("this tool writes with `-o`, and `--out` is not a flag it reads",
           "spell it `-o PATH`, the way the usage line for every writing verb does")
}

// the veins, one argv prefix per line: the whole strangler ledger.
//
// A vein is a PREFIX, so a verb moves whole or not at all: claiming `stdlib`
// claims `stdlib materialize` with it. That is why this line grew from
// `stdlib show` to the verb: half a verb on the list would hand this binary an
// argv it does not answer, and the python side would never see it.
if args == ["--carries"] {
    out("stdlib\nexport\nseam\nlog\naside\ndeclare\nmine\ntheirs\ninit\ndrift\nmy\n"
        + "status\nfsck\nbadge\n")
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
    let asked = args.filter { $0 != "--json" }
    guard asked.count >= 3 else {
        // the naked `show` is answered in words here; the parity vector
        // walks named veins, and the python side still tracebacks on this
        cannot("stdlib show takes a module name", "`gate stdlib` lists them")
    }
    let name = asked[2]
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
    let asked = args.filter { $0 != "--json" }
    guard asked.count >= 3 else {
        cannot("stdlib materialize takes a module name", "`gate stdlib` lists them")
    }
    let name = asked[2]
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

// ── THE WORLD, READ THE WAY THE PYTHON SIDE READS IT. Every verb still on the
// other side of the strangler needs three things this vein did not have: a way
// to run git, the layout the manifest declares, and which of those rows the
// courts read. The three carried verbs took their files from argv and needed
// none of it. This is the first stretch of that road, written for `log` and
// shaped for the verbs behind it.
//
// The manifest is read by the same targeted patterns the python side uses, not
// by a second grammar: a row is a declaration with a `Kind` axis and a
// `typeName` literal, and both sides read exactly those.
func runGit(_ arguments: [String], _ cwd: String) -> String {
    let p = Process()
    p.executableURL = URL(fileURLWithPath: "/usr/bin/env")
    p.arguments = ["git"] + arguments
    p.currentDirectoryURL = URL(fileURLWithPath: cwd)
    let pipe = Pipe(), quiet = Pipe()
    p.standardOutput = pipe
    p.standardError = quiet
    do { try p.run() } catch { return "" }
    let said = pipe.fileHandleForReading.readDataToEndOfFile()
    quiet.fileHandleForReading.readDataToEndOfFile()
    p.waitUntilExit()
    return String(data: said, encoding: .utf8) ?? ""
}

func theirsText(_ path: String, _ what: String) -> String {
    // ── THE ONE DOOR, ON THIS SIDE TOO. A file that is not there and a file that
    // is not text are two different sentences, and this vein said the first one
    // for both: `no such side` about a file sitting right there, while the other
    // carrier named the byte. Two carriers, one verb, two stories.
    guard let data = FileManager.default.contents(atPath: path) else {
        cannot("no such file: " + path, "point it at " + what)
    }
    if let text = String(data: data, encoding: .utf8) { return text }
    // the first byte that is not utf-8, counted the way the other side counts it
    let bytes = [UInt8](data)
    var i = 0
    while i < bytes.count {
        let b = bytes[i]
        var width = 0
        if b < 0x80 { width = 1 }
        else if b >= 0xC2 && b <= 0xDF { width = 2 }
        else if b >= 0xE0 && b <= 0xEF { width = 3 }
        else if b >= 0xF0 && b <= 0xF4 { width = 4 }
        else { break }
        if i + width > bytes.count { break }
        var ok = true
        for k in 1..<max(width, 1) where bytes[i + k] < 0x80 || bytes[i + k] > 0xBF { ok = false }
        if !ok { break }
        i += width
    }
    let said = String(format: "%#04x", Int(bytes[min(i, bytes.count - 1)]))
    cannot(path + " is not text this can read: byte " + said + " at offset \(i) is not utf-8",
           "point it at a text file. If it is text in another encoding, "
           + "`iconv -f <encoding> -t utf-8` writes the one this reads")
}

func uncommented(_ text: String) -> String {
    // a `//` inside a string literal is not a comment, which is why this walks
    // rather than greps: the python side learned that on a typeName holding a URL
    var out = "", inString = false
    var i = text.startIndex
    while i < text.endIndex {
        let c = text[i]
        if c == "\"" { inString.toggle(); out.append(c); i = text.index(after: i); continue }
        if !inString, c == "/", text.index(after: i) < text.endIndex,
           text[text.index(after: i)] == "/" {
            while i < text.endIndex, text[i] != "\n" { i = text.index(after: i) }
            continue
        }
        out.append(c)
        i = text.index(after: i)
    }
    return out
}

struct WorldRow { let path: String; let role: String }

func manifestRows(_ dir: String) -> (rows: [WorldRow], manifest: String?) {
    let mp = (dir as NSString).appendingPathComponent("gate.manifest.swift")
    guard let text = try? String(contentsOfFile: mp, encoding: .utf8) else { return ([], nil) }
    let code = uncommented(text)
    var literal: [String: String] = [:]
    for m in matches("extension (\\w+)\\b[^{]*\\{(.*?)\\n(?=public |extension |\\Z)",
                     code + "\n", dotAll: true) where m.count == 2 {
        let found = matches("typeName:\\s*String\\s*\\{\\s*\"([^\"]*)\"\\s*\\}", m[1])
        if let first = found.first, first.count == 1 { literal[m[0]] = first[0] }
    }
    // ── AND EACH ROW IS READ AT ITS OWN NAME. One pattern over the whole
    // document, with the dot matching newlines, let the FIRST declaration in the
    // file swallow the second: `public enum WorldFile: Role {}` is written on one
    // line, so a body search from there ran to the next `\n}`, which belonged to
    // the row after it. The python side never had that hole because it finds the
    // heads first and then asks for each body BY NAME; this does the same, and
    // the row it was losing is the first row of this repository's own layout.
    var rows: [WorldRow] = []
    for m in matches("public enum (\\w+): (Mine|Theirs|WorldFile|SeamFile) \\{", code)
    where m.count == 2 {
        guard let path = literal[m[0]], !path.isEmpty else { continue }
        let body = matches("public enum " + m[0] + "\\b[^{]*\\{(.*?)\\n\\}",
                           code + "\n", dotAll: true).first?.first ?? ""
        let kind = matches("typealias\\s+Kind\\s*=\\s*(\\w+)", body).first?.first ?? ""
        let role: String
        switch kind {
        case "WorldFile": role = "world"
        case "SeamFile": role = "seam"
        case "FormsFile": role = "forms"
        case "JudgeFile": role = "judge"
        case "CarriedFile": role = "carried"
        case "ToolFile": role = "tool"
        case "Seam": role = "seam"
        default:
            // no Kind axis: the older spellings said it in the atom itself
            role = kind.isEmpty ? (m[1] == "WorldFile" ? "world"
                                   : m[1] == "SeamFile" ? "seam" : "")
                                : kind.lowercased()
        }
        if !role.isEmpty { rows.append(WorldRow(path: path, role: role)) }
    }
    return (rows, mp)
}

// ── AND THE TWO FACTS A JOURNAL READS BESIDE GIT. An email is not a person:
// `tables/identities.csv` binds the two where a world keeps one, and a journal
// that skipped it printed addresses where the other side printed names. And a
// wheel the operator turned is a declaration like any other: `MyJournal` says
// what you get when you type no word at all, read from the world's own files
// and from your personal one. A verb moves whole or not at all, so both travel.
func commandIn(_ said: String) -> String? {
    // ── THE LAST MILE, ON THIS SIDE TOO. Every answer ends with a step naming a
    // command in backticks, and the python side lifts that command out beside
    // the sentence so nobody retypes it. An answer carried by this vein that
    // dropped the field would be the same verb saying less on one carrier.
    guard let m = matches("`([^`]+)`", said).first?.first else { return nil }
    let ready = m.trimmingCharacters(in: .whitespaces)
    let starts = ["gate", "git", "bin/", "yq", "swift"]
    return starts.contains(where: { ready.hasPrefix($0) }) ? ready : nil
}

func sha1Prefix(_ text: String) -> String {
    // ── SHA-1, WRITTEN OUT, because the alternative is a platform library on one
    // side of a binary that has to build on the other. Eight hex digits of it name
    // a personal world for a clone with no remote, which is the one place this
    // tool hashes anything at all.
    var h: [UInt32] = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]
    var message = Array(text.utf8)
    let bitCount = UInt64(message.count) * 8
    message.append(0x80)
    while message.count % 64 != 56 { message.append(0) }
    for i in (0..<8).reversed() { message.append(UInt8((bitCount >> (UInt64(i) * 8)) & 0xFF)) }
    for chunk in stride(from: 0, to: message.count, by: 64) {
        var w = [UInt32](repeating: 0, count: 80)
        for i in 0..<16 {
            let o = chunk + i * 4
            w[i] = (UInt32(message[o]) << 24) | (UInt32(message[o + 1]) << 16)
                 | (UInt32(message[o + 2]) << 8) | UInt32(message[o + 3])
        }
        for i in 16..<80 {
            let x = w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16]
            w[i] = (x << 1) | (x >> 31)
        }
        var a = h[0], b = h[1], c = h[2], d = h[3], e = h[4]
        for i in 0..<80 {
            var f: UInt32 = 0, k: UInt32 = 0
            switch i {
            case 0..<20:  f = (b & c) | (~b & d);          k = 0x5A827999
            case 20..<40: f = b ^ c ^ d;                   k = 0x6ED9EBA1
            case 40..<60: f = (b & c) | (b & d) | (c & d); k = 0x8F1BBCDC
            default:      f = b ^ c ^ d;                   k = 0xCA62C1D6
            }
            let t = ((a << 5) | (a >> 27)) &+ f &+ e &+ k &+ w[i]
            e = d; d = c; c = (b << 30) | (b >> 2); b = a; a = t
        }
        h[0] = h[0] &+ a; h[1] = h[1] &+ b; h[2] = h[2] &+ c
        h[3] = h[3] &+ d; h[4] = h[4] &+ e
    }
    return h.map { String(format: "%08x", $0) }.joined().prefix(8).description
}

func identities(_ base: String) -> [String: String] {
    let path = (base as NSString).appendingPathComponent("tables/identities.csv")
    guard let text = try? String(contentsOfFile: path, encoding: .utf8) else { return [:] }
    var rows = text.components(separatedBy: "\n").filter { !$0.trimmingCharacters(in: .whitespaces).isEmpty }
    guard !rows.isEmpty else { return [:] }
    let head = rows.removeFirst().components(separatedBy: ",").map {
        $0.trimmingCharacters(in: .whitespaces) }
    guard let mail = head.firstIndex(of: "email"), let who = head.firstIndex(of: "id") else { return [:] }
    var out: [String: String] = [:]
    for row in rows {
        let cells = row.components(separatedBy: ",")
        if cells.count > max(mail, who) { out[cells[mail]] = cells[who] }
    }
    return out
}

func repoKey(_ base: String) -> String {
    let url = runGit(["config", "--get", "remote.origin.url"], base)
        .trimmingCharacters(in: .whitespacesAndNewlines)
    if !url.isEmpty {
        var k = url
        for pattern in ["^[a-zA-Z+]+://", "^[^@/]+@", "\\.git$"] {
            k = k.replacingOccurrences(of: pattern, with: "", options: .regularExpression)
        }
        k = k.replacingOccurrences(of: ":", with: "/")
        k = k.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        return k.replacingOccurrences(of: "[^A-Za-z0-9._-]", with: "_", options: .regularExpression)
    }
    let top = runGit(["rev-parse", "--show-toplevel"], base)
        .trimmingCharacters(in: .whitespacesAndNewlines)
    let home = top.isEmpty ? base : top
    let name = (home as NSString).lastPathComponent
        .replacingOccurrences(of: "[^A-Za-z0-9._-]", with: "_", options: .regularExpression)
    return name + "-" + sha1Prefix(home)
}

func turned(_ surface: String, _ base: String, _ files: [String]) -> [String: String] {
    var out: [String: String] = [:]
    for path in files {
        guard let raw = try? String(contentsOfFile: path, encoding: .utf8) else { continue }
        // a comment is not a declaration: the shelf documents this very wheel by
        // showing one, and reading the example as an answer made `gate log` obey
        // a line written to explain it
        let text = raw.components(separatedBy: "\n")
            .filter { !$0.trimmingCharacters(in: .whitespaces).hasPrefix("//") }
            .joined(separator: "\n")
        for m in matches("public enum \\w+: " + surface + " \\{(.*?)\\n\\}", text, dotAll: true)
        where m.count == 1 {
            for a in matches("public typealias (\\w+) = (\\w+)", m[0]) where a.count == 2 {
                out[a[0]] = a[1]
            }
        }
    }
    return out
}

// ── JSON, READ WITH ITS ORDER KEPT. Foundation's reader hands back a
// dictionary, and a dictionary has no order: a file rewritten through it comes
// out with its keys shuffled, which is a diff nobody can read and a review
// nobody can do. The other carrier keeps whatever order the file had, because
// python's own reader does. So this one does too: an object is a list of pairs,
// and a number keeps the text it was written as, so what goes back out is what
// came in unless something meant to change it.
indirect enum Said {
    case text(String), number(String), yes, no, nothing
    case list([Said])
    case object([(String, Said)])

    var asText: String? { if case .text(let s) = self { return s }; return nil }
    var asList: [Said]? { if case .list(let l) = self { return l }; return nil }
    var asObject: [(String, Said)]? { if case .object(let o) = self { return o }; return nil }
    func at(_ key: String) -> Said? { asObject?.first(where: { $0.0 == key })?.1 }
}

func readSaid(_ text: String) -> Said? {
    var chars = Array(text.unicodeScalars)
    var i = 0

    func skip() { while i < chars.count, chars[i] == " " || chars[i] == "\n"
                        || chars[i] == "\t" || chars[i] == "\r" { i += 1 } }

    func string() -> String? {
        guard i < chars.count, chars[i] == "\"" else { return nil }
        i += 1
        var out = ""
        while i < chars.count {
            let c = chars[i]
            if c == "\\" , i + 1 < chars.count {
                let e = chars[i + 1]
                i += 2
                switch e {
                case "n": out.append("\n")
                case "t": out.append("\t")
                case "r": out.append("\r")
                case "b": out.append("\u{08}")
                case "f": out.append("\u{0C}")
                case "u":
                    let hex = String(String.UnicodeScalarView(chars[i..<min(i + 4, chars.count)]))
                    i += 4
                    if let n = UInt32(hex, radix: 16), let scalar = Unicode.Scalar(n) {
                        out.unicodeScalars.append(scalar)
                    }
                default: out.unicodeScalars.append(e)
                }
                continue
            }
            if c == "\"" { i += 1; return out }
            out.unicodeScalars.append(c)
            i += 1
        }
        return nil
    }

    func value() -> Said? {
        skip()
        guard i < chars.count else { return nil }
        switch chars[i] {
        case "\"":
            return string().map { Said.text($0) }
        case "{":
            i += 1
            var pairs: [(String, Said)] = []
            skip()
            if i < chars.count, chars[i] == "}" { i += 1; return .object(pairs) }
            while i < chars.count {
                skip()
                guard let k = string() else { return nil }
                skip()
                guard i < chars.count, chars[i] == ":" else { return nil }
                i += 1
                guard let v = value() else { return nil }
                pairs.append((k, v))
                skip()
                if i < chars.count, chars[i] == "," { i += 1; continue }
                if i < chars.count, chars[i] == "}" { i += 1; return .object(pairs) }
                return nil
            }
            return nil
        case "[":
            i += 1
            var items: [Said] = []
            skip()
            if i < chars.count, chars[i] == "]" { i += 1; return .list(items) }
            while i < chars.count {
                guard let v = value() else { return nil }
                items.append(v)
                skip()
                if i < chars.count, chars[i] == "," { i += 1; continue }
                if i < chars.count, chars[i] == "]" { i += 1; return .list(items) }
                return nil
            }
            return nil
        case "t", "f", "n":
            // the literal is spelled out or it is not a literal: `not json at
            // all` begins with an n, and a reader that took the first letter
            // for `null` said a document was empty where the other carrier said
            // it was not JSON at all
            for (word, said) in [("true", Said.yes), ("false", .no), ("null", .nothing)] {
                let end = i + word.count
                if end <= chars.count,
                   String(String.UnicodeScalarView(chars[i..<end])) == word {
                    i = end
                    return said
                }
            }
            return nil
        default:
            var raw = ""
            while i < chars.count, "0123456789+-.eE".unicodeScalars.contains(chars[i]) {
                raw.unicodeScalars.append(chars[i]); i += 1
            }
            return raw.isEmpty ? nil : .number(raw)
        }
    }
    let said = value()
    skip()
    // and nothing may follow it: a document with a tail is not this document
    return i >= chars.count ? said : nil
}

func jsonPlace(_ text: String) -> (line: Int, column: Int) {
    // where the other carrier's reader stops, said its way: a line and a column,
    // both counted from one. For a document that is not JSON at all this is the
    // first character, which is what its message names.
    return (1, 1)
}

// ── WRITING A ROW INTO A LAYOUT, which is what `declare`, `init`, `mine` and
// `theirs` all do and none of them can do without. The reading side landed with
// `log`; this is the writing side, and it obeys the same two laws: a record's
// boundary comes from the file (kind 14), and the bytes of somebody else's file
// outside your own line do not change (kind 12).
let ROLE_ATOM: [String: String] = ["world": "WorldFile", "seam": "SeamFile",
                                   "forms": "FormsFile", "judge": "JudgeFile",
                                   "carried": "CarriedFile", "tool": "ToolFile"]

func sanitized(_ s: String) -> String {
    return s.replacingOccurrences(of: "[^A-Za-z0-9]", with: "_", options: .regularExpression)
}

func rowAtom(_ rel: String) -> String {
    // the other carrier's `row_atom`: the path without its extension, sanitised,
    // title-cased, and its separators dropped
    let stem = (rel as NSString).deletingPathExtension
    let said = sanitized(stem)
    let titled = said.split(separator: "_", omittingEmptySubsequences: false)
        .map { $0.isEmpty ? "" : $0.prefix(1).uppercased() + $0.dropFirst().lowercased() }
        .joined()
    let out = titled.replacingOccurrences(of: "/", with: "")
    return out.isEmpty ? "Side" : out
}

func worldRootFor(_ path: String) -> String {
    // the world a file belongs to is found the way .git is: walking up from the
    // FILE, never from wherever the command happened to be typed. The walk goes
    // from the file's absolute place, because a relative path with a folder in
    // it walked from the folder's own name and founded a world inside it; and
    // nothing here standardizes, because that strips /private from a path that
    // exists and leaves it on one that does not, and the row's relative path is
    // computed against this root by plain string arithmetic.
    // a world being founded right here stops the walk: entry writes DIR's
    // first files, and the walk up from the first one must not put its rows
    // into a world standing overhead
    if let f = FOUNDING,
       relPath(absPath(path), f).components(separatedBy: "/").first != ".." {
        return f
    }
    var walk = (absPath(path) as NSString).deletingLastPathComponent
    while true {
        for name in ["gate.swift", "gate.manifest.swift"] {
            if FileManager.default.fileExists(atPath: (walk as NSString).appendingPathComponent(name)) {
                return walk
            }
        }
        let up = (walk as NSString).deletingLastPathComponent
        if up == walk || up.isEmpty { break }
        walk = up
    }
    // ── AND THE FALLBACK IS NOT «WHEREVER I AM STANDING». Falling back to the
    // working directory wrote rows into THIS repository's own layout naming
    // temp folders: claims about directories deleted the same minute, which is
    // the exact defect the guard downstream names. The other carrier falls back
    // to the working directory only when the file is UNDER it, and to the
    // file's own folder otherwise.
    let here = FileManager.default.currentDirectoryPath
    let standing = (absPath(path) as NSString).deletingLastPathComponent
    return relPath(standing, here).components(separatedBy: "/").first == ".."
        ? standing : here
}

func shelfPage(_ name: String) -> String {
    for page in shelf() where page.name == name { return page.text }
    cannot("the shelf page this writes from is missing: stdlib/" + name + ".swift",
           "restore the file, or run this where the tool's own stdlib/ is beside it")
}

func shelfSection(_ name: String, _ mark: String) -> String {
    // a page may carry more than one text, and each says where it begins: a
    // section runs from its own mark to the next, and a mark is a line the page
    // shows a reader. Nothing here counts lines.
    let said = shelfPage(name)
    guard let cut = said.range(of: mark) else {
        cannot("the shelf page " + name + " does not carry the section this writes",
               "restore stdlib/" + name + ".swift")
    }
    let rest = String(said[cut.upperBound...])
    if let next = matchRange(rest, "^// ── .+ ──$") { return String(rest[..<next.lowerBound]) }
    return rest
}

func matchRange(_ text: String, _ pattern: String) -> Range<String.Index>? {
    guard let re = try? NSRegularExpression(pattern: pattern, options: [.anchorsMatchLines])
    else { return nil }
    let ns = text as NSString
    guard let m = re.firstMatch(in: text, range: NSRange(location: 0, length: ns.length))
    else { return nil }
    return Range(m.range, in: text)
}

func manifestHead() -> String {
    // one home for the text, read from the same page the other carrier reads
    let mark = "// ── what is written into a world begins here ──\n"
    for page in shelf() where page.name == "manifest" {
        if let cut = page.text.range(of: mark) {
            return String(page.text[cut.upperBound...])
        }
    }
    cannot("the shelf page a layout is born from is missing: stdlib/manifest.swift",
           "restore the file, or run this where the tool's own stdlib/ is beside it")
}

func upsertRow(_ text: String, name: String, rel: String, kind: String, role: String,
               from: String? = nil, written: String? = nil, opens: String? = nil) -> String {
    var said = text
    func ensure(_ line: String) {
        if !said.contains(line) {
            said = said.replacingOccurrences(of: "\n+$", with: "\n",
                                             options: .regularExpression) + line + "\n"
        }
    }
    guard let atom = ROLE_ATOM[role] else {
        cannot("no such role: " + role, "a row says which court reads it: world, seam or forms")
    }
    if !said.contains("public enum " + atom + ": Role {}") {
        ensure("public enum " + atom + ": Role {}")
    }
    if let opens = opens {
        if !said.contains("public protocol View {}") { ensure("public protocol View {}") }
        if !said.contains("public enum " + opens + ": View {}") {
            ensure("public enum " + opens + ": View {}")
        }
    }
    if kind == "Mine", !said.contains("public protocol Mine {}") {
        ensure("\npublic protocol Mine {}")
    }
    if kind == "Theirs", !said.contains("public protocol Theirs {}") {
        // the fourth text a layout carries, off the same page as its head
        said += shelfSection("manifest",
                             "// ── what a world says when it first takes something begins here ──\n")
    }
    var rev = ""
    var revAtom = ""
    if let from = from {
        revAtom = "Rev_" + sanitized(from).trimmingCharacters(in: CharacterSet(charactersIn: "_"))
        if !said.contains("public enum " + revAtom + " {}") {
            rev = "public enum " + revAtom + " {}\n"
                + "extension " + revAtom + " { public static var typeName: String { \""
                + from + "\" } }\n"
        }
    }
    var line = rev + "public enum " + name + ": " + kind + " {\n"
    line += "    public typealias Kind = " + atom + "\n"
    if from != nil { line += "    public typealias At = " + revAtom + "\n" }
    if let written = written { line += "    public typealias Written = " + written + "\n" }
    if let opens = opens { line += "    public typealias Opens = " + opens + "\n" }
    line += "}\n"
    line += "extension " + name + " { public static var typeName: String { \"" + rel + "\" } }\n"
    if said.contains(line) { return said }
    // kept in its own group, because this document is read by a person: what I
    // write and what I only read are the one distinction it exists to draw
    var rows = said.components(separatedBy: "\n")
    var last = -1
    for (i, r) in rows.enumerated()
    where r.hasPrefix("public enum ") && r.hasSuffix(": " + kind + " {}") { last = i }
    if last >= 0 {
        // past the whole block, not past one line of it: a row is an extension
        // BODY, and stepping over it by its first line puts the next row inside
        // the previous one's braces
        while last + 1 < rows.count && rows[last + 1].hasPrefix("extension ") {
            var depth = 0
            while last + 1 < rows.count {
                last += 1
                depth += rows[last].filter { $0 == "{" }.count
                depth -= rows[last].filter { $0 == "}" }.count
                if depth <= 0 { break }
            }
        }
        rows.insert(String(line.dropLast()), at: last + 1)
        return rows.joined(separator: "\n")
    }
    return said + line
}

// ── WHAT A CONTRACT DECLARES, read for the one thing a client must agree with:
// the fields of a request, and the sort of thing each one is. The other carrier
// reads it in document order, so this one needs the reader above rather than
// Foundation's: a list of fields whose order changes run to run is a diff.
let DECLARED: [String: String] = ["string": "Text", "integer": "Count",
                                  "number": "Count", "boolean": "Flag",
                                  "array": "Many", "object": "Nested"]

func declaredShape(_ said: Said?) -> String? {
    guard let said = said else { return nil }
    if case .list(let items) = said {
        // two types is the contract leaving it open, and `null` beside one is not
        let real = items.compactMap { $0.asText }.filter { $0 != "null" }
        return real.count == 1 ? DECLARED[real[0]] : nil
    }
    return said.asText.flatMap { DECLARED[$0] }
}

struct Field { let route: String; let field: String; let where_: String; let shape: String? }

func spellable(_ name: String) -> Bool {
    // a name a library could spell: `project_ids` yes, `Parameter1.Name` no,
    // `StartTime<` no. The wire has a syntax; a vocabulary does not carry it.
    let pattern = "[A-Za-z_]\\w*(?:-\\w+)*"
    guard let re = try? NSRegularExpression(pattern: pattern) else { return false }
    let ns = name as NSString
    let m = re.firstMatch(in: name, range: NSRange(location: 0, length: ns.length))
    return m?.range.length == ns.length && m?.range.location == 0
}

func contractFields(_ spec: Said) -> [Field] {
    var shelf: [(String, Said)] = spec.at("definitions")?.asObject ?? []
    if let s = spec.at("components")?.at("schemas")?.asObject { shelf += s }
    func resolve(_ s: Said) -> Said {
        if let ref = s.at("$ref")?.asText {
            let name = ref.components(separatedBy: "/").last ?? ""
            return shelf.first(where: { $0.0 == name })?.1 ?? .object([])
        }
        return s
    }
    // what the contract also SENDS BACK: where one shape serves both directions,
    // its fields say nothing about what a request carries
    var returned = Set<String>()
    func gather(_ node: Said?) {
        guard let node = node else { return }
        switch node {
        case .object(let pairs):
            for (k, v) in pairs {
                if k == "$ref", let r = v.asText { returned.insert(r) }
                gather(v)
            }
        case .list(let items):
            for v in items { gather(v) }
        default: break
        }
    }
    for (_, ops) in spec.at("paths")?.asObject ?? [] {
        for (_, op) in ops.asObject ?? [] { gather(op.at("responses")) }
    }

    var out: [Field] = []
    for (route, ops) in spec.at("paths")?.asObject ?? [] {
        guard let opPairs = ops.asObject else { continue }
        let shared = ops.at("parameters")?.asList ?? []
        for (_, op) in opPairs {
            guard let _ = op.asObject else { continue }
            for p in (op.at("parameters")?.asList ?? []) + shared {
                guard p.asObject != nil, p.at("in")?.asText == "query",
                      let raw = p.at("name")?.asText, !raw.isEmpty else { continue }
                let sch = p.at("schema")
                if let inner = sch.map({ resolve($0) })?.at("properties")?.asObject, !inner.isEmpty {
                    // a query parameter declared as an object carries its fields
                    // in its properties; its own name is a wrapper nobody writes
                    for (nm, pr) in inner.sorted(by: { $0.0 < $1.0 }) {
                        out.append(Field(route: route, field: nm, where_: "query",
                                         shape: declaredShape(pr.at("type"))))
                    }
                    continue
                }
                // `project_ids[]` is how a repeated key is written ON THE WIRE
                let nm = raw.hasSuffix("[]") ? String(raw.dropLast(2)) : raw
                if !spellable(nm) { continue }
                out.append(Field(route: route, field: nm, where_: "query",
                                 shape: declaredShape(sch?.at("type") ?? p.at("type"))))
            }
            let content = op.at("requestBody")?.at("content")
            var body = content?.at("application/json")?.at("schema")
            if body == nil {
                // a form is a request too: the names go on the wire as written
                for kind in ["application/x-www-form-urlencoded", "multipart/form-data"] {
                    if let s = content?.at(kind)?.at("schema") { body = s; break }
                }
            }
            if body == nil {
                // swagger 2.0 puts the body among the parameters
                for p in op.at("parameters")?.asList ?? [] {
                    if p.at("in")?.asText == "body", let s = p.at("schema") { body = s; break }
                }
            }
            guard let found = body else { continue }
            if let ref = found.at("$ref")?.asText, returned.contains(ref) { continue }
            for (name, prop) in (resolve(found).at("properties")?.asObject ?? [])
                .sorted(by: { $0.0 < $1.0 }) {
                if !spellable(name) { continue }
                if case .yes = prop.at("readOnly") ?? .nothing { continue }
                out.append(Field(route: route, field: name, where_: "body",
                                 shape: declaredShape(prop.at("type") ?? resolve(prop).at("type"))))
            }
        }
    }
    return out
}

// ── aside ROUTE FIELD --because KEY: a divergence somebody means, said out loud
//
// The only writing verb this vein carries, and it writes one file: the
// divergences you declare, in the order they were declared. A record read back
// keeps its keys and their order, because a file rewritten in a different order
// every run is a diff nobody can read and a pair nobody can review.
func kindOf(_ said: Said) -> String {
    switch said {
    case .text: return "str"
    case .number: return "int"
    case .yes, .no: return "bool"
    case .nothing: return "NoneType"
    case .list: return "list"
    case .object: return "dict"
    }
}

func sameAgain(_ said: Said) -> String {
    // a value written back the way the other carrier writes it: `json.dumps`
    // with its own defaults, which is what both the guard's sentence and the
    // kept top-level keys go through
    switch said {
    case .text(let s): return asciiJSONString(s)
    case .number(let n): return n
    case .yes: return "true"
    case .no: return "false"
    case .nothing: return "null"
    case .list(let items): return "[" + items.map(sameAgain).joined(separator: ", ") + "]"
    case .object(let pairs):
        return "{" + pairs.map { asciiJSONString($0.0) + ": " + sameAgain($0.1) }
            .joined(separator: ", ") + "}"
    }
}

func laidOutBy(_ said: Said, _ depth: Int, _ step: Int) -> String {
    // the same shape at another indent: this file is written with one space,
    // the ANSWER is printed with two, and both are the other carrier's own
    let pad = String(repeating: " ", count: (depth + 1) * step)
    let close = String(repeating: " ", count: depth * step)
    switch said {
    case .list(let items):
        if items.isEmpty { return "[]" }
        return "[\n" + items.map { pad + laidOutBy($0, depth + 1, step) }
            .joined(separator: ",\n") + "\n" + close + "]"
    case .object(let pairs):
        if pairs.isEmpty { return "{}" }
        return "{\n" + pairs.map { pad + jsonString($0.0) + ": " + laidOutBy($0.1, depth + 1, step) }
            .joined(separator: ",\n") + "\n" + close + "}"
    default:
        return sameAgain(said)
    }
}

func laidOut(_ said: Said, _ depth: Int) -> String {
    // python's `json.dump(..., indent=1)`, which is what writes this file on the
    // other carrier: a container opens, its items sit one deeper, and the
    // closing bracket comes back to the container's own depth. The compact form
    // above is `json.dumps(x)` with no indent, which is what a SENTENCE about a
    // value uses; a file and a sentence are not the same channel.
    let pad = String(repeating: " ", count: depth + 1)
    let close = String(repeating: " ", count: depth)
    switch said {
    case .list(let items):
        if items.isEmpty { return "[]" }
        return "[\n" + items.map { pad + laidOut($0, depth + 1) }.joined(separator: ",\n")
             + "\n" + close + "]"
    case .object(let pairs):
        if pairs.isEmpty { return "{}" }
        return "{\n" + pairs.map { pad + asciiJSONString($0.0) + ": " + laidOut($0.1, depth + 1) }
            .joined(separator: ",\n") + "\n" + close + "}"
    default:
        return sameAgain(said)
    }
}

func asciiJSONString(_ s: String) -> String {
    // the file this verb writes goes through python's `json.dump` on the other
    // carrier, whose default escapes everything above ascii; the ANSWER goes
    // through `json.dumps(..., ensure_ascii=False)` and does not. One tool, two
    // channels, and the bytes have to match on each.
    var out = "\""
    for scalar in s.unicodeScalars {
        switch scalar {
        case "\"": out += "\\\""
        case "\\": out += "\\\\"
        case "\n": out += "\\n"
        case "\t": out += "\\t"
        case "\r": out += "\\r"
        default:
            if scalar.value < 0x20 {
                out += String(format: "\\u%04x", scalar.value)
            } else if scalar.value < 0x80 {
                out.unicodeScalars.append(scalar)
            } else if scalar.value > 0xFFFF {
                let v = scalar.value - 0x10000
                out += String(format: "\\u%04x\\u%04x", 0xD800 + (v >> 10), 0xDC00 + (v & 0x3FF))
            } else {
                out += String(format: "\\u%04x", scalar.value)
            }
        }
    }
    return out + "\""
}

func asideJSON(_ rows: [[(String, String)]], _ others: [(String, String)]) -> String {
    // python writes this with `json.dump(..., indent=1)`, and this is that shape
    // written out: one space of indent, keys in the order they were set
    // whatever else the file said at its top level travels with it, in the order
    // it was written: the other carrier keeps those keys because it loads the
    // whole document and replaces one of them
    var head = others.map { " " + asciiJSONString($0.0) + ": " + $0.1 }
    if rows.isEmpty {
        head.append(" \"diverges\": []")
        return "{\n" + head.joined(separator: ",\n") + "\n}"
    }
    var blocks: [String] = []
    for r in rows {
        let inner = r.map { "   " + asciiJSONString($0.0) + ": " + asciiJSONString($0.1) }
            .joined(separator: ",\n")
        blocks.append("  {\n" + inner + "\n  }")
    }
    head.append(" \"diverges\": [\n" + blocks.joined(separator: ",\n") + "\n ]")
    return "{\n" + head.joined(separator: ",\n") + "\n}"
}

// ── A ROAD MAY BE WALKED BEFORE ITS VERB ARRIVES. `contractFields` is the
// reading `declare` and `drift` will both stand on, and it is here now with
// nothing routed to it: a door the BATTERY opens, never an argv a person types.
// The alternative was leaving it in a session's scratch, where it would have
// died with the session; sleeping code a vector holds is not dead code.
// the writing road, opened by the battery and by no argv: it prints what the
// layout WOULD become, and writes nothing, so the comparison is byte for byte
// against what the other carrier's own writing verb leaves on disk
if args.first == "--manifest-row" {
    guard args.count > 4 else {
        cannot("--manifest-row takes a file, a kind, a role and a world",
               "the battery calls this, not a person")
    }
    let path = args[1], kind = args[2], role = args[3], root = args[4]
    let mp = (root as NSString).appendingPathComponent("gate.manifest.swift")
    let text = FileManager.default.fileExists(atPath: mp)
        ? theirsText(mp, "the layout of this world") : manifestHead()
    let rel = path.hasPrefix(root + "/") ? String(path.dropFirst(root.count + 1)) : path
    out(upsertRow(text, name: rowAtom(rel), rel: rel, kind: kind, role: role))
    exit(0)
}

if args.first == "--contract-fields" {
    guard args.count > 1 else { cannot("--contract-fields takes a document", "name one") }
    let text = theirsText(args[1], "an OpenAPI document")
    guard let spec = readSaid(text) else {
        cannot(args[1] + " is not the JSON this reads", "point it at an OpenAPI document")
    }
    var blocks: [String] = []
    for f in contractFields(spec) {
        var one = "  {\n"
        one += "    \"route\": " + jsonString(f.route) + ",\n"
        one += "    \"field\": " + jsonString(f.field) + ",\n"
        one += "    \"where\": " + jsonString(f.where_) + ",\n"
        one += "    \"shape\": " + (f.shape.map { jsonString($0) } ?? "null") + "\n"
        one += "  }"
        blocks.append(one)
    }
    out(blocks.isEmpty ? "[]\n" : "[\n" + blocks.joined(separator: ",\n") + "\n]\n")
    exit(0)
}

// ── THE STATUS CORE: the last big road, and the one every asking verb will
// stand on. The world is discovered the way the other carrier discovers it,
// each row is routed to its court by role, the courts are the ones compiled
// into this binary, and the guards beside them are the python side's, spelled
// a second time and held to the first by the battery's parity on worlds that
// refuse for every reason a guard exists. Nothing here is reached by a carried
// argv: the door at the end of the section is the battery's, the way
// `--contract-fields` and `--manifest-row` are, because the verb itself moves
// with the pack that asks it, and the tables bootstrap (`ensure_world`) stays
// on the python side until the import family moves.

// the roles a row may have, in the order the refusal lists them
let STATUS_ROLES: [(String, String)] = [
    ("world", "judged with the rest of my world, by the plain court"),
    ("seam", "judged where it meets mine, and nowhere else"),
    ("forms", "grammar and the certificates over it, judged by the where court"),
    ("judge", "the court itself: held by a reproducible build, not by judgement"),
    ("carried", "brought here unchanged: held by its source's name and version, "
              + "and by no court of this world"),
    ("tool", "the tool's own source: held by the battery's parity, "
           + "and by no court of this world"),
]
let ROLE_OF_KIND: [String: String] = ["WorldFile": "world", "SeamFile": "seam",
                                      "FormsFile": "forms", "JudgeFile": "judge",
                                      "CarriedFile": "carried", "ToolFile": "tool",
                                      "Seam": "seam"]

// the shelf, loaded once per run the way the other carrier loads it at import:
// filled by the status door, empty on every carried argv, so no vein pays for
// a road it is not walking
var STDLIB_TEXTS: [String: String] = [:]
var SHELF_ORDER: [String] = []
var SHIPPED_SET: Set<String> = []

func loadStatusShelf() {
    for page in shelf() {
        STDLIB_TEXTS[page.name] = page.text
        SHELF_ORDER.append(page.name)
        SHIPPED_SET.insert(absPath((root.appendingPathComponent("stdlib").path as NSString)
            .appendingPathComponent(page.name + ".swift")))
    }
}

func absPath(_ p: String) -> String {
    // python's abspath is lexical: nothing is resolved, `.` and `..` fold away
    let full = p.hasPrefix("/") ? p
        : (FileManager.default.currentDirectoryPath as NSString).appendingPathComponent(p)
    var out: [String] = []
    for c in full.components(separatedBy: "/") {
        if c.isEmpty || c == "." { continue }
        if c == ".." { if !out.isEmpty { out.removeLast() }; continue }
        out.append(c)
    }
    return "/" + out.joined(separator: "/")
}

func relPath(_ path: String, _ start: String) -> String {
    let p = absPath(path).components(separatedBy: "/").filter { !$0.isEmpty }
    let s = absPath(start).components(separatedBy: "/").filter { !$0.isEmpty }
    var i = 0
    while i < min(p.count, s.count), p[i] == s[i] { i += 1 }
    let rest = [String](repeating: "..", count: s.count - i) + p[i...]
    return rest.isEmpty ? "." : rest.joined(separator: "/")
}

func readText(_ path: String) -> String? {
    // read with python's errors="replace": a byte that is not utf-8 becomes the
    // replacement character rather than a refusal to read the file at all
    guard let data = FileManager.default.contents(atPath: path) else { return nil }
    return String(decoding: data, as: UTF8.self)
}

func matchesAt(_ pattern: String, _ text: String,
               dotAll: Bool = false, lines: Bool = false) -> [(groups: [String], line: Int)] {
    // like `matches`, and each hit carries the line its match starts on,
    // counted from one: the other carrier addresses a row by
    // text[:m.start()].count("\n") + 1
    var opts: NSRegularExpression.Options = []
    if dotAll { opts.insert(.dotMatchesLineSeparators) }
    if lines { opts.insert(.anchorsMatchLines) }
    guard let re = try? NSRegularExpression(pattern: pattern, options: opts) else { return [] }
    let ns = text as NSString
    return re.matches(in: text, range: NSRange(location: 0, length: ns.length)).map { m in
        let groups = (1..<m.numberOfRanges).map { i in
            m.range(at: i).location == NSNotFound ? "" : ns.substring(with: m.range(at: i))
        }
        let before = ns.substring(to: m.range.location)
        return (groups, before.components(separatedBy: "\n").count)
    }
}

func matchAt(_ text: String, _ pattern: String) -> [String]? {
    // python's re.match: anchored at the start, groups from the whole match on
    guard let re = try? NSRegularExpression(pattern: "^(?:" + pattern + ")") else { return nil }
    let ns = text as NSString
    guard let m = re.firstMatch(in: text, range: NSRange(location: 0, length: ns.length)),
          m.range.location == 0 else { return nil }
    return (0..<m.numberOfRanges).map { i in
        m.range(at: i).location == NSNotFound ? "" : ns.substring(with: m.range(at: i))
    }
}

struct LayoutRow {
    var name: String?
    var source: String
    var path: String
    var role: String?
    var from: String?
    var written: String?
    var opens: String?
    var line: Int
}
struct Layout { var manifest: String; var rows: [LayoutRow] }
struct WorldState { var facts: String?; var tables: String?; var layout: Layout? }

func layoutDir(_ w: WorldState) -> String? {
    return w.layout.map { ($0.manifest as NSString).deletingLastPathComponent }
}

func layoutRowsFull(_ dir: String) -> (rows: [LayoutRow], manifest: String?) {
    let mp = (dir as NSString).appendingPathComponent("gate.manifest.swift")
    guard let text = readText(mp) else { return ([], nil) }
    let code = uncommented(text)
    var lit: [String: String] = [:]
    for m in matches("extension (\\w+)\\b[^{]*\\{(.*?)\\n(?=public |extension |\\z)",
                     code + "\n", dotAll: true) where m.count == 2 {
        if let f = matches("typeName:\\s*String\\s*\\{\\s*\"([^\"]*)\"\\s*\\}", m[1]).first,
           f.count == 1 {
            lit[m[0]] = f[0]
        }
    }
    var rows: [LayoutRow] = []
    for (m, at) in matchesAt("public enum (\\w+): (Mine|Theirs|WorldFile|SeamFile) \\{", code) {
        let name = m[0], atom = m[1]
        let inner = matches("public enum " + name + "\\b[^{]*\\{(.*?)\\n\\}",
                            code + "\n", dotAll: true).first?.first ?? ""
        let outer = matches("extension " + name + "\\b[^{]*\\{(.*?)\\n(?=public |extension |\\z)",
                            code + "\n", dotAll: true).first?.first ?? ""
        let both = inner + outer
        func field(_ k: String) -> String? {
            return matches(k + ":\\s*String\\s*\\{\\s*\"([^\"]*)\"\\s*\\}", both).first?.first
        }
        func axis(_ k: String) -> String? {
            return matches("typealias " + k + "\\s*=\\s*(\\w+)", both).first?.first
        }
        var path = lit[name] ?? ""
        if path.isEmpty { path = field("typeName") ?? "" }
        if path.isEmpty { continue }
        let kind = axis("Kind")
        var role: String? = kind.map { ROLE_OF_KIND[$0] ?? $0.lowercased() }
        if role == nil || role!.isEmpty { role = field("role") }
        if role == nil || role!.isEmpty {
            role = atom == "WorldFile" ? "world" : atom == "SeamFile" ? "seam" : nil
        }
        var from = axis("At").flatMap { lit[$0] }
        if from == nil || from!.isEmpty { from = field("from") }
        rows.append(LayoutRow(name: name,
                              source: (atom == "Mine" || atom == "WorldFile") ? "mine" : "theirs",
                              path: path, role: role,
                              from: (from?.isEmpty ?? true) ? nil : from,
                              written: axis("Written"), opens: axis("Opens"), line: at))
    }
    if rows.isEmpty && !code.contains("Mine") && !code.contains("WorldFile") {
        // older layouts: a bare list of paths, every one of them a world file
        rows = matches("typeName:\\s*String\\s*\\{\\s*\"([^\"]+)\"\\s*\\}", code).map {
            LayoutRow(name: nil, source: "mine", path: $0[0], role: "world",
                      from: nil, written: nil, opens: nil, line: 0)
        }
    }
    return (rows, mp)
}

func discoverWorld() -> WorldState {
    // the world is found the way .git is: walking up. GATE_FACTS pins it for
    // probes and carries no layout, the way the other carrier's override does.
    if let env = ProcessInfo.processInfo.environment["GATE_FACTS"], !env.isEmpty {
        return WorldState(facts: env, tables: nil, layout: nil)
    }
    var d = FileManager.default.currentDirectoryPath
    while true {
        let w = (d as NSString).appendingPathComponent("gate.swift")
        let t = (d as NSString).appendingPathComponent("tables")
        let hasTables = FileManager.default.fileExists(
                atPath: (t as NSString).appendingPathComponent("people.csv"))
            && FileManager.default.fileExists(
                atPath: (t as NSString).appendingPathComponent("grants.csv"))
        let (rows, mp) = layoutRowsFull(d)
        let layout = mp.map { Layout(manifest: $0, rows: rows) }
        if FileManager.default.fileExists(atPath: w) || hasTables || layout != nil {
            return WorldState(facts: w, tables: hasTables ? t : nil, layout: layout)
        }
        let up = (d as NSString).deletingLastPathComponent
        if up == d || up.isEmpty { break }
        d = up
    }
    if let corpus = ProcessInfo.processInfo.environment["GATE_CORPUS"], !corpus.isEmpty {
        let f = (((corpus as NSString).appendingPathComponent("Sources") as NSString)
            .appendingPathComponent("Organization") as NSString)
            .appendingPathComponent("System/GeneratedTeam.swift")
        return WorldState(facts: f, tables: nil, layout: nil)
    }
    return WorldState(facts: nil, tables: nil, layout: nil)
}

func worldFilesOf(_ w: WorldState) -> [String] {
    var files: [String] = []
    if let f = w.facts, FileManager.default.fileExists(atPath: f) { files.append(f) }
    if let d = layoutDir(w) {
        // filtered against the list as it stood, not as it grows: two rows
        // naming one file keep both copies here, exactly as the other carrier
        // keeps them, and the second-row guard is the one that refuses the pair
        let stood = files
        for r in w.layout!.rows where r.role == "world" {
            let p = (d as NSString).appendingPathComponent(r.path)
            if !stood.contains(p) { files.append(p) }
        }
    }
    return files
}

func worldPeopleOf(_ w: WorldState) -> Set<String> {
    var names = Set<String>()
    var seen = worldFilesOf(w)
    let base = layoutDir(w) ?? "."
    for r in w.layout?.rows ?? [] {
        let p = (base as NSString).appendingPathComponent(r.path)
        if ["world", "forms", "seam"].contains(r.role ?? ""),
           FileManager.default.fileExists(atPath: p), !seen.contains(p) {
            seen.append(p)
        }
    }
    for p in seen {
        guard let text = readText(p) else { continue }
        for m in matches("(?:public\\s+)?enum\\s+(\\w+)\\s*:", text) { names.insert(m[0]) }
    }
    return names
}

func canonicalPath(_ p: String) -> String {
    // one door for every path comparison that crosses realpath: macOS's
    // resolvingSymlinksInPath strips the /private prefix from a path that
    // exists and leaves it on one that does not, so both sides of any
    // comparison go through here and the spelling cannot split them
    let r = (absPath(p) as NSString).resolvingSymlinksInPath
    for known in ["/private/tmp/", "/private/var/", "/private/etc/"]
    where r.hasPrefix(known) || r == String(known.dropLast()) {
        return String(r.dropFirst("/private".count))
    }
    return r
}

func leavesWorldHere(_ path: String, _ rootDir: String) -> Bool {
    let real = canonicalPath((rootDir as NSString).appendingPathComponent(path))
    return relPath(real, canonicalPath(rootDir)).components(separatedBy: "/").first == ".."
}

func isSeamSide(_ path: String) -> Bool {
    guard let data = FileManager.default.contents(atPath: path) else { return false }
    let head = String(decoding: data.prefix(4000), as: UTF8.self)
    return !matches("^public enum \\w+: Carrier \\{\\}", head, lines: true).isEmpty
        || !matches("^public enum F_\\w+: Declared \\{", head, lines: true).isEmpty
}

func topNames(_ text: String) -> [(String, Int)] {
    // the names a file gives, at the top of it and nowhere else: a typealias
    // inside a declaration is an axis, and every record of a kind states the
    // same ones
    var out: [(String, Int)] = []
    var depth = 0
    for (i, line) in text.components(separatedBy: "\n").enumerated() {
        let code = line.components(separatedBy: "//")[0]
        if depth == 0,
           let m = matchAt(code, "\\s*(?:public\\s+)?(enum|protocol|struct|typealias)\\s+(\\w+)") {
            out.append((m[2], i + 1))
        }
        depth += code.filter { $0 == "{" }.count - code.filter { $0 == "}" }.count
    }
    return out
}

func undeclaredHere(_ w: WorldState) -> [String] {
    guard let layout = w.layout else { return [] }
    let d = (layout.manifest as NSString).deletingLastPathComponent
    var declared = Set<String>([layout.manifest,
                                (d as NSString).appendingPathComponent("gate.swift"),
                                (d as NSString).appendingPathComponent("gate.policy.swift")])
    var spoken = Set<String>([d])
    for r in layout.rows where !r.path.isEmpty {
        let p = (d as NSString).appendingPathComponent(r.path)
        declared.insert(p)
        spoken.insert((p as NSString).deletingLastPathComponent)
    }
    var out: [String] = []
    for dd in spoken.sorted() {
        var isDir: ObjCBool = false
        guard FileManager.default.fileExists(atPath: dd, isDirectory: &isDir),
              isDir.boolValue else { continue }
        for f in ((try? FileManager.default.contentsOfDirectory(atPath: dd)) ?? []).sorted() {
            let p = (dd as NSString).appendingPathComponent(f)
            if f.hasSuffix(".swift"), !declared.contains(p), !isSeamSide(p),
               !leavesWorldHere(relPath(p, d), d) {
                out.append(relPath(p, d))
            }
        }
    }
    return out
}

func manifestGuards(_ w: WorldState) -> [(address: String, claim: String)] {
    // layout guards, both directions: a declared file exists, a neighbouring
    // *.swift is declared, a row says which court reads it, and every claim
    // below is the other carrier's, word for word
    guard let layout = w.layout else { return [] }
    var bad: [(address: String, claim: String)] = []
    let man = (layout.manifest as NSString).lastPathComponent
    let d = (layout.manifest as NSString).deletingLastPathComponent
    let live = layout.rows
    let liveText = uncommented(readText(layout.manifest) ?? "")
    var seenPaths: [String: String] = [:]
    for r in live {
        let said = r.name ?? "None"
        if let role = r.role, let atom = ROLE_ATOM[role],
           liveText.contains("public typealias Kind = " + atom),
           !liveText.contains("public enum " + atom + ": Role {}") {
            bad.append(("\(man):\(r.line)",
                        "`\(said)` is filed under `\(role)` and this document "
                      + "declares no `\(atom)`: a column is an axis to a declared atom, "
                      + "and a name nothing declares names nothing"))
        }
        if let prev = seenPaths[r.path] {
            bad.append(("\(man):\(r.line)",
                        "`\(said)` is a second row about \(r.path), which "
                      + "`\(prev)` already speaks for: one file, one "
                      + "row, or two rows can say different things about it"))
        }
        seenPaths[r.path] = said
        if leavesWorldHere(r.path, d) {
            bad.append(("\(man):\(r.line)",
                        "`\(said)` names \(r.path), which is outside this world: "
                      + "a row is a claim about this world's own tree, and a path that "
                      + "leaves it holds only on the machine that wrote it"))
        }
        if r.role == nil || r.role!.isEmpty {
            bad.append(("\(man):\(r.line)",
                        "`\(said)` does not say what it is for. A row names its court: "
                      + STATUS_ROLES.map { "`\($0.0)` — \($0.1)" }.joined(separator: " · ")))
        } else if r.role == "seam",
                  FileManager.default.fileExists(
                      atPath: (d as NSString).appendingPathComponent(r.path)),
                  !isSeamSide((d as NSString).appendingPathComponent(r.path)) {
            bad.append(("\(man):\(r.line)",
                        "`\(said)` is filed under `seam`, and \(r.path) does not "
                      + "say it is one side of one: a side states a contract or claims "
                      + "to carry one, in its own first lines"))
        } else if !STATUS_ROLES.contains(where: { $0.0 == r.role }) {
            bad.append(("\(man):\(r.line)",
                        "`\(said)` is for `\(r.role!)`, which no court here reads. "
                      + "A row gate cannot place is refused, never quietly taken as a "
                      + "fragment of your world: "
                      + STATUS_ROLES.map { $0.0 }.joined(separator: " · ")))
        }
        if r.source == "theirs" && r.from == nil {
            bad.append(("\(man):\(r.line)",
                        "`\(said)` is theirs and does not say which revision it was "
                      + "taken at. Taken means taken from somewhere, at something: "
                      + "`gate theirs " + r.path + " --at REV`"))
        }
    }
    let named = Set(live.compactMap { $0.name })
    for (m, at) in matchesAt("public enum (\\w+): (Mine|Theirs|WorldFile|SeamFile) \\{", liveText)
    where !named.contains(m[0]) {
        bad.append(("\(man):\(at)",
                    "`\(m[0])` is a row and names no file: a row is about one file, "
                  + "said as `extension \(m[0]) { public static var typeName: "
                  + "String { \"path\" } }`. Give it one or take the row out"))
    }
    for r in live where ["world", "seam", "forms"].contains(r.role ?? "") {
        if !FileManager.default.fileExists(atPath: (d as NSString).appendingPathComponent(r.path)) {
            bad.append(("\(man):\(r.line)",
                        "the manifest declares \(r.path), and no such file exists: "
                      + "either the file is gone or the row is, and a row for a file "
                      + "nobody has is a court with nothing to check"))
        }
    }
    for r in live where r.role == "forms" && !r.path.isEmpty {
        let p = (d as NSString).appendingPathComponent(r.path)
        guard let data = FileManager.default.contents(atPath: p) else { continue }
        let head = String(decoding: data.prefix(1200), as: UTF8.self)
            .components(separatedBy: "\n").prefix(8)
        var want: String? = nil
        var saw = false
        for ln in head where ln.hasPrefix("//") && ln.contains("written in") {
            saw = true
            want = matches("stdlib show ([\\w-]+)", ln).first.map { $0[0] }
            break
        }
        guard saw, let shelfName = want else { continue }
        let wantFile = shelfName + ".swift"
        let mineNames = Set(topNames(String(decoding: data, as: UTF8.self)).map { $0.0 })
        let theirs = Set(topNames(STDLIB_TEXTS[shelfName] ?? "").map { $0.0 })
        if !theirs.isDisjoint(with: mineNames) { continue }
        let row = live.first(where: { $0.name == r.written })
        if row == nil || (row!.path as NSString).lastPathComponent != wantFile {
            bad.append(("\(man):\(r.line)",
                        "`\(r.name ?? "None")` says in its own head that it is written in "
                      + "\(wantFile), and this row does not declare it: add "
                      + "`public typealias Written = <the row for \(wantFile)>`. Which laws a "
                      + "page is judged under is a column, not a comment"))
        }
    }
    for rel in undeclaredHere(w) {
        bad.append((rel,
                    "this file sits beside the judged ones and has no row in the "
                  + "manifest, so it is not judged. `gate mine PATH --role R` adds "
                  + "the row"))
    }
    return bad
}

func findAll(_ pattern: String, _ text: String, lines: Bool = false) -> [String] {
    // python's findall for a pattern with no groups: the whole match, each time
    var opts: NSRegularExpression.Options = []
    if lines { opts.insert(.anchorsMatchLines) }
    guard let re = try? NSRegularExpression(pattern: pattern, options: opts) else { return [] }
    let ns = text as NSString
    return re.matches(in: text, range: NSRange(location: 0, length: ns.length))
        .map { ns.substring(with: $0.range) }
}

func oneStream(_ w: WorldState, _ named: [(String, String)]) -> [(String, String)] {
    // one namespace is one stream, and this is the one place that says which:
    // a forms file is its own stream, and the layout's court is the guards
    let forms = Set((w.layout?.rows ?? []).filter { $0.role == "forms" }.map { $0.path })
    var apart = Set<String>()
    if let l = w.layout { apart.insert(absPath(l.manifest)) }
    if let pp = policyPathOf(w) { apart.insert(absPath(pp)) }
    return named.filter { !forms.contains($0.0) && !apart.contains(absPath($0.1)) }
}

func diskSources(_ w: WorldState) -> [(String, String)] {
    var out: [(String, String)] = []
    for (n, p) in oneStream(w, benchFilesOf(w)) where FileManager.default.fileExists(atPath: p) {
        out.append((n, readText(p) ?? ""))
    }
    return out
}

func duplicateGuardsOver(_ sources: [(String, String)]) -> [(address: String, claim: String)] {
    var seen: [String: String] = [:]
    var bad: [(address: String, claim: String)] = []
    for (name, text) in sources {
        for (who, i) in topNames(text) {
            let here = "\(name):\(i)"
            if let was = seen[who] {
                bad.append((here,
                            "`\(who)` is declared twice: once at \(was) and again "
                          + "here. One name, one declaration: two of them are two truths "
                          + "about it, and only one can be read"))
            } else {
                seen[who] = here
            }
        }
    }
    return bad
}

func entryGuardsOver(_ sources: [(String, String)]) -> [(address: String, claim: String)] {
    // the body is total, the way the top of a file is: every line inside one
    // belongs to a whole entry, and an entry that never closes is named
    var bad: [(address: String, claim: String)] = []
    for (name, text) in sources {
        let lines = text.components(separatedBy: "\n")
        var inBody = false, depth = 0
        var openAt: Int? = nil
        for (i0, rawLine) in lines.enumerated() {
            let i = i0 + 1
            let code = rawLine.components(separatedBy: "//")[0]
            if !inBody {
                if !matches("var\\s+body\\s*:\\s*some\\s+Structure\\s*\\{", code).isEmpty {
                    inBody = true; depth = 1; openAt = nil
                }
                continue
            }
            depth += code.filter { $0 == "{" }.count - code.filter { $0 == "}" }.count
            if depth <= 0 {
                if let at = openAt {
                    bad.append(("\(name):\(at)",
                                "an entry opens here and never closes: everything after it "
                              + "stops being read as a claim, and the judge says nothing"))
                }
                inBody = false
                continue
            }
            let bare = code.trimmingCharacters(in: .whitespaces)
            if bare.isEmpty { continue }
            let closes = !matches(">\\s*\\.self\\s*;?", bare).isEmpty
            let opens = matchAt(bare, "[A-Z]\\w*\\s*<") != nil
            if opens {
                if let at = openAt {
                    bad.append(("\(name):\(at)",
                                "an entry opens here and never closes: the next one begins "
                              + "before it ends, so neither is read as a claim"))
                }
                openAt = i
                if closes { openAt = nil }
                continue
            }
            if closes {
                if openAt == nil {
                    bad.append(("\(name):\(i)",
                                "an entry closes here that nothing opens: its form is "
                              + "commented out or missing, so the claim it made is gone "
                              + "and what is left is not Swift"))
                }
                openAt = nil
                continue
            }
            if openAt == nil {
                bad.append(("\(name):\(i)",
                            "`\(bare.prefix(40))` stands inside a body and belongs to no entry: "
                          + "a body holds claims, and every claim is a form, its arguments "
                          + "and the `>.self` that ends it"))
            }
        }
    }
    return bad
}

func lawNotes(_ texts: [String]) -> [String: String] {
    // a law's own sentence, read from the file the law is written in: the ///
    // run directly above a declaration, first spelling wins
    var out: [String: String] = [:]
    for text in texts {
        let lines = text.components(separatedBy: "\n")
        for (i, line) in lines.enumerated() {
            guard let m = matchAt(line.trimmingCharacters(in: .whitespaces),
                                  "public (?:protocol|enum|typealias) (\\w+)"),
                  out[m[1]] == nil else { continue }
            var said: [String] = []
            var j = i - 1
            while j >= 0 {
                let s = lines[j].trimmingCharacters(in: .whitespaces)
                if !s.hasPrefix("///") { break }
                said.insert(String(s.dropFirst(3)).trimmingCharacters(in: .whitespaces), at: 0)
                j -= 1
            }
            if !said.isEmpty {
                out[m[1]] = said.joined(separator: " ").trimmingCharacters(in: .whitespaces)
            }
        }
    }
    return out
}

func plainly(_ claim: String, _ notes: [String: String]) -> String {
    // the where court's sentence, said the way the plain court says its own:
    // the certificate, the two sides, and the law in the law's own words
    guard let m = matchAt(claim, "'(\\w+)[^']*' requires the types '[^']*' \\(aka '([^']+)'\\) "
                               + "and '[^']*' \\(aka '([^']+)'\\) be equivalent(?: \\[(\\w+)\\])?")
    else { return claim }
    let said = notes[m[4]]
    return "\(m[1]) · \(m[2]) against \(m[3])" + (said.map { ": " + $0 } ?? "")
}

func presentedOver(_ w: WorldState, _ shelfName: String)
    -> (text: String, placed: [(String, String)], clash: [(address: String, claim: String)]) {
    // a world you present replaces a value in a world this tool ships, in
    // place, and only this world's names; two declarations inside one layer
    // are refused with both addresses rather than settled by list order
    let shipped = STDLIB_TEXTS[shelfName] ?? ""
    let rows = w.layout?.rows ?? []
    if rows.isEmpty { return (shipped, [], []) }
    let base = layoutDir(w) ?? "."
    var mine: [(name: String, path: String, line: Int, raw: String)] = []
    var clash: [(address: String, claim: String)] = []
    for r in rows where r.role == "forms" {
        if SHIPPED_SET.contains(absPath((base as NSString).appendingPathComponent(r.path))) {
            continue
        }
        let fp = (base as NSString).appendingPathComponent(r.path)
        guard FileManager.default.fileExists(atPath: fp), let body = readText(fp) else { continue }
        var depth = 0
        for (i0, line) in body.components(separatedBy: "\n").enumerated() {
            let i = i0 + 1
            let code = line.components(separatedBy: "//")[0]
            let atTop = depth == 0
            depth += code.filter { $0 == "{" }.count - code.filter { $0 == "}" }.count
            guard let m = matchAt(line.trimmingCharacters(in: .whitespaces),
                                  "public typealias (\\w+) = "), atTop else { continue }
            let name = m[1]
            let head = matchAt(line.trimmingCharacters(in: .whitespaces),
                               "public typealias \\w+ = (\\w+)<")
            let was = matches("^public typealias " + name + " = (\\w+)<", shipped, lines: true).first
            if let was = was, head == nil || head![1] != was[0] {
                clash.append(("\(r.path):\(i)",
                              "`\(name)` is a law of a world you did not write, and this "
                            + "says it is `\(head.map { $0[1] } ?? "a value")` where "
                            + "it is `\(was[0])`. Restate what holds of your own "
                            + "numbers as much as you like. The form is not yours to "
                            + "replace, or the law could be rewritten to permit whatever "
                            + "broke it"))
                continue
            }
            if let had = mine.first(where: { $0.name == name }), had.path != r.path {
                clash.append(("\(r.path):\(i)",
                              "`\(name)` is said here and at \(had.path):"
                            + "\(had.line) — two worlds you present, one name, "
                            + "and nothing but the order they are listed in to choose "
                            + "between them. One layer, one declaration"))
                continue
            }
            if let at = mine.firstIndex(where: { $0.name == name }) {
                mine[at] = (name, r.path, i, line)
            } else {
                mine.append((name, r.path, i, line))
            }
        }
    }
    if mine.isEmpty { return (shipped, [], clash) }
    var out: [String] = []
    var placed: [(String, String)] = []
    for ln in shipped.components(separatedBy: "\n") {
        if let m = matchAt(ln.trimmingCharacters(in: .whitespaces), "public typealias (\\w+) = "),
           let had = mine.first(where: { $0.name == m[1] }) {
            out.append(had.raw)
            if !placed.contains(where: { $0.0 == m[1] }) { placed.append((m[1], had.path)) }
        } else {
            out.append(ln)
        }
    }
    return (out.joined(separator: "\n"), placed, clash)
}

func canonGuard(_ w: WorldState, _ out: String, _ spoke: Bool, _ verb: String)
    -> [(address: String, claim: String)] {
    // a court that did not answer is not a court that found nothing: each
    // court is held to its own printed voice, and a silence is named
    if spoke { return [] }
    let words = out.split(whereSeparator: { $0 == " " || $0 == "\n" || $0 == "\t" || $0 == "\r"
                                            || $0 == "\u{0b}" || $0 == "\u{0c}" })
        .joined(separator: " ")
    let said = words.isEmpty ? "nothing at all" : String(words.prefix(120))
    let address = w.layout.map { ($0.manifest as NSString).lastPathComponent } ?? "gate-judge"
    return [(address,
             "the court was asked `\(verb)` and did not answer in its own canon: it "
           + "said `\(said)`. Every verdict here is read out of that answer, so an "
           + "answer this tool cannot read is not a green. It is a court that did not "
           + "sit, and a green over it would be this tool's own worst failure")]
}

func whereRefused(_ out: String) -> [(cert: String?, claim: String)] {
    var found: [(String?, String)] = []
    for line in out.components(separatedBy: "\n") {
        let l = line.trimmingCharacters(in: .whitespaces)
        guard l.hasPrefix("✗") else { continue }
        let claim = String(l.dropFirst()).trimmingCharacters(in: .whitespaces)
        found.append((matchAt(claim, "'(\\w+)").map { $0[1] }, claim))
    }
    return found
}

func formsGuards(_ w: WorldState, _ size: inout [String: Int]) -> [(address: String, claim: String)] {
    // the forms rows of one layout are one world laid out in files: glued and
    // judged together by the where court, with the shelf worlds an operator
    // overrides judged each as its own stream
    guard let layout = w.layout else { return [] }
    let d = (layout.manifest as NSString).deletingLastPathComponent
    let rows = layout.rows.filter { $0.role == "forms"
        && FileManager.default.fileExists(atPath: (d as NSString).appendingPathComponent($0.path)) }
    if rows.isEmpty { return [] }
    var bad: [(address: String, claim: String)] = []
    func bodyOf(_ r: LayoutRow) -> String {
        return readText((d as NSString).appendingPathComponent(r.path)) ?? ""
    }
    var streams: [(shelf: String?, text: String, mine: [(String, String)])] = []
    for shelfName in SHELF_ORDER {
        let (text, placed, clash) = presentedOver(w, shelfName)
        bad += clash
        if !placed.isEmpty { streams.append((shelfName, text, placed)) }
    }
    streams.append((nil, rows.map(bodyOf).joined(separator: "\n"), []))
    var whereMap: [String: String] = [:]
    for r in rows {
        for (i0, line) in bodyOf(r).components(separatedBy: "\n").enumerated() {
            if let m = matchAt(line.trimmingCharacters(in: .whitespaces),
                               "public (?:typealias|enum|protocol) (\\w+)"),
               whereMap[m[1]] == nil {
                whereMap[m[1]] = "\(r.path):\(i0 + 1)"
            }
        }
    }
    let tmp = NSTemporaryDirectory() + "gate-forms-\(ProcessInfo.processInfo.processIdentifier)"
    try? FileManager.default.createDirectory(atPath: tmp, withIntermediateDirectories: true)
    for (shelfName, text, mine) in streams {
        let fp = (tmp as NSString).appendingPathComponent((shelfName ?? "presented") + ".swift")
        try? text.write(toFile: fp, atomically: false, encoding: .utf8)
        let said = courtSays(["where", fp])
        bad += canonGuard(w, said,
                          (said.contains("THE WHERE") && said.contains("canon v"))
                              || said.contains("✗"),
                          "judge where")
        for (cert, claim) in whereRefused(said) {
            var spot: String? = cert.flatMap { whereMap[$0] }
            if spot == nil && !mine.isEmpty {
                let touched = mine.map { $0.0 }.filter { claim.contains($0) }
                spot = touched.first.flatMap { whereMap[$0] }
                if spot == nil, let t = touched.first {
                    spot = mine.first(where: { $0.0 == t })?.1
                }
            }
            bad.append((spot ?? rows[0].path, plainly(claim, lawNotes([text]))))
        }
        if let m = matches("(\\d+) equalities and (\\d+) memberships judged across (\\d+) uses",
                           said).first {
            size["equalities"] = (size["equalities"] ?? 0) + (Int(m[0]) ?? 0)
            size["memberships"] = (size["memberships"] ?? 0) + (Int(m[1]) ?? 0)
            size["uses"] = (size["uses"] ?? 0) + (Int(m[2]) ?? 0)
        }
    }
    try? FileManager.default.removeItem(atPath: tmp)
    return bad
}

func policyPathOf(_ w: WorldState) -> String? {
    guard let f = w.facts else { return nil }
    let p = ((absPath(f) as NSString).deletingLastPathComponent as NSString)
        .appendingPathComponent("gate.policy.swift")
    return FileManager.default.fileExists(atPath: p) ? p : nil
}

func policyGuards(_ w: WorldState) -> [(address: String, claim: String)] {
    // the policy file is not in the judged list, so status guards it: every
    // Person an identity names is declared by the world, every Requires is a
    // name something this world reads declares
    guard let pp = policyPathOf(w) else { return [] }
    let text = readText(pp) ?? ""
    var ids: [(mail: String, who: String)] = []
    var rules: [(action: String, rank: String)] = []
    var whereAt: [String: (String, Int)] = [:]
    let name = (pp as NSString).lastPathComponent
    for (m, at) in matchesAt("(?:public\\s+)?enum\\s+(\\w+)\\s*:[^{\\n]*\\bIdentity\\b[^{\\n]*"
                             + "\\{(.*?)\\n\\}", text, dotAll: true) {
        guard let who = matches("typealias\\s+Person\\s*=\\s*(\\w+)", m[1]).first?.first,
              let mail = matches("extension\\s+" + m[0] + "\\b.*?typeName.*?\"([^\"]+)\"",
                                 text, dotAll: true).first?.first else { continue }
        if let i = ids.firstIndex(where: { $0.mail == mail }) { ids[i] = (mail, who) }
        else { ids.append((mail, who)) }
        whereAt[mail] = (name, at)
    }
    for (m, at) in matchesAt("(?:public\\s+)?enum\\s+(\\w+)Policy\\s*\\{(.*?)\\n\\}",
                             text, dotAll: true) {
        guard let req = matches("typealias\\s+Requires\\s*=\\s*(\\w+)", m[1]).first?.first
        else { continue }
        let action = m[0].lowercased()
        if let i = rules.firstIndex(where: { $0.action == action }) { rules[i] = (action, req) }
        else { rules.append((action, req)) }
        whereAt["policy:" + action] = (name, at)
    }
    let people = worldPeopleOf(w)
    var declared = people
    let base = layoutDir(w) ?? "."
    for r in w.layout?.rows ?? [] where r.role == "forms" {
        let p = (base as NSString).appendingPathComponent(r.path)
        guard FileManager.default.fileExists(atPath: p), let t = readText(p) else { continue }
        for m in matches("(?:public\\s+)?enum\\s+(\\w+)\\s*:", t) { declared.insert(m[0]) }
    }
    for shelfName in SHELF_ORDER {
        for m in matches("(?:public\\s+)?enum\\s+(\\w+)\\s*:", STDLIB_TEXTS[shelfName] ?? "") {
            declared.insert(m[0])
        }
    }
    var bad: [(address: String, claim: String)] = []
    for (mail, who) in ids where !people.contains(who) {
        let (f, ln) = whereAt[mail] ?? (name, 1)
        bad.append(("\(f):\(ln)",
                    "an identity names `\(who)`, and the world declares no such person"))
    }
    for (action, rank) in rules {
        let (f, ln) = whereAt["policy:" + action] ?? (name, 1)
        if matchAt(rank, "[A-Z]\\w*$") == nil {
            bad.append(("\(f):\(ln)",
                        "the \(action) policy requires `\(rank)`, which is not a name"))
        } else if !declared.isEmpty && !declared.contains(rank) {
            bad.append(("\(f):\(ln)",
                        "the \(action) policy requires `\(rank)`, and nothing this world "
                      + "reads declares it. A policy naming a rank nobody has is a "
                      + "policy that can never be met"))
        }
    }
    return bad
}

let SHELF_SPEAKS = ["a-domain", "the-tool", "the-bench", "the-reader"]

func shelfHeadLine(_ name: String, _ label: String) -> String? {
    for line in (STDLIB_TEXTS[name] ?? "").components(separatedBy: "\n").prefix(4) {
        if let m = matchAt(line.trimmingCharacters(in: .whitespaces), label + " (.+)") {
            return m[1].trimmingCharacters(in: .whitespaces)
        }
    }
    return nil
}

func stdlibGuards(_ w: WorldState) -> [(address: String, claim: String)] {
    // a printout that no longer matches what it prints, and a shelf page that
    // does not say what it is or whose voice it speaks in
    guard let f = w.facts else { return [] }
    let d = (absPath(f) as NSString).deletingLastPathComponent
    var bad: [(address: String, claim: String)] = []
    for name in SHELF_ORDER where shelfHeadLine(name, "// role:") == nil {
        bad.append(("stdlib/\(name).swift:2",
                    "this page does not say what it is. A shelf file states its own "
                  + "role in its second line: `// role: forms` for what an operator "
                  + "speaks, `// role: gate's own` for this tool's furniture, and "
                  + "one that says nothing cannot be placed"))
    }
    for name in SHELF_ORDER {
        guard let said = shelfHeadLine(name, "// speaks-for:") else {
            bad.append(("stdlib/\(name).swift:3",
                        "this page does not say whose voice it speaks in. A shelf file "
                      + "states its sort in its third line, beside its role: "
                      + "`// speaks-for: a-domain` for the words a world of yours is "
                      + "written in, `the-tool` for what this tool's own verbs and "
                      + "courts are written in, `the-bench` for the page you read them "
                      + "on, `the-reader` for what a repository is met with"))
            continue
        }
        if !SHELF_SPEAKS.contains(said) {
            bad.append(("stdlib/\(name).swift:3",
                        "`\(said)` is not a sort of the shelf: this page names a group "
                      + "nobody declared, and the reader it was written for would look "
                      + "for it and find nothing. It is one of "
                      + SHELF_SPEAKS.joined(separator: " · ")
                      + ", and the list is closed so that what "
                      + "taking this tool puts on a repository stays a list somebody "
                      + "can read to the end"))
        }
    }
    for name in SHELF_ORDER {
        let p = (d as NSString).appendingPathComponent(name + ".swift")
        guard FileManager.default.fileExists(atPath: p), let text = readText(p) else { continue }
        if text.hasPrefix("// gate stdlib") && text != (STDLIB_TEXTS[name] ?? "") {
            bad.append(("\(name).swift",
                        "this printout no longer matches the words the judge carries, and "
                      + "still says it does. Editing it adds no word to the language: print "
                      + "it again, or drop the header so it stops claiming to be the printout"))
        }
    }
    return bad
}

func gateShapeGuards(_ w: WorldState) -> [(address: String, claim: String)] {
    // a gated conformance written on one line is read by no court, in either
    // carrier of the court: refused rather than left quietly unjudged
    var bad: [(address: String, claim: String)] = []
    guard let layout = w.layout else { return bad }
    let d = (layout.manifest as NSString).deletingLastPathComponent
    for r in layout.rows where r.role == "forms" {
        let path = (d as NSString).appendingPathComponent(r.path)
        guard FileManager.default.fileExists(atPath: path), let text = readText(path)
        else { continue }
        for (i0, line) in text.components(separatedBy: "\n").enumerated() {
            if !matches("^\\s*(?:public )?extension\\s+\\w+\\s*:\\s*\\w+\\b.*\\bwhere\\b.*"
                        + "\\{\\s*\\}\\s*$", line).isEmpty {
                bad.append(("\(r.path):\(i0 + 1)",
                            "a gated conformance written on one line is read by no court: "
                          + "break the line before `where` and the law is judged again. "
                          + "Left as it is, every certificate over it holds without "
                          + "being checked"))
            }
        }
    }
    return bad
}

func ownSurfaceGuards(_ w: WorldState) -> [(address: String, claim: String)] {
    // the table of verbs and the dispatch, held to each other by name: the
    // dispatch is still the python side's, so its file is the one read
    guard let layout = w.layout else { return [] }
    let d = (layout.manifest as NSString).deletingLastPathComponent
    let rows = layout.rows.filter { $0.role == "forms"
        && SHIPPED_SET.contains(absPath((d as NSString).appendingPathComponent($0.path)))
        && ($0.path as NSString).lastPathComponent == "verbs.swift" }
    guard let first = rows.first else { return [] }
    let name = first.path
    let text = readText((d as NSString).appendingPathComponent(name)) ?? ""
    var said: [String: String] = [:]
    var at: [String: Int] = [:]
    for (i0, line) in text.components(separatedBy: "\n").enumerated() {
        guard let m = matchAt(line.trimmingCharacters(in: .whitespaces),
                              "public enum (\\w+): (Verb|Spelling) \\{") else { continue }
        if let spelt = matches("extension " + m[1] + " \\{ public static var typeName: "
                               + "String \\{ \"([^\"]+)\" \\} \\}", text).first {
            said[spelt[0]] = m[1]
            at[spelt[0]] = i0 + 1
        }
    }
    let src = readText(root.appendingPathComponent("gate").path) ?? ""
    var verbs = Set(matches("cmd\\s*==\\s*\"([a-z-]+)\"", src).map { $0[0] })
    for grp in matches("cmd\\s+in\\s+\\(([^)]*)\\)", src) {
        for m in matches("\"([a-z-]+)\"", grp[0]) { verbs.insert(m[0]) }
    }
    for grp in matches("args\\[0\\]\\s+in\\s+\\(([^)]*)\\)", src) {
        for m in matches("\"([a-z-]+)\"", grp[0]) {
            verbs.insert(String(m[0].drop(while: { $0 == "-" })))
        }
    }
    var bad: [(address: String, claim: String)] = []
    for word in Set(said.keys).subtracting(verbs).sorted() {
        bad.append(("\(name):\(at[word]!)",
                    "`gate \(word)` is a record here and no word the dispatch answers to: "
                  + "a promise this tool no longer keeps"))
    }
    for word in verbs.subtracting(said.keys).sorted() {
        bad.append((name,
                    "`gate \(word)` is a word this tool answers to and no record here says "
                  + "so: a verb nobody is told about"))
    }
    return bad
}

let BENCH_VIEWS = ["full", "bare", "table"]

func personalPathOf(_ w: WorldState) -> String? {
    guard let f = w.facts else { return nil }
    let proot = ProcessInfo.processInfo.environment["GATE_ME"]
        ?? (NSHomeDirectory() as NSString).appendingPathComponent(".gate/me")
    let base = (absPath(f) as NSString).deletingLastPathComponent
    return (((proot as NSString).appendingPathComponent("worlds") as NSString)
        .appendingPathComponent(repoKey(base)) as NSString).appendingPathComponent("my.swift")
}

func benchFilesOf(_ w: WorldState) -> [(String, String)] {
    // the shared world, its forms, the layout, the policy and the personal
    // slot: the list the panel opens, and the list the stream guards walk
    guard let f = w.facts else { return [] }
    let base = (absPath(f) as NSString).deletingLastPathComponent
    var out: [(String, String)] = worldFilesOf(w).map { (relPath($0, base), $0) }
    for r in w.layout?.rows ?? [] where r.role == "forms" {
        let p = (base as NSString).appendingPathComponent(r.path)
        if FileManager.default.fileExists(atPath: p),
           !out.contains(where: { $0.0 == r.path && $0.1 == p }) {
            out.append((r.path, p))
        }
    }
    if let l = w.layout, FileManager.default.fileExists(atPath: l.manifest) {
        out.append((relPath(l.manifest, base), l.manifest))
    }
    if let pp = policyPathOf(w) {
        let rel = relPath(pp, base)
        if !out.contains(where: { $0.0 == rel }) { out.append((rel, pp)) }
    }
    if let pf = personalPathOf(w) {
        let name = out.contains(where: { $0.0 == "my.swift" }) ? "personal-my.swift" : "my.swift"
        out.append((name, pf))
    }
    return out
}

func opensAs(_ w: WorldState, _ path: String) -> (view: String?, said: String?) {
    let base = w.facts.map { (absPath($0) as NSString).deletingLastPathComponent }
        ?? FileManager.default.currentDirectoryPath
    for r in w.layout?.rows ?? [] {
        if absPath((base as NSString).appendingPathComponent(r.path)) == absPath(path),
           let opens = r.opens, !opens.isEmpty {
            let said = opens.lowercased()
            return (BENCH_VIEWS.contains(said) ? said : nil, said)
        }
    }
    guard let data = FileManager.default.contents(atPath: path) else { return (nil, nil) }
    let head = String(decoding: data.prefix(2000), as: UTF8.self)
    for line in head.components(separatedBy: "\n").prefix(6) {
        if let m = matchAt(line.trimmingCharacters(in: .whitespaces), "//\\s*opens:\\s*(\\S+)") {
            let said = m[1].trimmingCharacters(in: .whitespaces).lowercased()
            return (BENCH_VIEWS.contains(said) ? said : nil, said)
        }
    }
    return (nil, nil)
}

func opensGuards(_ w: WorldState) -> [(address: String, claim: String)] {
    var bad: [(address: String, claim: String)] = []
    for (name, path) in benchFilesOf(w) {
        guard FileManager.default.fileExists(atPath: path) else { continue }
        let (view, said) = opensAs(w, path)
        if let said = said, view == nil {
            bad.append((name,
                        "`\(said)` is not a view: this file says how it should first be "
                      + "met and names something the bench cannot open. It is one of "
                      + BENCH_VIEWS.joined(separator: " · ")))
        }
    }
    return bad
}

func sha256Hex(_ data: Data) -> String {
    // SHA-256, written out for the same reason SHA-1 above is: the vendored
    // judge states its digest and somebody has to be able to check it
    let k: [UInt32] = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
        0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
        0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
        0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
        0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
        0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]
    var h: [UInt32] = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
                       0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
    var message = [UInt8](data)
    let bits = UInt64(message.count) * 8
    message.append(0x80)
    while message.count % 64 != 56 { message.append(0) }
    for i in (0..<8).reversed() { message.append(UInt8((bits >> (UInt64(i) * 8)) & 0xFF)) }
    func rot(_ x: UInt32, _ n: UInt32) -> UInt32 { return (x >> n) | (x << (32 - n)) }
    for chunk in stride(from: 0, to: message.count, by: 64) {
        var w = [UInt32](repeating: 0, count: 64)
        for i in 0..<16 {
            let o = chunk + i * 4
            w[i] = (UInt32(message[o]) << 24) | (UInt32(message[o + 1]) << 16)
                 | (UInt32(message[o + 2]) << 8) | UInt32(message[o + 3])
        }
        for i in 16..<64 {
            let s0 = rot(w[i - 15], 7) ^ rot(w[i - 15], 18) ^ (w[i - 15] >> 3)
            let s1 = rot(w[i - 2], 17) ^ rot(w[i - 2], 19) ^ (w[i - 2] >> 10)
            w[i] = w[i - 16] &+ s0 &+ w[i - 7] &+ s1
        }
        var a = h[0], b = h[1], c = h[2], d = h[3]
        var e = h[4], f = h[5], g = h[6], hh = h[7]
        for i in 0..<64 {
            let s1 = rot(e, 6) ^ rot(e, 11) ^ rot(e, 25)
            let ch = (e & f) ^ (~e & g)
            let t1 = hh &+ s1 &+ ch &+ k[i] &+ w[i]
            let s0 = rot(a, 2) ^ rot(a, 13) ^ rot(a, 22)
            let mj = (a & b) ^ (a & c) ^ (b & c)
            let t2 = s0 &+ mj
            hh = g; g = f; f = e; e = d &+ t1
            d = c; c = b; b = a; a = t1 &+ t2
        }
        h[0] = h[0] &+ a; h[1] = h[1] &+ b; h[2] = h[2] &+ c; h[3] = h[3] &+ d
        h[4] = h[4] &+ e; h[5] = h[5] &+ f; h[6] = h[6] &+ g; h[7] = h[7] &+ hh
    }
    return h.map { String(format: "%08x", $0) }.joined()
}

func binaryRuns(_ p: String) -> Bool {
    // runnable is tested by running: bytes say nothing about which platform a
    // judge was built for, so the one question with an answer is asked once
    guard FileManager.default.fileExists(atPath: p) else { return false }
    let proc = Process()
    proc.executableURL = URL(fileURLWithPath: p)
    proc.arguments = ["judge"]
    proc.standardOutput = Pipe()
    proc.standardError = Pipe()
    do { try proc.run() } catch { return false }
    proc.waitUntilExit()
    return true
}

func vendoredGuards(_ w: WorldState) -> [(address: String, claim: String)] {
    // .gate/ is a materialized shelf like any other: the judge it carries must
    // be the judge it says it carries, and a digest says nothing about running
    guard let f = w.facts else { return [] }
    let d = (absPath(f) as NSString).deletingLastPathComponent
    let readme = ((d as NSString).appendingPathComponent(".gate") as NSString)
        .appendingPathComponent("README.md")
    let binp = (((d as NSString).appendingPathComponent(".gate") as NSString)
        .appendingPathComponent("bin") as NSString).appendingPathComponent("gate-judge")
    guard FileManager.default.fileExists(atPath: readme),
          FileManager.default.fileExists(atPath: binp),
          let stated = matches("judge sha256: ([0-9a-f]{64})", readText(readme) ?? "").first
    else { return [] }
    let actual = sha256Hex(FileManager.default.contents(atPath: binp) ?? Data())
    if actual != stated[0] {
        return [(".gate/README.md",
                 "the carried judge is not the judge this repository states: "
               + "sha256 \(actual.prefix(12)) against \(stated[0].prefix(12)). "
               + "Re-run `gate init . --vendor`, or state the one you mean")]
    }
    if !binaryRuns(binp) {
        return [(".gate/bin/gate-judge",
                 "the carried judge matches its recorded digest and does not run on "
               + "this machine: it was built for another platform. The port serves "
               + "the plain court where node is installed, and `bin/build-judge.sh` "
               + "builds a judge that runs here")]
    }
    return []
}

func judgeFrom() -> String? {
    let p = root.appendingPathComponent("bin").appendingPathComponent("gate-judge.from").path
    let said = (readText(p) ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
    return said.isEmpty ? nil : said
}

func takenJudgeGuard(_ w: WorldState) -> [(address: String, claim: String)] {
    // the one row this whole document exists to keep honest: the revision the
    // world says it took the judge at, against the one the judge was built from
    guard let layout = w.layout,
          let claimed = layout.rows.first(where: { $0.role == "judge" })?.from else { return [] }
    let man = (layout.manifest as NSString).lastPathComponent
    guard let built = judgeFrom() else {
        return [(man,
                 "this world says it took the judge at `\(claimed)`, and the judge "
               + "beside it records no revision at all. `bin/build-judge.sh` writes "
               + "one down, and until it does the row answers for nothing")]
    }
    let said = claimed.components(separatedBy: "@").last ?? claimed
    if !(built.hasPrefix(said) || said.hasPrefix(built)) {
        return [(man,
                 "this world says it took the judge at `\(said)`, and the judge beside "
               + "it was built from `\(built.prefix(12))` — one of the two is out of date, "
               + "and a row that names the court may not disagree with the court")]
    }
    return []
}

let CODEOWNERS_HEADER = "// printed by gate import codeowners: who owns what in this repository,\n"
    + "// written in the grants vocabulary (`gate stdlib show forms-grants`). A zone is\n"
    + "// a top of the tree, a room is a pattern, and an owner keeps a zone: owning\n"
    + "// is entry whose key administers, judged like any other claim.\n//\n"

func readCodeowners(_ path: String) -> [(line: Int, pattern: String, owners: [String])] {
    var rules: [(Int, String, [String])] = []
    for (n0, raw) in (readText(path) ?? "").components(separatedBy: "\n").enumerated() {
        let line = raw.components(separatedBy: "#")[0].trimmingCharacters(in: .whitespaces)
        if line.isEmpty { continue }
        // a space in a path is escaped as `\ `, and the split happens on the
        // spaces that are not
        let parts = line.replacingOccurrences(of: "\\ ", with: "\u{0}")
            .components(separatedBy: .whitespaces).filter { !$0.isEmpty }
            .map { $0.replacingOccurrences(of: "\u{0}", with: " ") }
        let owners = parts.dropFirst().filter { $0.hasPrefix("@") || $0.contains("@") }
        if !owners.isEmpty { rules.append((n0 + 1, parts[0], Array(owners))) }
    }
    return rules
}

func readOwnersPolicy(_ path: String) -> [(owner: String, zone: String)] {
    // owner,zone pairs, first spelling of an owner wins. The other carrier
    // reads this through csv; the two files this guard meets are plain columns
    var rows = (readText(path) ?? "").components(separatedBy: "\n")
        .filter { !$0.trimmingCharacters(in: .whitespaces).isEmpty }
    guard !rows.isEmpty else { return [] }
    let head = rows.removeFirst().components(separatedBy: ",")
        .map { $0.trimmingCharacters(in: .whitespaces) }
    guard let oi = head.firstIndex(of: "owner"), let zi = head.firstIndex(of: "zone")
    else { return [] }
    var out: [(String, String)] = []
    for row in rows {
        let cells = row.components(separatedBy: ",")
        guard cells.count > max(oi, zi) else { continue }
        let owner = String(cells[oi].drop(while: { $0 == "@" }))
        if !out.contains(where: { $0.0 == owner }) { out.append((owner, cells[zi])) }
    }
    return out
}

func codeownersZone(_ pattern: String) -> String {
    let p = String(pattern.trimmingCharacters(in: .whitespaces).drop(while: { $0 == "/" }))
    if p.isEmpty || p.hasPrefix("*") { return "Root" }
    let z = sanitized(p.components(separatedBy: "/")[0])
    return z.isEmpty ? "Root" : z
}

func codeownersWorldLines(_ src: String, _ policy: [(owner: String, zone: String)],
                          _ saidFrom: String) -> (lines: [String], srcmap: [String: String]) {
    // one translator, whoever asks: the import prints a world with this, and
    // the pair guard prints the same world again to compare
    let rules = readCodeowners(src)
    var zones = Set(rules.map { codeownersZone($0.pattern) })
    for (_, z) in policy { zones.insert(sanitized(z)) }
    var lines = [CODEOWNERS_HEADER + "// from: " + saidFrom + "\n//\n"
                 + (STDLIB_TEXTS["forms-grants"] ?? ""), ""]
    for z in zones.sorted() { lines.append("public enum Zone_\(z): Realm {}") }
    lines.append("")
    var keepers = Set<String>()
    var srcmap: [String: String] = [:]
    for (i, r) in rules.enumerated() {
        let zone = codeownersZone(r.pattern)
        let room = "Path_\(i)_" + String(sanitized(r.pattern).prefix(40))
        lines.append("public enum \(room): Room {")
        lines.append("    public typealias Place = Zone_\(zone)")
        lines.append("}")
        for owner in r.owners {
            let plain = String(owner.drop(while: { $0 == "@" }))
            let kept = policy.first(where: { $0.owner == plain })?.zone
            let keeper = kept != nil ? "Owner_\(sanitized(plain))"
                                     : "Owner_\(sanitized(plain))_in_\(zone)"
            if !keepers.contains(keeper) {
                keepers.insert(keeper)
                lines.append("public enum \(keeper): Keeper {")
                lines.append("    public typealias Post = Zone_\(kept.map(sanitized) ?? zone)")
                lines.append("    public typealias Key = WardenKey")
                lines.append("}")
            }
            let cert = "Owns_\(i)_\(sanitized(plain))"
            lines.append("public typealias \(cert) = Owns<\(keeper), \(room)>")
            srcmap[cert] = "\((src as NSString).lastPathComponent):\(r.line) · \(r.pattern) \(owner)"
        }
    }
    return (lines, srcmap)
}

func codeownersPairGuards(_ w: WorldState) -> [(address: String, claim: String)] {
    // the print and its source are a pair: the same translator prints the
    // world again, and the certificates are compared, refusals at the line
    // that makes them
    guard let f = w.facts else { return [] }
    var judged = Set(worldFilesOf(w))
    judged.insert(absPath(f))
    if let l = w.layout {
        let mdir = (l.manifest as NSString).deletingLastPathComponent
        for r in l.rows { judged.insert((mdir as NSString).appendingPathComponent(r.path)) }
    }
    var out: [(address: String, claim: String)] = []
    for path in judged.sorted() where FileManager.default.fileExists(atPath: path) {
        // a declared row may be a binary, and a binary is nobody's half of a
        // printed pair: strict utf-8 here, the way the other carrier reads it
        guard let data = FileManager.default.contents(atPath: path),
              let text = String(data: data, encoding: .utf8),
              text.contains("printed by gate import codeowners"),
              let m = matchesAt("^// from: (\\S+)(?: --policy (\\S+))?$", text, lines: true)
                  .first?.groups
        else { continue }
        let name = (path as NSString).lastPathComponent
        let srcp = ((absPath(path) as NSString).deletingLastPathComponent as NSString)
            .appendingPathComponent(m[0])
        if !FileManager.default.fileExists(atPath: srcp) {
            out.append(("\(name):1",
                        "printed from \(m[0]), and no file of that name is here now"))
            continue
        }
        let policy = m[1].isEmpty ? []
            : readOwnersPolicy(((absPath(path) as NSString).deletingLastPathComponent as NSString)
                .appendingPathComponent(m[1]))
        let (lines, srcmap) = codeownersWorldLines(srcp, policy, "")
        let fresh = Set(lines.filter { $0.hasPrefix("public typealias Owns_") })
        let disk = text.components(separatedBy: "\n")
        let held = Set(disk.filter { $0.hasPrefix("public typealias Owns_") })
        for lost in fresh.subtracting(held).sorted() {
            let cert = lost.components(separatedBy: .whitespaces).filter { !$0.isEmpty }[2]
            let mapped = (srcmap[cert] ?? "").components(separatedBy: " · ")[0]
            let spot = mapped.isEmpty ? "\(m[0]):1" : mapped
            out.append((spot,
                        "\(m[0]) writes this rule, and the world does not "
                      + "hold it: `\(lost)`. Run the import again, or take the rule out"))
        }
        for extra in held.subtracting(fresh).sorted() {
            out.append(("\(name):\((disk.firstIndex(of: extra) ?? 0) + 1)",
                        "the world holds this claim, and \(m[0]) no longer "
                      + "writes it: `\(extra)`. Run the import again, or put the "
                      + "line back"))
        }
    }
    return out
}

func judgedRefusals(_ out: String) -> [(address: String, claim: String)] {
    // the plain verdict has one reader, here as on the other carrier
    return matches("^\\s+(\\S+\\.swift:\\d+)\\s+(.+)$", out, lines: true)
        .filter { $0.count == 2 }
        .map { ($0[0], $0[1].trimmingCharacters(in: .whitespaces)) }
}

func locateClaim(_ text: String, _ claim: String) -> Int? {
    // the line where this text actually makes this claim: one entry at a time,
    // every party inside THAT entry, and the argument the claim turns on
    let names = findAll("\\b[A-Z]\\w*", claim)
    guard let form = names.first else { return nil }
    let parties = matches("\\b([A-Z]\\w*)\\.\\w+", claim).map { $0[0] }
    let wanted = matches("==\\s*([A-Z]\\w*)", claim).first?.first
    let inside = parties + (wanted.map { [$0] } ?? [])
    let lines = text.components(separatedBy: "\n")
    for (i, ln) in lines.enumerated() {
        let f = NSRegularExpression.escapedPattern(for: form)
        if matches("\\b" + f + "\\b", ln).isEmpty { continue }
        var end = i
        while end < min(lines.count, i + 10), !lines[end].contains(">") { end += 1 }
        let entry = Array(lines[i..<min(end + 1, lines.count)])
        let joined = entry.joined(separator: "\n")
        let all = inside.allSatisfy {
            !matches("\\b" + NSRegularExpression.escapedPattern(for: $0) + "\\b", joined).isEmpty
        }
        if !all { continue }
        let want = parties.first ?? form
        for (k, line) in entry.enumerated() {
            if !matches("\\b" + NSRegularExpression.escapedPattern(for: want) + "\\b",
                        line).isEmpty {
                return i + k + 1
            }
        }
        return i + 1
    }
    return nil
}

func attributeRefusals(_ refusals: [(address: String, claim: String)],
                       _ sources: [(String, String)]) -> [(address: String, claim: String)] {
    // a refusal belongs to the file that makes the claim: the judge repeats
    // one per file it was given, and the broadcast copies are dropped
    var first: [String: (address: String, claim: String)] = [:]
    var order: [String] = []
    for r in refusals where first[r.claim] == nil {
        first[r.claim] = r
        order.append(r.claim)
    }
    var out: [(address: String, claim: String)] = []
    for claim in order {
        let orig = first[claim]!
        let ofile = orig.address.components(separatedBy: ":")[0]
        let otail = orig.address.components(separatedBy: ":").dropFirst().first ?? ""
        let oline = Int(otail)
        if !claim.contains(" requires ") {
            out.append(orig)
            continue
        }
        var placed = false
        for (name, text) in sources {
            guard var line = locateClaim(text, claim) else { continue }
            if name == ofile, let ol = oline {
                line = abs(line - ol) <= 8 ? line : ol
            }
            out.append(("\(name):\(line)", claim))
            placed = true
        }
        if !placed { out.append(orig) }
    }
    return out
}

func nextRung(_ w: WorldState, _ refused: Bool) -> String {
    // ONE next step, chosen by what the repository already has: each rung
    // names what becomes yours once the step is taken, and a rung already
    // taken is not offered
    if refused {
        return "open the address above, or run `gate serve` and watch the verdict move as you type"
    }
    let rootDir = w.facts.map { (absPath($0) as NSString).deletingLastPathComponent } ?? "."
    let hooked = runGit(["config", "--get", "core.hooksPath"], rootDir)
        .trimmingCharacters(in: .whitespacesAndNewlines)
    if hooked.isEmpty {
        return "run `gate init .` to wire the hook: from here on, what you commit is what holds"
    }
    let rows = (w.layout?.rows ?? []).filter { !$0.path.isEmpty }
    let saidSomething = w.facts.map { FileManager.default.fileExists(atPath: $0) } ?? false
    func arrivedByTaking(_ rel: String) -> Bool {
        let p = (rootDir as NSString).appendingPathComponent(rel)
        return (readText(p) ?? "").contains("Origin: gate's shelf")
    }
    if !rows.isEmpty && !saidSomething && rows.allSatisfy({ arrivedByTaking($0.path) })
        && rows.contains(where: { ($0.path as NSString).lastPathComponent == "readme.swift" }) {
        return "gate serve"
    }
    if policyPathOf(w) == nil {
        return "say who may merge: gate.policy.swift"
    }
    let ci = ((rootDir as NSString).appendingPathComponent(".github") as NSString)
        .appendingPathComponent("workflows")
    var isDir: ObjCBool = false
    if !(FileManager.default.fileExists(atPath: ci, isDirectory: &isDir) && isDir.boolValue) {
        return "put `gate status` in the CI you already run: from then on nobody reads a diff "
             + "to know the claims still hold"
    }
    return "run `gate serve` for the bench: your world on the left, the verdict on the right, "
         + "and a page of your own beside them"
}

// python's json.dumps(..., ensure_ascii=False, indent=2), for the one answer
// this door prints: keys in the order they were said, non-ascii kept
indirect enum StatusJSON {
    case text(String), raw(String), null
    case list([StatusJSON])
    case object([(String, StatusJSON)])
}

func statusDumps(_ v: StatusJSON, _ depth: Int) -> String {
    let pad = String(repeating: " ", count: (depth + 1) * 2)
    let close = String(repeating: " ", count: depth * 2)
    switch v {
    case .text(let s): return jsonString(s)
    case .raw(let r): return r
    case .null: return "null"
    case .list(let items):
        if items.isEmpty { return "[]" }
        return "[\n" + items.map { pad + statusDumps($0, depth + 1) }.joined(separator: ",\n")
             + "\n" + close + "]"
    case .object(let pairs):
        if pairs.isEmpty { return "{}" }
        return "{\n" + pairs.map { pad + jsonString($0.0) + ": " + statusDumps($0.1, depth + 1) }
            .joined(separator: ",\n") + "\n" + close + "}"
    }
}

func floatRepr(_ s: String) -> String {
    // the other carrier prints float(times[-1]): the shortest spelling that
    // round-trips, which is also what Swift's description prints
    guard let d = Double(s) else { return s }
    return String(d)
}

// ── THE TABLES BOOTSTRAP, the one thing that stood between this vein and the
// verbs that ask about a world. The other carrier runs it in its dispatcher
// before `status`, and the strangler's door hands an argv over ABOVE that line,
// so a carried verb never reached it: in a repository holding tables and no
// world yet, one carrier seeded the world and the other did not. It is not a
// verb and it does not go on the ledger. It is a precondition, and it is here so
// that the verb standing on it can move.
//
// Seeded ONCE, and never again: from then on the world is the source, and fresh
// tables come in through an explicit `gate import`. That is the whole reason
// this is three lines of condition and not a sync.
func csvRows(_ text: String) -> [[String]] {
    // read the way the other carrier's csv module reads: a quote protects commas
    // and newlines, a doubled quote inside a quoted field is one quote, and a
    // blank line is an empty row rather than a row of one empty field
    var rows: [[String]] = [], row: [String] = [], field = ""
    var quoted = false, started = false
    var i = text.startIndex
    while i < text.endIndex {
        let c = text[i]
        if quoted {
            if c == "\"" {
                let n = text.index(after: i)
                if n < text.endIndex, text[n] == "\"" { field.append("\""); i = n }
                else { quoted = false }
            } else { field.append(c) }
        } else if c == "\"" {
            quoted = true; started = true
        } else if c == "," {
            row.append(field); field = ""; started = true
        } else if c == "\n" || c == "\r" {
            let n = text.index(after: i)
            if c == "\r", n < text.endIndex, text[n] == "\n" { i = n }
            if started || !field.isEmpty { row.append(field) }
            rows.append(row)
            row = []; field = ""; started = false
        } else { field.append(c); started = true }
        i = text.index(after: i)
    }
    if started || !field.isEmpty { row.append(field); rows.append(row) }
    return rows
}

struct CsvTable {
    var header: [String] = []
    var rows: [[String]] = []       // the header's row is not among these
    func has(_ key: String) -> Bool { header.contains(key) }
    // a row shorter than the header leaves the rest unfilled, and the other
    // carrier's reader fills those with None, which prints as `None`
    func at(_ r: Int, _ key: String) -> String? {
        guard let i = header.firstIndex(of: key), r < rows.count else { return nil }
        return i < rows[r].count ? rows[r][i] : nil
    }
    func text(_ r: Int, _ key: String) -> String { at(r, key) ?? "None" }
}

func csvTable(_ path: String, _ what: String) -> CsvTable {
    var all = csvRows(theirsText(path, what))
    all.removeAll { $0.isEmpty }            // the reader skips an empty row
    guard let head = all.first else { return CsvTable() }
    return CsvTable(header: head, rows: Array(all.dropFirst()))
}

func seededWorld(_ peoplePath: String, _ grantsPath: String) -> String {
    let people = csvTable(peoplePath, "the people this world is seeded from")
    let grants = csvTable(grantsPath, "the grants this world is seeded from")
    // ── AND A TABLE MISSING A COLUMN IS SAID, NOT RAISED. The other carrier
    // reads `row['rank']` straight, so a table without that column meets a
    // person with a KeyError and a stack trace, inside the one command they ran
    // to look at their repository. A column is a name this reader can check.
    for (table, path, need) in [(people, peoplePath, ["id", "rank", "home", "given",
                                                      "family", "born", "site"]),
                                (grants, grantsPath, ["who", "doc"])] {
        let missing = need.filter { !table.has($0) }
        if !table.header.isEmpty && !missing.isEmpty {
            cannot((path as NSString).lastPathComponent + " has no column named "
                   + missing.map { "`\($0)`" }.joined(separator: ", ")
                   + ", and the world is seeded from those",
                   "the header line names the columns: "
                   + need.joined(separator: ", ") + " for people, who, doc for grants")
        }
    }
    var lines: [String] = []
    func emit(_ chunk: String) { lines += chunk.components(separatedBy: "\n") }
    emit("// the facts world, yours: the source you read and edit, and the")
    emit("// one this tool answers for. Not a generated artifact. The tables")
    emit("// only seeded it once, below, and from here the world is what is")
    emit("// edited and judged. A gate.manifest.swift may split it across")
    emit("// several files, all judged together. git carries the history.")
    emit("//")
    emit("// seeded by gate import from: \((peoplePath as NSString).lastPathComponent), "
         + "\((grantsPath as NSString).lastPathComponent)")
    emit("//")
    emit("// the language it is written in: `gate stdlib show forms-organization`.")
    emit("// Those words are carried by the judge, and `materialize` writes them out")
    emit("// beside this file to read: editing that copy adds no word to the language.")
    // the atom pools: distinct values from the data, each ring closed in a circle
    func ring(_ names: [String], _ conf: String, _ extra: [String: String]? = nil) {
        var seen = Set<String>(), order: [String] = []
        for n in names where !seen.contains(n) { seen.insert(n); order.append(n) }
        for (i, n) in order.enumerated() {
            let next = order[(i + 1) % order.count]
            var body = "    public typealias Next = \(next)\n"
            if let extra = extra { body += "    public typealias Sex = \(extra[n] ?? "None")\n" }
            emit("\npublic enum \(n): \(conf) {\n\(body)}")
        }
    }
    var sexes: [String: String] = [:]
    for r in people.rows.indices {
        sexes[people.text(r, "given")] = people.has("sex") ? people.text(r, "sex") : "Male"
    }
    ring(people.rows.indices.map { people.text($0, "given") }, "GivenNameCycle", sexes)
    ring(people.rows.indices.map { people.text($0, "family") }, "FamilyNameCycle")
    ring(people.rows.indices.map { people.text($0, "born") }, "BirthYearCycle")
    for r in people.rows.indices {
        emit("\npublic enum \(people.text(r, "id")): Employee, Person {\n"
             + "    public typealias Rank = \(people.text(r, "rank"))\n"
             + "    public typealias Home = \(people.text(r, "home"))\n"
             + "    public typealias Given = \(people.text(r, "given"))\n"
             + "    public typealias Family = \(people.text(r, "family"))\n"
             + "    public typealias Born = \(people.text(r, "born"))\n"
             + "    public typealias Site = \(people.text(r, "site"))\n"
             + "    public typealias Sex = Given.Sex\n}")
    }
    emit("\npublic enum ImportedTeam: Team {\n    @StructureBuilder\n"
         + "    public static var body: some Structure {")
    for r in people.rows.indices {
        let id = people.text(r, "id")
        emit("        VerifiedInDepartment<\n            \(id),\n"
             + "            \(people.text(r, "home"))\n        >.self")
        emit("        VerifiedAtRank<\n            \(id),\n"
             + "            \(people.text(r, "rank"))\n        >.self")
        emit("        VerifiedAtWorkplace<\n            \(id),\n"
             + "            \(people.text(r, "site"))\n        >.self")
    }
    emit("    }\n}")
    emit("\npublic enum ImportedAccesses: AccessLedger {\n    @StructureBuilder\n"
         + "    public static var body: some Structure {")
    for r in grants.rows.indices {
        emit("            VerifiedView<\n                \(grants.text(r, "who")),\n"
             + "                \(grants.text(r, "doc"))\n            >.self")
    }
    emit("    }\n}")
    return lines.joined(separator: "\n") + "\n"
}

@discardableResult
func ensureWorld(_ w: WorldState) -> Bool {
    // bootstrap only: tables present and no world yet. The court is not asked
    // here, the way the other carrier's bootstrap discards the verdict it takes:
    // what this owes the caller is the world file, and the caller judges it.
    guard let tables = w.tables, let facts = w.facts,
          !FileManager.default.fileExists(atPath: facts) else { return false }
    let world = seededWorld((tables as NSString).appendingPathComponent("people.csv"),
                            (tables as NSString).appendingPathComponent("grants.csv"))
    do { try world.write(toFile: facts, atomically: false, encoding: .utf8) }
    catch {
        cannot(facts + " cannot be written here: " + error.localizedDescription.lowercased(),
               "the world is seeded beside the tables it comes from, so this needs a folder "
               + "you can write in")
    }
    return true
}

// the whole status answer, assembled once and returned: the door below prints
// it, and the verbs that ask about a world (`badge` today, its neighbours next)
// take their counts from the verb that owns them rather than counting again.
// Every field here is one the door already printed, and the split moves no byte.
struct StatusAnswer {
    var noWorld = false
    var judged: [String] = []
    var refusals: [(address: String, claim: String)] = []
    var judgeMs: String? = nil
    var wallMs: Double = 0
    var world: [String]? = nil          // declarations, lookups, premises
    var whereSize: [String: Int] = [:]
    var next = ""
    var then = ""
    var verdict: String { noWorld ? "no world here" : (refusals.isEmpty ? "holds" : "refused") }
}

func statusAnswer() -> StatusAnswer {
    // ── THE ANSWER THE BATTERY OPENS THROUGH A DOOR, and no argv a person
    // types: byte for byte against the other carrier on the worlds the battery
    // keeps. The verb itself moves with the asking pack, because the tables
    // bootstrap (`ensure_world`, python's `cmd_import`) has not moved: this
    // reads worlds, it does not seed them.
    loadStatusShelf()
    let w = discoverWorld()
    ensureWorld(w)                  // tables and no world yet: seed it, once
    let files = worldFilesOf(w)
    let here = FileManager.default.currentDirectoryPath
    var answer = StatusAnswer()
    if files.isEmpty && (w.layout?.rows.isEmpty ?? true) {
        // no world here: the rung the reader is standing on, chosen by what is
        // actually in the folder
        let inside = runGit(["rev-parse", "--is-inside-work-tree"], here)
            .trimmingCharacters(in: .whitespacesAndNewlines) == "true"
        let commits = runGit(["rev-list", "--count", "HEAD"], here)
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let hasPast = !commits.isEmpty && commits.allSatisfy { $0.isNumber }
            && Int(commits) ?? 0 > 0
        let next = inside && hasPast
            ? "run `gate log` to read this repository's own history: nothing to translate"
            : inside
            ? "run `gate demo` for a repository to look at: a CODEOWNERS, a policy, and one refusal"
            : "run `gate init .` to start a world in this folder"
        let then = FileManager.default.fileExists(atPath: "CODEOWNERS")
            ? "run `gate import codeowners CODEOWNERS --tree . --policy owners.csv` "
            + "because this repository already has the file, and two columns of "
            + "`owner,zone` are the rest"
            : "run `gate demo` for a repository with one, or drop your own tables "
            + "into tables/ and run gate status again"
        answer.noWorld = true
        answer.next = next
        answer.then = then
        return answer
    }
    let t0 = Date()
    let raw = courtSays(files)
    let wallMs = ((Date().timeIntervalSince(t0) * 1000 * 10).rounded(.toNearestOrEven)) / 10
    var refusals = judgedRefusals(raw)
    if files.count > 1 {
        // the declared list, not the readable list: a ghost row is the layout
        // guard's to name, and both carriers place claims over what is here
        let sources = files.filter { FileManager.default.fileExists(atPath: $0) }
            .map { (($0 as NSString).lastPathComponent, readText($0) ?? "") }
        refusals = attributeRefusals(refusals, sources)
    }
    if !files.isEmpty {
        refusals += canonGuard(w, raw, raw.contains("THE JUDGE"), "judge")
    }
    refusals += manifestGuards(w)
    var whereSize: [String: Int] = [:]
    refusals += formsGuards(w, &whereSize)
    refusals += policyGuards(w)
    refusals += stdlibGuards(w)
    refusals += gateShapeGuards(w) + ownSurfaceGuards(w) + opensGuards(w)
    refusals += vendoredGuards(w) + takenJudgeGuard(w)
    refusals += codeownersPairGuards(w)
    refusals += duplicateGuardsOver(diskSources(w))
    refusals += entryGuardsOver(diskSources(w))
    let times = matches("([\\d.]+) ms", raw).compactMap { $0.first }
    var judged = files
    if judged.isEmpty {
        judged = Set((w.layout?.rows ?? []).filter { $0.role == "forms" }.map { $0.path }).sorted()
    }
    answer.judged = judged
    answer.refusals = refusals
    answer.judgeMs = times.last
    answer.wallMs = wallMs
    answer.world = matches("(\\d+) declarations · (\\d+) lookups · (\\d+) premises", raw).first
    answer.whereSize = whereSize
    answer.next = nextRung(w, !refusals.isEmpty)
    return answer
}

// the door: it prints what the answer above assembled, and decides nothing
func statusDoor(_ asJson: Bool) -> Never {
    let a = statusAnswer()
    if a.noWorld {
        if asJson {
            var pairs: [(String, StatusJSON)] = [
                ("command", .text("status")),
                ("verdict", .text("no world here")),
                ("refusals", .list([])),
                ("next", .text(a.next)),
                ("then", .text(a.then)),
                ("mutates", .raw("false")),
            ]
            if let ready = commandIn(a.next) ?? commandIn(a.then) {
                pairs.append(("command_to_run", .text(ready)))
            }
            out(statusDumps(.object(pairs), 0) + "\n")
        } else {
            out("status: no world here\n  next: \(a.next)\n  then: \(a.then)\n")
        }
        exit(0)
    }
    let (judged, refusals, whereSize) = (a.judged, a.refusals, a.whereSize)
    let (verdict, worldM, next, times) = (a.verdict, a.world, a.next, a.judgeMs)
    let wallMs = a.wallMs
    if asJson {
        var pairs: [(String, StatusJSON)] = [
            ("command", .text("status")),
            ("facts", judged.count == 1 ? .text(judged[0])
                                        : .list(judged.map { .text($0) })),
            ("verdict", .text(verdict)),
            ("refusals", .list(refusals.map {
                .object([("address", .text($0.address)), ("claim", .text($0.claim))]) })),
            ("judge_ms", times.map { .raw(floatRepr($0)) } ?? .null),
            ("wall_ms", .raw(String(wallMs))),
            ("mutates", .raw("false")),
        ]
        if let m = worldM {
            pairs.append(("world", .object([("declarations", .raw(m[0])),
                                            ("lookups", .raw(m[1])),
                                            ("premises", .raw(m[2]))])))
        }
        if whereSize["equalities"] != nil {
            pairs.append(("forms", .object([
                ("equalities", .raw(String(whereSize["equalities"] ?? 0))),
                ("memberships", .raw(String(whereSize["memberships"] ?? 0))),
                ("uses", .raw(String(whereSize["uses"] ?? 0)))])))
        }
        pairs.append(("court", .text("the judge")))
        pairs.append(("next", .text(next)))
        if let ready = commandIn(next) { pairs.append(("command_to_run", .text(ready))) }
        out(statusDumps(.object(pairs), 0) + "\n")
    } else {
        let head = refusals.isEmpty ? "holds" : "refused \(refusals.count)"
        var tail: [String] = []
        if let m = worldM {
            tail.append(many(Int(m[0]) ?? 0, "declaration") + " · "
                      + many(Int(m[1]) ?? 0, "lookup") + " · "
                      + many(Int(m[2]) ?? 0, "premise"))
        }
        if let n = whereSize["equalities"] {
            if n != 0 {
                tail.append(many(n, "equality", "equalities"))
            } else if refusals.isEmpty && worldM == nil {
                tail.append("nothing claimed here yet, so nothing was checked")
            }
        }
        if let ms = times { tail.append(floatRepr(ms) + " ms") }
        var lines = ["status: " + head + (tail.isEmpty ? "" : " · " + tail.joined(separator: " · "))]
        for r in refusals { lines.append("  \(r.address) · \(r.claim)") }
        lines.append("  next: " + next)
        out(lines.joined(separator: "\n") + "\n")
    }
    exit(refusals.isEmpty ? 0 : 1)
}

// the road's own door: the battery calls this, not a person
if args.first == "--status-core" {
    statusDoor(args.contains("--json"))
}

// every whole match of a pattern, in the order they stand: `matches` hands back
// capture groups, and a pattern with none of those has nothing to hand back
func wholeMatches(_ pattern: String, _ text: String) -> [String] {
    guard let re = try? NSRegularExpression(pattern: pattern) else { return [] }
    let ns = text as NSString
    return re.matches(in: text, range: NSRange(location: 0, length: ns.length))
        .map { ns.substring(with: $0.range) }
}

// ── survey [N]: the t0 gesture, a read-only map of the repository with NO
// translation. Unwritten links out of its own history (co-change, exact
// statistics), identity, object candidates, and the fabric's own coverage.
//
// The verdict is not worked out a second time here: this asks the verb that
// owns it and prints what it said. A survey that judged on its own would be a
// second reading of one question, which is the defect this whole tool is about.
if args.first == "survey" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    var n = 500
    if let said = rest.first {
        guard let asked = Int(said.trimmingCharacters(in: .whitespaces)) else {
            cannot("`" + said + "` is not a number of commits, and this reads how many to walk",
                   "say a count, such as `gate survey 200`, or leave it out for the last 500")
        }
        n = asked
    }
    let here = FileManager.default.currentDirectoryPath
    // one walk of the log carries both halves: who signed, and what moved together
    var commits: [[String]] = []
    var authorOrder: [String] = [], authorCount: [String: Int] = [:]
    var signed = 0
    var current: [String] = []
    for line in runGit(["log", "-\(n)", "--format=%x40%ae %G?", "--name-only"], here)
        .components(separatedBy: "\n") {
        if line.hasPrefix("@") {
            if !current.isEmpty { commits.append(current); current = [] }
            let said = line.dropFirst().split(separator: " ").map(String.init)
            let email = said.first ?? ""
            let mark = said.count > 1 ? said[1] : "N"
            if authorCount[email] == nil { authorOrder.append(email) }
            authorCount[email, default: 0] += 1
            if ["G", "U", "X", "Y"].contains(mark) { signed += 1 }
        } else if !line.trimmingCharacters(in: .whitespaces).isEmpty {
            current.append(line.trimmingCharacters(in: .whitespaces))
        }
    }
    if !current.isEmpty { commits.append(current) }
    // a pair is counted once per commit, and the counters keep the order the
    // pairs were first seen: the other carrier's most_common is a stable sort
    // over that order, and a tie printed in another order is another answer
    var pairOrder: [String] = [], pairCount: [String: Int] = [:]
    var fileCount: [String: Int] = [:]
    for files in commits {
        let distinct = Array(Set(files)).sorted()
        for f in distinct { fileCount[f, default: 0] += 1 }
        for i in distinct.indices {
            for j in distinct.indices where j > i {
                let key = distinct[i] + "\u{0}" + distinct[j]
                if pairCount[key] == nil { pairOrder.append(key) }
                pairCount[key, default: 0] += 1
            }
        }
    }
    func mostCommon(_ order: [String], _ count: [String: Int], _ take: Int) -> [(String, Int)] {
        order.enumerated()
            .sorted { a, b in
                let (ca, cb) = (count[a.element] ?? 0, count[b.element] ?? 0)
                return ca == cb ? a.offset < b.offset : ca > cb
            }
            .prefix(take).map { ($0.element, count[$0.element] ?? 0) }
    }
    var links: [(a: String, b: String, together: Int, confidence: Double)] = []
    for (key, c) in mostCommon(pairOrder, pairCount, 30) where c >= 5 && links.count < 10 {
        let two = key.components(separatedBy: "\u{0}")
        let floor = min(fileCount[two[0]] ?? 1, fileCount[two[1]] ?? 1)
        let raw = Double(c) / Double(floor)
        links.append((two[0], two[1], c, (raw * 100).rounded(.toNearestOrEven) / 100))
    }
    let subjects = runGit(["log", "-\(n)", "--format=%s %b"], here)
    var keyOrder: [String] = [], keyCount: [String: Int] = [:]
    for m in wholeMatches("\\b[A-Z][A-Z0-9]+-\\d+\\b", subjects) {
        if keyCount[m] == nil { keyOrder.append(m) }
        keyCount[m, default: 0] += 1
    }
    // ── AND A WORLD OF FORMS IS STILL A WORLD, HERE TOO. This asked FACTS, the
    // plain court's one file, so a repository whose world is a manifest and a
    // shelf of forms was told `no world yet: coverage 0%` while `status` in the
    // same folder answered that it holds. That repository is this one.
    loadStatusShelf()
    let w = discoverWorld()
    var fabric: [(String, StatusJSON)] = [("facts", .null),
        ("note", .text("no world yet: coverage 0%. The links above say where to start"))]
    var hasWorld = false
    if !worldFilesOf(w).isEmpty || !((w.layout?.rows ?? []).isEmpty) {
        hasWorld = true
        let said = statusAnswer()
        let facts = w.facts.flatMap { FileManager.default.fileExists(atPath: $0) ? $0 : nil }
            ?? (w.layout.map { ($0.manifest as NSString).lastPathComponent } ?? "")
        fabric = [("facts", .text(facts)),
                  ("verdict", .text(said.verdict)),
                  ("refusals", .raw(String(said.refusals.count)))]
    }
    let next = hasWorld
        ? "run `gate status`: these are candidates from your history, and a world is what holds them"
        : "nothing here is judged yet: put a table into tables/ and run `gate status`"
    if asJson {
        var pairs: [(String, StatusJSON)] = [
            ("command", .text("survey")),
            ("next", .text(next)),
            ("commits", .raw(String(commits.count))),
            ("unwritten_links", .list(links.map {
                .object([("a", .text($0.a)), ("b", .text($0.b)),
                         ("together", .raw(String($0.together))),
                         ("confidence", .raw(String($0.confidence)))]) })),
            ("identity", .object([
                ("authors", .raw(String(authorOrder.count))),
                ("top", .list(mostCommon(authorOrder, authorCount, 5).map {
                    .text("\($0.0) (\($0.1))") })),
                ("signed_commits", .raw(String(signed)))])),
            ("object_candidates", .object(mostCommon(keyOrder, keyCount, 10).map {
                ($0.0, .raw(String($0.1))) })),
            ("fabric", .object(fabric)),
        ]
        if let ready = commandIn(next) { pairs.append(("command_to_run", .text(ready))) }
        out(statusDumps(.object(pairs), 0) + "\n")
    } else {
        var lines = ["survey: " + many(commits.count, "commit") + ", read-only",
                     "  unwritten links (co-change from your own history):"]
        for l in links {
            let pct = Int((l.confidence * 100).rounded(.toNearestOrEven))
            lines.append("    " + String(repeating: " ", count: max(0, 3 - String(l.together).count))
                         + "\(l.together)x "
                         + String(repeating: " ", count: max(0, 4 - (String(pct).count + 1)))
                         + "\(pct)%  \(l.a) <-> \(l.b)")
        }
        lines.append("  identity: \(authorOrder.count) author(s), \(signed) signed commits")
        for (who, c) in mostCommon(authorOrder, authorCount, 5) { lines.append("    \(who) (\(c))") }
        let keys = mostCommon(keyOrder, keyCount, 10)
        if !keys.isEmpty {
            lines.append("  object candidates in commit messages: "
                         + keys.map { "\($0.0)(\($0.1))" }.joined(separator: ", "))
        }
        if hasWorld {
            let facts = fabric.first(where: { $0.0 == "facts" }).map { pair -> String in
                if case .text(let s) = pair.1 { return s }
                return "no world yet"
            } ?? "no world yet"
            let verdict = fabric.first(where: { $0.0 == "verdict" }).map { pair -> String in
                if case .text(let s) = pair.1 { return s }
                return ""
            } ?? ""
            let refused = fabric.first(where: { $0.0 == "refusals" }).map { pair -> String in
                if case .raw(let s) = pair.1 { return s }
                return "0"
            } ?? "0"
            lines.append("  fabric: \(facts) · \(verdict), \(refused) refusal(s)")
        } else {
            lines.append("  fabric: no world yet · no world yet: coverage 0%. "
                         + "The links above say where to start")
        }
        lines.append("  next: " + next)
        out(lines.joined(separator: "\n") + "\n")
    }
    exit(0)
}

// somebody else's place to put a file, refused in words rather than raised: the
// writing half of theirsText, with the same three sentences the other carrier's
// errno names
func oursWrite(_ path: String, _ what: String, _ text: String) {
    let fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0o644)
    if fd < 0 {
        let why = errno
        if why == EISDIR {
            cannot(path + " is a directory, and this writes " + what,
                   "name a file inside it, or another path")
        }
        if why == EACCES || why == EPERM {
            cannot(path + " cannot be written here: permission denied",
                   "name a path you can write, and this will put " + what + " there")
        }
        cannot(path + " cannot be written here: "
               + String(cString: strerror(why)).lowercased(),
               "name a path whose folder exists, and this will put " + what + " there")
    }
    let bytes = Array(text.utf8)
    _ = bytes.withUnsafeBufferPointer { write(fd, $0.baseAddress, $0.count) }
    close(fd)
}

func escXml(_ s: String) -> String {
    s.replacingOccurrences(of: "&", with: "&amp;")
        .replacingOccurrences(of: "<", with: "&lt;")
        .replacingOccurrences(of: ">", with: "&gt;")
}

// git show, with the failure kept rather than flattened: a file that was not in
// that tree yet answers `nil`, and an empty file answers an empty string. The
// plain runGit cannot tell those apart, and the replay below counts on it.
func gitShow(_ spec: String, _ root: String) -> String? {
    let p = Process()
    p.executableURL = URL(fileURLWithPath: "/usr/bin/env")
    p.arguments = ["git", "-C", root, "show", spec]
    let pipe = Pipe(), quiet = Pipe()
    p.standardOutput = pipe
    p.standardError = quiet
    do { try p.run() } catch { return nil }
    let said = pipe.fileHandleForReading.readDataToEndOfFile()
    quiet.fileHandleForReading.readDataToEndOfFile()
    p.waitUntilExit()
    if p.terminationStatus != 0 { return nil }
    return String(data: said, encoding: .utf8) ?? ""
}

// whole days from a `YYYY-MM-DD` to today, the way the other carrier's date
// arithmetic counts them: calendar days in the machine's own zone, never hours
func daysSince(_ iso: String) -> Int {
    var calendar = Calendar(identifier: .gregorian)
    calendar.timeZone = TimeZone.current
    let parts = iso.split(separator: "-").compactMap { Int($0) }
    guard parts.count == 3 else { return 0 }
    var then = DateComponents()
    (then.year, then.month, then.day) = (parts[0], parts[1], parts[2])
    guard let from = calendar.date(from: then) else { return 0 }
    let today = calendar.startOfDay(for: Date())
    return calendar.dateComponents([.day], from: calendar.startOfDay(for: from),
                                   to: today).day ?? 0
}

let BADGE_SVG = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{w}\" height=\"20\" "
    + "role=\"img\" aria-label=\"{alt}\"><rect width=\"{lw}\" height=\"20\" rx=\"3\" "
    + "fill=\"#2F3131\"/><rect x=\"{lw}\" width=\"{rw}\" height=\"20\" rx=\"3\" fill=\"{fill}\"/>"
    + "<g font-family=\"ui-monospace,Menlo,monospace\" font-size=\"11\">"
    + "<text x=\"6\" y=\"14\" fill=\"#FDFDFD\">gate</text>"
    + "<text x=\"{tx}\" y=\"14\" fill=\"#FDFDFD\">{right}</text></g></svg>"

// ── badge [-o FILE.svg] [--since DATE]: the souvenir, and the only numbers on
// it are ones nobody can raise by hand. A coverage badge is gamed by writing
// tests that assert nothing; this one counts CLAIMS, which the court counts, and
// DAYS, which come from REPLAYING the world's own history through the same
// court. Anybody may re-run it and get the same answer.
//
// What it does NOT say is `no silent error`, because that is exactly what nobody
// saw. It says how many claims were judged and how long every commit that
// touched them has held: provable, and duller, and true.
if args.first == "badge" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    func after(_ flag: String) -> String? {
        guard let i = rest.firstIndex(of: flag), i + 1 < rest.count else { return nil }
        return rest[i + 1]
    }
    let outPath = after("-o")
    let since = after("--since")
    let t0 = Date()
    // AND THE NUMBER IS THE ONE STATUS COUNTS, asked rather than worked out
    // again: premises where the plain court sits, equalities where the where
    // court does. Both are claims judged, and neither can be raised by hand.
    //
    // ── AND THE COURT IS ASKED BEFORE THE WORLD IS DECLARED ABSENT. The
    // emptiness test below reads the world's FILES, and asking it first meant a
    // repository holding tables and no world yet was told `no world here` while
    // `status` in the same folder seeded and answered `holds · 82 premises`:
    // running the verb twice printed two different answers, which is the tell.
    // The court is asked first, and the court is the thing that seeds.
    let said = statusAnswer()
    let w = discoverWorld()          // read after the answer that may have seeded it
    let files = worldFilesOf(w)
    // a badge counts JUDGED claims, so it belongs to a world and to nothing
    // else. A world of forms is still a world, which this was the last place
    // not to know: the plain court's list rightly holds no forms row, and
    // reading emptiness there as emptiness altogether printed `no world here`
    // in this tool's own repository, two lines after `status` said it holds.
    let formsRows = files.isEmpty
        ? (w.layout?.rows ?? []).filter { $0.role == "forms" }.filter {
            FileManager.default.fileExists(atPath:
                (((w.layout!.manifest as NSString).deletingLastPathComponent) as NSString)
                    .appendingPathComponent($0.path)) }
        : []
    if files.isEmpty && formsRows.isEmpty {
        let next = "run `gate init .` to start a world in this folder"
        let then = "then `gate badge -o gate.svg` prints a badge nobody can forge"
        if asJson {
            var pairs: [(String, StatusJSON)] = [
                ("command", .text("badge")),
                ("verdict", .text("no world here")),
                ("refusals", .list([])),
                ("next", .text(next)),
                ("then", .text(then)),
                ("mutates", .raw("false")),
            ]
            if let ready = commandIn(next) ?? commandIn(then) {
                pairs.append(("command_to_run", .text(ready)))
            }
            out(statusDumps(.object(pairs), 0) + "\n")
        } else {
            out("badge: no world here\n  next: \(next)\n  then: \(then)\n")
        }
        exit(0)
    }
    let holds = said.verdict == "holds"
    let claims: Int
    if files.isEmpty { claims = said.whereSize["equalities"] ?? 0 }
    else if let m = said.world, m.count == 3 { claims = Int(m[2]) ?? 0 }
    else { claims = 0 }
    let here = FileManager.default.currentDirectoryPath
    var root = runGit(["rev-parse", "--show-toplevel"], here)
        .trimmingCharacters(in: .whitespacesAndNewlines)
    if !root.isEmpty { root = canonicalPath(root) }
    let rels = root.isEmpty ? [] : files.map { relPath(canonicalPath($0), root) }
    let shallow = !root.isEmpty
        && runGit(["rev-parse", "--is-shallow-repository"], root)
            .trimmingCharacters(in: .whitespacesAndNewlines) == "true"
    // ── AND THE RUN OF DAYS IS COUNTED WHERE IT CAN BE COUNTED HONESTLY. The
    // replay judges each past commit with the plain court over the world's own
    // files, and a forms world is not judged that way: status reads its pages in
    // a grouping of its own, and replaying them any other way would print a run
    // of green days over a period nobody checked, which is the one thing this
    // badge exists against.
    //
    // An empty `rels` means no path filter, so the walk would take the WHOLE
    // repository's history and print a run of days over commits that never
    // touched a world.
    var marks: [(sha: String, when: String)] = []
    if !root.isEmpty && !shallow && !rels.isEmpty {
        for line in gitLines(root, ["log", "--format=%H %as"]
                             + (since.map { ["--since=" + $0] } ?? []) + ["--"] + rels) {
            let parts = line.split(separator: " ", maxSplits: 1).map(String.init)
            if parts.count == 2 { marks.append((parts[0], parts[1])) }
        }
    }
    // newest first, back until one refuses: the leash is the run of commits
    // since the last time this world did not hold
    var judged = 0
    var broke: String? = nil
    for mark in marks {
        let d = NSTemporaryDirectory() + "/gate-badge-" + mark.sha
        try? FileManager.default.createDirectory(atPath: d,
                                                 withIntermediateDirectories: true)
        var wrote: [String] = []
        for rel in rels {
            guard let text = gitShow(mark.sha + ":" + rel, root) else { continue }
            let p = (d as NSString).appendingPathComponent((rel as NSString).lastPathComponent)
            try? text.write(toFile: p, atomically: false, encoding: .utf8)
            wrote.append(p)
        }
        let ok = !wrote.isEmpty && courtSays(wrote).contains("THE JUDGE holds")
        try? FileManager.default.removeItem(atPath: d)
        if wrote.isEmpty { continue }
        judged += 1
        if !ok { broke = mark.when; break }
    }
    let days = broke.map { daysSince($0) } ?? marks.last.map { daysSince($0.when) }
    // ── AND A RED BADGE DOES NOT REPORT NOUGHT CLAIMS. The claim count comes
    // from the court's own holding line, and a refusal prints no such line, so a
    // world with eighty-two premises and two refusals wore `0 claims · refused`
    // in the file people put in a README. This badge exists to say how WIDE the
    // green is, and on a red world there is no green to be wide: it says how
    // many were refused, which is the number that is true then.
    let right = (holds ? many(claims, "claim") + " · holds"
                       : "refused \(said.refusals.count)")
        + (days.map { " · \($0)d" } ?? "")
    if let path = outPath {
        let lw = 40, rw = 8 + Int(Double(right.count) * 6.2)
        var svg = BADGE_SVG
        for (k, v) in [("{w}", String(lw + rw)), ("{lw}", String(lw)), ("{rw}", String(rw)),
                       ("{tx}", String(lw + 5)), ("{right}", escXml(right)),
                       ("{fill}", holds ? "#007D36" : "#BF4035"),
                       ("{alt}", escXml("gate: " + right))] {
            svg = svg.replacingOccurrences(of: k, with: v)
        }
        oursWrite(path, "the badge", svg)
    }
    let note = (files.isEmpty
                ? "this world is forms, and the run of days is not counted for one yet: "
                + "replaying its pages any way other than the one status reads them in "
                + "would print green days over a period nothing checked"
                : shallow || marks.isEmpty
                ? "this repository arrived without history, so only today is counted"
                : many(judged, "commit") + " that touched this world were judged again, "
                + "oldest \(marks[marks.count - 1].when)"
                + (broke.map { ", and the last that did not hold was \($0)" }
                   ?? ", and every one held"))
        + ": the judge counts the claims again on every run"
    let next = "put it in the README beside the build: it says how WIDE the green is, "
             + "which a badge that only says green does not"
    let ms = ((Date().timeIntervalSince(t0) * 1000 * 10).rounded(.toNearestOrEven)) / 10
    if asJson {
        var pairs: [(String, StatusJSON)] = [
            ("command", .text("badge")),
            ("claims", .raw(String(claims))),
            ("verdict", .text(holds ? "holds" : "refused")),
            ("commits_judged", .raw(String(judged))),
            ("unbroken_days", days.map { .raw(String($0)) } ?? .null),
            ("last_refusal", broke.map { .text($0) } ?? .null),
            ("shallow", .raw(shallow ? "true" : "false")),
            ("wrote", outPath.map { .text($0) } ?? .null),
            ("text", .text(right)),
            ("ms", .raw(String(ms))),
            ("note", .text(note)),
            ("next", .text(next)),
            ("mutates", .raw(outPath != nil ? "true" : "false")),
        ]
        if let ready = commandIn(next) { pairs.append(("command_to_run", .text(ready))) }
        out(statusDumps(.object(pairs), 0) + "\n")
    } else {
        out("badge: " + right + (outPath.map { " · wrote \($0)" } ?? "")
            + "\n  note: " + note + "\n  next: " + next + "\n")
    }
    exit(holds ? 0 : 1)
}

// and the verb itself, now that the bootstrap it stood on is here. `fsck` is
// the second spelling of the same question, and it travels with it: the other
// carrier answers both from one branch and names the answer `status` either
// way, so a spelling left behind would be one word answered by two carriers.
if args.first == "status" || args.first == "fsck" {
    statusDoor(args.contains("--json"))
}

// ── my — your personal world: where it is, and its verdict WITH the shared
// world (the claims you keep, judged against facts other people own)
//
// This one moves as a verb and not as a door: nothing here seeds a world, so
// the bootstrap that keeps `status` off the carries line does not hold it back.
if args.first == "my" {
    let asJson = args.contains("--json")
    loadStatusShelf()
    let w = discoverWorld()
    guard let personal = personalPathOf(w), let facts = w.facts else {
        cannot("your own world lives beside a shared one, and there is no world here",
               "run `gate init .` to start one, or `gate demo` for a repository to look at")
    }
    let key = repoKey((absPath(facts) as NSString).deletingLastPathComponent)
    if !FileManager.default.fileExists(atPath: personal) {
        // nothing was written, so nothing is stored: an empty personal world is
        // no file at all, and this says so rather than making one to report on
        let next = "nobody has written in your world, so it is not stored anywhere. "
                 + "Open the bench and write a claim in my.swift: it is judged with the "
                 + "shared world, stays out of it, and is kept on this machine alone. "
                 + "Clear it again and it is gone."
        if asJson {
            out(statusDumps(.object([
                ("command", .text("my")),
                ("personal", .text(personal)),
                ("repo_key", .text(key)),
                ("empty", .raw("true")),
                ("verdict", .text("holds")),
                ("refusals", .list([])),
                ("shared_repo_untouched", .raw("true")),
                ("next", .text(next)),
            ]), 0) + "\n")
        } else {
            out("my: holds\n  next: " + next + "\n")
        }
        exit(0)
    }
    // ── AND A FORMS ROW GOES TO THE COURT THAT READS IT, HERE TOO. Handing
    // every file of the world to the PLAIN court refuses a forms page for
    // declaring protocols, which that court reads as outside its fragment, and
    // `gate my` then answers with MORE than the world has while `gate status`
    // holds. The layout and the policy are META beside them: judged by their own
    // guards and by no court. A court that answers about a world may not answer
    // with less than the court beside it, and answering with more is that same
    // fault mirrored.
    var apart = Set<String>()
    if let l = w.layout {
        let mbase = (l.manifest as NSString).deletingLastPathComponent
        for r in l.rows where r.role == "forms" {
            apart.insert(absPath((mbase as NSString).appendingPathComponent(r.path)))
        }
        apart.insert(absPath(l.manifest))
    }
    if let pp = policyPathOf(w) { apart.insert(absPath(pp)) }
    let named = benchFilesOf(w).filter {
        FileManager.default.fileExists(atPath: $0.1) && !apart.contains(absPath($0.1))
    }
    let raw = named.isEmpty ? "" : courtSays(named.map { $0.1 })
    var refusals = judgedRefusals(raw)
    refusals = attributeRefusals(refusals, named.map { ($0.0, readText($0.1) ?? "") })
    // AND THE SAME GUARDS THE SHARED WORLD GETS. Declaring `MyBench` in a
    // personal world when the shared one already declares it is two truths about
    // one name: `gate status` refused it with both addresses and this said
    // `holds`, which is the one command a person runs about the file that
    // carries the second one.
    let sources = oneStream(w, named).map { ($0.0, readText($0.1) ?? "") }
    refusals += duplicateGuardsOver(sources)
    refusals += entryGuardsOver(sources)
    var whereSize: [String: Int] = [:]
    refusals += formsGuards(w, &whereSize)   // the forms half, by the court that reads it
    if asJson {
        out(statusDumps(.object([
            ("command", .text("my")),
            ("personal", .text(personal)),
            ("repo_key", .text(key)),
            ("shared_repo_untouched", .raw("true")),
            ("verdict", .text(refusals.isEmpty ? "holds" : "refused")),
            ("refusals", .list(refusals.map {
                .object([("address", .text($0.address)), ("claim", .text($0.claim))]) })),
        ]), 0) + "\n")
    } else {
        var lines = ["my: " + (refusals.isEmpty ? "holds" : "refused \(refusals.count)")]
        for r in refusals { lines.append("  \(r.address) · \(r.claim)") }
        out(lines.joined(separator: "\n") + "\n")
    }
    exit(refusals.isEmpty ? 0 : 1)
}

// ── declare contract SPEC [-o F] · declare carrier DECL.json [-o F]
//
// THE ACT OF ENTRY. Everything this tool judges is on this side of it. The two
// halves are asymmetric on purpose: a contract states its own types in a public
// format, so one emitter serves everybody and the tool ships it; a library's
// grammar is its own, so its build emits a small declaration and this renders
// that into the shared words. Both heads come off the shelf page, one home.
if args.first == "declare" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    let what = rest.first ?? ""
    func after(_ flag: String) -> String? {
        guard let i = rest.firstIndex(of: flag), i + 1 < rest.count else { return nil }
        return rest[i + 1]
    }
    let outPath = after("-o")
    let mineToo = rest.contains("--theirs") || rest.contains("--mine")
    let askNote = "declare contract SPEC [-o F]  ·  declare carrier DECL.json [-o F]"

    func asks(_ note: String, _ next: String) -> Never {
        if asJson {
            out("{\n  \"command\": \"declare\",\n  \"asks\": true,\n"
                + "  \"note\": " + jsonString(note) + ",\n"
                + "  \"next\": " + jsonString(next) + "\n}\n")
        } else {
            out("usage: " + note + "\n  next: " + next + "\n")
        }
        exit(0)
    }
    if (what == "contract" || what == "carrier") && rest.count < 2 {
        asks(askNote, "the spec is a JSON OpenAPI document, and the carrier declaration is "
             + "what your build emits. After this it is what you have SAID, and judged")
    }
    if what != "contract" && what != "carrier" {
        asks(askNote, "the carrier declaration is emitted by that library's own build: "
             + "{\"carrier\": N, \"against\": {...}, \"carries\": "
             + "[{\"route\", \"field\", \"as\", \"mine\"?}]}")
    }

    func writeWorld(_ world: String, _ path: String) {
        do { try world.write(toFile: path, atomically: true, encoding: .utf8) }
        catch {
            cannot(path + " cannot be written here: " + error.localizedDescription.lowercased(),
                   "name a path you can write, and this will put the side you are declaring there")
        }
    }
    // the row this world writes for a side it took, through the writing road
    func declaredIn(_ path: String?, _ pin: String?) -> String? {
        guard mineToo, let path = path else { return nil }
        let root = worldRootFor(path)
        let mp = (root as NSString).appendingPathComponent("gate.manifest.swift")
        let text = FileManager.default.fileExists(atPath: mp)
            ? theirsText(mp, "the layout of this world") : manifestHead()
        var rel = ((path as NSString).standardizingPath)
        let base = (root as NSString).standardizingPath
        if rel.hasPrefix(base + "/") { rel = String(rel.dropFirst(base.count + 1)) }
        // a row may not point out of the world that makes it: the other carrier
        // raises here, and a row about somebody else's tree is a claim this
        // world cannot answer for
        if rel.hasPrefix("/") || rel.hasPrefix("../") {
            cannot(path + " is not inside the world at " + base + ": a row says where a "
                   + "file is relative to the world that declares it",
                   "write the side inside the world that declares it")
        }
        let said = upsertRow(text, name: rowAtom(rel), rel: rel, kind: "Theirs",
                             role: "seam", from: pin)
        writeWorld(said, mp)
        return (mp as NSString).lastPathComponent
    }

    var world = "", declares = 0, extra: [(String, String)] = []
    if what == "contract" {
        let src = rest[1]
        guard let spec = readSaid(theirsText(src, "an OpenAPI document")) else {
            let at = jsonPlace(theirsText(src, "an OpenAPI document"))
            cannot(src + " is not the JSON this reads (an OpenAPI document): Expecting value at "
                   + "line \(at.line), column \(at.column)",
                   "point it at the document itself. For YAML, `yq -o=json '.' file.yml > "
                   + "file.json` writes the JSON this reads")
        }
        let fields = contractFields(spec).filter { $0.shape != nil }
        declares = fields.count
        var lines = [shelfSection("declare",
                                  "// ── what a contract side is printed under begins here ──\n")
                     + shelfPage("forms-contract"), ""]
        for f in fields {
            let rec = "F_" + sanitized(f.route) + "_" + sanitized(f.field)
            lines += ["// " + f.route + " · " + f.field,
                      "public enum " + rec + ": Declared {",
                      "    public typealias Of = " + (f.shape ?? ""), "}"]
        }
        world = lines.joined(separator: "\n") + "\n"
        if let o = outPath { writeWorld(world, o) }
        let pin = after("--at") ?? (src as NSString).lastPathComponent
        let mine = declaredIn(outPath, pin)
        extra = [("of", jsonString((src as NSString).lastPathComponent)),
                 ("declared_in", mine.map { jsonString($0) } ?? "null")]
    } else {
        let src = rest[1]
        guard let decl = readSaid(theirsText(src, "a carrier declaration your build emits")) else {
            let at = jsonPlace(theirsText(src, "a carrier declaration your build emits"))
            cannot(src + " is not the JSON this reads (a carrier declaration your build emits): "
                   + "Expecting value at line \(at.line), column \(at.column)",
                   "point it at the document itself")
        }
        let who = sanitized(decl.at("carrier")?.asText ?? "Carrier")
        let against = decl.at("against")
        let contractSaid = against?.at("contract")?.asText ?? "a contract"
        let revision = against?.at("revision")?.asText
        var head = shelfSection("declare",
                                "// ── what a carrier side is printed under begins here ──\n")
        head += "// " + who + " · against " + contractSaid
        head += revision.map { " at " + $0 } ?? ""
        var lines = [head + "\n", "public enum " + who + ": Carrier {}", ""]
        let carries = decl.at("carries")?.asList ?? []
        declares = carries.count
        for (i, c) in carries.enumerated() {
            let route = c.at("route")?.asText ?? "", field = c.at("field")?.asText ?? ""
            let rec = "F_" + sanitized(route) + "_" + sanitized(field)
            let mineName = c.at("mine")?.asText
            lines.append("// " + route + " · " + field
                         + (mineName.map { " (it calls it " + $0 + ")" } ?? ""))
            lines.append("public typealias Carry_\(i) = Carries<" + who + ", " + rec + ", "
                         + (c.at("as")?.asText ?? "") + ">")
        }
        world = lines.joined(separator: "\n") + "\n"
        if let o = outPath { writeWorld(world, o) }
        let pin = after("--at") ?? revision ?? against?.at("contract")?.asText
        let mine = declaredIn(outPath, pin)
        var againstJSON = "{}"
        if let a = against { againstJSON = laidOutBy(a, 1, 2) }
        extra = [("carrier", jsonString(who)),
                 ("declared_in", mine.map { jsonString($0) } ?? "null"),
                 ("against", againstJSON)]
    }
    let noteSaid = what == "contract"
        ? "a view of that document: every field it states a type for, as a record whose shape "
          + "is an axis. Fields it leaves open state no shape and are not here. A contract that "
          + "says `anyOf` has not said which"
        : "what this library says it carries. It is not judgeable alone: a carrier declaration "
          + "is about a contract, and the pair is judged by `gate seam`"
    let declaredIn_ = extra.first(where: { $0.0 == "declared_in" })?.1 ?? "null"
    let nextSaid = what == "contract"
        ? "commit it: from here on it is what you have said, and it is judged"
        : (declaredIn_ == "null"
           ? "run it again with --theirs to write it into gate.manifest.swift, and put this file "
             + "plus those two lines in THEIR repository: their own CI then holds them to what "
             + "you carry"
           : "put this file and its two manifest lines in THEIR repository: from then on their "
             + "CI parts the seam the day they touch what you carry")
    let cmd = "declare " + what
    if asJson {
        var text = "{\n  \"command\": " + jsonString(cmd) + ",\n"
        for (k, v) in extra where k != "declared_in" && k != "against" {
            text += "  " + jsonString(k) + ": " + v + ",\n"
        }
        text += "  \"declared_in\": " + declaredIn_ + ",\n"
        text += "  \"declares\": " + String(declares) + ",\n"
        text += "  \"wrote\": " + (outPath.map { jsonString($0) } ?? "null") + ",\n"
        text += "  \"world\": " + (outPath == nil ? jsonString(world) : "null") + ",\n"
        if let a = extra.first(where: { $0.0 == "against" })?.1 {
            text += "  \"against\": " + a + ",\n"
        }
        text += "  \"note\": " + jsonString(noteSaid) + ",\n"
        text += "  \"next\": " + jsonString(nextSaid) + ",\n"
        text += "  \"mutates\": " + (outPath == nil ? "false" : "true")
        if let ready = commandIn(nextSaid) {
            text += ",\n  \"command_to_run\": " + jsonString(ready)
        }
        out(text + "\n}\n")
        exit(0)
    }
    out(cmd + ": " + String(declares) + " declared"
        + (outPath.map { " · wrote " + $0 } ?? "")
        + "\n  note: " + noteSaid + "\n  next: " + nextSaid + "\n")
    exit(0)
}

if args.first == "aside" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    let note = "aside ROUTE FIELD --because KEY [--by WHO] [-o known.json]"
    let next = "the reason is not optional: name something that can close, such as a ticket, a "
             + "release. This stands aside only while that is open"
    if rest.count < 2 || !rest.contains("--because") {
        // named a route and a field and no reason: half a sentence, and the
        // nought exit told a script the divergence was set aside
        if !rest.isEmpty { cannot(note, next) }
        if asJson {
            out("{\n  \"command\": \"aside\",\n  \"asks\": true,\n"
                + "  \"note\": " + jsonString(note) + ",\n"
                + "  \"next\": " + jsonString(next) + "\n}\n")
        } else {
            out("usage: " + note + "\n  next: " + next + "\n")
        }
        exit(0)
    }
    func after(_ flag: String) -> String? {
        guard let i = rest.firstIndex(of: flag), i + 1 < rest.count else { return nil }
        return rest[i + 1]
    }
    let route = rest[0], field = rest[1]
    let because = after("--because") ?? ""
    let here = FileManager.default.currentDirectoryPath
    let by = after("--by") ?? {
        let said = runGit(["config", "user.name"], here)
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return said.isEmpty ? "somebody" : said
    }()
    let path = after("-o") ?? "known.json"
    var rows: [[(String, String)]] = []
    var others: [(String, String)] = []
    if FileManager.default.fileExists(atPath: path) {
        let text = theirsText(path, "the divergences you declared")
        if let top = readSaid(text), let pairsTop = top.asObject {
            // every other key the file states, kept as it was written
            for (k, v) in pairsTop where k != "diverges" {
                others.append((k, laidOut(v, 1)))
            }
        }
        if let top = readSaid(text), let held = top.at("diverges"), held.asList == nil {
            cannot(path + " states `diverges` as " + kindOf(held)
                   + ", and it is a list of records",
                   "each divergence is an object with a route and a field; fix the file, or move "
                   + "it aside and let this write a new one")
        }
        if let top = readSaid(text), let said = top.at("diverges")?.asList {
            for d in said {
                guard let pairs = d.asObject else {
                    cannot(path + " holds a divergence that is not a record: " + sameAgain(d).prefix(40),
                           "each divergence is an object with a route and a field; fix that line, "
                           + "or move the file aside and let this write a new one")
                }
                let r = pairs.first(where: { $0.0 == "route" })?.1.asText ?? ""
                let f = pairs.first(where: { $0.0 == "field" })?.1.asText ?? ""
                if r == route && f == field { continue }
                // every key the row had, in the order the file had them: the
                // other carrier keeps that order because its reader does, and a
                // row rewritten in another order is a diff nobody can read
                rows.append(pairs.map { ($0.0, $0.1.asText ?? "") })
            }
        }
    }
    rows.append([("route", route), ("field", field),
                 ("because", because), ("declared_by", by)])
    let said = asideJSON(rows, others)
    do {
        try said.write(toFile: path, atomically: true, encoding: .utf8)
    } catch {
        cannot(path + " cannot be written here: " + error.localizedDescription.lowercased(),
               "name a path you can write, and this will put the divergences you declare there")
    }
    let address = route + " · " + field
    let noteSaid = by + " says this one is meant, while " + because + " is open. It stands out of "
                 + "the way until " + because + " closes, and comes back by itself when it does"
    let nextSaid = "point a tracker export at it — `gate attention … --known " + path
                 + " --tracker tickets.json`, and the day it closes this returns first"
    if asJson {
        var text = "{\n"
        text += "  \"command\": \"aside\",\n"
        text += "  \"address\": " + jsonString(address) + ",\n"
        text += "  \"because\": " + jsonString(because) + ",\n"
        text += "  \"declared_by\": " + jsonString(by) + ",\n"
        text += "  \"wrote\": " + jsonString(path) + ",\n"
        text += "  \"standing\": " + String(rows.count) + ",\n"
        text += "  \"note\": " + jsonString(noteSaid) + ",\n"
        text += "  \"next\": " + jsonString(nextSaid) + ",\n"
        text += "  \"mutates\": true"
        if let ready = commandIn(nextSaid) {
            text += ",\n  \"command_to_run\": " + jsonString(ready)
        }
        out(text + "\n}\n")
        exit(0)
    }
    // the step is printed by the other carrier's own common tail, under every
    // answer it gives: a verb that ends without one is a verb that stops short
    out("aside: " + address + " · while " + because + " is open · said by " + by
        + " · " + String(rows.count) + " standing\n  note: " + noteSaid
        + "\n  next: " + nextSaid + "\n")
    exit(0)
}

// ── drift CONTRACT --client DIR: observation, and nothing else. A world that
// has not entered ours holds no court and carries no verdict: what prints is
// lexical facts about git objects and a walk whose bounds travel with every
// absence. The exit code follows the operator's own threshold, never a verdict.
func gitLines(_ rootDir: String, _ arguments: [String]) -> [String] {
    return runGit(["-C", rootDir] + arguments, FileManager.default.currentDirectoryPath)
        .components(separatedBy: "\n")
        .filter { !$0.trimmingCharacters(in: .whitespaces).isEmpty }
}

func contractRevisions(_ path: String, _ since: String?) -> (root: String?, revs: [(String, Data)]) {
    // every revision of a contract, oldest first, read out of git and never off
    // the disk: one cat-file --batch for the lot
    let full = canonicalPath(path)
    var here = (full as NSString).deletingLastPathComponent
    if here.isEmpty { here = "." }
    let rootSaid = runGit(["-C", here, "rev-parse", "--show-toplevel"],
                          FileManager.default.currentDirectoryPath)
        .trimmingCharacters(in: .whitespacesAndNewlines)
    if rootSaid.isEmpty { return (nil, []) }
    let rootDir = canonicalPath(rootSaid)
    let rel = relPath(full, rootDir)
    if rel.hasPrefix("..") { return (nil, []) }
    var logArgs = ["log", "--reverse", "--format=%H %as"]
    if let since = since { logArgs.append("--since=" + since) }
    logArgs += ["--", rel]
    let marks = gitLines(rootDir, logArgs).map { line -> (String, String) in
        let parts = line.split(separator: " ", maxSplits: 1).map(String.init)
        return (parts.first ?? "", parts.count > 1 ? parts[1] : "")
    }
    if marks.isEmpty { return (rootDir, []) }
    let p = Process()
    p.executableURL = URL(fileURLWithPath: "/usr/bin/env")
    p.arguments = ["git", "-C", rootDir, "cat-file", "--batch"]
    let put = Pipe(), got = Pipe()
    p.standardInput = put
    p.standardOutput = got
    p.standardError = Pipe()
    guard (try? p.run()) != nil else { return (rootDir, []) }
    let asked = marks.map { "\($0.0):\(rel)" }.joined(separator: "\n")
    // written on its own queue, the way communicate does: a batch bigger than
    // the pipe would deadlock a writer who waits to read
    DispatchQueue.global().async {
        put.fileHandleForWriting.write(Data(asked.utf8))
        put.fileHandleForWriting.closeFile()
    }
    let blob = got.fileHandleForReading.readDataToEndOfFile()
    p.waitUntilExit()
    var out: [(String, Data)] = []
    var i = 0
    for (_, when) in marks {
        guard let j = blob[i...].firstIndex(of: 0x0A) else { break }
        let head = String(decoding: blob[i..<j], as: UTF8.self)
            .split(separator: " ").map(String.init)
        if head.count < 3 { i = j + 1; continue }
        let size = Int(head[2]) ?? 0
        out.append((when, blob.subdata(in: (j + 1)..<min(j + 1 + size, blob.count))))
        i = j + 1 + size + 1
        if i > blob.count { break }
    }
    return (rootDir, out)
}

func snakeOf(_ name: String) -> String {
    var out = ""
    for (i, ch) in name.enumerated() {
        if i > 0, ch.isUppercase { out.append("_") }
        out.append(ch)
    }
    return out.lowercased()
}

func nameVariants(_ name: String) -> Set<String> {
    // a wire name is rarely the name a library writes: the contract's
    // hyphenated spelling, the snake, and the camel are all one word
    let plain = name.replacingOccurrences(of: "-", with: "_")
    var camel = ""
    var lift = false
    for ch in name {
        if ch == "-" || ch == "_" { lift = true; continue }
        camel.append(lift ? Character(ch.uppercased()) : ch)
        lift = false
    }
    return [name, plain, snakeOf(plain), camel]
}

func firstMentions(_ rootDir: String, _ names: [String],
                   only: String?, without: String?) -> [String: String] {
    // when each name first appeared in a library, read from the diffs
    // themselves, in every spelling the library might use; the log is streamed
    // and torn down the moment the last name is found
    var whereArgs: [String] = []
    if let only = only { whereArgs = ["--", only] }
    if let without = without {
        if whereArgs.isEmpty { whereArgs = ["--"] }
        whereArgs.append(":(exclude)" + without)
    }
    var left: [(String, NSRegularExpression)] = []
    for n in names {
        let alt = nameVariants(n).map { NSRegularExpression.escapedPattern(for: $0) }
            .joined(separator: "|")
        if let re = try? NSRegularExpression(pattern: "\\b(?:" + alt + ")\\b") {
            left.append((n, re))
        }
    }
    var seen: [String: String] = [:]
    let p = Process()
    p.executableURL = URL(fileURLWithPath: "/usr/bin/env")
    p.arguments = ["git", "-C", rootDir, "log", "--reverse", "-p", "--no-color",
                   "--format=~gate~ %as"] + whereArgs
    let got = Pipe()
    p.standardOutput = got
    p.standardError = Pipe()
    guard (try? p.run()) != nil else { return seen }
    var when: String? = nil
    var carry = Data()
    let handle = got.fileHandleForReading
    reading: while true {
        let chunk = handle.availableData
        if chunk.isEmpty { break }
        carry.append(chunk)
        while let nl = carry.firstIndex(of: 0x0A) {
            let line = String(decoding: carry[carry.startIndex..<nl], as: UTF8.self)
            carry.removeSubrange(carry.startIndex...nl)
            if line.hasPrefix("~gate~ ") {
                when = String(line.dropFirst(7)).trimmingCharacters(in: .whitespaces)
                continue
            }
            guard line.hasPrefix("+"), !line.hasPrefix("+++") else { continue }
            let ns = line as NSString
            for (i, (n, re)) in left.enumerated().reversed()
            where re.firstMatch(in: line, range: NSRange(location: 0, length: ns.length)) != nil {
                seen[n] = when ?? ""
                left.remove(at: i)
            }
            if left.isEmpty { break reading }
        }
    }
    p.terminate()
    handle.closeFile()
    return seen
}

let CARRIER_KINDS = [".py", ".ts", ".js", ".rs", ".go", ".rb", ".java", ".kt"]

func readCarrier(_ rootDir: String) -> (body: String, files: Int, said: String) {
    // what a client library names, and, said out loud, where this looked:
    // absence is a fact about a walk, so the bounds travel with it
    var texts: [String] = []
    var count = 0
    func walk(_ d: String) {
        let names = ((try? FileManager.default.contentsOfDirectory(atPath: d)) ?? []).sorted()
        for f in names {
            let p = (d as NSString).appendingPathComponent(f)
            var isDir: ObjCBool = false
            guard FileManager.default.fileExists(atPath: p, isDirectory: &isDir) else { continue }
            if isDir.boolValue {
                if [".git", "node_modules", "target", "dist", "build", ".venv",
                    "proto"].contains(f) { continue }
                if f.lowercased().contains("test") || f.lowercased().contains("example") {
                    continue
                }
                walk(p)
                continue
            }
            guard CARRIER_KINDS.contains((f as NSString).pathExtension.isEmpty
                                         ? "" : "." + (f as NSString).pathExtension)
            else { continue }
            if f.lowercased().contains("test") || f.lowercased().contains("example") { continue }
            if f.contains("_pb2") || f.hasSuffix("_pb.js") || f.hasSuffix("_pb.ts") { continue }
            guard let text = readText(p) else { continue }
            texts.append(text)
            count += 1
        }
    }
    walk(rootDir)
    return (texts.joined(separator: "\n"), count,
            "directories named test/example, and .git node_modules target dist build .venv "
            + "proto, files named test/example, protobuf stubs (_pb2, _pb.js, _pb.ts)")
}

if args.first == "drift" {
    let asJson = args.contains("--json")
    let a = Array(args.dropFirst()).filter { $0 != "--json" }
    let specNext = "the contract is a JSON OpenAPI document in a git checkout, and "
                 + "for YAML, `yq -o=json '.' spec.yml > spec.json` first"
    if a.isEmpty || a[0].hasPrefix("-") {
        let note = "drift CONTRACT --client DIR [--since DATE] [--name N] [--fail-over DAYS]"
        if asJson {
            var pairs: [(String, StatusJSON)] = [
                ("command", .text("drift")), ("asks", .raw("true")),
                ("note", .text(note)), ("next", .text(specNext))]
            if let ready = commandIn(specNext) { pairs.append(("command_to_run", .text(ready))) }
            out(statusDumps(.object(pairs), 0) + "\n")
        } else {
            out("usage: " + note + "\n  next: " + specNext + "\n")
        }
        exit(0)
    }
    if !FileManager.default.fileExists(atPath: a[0]) {
        cannot("no such contract here: \(a[0])", specNext)
    }
    let src = a[0]
    func after(_ flag: String) -> String? {
        guard let i = a.firstIndex(of: flag), i + 1 < a.count else { return nil }
        return a[i + 1]
    }
    let clientRoot = after("--client") ?? "."
    let since = after("--since")
    let who = after("--name") ?? sanitized((absPath(clientRoot) as NSString).lastPathComponent)
    let over = after("--fail-over").flatMap { Int($0) }
    let t0 = Date()
    let (sroot, revs) = contractRevisions(src, since)
    // history dates; today walks: the union is what the contract has EVER
    // said, and only the dates come from it
    var declared: [(field: String, when: String?)] = []
    func setdefault(_ f: String, _ when: String?) {
        if !declared.contains(where: { $0.field == f }) { declared.append((f, when)) }
    }
    for (when, blob) in revs {
        guard let spec = readSaid(String(decoding: blob, as: UTF8.self)) else { continue }
        for f in contractFields(spec) { setdefault(f.field, when) }
    }
    var current: [String] = []
    var routes: [String] = []
    if let spec = readText(src).flatMap({ readSaid($0) }) {
        for f in contractFields(spec) {
            current.append(f.field)
            if !routes.contains(f.route) { routes.append(f.route) }
            setdefault(f.field, nil)
        }
    }
    let carrier = readCarrier(clientRoot)
    let words = Set(findAll("\\w+", carrier.body))
    let spoken = Set(matches("[\"'`/]([A-Za-z0-9_.\\-]+)(?=[\"'`/?]|$)", carrier.body,
                             lines: true).map { $0[0] })
    let unwritten = Set(current.filter { nameVariants($0).isDisjoint(with: words) }).sorted()
    var silent: [String] = []
    func segments(_ r: String) -> [String] {
        return r.components(separatedBy: "/").filter { !$0.isEmpty && !$0.hasPrefix("{") }
    }
    if routes.contains(where: { segments($0).allSatisfy { spoken.contains($0) } }) {
        for r in routes.sorted() {
            let segs = segments(r)
            if !segs.isEmpty, !segs.allSatisfy({ spoken.contains($0) }) { silent.append(r) }
        }
    }
    let crootSaid = runGit(["-C", clientRoot, "rev-parse", "--show-toplevel"],
                           FileManager.default.currentDirectoryPath)
        .trimmingCharacters(in: .whitespacesAndNewlines)
    let croot = crootSaid.isEmpty ? "" : canonicalPath(crootSaid)
    func shallow(_ r: String) -> Bool {
        return !r.isEmpty && runGit(["-C", r, "rev-parse", "--is-shallow-repository"],
                                    FileManager.default.currentDirectoryPath)
            .trimmingCharacters(in: .whitespacesAndNewlines) == "true"
    }
    var thin: [String] = []
    if sroot == nil || shallow(sroot ?? "") || revs.count < 2 {
        thin.append((src as NSString).lastPathComponent)
    }
    if croot.isEmpty || shallow(croot) {
        thin.append(who)
    }
    var late: [(field: String, contract: String, carrier: String, days: Int)] = []
    var undatable: [String] = []
    var median = 0
    if thin.isEmpty {
        let here = relPath(canonicalPath(clientRoot), croot)
        let specReal = canonicalPath(src)
        let specRel = specReal.hasPrefix(croot + "/") ? relPath(specReal, croot) : nil
        let seen = firstMentions(croot, declared.map { $0.field },
                                 only: (here == "." || here.isEmpty) ? nil : here,
                                 without: specRel)
        // a window has an edge: whatever the contract already declared when
        // the window opened carries the window's date, not the day it was said
        let edge = since != nil ? revs.first?.0 : nil
        func daysApart(_ a: String, _ b: String) -> Int? {
            let f = DateFormatter()
            f.dateFormat = "yyyy-MM-dd"
            f.timeZone = TimeZone(identifier: "UTC")
            guard let da = f.date(from: a), let db = f.date(from: b) else { return nil }
            return Int((db.timeIntervalSince(da) / 86400).rounded())
        }
        for (f, sd) in declared {
            guard let sd = sd, sd != edge else { undatable.append(f); continue }
            guard let cd = seen[f] else { continue }
            guard let days = daysApart(sd, cd), days > 0 else { continue }
            late.append((f, sd, cd, days))
        }
        // sorted the way the other carrier sorts: by days descending, and the
        // declaration order kept where two are equal, because its sort is stable
        late = late.enumerated().sorted {
            $0.element.days != $1.element.days
                ? $0.element.days > $1.element.days : $0.offset < $1.offset
        }.map { $0.element }
        let mid = late.map { $0.days }.sorted()
        if !mid.isEmpty {
            median = mid.count % 2 == 1 ? mid[mid.count / 2]
                                        : (mid[mid.count / 2 - 1] + mid[mid.count / 2]) / 2
        }
    }
    let worst = Array(late.prefix(5))
    let ms = ((Date().timeIntervalSince(t0) * 1000 * 10).rounded(.toNearestOrEven)) / 10
    let noteSaid = "an observation, of a world that has not entered: git objects, and a walk. "
        + (thin.isEmpty
           ? many(revs.count, "revision") + " of the contract were read, and the library's "
             + "history walked once. "
           : "no history to date anything: " + thin.joined(separator: " and ")
             + " arrived with one commit standing in for all of them. ")
        + "Absence is a fact about this walk: " + many(carrier.files, "file") + " under "
        + absPath(clientRoot) + ", kinds " + CARRIER_KINDS.joined(separator: " ")
        + ", skipping " + carrier.said
        + (undatable.isEmpty ? ""
           : "; " + many(undatable.count, "name") + " cannot be dated, being already declared "
             + "when the window opened")
    let nextSaid = thin.isEmpty
        ? "re-run it yourself: everything above is a git object or a walk whose bounds "
          + "are printed with it"
        : "git fetch --unshallow in \(thin[0]), and the dates become readable"
    let red = over != nil && median > over!
    if asJson {
        var pairs: [(String, StatusJSON)] = [
            ("command", .text("drift")),
            ("contract", .text((src as NSString).lastPathComponent)),
            ("carrier", .text(who)),
            ("revisions", .raw(String(revs.count))),
            ("declares", .raw(String(current.count))),
            ("since", since.map { .text($0) } ?? .null),
            ("thin", .list(thin.map { .text($0) })),
            ("scope", .object([("files", .raw(String(carrier.files))),
                               ("root", .text(absPath(clientRoot))),
                               ("kinds", .text(CARRIER_KINDS.joined(separator: " "))),
                               ("skipped", .text(carrier.said))])),
            ("unwritten", .list(unwritten.map { .text($0) })),
            ("silent_routes", .list(silent.map { .text($0) })),
            ("late", .raw(String(late.count))),
            ("median_days", .raw(String(median))),
            ("worst_days", .raw(String(late.first?.days ?? 0))),
            ("worst", .list(worst.map { .object([
                ("field", .text($0.field)), ("contract", .text($0.contract)),
                ("carrier", .text($0.carrier)), ("days", .raw(String($0.days)))]) })),
            ("undatable", .raw(String(undatable.count))),
            ("over_threshold", .raw(red ? "true" : "false")),
            ("threshold", over.map { .raw(String($0)) } ?? .null),
            ("ms", .raw(String(ms))),
            ("note", .text(noteSaid)),
            ("next", .text(nextSaid)),
        ]
        if let ready = commandIn(nextSaid) { pairs.append(("command_to_run", .text(ready))) }
        out(statusDumps(.object(pairs), 0) + "\n")
        exit(red ? 1 : 0)
    }
    var head = "drift: observation of \(who) against \((src as NSString).lastPathComponent)"
    if !thin.isEmpty {
        head += " · no history here, so nothing is dated"
    } else if !late.isEmpty {
        head += " · behind on " + many(late.count, "name") + " · median "
              + many(median, "day") + " · worst \(late.first!.days)"
    } else {
        head += " · nothing arrived late"
    }
    var lines = [head]
    for w in worst {
        lines.append("  in history · \(w.field) · the contract's earliest revision saying it is "
                   + "\(w.contract), the library's earliest commit writing it \(w.carrier): "
                   + "\(w.days) days")
    }
    for n in unwritten.prefix(5) {
        lines.append("  in this walk · \(n) · the contract declares it; no file walked writes it")
    }
    if unwritten.count > 5 {
        lines.append("  … and \(unwritten.count - 5) more names no file walked writes")
    }
    for r in silent.prefix(3) {
        lines.append("  in this walk · \(r) · the contract declares this route; no file walked "
                   + "spells its segments")
    }
    if red {
        lines.append("  threshold: you set --fail-over \(over!), and the median is "
                   + "\(median) — this exits non-zero by your rule, not by a verdict")
    }
    lines.append("  note: " + noteSaid)
    lines.append("  next: " + nextSaid)
    out(lines.joined(separator: "\n") + "\n")
    exit(red ? 1 : 0)
}

// ── init [DIR] [--vendor]: entry, which is the act of taking performed once
// for somebody who has not typed anything yet. The letter and the reference
// arrive by the same verb everything arrives by, the hook wires itself where
// a .git stands, and --vendor makes the tool travel with the repository.
let INIT_HOOK = "#!/bin/sh\n"
    + "# the claims must hold before a commit is made (they are judged, never reprinted)\n"
    + "if [ -x ./gatew ]; then exec ./gatew status; fi\n"
    + "# a clone carries the tool at ./gate, which is the way the cover says to run it\n"
    + "# (\"no install step\"), so the hook looks there before it looks for an install\n"
    + "if [ -x ./gate ]; then exec ./gate status; fi\n"
    + "if command -v gate >/dev/null 2>&1; then exec gate status; fi\n"
    + "echo \"pre-commit: gate is not on PATH and there is no ./gatew here, so nothing\"\n"
    + "echo \"checked the claims in this repository. Put gate on PATH, run\"\n"
    + "echo \"gate init . --vendor to carry it here, or delete .githooks/pre-commit.\"\n"
    + "exit 1\n"

func copyItem(_ src: String, _ dst: String) {
    try? FileManager.default.removeItem(atPath: dst)
    try? FileManager.default.copyItem(atPath: src, toPath: dst)
}

func vendorInto(_ rootDir: String) -> (carried: [String], digest: String?, shim: String) {
    // the tool travels WITH the repository, the way ./gradlew does: one person
    // commits .gate/, and everybody who pulls has it
    let here = root.path
    let dst = (rootDir as NSString).appendingPathComponent(".gate")
    try? FileManager.default.createDirectory(
        atPath: (dst as NSString).appendingPathComponent("bin"),
        withIntermediateDirectories: true)
    var carried: [String] = []
    let pcli = (here as NSString).appendingPathComponent("bin/judge-cli.js")
    if FileManager.default.fileExists(atPath: pcli) {
        copyItem(pcli, (dst as NSString).appendingPathComponent("bin/judge-cli.js"))
    }
    for sub in ["web", "docs"] {
        try? FileManager.default.createDirectory(
            atPath: (dst as NSString).appendingPathComponent(sub),
            withIntermediateDirectories: true)
    }
    for rel in ["gate", "bin/judge.js", "bin/judge-where.js", "web/ui.html",
                "web/codemirror.js", "web/codemirror.css", "LICENSE", "docs/NOTICE.md"] {
        let src = (here as NSString).appendingPathComponent(rel)
        if FileManager.default.fileExists(atPath: src) {
            copyItem(src, (dst as NSString).appendingPathComponent(rel))
            carried.append(rel)
        }
    }
    let shelfSrc = (here as NSString).appendingPathComponent("stdlib")
    var isDir: ObjCBool = false
    if FileManager.default.fileExists(atPath: shelfSrc, isDirectory: &isDir), isDir.boolValue {
        let shelfDst = (dst as NSString).appendingPathComponent("stdlib")
        try? FileManager.default.createDirectory(atPath: shelfDst,
                                                 withIntermediateDirectories: true)
        for f in ((try? FileManager.default.contentsOfDirectory(atPath: shelfSrc)) ?? []).sorted() {
            copyItem((shelfSrc as NSString).appendingPathComponent(f),
                     (shelfDst as NSString).appendingPathComponent(f))
        }
        carried.append("stdlib/")
    }
    let jsrc = (here as NSString).appendingPathComponent("bin/gate-judge")
    var digest: String? = nil
    if FileManager.default.fileExists(atPath: jsrc) {
        let jdst = (dst as NSString).appendingPathComponent("bin/gate-judge")
        copyItem(jsrc, jdst)
        try? FileManager.default.setAttributes([.posixPermissions: 0o755], ofItemAtPath: jdst)
        digest = sha256Hex(FileManager.default.contents(atPath: jsrc) ?? Data())
        carried.append("bin/gate-judge")
        if FileManager.default.fileExists(atPath: jsrc + ".from") {
            copyItem(jsrc + ".from", jdst + ".from")
            carried.append("bin/gate-judge.from")
        }
    }
    try? FileManager.default.setAttributes(
        [.posixPermissions: 0o755],
        ofItemAtPath: (dst as NSString).appendingPathComponent("gate"))
    let shim = (rootDir as NSString).appendingPathComponent("gatew")
    try? ("#!/bin/sh\n# gate, carried by this repository. Nothing to install.\n"
          + "exec python3 \"$(dirname \"$0\")/.gate/gate\" \"$@\"\n")
        .write(toFile: shim, atomically: false, encoding: .utf8)
    try? FileManager.default.setAttributes([.posixPermissions: 0o755], ofItemAtPath: shim)
    let readme = "# gate, carried by this repository\n\n"
        + "Run `./gatew status`. Nothing to install: this directory is the tool\n"
        + "itself, pinned by the commit that added it, so every clone judges with\n"
        + "the same judge and an old commit is judged by the judge it was written\n"
        + "with.\n\n"
        + "judge sha256: \(digest ?? "None")\n\n"
        + "The judge is rebuilt from a public corpus: `bin/build-judge.sh <pin>`\n"
        + "builds the same judge, and the battery checks a build,\n"
        + "`GATE_JUDGE=path tests/smoke.py`. The linker is not byte-stable, so\n"
        + "the hash above names what is here and is not the check.\n\n"
        + "MIT licensed: LICENSE and docs/NOTICE.md are here beside it.\n"
    try? readme.write(toFile: (dst as NSString).appendingPathComponent("README.md"),
                      atomically: false, encoding: .utf8)
    return (carried, digest, "./gatew")
}

if args.first == "init" {
    loadStatusShelf()
    let asJson = args.contains("--json")
    var a = Array(args.dropFirst()).filter { $0 != "--json" }
    let vendor = a.contains("--vendor")
    a = a.filter { $0 != "--vendor" }
    let hereIsWorld = FileManager.default.fileExists(atPath: "gate.swift")
        || FileManager.default.fileExists(atPath: "gate.manifest.swift")
    var isGitDir: ObjCBool = false
    let hasGit = FileManager.default.fileExists(atPath: ".git", isDirectory: &isGitDir)
        && isGitDir.boolValue
    let rootDir = a.first ?? ((hereIsWorld || hasGit) ? "." : "world")
    var made: [String] = []
    let hookRel = ".githooks/pre-commit"
    let hookPath = (rootDir as NSString).appendingPathComponent(hookRel)
    do {
        try FileManager.default.createDirectory(
            atPath: (hookPath as NSString).deletingLastPathComponent,
            withIntermediateDirectories: true)
    } catch {
        cannot("a world cannot be founded at \(rootDir): "
               + error.localizedDescription.lowercased(),
               "name a directory you can write in, or `gate init .` to found one here")
    }
    if !FileManager.default.fileExists(atPath: hookPath) {
        try? INIT_HOOK.write(toFile: hookPath, atomically: false, encoding: .utf8)
        made.append(hookRel)
    }
    try? FileManager.default.setAttributes([.posixPermissions: 0o755], ofItemAtPath: hookPath)
    var letter: String? = nil
    let manPath = (rootDir as NSString).appendingPathComponent("gate.manifest.swift")
    let layoutWas = FileManager.default.fileExists(atPath: manPath)
    // this world is founded HERE, so every row entry writes belongs to it and
    // not to a world overhead
    FOUNDING = absPath(rootDir)
    var declaredPages = Set<String>()
    if let t = readText(manPath) {
        for m in matches("typeName:\\s*String\\s*\\{\\s*\"([^\"]+)\"\\s*\\}", t) {
            declaredPages.insert((m[0] as NSString).lastPathComponent)
        }
    }
    if STDLIB_TEXTS["readme"] != nil, !declaredPages.contains("readme.swift") {
        let (took, _) = takeShelf("readme", rootDir)
        if let took = took {
            letter = took.wrote
            made += [took.wrote] + took.with
        }
    }
    if STDLIB_TEXTS["verbs"] != nil, !declaredPages.contains("verbs.swift") {
        let (tookRef, _) = takeShelf("verbs", rootDir)
        if let tookRef = tookRef { made += [tookRef.wrote] + tookRef.with }
    }
    if !layoutWas, FileManager.default.fileExists(atPath: manPath) {
        made.append("gate.manifest.swift")
    }
    let vendored = vendor ? vendorInto(rootDir) : nil
    var hooksNote: String? = nil
    var undo: String? = nil
    var gitDir: ObjCBool = false
    if FileManager.default.fileExists(
        atPath: (rootDir as NSString).appendingPathComponent(".git"),
        isDirectory: &gitDir), gitDir.boolValue {
        let prior = runGit(["config", "--local", "core.hooksPath"], rootDir)
            .trimmingCharacters(in: .whitespacesAndNewlines)
        _ = runGit(["config", "core.hooksPath", ".githooks"], rootDir)
        var note = "pre-commit hook wired (core.hooksPath = .githooks)"
        undo = prior.isEmpty ? "git config --unset core.hooksPath"
                             : "git config core.hooksPath " + prior
        if !prior.isEmpty { note += ". It was " + prior }
        let gatew = (rootDir as NSString).appendingPathComponent("gatew")
        let gateHere = (rootDir as NSString).appendingPathComponent("gate")
        let onPath = (ProcessInfo.processInfo.environment["PATH"] ?? "")
            .components(separatedBy: ":").contains(where: {
                FileManager.default.isExecutableFile(
                    atPath: ($0 as NSString).appendingPathComponent("gate")) })
        if !(FileManager.default.isExecutableFile(atPath: gatew)
             || FileManager.default.isExecutableFile(atPath: gateHere) || onPath) {
            note += ". It will not find gate from here, and will refuse every commit "
                  + "until it can: run `gate init . --vendor` to carry the tool in "
                  + "this repository, or put gate on PATH"
        }
        hooksNote = note
    }
    var observed: String? = nil
    if hooksNote != nil {
        let signed = runGit(["config", "user.name"], rootDir)
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if !signed.isEmpty {
            observed = "read from git, and not judged: commits in this clone are signed "
                     + signed + ". If that is you, say so in my.swift. Nothing here writes "
                     + "your name for you"
        }
    }
    FOUNDING = nil
    // the command that makes a world knows the world it made: the rung is for
    // the repository as it stands now
    let w2 = WorldState(facts: (absPath(rootDir) as NSString)
                            .appendingPathComponent("gate.swift"),
                        tables: nil,
                        layout: layoutRowsFull(absPath(rootDir)).manifest.map {
                            Layout(manifest: $0, rows: layoutRowsFull(absPath(rootDir)).rows) })
    let next = nextRung(w2, false)
    if asJson {
        var pairs: [(String, StatusJSON)] = [
            ("command", .text("init")),
            ("root", .text(rootDir)),
            ("created", .list(made.map { .text($0) })),
            ("hooks", hooksNote.map { .text($0) } ?? .null),
            ("readme", letter.map { .text($0) } ?? .null),
            ("observed", observed.map { .text($0) } ?? .null),
            ("next", .text(next)),
            ("undo_hooks", undo.map { .text($0) } ?? .null),
            ("changed_git_config", .raw(hooksNote != nil ? "true" : "false")),
            ("vendored", vendored.map { v in .object([
                ("carried", .list(v.carried.map { .text($0) })),
                ("judge_sha256", v.digest.map { .text($0) } ?? .null),
                ("shim", .text(v.shim))]) } ?? .null),
        ]
        if let ready = commandIn(next) { pairs.append(("command_to_run", .text(ready))) }
        out(statusDumps(.object(pairs), 0) + "\n")
        exit(0)
    }
    var lines = ["init: " + rootDir
                 + (made.isEmpty ? " · already there" : " · created " + many(made.count, "file"))]
    lines.append("  next: " + next)
    if let h = hooksNote { lines.append("  " + h) }
    if let u = undo { lines.append("  to undo that one git setting: " + u) }
    if let o = observed { lines.append("  " + o) }
    if let v = vendored {
        lines.append("  gate now travels with this repository: .gate/ + " + v.shim)
        lines.append("  commit it, and every clone has the tool. Nothing to install")
        if let d = v.digest {
            lines.append("  judge sha256: " + String(d.prefix(16)) + "…")
        }
    }
    out(lines.joined(separator: "\n") + "\n")
    exit(0)
}

// ── mine PATH [--role R] · theirs PATH --at REV: one account, two directions,
// and nobody special. What I emit is judged and moves the verdict; what I took
// I took from somewhere at something, and that is a fact about it the way its
// path is. The writing side of the layout landed with the roads; this is the
// verb over it, moved whole: the account listing, the taking of a shelf world,
// the forgetting, and the pin that refuses to move.
let MOVING_NAMES: Set<String> = ["latest", "head", "tip", "main", "master", "trunk",
                                 "default", "stable", "edge", "dev", "develop",
                                 "nightly", "current", "next"]

func movingPin(_ at: String?) -> String? {
    // a pin names a moment, and this is why: a seam's verdict is a pure
    // function of two fixed texts, and a range or a moving name breaks the
    // precondition under which the question has an answer at all
    let a = (at ?? "").trimmingCharacters(in: .whitespaces)
    if a.isEmpty { return "a revision nobody wrote down" }
    if MOVING_NAMES.contains(a.lowercased()) {
        return "`\(a)` is a name that moves: whatever it points at today, it points somewhere "
             + "else tomorrow, and a row that says it stops being a fact the moment it is true"
    }
    if !matches("[\\^~*]|[<>]=?|,\\s*[<>^~]|\\|\\|", a).isEmpty {
        return "`\(a)` is a range, not a revision: it names a SET of revisions, and this world "
             + "took exactly one"
    }
    if matchAt(a, "[\\d.]*[xX](\\.[\\dxX]+)*$") != nil, !matches("\\d", a).isEmpty {
        return "`\(a)` is a range with a wildcard in it, and this world took exactly one revision"
    }
    return nil
}

func foundsWorld(_ path: String) -> Bool {
    // true when this claim would found a world rather than join one
    let rootDir = worldRootFor(path)
    return !(FileManager.default.fileExists(atPath: (rootDir as NSString)
                 .appendingPathComponent("gate.swift"))
        || FileManager.default.fileExists(atPath: (rootDir as NSString)
                 .appendingPathComponent("gate.manifest.swift")))
}

func forgetSide(_ relSaid: String, _ d: String) -> (mp: String?, row: LayoutRow?) {
    // unsubscribing is deleting a line, by braces and never by shape: the row
    // is an enum body and an extension body, and the file itself is not touched
    let mp = (d as NSString).appendingPathComponent("gate.manifest.swift")
    guard FileManager.default.fileExists(atPath: mp), let text = readText(mp)
    else { return (nil, nil) }
    let (rows, _) = layoutRowsFull(d)
    guard let row = rows.first(where: { $0.path == relSaid }), let n = row.name
    else { return (nil, nil) }
    var out: [String] = []
    let lines = text.components(separatedBy: "\n")
    var i = 0
    while i < lines.count {
        if lines[i].hasPrefix("public enum " + n + ":") || lines[i].hasPrefix("extension " + n + " ")
            || lines[i].hasPrefix("extension " + n + "{") {
            var depth = lines[i].filter { $0 == "{" }.count - lines[i].filter { $0 == "}" }.count
            i += 1
            while depth > 0 && i < lines.count {
                depth += lines[i].filter { $0 == "{" }.count - lines[i].filter { $0 == "}" }.count
                i += 1
            }
            continue
        }
        out.append(lines[i])
        i += 1
    }
    do { try out.joined(separator: "\n").write(toFile: mp, atomically: false, encoding: .utf8) }
    catch {
        cannot(mp + " cannot be written here: " + error.localizedDescription.lowercased(),
               "the row is still in the layout: nothing was changed")
    }
    return ((mp as NSString).lastPathComponent, row)
}

func declareSideHere(_ path: String, _ kind: String, _ role: String, _ frm: String?,
                     _ written: String? = nil, _ opens: String? = nil)
    -> (declared: String?, refused: String?) {
    // the writing road with a file at the end of it: the same bytes the
    // reading side proved, landed where the world's own walk says
    let d = worldRootFor(path)
    let mp = (d as NSString).appendingPathComponent("gate.manifest.swift")
    let rel = relPath(absPath(path), d)
    if rel.components(separatedBy: "/").first == ".." || leavesWorldHere(rel, d) {
        return (nil, path + " is not inside the world at " + d + ": a row says where a "
                     + "file is relative to the world that declares it")
    }
    let text = FileManager.default.fileExists(atPath: mp)
        ? theirsText(mp, "the layout of this world") : manifestHead()
    let said = upsertRow(text, name: rowAtom(rel), rel: rel, kind: kind, role: role,
                         from: frm, written: written, opens: opens)
    do { try said.write(toFile: mp, atomically: false, encoding: .utf8) } catch {
        cannot(mp + " cannot be written here: " + error.localizedDescription.lowercased(),
               "name a path you can write, and the row will have a home")
    }
    return ((mp as NSString).lastPathComponent, nil)
}

struct Took { var wrote: String; var with: [String]; var declaredIn: String
              var from: String?; var court: String }

func takeShelf(_ mod: String, _ into: String = ".") -> (took: Took?, dest: String) {
    // one act of taking, and every door uses it: a copy lands where they
    // stand, carrying where it came from, declared in the same movement
    let dest = absPath((into as NSString).appendingPathComponent(mod + ".swift"))
    if FileManager.default.fileExists(atPath: dest) { return (nil, dest) }
    let roleSaid = shelfHeadLine(mod, "// role:")
    let court = STATUS_ROLES.contains(where: { $0.0 == roleSaid }) ? roleSaid! : "forms"
    let came = judgeFrom()
    var body = (STDLIB_TEXTS[mod] ?? "").components(separatedBy: "\n")
    let opens = body.prefix(8).map { $0.trimmingCharacters(in: .whitespaces) }
        .first(where: { $0.hasPrefix("// opens:") })
    let written = body.prefix(8).first(where: { $0.contains("written in") && $0.hasPrefix("//") })?
        .trimmingCharacters(in: .whitespaces)
    let grammar = matches("stdlib show ([\\w-]+)", written ?? "").first?.first
    while let first = body.first, first.hasPrefix("//") { body.removeFirst() }
    let view = opens.flatMap { matches("opens:\\s*(\\S+)", $0).first?.first }?
        .trimmingCharacters(in: .whitespaces).lowercased()
    var page = "// This copy is yours: read it, change it, break it, delete it when you are\n"
             + "// done.\n"
    var middle = body.joined(separator: "\n")
    while middle.hasSuffix("\n") { middle.removeLast() }
    while middle.hasPrefix("\n") { middle.removeFirst() }
    page += "\n" + middle + "\n"
    page += "\n// Origin: gate's shelf"
    page += came.map { ", built from \($0.prefix(7))" } ?? ""
    page += ". `gate stdlib show \(mod)` prints what shipped, unchanged,\n"
          + "// for comparing or restoring by hand. Deleting this file and its row in\n"
          + "// `gate.manifest.swift` removes it completely.\n"
    do { try page.write(toFile: dest, atomically: false, encoding: .utf8) } catch {
        cannot(dest + " cannot be written here: " + error.localizedDescription.lowercased(),
               "stand in a directory you can write, and the copy lands beside you")
    }
    // the grammar arrives FIRST, so the row for this page can point at its row
    var withIt: [String] = []
    var grammarAtom: String? = nil
    if let g = grammar, g != mod, STDLIB_TEXTS[g] != nil {
        let (also, adest) = takeShelf(g, into)
        grammarAtom = rowAtom(relPath(adest, absPath(into)))
        if let also = also { withIt.append(also.wrote) }
    }
    let (mp, _) = declareSideHere(dest, "Mine", court, nil,
                                  grammarAtom, view.map { $0.prefix(1).uppercased() + $0.dropFirst() })
    return (Took(wrote: relPath(dest, absPath(into)), with: withIt,
                 declaredIn: mp ?? "gate.manifest.swift", from: came, court: court), dest)
}

if args.first == "mine" || args.first == "theirs" {
    loadStatusShelf()
    let kind = args.first == "mine" ? "Mine" : "Theirs"
    let word = args.first!
    let asJson = args.contains("--json")
    let a = Array(args.dropFirst()).filter { $0 != "--json" }
    func flagValue(_ flag: String) -> String? {
        guard let i = a.firstIndex(of: flag) else { return nil }
        return i + 1 < a.count ? a[i + 1] : nil
    }
    // a flag as the last word names nothing, and the sentence for a missing
    // value already stands downstream: the same guard the other carrier keeps
    let role = a.contains("--role") ? flagValue("--role")
                                    : (kind == "Mine" ? "world" : "seam")
    let at = flagValue("--at")
    var rest = a.filter { !$0.hasPrefix("--") }
    for flag in ["--role", "--at"] {
        if let v = flagValue(flag) { rest = rest.filter { $0 != v } }
    }
    let roleList = STATUS_ROLES.map { $0.0 }.joined(separator: "|")
    let usage = "gate \(word) PATH" + (kind == "Mine" ? "" : " --at REV")
              + " [--role " + roleList + "] · gate \(word) PATH --forget"

    func answer(_ pairs: [(String, StatusJSON)], _ human: [String]) -> Never {
        if asJson { out(statusDumps(.object(pairs), 0) + "\n") }
        else { out(human.joined(separator: "\n") + "\n") }
        exit(0)
    }
    func asks(_ note: String, _ next: String) -> Never {
        answer([("command", .text(word)), ("asks", .raw("true")),
                ("note", .text(note)), ("next", .text(next))],
               ["usage: " + note, "  next: " + next])
    }
    if rest.isEmpty {
        // the same word asks and answers: with a path it declares, with none
        // it is the account an owner actually has
        let w = discoverWorld()
        let d = w.facts.map { (absPath($0) as NSString).deletingLastPathComponent }
            ?? FileManager.default.currentDirectoryPath
        let (rows, _) = layoutRowsFull(d)
        let held = rows.filter { $0.source == word }
        if held.isEmpty {
            asks(usage, kind == "Mine"
                 ? "a file you emit, judged with the rest of your world"
                 : "a file you took from somewhere, at the revision you took it at")
        }
        var lines = ["\(word): \(held.count)"]
        for h in held {
            let atSaid = h.from.map { " · at \($0)" } ?? ""
            let file = h.path.padding(toLength: max(28, h.path.count), withPad: " ",
                                      startingAt: 0)
            let roleSaid = (h.role?.isEmpty ?? true) ? "unsaid" : h.role!
            lines.append("  " + file + " "
                         + roleSaid.padding(toLength: max(7, roleSaid.count), withPad: " ",
                                            startingAt: 0) + atSaid)
        }
        lines.append("  next: `gate \(word) FILE --forget` takes one out of the list, "
                     + "and leaves the file alone")
        answer([("command", .text(word)),
                ("held", .list(held.map { .object([
                    ("file", .text($0.path)),
                    ("role", $0.role.map { .text($0) } ?? .null),
                    ("at", $0.from.map { .text($0) } ?? .null)]) })),
                ("note", .text(usage)), ("mutates", .raw("false"))], lines)
    }
    let path = rest[0]
    if a.contains("--forget") {
        let d = worldRootFor(path)
        let (mp, row) = forgetSide(relPath(absPath(path), d), d)
        guard let mp = mp, let row = row else {
            asks("\((path as NSString).lastPathComponent) is not in your list",
                 "gate \(word) — what is in it")
        }
        answer([("command", .text(word)), ("forgot", .text(row.path)),
                ("declared_in", .text(mp)), ("mutates", .raw("true")),
                ("note", .text("out of your account. The file is still on disk: taking a thing "
                             + "out of your list is not throwing it away, and that second act "
                             + "is yours alone")),
                ("next", .text("delete the file too if you meant that: a commit like any "
                             + "other, visible and dated"))],
               ["\(word): \(row.path) · out of \(mp)",
                "  the file is still on disk: that is a separate act, and yours",
                "  next: delete the file too if you meant that: a commit like any "
                + "other, visible and dated"])
    }
    // making something yours is the third verb: a shelf world taken in hand,
    // copied here, declared in the same movement, judged from that second
    if kind == "Mine", !FileManager.default.fileExists(atPath: path),
       STDLIB_TEXTS[path] != nil {
        let (took, _) = takeShelf(path)
        guard let took = took else {
            asks("\(path).swift is already here",
                 "gate \(word) \(path).swift — declare the copy you have, or move it "
                 + "aside first: nothing here overwrites a file you wrote")
        }
        answer([("command", .text(word)), ("made_mine", .text(path)),
                ("wrote", .text((took.wrote as NSString).lastPathComponent)),
                ("with", .list(took.with.map { .text($0) })),
                ("court", .text(took.court)),
                ("declared_in", .text(took.declaredIn)),
                ("from", took.from.map { .text($0) } ?? .null),
                ("mutates", .raw("true")),
                ("note", .text("\(path) is yours: a copy is here, declared, and judged from "
                             + "now on. What the shelf ships is unchanged and still shipped. "
                             + "Yours simply stands where it stood")),
                ("next", .text("gate status: it is judged with the rest of your world"))],
               ["\(word): \(path) is yours · wrote \((took.wrote as NSString).lastPathComponent)"
                + (took.with.isEmpty ? "" : " and " + took.with.joined(separator: " and "))
                + (took.from.map { " · from the judge at \($0.prefix(7))" } ?? ""),
                "  note: \(path) is yours: a copy is here, declared, and judged from now on. "
                + "What the shelf ships is unchanged and still shipped. Yours simply stands "
                + "where it stood",
                "  next: gate status: it is judged with the rest of your world"])
    }
    if !FileManager.default.fileExists(atPath: path) {
        cannot("no file at \(path)",
               kind == "Mine"
               ? "bring the file here first, or name one this tool ships: "
                 + SHELF_ORDER.sorted().joined(separator: " · ")
               : "bring the file here first. gate never fetches: a file of theirs "
                 + "arrives by a checkout, a copy, a vendor step you already trust")
    }
    if !STATUS_ROLES.contains(where: { $0.0 == role }) {
        cannot("`\(role ?? "None")` is not a court anything here reads",
               "a row says what it is for: "
               + STATUS_ROLES.map { "`\($0.0)` — \($0.1)" }.joined(separator: " · "))
    }
    if kind == "Theirs", let at = at, !at.isEmpty, let moving = movingPin(at) {
        asks(moving,
             "write down the revision you actually took: a commit, a tag, a release. "
             + "What holds between two sides is a fact about two fixed texts. Name a "
             + "moving one and there is nothing for it to be a fact about, which is "
             + "the whole reason nothing here has to be solved")
    }
    if kind == "Theirs" && (at == nil || at!.isEmpty) {
        cannot("what is taken is taken at a revision, and this one says none",
               "gate theirs \((path as NSString).lastPathComponent) --at REV — a commit, a "
               + "tag, a release: whatever the source calls the thing you actually took")
    }
    let here = absPath(".")
    let outside = relPath(absPath(path), here).components(separatedBy: "/").first == ".."
    if outside && foundsWorld(path) {
        asks("\(path) is not inside the world here, and there is no world around it",
             "a world is founded where you stand: run this from the directory that "
             + "world is in, or bring the file into this one. A world judges what "
             + "is in it")
    }
    let (rows2, _) = layoutRowsFull(worldRootFor(path))
    let rel2 = relPath(absPath(path), worldRootFor(path))
    if let said = rows2.first(where: { $0.path == rel2 }) {
        asks("\(rel2) is already declared, as `\(said.name ?? "None")` "
             + "(\(said.source), \(said.role ?? "None"))",
             "gate \(word) \(rel2) --forget, then say it again — a file is declared "
             + "once, or the list stops being an account of anything")
    }
    let (mp, refused) = declareSideHere(path, kind, role!, at)
    if let refused = refused {
        asks(refused,
             "bring the file into the world first. A world judges what is in "
             + "it, and a row that points outside is a claim it cannot keep")
    }
    let roleMeans = STATUS_ROLES.first(where: { $0.0 == role })!.1
    let file = (path as NSString).lastPathComponent
    if kind == "Mine" {
        answer([("command", .text(word)), ("file", .text(file)),
                ("declared_in", .text(mp!)), ("role", .text(role!)),
                ("role_means", .text(roleMeans)), ("mutates", .raw("true")),
                ("note", .text("mine: I emit it, it is judged with the rest of my world, and "
                             + "changing it changes the verdict")),
                ("next", .text("gate status: it is judged from here on"))],
               ["\(word): \(file) · written down in \(mp!)",
                "  role `\(role!)` — \(roleMeans)",
                "  next: gate status: it is judged from here on"])
    }
    let nextSaid = role == "seam"
        ? "gate attention: what now waits for a word, read the same from either side"
        : "gate status: the row is accounted for, and its court is `" + role! + "`"
    answer([("command", .text(word)), ("file", .text(file)),
            ("declared_in", .text(mp!)), ("role", .text(role!)),
            ("role_means", .text(roleMeans)), ("mutates", .raw("true")),
            ("at", .text(at!)),
            ("note", .text("theirs, taken at \(at!): I read it and never rewrite it. To move "
                         + "it, take it again at a newer revision. There is nothing here to "
                         + "solve")),
            ("next", .text(nextSaid))],
           ["\(word): \(file) · took it at \(at!) · written down in \(mp!)",
            "  role `\(role!)` — \(roleMeans)",
            "  next: " + nextSaid])
}

// ── log: the repository's own history, projected and never judged ──
//
// A commit is closed iff it is reachable from the default branch. The world's
// history is git's own filtering by pathspec over the files the layout declares,
// which is why this needed the reader above; asking for a world's history where
// no file is declared one narrows nothing, and the line says so rather than
// printing the repository under the word `the world`.
if args.first == "log" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    let known: Set<String> = ["all", "--all", "world", "--world"]
    if let stray = rest.first(where: { !known.contains($0) && Int($0) == nil }) {
        let note = "`" + stray + "` is not a word this command knows"
        let next = "gate log  the world's history · gate log all  the repository's · "
                 + "gate log N  how many · and `MyJournal` declares what you get "
                 + "when you say none of them"
        if asJson {
            out("{\n  \"command\": \"log\",\n  \"asks\": true,\n"
                + "  \"note\": " + jsonString(note) + ",\n"
                + "  \"next\": " + jsonString(next) + "\n}\n")
        } else {
            out("usage: " + note + "\n  next: " + next + "\n")
        }
        exit(0)
    }
    let here = FileManager.default.currentDirectoryPath
    let (rows, manifest) = manifestRows(here)
    let facts = (here as NSString).appendingPathComponent("gate.swift")
    let base = here
    let limit = rest.compactMap { Int($0) }.first ?? 200

    // which files this world is made of: the plain court's own list, and the
    // forms rows beside it, because whose history this is does not depend on
    // which court reads the file
    var world = Set<String>()
    if FileManager.default.fileExists(atPath: facts) { world.insert("gate.swift") }
    if manifest != nil {
        for r in rows where r.role == "world" || r.role == "forms" {
            if FileManager.default.fileExists(atPath: (here as NSString).appendingPathComponent(r.path)) {
                world.insert(r.path)
            }
        }
    }
    let policy = (here as NSString).appendingPathComponent("gate.policy.swift")
    if FileManager.default.fileExists(atPath: policy) { world.insert("gate.policy.swift") }

    // a word typed now outranks a standing declaration, the way it does
    // everywhere else; with no word, the wheel the operator turned answers
    let personalRoot = ProcessInfo.processInfo.environment["GATE_ME"]
        ?? ((NSHomeDirectory() as NSString).appendingPathComponent(".gate/me"))
    let mine = (personalRoot as NSString)
        .appendingPathComponent("worlds/" + repoKey(base) + "/my.swift")
    var wheelFiles = world.sorted().map { (here as NSString).appendingPathComponent($0) }
    if !world.isEmpty { wheelFiles.append(mine) }
    let wheel = world.isEmpty ? [:] : turned("Journal", base, wheelFiles)
    // the FIRST word decides, which is what the other carrier reads: `gate log 1
    // all` says a count and then a word the reading never reaches, and a vein
    // that answered the word would be a second opinion about one argv
    let firstWord = rest.first ?? ""
    var scope = "world"
    if firstWord == "all" || firstWord == "--all" { scope = "all" }
    else if firstWord == "world" || firstWord == "--world" { scope = "world" }
    else if wheel["Scope"] == "AllRepo" { scope = "all" }
    let onlyMe = wheel["Author"] == "Me"
    let who = identities(base)

    var branch = ""
    for candidate in ["origin/HEAD", "main", "master"] {
        let said = runGit(["rev-parse", "--verify", "-q", candidate], base)
        if !said.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            branch = candidate
            break
        }
    }
    var merged = Set<String>()
    if !branch.isEmpty {
        merged = Set(runGit(["rev-list", branch], base)
            .split(whereSeparator: { $0 == "\n" || $0 == " " }).map(String.init))
    }
    let narrowed = !(scope == "world" && world.isEmpty)
    var arguments = ["log", "--all", "-\(limit)", "--format=%x01%H%x1f%ae%x1f%aI%x1f%s", "--name-only"]
    if scope == "world" && !world.isEmpty { arguments += ["--"] + world.sorted() }
    let said = runGit(arguments, base)

    struct Commit { var hash = "", email = "", when = "", subject = ""
                    var files: [String] = []; var touches = false; var closed: Bool? = nil }
    var commits: [Commit] = []
    for line in said.components(separatedBy: "\n") {
        if line.hasPrefix("\u{01}") {
            let parts = String(line.dropFirst()).components(separatedBy: "\u{1f}")
            var c = Commit()
            c.hash = parts.count > 0 ? parts[0] : ""
            c.email = parts.count > 1 ? parts[1] : ""
            c.when = parts.count > 2 ? parts[2] : ""
            c.subject = parts.count > 3 ? parts[3] : ""
            c.closed = merged.isEmpty ? nil : merged.contains(c.hash)
            commits.append(c)
        } else if !line.trimmingCharacters(in: .whitespaces).isEmpty, !commits.isEmpty {
            let f = line.trimmingCharacters(in: .whitespaces)
            commits[commits.count - 1].files.append(f)
            if world.contains(f) { commits[commits.count - 1].touches = true }
        }
    }
    let me = runGit(["config", "user.email"], base).trimmingCharacters(in: .whitespacesAndNewlines)
    if onlyMe && !me.isEmpty { commits = commits.filter { $0.email == me } }
    let nextSaid = world.isEmpty
        ? "run `gate demo` for a repository to look at, or drop a table you already export "
          + "into tables/ and run `gate status`"
        : "run `gate status` to have the judge read what these commits changed"

    if asJson {
        // built in pieces: one long concatenation put the type-checker past its
        // budget, and a shape this exact is easier to read a line at a time
        func arrayOf(_ items: [String], _ pad: String) -> String {
            if items.isEmpty { return "[]" }
            let inner = items.map { pad + "  " + jsonString($0) }.joined(separator: ",\n")
            return "[\n" + inner + "\n" + pad + "]"
        }
        var text = "{\n"
        text += "  \"command\": \"log\",\n"
        let branchSaid: String = branch.isEmpty ? "null" : jsonString(branch)
        text += "  \"default_branch\": " + branchSaid + ",\n"
        text += "  \"scope\": " + jsonString(scope) + ",\n"
        text += "  \"limit\": " + String(limit) + ",\n"
        text += "  \"mine_only\": " + (onlyMe ? "true" : "false") + ",\n"
        text += "  \"narrowed\": " + (narrowed ? "true" : "false") + ",\n"
        text += "  \"next\": " + jsonString(nextSaid) + ",\n"
        text += "  \"me\": " + jsonString(me) + ",\n"
        text += "  \"world_files\": " + arrayOf(world.sorted(), "  ") + ",\n"
        var blocks: [String] = []
        for c in commits {
            var one = "    {\n"
            one += "      \"hash\": " + jsonString(c.hash) + ",\n"
            one += "      \"short\": " + jsonString(String(c.hash.prefix(8))) + ",\n"
            one += "      \"email\": " + jsonString(c.email) + ",\n"
            let personSaid: String = who[c.email].map { jsonString($0) } ?? "null"
            one += "      \"person\": " + personSaid + ",\n"
            one += "      \"when\": " + jsonString(c.when) + ",\n"
            one += "      \"subject\": " + jsonString(c.subject) + ",\n"
            one += "      \"files\": " + arrayOf(c.files, "      ") + ",\n"
            one += "      \"touches_world\": " + (c.touches ? "true" : "false") + ",\n"
            let closedSaid: String = c.closed == nil ? "null" : (c.closed! ? "true" : "false")
            one += "      \"closed\": " + closedSaid + "\n"
            one += "    }"
            blocks.append(one)
        }
        let commitsSaid: String = blocks.isEmpty ? "[]"
            : "[\n" + blocks.joined(separator: ",\n") + "\n  ]"
        text += "  \"commits\": " + commitsSaid
        if let ready = commandIn(nextSaid) {
            text += ",\n  \"command_to_run\": " + jsonString(ready)
        }
        text += "\n}\n"
        out(text)
        exit(0)
    }
    var what = (scope == "world" && !world.isEmpty) ? "the world's history" : "the repository"
    if !narrowed { what += ": no file here is declared a world file, so there is nothing narrower" }
    var lines = ["log: " + many(commits.count, "commit") + " · " + what
                 + " · observed, not judged · closed = reachable from "
                 + (branch.isEmpty ? "?" : branch)]
    for c in commits {
        let state = c.closed == nil ? "?" : (c.closed! ? "closed" : "open")
        let said = who[c.email] ?? c.email
        let star = c.touches ? " *" : ""
        lines.append("  " + String(c.hash.prefix(8)) + " " + state.padding(toLength: 6, withPad: " ", startingAt: 0)
                     + " " + String(c.when.prefix(10)) + " "
                     + said.padding(toLength: max(20, said.count), withPad: " ", startingAt: 0)
                     + " " + c.subject + star)
    }
    lines.append("  next: " + nextSaid)
    out(lines.joined(separator: "\n") + "\n")
    exit(0)
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
        // ── AND A WORLD NAMED WITH NOWHERE TO PRINT IT IS A MISTAKE, NOT A
        // QUESTION. `export` bare is somebody learning what the verb takes;
        // `export gate.swift -o one.csv` is half a sentence, and the nought exit
        // told a script the two tables were written. The python side splits it
        // the same way, and this vein carries the verb.
        if !(rest.isEmpty || (rest.count == 1 && rest[0].hasPrefix("-"))) {
            cannot("export prints two tables and needs both named: "
                   + "`gate export gate.swift -o people.csv grants.csv`",
                   "name the two files, and each is printed for the round-trip diff "
                   + "against the table you imported")
        }
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
    guard FileManager.default.fileExists(atPath: world) else {
        cannot("no such world: \(world)",
               "name the file your world is written in, or `gate init .` to start one")
    }
    let text = theirsText(world, "the world to print back")
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
        out("export: " + many(rows.count, "person", "people") + ", "
            + many(grants.count, "grant") + " → "
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
func courtSays(_ asked: [String]) -> String {
    let bin = URL(fileURLWithPath: CommandLine.arguments[0]).resolvingSymlinksInPath().path
    let words: [String] = [bin, "judge"] + asked
#if canImport(Darwin)
    var fds: [Int32] = [0, 0]
    guard pipe(&fds) == 0 else { return "" }
    var actions: posix_spawn_file_actions_t?
    posix_spawn_file_actions_init(&actions)
    posix_spawn_file_actions_adddup2(&actions, fds[1], 1)
    // the court's stderr is captured and dropped, the way the other carrier's
    // judge_call captures both channels: a court asked about nothing says so
    // on stderr, and that sentence is the caller's to keep or to swallow
    let quiet = open("/dev/null", O_WRONLY)
    if quiet >= 0 { posix_spawn_file_actions_adddup2(&actions, quiet, 2) }
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
    if quiet >= 0 { close(quiet) }
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
    p.standardError = Pipe()
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
        // ── AND ONE SIDE OF TWO IS A MISTAKE, NOT A QUESTION. `gate seam` bare
        // is somebody learning what the verb takes and answers with a usage
        // line and a nought exit. `gate seam api.swift` is somebody who meant a
        // pair and named half of it, and the same nought exit tells a script
        // the two sides agree. The python side splits these the same way; this
        // vein carries the verb, so the split has to stand on both.
        if !rest.isEmpty { cannot(note, nextAsked) }
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
        // a file that is not there and a file that is not text are two
        // sentences, and the door says whichever one is true
        guard FileManager.default.fileExists(atPath: p) else {
            cannot("no such side: \(p)",
                   "both sides are files: `gate declare contract SPEC -o api.swift` and "
                   + "`gate declare carrier DECL.json -o sdk.swift` write them")
        }
        side.append(theirsText(p, "the side of the pair you named"))
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
    let said = courtSays(["where", path])
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
    var told = many(claims.count, "claim") + " judged"
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
