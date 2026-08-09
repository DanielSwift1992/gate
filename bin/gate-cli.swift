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
    out("stdlib\nexport\nseam\nlog\naside\n")
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
        case "t":
            i += 4; return .yes
        case "f":
            i += 5; return .no
        case "n":
            i += 4; return .nothing
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
    return i >= chars.count ? said : said
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
