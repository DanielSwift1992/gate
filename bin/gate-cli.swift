// The CLI: one file, every verb this tool answers, with the court compiled in
// at the judge's own pin.
//
// It arrived here by a strangler. A python CLI answered these verbs first, and
// each one moved across held byte for byte against the side it was leaving,
// until the ledger below named all twenty-seven and there was nothing left on
// that side to hold. `--carries` still prints that ledger, one vein per line,
// each a prefix of an argv: the list of what this binary answers lives here,
// next to the code that answers for it, and nothing else keeps a second copy.
//
// bin/build-cli.sh builds it. The binary is not committed: every executable
// line in the repository stays text. `gate` is a shim that finds a built
// binary, a vendored one, or one on PATH, and says so in one sentence when
// there is none.
import Foundation
// the socket calls the bench is served over. Foundation carries them on Darwin,
// linux keeps them in Glibc, and Windows in WinSDK under names of its own: this
// vein builds on all three, so each says where its calls come from.
#if canImport(Glibc)
import Glibc
#endif
#if canImport(WinSDK)
import WinSDK
#endif

// ── AND THE TOOL FINDS ITS OWN PLACE THROUGH ITS OWN DOOR. This was URL path
// arithmetic: `fileURLWithPath` then two `deletingLastPathComponent`. Those
// readers split a path on `/` wherever they run, so on the platform that
// separates with `\` and roots on a drive letter they answer about a path
// nobody wrote, and what they answer has never been measured here. The place
// the tool stands in decides where its shelf is read from, so it is read the
// same way every other path in this file is now.
// Declared after the door below in the file's own order of reading, which is
// why this is a function rather than a value: top level runs top to bottom.
func toolRoot() -> String {
    let mine = absPath(CommandLine.arguments[0])
    return parentPath(parentPath(mine) ?? mine) ?? mine
}
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

// ── AND A VERB THAT STOPS TAKES ITS OWN HALF-WORLD WITH IT. `demo` makes a
// directory and fills it, and where it stopped partway (a shelf it could not
// read, a file it could not write) it left the shell of one behind: a folder
// with a CODEOWNERS and no layout, which the next command reads as a world
// that is not a world. Whoever founds a directory says so here, and the door
// every refusal goes through unmakes it. A directory that already existed is
// never touched: this removes what this run made, and nothing else.
var FOUNDED_HERE: String? = nil

func unmakeFounded() {
    guard let made = FOUNDED_HERE else { return }
    FOUNDED_HERE = nil
    try? FileManager.default.removeItem(atPath: made)
}

func cannot(_ note: String, _ then: String) -> Never {
    unmakeFounded()
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
// a global for the early branches, declared in the head the way the others are:
// top-level order is execution order, and a door that runs before its var would
// read a value that does not exist yet
var scratchCount = 0

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
// ── THE PAGE A PERSON MEETS FIRST, carried here because the other carrier is
// about to stop being a file. It travels byte for byte: what the terminal
// printed yesterday is what it prints tomorrow, and the battery holds the two
// to each other while both are alive. It goes to stderr with a non-zero code,
// the way asking for nothing has always answered here.
let USAGE = """
git verifies bytes: change one and the hash changes. Nothing verifies the
words a repository runs on. A CODEOWNERS, a schema, a list of who may deploy were
true the day somebody wrote them. The day that stopped is recorded nowhere. Here
those words are claims, re-read every time a file changes, and a claim that stops
holding is named at its line.

usage (the git-shaped porcelain):
  gate init [dir]                     · gate status | fsck
  gate mine FILE [--role R]           (a file you emit: judged with your world,
                                       and changing it changes the verdict)
  gate theirs FILE --at REV [--role R]
                                      (a file you took, at the revision you took
                                       it at. You read it, never rewrite it, and
                                       gate never fetches it: you brought it
                                       here. There are no ranges anywhere in
                                       this tool, so there is nothing to solve,
                                       to move, take it again at a newer one.
                                       R is world|seam|forms, which court reads
                                       the row, and a row gate cannot place is
                                       refused rather than guessed at)
  gate check view WHO DOC             · gate check administer|delete WHO DOC
  gate diff  transfer WHO DEPT        · gate diff  grant|revoke WHO DOC
  gate diff  hire ID RANK HOME GIVEN FAMILY BORN SITE
  gate apply transfer|grant|revoke|hire ...   (writes only on holds, like a commit)
  gate declare contract SPEC [-o F]   (the act of entry: a view of a document
  gate declare carrier DECL.json [-o F] you publish, or of what your build says
                                       your library carries. After this it is
                                       what you have SAID, and judged)
  gate demo | gate demo seam | gate demo org
                                      (thirty seconds each: a repository whose
                                       CODEOWNERS is judged, two sides with one
                                       disagreement between them, or people and
                                       departments for a domain with no repo)
  gate attention CONTRACT.swift CARRIER.swift [--as WHO] [--known K.json]
                 [--tracker T.json]     (what waits for a word, not what changed:
                                       who owes whom a sentence, read the same
                                       from either side. A declared divergence
                                       is set aside while what it cites is open,
                                       and comes back by itself when that closes)
  gate aside ROUTE FIELD --because KEY (say a divergence is meant, naming what
                                       will end it, and it stands out of the way
                                       while that is open and returns by itself)
  gate seam CONTRACT.swift CARRIER.swift
                                      (the one court over a pair: two
                                       declarations, each signed by whoever made
                                       it, refused at an address when they part)
  gate drift SPEC --client DIR [--since DATE] [--fail-over DAYS]
                                      (OBSERVATION of a world that has not
                                       entered: git objects and a walk whose
                                       bounds are printed. No verdict: judgement
                                       is behind the gate. The exit code is the
                                       operator's own threshold, never a court's)
  gate badge [-o gate.svg]            (claims judged, and how long every commit
                                       that touched them has held, replayed)
  gate import people.csv grants.csv [-o gate.swift]
  gate import codeowners CODEOWNERS --tree . [--policy owners.csv]
                                      (who owns what, translated once and
                                       judged from then on)
  gate import workflows [--tree .]    (which paths wake a workflow, against
                                       the tree it names: a filter that woke
                                       nothing said nothing)
  gate import rbac rbac.json  ·  gate import refs tracker.json --code .
  gate export gate.swift -o people.csv grants.csv
  gate verify people.csv grants.csv --against CMD
  gate serve [port]                   (local read-only JSON surface)
  gate report [-o report.html]        (printable audit page. Nothing is written
                                       unless you name the file)
  gate guard [merge]                  (repo policy by the same gates: HEAD author
                                       via tables/identities.csv must hold the
                                       rank stated in tables/guard.csv)
  gate library [-o lib.json]          (the domain vocabulary: forms, axes, seed coverage)
  gate library diff a.json b.json     (set operations between vocabularies: forms, never facts)
  gate survey [N]                     (t0, read-only: unwritten links from your own
                                       history, identity, object candidates, fabric)
  gate log                            (the repository's own history, with no
                                       translation at all: any clone has it)
  gate findings [--md]                (what is true of this clone, in sentences:
                                       needs no world and no configuration)
  gate bare FILE [NAME ...] [--full]  (the same world with the ceremony stripped:
                                       a projection, and the file on disk is the
                                       full Swift it was, which `--full` prints.
                                       Name records to print those alone)
  gate my [clear]                     (your own world: a claim in your git alone)
  gate stdlib [show|materialize] NAME (the words a world may be written in)
  gate --version                      (the tool, and the revision its judge was
                                       built from)
(ask = check, change = diff/apply: old names stay as aliases)

  ── and if this is the first time: `gate demo` builds a repository with a
     CODEOWNERS and one owner reaching past their zone, and prints the refusal.
     Thirty seconds, `git checkout .` is the whole way back.
"""

if args.isEmpty || args == ["--help"] || args == ["-h"] {
    err(USAGE + "\n")
    exit(1)
}

// the veins, one argv prefix per line, said once: `--carries` prints this and
// the guard over the shelf's verbs page reads it, so what this binary answers
// to is one list rather than two that drift.
let CARRIES = ["stdlib", "export", "seam", "log", "aside", "declare", "mine", "theirs",
               "init", "drift", "my", "status", "fsck", "badge", "survey", "findings",
               "report", "bare", "import", "verify", "library", "guard", "check", "ask",
               "diff", "apply", "change", "attention", "demo", "serve"]

if args == ["--carries"] {
    out(CARRIES.joined(separator: "\n") + "\n")
    exit(0)
}

// ── the shelf, read the way the python side reads it: the files next to the
// CLI, sorted by name, each page whole ──
func shelf() -> [(name: String, text: String)] {
    // ── AND THE SHELF IS CARRIED, NOT ASSUMED. These pages were read off the
    // disk beside the binary, which is true in a clone and false for anybody
    // who downloaded one file: `gate demo` asked for stdlib/manifest.swift and
    // stopped, holding half a directory it had already made. The pages are
    // compiled in now (bin/shelf-into-swift.py writes them into the build), so
    // one binary is one binary.
    //
    // The disk still comes FIRST where there is one: a clone that edits a page
    // is editing the page, not arguing with a snapshot, and this tool would be
    // a poor advertisement for itself if the copy inside outranked the source.
    // The battery holds the two equal, because a snapshot nobody compares is
    // the second record this whole tool exists to refuse.
    let dir = joinPath(toolRoot(), "stdlib")
    let names = ((try? FileManager.default.contentsOfDirectory(atPath: dir)) ?? [])
        .filter { $0.hasSuffix(".swift") }.sorted()
    var out: [(String, String)] = []
    for file in names {
        let path = joinPath(dir, file)
        guard let data = FileManager.default.contents(atPath: path),
              let text = String(data: data, encoding: .utf8) else { continue }
        // ── AND A LINE ENDING IS NOT PART OF THE PAGE. A checkout on windows
        // hands these files over with `\r\n`, and the pages then read as pages:
        // sixteen of them, none of them cut at the mark this file looks for,
        // because that mark ends at a newline. `gate demo` stopped on the first
        // verb of the road with "the shelf page a layout is born from is
        // missing" over a page sitting right there, and the disk read had
        // already outranked the copy compiled in, so the binary's own shelf
        // never got a turn. The pages are this tool's own text and their line
        // endings are the checkout's, not theirs.
        out.append((String(file.dropLast(6)),
                    text.replacingOccurrences(of: "\r\n", with: "\n")))
    }
    return out.isEmpty ? SHELF_EMBEDDED.map { (name: $0.name, text: $0.text) } : out
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
    // the page comes off the shelf, which is the disk beside a clone and the
    // pages compiled in otherwise: reading the file directly here made `show`
    // the one verb that could not answer for a binary carrying its own shelf,
    // while `stdlib` beside it listed every page it would not print
    guard let text = shelf().first(where: { $0.name == name })?.text else {
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
    guard let re = compiled(pattern, opts) else { return [] }
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
// ── FINDING A TOOL THE WAY A SHELL DOES. Every launch here went through
// `/usr/bin/env`, which is a path and not a mechanism: windows has no such
// file, so a vein that spells it that way builds there and then fails to run
// git at all. PATH is the list a shell walks, and walking it is the portable
// spelling of the same act.
func toolPath(_ name: String) -> String {
    #if canImport(WinSDK)
    let sep: Character = ";"
    let suffixes = [".exe", ".cmd", ".bat", ""]
    #else
    let sep: Character = ":"
    let suffixes = [""]
    #endif
    let said = ProcessInfo.processInfo.environment["PATH"] ?? ""
    for dir in said.split(separator: sep, omittingEmptySubsequences: true) {
        for suffix in suffixes {
            let full = (String(dir) as NSString).appendingPathComponent(name + suffix)
            if FileManager.default.isExecutableFile(atPath: full) { return full }
        }
    }
    // said plainly rather than guessed: a launch of a name PATH does not carry
    // fails with the name in the message
    return name
}

// ── AND EVERY SPAWN IS COUNTED. The cost of this vein turned out to be
// repeated outside work rather than anything it computes, and a count of
// spawns is the honest measure of that: it is deterministic, it does not
// depend on the machine, and it outlives the other carrier. Under
// `GATE_SPAWN_LEDGER=1` the total is printed on the way out, and the battery
// pins the exact number a verb is built to need.
var SPAWNS = 0
var SPAWNS_GIT = 0
var SPAWNS_COURT = 0

func spawnCounted(_ kind: String) {
    SPAWNS += 1
    if kind == "court" { SPAWNS_COURT += 1 } else { SPAWNS_GIT += 1 }
}

func spawnLedger() {
    if ProcessInfo.processInfo.environment["GATE_SPAWN_LEDGER"] == "1" {
        err("gate-cli: spawns \(SPAWNS) (git \(SPAWNS_GIT), court \(SPAWNS_COURT))\n")
    }
}

// ── AND WAITING IS NOT WORK, SO IT MAY NOT COST LIKE WORK. `waitUntilExit`
// runs a run loop and wakes on ITS timer, not on the child: a git that answers
// in nine milliseconds was billed about a hundred and fifteen, and `status`
// spawns five. The verb spent 331 ms of which 47 was user and system time
// together: the rest was this tool asleep beside a finished process, and the
// cover promises milliseconds on every keystroke.
//
// The child says when it is done, so the wake comes from the child: a
// termination handler signals, and the caller waits on that. Every spawn in
// this file goes through here, so the ledger the battery holds (`spawns 5`)
// is unchanged and the price is paid once, at the door.
func waitDone(_ p: Process) {
    let done = DispatchSemaphore(value: 0)
    p.terminationHandler = { _ in done.signal() }
    // a process that already exited before the handler was set never signals,
    // and `isRunning` is false by then: the handler is the fast path and this
    // is the truth beside it
    if !p.isRunning { p.terminationHandler = nil; return }
    done.wait()
    p.terminationHandler = nil
}

func runGit(_ arguments: [String], _ cwd: String) -> String {
    mark("spawn:git")
    spawnCounted("git")
    let p = Process()
    p.executableURL = URL(fileURLWithPath: toolPath("git"))
    p.arguments = [] + arguments
    // the folder a child runs in is a path: `URL(fileURLWithPath:)` reads its
    // argument the posix way wherever it runs, and this vein hands it worlds
    // that live at a drive letter
    p.currentDirectoryPath = cwd
    let pipe = Pipe(), quiet = Pipe()
    p.standardOutput = pipe
    p.standardError = quiet
    do { try p.run() } catch { return "" }
    let said = pipe.fileHandleForReading.readDataToEndOfFile()
    quiet.fileHandleForReading.readDataToEndOfFile()
    waitDone(p)
    return String(data: said, encoding: .utf8) ?? ""
}

// and the same call read for its verdict rather than its words: `ls-files
// --error-unmatch` says whether git tracks a path by the code it exits with,
// and says nothing on stdout worth reading
func gitExitCode(_ arguments: [String], _ cwd: String) -> Int32 {
    spawnCounted("git")
    let p = Process()
    p.executableURL = URL(fileURLWithPath: toolPath("git"))
    p.arguments = [] + arguments
    // the folder a child runs in is a path: `URL(fileURLWithPath:)` reads its
    // argument the posix way wherever it runs, and this vein hands it worlds
    // that live at a drive letter
    p.currentDirectoryPath = cwd
    let quiet = Pipe(), alsoQuiet = Pipe()
    p.standardOutput = quiet
    p.standardError = alsoQuiet
    do { try p.run() } catch { return 1 }
    quiet.fileHandleForReading.readDataToEndOfFile()
    alsoQuiet.fileHandleForReading.readDataToEndOfFile()
    waitDone(p)
    return p.terminationStatus
}

func theirsText(_ path: String, _ what: String) -> String {
    mark("read:" + lastName(path))
    // ── THE ONE DOOR, ON THIS SIDE TOO. A file that is not there and a file that
    // is not text are two different sentences, and this vein said the first one
    // for both: `no such side` about a file sitting right there, while the other
    // carrier named the byte. Two carriers, one verb, two stories.
    guard let data = FileManager.default.contents(atPath: path) else {
        cannot("no such file: " + path, "point it at " + what)
    }
    if let text = String(data: data, encoding: .utf8) {
        // ── AND SOMEBODY ELSE'S FILE IS READ THE WAY THEY SAVED IT. A file a
        // Windows editor wrote opens with a byte-order mark, and the other
        // carrier reads through `utf-8-sig`, which drops it. This did not: the
        // mark travelled into the first CODEOWNERS pattern, so `/src/plain.go`
        // became a pattern no file matches and the tool refused a rule that was
        // right. Every reading of somebody else's text comes through here.
        // ── AND THE LINE ENDING IS THEIRS TO CHOOSE, the same as the mark. A
        // CODEOWNERS checked out on windows ends its lines with `\r\n`, the
        // carriage return travelled into the owner's name, and a name is
        // sanitised character by character: `Owns_0_alice` came back as
        // `Owns_0_alice_`. Eight refusals, every one of them the tool telling
        // the world it disagreed with itself about a name it had just written.
        let whole = text.hasPrefix("\u{feff}") ? String(text.dropFirst()) : text
        return whole.contains("\r\n")
            ? whole.replacingOccurrences(of: "\r\n", with: "\n") : whole
    }
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

// ── AND THE KEY OF A REPOSITORY IS ASKED FOR ONCE. This spawns git, twice
// where a clone has no remote, and it is called from the walk that lists the
// bench's files: `status` paid for about sixty spawns of about nine
// milliseconds, which was ninety per cent of what this verb cost. The other
// carrier computes this once per process and remembers it. Same key, same
// answer, one question.
var REPO_KEYS: [String: String] = [:]

func repoKey(_ base: String) -> String {
    if let held = REPO_KEYS[base] { return held }
    let said = repoKeyRead(base)
    REPO_KEYS[base] = said
    return said
}

func repoKeyRead(_ base: String) -> String {
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
// ── SAID CORE BEGIN. The json vocabulary and its reader: a value tree that
// keeps object order and number spellings, and a total parser from text.
// Pure over values; the battery cuts this out and compiles it under the
// rbac core, whose items are Said values.
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
// ── SAID CORE END.

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
    if let f = FOUNDING, !leavesRoot(absPath(path), f) {
        return f
    }
    var walk = parentPath(absPath(path)) ?? absPath(path)
    while true {
        for name in ["gate.swift", "gate.manifest.swift"] {
            if FileManager.default.fileExists(atPath: (walk as NSString).appendingPathComponent(name)) {
                return walk
            }
        }
        guard let up = parentPath(walk), up != walk else { break }
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
    return leavesRoot(standing, here) ? standing : here
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
    // ── AND A REFUSAL NAMES WHERE IT LOOKED. This said only that a page was
    // missing, which leaves a person on a platform nobody here sits at with a
    // sentence and no place in it: the pages come from two sources, the disk
    // beside the tool and the snapshot compiled inside, and the reader has to
    // be told which one answered and what it held.
    let looked = joinPath(toolRoot(), "stdlib")
    let onDisk = ((try? FileManager.default.contentsOfDirectory(atPath: looked)) ?? [])
        .filter { $0.hasSuffix(".swift") }.count
    cannot("the shelf page a layout is born from is missing: stdlib/manifest.swift. "
           + "This read \(shelf().count) pages: \(onDisk) beside the tool at \(looked), "
           + "and \(SHELF_EMBEDDED.count) carried inside this binary",
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
// ── AND THE DOORS THE STRANGLER NEEDED ARE GONE. `--manifest-row`,

// `--contract-fields` and `--status-core` were entrances this file opened
// for the battery alone, so a python verb could ask this binary for one
// piece of work and the two answers could be held to each other. There is
// one carrier now, and a door a tool answers only for its own tests holds
// the tool against something built to agree with it: the checks that used
// them ask the verbs a person types, which is what they were about.

// ── THE STATUS CORE: the last big road, and the one every asking verb will
// stand on. The world is discovered by one walk, each row is routed to its
// court by role, the courts are the ones compiled into this binary, and the
// guards stand beside them. The battery walks it on a world that refuses for
// every reason a guard exists, through `status`, which is the verb a person
// types: the door that used to stand here for the battery is gone with the
// carrier it was built to be compared against.

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
        SHIPPED_SET.insert(joinPath(joinPath(toolRoot(), "stdlib"), page.name + ".swift"))
    }
}

// ── PATH DOOR BEGIN. Every path this tool takes in comes through the readers
// between this line and the one that closes them. What a platform spells
// differently lives here as values, and nowhere below does anything ask which
// platform it is standing on. The battery cuts this text out at these two
// marks and compiles it on its own, so the answers a machine running windows
// would get are measured on a machine that is not one.
struct PathStyle {
    // a platform's spelling of a path, held as a value: whether a drive letter
    // roots a path here, which also decides whether a backslash separates one.
    let drives: Bool
    static let posix = PathStyle(drives: false)
    static let windows = PathStyle(drives: true)
}

#if os(Windows)
let HOST_PATHS = PathStyle.windows
#else
let HOST_PATHS = PathStyle.posix
#endif

func pathRoot(_ p: String, _ st: PathStyle) -> (root: String, rest: String)? {
    // the root this path already stands on, and what is left after it. A nil
    // says it stands on nothing, which is what relative means.
    if !st.drives { return p.hasPrefix("/") ? ("", p) : nil }
    let t = p.replacingOccurrences(of: "\\", with: "/")
    // a share stands on two names, and both of them are the root: `//host/share`
    if t.hasPrefix("//") {
        // counted by the reader, never by arithmetic over the lengths of the
        // names: `//h//s/a` is one separator written twice, and adding up what
        // the reader could see cut the rest of the path in the middle of a
        // folder's name and handed back a folder nobody wrote.
        var segs = t.dropFirst(2).components(separatedBy: "/")
        var head: [String] = []
        while head.count < 2, !segs.isEmpty {
            let s = segs.removeFirst()
            if !s.isEmpty { head.append(s) }
        }
        guard head.count == 2 else { return nil }
        return ("//" + head[0] + "/" + head[1], "/" + segs.joined(separator: "/"))
    }
    // a drive stands on one letter and a colon. The letter is folded to upper
    // case, and THAT IS THE ONLY FOLDING DONE HERE: NTFS compares the rest of a
    // path without case and this tool does not, so two spellings of one file
    // are two paths to it. Said aloud because a comparison that is almost equal
    // is the way a judge starts agreeing with itself about nothing.
    // ── AND `C:foo` IS READ AS `C:/foo`, WHICH IS NOT WHAT THAT PLATFORM
    // MEANS BY IT. It means foo beside wherever you last stood ON DRIVE C, and
    // a folder per drive is a thing only the platform itself remembers. This
    // door is lexical, like the abspath it was written against: it answers
    // from the text it was handed, and the one form where that is not the
    // platform's own answer is named here rather than guessed at.
    let c = Array(t)
    if c.count >= 2, c[1] == ":", c[0].isLetter {
        return (String(c[0]).uppercased() + ":", String(t.dropFirst(2)))
    }
    return nil
}

func absPath(_ p: String, _ st: PathStyle = HOST_PATHS,
             _ cwd: String = FileManager.default.currentDirectoryPath) -> String {
    // python's abspath is lexical: nothing is resolved, `.` and `..` fold away.
    // The working directory is a value here because the vectors for the other
    // platform have to name one, and a door that reads it from the machine can
    // only be measured on the machine it reads.
    let text = st.drives ? p.replacingOccurrences(of: "\\", with: "/") : p
    var root = ""
    var body = text
    if let r = pathRoot(text, st) {
        root = r.root
        body = r.rest
    } else if st.drives, text.hasPrefix("/") {
        // rooted, and on whichever drive you stand: that platform reads `\dir`
        // against the current drive and not against the current folder
        root = pathRoot(cwd, st)?.root ?? ""
        body = text
    } else {
        let r = pathRoot(cwd, st)
        root = r?.root ?? ""
        body = (r?.rest ?? cwd) + "/" + text
    }
    var out: [String] = []
    for c in body.components(separatedBy: "/") {
        if c.isEmpty || c == "." { continue }
        if c == ".." { if !out.isEmpty { out.removeLast() }; continue }
        out.append(c)
    }
    return root + "/" + out.joined(separator: "/")
}

func relPath(_ path: String, _ start: String, _ st: PathStyle = HOST_PATHS,
             _ cwd: String = FileManager.default.currentDirectoryPath) -> String {
    let a = absPath(path, st, cwd)
    let b = absPath(start, st, cwd)
    let ar = pathRoot(a, st)
    let br = pathRoot(b, st)
    if ar?.root ?? "" != br?.root ?? "" {
        // two roots, and no way from one to the other. The answer leads with a
        // step out, because every reader downstream asks this text whether a
        // file left the world, and the whole target follows it so a person is
        // shown the thing that was named.
        return "../" + a
    }
    let p = (ar?.rest ?? a).components(separatedBy: "/").filter { !$0.isEmpty }
    let s = (br?.rest ?? b).components(separatedBy: "/").filter { !$0.isEmpty }
    var i = 0
    while i < min(p.count, s.count), p[i] == s[i] { i += 1 }
    let rest = [String](repeating: "..", count: s.count - i) + p[i...]
    return rest.isEmpty ? "." : rest.joined(separator: "/")
}

func leavesRoot(_ path: String, _ root: String, _ st: PathStyle = HOST_PATHS) -> Bool {
    // THE question "is this file outside that world", asked in one place. Read
    // off the first component of a relative path by hand, it answers rightly
    // for the paths it was written against and says a silent no for a path on
    // another root, which is exactly how a check loses its subject and turns
    // green over nothing.
    return relPath(path, root, st).components(separatedBy: "/").first == ".."
}

func joinPath(_ base: String, _ more: String) -> String {
    // one join for the whole tool. `NSString.appendingPathComponent` splits on
    // `/`, knows nothing of a drive letter and is the reader this port took out
    // of every other place; the separator written here is `/` on both
    // platforms, because win32 takes one as readily as it takes its own.
    if more.isEmpty { return absPath(base) }
    if pathRoot(more, HOST_PATHS) != nil { return absPath(more) }
    return absPath(base + "/" + more)
}

func parentPath(_ p: String, _ st: PathStyle = HOST_PATHS) -> String? {
    // the folder a path stands in, and NOTHING at a root: a walk up a tree has
    // to know when it has arrived. Asked of the platform's own string reader,
    // that question is answered for a drive letter in a way this project has
    // never measured, and a walk that cannot tell it is standing on the root
    // either climbs forever or stops one floor early, which is a world found
    // where there is none.
    let a = absPath(p, st)
    let r = pathRoot(a, st)
    var seg = (r?.rest ?? a).components(separatedBy: "/").filter { !$0.isEmpty }
    guard !seg.isEmpty else { return nil }
    seg.removeLast()
    return (r?.root ?? "") + "/" + seg.joined(separator: "/")
}

func lastName(_ p: String, _ st: PathStyle = HOST_PATHS) -> String {
    // the name at the end of a path, asked of the door rather than of
    // `NSString.lastPathComponent`, which splits on `/` on every platform and
    // knows nothing of a drive letter or a backslash
    let text = st.drives ? p.replacingOccurrences(of: "\\", with: "/") : p
    return text.components(separatedBy: "/").last(where: { !$0.isEmpty }) ?? text
}

func canonicalPath(_ p: String, _ st: PathStyle = HOST_PATHS) -> String {
    // one door for every path comparison that crosses realpath: macOS's
    // resolvingSymlinksInPath strips the /private prefix from a path that
    // exists and leaves it on one that does not, so both sides of any
    // comparison go through here and the spelling cannot split them
    if st.drives {
        // ── AND WHAT IS NOT DONE HERE IS SAID OUT LOUD. On that platform this
        // resolves nothing. A reparse point is followed by the filesystem and
        // not by this text, and `resolvingSymlinksInPath` is an API this
        // project has never measured there: guessing at it would put a reading
        // nobody has seen underneath every comparison the tool makes. The fold
        // the door already did is what makes two paths comparable, and the
        // comparison stays bytes.
        return absPath(p, st)
    }
    let r = (absPath(p, st) as NSString).resolvingSymlinksInPath
    for known in ["/private/tmp/", "/private/var/", "/private/etc/"]
    where r.hasPrefix(known) || r == String(known.dropLast()) {
        return String(r.dropFirst("/private".count))
    }
    return r
}
// ── PATH DOOR END.

func readText(_ path: String) -> String? {
    // read with python's errors="replace": a byte that is not utf-8 becomes the
    // replacement character rather than a refusal to read the file at all
    guard let data = FileManager.default.contents(atPath: path) else { return nil }
    let text = String(decoding: data, as: UTF8.self)
    // ── AND A MARK AT THE HEAD OF A FILE IS NOT ITS FIRST CHARACTER. A file a
    // Windows editor wrote opens with a byte-order mark, and the other carrier
    // reads foreign text through `utf-8-sig`, which drops it. This did not, so
    // the mark travelled into the first CODEOWNERS pattern and the tool refused
    // a rule that was right, and into a policy header so no column was found.
    // ── AND A LINE ENDING IS THE CHECKOUT'S, NOT THE TEXT'S. A clone on
    // windows arrives with `\r\n` under git's own default, and every reader
    // downstream matches on lines that end at `\n`: the layout's rows parsed
    // to nothing, the world was therefore never found, and `gate status` in a
    // world said "no world here" AND EXITED NOUGHT. That is this project's own
    // oldest species, a check that lost its subject and went green, in the one
    // place where green is a claim somebody's hook believes. Measured here by
    // handing a made world over in that spelling.
    //
    // Nothing byte-exact goes through this door: the three digests this tool
    // takes read the file's own bytes, so a taken file is still identified by
    // what it is and not by what its lines end with.
    let whole = text.hasPrefix("\u{feff}") ? String(text.dropFirst()) : text
    return whole.contains("\r\n")
        ? whole.replacingOccurrences(of: "\r\n", with: "\n") : whole
}

func matchesAt(_ pattern: String, _ text: String,
               dotAll: Bool = false, lines: Bool = false) -> [(groups: [String], line: Int)] {
    // like `matches`, and each hit carries the line its match starts on,
    // counted from one: the other carrier addresses a row by
    // text[:m.start()].count("\n") + 1
    var opts: NSRegularExpression.Options = []
    if dotAll { opts.insert(.dotMatchesLineSeparators) }
    if lines { opts.insert(.anchorsMatchLines) }
    guard let re = compiled(pattern, opts) else { return [] }
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
    guard let re = compiled("^(?:" + pattern + ")", []) else { return nil }
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

// `said`, when given, is the document as somebody is typing it rather than as
// it sits on disk: the bench judges the layout the way it judges every other
// file it opens, and the saved copy would be a second, older answer
func layoutRowsFull(_ dir: String, said: String? = nil) -> (rows: [LayoutRow], manifest: String?) {
    let mp = (dir as NSString).appendingPathComponent("gate.manifest.swift")
    guard let text = said ?? readText(mp) else { return ([], nil) }
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
        guard let up = parentPath(d), up != d else { break }
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


func leavesWorldHere(_ path: String, _ rootDir: String) -> Bool {
    let real = canonicalPath((rootDir as NSString).appendingPathComponent(path))
    return leavesRoot(real, canonicalPath(rootDir))
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

// `liveRows` and `liveText` override the document on disk, for the same reason
// the forms guard takes a live text: the layout is judged as it is typed, and
// two of the checks below ask what the DOCUMENT says rather than what its rows
// say, so the text comes with them.
func manifestGuards(_ w: WorldState, liveRows: [LayoutRow]? = nil,
                    liveText: String? = nil) -> [(address: String, claim: String)] {
    // layout guards, both directions: a declared file exists, a neighbouring
    // *.swift is declared, a row says which court reads it, and every claim
    // below is the other carrier's, word for word
    guard let layout = w.layout else { return [] }
    var bad: [(address: String, claim: String)] = []
    // ── AND THE WORLD'S OWN FOLDER COMES OFF THE DOOR. This was NSString path
    // arithmetic, which splits on `/` wherever it runs: on the platform that
    // roots on a drive letter it hands back a folder nobody wrote, and every
    // file this guard then looks for is looked for in the wrong place. That is
    // what "the manifest declares ownership.swift, and no such file exists"
    // means on a machine where the file is sitting right there.
    let man = lastName(layout.manifest)
    let d = parentPath(layout.manifest) ?? layout.manifest
    let live = liveRows ?? layout.rows
    let liveText = uncommented(liveText ?? (readText(layout.manifest) ?? ""))
    var seenPaths: [String: String] = [:]
    for r in live {
        let said = r.name ?? "a row with no name"
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
                      + STATUS_ROLES.map { "`\($0.0)`: \($0.1)" }.joined(separator: " · ")))
        } else if r.role == "seam",
                  FileManager.default.fileExists(atPath: joinPath(d, r.path)),
                  !isSeamSide(joinPath(d, r.path)) {
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
        // ── AND THE PLACE THAT WAS LOOKED IN IS NAMED. This said a file is
        // missing and never where it looked for it, which is a sentence a
        // person cannot act on when the row and the folder are both in front
        // of them: a path with a stray character on the end reads as the path
        // it almost is. The looked-for path travels in quotes.
        let looked = joinPath(d, r.path)
        if !FileManager.default.fileExists(atPath: looked) {
            bad.append(("\(man):\(r.line)",
                        "the manifest declares \(r.path), and no such file exists at "
                      + "`\(looked)`: either the file is gone or the row is, and a row "
                      + "for a file nobody has is a court with nothing to check"))
        }
    }
    for r in live where r.role == "forms" && !r.path.isEmpty {
        // ── AND THIS ONE READS THROUGH THE DOOR TOO. It took the file's bytes
        // and cut them into lines by hand, which is a third reading of a text
        // in a file where every other one goes through `readText`. A page
        // checked out with `\r\n` is the same page, and the line endings are
        // the checkout's: on two platforms this guard fired over a world that
        // holds here, and a reader that spells a text its own way is how that
        // happens.
        let p = joinPath(d, r.path)
        guard let whole = readText(p) else { continue }
        let head = whole.prefix(1200).components(separatedBy: "\n").prefix(8)
        var want: String? = nil
        var saw = false
        for ln in head where ln.hasPrefix("//") && ln.contains("written in") {
            saw = true
            want = matches("stdlib show ([\\w-]+)", ln).first.map { $0[0] }
            break
        }
        guard saw, let shelfName = want else { continue }
        let wantFile = shelfName + ".swift"
        let mineNames = Set(topNames(whole).map { $0.0 })
        let theirs = Set(topNames(STDLIB_TEXTS[shelfName] ?? "").map { $0.0 })
        if !theirs.isDisjoint(with: mineNames) { continue }
        let row = live.first(where: { $0.name == r.written })
        if row == nil || lastName(row!.path) != wantFile {
            bad.append(("\(man):\(r.line)",
                        "`\(r.name ?? "a row with no name")` says in its own head that it is written in "
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
                            + "\(had.line): two worlds you present, one name, "
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

// `live` overrides what is on disk for the files it names, so the bench can
// hold a forms row to the same promise as every other file it opens: judged as
// you type. Reading the saved copy while somebody edits an unsaved one shows
// green over a lie.
func formsGuards(_ w: WorldState, _ size: inout [String: Int],
                 live: [String: String] = [:]) -> [(address: String, claim: String)] {
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
        if let typed = live[r.path] { return typed }
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
    let tmp = tempRoot() + "gate-forms-\(ProcessInfo.processInfo.processIdentifier)"
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

// who somebody is, and what an action demands: facts declared in the policy
// file and travelling through git like every other fact. Read once, here, so
// the guard that judges them and the page that prints them read one file with
// one pair of eyes.
struct PolicyRead {
    var ids: [(mail: String, who: String)] = []
    var rules: [(action: String, rank: String)] = []
    var whereAt: [String: (String, Int)] = [:]
    var name = ""
}

func readPolicy(_ w: WorldState) -> PolicyRead {
    var said = PolicyRead()
    guard let pp = policyPathOf(w) else { return said }
    let text = readText(pp) ?? ""
    said.name = (pp as NSString).lastPathComponent
    let name = said.name
    for (m, at) in matchesAt("(?:public\\s+)?enum\\s+(\\w+)\\s*:[^{\\n]*\\bIdentity\\b[^{\\n]*"
                             + "\\{(.*?)\\n\\}", text, dotAll: true) {
        guard let who = matches("typealias\\s+Person\\s*=\\s*(\\w+)", m[1]).first?.first,
              let mail = matches("extension\\s+" + m[0] + "\\b.*?typeName.*?\"([^\"]+)\"",
                                 text, dotAll: true).first?.first else { continue }
        if let i = said.ids.firstIndex(where: { $0.mail == mail }) { said.ids[i] = (mail, who) }
        else { said.ids.append((mail, who)) }
        said.whereAt[mail] = (name, at)
    }
    for (m, at) in matchesAt("(?:public\\s+)?enum\\s+(\\w+)Policy\\s*\\{(.*?)\\n\\}",
                             text, dotAll: true) {
        guard let req = matches("typealias\\s+Requires\\s*=\\s*(\\w+)", m[1]).first?.first
        else { continue }
        let action = m[0].lowercased()
        if let i = said.rules.firstIndex(where: { $0.action == action }) {
            said.rules[i] = (action, req)
        } else { said.rules.append((action, req)) }
        said.whereAt["policy:" + action] = (name, at)
    }
    return said
}

func policyGuards(_ w: WorldState) -> [(address: String, claim: String)] {
    // the policy file is not in the judged list, so status guards it: every
    // Person an identity names is declared by the world, every Requires is a
    // name something this world reads declares
    guard policyPathOf(w) != nil else { return [] }
    let said = readPolicy(w)
    let (ids, rules, whereAt, name) = (said.ids, said.rules, said.whereAt, said.name)
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
    // ── AND THE WORDS ARE THIS BINARY'S OWN. The dispatch used to live in the
    // other carrier's file, so this guard read that file; the dispatch is here
    // now, and what it answers to is the ledger it prints. One list, read by
    // the guard and by whoever asks `--carries`.
    var verbs = Set(CARRIES)
    // the two spellings of asking what runs here, which the shelf page records
    verbs.formUnion(["version", "v"])
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
    mark("spawn:judge-probe")
    let proc = Process()
    proc.executableURL = URL(fileURLWithPath: p)
    proc.arguments = ["judge"]
    proc.standardOutput = Pipe()
    proc.standardError = Pipe()
    do { try proc.run() } catch { return false }
    waitDone(proc)
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
    // ── AND A BINARY KNOWS WHAT IT WAS BUILT FROM. This read `.from` beside
    // the judge binary, which is a file in a clone and nothing at all for a
    // person who downloaded one file: `--version` there said the revision "is
    // not recorded", about the one dependency this whole tool rests on, while
    // the release was shipping that very revision in a file beside it under a
    // name this never looked for. The court is compiled in, so the revision it
    // was compiled at is compiled in with it. The file still comes first where
    // there is one: a clone that rebuilds its judge is answered by its own
    // disk rather than by whatever this binary remembers.
    let p = joinPath(toolRoot(), "bin/gate-judge.from")
    let said = (readText(p) ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
    if !said.isEmpty { return said }
    let built = COURT_PIN_BUILT_IN.trimmingCharacters(in: .whitespacesAndNewlines)
    return built.isEmpty ? nil : built
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
               + "it was built from `\(built.prefix(12))`: one of the two is out of date, "
               + "and a row that names the court may not disagree with the court")]
    }
    return []
}

// ── CODEOWNERS CORE BEGIN. The pure heart of `import codeowners`: text into
// rules, rules into a world. Everything between these two marks is total
// functions over values: no file is opened, no global is read, no process is
// asked, and the battery holds that lexically. It also CUTS this block out at
// the marks, compiles it alone and asks it questions with answers known in
// advance, so the heart is judged HERE on any machine, and a foreign platform
// only ever re-runs the thin rim around it: read, write, spawn, walk.
func sanitized(_ s: String) -> String {
    return s.replacingOccurrences(of: "[^A-Za-z0-9]", with: "_", options: .regularExpression)
}

func codeownersZone(_ pattern: String) -> String {
    let p = String(pattern.trimmingCharacters(in: .whitespaces).drop(while: { $0 == "/" }))
    if p.isEmpty || p.hasPrefix("*") { return "Root" }
    let z = sanitized(p.components(separatedBy: "/")[0])
    return z.isEmpty ? "Root" : z
}

func parseCodeowners(_ text: String) -> [(line: Int, pattern: String, owners: [String])] {
    var rules: [(Int, String, [String])] = []
    for (n0, raw) in text.components(separatedBy: "\n").enumerated() {
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

let CODEOWNERS_HEADER = "// printed by gate import codeowners: who owns what in this repository,\n"
    + "// written in the grants vocabulary (`gate stdlib show forms-grants`). A zone is\n"
    + "// a top of the tree, a room is a pattern, and an owner keeps a zone: owning\n"
    + "// is entry whose key administers, judged like any other claim.\n//\n"

func codeownersWorldBuild(_ rules: [(line: Int, pattern: String, owners: [String])],
                          _ policy: [(owner: String, zone: String)],
                          _ saidFrom: String, _ srcName: String, _ grantsPage: String)
    -> (lines: [String], srcmap: [String: String], keepers: Set<String>) {
    // rules into a world, over values alone: the page and the source's display
    // name arrive as arguments, because the core reads no shelf and no disk
    var zones = Set(rules.map { codeownersZone($0.pattern) })
    for (_, z) in policy { zones.insert(sanitized(z)) }
    var lines = [CODEOWNERS_HEADER + "// from: " + saidFrom + "\n//\n" + grantsPage, ""]
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
            srcmap[cert] = "\(srcName):\(r.line) · \(r.pattern) \(owner)"
        }
    }
    return (lines, srcmap, keepers)
}
// a multi-word line with no owner-shaped word is not a rule of this file's
// kind: a license pasted into a CODEOWNERS read as a two-rule map with forty
// lines nobody mentioned, because the parser kept the lines an owner stands
// on and dropped the rest in silence. What is not read is returned, to be
// said. One word alone stays legal: github's unowned-pattern spelling.
func codeownersUnread(_ text: String) -> [(line: Int, said: String)] {
    var out: [(Int, String)] = []
    for (n0, raw) in text.components(separatedBy: "\n").enumerated() {
        let line = raw.components(separatedBy: "#")[0].trimmingCharacters(in: .whitespaces)
        if line.isEmpty { continue }
        let parts = line.replacingOccurrences(of: "\\ ", with: "\u{0}")
            .components(separatedBy: .whitespaces).filter { !$0.isEmpty }
        if parts.count >= 2
            && !parts.dropFirst().contains(where: { $0.hasPrefix("@") || $0.contains("@") }) {
            out.append((n0 + 1, line))
        }
    }
    return out
}

// ── AND THE EXACT MATCH OF THE PLATFORM, FOR THE QUESTION THAT NEEDS IT.
// The wide matcher above is deliberate for DEATH: a rule it calls dead is
// dead by the narrower reading too. Shadowing flips the error's side: a
// wide LATER rule would beat earlier ones where the platform's own reading
// does not. So precedence is judged by gitignore semantics exactly: `*`
// stays inside a segment, `**` crosses, a slash at the head or the middle
// anchors to the root, and a matched directory owns its subtree.
func ghSegMatch(_ pat: [Character], _ name: [Character]) -> Bool {
    func walk(_ i: Int, _ j: Int) -> Bool {
        if i == pat.count { return j == name.count }
        if pat[i] == "*" {
            if walk(i + 1, j) { return true }
            return j < name.count && walk(i, j + 1)
        }
        if j == name.count { return false }
        if pat[i] == "?" || pat[i] == name[j] { return walk(i + 1, j + 1) }
        return false
    }
    return walk(0, 0)
}

func ghMatch(_ pattern: String, _ path: String) -> Bool {
    var pat = pattern
    let trimmed = pat.hasSuffix("/") ? String(pat.dropLast()) : pat
    let anchored = pat.hasPrefix("/") || trimmed.dropFirst().contains("/")
    while pat.hasPrefix("/") { pat.removeFirst() }
    while pat.hasSuffix("/") { pat.removeLast() }
    if pat.isEmpty { return true }
    let segs = pat.components(separatedBy: "/").map { Array($0) }
    let parts = path.components(separatedBy: "/").map { Array($0) }
    func walk(_ i: Int, _ j: Int) -> Bool {
        if i == segs.count { return true }        // a match owns its subtree
        if segs[i] == ["*", "*"] {
            if walk(i + 1, j) { return true }
            return j < parts.count && walk(i, j + 1)
        }
        if j == parts.count { return false }
        return ghSegMatch(segs[i], parts[j]) && walk(i + 1, j + 1)
    }
    if anchored { return walk(0, 0) }
    for start in 0...parts.count where walk(0, start) { return true }
    return false
}

// the rules that never win: every file a rule matches is taken by a LATER
// rule (github reads the last match). A later rule that keeps the same
// owners is a duplicate; one that drops an owner is an override, and the
// early author believes they route what they do not.
func codeownersShadows(_ rules: [(line: Int, pattern: String, owners: [String])],
                       _ files: [String])
    -> (overrides: [(line: Int, pattern: String, beatenBy: Int)], duplicates: Int) {
    let n = rules.count
    if n < 2 { return ([], 0) }
    var wins = [Int](repeating: 0, count: n)
    var seen = [Bool](repeating: false, count: n)
    var beatenBy = [[Int: Int]](repeating: [:], count: n)   // beater -> files taken
    var matched = [Int](repeating: 0, count: n)
    var ownerLoss = [Bool](repeating: false, count: n)
    for f in files {
        var winner: Int? = nil
        for idx in stride(from: n - 1, through: 0, by: -1) where ghMatch(rules[idx].pattern, f) {
            winner = idx; break
        }
        guard let w = winner else { continue }
        wins[w] += 1
        seen[w] = true
        matched[w] += 1
        for idx in stride(from: w - 1, through: 0, by: -1) where ghMatch(rules[idx].pattern, f) {
            seen[idx] = true
            matched[idx] += 1
            beatenBy[idx][w, default: 0] += 1
            if !Set(rules[idx].owners).isSubset(of: Set(rules[w].owners)) {
                ownerLoss[idx] = true
            }
        }
    }
    // ── AND A BROAD DEFAULT UNDER LATER SPECIFICS IS LAYERING, NOT A BUG.
    // An early catch-all beaten file-by-file by many narrow later rules is a
    // deliberate shape: it still catches tomorrow's files. The refusable
    // shape is the opposite one: an early SPECIFIC rule whose every file one
    // later, broader rule takes. So an override needs a single beater that
    // takes the early rule's whole match, and an owner who loses by it.
    var overrides: [(line: Int, pattern: String, beatenBy: Int)] = []
    var duplicates = 0
    for i in 0..<n where seen[i] && wins[i] == 0 {
        let whole = beatenBy[i].first { $0.value == matched[i] }
        if let w = whole, ownerLoss[i] {
            overrides.append((rules[i].line, rules[i].pattern, rules[w.key].line))
        } else if whole != nil && !ownerLoss[i] { duplicates += 1 }
    }
    return (overrides, duplicates)
}

// ── CODEOWNERS CORE END.

func readCodeowners(_ path: String) -> [(line: Int, pattern: String, owners: [String])] {
    // ── AND SOMEBODY ELSE'S FILE IS READ THROUGH THE ONE DOOR. This read it
    // with the reader that replaces a byte it cannot decode, so a file that is
    // not text at all came back as text full of replacement characters and the
    // verb answered `observed` over it. The other carrier read it through the
    // door that says what is wrong, and while it was alive its answer covered
    // this one. Found the day it stopped covering.
    // the rim reads, the core parses: one reading of the text, in the block
    // the battery compiles alone
    return parseCodeowners(theirsText(path, "a CODEOWNERS"))
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

func codeownersWorldLines(_ src: String, _ policy: [(owner: String, zone: String)],
                          _ saidFrom: String)
    -> (lines: [String], srcmap: [String: String],
        rules: [(line: Int, pattern: String, owners: [String])], keepers: Set<String>) {
    // one translator, whoever asks: the rim reads the file and the shelf, the
    // core builds the world out of the values
    let rules = readCodeowners(src)
    let (lines, srcmap, keepers) = codeownersWorldBuild(
        rules, policy, saidFrom, lastName(src), STDLIB_TEXTS["forms-grants"] ?? "")
    return (lines, srcmap, rules, keepers)
}

// ── ONE PAIR, TWO ASKERS. The worlds printed by `import codeowners`, each
// with the source its own `from:` line names: `status` re-translates and
// compares the pair, and `findings` asks whether a CODEOWNERS it met is
// already somebody's held half before offering to translate it. One
// enumeration, so the two mouths cannot disagree about what is paired.
func codeownersPairedWorlds(_ w: WorldState)
    -> [(world: String, name: String, fromTok: String, policyTok: String,
         srcAbs: String, text: String)] {
    guard let f = w.facts else { return [] }
    var judged = Set(worldFilesOf(w))
    judged.insert(absPath(f))
    if let l = w.layout {
        let mdir = (l.manifest as NSString).deletingLastPathComponent
        for r in l.rows { judged.insert((mdir as NSString).appendingPathComponent(r.path)) }
    }
    var out: [(world: String, name: String, fromTok: String, policyTok: String,
               srcAbs: String, text: String)] = []
    for path in judged.sorted() where FileManager.default.fileExists(atPath: path) {
        // a declared row may be a binary, and a binary is nobody's half of a
        // printed pair: strict utf-8 here, the way the other carrier reads it
        // the printed world is read the same way: a pair compared across two
        // spellings of a line ending is two records of one fact by arithmetic
        guard let data = FileManager.default.contents(atPath: path),
              let text = String(data: data, encoding: .utf8)?
                  .replacingOccurrences(of: "\r\n", with: "\n"),
              text.contains("printed by gate import codeowners"),
              let m = matchesAt("^// from: (\\S+)(?: --policy (\\S+))?$", text, lines: true)
                  .first?.groups
        else { continue }
        let srcp = ((absPath(path) as NSString).deletingLastPathComponent as NSString)
            .appendingPathComponent(m[0])
        out.append((path, (path as NSString).lastPathComponent, m[0], m[1], srcp, text))
    }
    return out
}

func codeownersPairGuards(_ w: WorldState) -> [(address: String, claim: String)] {
    // the print and its source are a pair: the same translator prints the
    // world again, and the certificates are compared, refusals at the line
    // that makes them
    var out: [(address: String, claim: String)] = []
    for pw in codeownersPairedWorlds(w) {
        let (path, name, text) = (pw.world, pw.name, pw.text)
        let m = [pw.fromTok, pw.policyTok]
        let srcp = pw.srcAbs
        if !FileManager.default.fileExists(atPath: srcp) {
            out.append(("\(name):1",
                        "printed from \(m[0]), and no file of that name is here now"))
            continue
        }
        let policy = m[1].isEmpty ? []
            : readOwnersPolicy(((absPath(path) as NSString).deletingLastPathComponent as NSString)
                .appendingPathComponent(m[1]))
        let (lines, srcmap, _, _) = codeownersWorldLines(srcp, policy, "")
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

func nextRung(_ w: WorldState, _ refused: Bool, serving: Bool = false) -> String {
    // ONE next step, chosen by what the repository already has: each rung
    // names what becomes yours once the step is taken, and a rung already
    // taken is not offered.
    // ── AND A STEP IS A STEP FROM WHERE THE READER IS STANDING. `serving` says
    // the asking came from the bench, so the bench counts as taken: the same
    // ladder, with the rung naming the room you are already in dropped.
    if refused {
        return serving
            ? "the refusal names its line: click it and the file opens there"
            : "open the address above, or run `gate serve` and watch the verdict move as you type"
    }
    let rootDir = w.facts.map { (absPath($0) as NSString).deletingLastPathComponent } ?? "."
    let hooked = runGit(["config", "--get", "core.hooksPath"], rootDir)
        .trimmingCharacters(in: .whitespacesAndNewlines)
    if hooked.isEmpty {
        // ── AND A RUNG NAMES WHAT BECOMES YOURS, NEVER WHAT WILL BE REFUSED.
        // This step used to end by naming what cannot be committed once the
        // hook is wired: the tool's act on the reader, and a word for whatever
        // they have today. What the hook actually gives them is the other half
        // of the same fact, said from their own side: what you commit is what
        // holds. The old wording survives in this comment, which is the
        // decision, and nowhere a terminal prints.
        return "run `gate init .` to wire the hook: from here on, what you commit is what holds"
    }
    let rows = (w.layout?.rows ?? []).filter { !$0.path.isEmpty }
    let saidSomething = w.facts.map { FileManager.default.fileExists(atPath: $0) } ?? false
    func arrivedByTaking(_ rel: String) -> Bool {
        let p = (rootDir as NSString).appendingPathComponent(rel)
        return (readText(p) ?? "").contains("Origin: gate's shelf")
    }
    if !rows.isEmpty && !saidSomething && rows.allSatisfy({ arrivedByTaking($0.path) })
        && rows.contains(where: { ($0.path as NSString).lastPathComponent == "readme.swift" })
        && !serving {
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
    // and on the bench that last rung is the room itself: a ladder whose steps
    // are all taken says nothing rather than inventing a step
    return serving ? ""
         : "run `gate serve` for the bench: your world on the left, the verdict on the right, "
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
// ── TABLES CORE BEGIN. The pure heart of the tables road: csv text into
// rows, rows into the seeded world, and the holes a world cannot be written
// over, returned as sentences for the rim to speak. Total over values, no
// reader of the world; the battery cuts this out at these two marks,
// compiles it alone, and asks it questions with answers known in advance.
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
    // a row shorter than the header leaves the rest unfilled: `at` says so
    // with nil, and every caller that writes a world out of these cells is
    // held to asking first. The filler used to be the string `None`, which
    // is what the other carrier printed for nothing, and it travelled into
    // worlds as a name no shelf declares.
    func at(_ r: Int, _ key: String) -> String? {
        guard let i = header.firstIndex(of: key), r < rows.count else { return nil }
        return i < rows[r].count ? rows[r][i] : nil
    }
    func text(_ r: Int, _ key: String) -> String { at(r, key) ?? "" }
}

func seededWorldBuild(_ people: CsvTable, _ grants: CsvTable,
                      _ peopleName: String, _ grantsName: String)
    -> (world: String, holes: [(said: String, fix: String)]) {
    var holes: [(said: String, fix: String)] = []
    // ── AND A TABLE MISSING A COLUMN IS SAID, NOT RAISED. The other carrier
    // reads `row['rank']` straight, so a table without that column meets a
    // person with a KeyError and a stack trace, inside the one command they ran
    // to look at their repository. A column is a name this reader can check.
    // The hole is returned as its sentence, and the rim speaks it.
    for (table, name, need) in [(people, peopleName, ["id", "rank", "home", "given",
                                                      "family", "born", "site"]),
                                (grants, grantsName, ["who", "doc"])] {
        let missing = need.filter { !table.has($0) }
        if !table.header.isEmpty && !missing.isEmpty {
            holes.append((name + " has no column named "
                   + missing.map { "`\($0)`" }.joined(separator: ", ")
                   + ", and the world is seeded from those",
                   "the header line names the columns: "
                   + need.joined(separator: ", ") + " for people, who, doc for grants"))
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
    emit("// seeded by gate import from: \(peopleName), \(grantsName)")
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
            if let extra = extra { let said = extra[n] ?? ""
                body += "    public typealias Sex = \(said.isEmpty ? "Male" : said)\n" }
            emit("\npublic enum \(n): \(conf) {\n\(body)}")
        }
    }
    // ── AND A ROW THAT STOPS EARLY IS SAID, NOT SEEDED. A cell the reader
    // could not find was written into somebody's world as `None`, which is
    // python's word for nothing and a name no shelf declares: the seeding
    // produced a world that refuses itself at the lines it had just written
    // (`the name None resolves to nothing`), in a repository that was empty a
    // second before. This tool's own law about columns is the law about this:
    // a column is an axis to a declared atom, and a name nothing declares
    // names nothing. `sex` is not owed, because a table without that column
    // has a stated default; a column that IS there and left empty is a hole.
    let owed = ["id", "rank", "home", "given", "family", "born", "site"]
    for r in people.rows.indices {
        for key in owed where (people.at(r, key) ?? "").isEmpty {
            holes.append(("row \(r + 1) of \(peopleName) "
                 + "states no \(key), and a world cannot be written from it",
                   "every column a world is written from is an axis to a name: fill that "
                 + "cell in, or take the column out of the table and nothing will ask for it"))
        }
    }
    // a table with no `sex` column has a stated default, and so does a row
    // whose own cell is empty: the two are the same absence, and one of
    // them used to reach the world as an empty name
    var sexes: [String: String] = [:]
    for r in people.rows.indices {
        let saidSex = people.has("sex") ? people.text(r, "sex") : ""
        sexes[people.text(r, "given")] = saidSex.isEmpty ? "Male" : saidSex
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
    return (lines.joined(separator: "\n") + "\n", holes)
}
// ── TABLES CORE END.

func csvTable(_ path: String, _ what: String) -> CsvTable {
    var all = csvRows(theirsText(path, what))
    all.removeAll { $0.isEmpty }            // the reader skips an empty row
    guard let head = all.first else { return CsvTable() }
    return CsvTable(header: head, rows: Array(all.dropFirst()))
}

// the rim of the tables road: read both tables, ask the core, and speak the
// first hole the way this mouth has always spoken it
func seededWorld(_ peoplePath: String, _ grantsPath: String) -> String {
    let people = csvTable(peoplePath, "the people this world is seeded from")
    let grants = csvTable(grantsPath, "the grants this world is seeded from")
    let built = seededWorldBuild(people, grants,
                                 lastName(peoplePath), lastName(grantsPath))
    if let h = built.holes.first { cannot(h.said, h.fix) }
    return built.world
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
    // the same ladder read from the bench: the room the reader is in is a rung
    // already taken, so it is not offered back to them (`serve`, below)
    var servingNext = ""
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
    answer.servingNext = nextRung(w, !refusals.isEmpty, serving: true)
    return answer
}

// the object the answer is said as, in the order the keys were said. Written
// once: the door below prints it indented, and the bench (`serve`) prints the
// same pairs compact, so a key added here is added to both by construction.
// ── AND THE LAST MILE IS NOT PART OF THE ANSWER. `command_to_run` is added
// where the answer is PRINTED, which is what the other carrier does in its own
// main; the bench recomputes the step for the room it is in and lifts the
// command out of THAT one, so the field cannot arrive here already spent.
func statusPairs(_ a: StatusAnswer) -> [(String, StatusJSON)] {
    if a.noWorld {
        return [
            ("command", .text("status")),
            ("verdict", .text("no world here")),
            ("refusals", .list([])),
            ("next", .text(a.next)),
            ("then", .text(a.then)),
            ("mutates", .raw("false")),
        ]
    }
    var pairs: [(String, StatusJSON)] = [
        ("command", .text("status")),
        ("facts", a.judged.count == 1 ? .text(a.judged[0])
                                      : .list(a.judged.map { .text($0) })),
        ("verdict", .text(a.verdict)),
        ("refusals", .list(a.refusals.map {
            .object([("address", .text($0.address)), ("claim", .text($0.claim))]) })),
        ("judge_ms", a.judgeMs.map { .raw(floatRepr($0)) } ?? .null),
        ("wall_ms", .raw(String(a.wallMs))),
        ("mutates", .raw("false")),
    ]
    if let m = a.world {
        pairs.append(("world", .object([("declarations", .raw(m[0])),
                                        ("lookups", .raw(m[1])),
                                        ("premises", .raw(m[2]))])))
    }
    if a.whereSize["equalities"] != nil {
        pairs.append(("forms", .object([
            ("equalities", .raw(String(a.whereSize["equalities"] ?? 0))),
            ("memberships", .raw(String(a.whereSize["memberships"] ?? 0))),
            ("uses", .raw(String(a.whereSize["uses"] ?? 0)))])))
    }
    pairs.append(("court", .text("the judge")))
    pairs.append(("next", .text(a.next)))
    return pairs
}

// the step, lifted out beside the sentence that names it: ready as it stands,
// for a person to copy and for an agent to read without parsing prose
func statusPrinted(_ a: StatusAnswer) -> [(String, StatusJSON)] {
    var pairs = statusPairs(a)
    if let ready = commandIn(a.next) ?? commandIn(a.then) {
        pairs.append(("command_to_run", .text(ready)))
    }
    return pairs
}

// the door: it prints what the answer above assembled, and decides nothing
func statusDoor(_ asJson: Bool) -> Never {
    let a = statusAnswer()
    if a.noWorld {
        if asJson {
            out(statusDumps(.object(statusPrinted(a)), 0) + "\n")
        } else {
            out("status: no world here\n  next: \(a.next)\n  then: \(a.then)\n")
        }
        exit(0)
    }
    let (refusals, whereSize) = (a.refusals, a.whereSize)
    let (worldM, next, times) = (a.world, a.next, a.judgeMs)
    spawnLedger()
    if asJson {
        out(statusDumps(.object(statusPrinted(a)), 0) + "\n")
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

// ── THE REPOSITORY'S OWN HISTORY, READ ONCE. `log` prints it, and the verbs
// that ask what is true of this clone read it rather than walking git a second
// time with a second set of rules. Observed, never judged: a commit is closed
// exactly when the default branch reaches it, and open otherwise.
struct JournalCommit {
    var hash = "", email = "", when = "", subject = ""
    var files: [String] = []
    var touches = false
    var closed: Bool? = nil
}

struct Journal {
    var commits: [JournalCommit] = []
    var branch = ""
    var me = ""
    var narrowed = true
}

// which files a world is made of, for the purpose of whose history this is: the
// plain court's own list, the forms rows beside it, and the policy. Whose
// history a file belongs to does not depend on which court reads it.
func journalWorld(_ base: String) -> Set<String> {
    var world = Set<String>()
    if FileManager.default.fileExists(atPath: (base as NSString)
        .appendingPathComponent("gate.swift")) { world.insert("gate.swift") }
    let (rows, manifest) = manifestRows(base)
    if manifest != nil {
        for r in rows where r.role == "world" || r.role == "forms" {
            if FileManager.default.fileExists(atPath:
                (base as NSString).appendingPathComponent(r.path)) { world.insert(r.path) }
        }
    }
    if FileManager.default.fileExists(atPath: (base as NSString)
        .appendingPathComponent("gate.policy.swift")) { world.insert("gate.policy.swift") }
    return world
}

func repoJournal(_ base: String, _ world: Set<String>, scope: String, limit: Int,
                 onlyMe: Bool) -> Journal {
    var journal = Journal()
    for candidate in ["origin/HEAD", "main", "master"] {
        let said = runGit(["rev-parse", "--verify", "-q", candidate], base)
        if !said.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            journal.branch = candidate
            break
        }
    }
    var merged = Set<String>()
    if !journal.branch.isEmpty {
        merged = Set(runGit(["rev-list", journal.branch], base)
            .split(whereSeparator: { $0 == "\n" || $0 == " " }).map(String.init))
    }
    journal.narrowed = !(scope == "world" && world.isEmpty)
    var arguments = ["log", "--all", "-\(limit)",
                     "--format=%x01%H%x1f%ae%x1f%aI%x1f%s", "--name-only"]
    if scope == "world" && !world.isEmpty { arguments += ["--"] + world.sorted() }
    for line in runGit(arguments, base).components(separatedBy: "\n") {
        if line.hasPrefix("\u{01}") {
            let parts = String(line.dropFirst()).components(separatedBy: "\u{1f}")
            var c = JournalCommit()
            c.hash = parts.count > 0 ? parts[0] : ""
            c.email = parts.count > 1 ? parts[1] : ""
            c.when = parts.count > 2 ? parts[2] : ""
            c.subject = parts.count > 3 ? parts[3] : ""
            c.closed = merged.isEmpty ? nil : merged.contains(c.hash)
            journal.commits.append(c)
        } else if !line.trimmingCharacters(in: .whitespaces).isEmpty,
                  !journal.commits.isEmpty {
            let f = line.trimmingCharacters(in: .whitespaces)
            journal.commits[journal.commits.count - 1].files.append(f)
            if world.contains(f) { journal.commits[journal.commits.count - 1].touches = true }
        }
    }
    journal.me = runGit(["config", "user.email"], base)
        .trimmingCharacters(in: .whitespacesAndNewlines)
    if onlyMe && !journal.me.isEmpty {
        journal.commits = journal.commits.filter { $0.email == journal.me }
    }
    return journal
}

// ── WHAT IS TRUE OF THIS REPOSITORY, said in sentences a person can act on.
// One producer behind `findings`, the audit page and the text of an issue: read
// the clone, name what is worth naming, and mark plainly which of it the judge
// checked and which was only read. Nothing here needs a translated world: a
// repository that has never heard of gate still has findings.
let CODEOWNERS_PLACES = ["CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"]

struct Finding { var kind = "", subject = "", sentence = "", evidence = "" }

func repoFindings(_ n: Int) -> [Finding] {
    var out: [Finding] = []
    loadStatusShelf()
    let w = discoverWorld()
    let base = w.facts.map { (absPath($0) as NSString).deletingLastPathComponent }
        ?? FileManager.default.currentDirectoryPath
    // the journal's own default scope is the history OF THE WORLD FILES, which
    // is right for a workbench and wrong for the one verb whose whole claim is
    // that a repository which has never heard of gate still has findings
    let world = journalWorld(base)
    let journal = repoJournal(base, world, scope: "all", limit: n, onlyMe: false)
    let commits = journal.commits
    if commits.isEmpty { return out }
    let who = identities(base)
    var authorOrder: [String] = [], authorCommits: [String: Int] = [:]
    for c in commits {
        if authorCommits[c.email] == nil { authorOrder.append(c.email) }
        authorCommits[c.email, default: 0] += 1
    }
    // what the world says, if there is one: refusals are findings of the first
    // order. A world of forms is still a world, which this asked wrong once.
    if !worldFilesOf(w).isEmpty || !((w.layout?.rows ?? []).isEmpty) {
        for r in statusAnswer().refusals {
            out.append(Finding(kind: "judged", subject: r.address,
                               sentence: r.address + " · " + r.claim,
                               evidence: "the judge, on this working copy"))
        }
    }
    // who touches the facts, and whether anything checked those edits
    if !world.isEmpty {
        var touchers = Set<String>()
        var edits = 0
        for c in commits where c.touches { touchers.insert(c.email); edits += 1 }
        var isDir: ObjCBool = false
        let ci = FileManager.default.fileExists(
            atPath: ((base as NSString).appendingPathComponent(".github") as NSString)
                .appendingPathComponent("workflows"), isDirectory: &isDir) && isDir.boolValue
        let hooked = runGit(["config", "--get", "core.hooksPath"], base)
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if edits > 0 && !(ci || !hooked.isEmpty) {
            out.append(Finding(
                kind: "observed", subject: "unchecked edits",
                sentence: many(touchers.count, "person", "people") + " changed these facts across "
                        + many(edits, "commit") + ", and nothing checked those edits: "
                        + "there is no hook and no workflow in this repository.",
                evidence: "git log over " + world.sorted().joined(separator: ", ")))
        }
        let unnamed = Set(commits.filter { $0.touches && who[$0.email] == nil }
            .map { $0.email }).sorted()
        if !unnamed.isEmpty {
            out.append(Finding(
                kind: "observed", subject: "unnamed authors",
                sentence: "\(unnamed.count) of the people who changed these facts "
                        + (unnamed.count == 1 ? "is" : "are") + " not tied to anyone "
                        + "in the world: an email is not a person until something says it is.",
                evidence: unnamed.prefix(4).joined(separator: ", ")))
        }
    }
    // ownership, if this repository states any: a stale owner is worth a sentence
    for place in CODEOWNERS_PLACES {
        let cand = (base as NSString).appendingPathComponent(place)
        guard FileManager.default.fileExists(atPath: cand) else { continue }
        let rules = readCodeowners(cand)
        var owners = Set<String>()
        for r in rules { for o in r.owners { owners.insert(o.hasPrefix("@") ? String(o.dropFirst()) : o) } }
        var seen = Set<String>()
        for c in commits {
            seen.insert(c.email.components(separatedBy: "@")[0])
            seen.insert((who[c.email] ?? "").lowercased())
        }
        let quiet = owners.filter { !$0.contains("/") && !seen.contains($0.lowercased()) }.sorted()
        // a history too short to be evidence proves nothing about anyone
        if !quiet.isEmpty && commits.count >= 50 {
            out.append(Finding(
                kind: "observed", subject: "quiet owners",
                sentence: "\(quiet.count) of the " + many(owners.count, "owner")
                        + " named in CODEOWNERS have not appeared in the last "
                        + many(commits.count, "commit") + ": ownership outlives people, "
                        + "and nothing here notices.",
                evidence: quiet.prefix(4).map { "@" + $0 }.joined(separator: ", ")))
        }
        let them = rules.count == 1 ? "it" : "them"
        // ── AND THE OFFER KNOWS A HELD PAIR FROM AN ORPHAN FILE. This said
        // "nothing checks it" of every CODEOWNERS it met, including one a
        // world here already names on its `from:` line and `status` re-judges
        // on every run: an offer to install the very lock that is on the
        // door. The offer asks the same enumeration the guard reads, so the
        // two mouths cannot part.
        let holder = codeownersPairedWorlds(w).first { $0.srcAbs == absPath(cand) }
        if let h = holder {
            out.append(Finding(
                kind: "read", subject: "CODEOWNERS",
                sentence: "CODEOWNERS states \(rules.count) " + (rules.count == 1 ? "rule" : "rules")
                        + " over \(owners.count) " + (owners.count == 1 ? "owner" : "owners")
                        + ", and \(h.name) holds \(them): every `gate status` "
                        + "translates the file again, and a line changed on "
                        + "either side alone is named at its line.",
                evidence: relPath(cand, base)))
        } else {
            out.append(Finding(
                kind: "offer", subject: "CODEOWNERS",
                // a count reads as a count: one rule is not `1 rules`, and this
                // sentence is the first thing the letter sends anybody to
                sentence: "CODEOWNERS states \(rules.count) " + (rules.count == 1 ? "rule" : "rules")
                        + " over \(owners.count) " + (owners.count == 1 ? "owner" : "owners")
                        + ", and nothing checks \(them). "
                        + "`gate import codeowners` reads \(them) as a world: a path "
                        + "no file matches, or an owner outside their zone, is "
                        + "named by the line it sits on.",
                evidence: relPath(cand, base)))
        }
        break
    }
    // the shape of the work, from the history itself
    let ranked = authorOrder.enumerated().sorted { a, b in
        let (ca, cb) = (authorCommits[a.element] ?? 0, authorCommits[b.element] ?? 0)
        return ca == cb ? a.offset < b.offset : ca > cb    // a tie keeps the order it arrived in
    }
    if commits.count >= 20, let top = ranked.first {
        let mine = authorCommits[top.element] ?? 0
        let share = Int((100.0 * Double(mine) / Double(commits.count)).rounded(.toNearestOrEven))
        if share >= 50 {
            out.append(Finding(
                kind: "observed", subject: "concentration",
                sentence: "\(share)% of the last " + many(commits.count, "commit")
                        + " are one person's (\(top.element)): what they know is not written down "
                        + "anywhere this repository can check.",
                evidence: "\(mine) of " + many(commits.count, "commit")))
        }
    }
    return out
}

func findingsMarkdown(_ found: [Finding]) -> String {
    // the same findings as a note somebody could read in an issue: what was
    // checked, what was only read, and how to see it for yourself
    if found.isEmpty {
        return "Nothing to report: this repository states no facts gate can read yet.\n"
    }
    var lines = ["### What this repository says about itself", ""]
    for f in found {
        let mark = f.kind == "judged" ? "**checked**" : (f.kind == "offer" ? "**offer**" : "read")
        lines.append("- \(f.sentence)  \n  <sub>\(mark) · \(f.evidence)</sub>")
    }
    lines += ["", "Everything marked *read* comes from the git history and is not a verdict.",
              "To see it yourself: `gate findings` in a clone. Nothing leaves the machine.", ""]
    return lines.joined(separator: "\n")
}

// ── WORKFLOWS CORE BEGIN. The pure heart of `import workflows` and of the
// pattern half of `import codeowners`: shell-style matching, the yaml block
// subset read as text, and the dead-filter arithmetic. Total functions over
// values, no reader of the world; the battery cuts this out at these two
// marks, compiles it alone, and asks it questions with answers known in
// advance (tests/smoke.py, "the workflows core is total").
// The regex memo lives inside the marks because globMatch is its caller
// here: a memo is process state, not a reading of the world.
// ── AND A PATTERN IS COMPILED ONCE, the way the other carrier's regex module
// keeps its own cache. Said out loud here rather than inherited. Measured
// honestly: this is NOT where this vein's cost sits. `status` spends 538ms of
// its own work against the other carrier's 110ms, the judge is 4ms of either,
// and this cache moved none of it. It stays because rebuilding a pattern for
// nothing is still rebuilding it; where the cost does sit is an open question
// with a name in the journal.
var PATTERNS: [String: NSRegularExpression] = [:]

func compiled(_ pattern: String, _ options: NSRegularExpression.Options) -> NSRegularExpression? {
    let key = "\(options.rawValue)\u{1}" + pattern
    if let held = PATTERNS[key] { return held }
    guard let made = try? NSRegularExpression(pattern: pattern, options: options) else { return nil }
    PATTERNS[key] = made
    return made
}

// ONE READER FOR THE HALF THE COURT CANNOT SEE. A pattern that matches no file
// is a divergence of the pair with no claim to refuse: the world holds, and the
// rule addresses nothing. The import walks a working tree for its paths and the
// history walk asks git for a commit's paths, so the matching lives here once
// and both callers ask it the same question.
// ── SHELL-STYLE MATCHING, WRITTEN HERE. `fnmatch` is a libc call and windows
// has no such name, so a vein that carried it built on two platforms out of
// three. Writing it once is also the honest reading: the other carrier matches
// with python's `fnmatch`, whose `*` crosses separators exactly as a zero-flag
// libc call does, and two implementations of one matching would be two
// behaviours the battery would have to hold apart.
func globMatch(_ pattern: String, _ name: String) -> Bool {
    var expr = "^"
    var chars = Array(pattern)
    var i = 0
    while i < chars.count {
        let c = chars[i]
        switch c {
        case "*": expr += ".*"
        case "?": expr += "."
        case "[":
            var j = i + 1
            if j < chars.count, chars[j] == "!" || chars[j] == "^" { j += 1 }
            if j < chars.count, chars[j] == "]" { j += 1 }
            while j < chars.count, chars[j] != "]" { j += 1 }
            if j >= chars.count {
                expr += "\\["            // an unclosed bracket is a literal one
            } else {
                var body = String(chars[(i + 1)...(j - 1)])
                if body.hasPrefix("!") { body = "^" + body.dropFirst() }
                expr += "[" + body + "]"
                i = j
            }
        default:
            expr += NSRegularExpression.escapedPattern(for: String(c))
        }
        i += 1
    }
    expr += "$"
    guard let re = compiled(expr, [.dotMatchesLineSeparators]) else { return false }
    let ns = name as NSString
    return re.firstMatch(in: name, range: NSRange(location: 0, length: ns.length)) != nil
}

// ── THE BLOCK SUBSET, READ EXACTLY OR NOT AT ALL. An adaptor translates a
// format somebody else's machine already obeys, so it may not guess: either a
// line is read the one way the format defines, or the document is refused with
// the line that stopped it. This takes the subset these files are written in:
//
//   comments and blank lines, `key:`, `key: value`, `- item`, nesting by
//   spaces, values quoted with ' or " or bare, a trailing comment after a
//   value
//
// and it stops at everything else, by name: a tab in the indentation, an
// anchor `&a`, an alias `*a`, a literal or folded scalar (`|`, `>`), a flow
// mapping `{`, a document separator. Those are legal yaml and this does not
// read them, which is a sentence it says rather than a thing it silently
// guesses at.
//
// A general yaml reader would be the wrong tool even if one were here: in yaml
// 1.1 the key `on` reads as the boolean true, so a document read that way
// answers about a key nobody wrote. Reading the text as text is the exact
// reading for this format.
final class YamlNode {
    var line = 0
    var value: String? = nil
    var children: [(key: String, node: YamlNode)] = []
    var items: [(line: Int, text: String, node: YamlNode)] = []
}

func yamlUnquote(_ said: String) -> String {
    var v = said.trimmingCharacters(in: .whitespaces)
    if let q = v.first, q == "\"" || q == "'" {
        let rest = v.dropFirst()
        if let end = rest.firstIndex(of: q) { return String(rest[rest.startIndex..<end]) }
        return String(rest)
    }
    if let hash = v.range(of: " #") { v = String(v[v.startIndex..<hash.lowerBound]) }
    return v.trimmingCharacters(in: .whitespaces)
}

func yamlBlock(_ text: String) -> (root: YamlNode, refused: (line: Int, why: String)?) {
    let root = YamlNode()
    var stack: [(indent: Int, node: YamlNode)] = [(-1, root)]
    var opened = false
    var skipTo = 0
    let lines = text.components(separatedBy: "\n")
    for (n, raw) in lines.enumerated() {
        if n < skipTo { continue }
        let no = n + 1
        if raw.trimmingCharacters(in: .whitespaces).isEmpty { continue }
        if raw.contains("\t") {
            return (root, (no, "a tab in the indentation, which yaml does not allow and "
                             + "this does not straighten out"))
        }
        let said = raw.trimmingCharacters(in: .whitespaces)
        if said.hasPrefix("#") { continue }
        // a `---` before anything else opens THE document, which is ordinary and
        // exact; a second one opens a second document, and this reads one
        if said.hasPrefix("---") || said.hasPrefix("...") {
            if opened || said.hasPrefix("...") {
                return (root, (no, "a second document in one file: this reads one"))
            }
            opened = true
            continue
        }
        if said.hasPrefix("&") || said.hasPrefix("*") {
            return (root, (no, "an anchor or an alias, which names a value somewhere else"))
        }
        let indent = raw.prefix(while: { $0 == " " }).count
        while stack.count > 1 && indent <= stack[stack.count - 1].indent { stack.removeLast() }
        let parent = stack[stack.count - 1].node
        if said.hasPrefix("- ") || said == "-" {
            let body = said == "-" ? "" : String(said.dropFirst(2))
                .trimmingCharacters(in: .whitespaces)
            if body.contains(": ") || body.hasSuffix(":") {
                // a mapping inside a list: legal, and not a shape this asks
                // about. Its first key may still open a literal block, and
                // `- run: |` is the commonest line in these files: the block's
                // lines are its value, and reading them as keys of the list is
                // how prometheus and superset stayed unread.
                let node = YamlNode()
                node.line = no
                parent.items.append((no, "", node))
                stack.append((indent, node))
                let firstValue = body.contains(": ")
                    ? String(body[body.range(of: ": ")!.upperBound...])
                        .trimmingCharacters(in: .whitespaces)
                    : ""
                // the inline pair itself is a child of the item: `- uses: x`
                // used to vanish here, and a door judging that route read a
                // tree with the address missing
                if body.contains(": "), !firstValue.hasPrefix("|"),
                   !firstValue.hasPrefix(">"), !firstValue.isEmpty {
                    let key = String(body[body.startIndex..<body.range(of: ": ")!.lowerBound])
                        .trimmingCharacters(in: CharacterSet(charactersIn: " \"'"))
                    let child = YamlNode()
                    child.line = no
                    child.value = yamlUnquote(firstValue)
                    node.children.append((key, child))
                }
                if firstValue.hasPrefix("|") || firstValue.hasPrefix(">") {
                    var j = n + 1
                    while j < lines.count {
                        let more = lines[j]
                        if more.trimmingCharacters(in: .whitespaces).isEmpty { j += 1; continue }
                        if more.prefix(while: { $0 == " " }).count <= indent { break }
                        j += 1
                    }
                    skipTo = j
                }
                continue
            }
            if body.hasPrefix("{") || body.hasPrefix("[") {
                return (root, (no, "a flow collection, written inline in brackets"))
            }
            if body.hasPrefix("&") || body.hasPrefix("*") {
                return (root, (no, "an anchor or an alias inside a list"))
            }
            parent.items.append((no, yamlUnquote(body), YamlNode()))
            continue
        }
        // ── AND A VALUE MAY GO ON PAST ITS KEY. `key:` with nothing after it
        // opens either a mapping or a plain scalar spread over the lines under
        // it, and the format tells them apart: a line that carries `: ` or ends
        // in `:` is a key, a `- ` opens an item, and anything else at a deeper
        // indent is the value continuing. crossplane's `stale-pr-message:` is
        // four lines of English, and reading its second line as a key is how a
        // whole file went unread.
        if !said.contains(": ") && !said.hasSuffix(":") && !said.hasPrefix("- ")
            && indent > (stack.last?.indent ?? -1) {
            continue
        }
        guard let colon = said.firstIndex(of: ":") else {
            return (root, (no, "a line that is neither a key nor a list item"))
        }
        let key = String(said[said.startIndex..<colon])
            .trimmingCharacters(in: CharacterSet(charactersIn: " \"'"))
        let after = String(said[said.index(after: colon)...])
            .trimmingCharacters(in: .whitespaces)
        // a literal or folded scalar: its value is every line indented past the
        // key, which is exact, so it is stepped over rather than refused. This
        // reads no claim out of it and makes none about it: `run: |` is in
        // nearly every one of these files, and refusing the document for it
        // would mean reading none of them.
        if after.hasPrefix("|") || after.hasPrefix(">") {
            let node = YamlNode()
            node.line = no
            parent.children.append((key, node))
            var j = n + 1
            while j < lines.count {
                let body = lines[j]
                if body.trimmingCharacters(in: .whitespaces).isEmpty { j += 1; continue }
                if body.prefix(while: { $0 == " " }).count <= indent { break }
                j += 1
            }
            skipTo = j
            continue
        }
        // a flow mapping that opens and closes on its own line is an opaque
        // value with exact bounds: stepped over, never read into. One that
        // does not close there is refused, because its end is a guess.
        if after.hasPrefix("{") {
            guard after.contains("}") else {
                return (root, (no, "a flow mapping that does not close on its own line"))
            }
            let node = YamlNode()
            node.line = no
            parent.children.append((key, node))
            continue
        }
        if after.hasPrefix("&") || after.hasPrefix("*") {
            return (root, (no, "an anchor or an alias as a value"))
        }
        let node = YamlNode()
        node.line = no
        if after.hasPrefix("[") {
            // a list on one line: read exactly, item by item
            let inner = after.dropFirst().prefix(while: { $0 != "]" })
            if !after.contains("]") {
                return (root, (no, "a flow list that does not close on its own line"))
            }
            for one in inner.components(separatedBy: ",") {
                let v = yamlUnquote(one)
                if !v.isEmpty { node.items.append((no, v, YamlNode())) }
            }
        } else if after.isEmpty, n + 1 < lines.count,
                  lines[n + 1].trimmingCharacters(in: .whitespaces).hasPrefix("["),
                  lines[n + 1].prefix(while: { $0 == " " }).count > indent {
            // `key:` and the list on the line under it, which superset writes
            // for a build matrix: one value, two lines, and exact either way
            let flow = lines[n + 1].trimmingCharacters(in: .whitespaces)
            guard flow.contains("]") else {
                return (root, (no + 1, "a flow list that does not close on its own line"))
            }
            for one in flow.dropFirst().prefix(while: { $0 != "]" }).components(separatedBy: ",") {
                let v = yamlUnquote(one)
                if !v.isEmpty { node.items.append((no + 1, v, YamlNode())) }
            }
            skipTo = n + 2
        } else if !after.isEmpty && !after.hasPrefix("#") {
            node.value = yamlUnquote(after)
            // a quoted scalar may run past its line, and it ends at its own
            // closing quote: exact, and stepped over the same way a literal
            // block is. `run: "cd x && \` spread over five lines is ordinary
            // in these files, and its lines are not keys of anything.
            if let q = after.first, q == "\"" || q == "'",
               after.dropFirst().firstIndex(of: q) == nil {
                var j = n + 1
                while j < lines.count {
                    let more = lines[j]
                    j += 1
                    if more.contains(String(q)) { break }
                }
                skipTo = j
            }
        }
        parent.children.append((key, node))
        stack.append((indent, node))
    }
    return (root, nil)
}

// the value at an address in the document, and nothing that merely looks like it
func yamlAt(_ node: YamlNode, _ address: [String]) -> YamlNode? {
    var here = node
    for key in address {
        guard let next = here.children.first(where: { $0.key == key })?.node else { return nil }
        here = next
    }
    return here
}

func yamlList(_ node: YamlNode, _ address: [String]) -> [(line: Int, text: String)] {
    guard let at = yamlAt(node, address) else { return [] }
    var out = at.items.filter { !$0.text.isEmpty }.map { (line: $0.line, text: $0.text) }
    // `paths: src/**` with one value is a list of one, the way that platform reads it
    if out.isEmpty, let v = at.value, !v.isEmpty { out = [(at.line, v)] }
    return out
}

// the dead-filter arithmetic, total over values. The matching is wider than
// that platform's on purpose: here `*` crosses a separator, there it does not
// and `**` does, so a pattern this calls dead is dead by the narrower reading
// too, and the error is pushed to the side that costs a missed finding rather
// than a wrong accusation.
// the union all three death questions share. Clause five is the zero-width
// `**`: both platforms read `**/x` as x at any depth INCLUDING none (root),
// and a union without it buries live roots (caught on tauri `**/Cargo.lock`,
// 2026-08-23). The error side of a death claim is: match generously.
func routeAlive(_ pat: String, _ p: String) -> Bool {
    if globMatch(pat, p) || globMatch(pat + "/*", p) || p.hasPrefix(pat + "/")
        || globMatch(pat, (p as NSString).lastPathComponent) { return true }
    if pat.contains("**/") {
        let collapsed = pat.replacingOccurrences(of: "**/", with: "")
        if !collapsed.isEmpty && globMatch(collapsed, p) { return true }
    }
    return false
}

// the Actions filter law is its own dialect (docs, verbatim): `?` matches
// zero or one OF THE PRECEDING character, `+` one or more of it, `*` stays
// inside a segment, `**` crosses. fnmatch reading of `?` buried a LIVE
// filter (flask **/*.yaml?, 13 runs on record, 2026-08-25): the run count
// of the executor is the natural control of every "does not run" claim.
func actionsFilterMatch(_ pattern: String, _ name: String) -> Bool {
    var expr = "^"
    let chars = Array(pattern)
    var i = 0
    while i < chars.count {
        let c = chars[i]
        switch c {
        case "*":
            if i + 1 < chars.count && chars[i + 1] == "*" { expr += ".*"; i += 1 }
            else { expr += "[^/]*" }
        case "?": expr += "?"
        case "+": expr += "+"
        case "[":
            var j = i + 1
            while j < chars.count, chars[j] != "]" { j += 1 }
            if j >= chars.count { expr += "\\[" }
            else { expr += "[" + String(chars[(i + 1)...(j - 1)]) + "]"; i = j }
        default:
            expr += NSRegularExpression.escapedPattern(for: String(c))
        }
        i += 1
    }
    expr += "$"
    guard let re = compiled(expr, [.dotMatchesLineSeparators]) else { return true }
    let ns = name as NSString
    return re.firstMatch(in: name, range: NSRange(location: 0, length: ns.length)) != nil
}

func actionsFilterAlive(_ pat: String, _ p: String) -> Bool {
    if actionsFilterMatch(pat, p) || p.hasPrefix(pat + "/") { return true }
    if pat.contains("**/") {
        let collapsed = pat.replacingOccurrences(of: "**/", with: "")
        if !collapsed.isEmpty && actionsFilterMatch(collapsed, p) { return true }
    }
    return false
}

func workflowsDeadFilters(_ filters: [(file: String, line: Int, key: String, pattern: String)],
                          _ paths: [String]) -> [(address: String, claim: String)] {
    var dead: [(String, String)] = []
    for f in filters {
        var pat = f.pattern
        // a negation names what NOT to wake on: a dead one excludes nothing,
        // which is harmless, and "waits for a change" would be the wrong
        // consequence. Its side is different, so no death claim is made.
        if pat.hasPrefix("!") { continue }
        while pat.hasPrefix("/") { pat.removeFirst() }
        while pat.hasSuffix("/") { pat.removeLast() }
        if pat.isEmpty { continue }
        let hit = paths.contains { p in actionsFilterAlive(pat, p) }
        if !hit {
            dead.append(("\(f.file):\(f.line)",
                         "`\(f.key)` names `\(f.pattern)`, and no file in the tree "
                       + "matches it: this workflow waits for a change that cannot "
                       + "arrive"))
        }
    }
    return dead
}
// ── WORKFLOWS CORE END.

// ── REFS CORE BEGIN. The pure heart of `import refs`: tracked issues and
// code citations into the reference world, total over values. The shelf
// page arrives as a parameter, the way the codeowners core takes its page;
// `sanitized` is the codeowners core's, and the battery compiles the two
// cuts together and asks this one alone.
func refsWorldBuild(_ tracked: [(key: String, state: String)],
                    _ cites: [(file: String, line: Int, key: String)],
                    _ head: String)
    -> (world: String, srcmap: [String: (address: String, key: String)]) {
    var lines = [head, ""]
    var keys = Set(cites.map { $0.key })
    for t in tracked { keys.insert(t.key) }
    for key in keys.sorted() {
        guard let state = tracked.first(where: { $0.key == key })?.state else { continue }
        lines.append("public enum \(sanitized(key)): Tracked {")
        lines.append("    public typealias State = \(state)")
        lines.append("}")
    }
    var srcmap: [String: (address: String, key: String)] = [:]
    var seen = Set<String>()
    for (i, c) in cites.enumerated() {
        let site = "At_\(sanitized(c.file))_L\(c.line)"
        if seen.contains(site) { continue }
        seen.insert(site)
        lines.append("public enum \(site): Site {}")
        let cert = "Cite_\(i)"
        lines.append("public typealias \(cert) = Cites<\(site), \(sanitized(c.key))>")
        srcmap[cert] = ("\(c.file):\(c.line)", c.key)
    }
    return (lines.joined(separator: "\n") + "\n", srcmap)
}
// ── REFS CORE END.

// ── RBAC CORE BEGIN. The pure heart of `import rbac`: a kubectl dump's
// items, already read as Said values, into the grants world with the read
// gate declared. Total over values: the key ladder, the namespace rooms,
// the cluster scope and the bindings all decide from the values alone; the
// battery compiles this under the said and codeowners cores and asks it
// with answers known in advance.
let RBAC_WRITES: Set<String> = ["create", "update", "patch", "delete", "deletecollection"]

func rbacKey(_ rules: [Said]) -> String {
    var verbs = Set<String>()
    for r in rules { for v in r.at("verbs")?.asList ?? [] { verbs.insert(v.asText ?? "") } }
    if verbs.contains("*") || !verbs.isDisjoint(with: ["escalate", "bind", "impersonate"]) {
        return "WardenKey"
    }
    if !verbs.isDisjoint(with: RBAC_WRITES) { return "WriterKey" }
    return "ReaderKey"
}

func rbacWorldBuild(_ items: [Said], _ head: String)
    -> (world: String, srcmap: [String: String], checked: Int,
        namespaces: Int, roles: Int, clusterRoles: Int) {
    var roleOrder: [String] = [], roles: [String: Said] = [:]
    var clusterOrder: [String] = [], clusterRoles: [String: Said] = [:]
    var bindings: [Said] = []
    var namespaces = Set<String>()
    for it in items {
        let kind = it.at("kind")?.asText ?? ""
        let meta = it.at("metadata")
        let ns = meta?.at("namespace")?.asText ?? ""
        let name = meta?.at("name")?.asText ?? ""
        if kind == "Role" {
            let key = ns + "\u{0}" + name
            if roles[key] == nil { roleOrder.append(key) }
            roles[key] = it
            namespaces.insert(ns)
        } else if kind == "ClusterRole" {
            if clusterRoles[name] == nil { clusterOrder.append(name) }
            clusterRoles[name] = it
        } else if kind == "RoleBinding" {
            bindings.append(it)
            namespaces.insert(ns)
        }
    }
    var lines = [head]
    // the read gate, this world's own: a read binding is not entry to work a
    // room, and pushing it through the writing gate was a lie the court
    // could not see while it dropped the conjunct
    lines.append("")
    lines.append("public protocol Viewed {}")
    lines.append("public enum View<Who: Keeper, Into: Room> {}")
    lines.append("extension View: Viewed")
    lines.append("where Who.Key: Reads, Who.Post == Into.Place {}")
    var srcmap: [String: String] = [:]
    for ns in namespaces.sorted() { lines.append("public enum Ns_\(sanitized(ns)): Realm {}") }
    lines.append("public enum ClusterScope: Realm {}")
    lines.append("")
    for key in roleOrder.sorted() {
        let two = key.components(separatedBy: "\u{0}")
        lines.append("public enum Role_\(sanitized(two[0]))_\(sanitized(two[1])): Room {")
        lines.append("    public typealias Place = Ns_\(sanitized(two[0]))")
        lines.append("}")
    }
    for name in clusterOrder.sorted() {
        lines.append("public enum CR_\(sanitized(name)): Room {")
        lines.append("    public typealias Place = ClusterScope")
        lines.append("}")
    }
    lines.append("")
    var checked = 0
    for b in bindings {
        let meta = b.at("metadata")
        let bns = meta?.at("namespace")?.asText ?? ""
        let bname = meta?.at("name")?.asText ?? ""
        let ref = b.at("roleRef")
        let rkind = ref?.at("kind")?.asText ?? ""
        let rname = ref?.at("name")?.asText ?? ""
        let keeper = "B_\(sanitized(bns))_\(sanitized(bname))"
        let cert = "Bind_\(sanitized(bns))_\(sanitized(bname))"
        var post = "", room = "", key = "", what = ""
        if rkind == "ClusterRole" {
            post = "ClusterScope"
            room = "CR_\(sanitized(rname))"
            key = rbacKey(clusterRoles[rname]?.at("rules")?.asList ?? [])
            what = "rolebinding \(bns)/\(bname) -> clusterrole \(rname)"
        } else {
            post = "Ns_\(sanitized(bns))"
            key = rbacKey(roles[bns + "\u{0}" + rname]?.at("rules")?.asList ?? [])
            if roles[bns + "\u{0}" + rname] != nil {
                room = "Role_\(sanitized(bns))_\(sanitized(rname))"
            } else {
                let foreign = roleOrder.compactMap { k -> String? in
                    let two = k.components(separatedBy: "\u{0}")
                    return two[1] == rname ? two[0] : nil
                }.sorted()
                room = "Role_\(sanitized(foreign.first ?? bns))_\(sanitized(rname))"
            }
            what = "rolebinding \(bns)/\(bname) -> role \(rname)"
        }
        lines.append("public enum \(keeper): Keeper {")
        lines.append("    public typealias Post = \(post)")
        lines.append("    public typealias Key = \(key)")
        lines.append("}")
        lines.append("public typealias \(cert) = "
                     + (key == "ReaderKey" ? "View" : "Enter") + "<\(keeper), \(room)>")
        srcmap[cert] = what
        checked += 1
    }
    return (lines.joined(separator: "\n") + "\n", srcmap, checked,
            namespaces.count, roleOrder.count, clusterOrder.count)
}
// ── RBAC CORE END.

// ── ADDRESSES CORE BEGIN. Every route a repository declares in its standard
// files, judged by existence: a workflow step using a local action that is
// not there, a working directory the tree does not carry, a dependabot
// directory whose updates are silently off, a labeler glob matching nothing,
// a README badge pointing at a workflow that does not exist. An address is a
// promise of a route; these are the promises this door can read today. Total
// over values (the yaml reader and the matcher are the workflows core's own);
// the battery cuts this out and compiles it under that core.

// every (key, line, value) pair of a yaml document, depth-first: the shapes
// judged here live at unknown nesting, so the walk is generic
func yamlPairs(_ node: YamlNode) -> [(key: String, line: Int, value: String)] {
    var out: [(key: String, line: Int, value: String)] = []
    for (key, child) in node.children {
        if let v = child.value, !v.isEmpty { out.append((key, child.line, v)) }
        out += yamlPairs(child)
    }
    for item in node.items { out += yamlPairs(item.node) }
    return out
}

// every list item text of a yaml document, with its line
func yamlItems(_ node: YamlNode) -> [(line: Int, text: String)] {
    var out: [(line: Int, text: String)] = []
    for item in node.items {
        if !item.text.isEmpty { out.append((item.line, item.text)) }
        out += yamlItems(item.node)
    }
    for (_, child) in node.children { out += yamlItems(child) }
    return out
}

// the four-clause route match, the same reading the codeowners ghosts use
func routeMatches(_ pattern: String, _ files: [String]) -> Bool {
    var pat = pattern
    if pat.hasPrefix("!") { pat.removeFirst() }
    while pat.hasPrefix("/") { pat.removeFirst() }
    while pat.hasSuffix("/") { pat.removeLast() }
    if pat.isEmpty { return true }
    return files.contains { p in routeAlive(pat, p) }
}


func hasDir(_ path: String, _ files: [String]) -> Bool {
    var p = path
    while p.hasPrefix("/") { p.removeFirst() }
    while p.hasSuffix("/") { p.removeLast() }
    if p.isEmpty { return true }
    return files.contains { $0.hasPrefix(p + "/") }
}

// one workflow file: local `uses:` and `working-directory:` judged
func wfAddressFindings(_ name: String, _ text: String, _ files: [String])
    -> (found: [(cls: String, address: String, claim: String)],
        unread: [(address: String, claim: String)], judged: Int) {
    let doc = yamlBlock(text)
    if let refused = doc.refused {
        return ([], [("\(name):\(refused.line)",
                      "this reading takes the block subset these files are written in, "
                    + "and stops at what it cannot read exactly: \(refused.why). "
                    + "No claim is made about this file")], 0)
    }
    var found: [(cls: String, address: String, claim: String)] = []
    var judged = 0
    // ── AND A ROUTE THE JOB ITSELF BUILDS IS NOT A DEAD ONE. A checkout
    // with `path: X` puts a working copy at X, and `./X/...` exists at run
    // time while the tree at HEAD knows nothing of it: spring-boot and
    // langchain both wear that shape. The error must cost a missed finding
    // rather than a wrong accusation, so a first segment mentioned anywhere
    // else in the file (a path:, an mkdir, an mv) silences the claim.
    func builtInFile(_ p: String) -> Bool {
        guard let seg = p.components(separatedBy: "/").first, !seg.isEmpty
        else { return true }
        return text.components(separatedBy: seg).count - 1 > 1
    }
    for (key, line, raw) in yamlPairs(doc.root) {
        let value = yamlUnquote(raw)
        if key == "uses" && value.hasPrefix("./") {
            judged += 1
            var p = String(value.dropFirst(2))
            while p.hasSuffix("/") { p.removeLast() }
            let ok = files.contains(p) || hasDir(p, files)
            if !ok && !builtInFile(p) {
                found.append(("workflow-uses", "\(name):\(line)",
                              "`uses: ./\(p)` and no such action is in the tree: "
                            + "the step silently has nothing to run"))
            }
        }
        if key == "working-directory" {
            let v = yamlUnquote(raw)
            if v.isEmpty || v == "." || v.contains("$") || v.contains("*") { continue }
            judged += 1
            var p = v
            if p.hasPrefix("./") { p = String(p.dropFirst(2)) }
            if !hasDir(p, files) && !files.contains(p) && !builtInFile(p) {
                found.append(("workflow-workdir", "\(name):\(line)",
                              "`working-directory: \(v)` is not in the tree: "
                            + "the step starts where nothing is"))
            }
        }
    }
    return (found, [], judged)
}

// dependabot: `directory:` and `directories:` entries judged as tree dirs
func dependabotFindings(_ name: String, _ text: String, _ files: [String])
    -> (found: [(cls: String, address: String, claim: String)],
        unread: [(address: String, claim: String)], judged: Int) {
    let doc = yamlBlock(text)
    if let refused = doc.refused {
        return ([], [("\(name):\(refused.line)",
                      "this reading takes the block subset these files are written in, "
                    + "and stops at what it cannot read exactly: \(refused.why). "
                    + "No claim is made about this file")], 0)
    }
    var found: [(cls: String, address: String, claim: String)] = []
    var judged = 0
    func judge(_ line: Int, _ raw: String) {
        let v = yamlUnquote(raw)
        guard v.hasPrefix("/"), !v.contains("$"), !v.contains("*") else { return }
        judged += 1
        if v != "/" && !hasDir(v, files) {
            found.append(("dependabot", "\(name):\(line)",
                          "`directory: \(v)` is not in the tree: "
                        + "updates for this ecosystem are silently off"))
        }
    }
    for (key, line, raw) in yamlPairs(doc.root) where key == "directory" {
        judge(line, raw)
    }
    for item in yamlItems(doc.root) where yamlUnquote(item.text).hasPrefix("/") {
        judge(item.line, item.text)
    }
    return (found, [], judged)
}

// labeler: list items that read as tree globs, judged by the route match
func labelerFindings(_ name: String, _ text: String, _ files: [String])
    -> (found: [(cls: String, address: String, claim: String)],
        unread: [(address: String, claim: String)], judged: Int) {
    let doc = yamlBlock(text)
    if let refused = doc.refused {
        return ([], [("\(name):\(refused.line)",
                      "this reading takes the block subset these files are written in, "
                    + "and stops at what it cannot read exactly: \(refused.why). "
                    + "No claim is made about this file")], 0)
    }
    var found: [(cls: String, address: String, claim: String)] = []
    var judged = 0
    for item in yamlItems(doc.root) {
        let v = yamlUnquote(item.text)
        guard v.contains("/"), !v.contains(" "), !v.contains("$"),
              !v.hasPrefix("http") else { continue }
        judged += 1
        if !routeMatches(v, files) {
            found.append(("labeler", "\(name):\(item.line)",
                          "`\(v)` matches nothing in the tree: "
                        + "this label is never applied"))
        }
    }
    return (found, [], judged)
}

// README badges: actions/workflows/NAME must name a workflow that exists
func badgeFindings(_ name: String, _ text: String, _ files: [String])
    -> (found: [(cls: String, address: String, claim: String)], judged: Int) {
    var found: [(cls: String, address: String, claim: String)] = []
    var judged = 0
    let needle = "actions/workflows/"
    for (n0, line) in text.components(separatedBy: "\n").enumerated() {
        var rest = Substring(line)
        while let r = rest.range(of: needle) {
            rest = rest[r.upperBound...]
            var wf = ""
            for ch in rest {
                if ch.isLetter || ch.isNumber || ch == "_" || ch == "-" || ch == "." {
                    wf.append(ch)
                } else { break }
            }
            guard wf.hasSuffix(".yml") || wf.hasSuffix(".yaml") else { continue }
            judged += 1
            if !files.contains(".github/workflows/" + wf) {
                found.append(("badge", "\(name):\(n0 + 1)",
                              "the badge points at `\(wf)` and no such workflow exists: "
                            + "the cover wears a verdict nothing earns"))
            }
        }
    }
    return (found, judged)
}
// ── ADDRESSES CORE END.

// ── EVERY PATH THIS TREE CARRIES, WHICH IS NOT EVERY REGULAR FILE IN IT. A
// repository tracks a symbolic link as a path of its own, and the walk under
// this asked `fileExists`, which FOLLOWS one: a link to a folder answered
// "directory" and was stepped over, so a folder that is a wall of links read as
// empty and every rule naming it was refused. Measured on apache/airflow, where
// `/.github/skills/` is nine links into `.agents/skills` and the court called
// the rule dead over a folder their tree carries. What is asked here is the
// entry's OWN kind, which is what `attributesOfItem` reads, and everything that
// is not a folder is a path this tree carries. An entry whose kind cannot be
// read at all is carried too: this reader exists to answer what is here, and
// the refusal it feeds must never be manufactured by a reader's own blindness.
func treeFiles(_ root: String) -> [String] {
    mark("walk:" + lastName(root))
    var paths: [String] = []
    guard let walk = FileManager.default.enumerator(atPath: root) else { return paths }
    for case let rel as String in walk {
        if rel.components(separatedBy: "/").contains(".git") {
            walk.skipDescendants()
            continue
        }
        let full = (root as NSString).appendingPathComponent(rel)
        let kind = (try? FileManager.default.attributesOfItem(atPath: full))?[.type]
            as? FileAttributeType
        if kind != .typeDirectory { paths.append(rel) }
    }
    return paths
}

func ghostPatterns(_ rules: [(line: Int, pattern: String, owners: [String])],
                   _ paths: [String], _ saidName: String) -> [(address: String, claim: String)] {
    var out: [(address: String, claim: String)] = []
    for r in rules {
        var pat = r.pattern
        while pat.hasPrefix("/") { pat.removeFirst() }
        while pat.hasSuffix("/") { pat.removeLast() }
        let hit = paths.contains { p in routeAlive(pat, p) }
        if !hit {
            out.append(("\(saidName):\(r.line)",
                        "CODEOWNERS names `\(r.pattern)`, and no file in "
                        + "the tree matches it: the rule matches nothing"))
        }
    }
    return out
}

struct HistoryRow {
    var at = "", when = "", file = ""
    var rules = 0, unmatched = 0
    var refusals: Int? = nil, divergences: Int? = nil
    var judged = false, read = false
}

// ── THE PAIR'S IMAGE, COMMIT BY COMMIT. `findings` says what is true of a
// repository now; this says what has been true of one pair over its history. At
// each commit the two sides are read out of git (the rules file, and the tree
// the rules address), translated by the ONE translator the import verb uses, and
// the image's divergences counted. Nothing is checked out and nothing is written
// into the repository: a commit's text goes to a scratch directory that leaves
// when the walk does.
//
// WHAT THIS COUNTS, said here because the number is easy to over-read: the
// divergences of the pair's JUDGED IMAGE under the declared translation, not the
// distance between the two records. A divergence of the image is a divergence of
// the pair; the reverse is not claimed.
func historyDivergence(_ n: Int, policyName: String?) -> (rows: [HistoryRow], whole: Bool) {
    loadStatusShelf()
    let w = discoverWorld()
    let base = w.facts.map { (absPath($0) as NSString).deletingLastPathComponent }
        ?? FileManager.default.currentDirectoryPath
    // ── AND THE WALK IS THE MAIN LINE, WHICH IS THE ONLY ONE THAT IS A TIME.
    // Plain `git log --reverse` walks the whole graph, so on a repository that
    // merges, adjacent rows sit on different branches and the same weeks are
    // read several times over: of 3000 rows on one public repository, 206 step
    // BACKWARDS in time. `--first-parent` reads five. It is also the right
    // sequence to claim: the states this repository actually stood in.
    let log = runGit(["log", "-\(n)", "--format=%H%x1f%aI", "--reverse", "--first-parent"], base)
        .trimmingCharacters(in: .whitespacesAndNewlines)
    if log.isEmpty { return ([], true) }
    // ── AND THE WALK KNOWS WHETHER IT REACHED THE START, which is the whole
    // difference between `parted before this reading` and `never agreed`. A line
    // cut by a shallow clone is not a line that ended, so git is asked which it
    // is rather than guessed at.
    let seen = log.components(separatedBy: "\n")
    let whole = seen.count < n
        && runGit(["rev-parse", "--is-shallow-repository"], base)
            .trimmingCharacters(in: .whitespacesAndNewlines) != "true"
    let tmp = tempRoot() + "/gate-history-\(ProcessInfo.processInfo.processIdentifier)"
    try? FileManager.default.createDirectory(atPath: tmp, withIntermediateDirectories: true)
    defer { try? FileManager.default.removeItem(atPath: tmp) }
    // AND THE PAIR IS LOOKED FOR AT EVERY COMMIT, not once at the tip. A file
    // moves: a CODEOWNERS written at the root and later filed under `.github` is
    // the same pair, and a walk that asks one path draws the history of a name
    // instead. The place that answered last is tried first.
    var places = CODEOWNERS_PLACES
    var rows: [HistoryRow] = []
    for line in seen {
        let parts = line.components(separatedBy: "\u{1f}")
        let sha = parts.count > 0 ? parts[0] : ""
        let when = parts.count > 1 ? String(parts[1].prefix(10)) : ""
        var said: String? = nil
        for (i, place) in places.enumerated() {
            if let text = gitShow(sha + ":" + place, base) {
                said = text
                if i != 0 { places.insert(places.remove(at: i), at: 0) }
                break
            }
        }
        guard let text = said else { continue }   // the pair does not exist at this commit
        let paths = runGit(["ls-tree", "-r", "--name-only", sha], base)
            .components(separatedBy: "\n").filter { !$0.isEmpty }
        var policy: [(owner: String, zone: String)] = []
        if let name = policyName, let pt = gitShow(sha + ":" + name, base) {
            let pp = (tmp as NSString).appendingPathComponent("policy.csv")
            try? pt.write(toFile: pp, atomically: false, encoding: .utf8)
            policy = readOwnersPolicy(pp)
        }
        let here = places[0]
        let cp = (tmp as NSString).appendingPathComponent((here as NSString).lastPathComponent)
        try? text.write(toFile: cp, atomically: false, encoding: .utf8)
        let rules = readCodeowners(cp)
        let (lines, srcmap, _, _) = codeownersWorldLines(cp, policy, here)
        let wp = (tmp as NSString).appendingPathComponent("world.swift")
        try? (lines.joined(separator: "\n") + "\n").write(toFile: wp, atomically: false,
                                                          encoding: .utf8)
        let out = courtSays(["where", wp])
        // and the court answered in its own voice, or this row is not a reading
        // at all: a silence parses as nought refusals, which would draw a flat
        // curve over a court that never sat
        let spoke = (out.contains("THE WHERE") && out.contains("canon v")) || out.contains("✗")
        let refused = whereRefused(out).filter { $0.cert.map { srcmap[$0] != nil } ?? false }
        let ghosts = ghostPatterns(rules, paths, (here as NSString).lastPathComponent)
        var row = HistoryRow(at: String(sha.prefix(8)), when: when, file: here,
                             rules: rules.count, unmatched: ghosts.count)
        row.refusals = spoke ? refused.count : nil
        row.divergences = spoke ? refused.count + ghosts.count : nil
        row.judged = !policy.isEmpty
        row.read = spoke
        rows.append(row)
    }
    return (rows, whole)
}

func historyMarkdown(_ rows: [HistoryRow], _ parted: String?) -> String {
    // the walk as a note somebody could paste into an issue: the sentence first,
    // and then the TURNING POINTS only. Pasting two hundred rows into a thread is
    // the same mistake the fold exists against.
    if rows.isEmpty {
        return "Nothing to report: no commit in this history carries the file this reads.\n"
    }
    var turns: [HistoryRow] = []
    for (i, r) in rows.enumerated() where i == 0 || r.divergences != rows[i - 1].divergences {
        turns.append(r)
    }
    var lines = ["### The pair over " + many(rows.count, "commit"), ""]
    lines.append(parted ?? "the two records agree at this repository's tip.")
    lines += ["", "| commit | date | divergences | rules |", "| --- | --- | --- | --- |"]
    for r in turns {
        let n = r.divergences.map { String($0) } ?? "not read"
        lines.append("| `\(r.at)` | \(r.when) | \(n) | \(r.rules) |")
    }
    lines += ["", "<sub>\(turns.count) row\(turns.count == 1 ? "" : "s") where the count "
              + "changed, of \(rows.count) read. "
              + "Divergences of the pair's judged image: claims the court refuses, plus "
              + "rules that address nothing. Read it yourself with "
              + "`gate findings --history`.</sub>", ""]
    return lines.joined(separator: "\n")
}

// every whole match of a pattern, in the order they stand: `matches` hands back
// capture groups, and a pattern with none of those has nothing to hand back
func wholeMatches(_ pattern: String, _ text: String) -> [String] {
    guard let re = try? NSRegularExpression(pattern: pattern) else { return [] }
    let ns = text as NSString
    return re.matches(in: text, range: NSRange(location: 0, length: ns.length))
        .map { ns.substring(with: $0.range) }
}

// the world's two tables, read back out of the text it is written in
func worldRows(_ text: String) -> (people: [[(String, String)]], grants: [(String, String)]) {
    var people: [[(String, String)]] = []
    for m in matches("public enum (\\w+): Employee, Person \\{(.*?)\\n\\}", text, dotAll: true) {
        var row: [(String, String)] = [("id", m[0])]
        for f in matches("public typealias (\\w+) = ([\\w.]+)", m[1]) where f[0] != "Sex" {
            row.append((f[0].lowercased(), f[1]))
        }
        people.append(row)
    }
    let grants = matches("VerifiedView<\\s*(\\w+),\\s*(\\w+)\\s*>\\.self;", text)
        .map { ($0[0], $0[1]) }
    return (people, grants)
}

// the judge pins a refusal to the previous drain's line: refine the address to
// the line holding the refusal's subject, in a window nearby
func refineAddresses(_ text: String, _ refusals: [(address: String, claim: String)],
                     _ fname: String) -> [(address: String, claim: String)] {
    let fileLines = text.components(separatedBy: "\n")
    return refusals.map { ref in
        let parts = ref.address.components(separatedBy: ":")
        guard parts.count > 1, let n = Int(parts[1]) else { return ref }
        let found = matches("requires (\\w+)\\.", ref.claim).first?.first
            ?? matches("(\\w+)(?:\\.\\w+)? resolves to nothing", ref.claim).first?.first
            ?? matchAt(ref.claim, "(\\w+)\\.").map { $0[1] }
        guard let subject = found else { return ref }
        for k in max(0, n - 4)..<min(fileLines.count, n + 8) {
            if !matches("\\b" + subject + "\\b", fileLines[k]).isEmpty
                || fileLines[k].range(of: "\\b" + subject + "\\b", options: .regularExpression)
                    != nil {
                return (address: "\(fname):\(k + 1)", claim: ref.claim)
            }
        }
        return ref
    }
}

// ── THE JUDGE'S OWN READING, ASKED FOR. Nothing here grows a grammar over
// somebody's world: `judge parse` hands out the parse the court already made,
// and both carriers ask the same route for it. The route lives in the port's
// wrapper, so it needs node even where the binary judges.
func whichNode() -> String? {
    for dir in (ProcessInfo.processInfo.environment["PATH"] ?? "").components(separatedBy: ":") {
        let p = (dir as NSString).appendingPathComponent("node")
        if FileManager.default.isExecutableFile(atPath: p) { return p }
    }
    return nil
}

func worldParse(_ path: String) -> Said {
    let node = whichNode()
    let port = joinPath(toolRoot(), "bin/judge-cli.js")
    guard let node = node, FileManager.default.fileExists(atPath: port) else {
        cannot("this reads the judge's own parse, and that route is the node port",
               "install node, which serves it through bin/judge-cli.js, or read the "
               + "file itself: it is plain Swift and `swiftc -typecheck` reads it too")
    }
    mark("spawn:node")
    let p = Process()
    p.executableURL = URL(fileURLWithPath: node)
    p.arguments = [port, "judge", "parse", path]
    let pipe = Pipe(), quiet = Pipe()
    p.standardOutput = pipe
    p.standardError = quiet
    var said = "", why = ""
    if (try? p.run()) != nil {
        said = String(data: pipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
        why = String(data: quiet.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
        waitDone(p)
    }
    if p.terminationStatus != 0 || said.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
        let first = why.split(separator: "\n").first.map(String.init) ?? "no reason given"
        cannot("the parse of " + (path as NSString).lastPathComponent + " came back empty: "
               + String(first.trimmingCharacters(in: .whitespaces).prefix(90)),
               "check the file is the Swift this judges, or run `gate status` to see "
               + "what the court says about it")
    }
    guard let top = readSaid(said), let one = top.asObject?.first?.1 else {
        cannot("the parse of " + (path as NSString).lastPathComponent + " is not a reading",
               "run `gate status` to see what the court says about it")
    }
    return one
}

func saidInt(_ s: Said?) -> Int {
    guard let s = s else { return 0 }
    if case .number(let n) = s { return Int(Double(n) ?? 0) }
    return Int(s.asText ?? "") ?? 0
}

// the `///` a writer put above a record is that record's own sentence
func bareNote(_ lines: [String], _ at: Int) -> String {
    var said: [String] = []
    var i = at - 2
    while i >= 0 && i < lines.count && lines[i].trimmingCharacters(in: .whitespaces)
        .hasPrefix("///") {
        var one = lines[i].trimmingCharacters(in: .whitespaces)
        while one.hasPrefix("/") { one.removeFirst() }
        said.insert(one.trimmingCharacters(in: .whitespaces), at: 0)
        i -= 1
    }
    return said.filter { !$0.isEmpty }.joined(separator: " ")
}

struct BareComment { var line = 0; var kind = ""; var text = "" }

// ── THE PROSE THE FILE ALREADY CARRIES, READ THE WAY IT WAS WRITTEN. A run of
// comment lines is one paragraph and a blank `//` is where the writer stopped;
// `── like this ──` is a heading; four spaces inside a comment is set, not
// flowed; `role:` and `opens:` are how a file tells this tool what it is, not
// something it says to a reader; `== word` marks a phrase and is not read out.
// A `///` line above a record belongs to that record and travels with it.
func bareComments(_ lines: [String], _ heads: [Int]) -> [BareComment] {
    var taken = Set<Int>()
    for at in heads {
        var i = at - 2
        while i >= 0 && i < lines.count && lines[i].trimmingCharacters(in: .whitespaces)
            .hasPrefix("///") { taken.insert(i); i -= 1 }
    }
    var out: [BareComment] = []
    var run: Int? = nil          // index into out
    for (i, raw) in lines.enumerated() {
        let stripped = raw.trimmingCharacters(in: .whitespaces)
        if !stripped.hasPrefix("//") || taken.contains(i) { run = nil; continue }
        let body = raw.replacingOccurrences(of: "^\\s*/+", with: "",
                                            options: .regularExpression)
        let said = body.trimmingCharacters(in: .whitespaces)
        if said.isEmpty
            || said.range(of: "^(role|opens):", options: [.regularExpression, .caseInsensitive])
                != nil
            || said.hasPrefix("== ") { run = nil; continue }
        if let head = matchAt(said, "^──+\\s*(.+?)\\s*──+$") {
            run = nil
            out.append(BareComment(line: i + 1, kind: "head", text: head[1]))
            continue
        }
        if body.range(of: "^\\s{4,}", options: .regularExpression) != nil {
            let cut = body.replacingOccurrences(of: "^\\s{1,4}", with: "",
                                                options: .regularExpression)
            if let r = run, out[r].kind == "set" { out[r].text += "\n" + cut }
            else {
                out.append(BareComment(line: i + 1, kind: "set", text: cut))
                run = out.count - 1
            }
            continue
        }
        if let r = run, out[r].kind == "prose" { out[r].text += " " + said }
        else {
            out.append(BareComment(line: i + 1, kind: "prose", text: said))
            run = out.count - 1
        }
    }
    return out.filter { !$0.text.isEmpty }
}

// ── BARE IS THE RECORD WITHOUT CEREMONY, NEVER THE RECORD WITHOUT ITS CONTENT.
// The same items the bench's own bare view draws, in the order the document has
// them: a record with its columns, the holes it opens, the clause it conforms
// under, the one string it is allowed, and the claims written inside it.
func bareLines(_ parsed: Said, _ text: String, _ only: [String]) -> [String] {
    let lines = text.components(separatedBy: "\n")
    var items: [(Int, [String])] = []
    let declarations = parsed.at("declarations")?.asList ?? []
    let topAliases = parsed.at("topAliases")?.asObject ?? []
    for d in declarations {
        let name = d.at("name")?.asText ?? ""
        if !only.isEmpty && !only.contains(name) { continue }
        var head = name
        let conformances = (d.at("conformances")?.asList ?? []).compactMap { $0.asText }
        if !conformances.isEmpty { head += ": " + conformances.joined(separator: ", ") }
        if let whereText = d.at("whereText")?.asText, !whereText.isEmpty {
            head += " when " + whereText
        }
        var block: [String] = []
        let at = saidInt(d.at("line"))
        let note = bareNote(lines, at)
        if !note.isEmpty { block.append(note) }
        block.append(head)
        if let typeName = d.at("typeName")?.asText { block.append("    \"" + typeName + "\"") }
        for (k, v) in d.at("aliases")?.asObject ?? [] {
            block.append("    \(k) = " + (v.at("target")?.asText ?? ""))
        }
        // a hole is a line, and the line says what may fill it: a gate's
        // parameter and a protocol's axis are the same act written two ways
        let kinds = (d.at("paramKinds")?.asList ?? []).map { $0.asText }
        var holes: [(String, String?)] = []
        for (i, a) in (d.at("params")?.asList ?? []).enumerated() {
            holes.append((a.asText ?? "", i < kinds.count ? kinds[i] : nil))
        }
        let axisKinds = d.at("axisKinds")?.asObject ?? []
        for a in d.at("axes")?.asList ?? [] {
            let name = a.asText ?? ""
            holes.append((name, axisKinds.first(where: { $0.0 == name })?.1.asText))
        }
        for (axis, kind) in holes { block.append("    \(axis) asks for \(kind ?? "anything")") }
        for e in d.at("entries")?.asList ?? [] {
            let args = (e.at("args")?.asList ?? []).compactMap { $0.asText }
            block.append("    " + (e.at("head")?.asText ?? "")
                         + (args.isEmpty ? "" : "<" + args.joined(separator: ", ") + ">"))
        }
        items.append((at, block))
    }
    for (name, a) in topAliases {
        if !only.isEmpty && !only.contains(name) { continue }
        let at = saidInt(a.at("line"))
        let note = bareNote(lines, at)
        items.append((at, (note.isEmpty ? [] : [note])
                      + ["\(name) = " + (a.at("target")?.asText ?? "")]))
    }
    if only.isEmpty {
        let heads = declarations.map { saidInt($0.at("line")) }
            + topAliases.map { saidInt($0.1.at("line")) }
        for c in bareComments(lines, heads) {
            items.append((c.line, c.kind == "head" ? ["── " + c.text + " ──"]
                          : c.kind == "set" ? c.text.components(separatedBy: "\n")
                          : [c.text]))
        }
    }
    items.sort { $0.0 < $1.0 }
    var out: [String] = []
    for (_, block) in items {
        if !out.isEmpty { out.append("") }
        out += block
    }
    return out
}

// ── THE ACT OF ENTRY, all four heads. Everything this tool judges is on this
// side of it: a pair of catalogue tables, a repository's own CODEOWNERS, the
// citations code makes to a tracker, and a cluster's roles and bindings. Each
// prints a world in the shipped forms and asks the court about it; none of them
// leaves a file behind unless asked by name with `-o`.
let REFS_HEADER = """
    // printed by gate import refs: the citations this code makes to a tracker,
    // written in the reference vocabulary (`gate stdlib show forms-reference`). A
    // tracked thing carries its state on an axis, a site is a place in your own
    // file, and a citation holds only while the thing it cites is open.
    //

    """.replacingOccurrences(of: "\n    ", with: "\n")

let RBAC_FORMS_HEADER = """
    // printed by gate import rbac: the K8s access world in the domain forms
    // (the exemplar: theory corpus Sources/Examples/Grants.swift @ 0fd0b38).
    // Realms are namespaces plus the cluster scope. A role is a room stating its
    // realm, a binding is a keeper stating its post, and the gate's equality is the
    // K8s invariant itself: a RoleBinding and its Role live in one namespace.
    // The forms below are the stdlib module forms-grants, printed from the shelf.


    """.replacingOccurrences(of: "\n    ", with: "\n")


func theirsJson(_ path: String, _ what: String) -> Said {
    let text = theirsText(path, what)
    guard let said = readSaid(text) else {
        cannot(path + " is not the json this reads", "point it at " + what)
    }
    return said
}

// a tracker export, in the shape every tracker can produce: a list of
// {key, status}. What counts as open is the tracker's word, not ours: anything
// it does not call done or closed is still open.
func readTracker(_ path: String) -> [(key: String, state: String)] {
    let raw = theirsJson(path, "a tracker export: a list of {key, status}")
    let items = raw.at("issues")?.asList ?? raw.asList ?? []
    var out: [(key: String, state: String)] = []
    for it in items {
        let key = (it.at("key")?.asText ?? it.at("id")?.asText ?? "")
            .trimmingCharacters(in: .whitespaces)
        if key.isEmpty { continue }
        let st = (it.at("status")?.asText ?? it.at("state")?.asText ?? "")
            .trimmingCharacters(in: .whitespaces).lowercased()
        let state = ["done", "closed", "resolved", "completed"].contains(st) ? "Closed" : "Open"
        if let i = out.firstIndex(where: { $0.key == key }) { out[i] = (key, state) }
        else { out.append((key, state)) }
    }
    return out
}

// every place the code names a ticket: TODO(KEY), FIXME(KEY), or a bare mention
// in a comment. The address is the reader's own file and line.
func readCitations(_ root: String) -> [(file: String, line: Int, key: String)] {
    var hits: [(file: String, line: Int, key: String)] = []
    let skip: Set<String> = [".git", "node_modules", "__pycache__", ".venv"]
    let kinds: Set<String> = ["py", "ts", "js", "rs", "go", "rb", "java", "swift", "md"]
    guard let walk = FileManager.default.enumerator(atPath: root) else { return hits }
    var found: [String] = []
    for case let rel as String in walk {
        if rel.components(separatedBy: "/").contains(where: { skip.contains($0) }) {
            walk.skipDescendants()
            continue
        }
        if kinds.contains((rel as NSString).pathExtension) { found.append(rel) }
    }
    // the other carrier walks with os.walk, whose order is the directory's own;
    // sorted here so two machines read one order, and the answer is a set anyway
    for rel in found.sorted() {
        let p = (root as NSString).appendingPathComponent(rel)
        guard let text = readText(p) else { continue }
        for (n, line) in text.components(separatedBy: "\n").enumerated() {
            for m in matches("\\b(?:TODO|FIXME|HACK|XXX)\\s*[(\\[:]?\\s*([A-Z][A-Z0-9]+-\\d+)",
                             line) {
                hits.append((rel, n + 1, m[0]))
            }
        }
    }
    return hits
}

// the two catalogue tables, printed as a world and judged: the emitter is the
// bootstrap's, so the seed and the verb write one text
func importWorld(_ peoplePath: String, _ grantsPath: String, _ outPath: String)
    -> (verdict: String, refusals: [(address: String, claim: String)], people: Int,
        grants: Int, judgeMs: String?, wallMs: Double) {
    let world = seededWorld(peoplePath, grantsPath)
    oursWrite(outPath, "the world this reads", world)
    let t0 = Date()
    let said = courtSays([outPath])
    let wallMs = ((Date().timeIntervalSince(t0) * 1000 * 10).rounded(.toNearestOrEven)) / 10
    let refusals = refineAddresses(world, judgedRefusals(said),
                                   (outPath as NSString).lastPathComponent)
    let people = csvTable(peoplePath, "the people this world is seeded from").rows.count
    let grants = csvTable(grantsPath, "the grants this world is seeded from").rows.count
    return (said.contains("THE JUDGE holds") && refusals.isEmpty ? "holds" : "refused",
            refusals, people, grants,
            matches("([\\d.]+) ms", said).compactMap { $0.first }.last, wallMs)
}

// ── ONE ROOT FOR EVERY TEMPORARY PLACE. Three verbs used to spell their own
// scratch out of NSTemporaryDirectory plus string glue, which is three private
// doors to one fact: where this machine keeps what nobody keeps. The rim's law
// is closure: every impure reach goes through a named door, and the battery
// counts the raw token to hold the set closed.
func tempRoot() -> String {
    return NSTemporaryDirectory()
}

func scratchDir(_ tag: String) -> String {
    let d = tempRoot() + "/" + tag + "\(ProcessInfo.processInfo.processIdentifier)-\(scratchCount)"
    scratchCount += 1
    try? FileManager.default.createDirectory(atPath: d, withIntermediateDirectories: true)
    return d
}

// ── verify people.csv grants.csv [--against CMD]: the differential rule check.
// Catalogue seeds are judged by the world AND by the checker the client has
// today; a verdict split is the address of an untranslated rule.
struct Seed { var name = ""; var people: [[String: String]] = []
              var grants: [[String: String]] = [] }

func csvDicts(_ table: CsvTable) -> [[String: String]] {
    (0..<table.rows.count).map { r in
        var row: [String: String] = [:]
        for k in table.header { row[k] = table.at(r, k) ?? "" }
        return row
    }
}

func seedCatalogue(_ people: [[String: String]], _ grants: [[String: String]]) -> [Seed] {
    // the seed catalogue: one violation per rule form, drawn from the data
    // itself, so a table with no rows is a sentence rather than an index
    guard let p0 = people.first, let g0 = grants.first else {
        cannot("the tables this reads have no rows: a seed is drawn from the data itself",
               "point it at the two CSVs you imported, people and grants, with their "
               + "header lines")
    }
    guard let otherHome = people.first(where: { $0["home"] != p0["home"] })?["home"] else {
        cannot("every row of this table keeps one home: a seed is drawn from the data itself",
               "point it at the two CSVs you imported, people and grants, with their "
               + "header lines")
    }
    var moved = people
    moved[0]["home"] = otherHome
    return [
        Seed(name: "cross-view", people: people,
             grants: grants + [["who": p0["id"] ?? "", "doc": otherHome + "Share"]]),
        Seed(name: "duplicate-grant", people: people, grants: grants + [g0]),
        Seed(name: "dangling-who", people: people,
             grants: grants + [["who": "Emp9999", "doc": (p0["home"] ?? "") + "Share"]]),
        Seed(name: "dangling-doc", people: people,
             grants: grants + [["who": p0["id"] ?? "", "doc": "NoSuchShare"]]),
        Seed(name: "stale-after-transfer", people: moved, grants: grants),
    ]
}

func verifySeeds(_ peoplePath: String, _ grantsPath: String, _ against: String?)
    -> (dirty: Bool, worldSays: [String], legacySays: [String],
        rows: [(seed: String, world: String, worldSays: [String], legacy: String,
                legacySays: [String], reading: String)]) {
    let people = csvDicts(csvTable(peoplePath, "the people this reads"))
    let grants = csvDicts(csvTable(grantsPath, "the grants this reads"))
    let d = scratchDir("gate-verify-")
    defer { try? FileManager.default.removeItem(atPath: d) }
    // step 0: the base must be clean on BOTH sides, or a background violation
    // masks the seeds and `covered` would mean nothing
    let base = importWorld(peoplePath, grantsPath, (d as NSString)
        .appendingPathComponent("base.swift"))
    var legacyBase: (code: Int32, said: String)? = nil
    if let against = against { legacyBase = runSaid(against, [peoplePath, grantsPath]) }
    if base.verdict != "holds" || (legacyBase.map { $0.code != 0 } ?? false) {
        return (true, base.refusals.map { $0.claim + " · " + $0.address },
                legacyBase.map { $0.said.split(separator: "\n").map(String.init) } ?? [], [])
    }
    let columns = ["id", "rank", "home", "given", "family", "born", "site", "sex"]
    var rows: [(seed: String, world: String, worldSays: [String], legacy: String,
                legacySays: [String], reading: String)] = []
    for seed in seedCatalogue(people, grants) {
        let pp = (d as NSString).appendingPathComponent("people.csv")
        let gp = (d as NSString).appendingPathComponent("grants.csv")
        var pText = columns.joined(separator: ",") + "\n"
        for p in seed.people { pText += columns.map { p[$0] ?? "" }.joined(separator: ",") + "\n" }
        var gText = "who,doc\n"
        for g in seed.grants { gText += "\(g["who"] ?? ""),\(g["doc"] ?? "")\n" }
        try? pText.write(toFile: pp, atomically: false, encoding: .utf8)
        try? gText.write(toFile: gp, atomically: false, encoding: .utf8)
        let world = importWorld(pp, gp, (d as NSString).appendingPathComponent("gate.swift"))
        var legacy = "n/a", legacySays: [String] = [], reading = ""
        if let against = against {
            let said = runSaid(against, [pp, gp])
            legacy = said.code != 0 ? "refused" : "holds"
            reading = world.verdict == "refused"
                ? (legacy == "refused" ? "covered: both refuse"
                                       : "WORLD STRICTER: the client's checker misses this")
                : (legacy == "refused"
                   ? "NOT TRANSLATED: the legacy rule has no gate in the world"
                   : "weak seed: neither side refuses")
            legacySays = Array(said.said.split(separator: "\n").map(String.init).prefix(2))
        } else {
            // --self: seeds against the world alone, which rules hold at all
            reading = world.verdict == "refused" ? "held by the world" : "NO GATE HOLDS THIS SEED"
        }
        rows.append((seed.name, world.verdict, Array(world.refusals.map { $0.claim }.prefix(2)),
                     legacy, legacySays, reading))
    }
    return (false, [], [], rows)
}

func runSaid(_ command: String, _ arguments: [String]) -> (code: Int32, said: String) {
    let words = command.split(separator: " ").map(String.init) + arguments
    guard let first = words.first else { return (0, "") }
    let p = Process()
    // the command is the operator's own word, so the tool it names is found the
    // same way a shell would find it rather than assumed to sit at one path
    p.executableURL = URL(fileURLWithPath: toolPath(first))
    p.arguments = Array(words.dropFirst())
    let pipe = Pipe(), quiet = Pipe()
    p.standardOutput = pipe
    p.standardError = quiet
    do { try p.run() } catch { return (127, "") }
    let said = String(data: pipe.fileHandleForReading.readDataToEndOfFile(),
                      encoding: .utf8) ?? ""
    quiet.fileHandleForReading.readDataToEndOfFile()
    waitDone(p)
    return (p.terminationStatus, said.trimmingCharacters(in: .whitespacesAndNewlines))
}

// one file, judged, with the addresses refined the way every caller wants them
func judgeFile(_ path: String) -> (verdict: String, refusals: [(address: String, claim: String)],
                                   judgeMs: String?, wallMs: Double) {
    let t0 = Date()
    let said = courtSays([path])
    let wallMs = ((Date().timeIntervalSince(t0) * 1000 * 10).rounded(.toNearestOrEven)) / 10
    let refusals = refineAddresses(readText(path) ?? "", judgedRefusals(said),
                                   (path as NSString).lastPathComponent)
    return (said.contains("THE JUDGE holds") ? "holds" : "refused", refusals,
            matches("([\\d.]+) ms", said).compactMap { $0.first }.last, wallMs)
}

// insert a new entry after the LAST entry of the same form: a probe writes
// beside an existing entry, in the world's own hand
// ── AND THE REFUSAL IS THROWN, NOT EXITED. Both writers below are read by two
// surfaces now: the terminal, which prints a refusal and leaves, and the bench,
// which must answer the request and stay up. `cannot` ends the process, so a
// question the bench could not satisfy would have shut the server on the person
// asking it. The refusal travels as a value, and each surface ends it its way.
struct CannotSay: Error {
    let note: String
    let next: String
}

func lastEntryInsert(_ text: String, _ head: String, _ first: String, _ second: String,
                     _ indent: Int, anchoredOn: String? = nil) throws -> String {
    let ns = text as NSString
    guard let re = try? NSRegularExpression(pattern: head + "<\\s*(\\w+),\\s*(\\w+)\\s*>\\.self;?")
    else { return text }
    var hits = re.matches(in: text, range: NSRange(location: 0, length: ns.length))
    // an anchor may be asked to share the second axis: a rank entry lands
    // beside the entries of that rank, not beside whatever came last
    if let axis = anchoredOn {
        hits = hits.filter { ns.substring(with: $0.range(at: 2)) == axis }
    }
    guard let m = hits.last else {
        throw CannotSay(note: "no \(head) entries to anchor on",
                        next: "this change writes beside an existing entry, and the world has none")
    }
    let pad = String(repeating: " ", count: indent)
    let inner = String(repeating: " ", count: indent + 4)
    let entry = "\n\(pad)\(head)<\n\(inner)\(first),\n\(inner)\(second)\n\(pad)>.self"
    let at = m.range.location + m.range.length
    return ns.substring(to: at) + entry + ns.substring(from: at)
}

func withTemp(_ text: String, _ name: String) -> String {
    // the probe carries the real world's filename, so addresses read as native
    let d = scratchDir("gate-")
    let p = (d as NSString).appendingPathComponent(name)
    try? text.write(toFile: p, atomically: false, encoding: .utf8)
    return p
}

func lockLine(_ path: String, _ name: String) -> Int {
    guard let text = readText(path) else { return 1 }
    for spelling in ["\"node_modules/\(name)\"", "\"\(name)\""] {
        if let r = text.range(of: spelling) {
            return text[text.startIndex..<r.lowerBound].components(separatedBy: "\n").count
        }
    }
    return 1
}

// ── THE TWO DECLARATIONS, TAKEN APART: what the contract stated, what the
// carrier claimed, and whose name is on the claims. One reading, so the verb
// that judges a pair and the verb that asks what waits on a word see one thing.
struct SeamSides {
    var stated: [(route: String, field: String)] = []
    var claims: [(cert: String, route: String, field: String, mine: String)] = []
    var carrier = "that library"
}

func seamRead(_ left: String, _ right: String) -> SeamSides {
    var said = SeamSides()
    for m in matches("^// (\\S+) · (\\S+)$", left, lines: true) {
        if !said.stated.contains(where: { $0.route == m[0] && $0.field == m[1] }) {
            said.stated.append((m[0], m[1]))
        }
    }
    for m in matches("^// (\\S+) · (\\S+)(?: \\(it calls it (\\S+)\\))?\\npublic typealias (Carry_\\d+)",
                     right, lines: true) {
        said.claims.append((m[3], m[0], m[1], m[2]))
    }
    if let who = matches("public enum (\\w+): Carrier", right).first?.first { said.carrier = who }
    return said
}

// which seams are mine is mine to say: the layout declares them, and each file
// says in its own first lines which side it is
func declaredSeamFiles(_ base: String) -> [String] {
    let (rows, manifest) = layoutRowsFull(base)
    guard manifest != nil else { return [] }
    return rows.filter { $0.role == "seam" }
        .map { (base as NSString).appendingPathComponent($0.path) }
}

// an anchor the world states a different number of times than the change
// expects is a sentence, never a silent rewrite of the wrong place
func mustSub(_ text: String, _ pattern: String, _ repl: String, _ what: String) throws -> String {
    let ns = text as NSString
    guard let re = try? NSRegularExpression(pattern: pattern,
                                            options: [.dotMatchesLineSeparators]) else {
        return text
    }
    let hits = re.matches(in: text, range: NSRange(location: 0, length: ns.length))
    if hits.count != 1 {
        throw CannotSay(note: "\(what): anchor x\(hits.count), want 1",
                        next: "the world says this a different number of times than the "
                            + "change expects")
    }
    return re.stringByReplacingMatches(in: text, range: NSRange(location: 0, length: ns.length),
                                       withTemplate: repl)
}

// the mechanics of a transfer: Home in the roster and the team entry, both
// facts. View grants are NOT touched: re-pointing or revoking access is a
// decision of intent, left to the human.
func transferText(_ text: String, _ who: String, _ dept: String) throws -> String {
    var said = try mustSub(text,
                       "(public enum \(who): Employee, Person \\{[^}]*?public typealias Home = )\\w+",
                       "$1" + dept, "roster entry of " + who)
    let ns = said as NSString
    if let re = try? NSRegularExpression(pattern: "(VerifiedInDepartment<\\s*\(who),\\s*)\\w+") {
        said = re.stringByReplacingMatches(in: said,
                                           range: NSRange(location: 0, length: ns.length),
                                           withTemplate: "$1" + dept)
    }
    return said
}

func grantText(_ text: String, _ who: String, _ doc: String) throws -> String {
    try lastEntryInsert(text, "VerifiedView", who, doc, 12)
}

func revokeText(_ text: String, _ who: String, _ doc: String) throws -> String {
    let pattern = "\\n\\s*VerifiedView<\\s*\(who),\\s*\(doc)\\s*>\\.self;?"
    let ns = text as NSString
    guard let re = try? NSRegularExpression(pattern: pattern) else { return text }
    let hits = re.matches(in: text, range: NSRange(location: 0, length: ns.length))
    if hits.count != 1 {
        throw CannotSay(note: "revoke: grant \(who)->\(doc) found x\(hits.count), want 1",
                        next: "revoke removes one grant, and the world states that one a "
                            + "different number of times")
    }
    return ns.replacingCharacters(in: hits[0].range, with: "")
}

func hireText(_ text: String, _ f: [String: String]) throws -> String {
    func said(_ k: String) -> String { f[k] ?? "" }
    let block = "\n\npublic enum \(said("id")): Employee, Person {\n"
        + "    public typealias Rank = \(said("rank"))\n"
        + "    public typealias Home = \(said("home"))\n"
        + "    public typealias Given = \(said("given"))\n"
        + "    public typealias Family = \(said("family"))\n"
        + "    public typealias Born = \(said("born"))\n"
        + "    public typealias Site = \(said("site"))\n"
        + "    public typealias Sex = Given.Sex\n}"
    let ns = text as NSString
    guard let roster = try? NSRegularExpression(pattern: "public enum \\w+: Employee, Person \\{.*?\\n\\}",
                                                options: [.dotMatchesLineSeparators]),
          let last = roster.matches(in: text,
                                    range: NSRange(location: 0, length: ns.length)).last else {
        cannot("hire: no roster entries to anchor on",
               "hire writes beside an existing person, and the world has none")
    }
    let at = last.range.location + last.range.length
    var out = ns.substring(to: at) + block + ns.substring(from: at)
    // the corpus world carries a Company list; an imported one does not, and the
    // judge needs none
    let outNs = out as NSString
    if let slice = try? NSRegularExpression(pattern: "(Emp\\w+\\.self;?)(?=\\s*\\n\\s*\\})"),
       let s = slice.matches(in: out, range: NSRange(location: 0, length: outNs.length)).first {
        let end = s.range.location + s.range.length
        out = outNs.substring(to: end) + " \(said("id")).self;" + outNs.substring(from: end)
    }
    out = try lastEntryInsert(out, "VerifiedView", said("id"), said("home") + "Share", 12)
    out = try lastEntryInsert(out, "VerifiedInDepartment", said("id"), said("home"), 8,
                              anchoredOn: said("home"))
    out = try lastEntryInsert(out, "VerifiedAtRank", said("id"), said("rank"), 8,
                              anchoredOn: said("rank"))
    out = try lastEntryInsert(out, "VerifiedAtWorkplace", said("id"), said("site"), 8,
                              anchoredOn: said("site"))
    return out
}

// ── AN ANSWER, BEFORE ANYBODY SAYS IT. Two surfaces ask these questions: the
// terminal prints the answer and exits, the bench answers a request with it and
// stays up. So the asking hands back what it found, and each surface says it in
// its own way. The refusal travels the same road for the same reason: a `cannot`
// that exits the process would take the bench down with the first incomplete
// request, where the other carrier answers `{"error": …, "next": …}` and lives.
enum Answered {
    case said([(String, StatusJSON)])
    case cannot(note: String, next: String?)
}

// reading a field back out of an assembled answer: the human line is printed
// from the same pairs the object is printed from, so the two cannot drift
func textIn(_ pairs: [(String, StatusJSON)], _ key: String) -> String? {
    if case .text(let s)? = pairs.first(where: { $0.0 == key })?.1 { return s }
    return nil
}

func rawIn(_ pairs: [(String, StatusJSON)], _ key: String) -> String? {
    if case .raw(let r)? = pairs.first(where: { $0.0 == key })?.1 { return r }
    return nil
}

func rowsIn(_ pairs: [(String, StatusJSON)], _ key: String) -> [[(String, StatusJSON)]] {
    guard case .list(let items)? = pairs.first(where: { $0.0 == key })?.1 else { return [] }
    return items.compactMap { if case .object(let o) = $0 { return o }; return nil }
}

func refusalLines(_ pairs: [(String, StatusJSON)]) -> [String] {
    return rowsIn(pairs, "refusals").map {
        "  \(textIn($0, "address") ?? "") · \(textIn($0, "claim") ?? "")"
    }
}

// the question of one entry: a probe written beside the world's own entries and
// judged, with nothing changed
func askViewAnswer(_ w: WorldState, _ who: String, _ doc: String) -> Answered {
    // ── AND A QUESTION OF A WORLD FILE NEEDS ONE, said where the reading is: a
    // world declared as a layout alone has no facts file, and this read it
    // unguarded, so the terminal met a FileNotFoundError and the bench dropped
    // the line with no answer at all.
    guard let facts = w.facts, FileManager.default.fileExists(atPath: facts) else {
        return .cannot(
            note: "this asks its question of a world file, and there is none here",
            next: "run `gate init .` to start one, or `gate demo` for a repository to look "
                + "at. A world declared as a layout alone is judged by `gate status`")
    }
    guard let probe = try? lastEntryInsert(readText(facts) ?? "", "VerifiedView", who, doc, 12)
    else {
        return .cannot(note: "no VerifiedView entries to anchor on",
                       next: "this change writes beside an existing entry, and the world has none")
    }
    let said = judgeFile(withTemp(probe, (facts as NSString).lastPathComponent))
    return .said([
        ("command", .text("ask view")), ("who", .text(who)), ("doc", .text(doc)),
        ("verdict", .text(said.verdict)),
        ("refusals", .list(said.refusals.map {
            .object([("address", .text($0.address)), ("claim", .text($0.claim))]) })),
        ("judge_ms", said.judgeMs.map { .raw(floatRepr($0)) } ?? .null),
        ("wall_ms", .raw(String(said.wallMs))),
        ("mutates", .raw("false")),
    ])
}

// ── check view WHO DOC · check administer|delete WHO DOC. A question about one
// entry: a probe is written beside the world's own entries and judged, and
// nothing changes. `ask` is the same question spelled the other way, so it
// travels with the verb.
if args.first == "check" || args.first == "ask" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    loadStatusShelf()
    let w = discoverWorld()
    func asked(_ note: String, _ next: String) -> Never {
        if asJson {
            out("{\n  \"command\": \"check\",\n  \"asks\": true,\n"
                + "  \"note\": " + jsonString(note) + ",\n"
                + "  \"next\": " + jsonString(next) + "\n}\n")
        } else {
            out("usage: " + note + "\n  next: " + next + "\n")
        }
        exit(0)
    }
    if rest.isEmpty {
        asked("check view WHO WHAT  ·  check administer WHO WHERE  ·  check delete WHO WHAT",
              "gate check view Emp0042 FinanceShare, with names your world declares "
              + "(`gate library` lists that vocabulary)")
    }
    let kind = rest[0]
    let tail = Array(rest.dropFirst())
    if kind == "view" {
        let asks = "gate check view Emp0042 FinanceShare, with names your world declares "
                 + "(`gate library` lists that vocabulary)"
        if tail.isEmpty {
            asked("check view WHO WHAT  ·  a question about one entry, and nothing changes",
                  asks)
        }
        if tail.count < 2 { cannot("check view WHO WHAT: this names only " + tail[0], asks) }
        let answered = askViewAnswer(w, tail[0], tail[1])
        guard case .said(let pairs) = answered else {
            if case .cannot(let note, let next) = answered { cannot(note, next ?? "") }
            exit(1)
        }
        let verdict = textIn(pairs, "verdict") ?? ""
        if asJson {
            out(statusDumps(.object(pairs), 0) + "\n")
        } else {
            var lines = ["ask view: "
                         + (verdict == "holds" ? "holds"
                            : "refused \(rowsIn(pairs, "refusals").count)")
                         + ((rawIn(pairs, "judge_ms").flatMap { $0 == "null" ? nil : $0 })
                            .map { " · " + $0 + " ms" } ?? "")]
            lines += refusalLines(pairs)
            out(lines.joined(separator: "\n") + "\n")
        }
        exit(verdict == "holds" ? 0 : 1)
    }
    if kind == "administer" || kind == "delete" {
        // the compiler gates: a probe entry in the corpus's own accesses and a
        // swift build. Seconds, and the full arbiter.
        guard let root = ProcessInfo.processInfo.environment["GATE_CORPUS"], !root.isEmpty else {
            cannot("check " + kind + " needs GATE_CORPUS (a checkout of the theory corpus "
                   + "with Team.swift)",
                   "set GATE_CORPUS to that checkout, or ask `gate check view` instead, "
                   + "which needs none")
        }
        let asks = "gate check \(kind) Emp0042 FinanceVault, with names your world declares "
                 + "(`gate library` lists that vocabulary)"
        if tail.isEmpty {
            asked("check \(kind) WHO WHAT  ·  the compiler is the arbiter, and it takes seconds",
                  asks)
        }
        if tail.count < 2 { cannot("check \(kind) WHO WHAT: this names only " + tail[0], asks) }
        let team = (((root as NSString).appendingPathComponent("Sources") as NSString)
            .appendingPathComponent("Organization") as NSString)
            .appendingPathComponent("System/Team.swift")
        let text = readText(team) ?? ""
        let anchor = "        Granted<Delete<Alice, FinanceVault>>.self         "
                   + "// only the owner, and only at manager rank, deletes"
        // the other carrier asserts this, which is a stack trace; a sentence
        // says the same thing to a person who can act on it
        if text.components(separatedBy: anchor).count - 1 != 1 {
            cannot("the corpus checkout at GATE_CORPUS does not carry the line this probe "
                   + "writes beside",
                   "point GATE_CORPUS at a checkout whose Team.swift still states the "
                   + "delete example, or ask `gate check view` instead")
        }
        let gateName = kind.prefix(1).uppercased() + kind.dropFirst()
        let probe = text.replacingOccurrences(
            of: anchor,
            with: anchor + "\n        Granted<\(gateName)<\(tail[0]), \(tail[1])>>.self // gate probe")
        try? probe.write(toFile: team, atomically: false, encoding: .utf8)
        let t0 = Date()
        let built = runSaid("swift build", [])
        let secs = (Date().timeIntervalSince(t0) * 100).rounded() / 100
        _ = runGit(["checkout", "--", team], root)
        var reasons = Set<String>()
        for m in matches("error: (.+)$", built.said, lines: true) { reasons.insert(m[0]) }
        let says = Array(reasons.sorted().prefix(3))
        let verdict = built.code == 0 ? "holds" : "refused"
        if asJson {
            out(statusDumps(.object([
                ("command", .text("ask \(kind)")), ("who", .text(tail[0])),
                ("doc", .text(tail[1])), ("verdict", .text(verdict)),
                ("compiler_says", .list(says.map { .text($0) })),
                ("build_s", .raw(String(secs))),
                ("mutates", .raw("false")),
            ]), 0) + "\n")
        } else {
            var lines = ["ask \(kind): " + (verdict == "holds" ? "holds" : "refused 0")
                         + " · build \(secs) s"]
            for s in says { lines.append("  compiler: " + s) }
            out(lines.joined(separator: "\n") + "\n")
        }
        exit(verdict == "holds" ? 0 : 1)
    }
    asked("check view WHO WHAT  ·  check administer WHO WHERE  ·  check delete WHO WHAT",
          "gate check view Emp0042 FinanceShare, with names your world declares "
          + "(`gate library` lists that vocabulary)")
}

// ── diff transfer WHO DEPT · diff hire … · apply the same words. The SINGLE
// source, the world, is edited, and the diff stays a Swift git diff. `change` is
// the third spelling of one act and travels with the two doors.
// the change itself, assembled once for both surfaces: what the world would say
// after the edit, and whether the edit was written. `apply` is the same act as
// `diff` with the bytes kept, which is why one reading answers both.
func changeAnswer(_ w: WorldState, _ facts: String, _ rest: [String],
                  applyIt: Bool) -> Answered {
    let text = readText(facts) ?? ""
    var label: [(String, StatusJSON)] = []
    var made = ""
    switch rest[0] {
    case "transfer":
        guard rest.count > 2 else {
            return .cannot(note: "change transfer WHO DEPT: this names too little",
                           next: "name the person and the department")
        }
        do { made = try transferText(text, rest[1], rest[2]) }
        catch let e as CannotSay { return .cannot(note: e.note, next: e.next) }
        catch { return .cannot(note: "this change could not be written", next: nil) }
        label = [("command", .text("change transfer")), ("who", .text(rest[1])),
                 ("to", .text(rest[2])),
                 ("note", .text("roster and team entry moved. View grants are intent, so "
                                + "resolve leftovers with grant/revoke"))]
    case "grant":
        guard rest.count > 2 else {
            return .cannot(note: "change grant WHO DOC: this names too little",
                           next: "name the person and the document")
        }
        do { made = try grantText(text, rest[1], rest[2]) }
        catch let e as CannotSay { return .cannot(note: e.note, next: e.next) }
        catch { return .cannot(note: "this change could not be written", next: nil) }
        label = [("command", .text("change grant")), ("who", .text(rest[1])),
                 ("doc", .text(rest[2]))]
    case "revoke":
        guard rest.count > 2 else {
            return .cannot(note: "change revoke WHO DOC: this names too little",
                           next: "name the person and the document")
        }
        do { made = try revokeText(text, rest[1], rest[2]) }
        catch let e as CannotSay { return .cannot(note: e.note, next: e.next) }
        catch { return .cannot(note: "this change could not be written", next: nil) }
        label = [("command", .text("change revoke")), ("who", .text(rest[1])),
                 ("doc", .text(rest[2]))]
    case "hire":
        let keys = ["id", "rank", "home", "given", "family", "born", "site"]
        var f: [String: String] = [:]
        for (i, k) in keys.enumerated() where i + 1 < rest.count { f[k] = rest[i + 1] }
        do { made = try hireText(text, f) }
        catch let e as CannotSay { return .cannot(note: e.note, next: e.next) }
        catch { return .cannot(note: "this change could not be written", next: nil) }
        label = [("command", .text("change hire"))]
            + keys.compactMap { k in f[k].map { (k, StatusJSON.text($0)) } }
    default:
        return .cannot(note: "unknown change " + rest[0],
                       next: "the changes this verb makes are `transfer`, `hire`, `grant` "
                           + "and `revoke`")
    }
    let said = judgeFile(withTemp(made, (facts as NSString).lastPathComponent))
    // ── AND `applied` MEANS SOMETHING CHANGED. A transfer to the department
    // somebody is already in rewrites the file with the bytes it already had,
    // and this said `applied` while `git status` stayed empty.
    let moved = (readText(facts) ?? "") != made
    var applied = false
    if applyIt && said.verdict == "holds" && moved {
        oursWrite(facts, "the world this edits", made)
        applied = true
    }
    var pairs = label
    pairs.append(("verdict", .text(said.verdict)))
    pairs.append(("refusals", .list(said.refusals.map {
        .object([("address", .text($0.address)), ("claim", .text($0.claim))]) })))
    pairs.append(("judge_ms", said.judgeMs.map { .raw(floatRepr($0)) } ?? .null))
    pairs.append(("wall_ms", .raw(String(said.wallMs))))
    pairs.append(("dry_run", .raw(applyIt ? "false" : "true")))
    pairs.append(("applied", .raw(applied ? "true" : "false")))
    pairs.append(("changed", .raw(moved ? "true" : "false")))
    return .said(pairs)
}

if args.first == "diff" || args.first == "apply" || args.first == "change" {
    let applyIt = args.first == "apply" || args.contains("--apply")
    let rest = Array(args.dropFirst()).filter { $0 != "--json" && $0 != "--apply" }
    let asJson = args.contains("--json")
    loadStatusShelf()
    let w = discoverWorld()
    guard let facts = w.facts, FileManager.default.fileExists(atPath: facts) else {
        cannot("this asks its question of a world file, and there is none here",
               "run `gate init .` to start one, or `gate demo` for a repository to look "
               + "at. A world declared as a layout alone is judged by `gate status`")
    }
    if rest.isEmpty {
        let note = "diff transfer WHO DEPT  ·  diff hire ID RANK HOME GIVEN FAMILY "
                 + "BORN SITE  ·  the same words after `apply` write the change"
        let next = "gate diff transfer Emp0042 Sales shows what would move and what "
                 + "would stop holding, and writes nothing"
        if asJson {
            out("{\n  \"command\": \"change\",\n  \"asks\": true,\n"
                + "  \"note\": " + jsonString(note) + ",\n"
                + "  \"next\": " + jsonString(next) + "\n}\n")
        } else {
            out("usage: " + note + "\n  next: " + next + "\n")
        }
        exit(0)
    }
    let answered = changeAnswer(w, facts, rest, applyIt: applyIt)
    guard case .said(let pairs) = answered else {
        if case .cannot(let note, let next) = answered { cannot(note, next ?? "") }
        exit(1)
    }
    let label = pairs
    if asJson {
        out(statusDumps(.object(pairs), 0) + "\n")
    } else {
        let head = textIn(label, "command") ?? ""
        let verdict = textIn(pairs, "verdict") ?? ""
        let applied = rawIn(pairs, "applied") == "true"
        let moved = rawIn(pairs, "changed") == "true"
        var tail: [String] = []
        if let ms = rawIn(pairs, "judge_ms"), ms != "null" { tail.append(ms + " ms") }
        tail.append(applyIt ? (applied ? "applied"
                               : (!moved && verdict == "holds"
                                  ? "nothing to change: it already says this" : "NOT applied"))
                            : "dry-run")
        var lines = [head + ": "
                     + (verdict == "holds" ? "holds" : "refused \(rowsIn(pairs, "refusals").count)")
                     + " · " + tail.joined(separator: " · ")]
        lines += refusalLines(pairs)
        if let note = textIn(label, "note") { lines.append("  note: " + note) }
        out(lines.joined(separator: "\n") + "\n")
    }
    exit((textIn(pairs, "verdict") ?? "") == "holds" ? 0 : 1)
}

// the way a person will type it: relative where a relative path exists
func saidPath(_ p: String) -> String {
    let rel = relPath(absPath(p), FileManager.default.currentDirectoryPath)
    return rel.isEmpty ? p : rel
}

// this tool, asked of itself, in a folder it has just made. The demo is
// orchestration and nothing else: every world it builds is built by the verb
// that owns that act, so there is one translator here and not a second one
// wearing a demo's clothes.
var SELF_SAID_CODE: Int32 = 0

func selfSaid(_ words: [String], _ cwd: String) -> String {
    // ── AND A SPAWN THAT DOES NOT HAPPEN IS NOT AN EMPTY ANSWER. This caught
    // the failure to run and returned "", so `gate demo` on windows built the
    // whole world, never wrote the one file the world declares, exited nought
    // and said nothing: the manifest promised `ownership.swift` and the folder
    // held everything else. Refusal-as-value is this project's oldest law and
    // this was the one door still swallowing.
    //
    // ── AND THE FOLDER IT RUNS IN IS A PATH, NOT A URL. `URL(fileURLWithPath:)`
    // reads its argument the posix way wherever it runs, and what this verb
    // hands it is a world at a drive letter. The working directory decides
    // where `-o ownership.swift` lands, so it is set from the string this
    // vein's own door produced.
    let bin = absPath(CommandLine.arguments[0])
    mark("spawn:self " + (words.first ?? ""))
    let p = Process()
    p.executableURL = URL(fileURLWithPath: bin)
    p.arguments = words
    p.currentDirectoryPath = cwd
    let pipe = Pipe(), quiet = Pipe()
    p.standardOutput = pipe
    p.standardError = quiet
    do { try p.run() } catch {
        cannot("this tool could not run itself at " + bin + " in " + cwd
               + ": " + error.localizedDescription,
               "the binary is there and this is the same one that is speaking, "
               + "so what failed is the spawn: report this with the platform")
    }
    let said = pipe.fileHandleForReading.readDataToEndOfFile()
    let complained = quiet.fileHandleForReading.readDataToEndOfFile()
    waitDone(p)
    // ── AND THE CODE THE CHILD LEFT WITH IS KEPT. A child that printed on
    // neither channel says everything through this number and nothing without
    // it: on windows the import above answered nought characters on both, and
    // whether that is a crash, a kill or a clean exit is exactly what the code
    // is for.
    SELF_SAID_CODE = p.terminationStatus
    let answer = String(data: said, encoding: .utf8) ?? ""
    // ── AND A CHILD THAT COULD NOT ANSWER IS NOT A CHILD THAT HELD. A verb of
    // this tool refuses on its own channel: a refusal is an ANSWER, on stdout,
    // with a code beside it, and only a failure to answer at all goes to the
    // other one. This read the answer and threw that away, so a spawned verb
    // that could not write the file it was told to write left its parent
    // carrying on as though the world had been made. What is refused here is
    // silence and never a refusal: the demo's own import is meant to refuse,
    // and it does that in JSON like everything else.
    if answer.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty, !complained.isEmpty {
        let why = String(decoding: complained, as: UTF8.self)
            .components(separatedBy: "\n").first(where: { !$0.isEmpty }) ?? ""
        cannot("this tool ran itself and it could not answer: " + why,
               "the words above are its own, from `" + words.joined(separator: " ")
               + "` run in " + cwd)
    }
    return answer
}

let SEAM_DEMO_SPEC = """
    {
     "paths": {
      "/messages": {
       "post": {
        "parameters": [
         {
          "name": "sendAt",
          "in": "query",
          "schema": {
           "type": "string"
          }
         }
        ],
        "requestBody": {
         "content": {
          "application/json": {
           "schema": {
            "properties": {
             "to": {
              "type": "string"
             },
             "body": {
              "type": "string"
             },
             "attachments": {
              "type": "array"
             }
            }
           }
          }
         }
        }
       }
      }
     }
    }
    """

let SEAM_DEMO_SDK = """
    {
     "carrier": "MessagesJS",
     "against": {
      "contract": "openapi.json",
      "revision": "a1b2c3d"
     },
     "carries": [
      {
       "route": "/messages",
       "field": "to",
       "as": "Text"
      },
      {
       "route": "/messages",
       "field": "body",
       "as": "Text"
      },
      {
       "route": "/messages",
       "field": "sendAt",
       "as": "Count"
      },
      {
       "route": "/messages",
       "field": "replyTo",
       "as": "Text"
      }
     ]
    }
    """

let SEAM_DEMO_KNOWN = """
    {
     "diverges": [
      {
       "route": "/messages",
       "field": "sendAt",
       "because": "PROJ-42",
       "declared_by": "sdk-team"
      }
     ]
    }
    """

let SEAM_DEMO_TICKETS = """
    [
     {
      "key": "PROJ-42",
      "status": "In Progress"
     }
    ]
    """

let SEAM_DEMO_MANIFEST = """
    // what this folder took, and from where. A seam is not found by looking
    // at what is lying about: it is here because this side said so, at the
    // revision it was taken at. The columns are axes to declared atoms, and
    // the one string is the typeName literal. A revision is an atom too.
    public protocol Role {}
    public enum SeamFile: Role {}
    public protocol Theirs {}
    public enum Rev_messages_api {}
    extension Rev_messages_api { public static var typeName: String { "messages-api@a1b2c3d" } }
    public enum TheContract: Theirs {
        public typealias Kind = SeamFile
        public typealias At = Rev_messages_api
    }
    extension TheContract { public static var typeName: String { "api.swift" } }
    public enum Rev_messages_js {}
    extension Rev_messages_js { public static var typeName: String { "messages-js@4f10e22" } }
    public enum OurSide: Theirs {
        public typealias Kind = SeamFile
        public typealias At = Rev_messages_js
    }
    extension OurSide { public static var typeName: String { "sdk.swift" } }

    """

// ── demo [dir] · demo org [dir] · demo seam [dir]: three worlds to look at in
// thirty seconds, and nothing in any of them talks to a network. The first is
// who owns what, in a repository shaped like the reader's own; the second is
// people and grants, for a domain with no repository; the third is a contract
// and a client disagreeing. Every world here is built by the verb that owns
// that act, asked of this same tool: the demo orchestrates and translates
// nothing of its own.
if args.first == "demo" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    loadStatusShelf()
    func put(_ root: String, _ name: String, _ text: String) {
        let p = (root as NSString).appendingPathComponent(name)
        try? FileManager.default.createDirectory(
            atPath: (p as NSString).deletingLastPathComponent,
            withIntermediateDirectories: true)
        try? text.write(toFile: p, atomically: false, encoding: .utf8)
    }
    func commit(_ root: String, _ message: String, _ noVerify: Bool) {
        _ = runGit(["add", "-A"], root)
        var words = ["-c", "user.email=you@example.com", "-c", "user.name=You",
                     "-c", "commit.gpgsign=false", "commit", "-qm", message]
        if noVerify { words.append("--no-verify") }
        _ = runGit(words, root)
    }
    func answer(_ pairs: [(String, StatusJSON)], _ words: [String]) -> Never {
        if asJson {
            out(statusDumps(.object(pairs), 0) + "\n")
        } else {
            out(words.joined(separator: "\n") + "\n")
        }
        exit(0)
    }

    // ── demo seam
    if rest.first == "seam" {
        let root = absPath(rest.count > 1 ? rest[1] : "gate-seam-demo")
        if !FileManager.default.fileExists(atPath: root) { FOUNDED_HERE = root }
        try? FileManager.default.createDirectory(atPath: root, withIntermediateDirectories: true)
        put(root, "openapi.json", SEAM_DEMO_SPEC)
        put(root, "sdk.declared.json", SEAM_DEMO_SDK)
        put(root, "known.json", SEAM_DEMO_KNOWN)
        put(root, "tickets.json", SEAM_DEMO_TICKETS)
        put(root, "gate.manifest.swift", SEAM_DEMO_MANIFEST)
        func side(_ what: String, _ from: String, _ to: String) -> Int {
            let said = selfSaid(["declare", what, (root as NSString).appendingPathComponent(from),
                                 "-o", (root as NSString).appendingPathComponent(to), "--json"],
                                root)
            return saidInt(readSaid(said)?.at("declares"))
        }
        let api = side("contract", "openapi.json", "api.swift")
        let sdk = side("carrier", "sdk.declared.json", "sdk.swift")
        let att = attentionOver((root as NSString).appendingPathComponent("api.swift"),
                                (root as NSString).appendingPathComponent("sdk.swift"),
                                "MessagesJS", nil, nil)
        func said(_ row: [(String, StatusJSON)], _ key: String) -> String {
            if case .text(let v)? = row.first(where: { $0.0 == key })?.1 { return v }
            return ""
        }
        let waiting = att.waitsOnYou.map { said($0, "address") }
        let theirs = att.youWaitOn.map { said($0, "address") }
        let parted = att.parted.map { said($0, "address") + " · " + said($0, "why") }
        let next = "cd \(saidPath(root)) && gate attention api.swift sdk.swift --as MessagesJS"
        let tries = ["gate seam api.swift sdk.swift: the court over the pair, in ms",
                     "gate attention api.swift sdk.swift --as MessagesJS --known known.json "
                     + "--tracker tickets.json: the same, with one divergence declared",
                     "edit tickets.json: mark PROJ-42 done, and watch the exception come back",
                     "gate declare contract openapi.json  the emitter, on your own spec"]
        var words = ["demo seam: two sides in \(root): the contract states \(api), "
                     + "the library claims \(sdk)"]
        for x in waiting { words.append("  waits on the library · " + x) }
        for x in theirs { words.append("  waits on the contract · " + x) }
        for x in parted { words.append("  parted · " + x) }
        words.append("  next: " + next)
        // ONE RUNG: a reader thirty seconds in gets a step, and whoever asked
        // for the whole ladder reads it in `--json`
        words.append("  more: \(tries.count) other things to try; `--json` lists them")
        answer([("command", .text("demo seam")), ("root", .text(root)),
                ("declared", .object([("contract", .raw(String(api))),
                                      ("carrier", .raw(String(sdk)))])),
                ("waiting_on_you", .list(waiting.map { .text($0) })),
                ("you_wait_on", .list(theirs.map { .text($0) })),
                ("parted", .list(parted.map { .text($0) })),
                ("next", .text(next)), ("try", .list(tries.map { .text($0) })),
                ("mutates", .raw("true"))], words)
    }

    // ── demo org
    if rest.first == "org" {
        // the tool's own folder, asked for by name: the demo's `root` is the
        // world it is making, and the two are not the same place
        let mine = toolRoot()
        let root = absPath(rest.count > 1 ? rest[1] : "gate-demo")
        if !FileManager.default.fileExists(atPath: root) { FOUNDED_HERE = root }
        try? FileManager.default.createDirectory(
            atPath: (root as NSString).appendingPathComponent("tables"),
            withIntermediateDirectories: true)
        for f in ["people.csv", "grants.csv"] {
            let src = joinPath(mine, "demo/" + f)
            if FileManager.default.fileExists(atPath: src) {
                try? FileManager.default.removeItem(
                    atPath: (root as NSString).appendingPathComponent("tables/" + f))
                try? FileManager.default.copyItem(
                    atPath: src,
                    toPath: (root as NSString).appendingPathComponent("tables/" + f))
            }
        }
        var isDir: ObjCBool = false
        if !(FileManager.default.fileExists(atPath: (root as NSString)
            .appendingPathComponent(".git"), isDirectory: &isDir) && isDir.boolValue) {
            _ = runGit(["init", "-q", root], FileManager.default.currentDirectoryPath)
        }
        let world = (root as NSString).appendingPathComponent("gate.swift")
        _ = selfSaid(["import", (root as NSString).appendingPathComponent("tables/people.csv"),
                      (root as NSString).appendingPathComponent("tables/grants.csv"),
                      "-o", world, "--json"], root)
        // AND THE WORLD PRESENTS THE FORMS IT IS WRITTEN IN: organization was
        // only ever an example of what somebody might write, and it belongs
        // beside the world that speaks it, as a file the operator can change.
        var body = (STDLIB_TEXTS["forms-organization"] ?? "").components(separatedBy: "\n")
        while let first = body.first, first.hasPrefix("//") { body.removeFirst() }
        var forms = "// the forms this world is written in: an example of what you might\n"
                  + "// write, and yours from here: change a rank, add a department, and the\n"
                  + "// world beside it is judged by what you said rather than by anything\n"
                  + "// this tool was born knowing.\n"
        var joined = body.joined(separator: "\n")
        while joined.hasPrefix("\n") { joined.removeFirst() }
        forms += joined
        put(root, "forms-organization.swift", forms)
        _ = declareSideHere((root as NSString).appendingPathComponent("forms-organization.swift"),
                            "Mine", "forms", nil)
        // ── AND THE JUDGE'S OWN ROW, WRITTEN IN YOUR NAME. Nothing stands in
        // this world without a row, and this is that row for the court itself.
        if let came = judgeFrom() {
            let short = String(came.prefix(7))
            let mp = (root as NSString).appendingPathComponent("gate.manifest.swift")
            let head = readText(mp) ?? ""
            let row = "\n// taken at demo setup, in your name. Nothing stands in this world\n"
                    + "// without a row, and this is that row for the court itself. The\n"
                    + "// revision is the dependency, not any file. Yours to edit or drop.\n"
                    + "public protocol Theirs {}\n"
                    + "public enum JudgeFile: Role {}\n"
                    + "public enum Rev_vi_\(short) {}\n"
                    + "extension Rev_vi_\(short) { public static var typeName: String "
                    + "{ \"verification-is-identification@\(short)\" } }\n"
                    + "public enum TheJudge: Theirs {\n"
                    + "    public typealias Kind = JudgeFile\n"
                    + "    public typealias At = Rev_vi_\(short)\n"
                    + "}\n"
                    + "extension TheJudge { public static var typeName: String "
                    + "{ \"gate-judge\" } }\n"
            try? (head + row).write(toFile: mp, atomically: false, encoding: .utf8)
        }
        put(root, "gate.policy.swift",
            "// who someone is, and what an action demands: facts of yours,\n"
            + "// beside the world and yours to change.\n"
            + "public enum MailYou: Identity {\n    public typealias Person = Emp9000\n}\n"
            + "extension MailYou { public static var typeName: String { \"you@example.com\" } }\n\n"
            + "public enum MergePolicy {\n    public typealias Requires = Manager\n}\n")
        commit(root, "a world of people and grants", false)
        var shown: [String] = []
        let asked = readSaid(selfSaid(["check", "view", "Emp9001", "EngineeringShare", "--json"],
                                      root))
        for r in asked?.at("refusals")?.asList ?? [] {
            shown.append((r.at("address")?.asText ?? "") + " · " + (r.at("claim")?.asText ?? ""))
        }
        let next = "cd \(saidPath(root)) && gate serve: then change one Home in "
                 + "gate.swift and watch the judge name the line"
        let back = "git checkout .  everything as it was, in one word: this world was "
                 + "committed the moment it was made, so nothing you try here can cost you "
                 + "anything"
        let tries = ["gate status  the world holds, in milliseconds",
                     "gate apply revoke Emp9002 FinanceShare  an edit judged before it lands",
                     "open gate.swift and change one Home to Engineering, and the judge "
                     + "names the line"]
        var words = ["demo: a world in \(root)"]
        for s in shown {
            words.append("  asked `gate check view Emp9001 EngineeringShare` for you, "
                         + "and it answers:")
            words.append("    " + s)
        }
        words.append("  next: " + next)
        words.append("  back: " + back)
        words.append("  more: \(tries.count) other things to try; `--json` lists them")
        answer([("command", .text("demo")), ("root", .text(root)),
                ("asked", .text("gate check view Emp9001 EngineeringShare")),
                ("refused", .list(shown.map { .text($0) })),
                ("next", .text(next)), ("back", .text(back)),
                ("try", .list(tries.map { .text($0) })),
                ("mutates", .raw("true"))], words)
    }

    // ── demo: who owns what, in a repository shaped like the reader's own
    let root = absPath(rest.first ?? "gate-demo")
    if !FileManager.default.fileExists(atPath: root) { FOUNDED_HERE = root }
    for rel in ["src/api", "src/ui", "src/db", "docs"] {
        try? FileManager.default.createDirectory(
            atPath: (root as NSString).appendingPathComponent(rel),
            withIntermediateDirectories: true)
    }
    for rel in ["src/api/handler.ts", "src/ui/view.tsx", "src/db/schema.sql", "docs/readme.md"] {
        put(root, rel, "// a file of this repository\n")
    }
    put(root, "CODEOWNERS",
        "# who owns what, the way every repository already writes it\n"
        + "src/api/    @alice\nsrc/ui/     @bob\ndocs/       @carol\nsrc/db/     @carol\n")
    // WHO MAY OWN WHAT is the thing CODEOWNERS cannot say, and without it every
    // rule is its own authority: a file that answers only to itself
    put(root, "owners.csv", "owner,zone\nalice,src\nbob,src\ncarol,docs\n")
    _ = runGit(["init", "-q", "-b", "main", "."], root)
    _ = selfSaid(["init", "."], root)
    // ── AND WHAT THE CHILD IS TOLD IS WHERE, NOT HERE. These were relative and
    // the child resolved them against a working directory the parent set for
    // it. On windows that setting did not take: the verb ran, wrote the world's
    // one declared file somewhere else entirely, and this world was left
    // promising `ownership.swift` in a manifest with no such file beside it.
    // `gate demo` exited nought over it, and `gate status` then refused for a
    // file that was never written, naming a path that was right all along.
    // A path decided here travels whole, and no other process has to agree
    // with us about where "here" is.
    let said = readSaid(selfSaid(["import", "codeowners", joinPath(root, "CODEOWNERS"),
                                  "--tree", root,
                                  "--policy", joinPath(root, "owners.csv"),
                                  "-o", joinPath(root, "ownership.swift"), "--json"],
                                 root))
    // ── AND A WORLD IS NOT DECLARED BEFORE IT IS THERE. The import above is a
    // verb of this tool run as its own process, and on windows it answered and
    // left no file: this went on to write a row for `ownership.swift` into the
    // manifest, commit the lot, and exit nought, so the world shipped
    // PROMISING a file nobody had. What `gate status` then said about it was
    // true and unactionable, and six runs of a hunt went into the sentence
    // rather than into this line. A verb that cannot make the world it
    // promises refuses, and says what its own child answered.
    let ours = joinPath(root, "ownership.swift")
    guard FileManager.default.fileExists(atPath: ours) else {
        // ── AND WHAT THE CHILD SAID TRAVELS RAW. Quoting the PARSED verdict
        // here was quoting a reading: on the platform this fires on, the
        // answer does not parse, so the sentence said "nothing this could
        // read" and named neither what came back nor why. The first line of
        // what it actually printed is the thing nobody here can guess.
        let again = selfSaid(["import", "codeowners", joinPath(root, "CODEOWNERS"),
                              "--tree", root, "--json"], root)
        let firstLine = again.components(separatedBy: "\n")
            .first(where: { !$0.trimmingCharacters(in: .whitespaces).isEmpty }) ?? ""
        cannot("this demo could not write " + ours + ", and a world is not "
               + "declared before it is there. Its own import left with code "
               + String(SELF_SAID_CODE) + " and answered "
               + String(again.count) + " characters beginning `"
               + String(firstLine.prefix(60)) + "`",
               "the folder is at " + root + " and holds what it holds: this is "
               + "the tool failing to run itself, not your repository")
    }
    _ = declareSideHere(ours, "Mine", "forms", nil)
    // the world ships with its one refusal on purpose, so the commit walks past
    // the hook the kit just wired: the hook is for the reader's own commits
    commit(root, "who owns what in this repository", true)
    // the address in CODEOWNERS is what a person recognises, so it leads
    var shown: [String] = []
    for r in (said?.at("refusals")?.asList ?? []).prefix(2) {
        let where_ = r.at("source")?.asText ?? r.at("address")?.asText ?? ""
        var claim = r.at("claim")?.asText ?? ""
        if let m = matchAt(claim, "^\\w+ · ") { claim = String(claim.dropFirst(m[0].count)) }
        shown.append(where_ + " · " + claim)
    }
    let next = "cd \(saidPath(root)) && gate status, for the same answer in a "
             + "millisecond, from the world rather than from CODEOWNERS"
    let back = "git checkout . puts everything back, in one word: this world was "
             + "committed the moment it was made"
    let tries = ["open ownership.swift at the line gate status names, and give that room to "
                 + "an owner whose zone matches. The file and the world are a pair: status "
                 + "compares them on every run",
                 "or edit CODEOWNERS and run the import again: same command, one line moved",
                 "gate serve opens the bench, with the world beside its verdict, judged as "
                 + "you type",
                 "gate demo org is the same machinery on people and departments, "
                 + "for a domain that has no repository"]
    var words = ["demo: a world in \(root)"]
    for s in shown {
        words.append("  asked `gate import codeowners CODEOWNERS --tree . --policy owners.csv` "
                     + "for you, and it answers:")
        words.append("    " + s)
    }
    words.append("  next: " + next)
    words.append("  back: " + back)
    words.append("  more: \(tries.count) other things to try; `--json` lists them")
    answer([("command", .text("demo")), ("root", .text(root)),
            ("asked", .text("gate import codeowners CODEOWNERS --tree . --policy owners.csv")),
            ("refused", .list(shown.map { .text($0) })),
            ("next", .text(next)), ("back", .text(back)),
            ("try", .list(tries.map { .text($0) })),
            ("mutates", .raw("true"))], words)
}

// ── attention CONTRACT.swift CARRIER.swift: NOT what changed, but what waits
// for a word. History is diachronic and git keeps it; this is the other cut, the
// standing ledger of who owes whom a sentence. It is two-sided by construction:
// an unanswered address sits on the side that owes the answer.
//
// AND THE STATE OF EVERY ADDRESS IS |S|. A seam is the premise V=I §5.4 leaves
// outside itself, asked as a game one level up: |S| = 1 both spoke and agree,
// |S| = 0 both spoke and nothing passes, |S| > 1 one is silent. Three sizes,
// three columns, and no fourth can be written without inventing a fourth size.
struct AttentionSaid {
    var me = "", carrier = ""
    var sizes: [(String, Int)] = []
    var waitsOnYou: [[(String, StatusJSON)]] = []
    var youWaitOn: [[(String, StatusJSON)]] = []
    var parted: [[(String, StatusJSON)]] = []
    var known: [[(String, StatusJSON)]] = []
    var expired: [[(String, StatusJSON)]] = []
    var stated = 0, claimed = 0
    var note = "", next = ""
}

func attentionOver(_ leftPath: String, _ rightPath: String, _ asWho: String?,
                   _ knownPath: String?, _ trackerPath: String?) -> AttentionSaid {
    let left = theirsText(leftPath, "the contract side of the pair")
    let right = theirsText(rightPath, "the carrier side of the pair")
    let sides = seamRead(left, right)
    let me = asWho ?? sides.carrier
    let known = knownPath.map { theirsJson($0, "the divergences you declared") }
    let tracker = trackerPath.map { readTracker($0) } ?? []
    let d = scratchDir("gate-att-")
    let path = (d as NSString).appendingPathComponent("seam.swift")
    try? (left + "\n" + right).write(toFile: path, atomically: false, encoding: .utf8)
    let outp = courtSays(["where", path])
    try? FileManager.default.removeItem(atPath: d)
    let statedKeys = Set(sides.stated.map { $0.route + "\u{1}" + $0.field })
    let claimedKeys = Set(sides.claims.map { $0.route + "\u{1}" + $0.field })
    var parted: [String: (want: String, got: String, mine: String)] = [:]
    for m in matches("^✗ '(\\w+)[^']*' requires the types '[^']*' \\(aka '([^']+)'\\) and "
                     + "'[^']*' \\(aka '([^']+)'\\)", outp, lines: true) {
        let it = sides.claims.first(where: { $0.cert == m[0] })
        let route = it?.route ?? "?", field = it?.field ?? m[0]
        // a claim about something the contract never stated is not a
        // DISAGREEMENT: there is nothing to disagree with, and it belongs in
        // the other column entirely
        if statedKeys.contains(route + "\u{1}" + field) {
            parted[route + "\u{1}" + field] = (m[1].lowercased(), m[2].lowercased(),
                                               it?.mine ?? "")
        }
    }
    let addresses = statedKeys.union(claimedKeys).sorted()
    var said = AttentionSaid()
    said.me = me
    said.carrier = sides.carrier
    for a in addresses {
        let n = parted[a] != nil ? 0
            : (statedKeys.contains(a) && claimedKeys.contains(a)) ? 1 : 2
        said.sizes.append((a.replacingOccurrences(of: "\u{1}", with: " · "), n))
    }
    // the carrier owes an answer where the contract stated and it stayed silent;
    // the contract owes one the other way: the same size, read from two ends
    let owesCarrier = addresses.filter { parted[$0] == nil && !claimedKeys.contains($0)
                                         && statedKeys.contains($0) }
    let owesContract = addresses.filter { parted[$0] == nil && !statedKeys.contains($0)
                                          && claimedKeys.contains($0) }
    func excuse(_ key: String) -> (because: String, by: String, state: String)? {
        let two = key.components(separatedBy: "\u{1}")
        for k in known?.at("diverges")?.asList ?? [] {
            guard k.at("route")?.asText == two[0], k.at("field")?.asText == two[1] else { continue }
            let why = k.at("because")?.asText ?? ""
            let state = tracker.first(where: { $0.key == why })?.state
            return (why, k.at("declared_by")?.asText ?? "somebody",
                    state ?? (tracker.isEmpty ? "not checked" : "unread"))
        }
        return nil
    }
    func sort(_ items: [String], _ kind: String)
        -> (plain: [[(String, StatusJSON)]], live: [[(String, StatusJSON)]],
            dead: [[(String, StatusJSON)]]) {
        var plain: [[(String, StatusJSON)]] = [], live: [[(String, StatusJSON)]] = []
        var dead: [[(String, StatusJSON)]] = []
        for key in items {
            let address = key.replacingOccurrences(of: "\u{1}", with: " · ")
            guard let ex = excuse(key) else {
                plain.append([("address", .text(address)), ("kind", .text(kind))])
                continue
            }
            let one: [(String, StatusJSON)] = [("address", .text(address)),
                                               ("because", .text(ex.because)),
                                               ("declared_by", .text(ex.by)),
                                               ("state", .text(ex.state)),
                                               ("kind", .text(kind))]
            if ex.state == "Closed" { dead.append(one) } else { live.append(one) }
        }
        return (plain, live, dead)
    }
    let mine = sort(me == sides.carrier ? owesCarrier : owesContract, "unanswered")
    let theirs = sort(me == sides.carrier ? owesContract : owesCarrier, "unanswered")
    var parts = sort(parted.keys.sorted(), "parted")
    func why(_ row: [(String, StatusJSON)]) -> [(String, StatusJSON)] {
        var out = row
        guard case .text(let address)? = row.first(where: { $0.0 == "address" })?.1
        else { return out }
        let key = address.replacingOccurrences(of: " · ", with: "\u{1}")
        guard let p = parted[key] else { return out }
        out.append(("why", .text("the contract states \(p.want); \(sides.carrier) declares "
                                 + (p.mine.isEmpty ? "" : "its own \(p.mine) as ") + p.got)))
        return out
    }
    parts.plain = parts.plain.map(why)
    parts.live = parts.live.map(why)
    parts.dead = parts.dead.map(why)
    said.waitsOnYou = mine.plain
    said.youWaitOn = theirs.plain
    said.parted = parts.plain
    said.known = mine.live + theirs.live + parts.live
    said.expired = mine.dead + theirs.dead + parts.dead
    said.stated = statedKeys.count
    said.claimed = sides.claims.count
    said.note = "a standing account of who owes whom a word. An unanswered axis stays with "
              + "whoever owes the answer, so this reads the same from either side"
              + (known != nil ? ", and a divergence somebody declared is set aside while the "
                              + "thing it cites is open, and comes back when that closes" : "")
    said.next = !said.waitsOnYou.isEmpty
        ? "answer the first line above, or declare the divergence with something that can close"
        : (said.youWaitOn.isEmpty && said.parted.isEmpty
           ? "nothing waits on you here"
           : "these wait on the other side, and they are listed so you know what you are "
             + "waiting for")
    return said
}

func attentionPairs(_ said: AttentionSaid) -> [(String, StatusJSON)] {
    [("command", .text("attention")), ("as", .text(said.me)), ("carrier", .text(said.carrier)),
     ("sizes", .object(said.sizes.map { ($0.0, .raw(String($0.1))) })),
     ("waits_on_you", .list(said.waitsOnYou.map { .object($0) })),
     ("you_wait_on", .list(said.youWaitOn.map { .object($0) })),
     ("parted", .list(said.parted.map { .object($0) })),
     ("known", .list(said.known.map { .object($0) })),
     ("expired", .list(said.expired.map { .object($0) })),
     ("stated", .raw(String(said.stated))), ("claimed", .raw(String(said.claimed))),
     ("note", .text(said.note)), ("next", .text(said.next)), ("mutates", .raw("false"))]
}

// ── THE SEAMS THIS FOLDER IS PARTY TO, assembled for both surfaces. A
// declaration is a world in the contract grammar, so a pair is found by what
// the files SAY they are rather than by where they sit: one states records, the
// other claims them, and a repository may be either side or both. The door
// counts over these and the bench prints them as they are.
func seamsHere(_ w: WorldState) -> [[(String, StatusJSON)]] {
    let base = w.facts.map { (absPath($0) as NSString).deletingLastPathComponent }
        ?? FileManager.default.currentDirectoryPath
    var stated: [String] = [], claimed: [String] = []
    for full in declaredSeamFiles(base) where FileManager.default.fileExists(atPath: full)
        && isSeamSide(full) {
        let head = String((readText(full) ?? "").prefix(4000))
        if !matches("^public enum \\w+: Carrier \\{\\}", head, lines: true).isEmpty {
            claimed.append(full)
        } else { stated.append(full) }
    }
    let knownPath = (base as NSString).appendingPathComponent("known.json")
    let tickPath = (base as NSString).appendingPathComponent("tickets.json")
    var seams: [[(String, StatusJSON)]] = []
    if stated.isEmpty || claimed.isEmpty {
        // A SIDE DECLARED ALONE IS A STATE, NOT A BLANK: whoever moves first
        // would otherwise see nothing and think the declaration had not taken
        for f in stated + claimed {
            let isCarrier = claimed.contains(f)
            let name = isCarrier
                ? (matches("public enum (\\w+): Carrier", readText(f) ?? "").first?.first
                   ?? (f as NSString).lastPathComponent)
                : (f as NSString).lastPathComponent
            seams.append([("command", .text("attention")),
                          ("alone", .text(isCarrier ? "carries" : "states")),
                          ("carrier", .text(name)),
                          ("contract_file", .text((f as NSString).lastPathComponent)),
                          ("carrier_file", .text((f as NSString).lastPathComponent)),
                          ("stated", .raw("0")), ("claimed", .raw("0")),
                          ("waits_on_you", .list([])), ("you_wait_on", .list([])),
                          ("parted", .list([])), ("known", .list([])),
                          ("expired", .list([])), ("against", .null),
                          ("read_known", .null), ("read_tracker", .null)])
        }
    } else {
        for c in stated {
            for k in claimed {
                let said = attentionOver(
                    c, k, nil,
                    FileManager.default.fileExists(atPath: knownPath) ? knownPath : nil,
                    FileManager.default.fileExists(atPath: tickPath) ? tickPath : nil)
                // the pair's own answer entire, and the seam's fields after
                // it: the other carrier adds to that dict rather than
                // rebuilding it, so `mutates` stays where it was
                var one = attentionPairs(said)
                let decl = matches("^// \\w+ · against ([^\\n]+)$",
                                   String((readText(k) ?? "").prefix(2000)), lines: true)
                one.append(("against", decl.first.map { .text($0[0]) } ?? .null))
                one.append(("contract_file", .text((c as NSString).lastPathComponent)))
                one.append(("carrier_file", .text((k as NSString).lastPathComponent)))
                // AND THE PIN, WHERE THE OWNER IS LOOKING: what YOU wrote
                // down when you took each file, which is the fact you can act
                // on, and it was readable only by opening the manifest
                let (rows, mp) = layoutRowsFull((absPath(c) as NSString)
                    .deletingLastPathComponent)
                // built a field at a time: one long literal put the
                // type-checker past its budget, the way the journal's own
                // answer did before it
                var took: [StatusJSON] = []
                for f in [c, k] {
                    let name = (f as NSString).lastPathComponent
                    let row = rows.first(where: { $0.path == name })
                    var one2: [(String, StatusJSON)] = [("file", .text(name))]
                    let at: StatusJSON = row?.from.map { .text($0) } ?? .null
                    one2.append(("at", at))
                    let claim: StatusJSON = mp.map {
                        .text(($0 as NSString).lastPathComponent) } ?? .null
                    one2.append(("claim", claim))
                    let line: StatusJSON = row.map { .raw(String($0.line)) } ?? .null
                    one2.append(("line", line))
                    took.append(.object(one2))
                }
                one.append(("took", .list(took)))
                one.append(("read_known", FileManager.default.fileExists(atPath: knownPath)
                    ? .text("known.json") : .null))
                one.append(("read_tracker", FileManager.default.fileExists(atPath: tickPath)
                    ? .text("tickets.json") : .null))
                seams.append(one)
            }
        }
    }
    return seams
}

if args.first == "attention" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    loadStatusShelf()
    let w = discoverWorld()
    func flag(_ name: String) -> String? {
        guard let i = rest.firstIndex(of: name), i + 1 < rest.count else { return nil }
        return rest[i + 1]
    }
    if rest.count < 2 {
        // ── AND WITH NO ARGUMENTS IT IS THE MORNING QUESTION. This needed two
        // files named by hand, so the one thing an owner asks daily could only
        // be asked one pair at a time, by somebody who already knew the pairs.
        // The list is declared: this world knows its own seams.
        let seams = seamsHere(w)
        if seams.isEmpty {
            let note = "no seam is declared here, so nobody is waiting on anybody"
            let next = "gate theirs their-side.swift --role seam --at REV  say which pair you "
                     + "are party to, and this becomes the question you ask each morning"
            if asJson {
                out("{\n  \"command\": \"attention\",\n  \"asks\": true,\n"
                    + "  \"note\": " + jsonString(note) + ",\n"
                    + "  \"next\": " + jsonString(next) + "\n}\n")
            } else {
                out("usage: " + note + "\n  next: " + next + "\n")
            }
            exit(0)
        }
        func count(_ one: [(String, StatusJSON)], _ key: String) -> Int {
            guard case .list(let items)? = one.first(where: { $0.0 == key })?.1 else { return 0 }
            return items.count
        }
        let waiting = seams.reduce(0) { $0 + count($1, "waits_on_you") }
        let theirs = seams.reduce(0) { $0 + count($1, "you_wait_on") }
        let partedN = seams.reduce(0) { $0 + count($1, "parted") }
        let cameBack = seams.reduce(0) { $0 + count($1, "expired") }
        let next = "gate attention CONTRACT.swift CARRIER.swift  one pair, in full"
        if asJson {
            out(statusDumps(.object([
                ("command", .text("attention")),
                ("seams", .list(seams.map { .object($0) })),
                ("waiting_on_you", .raw(String(waiting))),
                ("you_wait_on", .raw(String(theirs))),
                ("parted", .raw(String(partedN))),
                ("came_back", .raw(String(cameBack))),
                ("next", .text(next)),
            ]), 0) + "\n")
        } else {
            // the morning cut: counted first, because the count is the answer
            var lines = ["attention: "
                         + (waiting > 0 ? "\(waiting) await your word" : "nothing awaits your word")
                         + " · \(theirs) awaiting theirs"
                         + (partedN > 0 ? " · parted at \(partedN)" : "")
                         + (cameBack > 0 ? " · \(cameBack) came back" : "")]
            for s in seams {
                var who = "a pair"
                if case .text(let a)? = s.first(where: { $0.0 == "against" })?.1 { who = a }
                else if case .text(let c)? = s.first(where: { $0.0 == "carrier" })?.1 { who = c }
                func rows(_ key: String) -> [[(String, StatusJSON)]] {
                    guard case .list(let items)? = s.first(where: { $0.0 == key })?.1
                    else { return [] }
                    return items.compactMap { if case .object(let o) = $0 { return o }; return nil }
                }
                func said(_ row: [(String, StatusJSON)], _ key: String) -> String {
                    if case .text(let v)? = row.first(where: { $0.0 == key })?.1 { return v }
                    return ""
                }
                for x in rows("expired") {
                    lines.append("  came back · \(said(x, "address")) · \(said(x, "because"))")
                }
                for x in rows("parted") { lines.append("  parted · \(said(x, "address")) · \(who)") }
                for x in rows("waits_on_you") {
                    lines.append("  your word · \(said(x, "address")) · \(who)")
                }
            }
            lines.append("  next: " + next)
            out(lines.joined(separator: "\n") + "\n")
        }
        exit(0)
    }
    let said = attentionOver(rest[0], rest[1], flag("--as"), flag("--known"), flag("--tracker"))
    if asJson {
        out(statusDumps(.object(attentionPairs(said)), 0) + "\n")
    } else {
        func said2(_ row: [(String, StatusJSON)], _ key: String) -> String {
            if case .text(let v)? = row.first(where: { $0.0 == key })?.1 { return v }
            return ""
        }
        var lines = ["attention: as \(said.me) · \(said.waitsOnYou.count) waiting on you · "
                     + "\(said.youWaitOn.count) you are waiting for · \(said.parted.count) parted"
                     + (said.expired.isEmpty ? "" : " · \(said.expired.count) came back")]
        for x in said.expired {
            lines.append("  came back · \(said2(x, "address")) · it was set aside for "
                         + "\(said2(x, "because")), and \(said2(x, "because")) is closed")
        }
        for x in said.waitsOnYou {
            let why = said2(x, "why")
            lines.append("  waits on you · \(said2(x, "address")) · "
                         + (why.isEmpty ? "stated by the contract, and you have not said "
                            + "whether you carry it" : why))
        }
        for x in said.youWaitOn {
            let why = said2(x, "why")
            lines.append("  you are waiting · \(said2(x, "address")) · "
                         + (why.isEmpty ? "you carry it, and the contract has not stated it" : why))
        }
        for x in said.parted {
            lines.append("  parted · \(said2(x, "address")) · \(said2(x, "why"))")
        }
        for x in said.known {
            lines.append("  known · \(said2(x, "address")) · set aside by "
                         + "\(said2(x, "declared_by")) for \(said2(x, "because")) "
                         + "(\(said2(x, "state").lowercased()))")
        }
        lines.append("  note: " + said.note)
        lines.append("  next: " + said.next)
        out(lines.joined(separator: "\n") + "\n")
    }
    exit(0)
}

// ── guard [merge] · guard deps [manifest lock]: the repository's OWN action
// policy by the same gates. A git object (the HEAD author) becomes an identity
// the world declares, becomes a probe entry of an existing form, becomes a
// judgement. CI and hooks only transport the verdict.
if args.first == "guard" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    loadStatusShelf()
    let w = discoverWorld()

    if rest.first == "deps" {
        // git's own soil: manifest against lockfile. The lock declares the atoms
        // and a requirement references its pin through an axis, so a drift
        // resolves to nothing, with an address. Not one new form.
        let tail = Array(rest.dropFirst())
        let manifestPath = tail.first ?? "package.json"
        let lockPath = tail.count > 1 ? tail[1] : "package-lock.json"
        let manifest = theirsJson(manifestPath, "a package manifest")
        let lock = theirsJson(lockPath, "the lockfile your resolver wrote")
        let deps = manifest.at("dependencies")?.asObject ?? []
        var pins: [(name: String, version: String)] = []
        for (name, info) in lock.at("packages")?.asObject ?? []
        where name.hasPrefix("node_modules/") {
            pins.append((String(name.dropFirst("node_modules/".count)),
                         info.at("version")?.asText ?? ""))
        }
        func atom(_ n: String, _ v: String) -> String {
            (n + "_" + v).replacingOccurrences(of: "-", with: "_")
                .replacingOccurrences(of: ".", with: "_")
                .replacingOccurrences(of: "@", with: "")
                .replacingOccurrences(of: "/", with: "_")
        }
        var lines = ["// printed by gate guard deps: the lockfile declares the atoms,",
                     "// the manifest's requirements reference them, so a drift fails to resolve.",
                     ""]
        var srcmap: [Int: String] = [:]
        for p in pins.sorted(by: { $0.name < $1.name }) {
            lines.append("public enum \(atom(p.name, p.version)): Close {}")
        }
        lines.append("")
        for (n, wantSaid) in deps.sorted(by: { $0.0 < $1.0 }) {
            let want = wantSaid.asText ?? ""
            let pinned = pins.first(where: { $0.name == n })?.version
            let first = want.first
            let target = (first != nil && (first!.isNumber || want.hasPrefix("=")))
                ? atom(n, String(want.drop(while: { $0 == "=" || $0 == "v" })))
                : (pinned.map { atom(n, $0) } ?? atom(n, "unpinned"))
            let stem = String(atom(n, "").dropLast())
            lines.append("public enum Req_\(stem): Close {")
            srcmap[lines.count] = "\((manifestPath as NSString).lastPathComponent) · "
                + "\"\(n)\": \"\(want)\""
            lines.append("    public typealias Pin = \(target)")
            lines.append("}")
        }
        let orphans = pins.map { $0.name }.filter { name in
            !deps.contains(where: { $0.0 == name }) }.sorted()
        let world = lines.joined(separator: "\n") + "\n"
        let d = scratchDir("gate-deps-")
        let p = (d as NSString).appendingPathComponent("deps-gate.swift")
        try? world.write(toFile: p, atomically: false, encoding: .utf8)
        var said = judgeFile(p)
        var sources: [String?] = said.refusals.map { ref in
            guard let n = Int(ref.address.components(separatedBy: ":").last ?? "")
            else { return nil }
            for k in max(0, n - 2)..<(n + 2) { if let s = srcmap[k] { return s } }
            return nil
        }
        try? FileManager.default.removeItem(atPath: d)
        var verdict = said.verdict
        if !orphans.isEmpty {
            verdict = "refused"
            for o in orphans {
                let version = pins.first(where: { $0.name == o })?.version ?? ""
                said.refusals.append((
                    "\((lockPath as NSString).lastPathComponent):\(lockLine(lockPath, o))",
                    "pin \(o)@\(version) is required by nothing: a leftover after removal"))
                sources.append(nil)
            }
        }
        let note = "a sketch, and not a product path: only orphan pins are detected. A missing "
                 + "pin yields a holds that means nothing, because the judge resolves no axis "
                 + "without a reading premise. Native ecosystem lockfile checkers already cover "
                 + "this class"
        if asJson {
            var pairs: [(String, StatusJSON)] = [
                ("command", .text("guard deps")),
                ("requirements", .raw(String(deps.count))),
                ("pins", .raw(String(pins.count))),
                ("verdict", .text(verdict)),
                ("refusals", .list(said.refusals.enumerated().map { (i, r) in
                    var one: [(String, StatusJSON)] = [("address", .text(r.address)),
                                                       ("claim", .text(r.claim))]
                    if i < sources.count, let s = sources[i] { one.append(("source", .text(s))) }
                    return .object(one) })),
                ("judge_ms", said.judgeMs.map { .raw(floatRepr($0)) } ?? .null),
                ("wall_ms", .raw(String(said.wallMs))),
            ]
            if !orphans.isEmpty {
                pairs.append(("orphan_pins", .list(orphans.map { .text($0) })))
            }
            pairs.append(("note", .text(note)))
            out(statusDumps(.object(pairs), 0) + "\n")
        } else {
            var lines = ["guard deps: "
                         + (verdict == "holds" ? "holds" : "refused \(said.refusals.count)")
                         + (said.judgeMs.map { " · " + floatRepr($0) + " ms" } ?? "")]
            for (i, r) in said.refusals.enumerated() {
                let s = i < sources.count ? (sources[i] ?? "") : ""
                lines.append("  \(r.address) · \(r.claim)" + (s.isEmpty ? "" : "  (\(s))"))
            }
            lines.append("  note: " + note)
            out(lines.joined(separator: "\n") + "\n")
        }
        exit(verdict == "holds" ? 0 : 1)
    }

    let action = rest.first ?? "merge"
    guard let facts = w.facts, FileManager.default.fileExists(atPath: facts) else {
        cannot("guard reads who may act from a world, and there is no world here",
               "run `gate init .` to start one, or `gate demo` for a repository to look at")
    }
    let worldDir = (absPath(facts) as NSString).deletingLastPathComponent
    let email = runGit(["log", "-1", "--format=%ae"], worldDir)
        .trimmingCharacters(in: .whitespacesAndNewlines)
    var policy = readPolicy(w)
    var statedIn = "gate.policy.swift"
    if policy.ids.isEmpty && policy.rules.isEmpty, let tables = w.tables {
        // a world that has not stated them yet: the tables are a seed, and the
        // sentence says so rather than pretending the world declared it
        statedIn = "tables (a seed): declare them in the world to put them under review"
        let idp = (tables as NSString).appendingPathComponent("identities.csv")
        if FileManager.default.fileExists(atPath: idp) {
            let t = csvTable(idp, "the identities this world binds")
            for r in t.rows.indices {
                policy.ids.append((t.text(r, "email"), t.text(r, "id")))
            }
        }
        let gp = (tables as NSString).appendingPathComponent("guard.csv")
        if FileManager.default.fileExists(atPath: gp) {
            let t = csvTable(gp, "the actions this world guards")
            for r in t.rows.indices {
                policy.rules.append((t.text(r, "action"), t.text(r, "requires_rank")))
            }
        }
    }
    guard let required = policy.rules.first(where: { $0.action == action })?.rank else {
        // capitalize the way the other carrier's str.capitalize does: the first
        // letter up and the rest DOWN. And the doubled braces are its own, from
        // an f-string that escapes them twice: a sentence is copied, not fixed.
        cannot("no policy states who may " + action,
               "declare `public enum " + action.prefix(1).uppercased()
               + action.dropFirst().lowercased()
               + "Policy {{ public typealias Requires = <rank> }}` in gate.policy.swift")
    }
    let who = policy.ids.first(where: { $0.mail == email })?.who
    func answer(_ pairs: [(String, StatusJSON)], _ red: Bool) -> Never {
        if asJson {
            out(statusDumps(.object(pairs), 0) + "\n")
        } else {
            var lines: [String] = []
            var head = ""
            var refusals: [(String, String)] = []
            var ms: String? = nil
            for (k, v) in pairs {
                if k == "verdict", case .text(let s) = v { head = s }
                if k == "judge_ms", case .raw(let s) = v { ms = s }
                if k == "refusals", case .list(let items) = v {
                    for one in items {
                        guard case .object(let o) = one else { continue }
                        var a = "", c = ""
                        for (kk, vv) in o {
                            if kk == "address", case .text(let s) = vv { a = s }
                            if kk == "claim", case .text(let s) = vv { c = s }
                        }
                        refusals.append((a, c))
                    }
                }
            }
            lines.append("guard \(action): "
                         + (head == "holds" ? "holds" : "refused \(refusals.count)")
                         + (ms.map { " · " + $0 + " ms" } ?? ""))
            for (a, c) in refusals { lines.append("  \(a) · \(c)") }
            out(lines.joined(separator: "\n") + "\n")
        }
        exit(red ? 1 : 0)
    }
    guard let who = who else {
        answer([("command", .text("guard " + action)), ("author", .text(email)),
                ("policy_from", .text(statedIn)), ("verdict", .text("refused")),
                ("refusals", .list([.object([
                    ("address", .text((facts as NSString).lastPathComponent)),
                    ("claim", .text("author \(email) is not mapped to any person: an "
                                    + "unknown identity performs no guarded action"))])]))],
               true)
    }
    // the shared world alone, and literally the same reading `status` makes
    if !worldPeopleOf(w).contains(who) {
        let (f, ln) = policy.whereAt[email] ?? ((facts as NSString).lastPathComponent, 1)
        answer([("command", .text("guard " + action)),
                ("author", .text("\(email) = \(who)")),
                ("policy_from", .text(statedIn)), ("verdict", .text("refused")),
                ("refusals", .list([.object([
                    ("address", .text("\(f):\(ln)")),
                    ("claim", .text("an identity names `\(who)`, and the world declares "
                                    + "no such person"))])]))],
               true)
    }
    // this door has one surface, the terminal, so a refusal here still ends the
    // run: it is said in the same words the writer hands back
    let probe: String
    do { probe = try lastEntryInsert(readText(facts) ?? "", "VerifiedAtRank", who, required, 8) }
    catch let e as CannotSay { cannot(e.note, e.next) }
    catch { cannot("this check could not be written", "run `gate status` and read the world") }
    let said = judgeFile(withTemp(probe, (facts as NSString).lastPathComponent))
    answer([("command", .text("guard " + action)),
            ("author", .text("\(email) = \(who)")),
            ("requires", .text(required)),
            ("policy_from", .text(statedIn)),
            ("verdict", .text(said.verdict)),
            ("refusals", .list(said.refusals.map {
                .object([("address", .text($0.address)), ("claim", .text($0.claim))]) })),
            ("judge_ms", said.judgeMs.map { .raw(floatRepr($0)) } ?? .null),
            ("wall_ms", .raw(String(said.wallMs))),
            ("mutates", .raw("false"))],
           said.verdict != "holds")
}

if args.first == "verify" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    loadStatusShelf()
    // a verb meets a person with a sentence, never a stack trace: typed in a
    // world that keeps no tables this answered with an index error
    if rest.count < 2 || rest[0].hasPrefix("-") || rest[1].hasPrefix("-") {
        let note = "verify reads two catalogue files and judges their seeds"
        let next = "gate verify people.csv grants.csv [--against CMD]: the two tables, "
                 + "and the checker you have today if you want the two answers compared "
                 + "claim by claim"
        if !rest.filter({ !$0.hasPrefix("-") }).isEmpty { cannot(note, next) }
        if asJson {
            out("{\n  \"command\": \"verify\",\n  \"asks\": true,\n"
                + "  \"note\": " + jsonString(note) + ",\n"
                + "  \"next\": " + jsonString(next) + "\n}\n")
        } else {
            out("usage: " + note + "\n  next: " + next + "\n")
        }
        exit(0)
    }
    let against = rest.firstIndex(of: "--against").flatMap {
        $0 + 1 < rest.count ? rest[$0 + 1] : nil }
    let said = verifySeeds(rest[0], rest[1], against)
    if said.dirty {
        if asJson {
            out(statusDumps(.object([
                ("command", .text("verify")),
                ("base", .text("dirty: fix these before seeding")),
                ("world_says", .list(said.worldSays.map { .text($0) })),
                ("legacy_says", .list(said.legacySays.map { .text($0) })),
            ]), 0) + "\n")
        } else {
            var lines = ["verify: base dirty. Fix these before seeding"]
            for w in said.worldSays { lines.append("  world:  " + w) }
            for l in said.legacySays { lines.append("  legacy: " + l) }
            out(lines.joined(separator: "\n") + "\n")
        }
        exit(1)
    }
    let holes = said.rows.filter { $0.reading.hasPrefix("NOT TRANSLATED")
                                || $0.reading.hasPrefix("NO GATE") }.count
    if asJson {
        out(statusDumps(.object([
            ("command", .text("verify")),
            ("seeds", .list(said.rows.map { r in
                .object([("seed", .text(r.seed)), ("world", .text(r.world)),
                         ("world_says", .list(r.worldSays.map { .text($0) })),
                         ("legacy", .text(r.legacy)),
                         ("legacy_says", .list(r.legacySays.map { .text($0) })),
                         ("reading", .text(r.reading))]) })),
            ("translation_holes", .raw(String(holes))),
        ]), 0) + "\n")
    } else {
        var lines = ["verify: \(holes) hole(s)"]
        for r in said.rows {
            lines.append("  " + r.seed.padding(toLength: max(22, r.seed.count),
                                               withPad: " ", startingAt: 0)
                         + " world=" + r.world.padding(toLength: max(8, r.world.count),
                                                       withPad: " ", startingAt: 0)
                         + " legacy=" + r.legacy.padding(toLength: max(8, r.legacy.count),
                                                         withPad: " ", startingAt: 0)
                         + " → " + r.reading)
        }
        out(lines.joined(separator: "\n") + "\n")
    }
    exit(holes > 0 ? 1 : 0)
}

// ── library [-o lib.json] | library diff a.json b.json: the domain vocabulary.
// Forms carry no facts, so a library is shareable and client data never is
// (SAT5: a domain has one canonical vocabulary; two worlds are subsets of it).
if args.first == "library" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    if rest.first == "diff" {
        guard rest.count > 2 else {
            cannot("library diff reads two libraries printed by `gate library -o`",
                   "name them: `gate library diff a.json b.json`")
        }
        let la = theirsJson(rest[1], "a library printed by `gate library -o`")
        let lb = theirsJson(rest[2], "a library printed by `gate library -o`")
        let a = Set((la.at("forms")?.asList ?? []).compactMap { $0.asText })
        let b = Set((lb.at("forms")?.asList ?? []).compactMap { $0.asText })
        let note = "the union is safe by construction: one domain has one canonical "
                 + "vocabulary (SAT5), so a difference is teachable form, never client data"
        // this head has no line of its own on the other carrier: its answer
        // falls through to the object, whichever way it was asked
        out(statusDumps(.object([
            ("command", .text("library diff")),
            ("shared", .list(a.intersection(b).sorted().map { .text($0) })),
            ("only_first", .list(a.subtracting(b).sorted().map { .text($0) })),
            ("only_second", .list(b.subtracting(a).sorted().map { .text($0) })),
            ("note", .text(note)),
        ]), 0) + "\n")
        exit(0)
    }
    // ── AND THE GUARD SITS AT THE READING, NOT AT ONE SPELLING OF THE ARGV. It
    // asked whether argv was empty, so `library` bare refused in words and
    // `library -o lib.json` opened a world file that is not there and raised.
    loadStatusShelf()
    let w = discoverWorld()
    guard let facts = w.facts, FileManager.default.fileExists(atPath: facts) else {
        cannot("library reads the vocabulary a world is written in, and there is no world here",
               "run `gate init .` to start one, or `gate demo` for a repository to look "
               + "at. `gate library diff a.json b.json` needs no world")
    }
    let outPath = rest.firstIndex(of: "-o").flatMap { $0 + 1 < rest.count ? rest[$0 + 1] : nil }
    let text = readText(facts) ?? ""
    let heads = Set(matches("(\\w+)<\\s*\\w+,\\s*\\w+\\s*>\\.self;?", text)
        .compactMap { $0.first }).sorted()
    let axes = Set(matches("public typealias (\\w+) = ", text)
        .compactMap { $0.first }).sorted()
    var coverage: [(String, String)] = []
    if let tables = w.tables {
        let said = verifySeeds((tables as NSString).appendingPathComponent("people.csv"),
                               (tables as NSString).appendingPathComponent("grants.csv"), nil)
        for r in said.rows {
            coverage.append((r.seed, r.world == "refused" ? "held" : "no gate"))
        }
    }
    let next = "run `gate status` to judge what this vocabulary is used to say"
    var lib: [(String, StatusJSON)] = [("forms", .list(heads.map { .text($0) })),
                                       ("axes", .list(axes.map { .text($0) }))]
    if !coverage.isEmpty {
        lib.append(("coverage", .object(coverage.map { ($0.0, .text($0.1)) })))
    }
    if let path = outPath {
        // sort_keys, indent 2: the shape the other carrier's json.dump writes
        // sort_keys, indent 2, and no trailing newline: the shape the other
        // carrier's json.dump leaves on disk
        var page: [(String, StatusJSON)] = lib.sorted { $0.0 < $1.0 }
        if let i = page.firstIndex(where: { $0.0 == "coverage" }),
           case .object(let rows) = page[i].1 {
            page[i] = ("coverage", .object(rows.sorted { $0.0 < $1.0 }))
        }
        oursWrite(path, "this world's vocabulary", statusDumps(.object(page), 0))
    }
    var pairs: [(String, StatusJSON)] = [("command", .text("library")),
                                         ("facts", .text(facts))] + lib
    pairs.append(("next", .text(next)))
    if let path = outPath { pairs.append(("wrote", .text(path))) }
    if let ready = commandIn(next) { pairs.append(("command_to_run", .text(ready))) }
    if asJson {
        out(statusDumps(.object(pairs), 0) + "\n")
    } else {
        out("library: " + many(heads.count, "form")
            + (outPath.map { " · wrote " + $0 } ?? "")
            + "\n  next: " + next + "\n")
    }
    exit(0)
}

if args.first == "import" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    // the shelf before anything is printed: every head here prints a world in
    // the shipped forms, and a world printed before the shelf was read is a
    // world with its own vocabulary missing
    loadStatusShelf()
    func after(_ flag: String) -> String? {
        guard let i = rest.firstIndex(of: flag), i + 1 < rest.count else { return nil }
        return rest[i + 1]
    }
    let head = rest.first ?? ""

    // ── import codeowners CODEOWNERS [--tree DIR] [--policy owners.csv] [-o F]
    if head == "codeowners" {
        let tail = Array(rest.dropFirst())
        // the verb the cover sells finds the file it is named after: typed bare
        // it read argv[0] of an empty argv and met a person with an IndexError
        let src = (tail.first.flatMap { $0.hasPrefix("-") ? nil : $0 })
            ?? CODEOWNERS_PLACES.first(where: { FileManager.default.fileExists(atPath: $0) })
        guard let src = src else {
            cannot("this reads a CODEOWNERS, and there is none at "
                   + CODEOWNERS_PLACES.joined(separator: ", "),
                   "name the file: `gate import codeowners PATH`, or run `gate demo` for a "
                   + "repository that has one")
        }
        func flag(_ name: String) -> String? {
            guard let i = tail.firstIndex(of: name), i + 1 < tail.count else { return nil }
            return tail[i + 1]
        }
        let asked = flag("-o")
        // without -o the world still goes to a path, because the court reads
        // one: it goes to the scratch this verb sweeps
        let kept = asked == nil ? scratchDir("gate-codeowners-") : nil
        let outPath = asked ?? (kept! as NSString)
            .appendingPathComponent("codeowners-gate.swift")
        let tree = flag("--tree")
        let policyPath = flag("--policy")
        let policy = policyPath.map { readOwnersPolicy($0) } ?? []
        // ── AND THE PROVENANCE IS WRITTEN THE WAY THE WORLD WILL READ IT. This
        // recorded the source exactly as it was typed, and the guard that
        // checks it resolves that text against the world the file lives in: a
        // caller who names an absolute path (which is what a verb spawning
        // this one should do, since no two processes need agree about "here")
        // left a world refusing itself for a file sitting right beside it.
        // What is recorded is the path from the world to its source.
        let outDir = parentPath(absPath(outPath)) ?? absPath(outPath)
        func fromHere(_ p: String) -> String {
            return leavesRoot(absPath(p), outDir) ? p : relPath(absPath(p), outDir)
        }
        let saidFrom = fromHere(src) + (policyPath.map { " --policy " + fromHere($0) } ?? "")
        mark("codeowners-begin")
        let (lines, srcmap, rules, keepers) = codeownersWorldLines(src, policy, saidFrom)
        mark("world-built")
        let world = lines.joined(separator: "\n") + "\n"
        oursWrite(outPath, "the world this prints", world)
        mark("world-written")
        let t0 = Date()
        let outp = courtSays(["where", outPath])
        mark("world-judged")
        let ms = ((Date().timeIntervalSince(t0) * 1000 * 10).rounded(.toNearestOrEven)) / 10
        // ONE FACT, ONE SENTENCE: the words belong to the law, in the file the
        // law is written in, and both surfaces read them from there
        let notes = lawNotes([world])
        mark("notes-built")
        var refusals: [(certificate: String, source: String, address: String, claim: String)] = []
        for (cert, claim) in whereRefused(outp) {
            guard let cert = cert, let source = srcmap[cert] else { continue }
            refusals.append((cert, source, source.components(separatedBy: " · ")[0],
                             plainly(claim, notes)))
        }
        // a pattern matching no file in the tree: CODEOWNERS says it, the tree does not
        var ghosts: [(address: String, claim: String)] = []
        var dupShadows = 0
        if let tree = tree {
            let paths = treeFiles(tree)
            // the address names the file that makes the claim, relative to the
            // walked tree, which is how the reader's own editor opens it
            let rel = relPath(absPath(src), absPath(tree))
            let at = rel.hasPrefix("..") ? src : rel
            ghosts = ghostPatterns(rules, paths, at)
            // and the rules that never win: github reads the LAST match, so a
            // rule every file of which is taken by a later one decides nothing.
            // An override (the early owner loses routing) is refused at its
            // line; a duplicate is counted aloud and refuses nothing.
            let sh = codeownersShadows(rules, paths)
            dupShadows = sh.duplicates
            for o in sh.overrides {
                ghosts.append(("\(at):\(o.line)",
                               "`\(o.pattern)` never wins: every file it matches is "
                             + "taken by the rule at line \(o.beatenBy), which names "
                             + "different owners"))
            }
        }
        mark("refusals-read")
        let zones = Set(rules.map { codeownersZone($0.pattern) }).count
        // ── AND AN EMPTY READ IS A REFUSAL, NOT A VERDICT. A CODEOWNERS this
        // door reads no line of, because it is empty, or all comments, or
        // written in a shape this reader does not take, used to answer `holds`
        // and exit nought. The counts beside that word were honest (zones 0,
        // paths 0, owners 0) and the word ignored them, so a person whose file
        // is spelled another way was told their ownership was guarded. The law
        // is already here, one line down: a run with no policy is `observed`
        // rather than `holds`, because a green nobody could have broken is not
        // a green. Nothing read is that said harder: there was nothing to
        // break, and nothing to hold.
        var unread: [(address: String, claim: String)] = []
        if rules.isEmpty {
            let at = tree.map { relPath(absPath(src), absPath($0)) }
            unread.append((at.map { $0.hasPrefix("..") ? src : $0 } ?? src,
                           "states no rule this reads, so nothing was read and there is "
                         + "nothing to hold: a line names a path and then who keeps it, "
                         + "`src/api/ @alice`"))
        }
        // ── AND WHAT THIS DID NOT READ IS SAID, NOT SKIPPED. The lines an
        // owner stands on became rules and the rest fell in silence, so a
        // file with prose pasted into it judged as a clean map of whatever
        // rules survived. A line this reader does not take is named at its
        // line, and no claim is made about it.
        let atSrc = { (n: Int) -> String in
            let r = tree.map { relPath(absPath(src), absPath($0)) }
            let head = (r?.hasPrefix("..") ?? true) ? src : r!
            return "\(head):\(n)"
        }
        var noise: [(address: String, claim: String)] = []
        for nl in codeownersUnread(theirsText(src, "the CODEOWNERS this reads")) {
            noise.append((atSrc(nl.line),
                          "this line does not read as a rule: a rule is a path and "
                        + "then who keeps it, and no word here is an owner. No claim "
                        + "is made about it"))
        }
        let refusedAny = !refusals.isEmpty || !ghosts.isEmpty || !unread.isEmpty
            || !noise.isEmpty
        // A GREEN NOBODY COULD HAVE BROKEN IS NOT A GREEN: without a policy every
        // rule is its own authority, so the equalities cannot fail
        let verdict = refusedAny ? "refused" : (policy.isEmpty ? "observed" : "holds")
        // and the note says what the run WAS: a note about halves being held,
        // printed over a read that took nothing in, is the same green wearing
        // longer words
        let note = !unread.isEmpty
            ? "nothing was read, so nothing here is a statement about your ownership: "
              + "this door takes a path and then who keeps it. Check the shape of the "
              + "file, or point this at the one your reviews actually use"
            : !noise.isEmpty
            ? "part of this file is not rules: the lines named above were not read, "
              + "and the rules beside them were judged as usual"
            : policy.isEmpty
            ? "no ownership policy given (--policy owner,zone): every rule is its own "
              + "authority, so the equalities hold trivially. The unmatched patterns above "
              + "are read from the tree, not judged."
            : "ownership is the warden's threshold and this run holds both halves of "
              + "it: the zone equalities against one canon, and the key's class through "
              + "the ladder this world presents (docs/DETAILS.md, "
              + "what this road does not judge)"
        let note2 = dupShadows > 0
            ? note + " " + many(dupShadows, "rule") + " duplicate"
              + (dupShadows == 1 ? "s" : "") + " later rules naming the same owners."
            : note
        let w = discoverWorld()
        mark("world-discovered")
        let declared = (w.layout?.rows ?? []).map { $0.path }
        let next = !unread.isEmpty
            ? "`gate import codeowners` reads the shape github reads: a path, then the "
              + "people who keep it. If yours is that shape and this still reads none of "
              + "it, that is worth telling us: docs/SECURITY.md says how"
            : !noise.isEmpty
            ? "open the address above: if that line is meant to be a rule, give it an "
              + "owner; if it is prose, move it out or put a `#` in front of it"
            : asked == nil
            // the advice knows what already stands: offering -o beside a world
            // whose from: line names this very file is the lock-on-the-door
            // species, and the pair enumeration answers it
            ? (codeownersPairedWorlds(w).first { $0.srcAbs == absPath(src) }.map {
                   $0.name + " already keeps this file, and every `gate status` "
                 + "translates it again: a line changed on either side alone "
                 + "is named at its line"
               } ?? ("nothing was written: this read your CODEOWNERS and your tree and left "
                     + "both as they were. Add `-o ownership.swift` to keep the world it printed"))
            : (w.layout != nil && !declared.contains(asked!))
            ? "declare it: `gate mine \(asked!) --role forms` adds the row the layout "
              + "in gate.manifest.swift asks for, and then commit. Until it has one, "
              + "status names it as a file standing beside the judged ones"
            : "commit it: from here on it is what you have said, and it is judged"
        if kept != nil { try? FileManager.default.removeItem(atPath: kept!) }
        let all = refusals.map { (address: $0.address, claim: $0.claim) } + ghosts + unread
            + noise
        if asJson {
            var pairs: [(String, StatusJSON)] = [
                ("command", .text("import codeowners")),
                ("world", asked.map { .text($0) } ?? .null),
                ("wrote", asked.map { .text($0) } ?? .null),
                ("zones", .raw(String(zones))),
                ("paths", .raw(String(rules.count))),
                ("owners", .raw(String(keepers.count))),
                ("policy", policy.isEmpty ? .null
                    : .text(many(policy.count, "owner") + " "
                            + (policy.count == 1 ? "has" : "have") + " a stated zone")),
                ("verdict", .text(verdict)),
                ("refusals", .list(refusals.map {
                    .object([("certificate", .text($0.certificate)),
                             ("source", .text($0.source)),
                             ("address", .text($0.address)),
                             ("claim", .text($0.claim))]) }
                    + (ghosts + unread + noise).map {
                    .object([("address", .text($0.address)), ("claim", .text($0.claim))]) })),
                ("judge_ms", .raw(String(ms))),
                ("canon_handshake", .raw(outp.contains("canon v2") ? "true" : "false")),
                ("note", .text(note2)),
                ("next", .text(next)),
            ]
            if let ready = commandIn(next) { pairs.append(("command_to_run", .text(ready))) }
            out(statusDumps(.object(pairs), 0) + "\n")
        } else {
            let headSaid = verdict == "refused" ? "refused \(all.count)" : verdict
            var lines = ["import codeowners: " + headSaid + " · " + floatRepr(String(ms)) + " ms"]
            for r in refusals {
                let rule = r.source.hasPrefix(r.address + " · ")
                    ? String(r.source.dropFirst(r.address.count + 3)) : r.source
                lines.append("  \(r.address) · \(r.claim)" + (rule.isEmpty ? "" : "  (\(rule))"))
            }
            for g in ghosts + unread + noise { lines.append("  \(g.address) · \(g.claim)") }
            lines.append("  note: " + note2)
            lines.append("  next: " + next)
            out(lines.joined(separator: "\n") + "\n")
        }
        exit(refusedAny ? 1 : 0)
    }

    // ── import refs tracker.json [--code DIR] [-o refs-gate.swift]
    if head == "refs" {
        mark("refs-begin")
        let tail = Array(rest.dropFirst())
        guard let src = tail.first, !src.hasPrefix("-") else {
            cannot("this reads a tracker export, and no file was named",
                   "name it: `gate import refs tracker.json --code .`")
        }
        func flag(_ name: String) -> String? {
            guard let i = tail.firstIndex(of: name), i + 1 < tail.count else { return nil }
            return tail[i + 1]
        }
        let code = flag("--code") ?? "."
        let keep = tail.contains("-o")
        let kept = keep ? nil : scratchDir("gate-refs-")
        let outPath = flag("-o") ?? (kept! as NSString).appendingPathComponent("refs-gate.swift")
        let tracked = readTracker(src)
        let cites = readCitations(code)
        // the world is built by the refs core, cut out and asked alone by the
        // battery; the readers above and the writer below stay in the rim
        let built = refsWorldBuild(tracked, cites,
                                   REFS_HEADER + (STDLIB_TEXTS["forms-reference"] ?? ""))
        let (world, srcmap) = (built.world, built.srcmap)
        oursWrite(outPath, "the world this prints", world)
        let t0 = Date()
        let outp = courtSays(["where", outPath])
        let ms = ((Date().timeIntervalSince(t0) * 1000 * 10).rounded(.toNearestOrEven)) / 10
        var refusals: [(address: String, claim: String)] = []
        for m in matches("^✗ '(\\w+)[^']*' requires the types '[^']*' \\(aka '([^']+)'\\)",
                         outp, lines: true) {
            guard let where_ = srcmap[m[0]] else { continue }
            let claim = m[1].hasSuffix(".State")
                ? "the code cites \(where_.key), and the tracker has no such thing"
                : "the code cites \(where_.key) as live work, and the tracker calls it "
                  + m[1].lowercased()
            refusals.append((where_.address, claim))
        }
        if let kept = kept { try? FileManager.default.removeItem(atPath: kept) }
        // ── AND AN EMPTY READ IS A REFUSAL HERE TOO. A tracker with no issues
        // in it, or a tree with no citation in it, is not a world where every
        // citation outlives nothing: it is a reading that took nothing in, and
        // the word over it may not be the word for a world that held.
        if tracked.isEmpty || cites.isEmpty {
            refusals.append((address: (src as NSString).lastPathComponent,
                             claim: tracked.isEmpty
                                ? "states no issue this reads, so there is nothing for a "
                                + "citation to outlive: name the export your tracker writes"
                                : "no citation was found under \(code), so nothing was "
                                + "read: a citation names its key, `TODO(PROJ-1)`"))
        }
        let next = refusals.isEmpty
            // the advice knows where it is standing, as in import workflows
            ? (ProcessInfo.processInfo.environment["GITHUB_ACTIONS"] == "true"
               ? "this run is that wire: a citation cannot outlive its ticket again"
               : "wire it into CI: a citation cannot outlive its ticket again")
            : "open the address above: the citation outlived the thing it cites"
        if asJson {
            var pairs: [(String, StatusJSON)] = [
                ("command", .text("import refs")),
                ("wrote", keep ? .text(outPath) : .null),
                ("tracked", .raw(String(tracked.count))),
                ("citations", .raw(String(cites.count))),
                ("ms", .raw(String(ms))),
                ("verdict", .text(refusals.isEmpty ? "holds" : "refused")),
                ("refusals", .list(refusals.map {
                    .object([("address", .text($0.address)), ("claim", .text($0.claim))]) })),
                ("next", .text(next)),
                ("mutates", .raw("true")),
            ]
            if let ready = commandIn(next) { pairs.append(("command_to_run", .text(ready))) }
            out(statusDumps(.object(pairs), 0) + "\n")
        } else {
            var lines = ["import refs: "
                         + (refusals.isEmpty ? "holds" : "refused \(refusals.count)")]
            for r in refusals { lines.append("  \(r.address) · \(r.claim)") }
            lines.append("  next: " + next)
            out(lines.joined(separator: "\n") + "\n")
        }
        exit(refusals.isEmpty ? 0 : 1)
    }

    // ── import rbac rbac.json [-o gate.swift]
    if head == "rbac" {
        mark("rbac-begin")
        let tail = Array(rest.dropFirst())
        guard let src = tail.first, !src.hasPrefix("-") else {
            cannot("this reads a kubectl dump of roles and bindings, and no file was named",
                   "name it: `gate import rbac rbac.json`")
        }
        let outPath = { () -> String in
            guard let i = tail.firstIndex(of: "-o"), i + 1 < tail.count else {
                return "rbac-gate.swift"
            }
            return tail[i + 1]
        }()
        let items = theirsJson(src, "a kubectl dump of roles and bindings")
            .at("items")?.asList ?? []
        // the world is built by the rbac core, cut out and asked alone by the
        // battery; the reader above and the writer below stay in the rim
        let built = rbacWorldBuild(items,
                                   RBAC_FORMS_HEADER + (STDLIB_TEXTS["forms-grants"] ?? ""))
        let (world, srcmap, checked) = (built.world, built.srcmap, built.checked)
        oursWrite(outPath, "the world this prints", world)
        let t0 = Date()
        let outp = courtSays(["where", outPath])
        let ms = ((Date().timeIntervalSince(t0) * 1000 * 10).rounded(.toNearestOrEven)) / 10
        var refusals: [(certificate: String, source: String, address: String, claim: String)] = []
        for m in matches("^✗ '(\\w+)[^']*' requires the types '[^']*' \\(aka '([^']+)'\\) "
                         + "and '[^']*' \\(aka '([^']+)'\\) be equivalent", outp, lines: true) {
            guard let what = srcmap[m[0]] else { continue }
            let dangling = matchAt(m[2], "^(\\w+)\\.Place$") != nil
            let claim = dangling
                ? "roleRef names a Role that exists nowhere (\(m[2]) undeclared)"
                : "the binding lives in \(m[1]), its Role lives in \(m[2]): a RoleBinding "
                  + "and its Role must share one namespace"
            refusals.append((m[0], what, what.components(separatedBy: " · ")[0], claim))
        }
        // ── AND AN EMPTY READ IS A REFUSAL HERE TOO. A cluster export with no
        // binding in it does not hold: nothing was posted, so nothing could be
        // posted wrongly, and a word about two tiers being judged over a read
        // of nothing is that green wearing longer words.
        if checked == 0 {
            refusals.append(((src as NSString).lastPathComponent,
                             (src as NSString).lastPathComponent,
                             (src as NSString).lastPathComponent,
                             "states no RoleBinding this reads, so no posting was judged: "
                           + "point this at the export your cluster writes, items and all"))
        }
        let note = checked == 0
            ? "nothing was judged: this read the export and found no binding to post, so "
              + "no sentence here is about your cluster"
            : "both tiers of the gate are judged by this run: the posting equalities "
                 + "against one canon, and the key's class through the ladder the world "
                 + "presents (the membership court)"
        if asJson {
            out(statusDumps(.object([
                ("command", .text("import rbac")),
                ("world", .text(outPath)),
                ("namespaces", .raw(String(built.namespaces))),
                ("roles", .raw(String(built.roles))),
                ("cluster_roles", .raw(String(built.clusterRoles))),
                ("bindings_judged", .raw(String(checked))),
                ("verdict", .text(refusals.isEmpty ? "holds" : "refused")),
                ("refusals", .list(refusals.map {
                    .object([("certificate", .text($0.certificate)),
                             ("source", .text($0.source)),
                             ("address", .text($0.address)),
                             ("claim", .text($0.claim))]) })),
                ("judge_ms", .raw(String(ms))),
                ("canon_handshake", .raw(outp.contains("canon v2") ? "true" : "false")),
                ("note", .text(note)),
            ]), 0) + "\n")
        } else {
            var lines = ["import rbac: "
                         + (refusals.isEmpty ? "holds" : "refused \(refusals.count)")
                         + " · " + floatRepr(String(ms)) + " ms"]
            for r in refusals {
                let rule = r.source.hasPrefix(r.address + " · ")
                    ? String(r.source.dropFirst(r.address.count + 3)) : r.source
                lines.append("  \(r.address) · \(r.claim)" + (rule.isEmpty ? "" : "  (\(rule))"))
            }
            lines.append("  note: " + note)
            out(lines.joined(separator: "\n") + "\n")
        }
        exit(refusals.isEmpty ? 0 : 1)
    }

    // ── import workflows [--tree DIR]: the second adaptor.
    //
    // A workflow says which paths wake it: `on.push.paths`, and `paths-ignore`
    // beside it. That is a claim about this tree, written by one team and
    // obeyed by a runner nobody watches; when a folder is renamed the filter
    // goes on being obeyed and wakes nothing, and nothing anywhere says so. A
    // job that does not run leaves no red line, no log and no mail.
    //
    // AND THIS DOES NOT SEARCH THE FILE, IT READS THE DOCUMENT. The first cut
    // of this looked for `paths:` anywhere in the text and took what followed.
    // That is a search, and a search answers about things it was not asked
    // about: on vitess it found four `paths:` keys belonging to somebody
    // else's action under `with:`, and called a step's parameter a claim about
    // this repository. Both mistakes are the same mistake, which is reading a
    // format by resemblance instead of by structure.
    //
    // So the reading is structural and NARROW, and it refuses rather than
    // guesses. `yamlBlock` below takes the block subset these files are
    // written in: comments, `key:`, `key: value`, `- item`, nesting by spaces.
    // Anything outside that subset (a tab, an anchor, an alias, a folded or
    // literal scalar, a flow mapping) is not read past: the file is NAMED as
    // unread, with the line, and no claim is made about it. A reader that
    // skips what it does not understand is the silence this tool exists
    // against, and one that guesses is worse.
    //
    // The claim is then taken by its address in the document, `on` then `push`
    // or `pull_request` then `paths`, and never by where a string happens to
    // appear. Note that a general yaml reader is no help here: in yaml 1.1 the
    // key `on` reads as the boolean true, which is why this platform's own
    // documents are famous for it. Reading the text as text is the exact
    // reading.
    if head == "workflows" {
        mark("workflows-begin")
        let tail = Array(rest.dropFirst())
        var tree = "."
        if let i = tail.firstIndex(of: "--tree"), i + 1 < tail.count { tree = tail[i + 1] }
        let dir = (absPath(tree) as NSString).appendingPathComponent(".github/workflows")
        let names = ((try? FileManager.default.contentsOfDirectory(atPath: dir)) ?? [])
            .filter { $0.hasSuffix(".yml") || $0.hasSuffix(".yaml") }.sorted()
        let paths = treeFiles(absPath(tree))
        var filters: [(file: String, line: Int, key: String, pattern: String)] = []
        var unread: [(address: String, claim: String)] = []
        for file in names {
            let at = (dir as NSString).appendingPathComponent(file)
            guard let text = readText(at) else {
                unread.append((file, "this file is not text this can read, so the paths it "
                                   + "names were not read either"))
                continue
            }
            let doc = yamlBlock(text)
            if let refused = doc.refused {
                unread.append(("\(file):\(refused.line)",
                               "this reading takes the block subset these files are written "
                             + "in, and stops at what it cannot read exactly: \(refused.why). "
                             + "No claim is made about this file"))
                continue
            }
            // the claim by its address in the document, never by resemblance
            for when in ["push", "pull_request", "pull_request_target"] {
                for key in ["paths", "paths-ignore"] {
                    for item in yamlList(doc.root, ["on", when, key]) {
                        filters.append((file, item.line, key, item.text))
                    }
                }
            }
        }
        // the arithmetic and its wider-than-that-platform matching live in
        // the workflows core, cut out and asked alone by the battery
        let dead = workflowsDeadFilters(filters, paths)
        let all = dead + unread
        // an empty read is a refusal, not a verdict: no workflow at all and
        // workflows stating no filter are two answers, and neither is `holds`
        let nothing = names.isEmpty
            ? "there is no .github/workflows here, so nothing was read"
            : filters.isEmpty && unread.isEmpty
            ? "no workflow here states a path filter under `on`, so there is nothing "
              + "for this to judge" : ""
        let verdict = !all.isEmpty ? "refused" : (nothing.isEmpty ? "holds" : "observed")
        let next = !dead.isEmpty
            ? "open the address above: the filter names a path this tree does not have, so "
              + "the job it guards does not run on the change it was written for"
            : !unread.isEmpty
            ? "that file is written outside the subset this reads exactly. If it is "
              + "ordinary block yaml, that is worth telling us: docs/SECURITY.md says how"
            : nothing.isEmpty
            // ── AND THE ADVICE KNOWS WHERE IT IS STANDING. On a green read
            // this gave the wiring advice to every caller, including the CI
            // step that was that wire, running. The runner's own record
            // answers, not a guess over text.
            ? (ProcessInfo.processInfo.environment["GITHUB_ACTIONS"] == "true"
               ? "this run is that wire: a filter cannot go quiet again without saying so"
               : "wire it into CI: a filter cannot go quiet again without saying so")
            : nothing
        if asJson {
            var pairs: [(String, StatusJSON)] = [
                ("command", .text("import workflows")),
                ("workflows", .raw(String(names.count))),
                ("filters", .raw(String(filters.count))),
                ("files", .raw(String(paths.count))),
                ("verdict", .text(verdict)),
                ("refusals", .list(all.map {
                    .object([("address", .text($0.address)), ("claim", .text($0.claim))]) })),
                ("next", .text(next)),
            ]
            if let ready = commandIn(next) { pairs.append(("command_to_run", .text(ready))) }
            out(statusDumps(.object(pairs), 0) + "\n")
        } else {
            var lines = ["import workflows: "
                         + (all.isEmpty ? verdict : "refused \(all.count)")
                         + " · " + many(filters.count, "filter")
                         + " in " + many(names.count, "workflow")]
            for r in all { lines.append("  \(r.address) · \(r.claim)") }
            lines.append("  next: " + next)
            out(lines.joined(separator: "\n") + "\n")
        }
        exit(all.isEmpty && nothing.isEmpty ? 0 : 1)
    }

    // ── import addresses [--tree DIR]: every declared route, judged at once
    if head == "addresses" {
        mark("addresses-begin")
        let tail = Array(rest.dropFirst())
        var tree = "."
        if let i = tail.firstIndex(of: "--tree"), i + 1 < tail.count { tree = tail[i + 1] }
        let files = treeFiles(absPath(tree))
        var found: [(cls: String, address: String, claim: String)] = []
        var unread: [(address: String, claim: String)] = []
        var judged = 0, sources = 0
        let wfDir = (absPath(tree) as NSString).appendingPathComponent(".github/workflows")
        let wfNames = ((try? FileManager.default.contentsOfDirectory(atPath: wfDir)) ?? [])
            .filter { $0.hasSuffix(".yml") || $0.hasSuffix(".yaml") }.sorted()
        for name in wfNames {
            sources += 1
            let text = theirsText((wfDir as NSString).appendingPathComponent(name),
                                  "a workflow this reads")
            let said = wfAddressFindings(".github/workflows/" + name, text, files)
            found += said.found; unread += said.unread; judged += said.judged
        }
        for place in [".github/dependabot.yml", ".github/dependabot.yaml"] {
            let at = (absPath(tree) as NSString).appendingPathComponent(place)
            guard FileManager.default.fileExists(atPath: at) else { continue }
            sources += 1
            let said = dependabotFindings(place, theirsText(at, "a dependabot config"), files)
            found += said.found; unread += said.unread; judged += said.judged
            break
        }
        for place in [".github/labeler.yml", ".github/labeler.yaml"] {
            let at = (absPath(tree) as NSString).appendingPathComponent(place)
            guard FileManager.default.fileExists(atPath: at) else { continue }
            sources += 1
            let said = labelerFindings(place, theirsText(at, "a labeler config"), files)
            found += said.found; unread += said.unread; judged += said.judged
            break
        }
        for place in ["README.md", "README.rst", "readme.md"] {
            let at = (absPath(tree) as NSString).appendingPathComponent(place)
            guard FileManager.default.fileExists(atPath: at) else { continue }
            sources += 1
            let said = badgeFindings(place, theirsText(at, "the cover this reads"), files)
            found += said.found; judged += said.judged
            break
        }
        let all = found.map { (address: $0.address, claim: $0.claim) } + unread
        let nothing = sources == 0
            ? "nothing here declares an address this reads: no workflows, no dependabot, "
              + "no labeler, no README"
            : judged == 0 && unread.isEmpty
            ? "the declared files state no address this reads, so there is nothing to judge"
            : ""
        let verdict = !all.isEmpty ? "refused" : (nothing.isEmpty ? "holds" : "observed")
        let next = !found.isEmpty
            ? "open the address above: the route names what the tree does not carry, so "
              + "its traffic arrives nowhere"
            : !unread.isEmpty
            ? "that file is written outside the subset this reads exactly. If it is "
              + "ordinary block yaml, that is worth telling us: docs/SECURITY.md says how"
            : nothing.isEmpty
            ? (ProcessInfo.processInfo.environment["GITHUB_ACTIONS"] == "true"
               ? "this run is that wire: a route cannot go quiet again without saying so"
               : "wire it into CI: a route cannot go quiet again without saying so")
            : nothing
        if asJson {
            var pairs: [(String, StatusJSON)] = [
                ("command", .text("import addresses")),
                ("sources", .raw(String(sources))),
                ("addresses", .raw(String(judged))),
                ("files", .raw(String(files.count))),
                ("verdict", .text(verdict)),
                ("refusals", .list(all.map {
                    .object([("address", .text($0.address)), ("claim", .text($0.claim))]) })),
                ("next", .text(next)),
            ]
            if let ready = commandIn(next) { pairs.append(("command_to_run", .text(ready))) }
            out(statusDumps(.object(pairs), 0) + "\n")
        } else {
            var lines = ["import addresses: "
                         + (all.isEmpty ? verdict : "refused \(all.count)")
                         + " · " + many(judged, "route")
                         + " in " + many(sources, "source")]
            for r in all { lines.append("  \(r.address) · \(r.claim)") }
            lines.append("  next: " + next)
            out(lines.joined(separator: "\n") + "\n")
        }
        exit(all.isEmpty && nothing.isEmpty ? 0 : 1)
    }

    // ── import people.csv grants.csv [-o gate.swift]
    let tables = rest.filter { !$0.hasPrefix("-") }
    if tables.count < 2 {
        let note = "import people.csv grants.csv [-o gate.swift]  ·  "
                 + "import codeowners CODEOWNERS --tree . [--policy owners.csv]  ·  "
                 + "import rbac rbac.json  ·  import refs FILE  ·  "
                 + "import workflows [--tree DIR]  ·  import addresses [--tree DIR]"
        let next = "gate import codeowners CODEOWNERS --tree . reads ownership you "
                 + "already keep, and writes one small file you commit"
        if asJson {
            out("{\n  \"command\": \"import\",\n  \"asks\": true,\n"
                + "  \"note\": " + jsonString(note) + ",\n"
                + "  \"next\": " + jsonString(next) + "\n}\n")
        } else {
            out("usage: " + note + "\n  next: " + next + "\n")
        }
        exit(0)
    }
    let outPath = after("-o") ?? "gate.swift"
    mark("tables-begin")
    let said = importWorld(tables[0], tables[1], outPath)
    if asJson {
        out(statusDumps(.object([
            ("command", .text("import")),
            ("world", .text(outPath)),
            ("people", .raw(String(said.people))),
            ("grants", .raw(String(said.grants))),
            ("verdict", .text(said.verdict)),
            ("refusals", .list(said.refusals.map {
                .object([("address", .text($0.address)), ("claim", .text($0.claim))]) })),
            ("judge_ms", said.judgeMs.map { .raw(floatRepr($0)) } ?? .null),
            ("wall_ms", .raw(String(said.wallMs))),
        ]), 0) + "\n")
    } else {
        var lines = ["import: " + (said.verdict == "holds" ? "holds"
                                   : "refused \(said.refusals.count)")
                     + (said.judgeMs.map { " · " + floatRepr($0) + " ms" } ?? "")]
        for r in said.refusals { lines.append("  \(r.address) · \(r.claim)") }
        out(lines.joined(separator: "\n") + "\n")
    }
    exit(said.verdict == "holds" ? 0 : 1)
}

// ── bare FILE [NAME ...] [--full]: the world with the ceremony stripped,
// printed by the tool rather than by hand. A projection over one source: the
// file on disk stays the full Swift it was, git keeps it, swiftc reads it, and
// this writes nothing at all.
if args.first == "bare" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    let paths = rest.filter { !$0.hasPrefix("-") }
    if paths.isEmpty {
        let note = "bare FILE [NAME ...] [--full]  ·  the same world with the ceremony stripped"
        let next = "name a world file: `gate bare gate.swift`, or `gate bare "
                 + "stdlib/verbs.swift` for a page off the shelf"
        if asJson {
            out("{\n  \"command\": \"bare\",\n  \"asks\": true,\n"
                + "  \"note\": " + jsonString(note) + ",\n"
                + "  \"next\": " + jsonString(next) + "\n}\n")
        } else {
            out("usage: " + note + "\n  next: " + next + "\n")
        }
        exit(0)
    }
    let src = paths[0]
    if !FileManager.default.fileExists(atPath: src) {
        cannot("no file at " + src,
               "name a world file this judges, or run `gate demo` for a repository that has one")
    }
    let text = theirsText(src, "the world to strip")
    if rest.contains("--full") {
        let note = "the whole text, as it sits on disk and as swiftc reads it"
        let next = "`gate bare " + src + "` prints the same world stripped"
        if asJson {
            var pairs: [(String, StatusJSON)] = [
                ("command", .text("bare")), ("file", .text(src)), ("full", .text(text)),
                ("mutates", .raw("false")), ("note", .text(note)), ("next", .text(next)),
            ]
            if let ready = commandIn(next) { pairs.append(("command_to_run", .text(ready))) }
            out(statusDumps(.object(pairs), 0) + "\n")
        } else {
            var lines = text.hasSuffix("\n")
                ? String(text.reversed().drop(while: { $0 == "\n" }).reversed())
                : text
            lines += "\n\n  " + note + "\n  next: " + next + "\n"
            out(lines)
        }
        exit(0)
    }
    let only = Array(paths.dropFirst())
    let parsed = worldParse(src)
    if !only.isEmpty {
        var known = Set((parsed.at("declarations")?.asList ?? [])
            .compactMap { $0.at("name")?.asText })
        for (n, _) in parsed.at("topAliases")?.asObject ?? [] { known.insert(n) }
        let missing = only.filter { !known.contains($0) }
        if !missing.isEmpty {
            cannot(src + " declares no " + (missing.count == 1 ? "record" : "records") + " "
                   + missing.joined(separator: ", "),
                   "`gate bare " + src + "` prints every record it does declare")
        }
    }
    let lines = bareLines(parsed, text, only)
    let note = "a projection: the file on disk is unchanged full Swift, and "
             + "`gate bare " + src + " --full` prints it"
    let next = "run `gate serve` to edit this view and watch the verdict move"
    if asJson {
        var pairs: [(String, StatusJSON)] = [
            ("command", .text("bare")), ("file", .text(src)),
            ("only", only.isEmpty ? .null : .list(only.map { .text($0) })),
            ("lines", .list(lines.map { .text($0) })),
            ("mutates", .raw("false")), ("note", .text(note)), ("next", .text(next)),
        ]
        if let ready = commandIn(next) { pairs.append(("command_to_run", .text(ready))) }
        out(statusDumps(.object(pairs), 0) + "\n")
    } else {
        out((lines + ["", "  " + note, "  next: " + next]).joined(separator: "\n") + "\n")
    }
    exit(0)
}

// ── report [-o report.html]: the printable audit page, the world's tables plus
// the verdict. No server: one self-contained page, mailable to an audit.
//
// AND NOTHING LANDS IN SOMEBODY'S REPOSITORY UNASKED. This defaulted to
// `report.html` once and dropped the file into the working copy of anybody who
// typed the verb to see what it did, while the page beside it promised that
// unless you ask for it by name with `-o`, your repository is left as it was.
if args.first == "report" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    let outPath = rest.firstIndex(of: "-o").flatMap { $0 + 1 < rest.count ? rest[$0 + 1] : nil }
    loadStatusShelf()
    let w = discoverWorld()
    ensureWorld(w)
    // a page is printed OUT OF a world, and this read the facts without asking
    // whether there is one: in a repository with none it opened nothing and raised
    guard let facts = w.facts, FileManager.default.fileExists(atPath: facts) else {
        cannot("report prints a world and its verdict as one page, and there is no world here",
               "run `gate init .` to start one, or `gate demo` for a repository to look "
               + "at. `report -o audit.html` writes the page; without `-o` nothing is written")
    }
    let text = readText(facts) ?? ""
    let (people, grants) = worldRows(text)
    let said = courtSays([facts])
    let refusals = refineAddresses(text, judgedRefusals(said),
                                   (facts as NSString).lastPathComponent)
    let holds = said.contains("THE JUDGE holds")
    let judgeMs = matches("([\\d.]+) ms", said).compactMap { $0.first }.last
    func table(_ rows: [[(String, String)]], _ cols: [String]) -> String {
        let head = cols.map { "<th>\($0)</th>" }.joined()
        let body = rows.map { row in
            "<tr>" + cols.map { c in
                "<td>" + (row.first(where: { $0.0 == c })?.1 ?? "") + "</td>" }.joined() + "</tr>"
        }.joined()
        return "<table><tr>\(head)</tr>\(body)</table>"
    }
    let verdictHtml = holds && refusals.isEmpty
        ? "<p class='ok'>holds: every claim checked</p>"
        : "<ul class='bad'>"
          + refusals.map { "<li><code>\($0.address)</code> · \($0.claim)</li>" }.joined()
          + "</ul>"
    // who may do what, and when that last changed: an audit asks for both, and
    // git already answers the second out of the policy's own history
    let policy = readPolicy(w)
    var policyHtml = ""
    if !policy.ids.isEmpty || !policy.rules.isEmpty {
        var rows: [[(String, String)]] = policy.rules.sorted { $0.action < $1.action }
            .map { [("what", "\($0.action) requires"), ("who", $0.rank)] }
        rows += policy.ids.sorted { $0.mail < $1.mail }
            .map { [("what", $0.mail), ("who", $0.who)] }
        let base = w.facts.map { (absPath($0) as NSString).deletingLastPathComponent }
            ?? FileManager.default.currentDirectoryPath
        let journal = repoJournal(base, journalWorld(base), scope: "world", limit: 50,
                                  onlyMe: false)
        let who = identities(base)
        let pf = policyPathOf(w).map { ($0 as NSString).lastPathComponent } ?? ""
        let changes = journal.commits.filter { !pf.isEmpty && $0.files.contains(pf) }
        let hist = changes.prefix(10).map { c in
            "<li><code>\(String(c.hash.prefix(8)))</code> \(String(c.when.prefix(10))) · "
            + (who[c.email] ?? c.email) + " · \(c.subject)</li>"
        }.joined()
        policyHtml = "<h2>Policy</h2>" + table(rows, ["what", "who"])
            + (hist.isEmpty ? "<p>Stated, and unchanged in the last 50 commits.</p>"
                            : "<p>Last changed:</p><ul>" + hist + "</ul>")
    }
    let found = repoFindings(200)
    var findingsHtml = ""
    if !found.isEmpty {
        let items = found.map { f in
            "<li>\(f.sentence)<br><small>"
            + (f.kind == "judged" ? "checked by the judge"
                                  : "read from git history, not a verdict")
            + " · \(f.evidence)</small></li>"
        }.joined()
        findingsHtml = "<h2>Findings</h2><ul class='findings'>\(items)</ul>"
    }
    let html = """
        <!-- printed by gate report; the table is read from the world, never stored -->
        <meta charset="utf-8"><title>gate report</title>
        <style>
        body{font:14px/1.5 -apple-system,sans-serif;max-width:60em;margin:2em auto;padding:0 1em;color:#1d1d1f}
        table{border-collapse:collapse;margin:1em 0}td,th{border:1px solid #d2d2d7;padding:.3em .8em;text-align:left}
        th{background:#f5f5f7}.ok{color:#248a3d}.bad li{color:#c4453b;margin:.3em 0}code{background:#f5f5f7;padding:0 .3em}
        .findings li{margin:.6em 0}.findings small{color:#8e8e93}
        </style>
        <h1>gate report</h1>
        <p>\(many(people.count, "person", "people")) · \(many(grants.count, "grant")) · judged in \(judgeMs.map { floatRepr($0) + " ms" } ?? "an unread clock")</p>
        <h2>Verdict</h2>\(verdictHtml)
        <h2>People</h2>\(table(people, ["id", "rank", "home", "site", "given", "family", "born"]))
        <h2>Grants</h2>\(table(grants.map { [("who", $0.0), ("doc", $0.1)] }, ["who", "doc"]))
        \(policyHtml)
        \(findingsHtml)

        """.replacingOccurrences(of: "\n        ", with: "\n")
        .trimmingCharacters(in: CharacterSet(charactersIn: " "))
    if let path = outPath { oursWrite(path, "the page", html) }
    let note = outPath == nil
        ? "nothing written: name a file to keep this page. `gate report -o report.html`"
        : nil
    if asJson {
        var pairs: [(String, StatusJSON)] = [
            ("command", .text("report")),
            ("wrote", outPath.map { .text($0) } ?? .null),
            ("people", .raw(String(people.count))),
            ("grants", .raw(String(grants.count))),
            ("verdict", .text(holds && refusals.isEmpty ? "holds" : "refused")),
            ("judge_ms", judgeMs.map { .raw(floatRepr($0)) } ?? .null),
            ("refusals", .list(refusals.map {
                .object([("address", .text($0.address)), ("claim", .text($0.claim))]) })),
            ("note", note.map { .text($0) } ?? .null),
            ("mutates", .raw(outPath != nil ? "true" : "false")),
        ]
        // and no `command_to_run` beside it: the other carrier lifts one out of
        // `next`, `then` or `try`, and this answer carries none of the three.
        // A note is a sentence about what did not happen, not a step to take.
        out(statusDumps(.object(pairs), 0) + "\n")
    } else {
        let head = holds && refusals.isEmpty ? "holds" : "refused \(refusals.count)"
        var lines = ["report: " + head
                     + (judgeMs.map { " · " + floatRepr($0) + " ms" } ?? "")]
        for r in refusals { lines.append("  \(r.address) · \(r.claim)") }
        if let n = note { lines.append("  note: " + n) }
        out(lines.joined(separator: "\n") + "\n")
    }
    exit(holds && refusals.isEmpty ? 0 : 1)
}

// ── findings [--md] [--history] [N]: what is true of this repository, in
// sentences; with --history, what has been true of one pair over its commits.
if args.first == "findings" {
    let rest = Array(args.dropFirst()).filter { $0 != "--json" }
    let asJson = args.contains("--json")
    let n = rest.first(where: { !$0.isEmpty && $0.allSatisfy { $0.isNumber } }).flatMap { Int($0) }
    let wantsMarkdown = rest.contains("--md")
    if rest.contains("--history") {
        var policyName: String? = nil
        if let i = rest.firstIndex(of: "--policy"), i + 1 < rest.count {
            policyName = (rest[i + 1] as NSString).lastPathComponent
        }
        // ── AND A DIRECTORY THAT IS NOT A REPOSITORY IS TOLD SO. This read
        // nought commits there and answered `0 commits carry the pair, read from
        // git` beside no git at all: a true-sounding sentence about a thing that
        // is not there. A repository with no commits yet is a different answer.
        loadStatusShelf()
        let w0 = discoverWorld()
        let base = w0.facts.map { (absPath($0) as NSString).deletingLastPathComponent }
            ?? FileManager.default.currentDirectoryPath
        if runGit(["rev-parse", "--git-dir"], base)
            .trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            cannot("this walks a repository's commits, and this directory is not one",
                   "run it inside a git repository, or ask `gate findings` for what is "
                   + "true here now")
        }
        let (rows, whole) = historyDivergence(n ?? 200, policyName: policyName)
        // ── AND WHAT A FALL IS, SAID WHERE ONE IS VISIBLE. A curve that drops
        // reads like a thing that was fixed and stays fixed, and it is not: with
        // no court in the repository, a drop is somebody who compared the two
        // records by hand. That comparison is recorded nowhere, so nothing
        // carries it, and the level comes back.
        var fell = false
        for (i, r) in rows.enumerated() where i > 0 {
            if let a = rows[i - 1].divergences, let b = r.divergences, b < a { fell = true }
        }
        // the fold: when it parted, how long ago, and how much has gone past
        var markIndex: Int? = nil
        for (i, r) in rows.enumerated() where i > 0 {
            if rows[i - 1].divergences == 0 && (r.divergences ?? 0) > 0 { markIndex = i }
        }
        let standing = rows.last?.divergences
        let readRows = rows.enumerated().filter { $0.element.read }
        var parted: [(String, StatusJSON)]? = nil
        var partedSaid: String? = nil
        if let standing = standing, standing > 0,
           markIndex != nil || (readRows.first.map { ($0.element.divergences ?? 0) > 0 } ?? false) {
            let beyond = markIndex == nil
            let at = markIndex ?? readRows.first!.offset
            let mark = rows[at]
            let since = Array(rows[at...])
            let days = daysSince(mark.when)
            // ── AND NEVER AGREED IS NOT THE SAME AS PARTED LONG AGO. If the walk
            // reached the start of this line, there is no older commit for the
            // parting to hide in, and the honest reading is that the two records
            // have not agreed since the pair was written.
            let said = beyond
                ? "apart at every one of the "
                  + many(since.filter { $0.read }.count, "commit") + " this run read, "
                  + "back to \(mark.when), \(days) days ago; "
                  + (whole ? "the two records have not agreed since the pair was written"
                           : "it parted before this run's reading")
                  + "; \(standing) still apart today"
                : "parted at \(mark.at) on \(mark.when): \(days) days and "
                  + many(since.count - 1, "commit") + " carrying the pair ago; "
                  + "\(standing) still apart today"
            partedSaid = said
            parted = [("at", beyond ? .null : .text(mark.at)),
                      ("when", .text(mark.when)),
                      ("days", .raw(String(days))),
                      ("commits_since", .raw(String(since.count - 1))),
                      ("standing", .raw(String(standing))),
                      ("beyond", .raw(beyond ? "true" : "false")),
                      ("never", .raw(beyond && whole ? "true" : "false"))]
            parted!.append(("said", .text(said)))
        }
        let measure = "divergences of the pair's judged image at each commit: "
                    + "claims the court refuses, plus rules that address nothing. "
                    + "A divergence of the image is a divergence of the pair; the "
                    + "distance between the two records is not measured here"
        let next = rows.isEmpty
            ? "no commit in this history carries the file this reads"
            : "run `gate import codeowners` to see one of these commits translated in full"
        let shape = fell
            ? "a fall here is somebody comparing the two records by hand. "
              + "That comparison is recorded nowhere, so nothing carries it "
              + "and the level comes back: with no court, nothing is obliged "
              + "to fall and nothing holds a fall either"
            : nil
        if asJson {
            var pairs: [(String, StatusJSON)] = [
                ("command", .text("findings history")),
                ("history", .list(rows.map { r in
                    .object([("at", .text(r.at)), ("when", .text(r.when)),
                             ("rules", .raw(String(r.rules))), ("file", .text(r.file)),
                             ("refusals", r.refusals.map { .raw(String($0)) } ?? .null),
                             ("unmatched", .raw(String(r.unmatched))),
                             ("divergences", r.divergences.map { .raw(String($0)) } ?? .null),
                             ("judged", .raw(r.judged ? "true" : "false")),
                             ("read", .raw(r.read ? "true" : "false"))]) })),
                ("parted", parted.map { .object($0) } ?? .null),
                ("markdown", wantsMarkdown ? .text(historyMarkdown(rows, partedSaid)) : .null),
                ("shape", shape.map { .text($0) } ?? .null),
                ("measure", .text(measure)),
                ("commits", .raw(String(rows.count))),
                ("next", .text(next)),
                ("mutates", .raw("false")),
            ]
            if let ready = commandIn(next) { pairs.append(("command_to_run", .text(ready))) }
            out(statusDumps(.object(pairs), 0) + "\n")
        } else {
            var lines = ["findings history: " + many(rows.count, "commit") + " "
                         + (rows.count == 1 ? "carries" : "carry") + " the pair, read from git"]
            // the fold first, because it is the finding and the rows are its evidence
            if let said = partedSaid { lines.append("  " + said) }
            lines.append("  " + measure)
            for r in rows {
                let said = r.divergences == nil ? "not read: no verdict in the reply"
                    : r.divergences == 0 ? "in agreement"
                    : "\(r.divergences!) divergence" + (r.divergences! == 1 ? "" : "s")
                lines.append("  \(r.at) \(r.when)  "
                             + said.padding(toLength: max(22, said.count), withPad: " ",
                                            startingAt: 0)
                             + " " + many(r.rules, "rule")
                             + (r.judged ? "" : ", no policy: only unmatched rules can show"))
            }
            // where the pair was read, said once rather than on every row, plus
            // every move: a file that changed place is the same pair, and a
            // reader who sees only the last path cannot tell that from a pair
            // that was born there
            var moves: [(String, String, String)] = []
            for r in rows where moves.isEmpty || moves[moves.count - 1].0 != r.file {
                moves.append((r.file, r.at, r.when))
            }
            if !moves.isEmpty {
                lines.append("  read from " + moves[0].0
                             + moves.dropFirst().map { ", moved to \($0.0) at \($0.1) \($0.2)" }
                                .joined())
            }
            if let shape = shape { lines.append("  " + shape) }
            if wantsMarkdown {
                lines.append("")
                lines.append(historyMarkdown(rows, partedSaid))
            }
            lines.append("  next: " + next)
            out(lines.joined(separator: "\n") + "\n")
        }
        exit(0)
    }
    let found = repoFindings(n ?? 400)
    let judged = found.filter { $0.kind == "judged" }.count
    let next = "run `gate status`: what is judged answers in milliseconds, and this does not"
    if asJson {
        var pairs: [(String, StatusJSON)] = [
            ("command", .text("findings")),
            ("findings", .list(found.map {
                .object([("kind", .text($0.kind)), ("subject", .text($0.subject)),
                         ("sentence", .text($0.sentence)), ("evidence", .text($0.evidence))]) })),
            ("next", .text(next)),
            ("judged", .raw(String(judged))),
            ("observed", .raw(String(found.count - judged))),
            ("markdown", wantsMarkdown ? .text(findingsMarkdown(found)) : .null),
            ("mutates", .raw("false")),
        ]
        if let ready = commandIn(next) { pairs.append(("command_to_run", .text(ready))) }
        out(statusDumps(.object(pairs), 0) + "\n")
    } else {
        var lines: [String] = []
        if found.isEmpty {
            lines.append("findings: nothing to report yet")
        } else {
            lines.append("findings: \(found.count) · \(judged) checked by the judge, "
                         + "\(found.count - judged) read from git")
            for x in found {
                let tag = x.kind == "judged" ? "checked"
                    : (x.kind == "offer" ? "offer  " : "read   ")
                lines.append("  [\(tag)] \(x.sentence)")
                lines.append("           \(x.evidence)")
            }
        }
        if wantsMarkdown {
            lines.append("")
            lines.append(findingsMarkdown(found))
        }
        lines.append("  next: " + next)
        out(lines.joined(separator: "\n") + "\n")
    }
    exit(0)
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
// ── ONE RAW OPEN, WITH THE MODE IN THE PLATFORM'S OWN SPELLING. ucrt's
// `_open` VALIDATES its third argument: any bit outside _S_IREAD|_S_IWRITE
// (0x0180) is an invalid parameter, and ucrt's handler does not hand back -1,
// it __fastfail()s the process, which is the 0xC0000409 this hunt chased.
// `0o644` carries such bits, so every write door of this vein was a fall
// waiting for its first caller on that platform: v0.2.0's import crashes on
// it. And _O_BINARY (0x8000) keeps the CRT from spelling \n as \r\n inside
// what this tool prints: the bytes written are the bytes given.
func rawOpen(_ path: String, _ flags: Int32) -> Int32 {
    #if canImport(WinSDK)
    return open(path, flags | 0x8000, Int32(0x0180))
    #else
    return open(path, flags, 0o644)
    #endif
}

// ── A TRAIL, BECAUSE A PROCESS THAT FALLS OVER CANNOT SPEAK. A trap on that
// platform is a fail fast: it takes both channels with it, so everything the
// verb was going to SAY is lost and only what it has already WRITTEN survives.
// Asked by `GATE_TRACE`, a verb leaves one word per step in that file, and
// whoever picks the wreck up reads the last one. Off unless the file is named,
// appended without buffering, and it says nothing about anybody's world: it is
// this tool's own state, in a file, which is where this project keeps state.
func mark(_ step: String) {
    guard let where_ = ProcessInfo.processInfo.environment["GATE_TRACE"],
          !where_.isEmpty else { return }
    let fd = rawOpen(where_, O_WRONLY | O_CREAT | O_APPEND)
    guard fd >= 0 else { return }
    let bytes = Array((step + "\n").utf8)
    _ = bytes.withUnsafeBufferPointer { buf -> Int in
        #if canImport(WinSDK)
        return Int(write(fd, buf.baseAddress, UInt32(buf.count)))
        #else
        return write(fd, buf.baseAddress, buf.count)
        #endif
    }
    close(fd)
}

func oursWrite(_ path: String, _ what: String, _ text: String) {
    mark("write:" + lastName(path))
    let fd = rawOpen(path, O_WRONLY | O_CREAT | O_TRUNC)
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
    _ = bytes.withUnsafeBufferPointer { buf -> Int in
        // the count is a machine word where this call comes from libc and a
        // 32-bit unsigned where it comes from the windows runtime
        #if canImport(WinSDK)
        return Int(write(fd, buf.baseAddress, UInt32(buf.count)))
        #else
        return write(fd, buf.baseAddress, buf.count)
        #endif
    }
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
    p.executableURL = URL(fileURLWithPath: toolPath("git"))
    p.arguments = ["-C", root, "show", spec]
    let pipe = Pipe(), quiet = Pipe()
    p.standardOutput = pipe
    p.standardError = quiet
    do { try p.run() } catch { return nil }
    let said = pipe.fileHandleForReading.readDataToEndOfFile()
    quiet.fileHandleForReading.readDataToEndOfFile()
    waitDone(p)
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
        let d = tempRoot() + "/gate-badge-" + mark.sha
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

// ── my: your personal world, where it is, and its verdict WITH the shared
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
// ── THE TWO SIDES, PRINTED. What a contract states and what a carrier claims
// are two texts built out of two documents, and the building is the whole of
// the act: the door around it names files and writes rows. Pulled out so the
// demo that makes a pair prints it with the verb's own hand rather than a
// second one of its own.
func contractWorld(_ spec: Said) -> (world: String, declares: Int) {
    let fields = contractFields(spec).filter { $0.shape != nil }
    var lines = [shelfSection("declare",
                              "// ── what a contract side is printed under begins here ──\n")
                 + shelfPage("forms-contract"), ""]
    for f in fields {
        let rec = "F_" + sanitized(f.route) + "_" + sanitized(f.field)
        lines += ["// " + f.route + " · " + f.field,
                  "public enum " + rec + ": Declared {",
                  "    public typealias Of = " + (f.shape ?? ""), "}"]
    }
    return (lines.joined(separator: "\n") + "\n", fields.count)
}

func carrierWorld(_ decl: Said) -> (world: String, declares: Int, who: String) {
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
    for (i, c) in carries.enumerated() {
        let route = c.at("route")?.asText ?? "", field = c.at("field")?.asText ?? ""
        let rec = "F_" + sanitized(route) + "_" + sanitized(field)
        let mineName = c.at("mine")?.asText
        lines.append("// " + route + " · " + field
                     + (mineName.map { " (it calls it " + $0 + ")" } ?? ""))
        lines.append("public typealias Carry_\(i) = Carries<" + who + ", " + rec + ", "
                     + (c.at("as")?.asText ?? "") + ">")
    }
    return (lines.joined(separator: "\n") + "\n", carries.count, who)
}

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
        // ── AND THESE TWO READ THROUGH THE DOOR NOW. They spelled a path with
        // `standardizingPath`, which this project forbids: it resolves a
        // symlink on one platform, folds a tilde it was never given, and knows
        // nothing of a drive letter. The relative text and the judgment come
        // from the same readers every other path here goes through.
        let base = absPath(root)
        let rel = relPath(absPath(path), base)
        // a row may not point out of the world that makes it: the other carrier
        // raises here, and a row about somebody else's tree is a claim this
        // world cannot answer for
        if leavesRoot(absPath(path), base) {
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
        let said = contractWorld(spec)
        (world, declares) = (said.world, said.declares)
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
        let against = decl.at("against")
        let revision = against?.at("revision")?.asText
        let said = carrierWorld(decl)
        (world, declares) = (said.world, said.declares)
        let who = said.who
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
        // ── AND A FILE THIS CANNOT READ IS NOT A FILE THIS MAY REWRITE. Every
        // shape below is careful with somebody else's bytes: the other keys
        // travel, a row that is not a record is refused, a `diverges` that is
        // not a list is refused. A file that is not json at all fell past all
        // three and was written over from nothing, which is the one outcome
        // this verb's own care exists to prevent: the care was spelled for
        // files it could read, and silence for the rest.
        guard readSaid(text) != nil else {
            cannot(path + " is not the json this verb keeps, so rewriting it would "
                   + "take whatever it does hold with it",
                   "this verb keeps every key it did not put there, and it can only do "
                   + "that for a file it can read: move that one aside and let this write "
                   + "a new one, or name another with `-o`")
        }
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
    let nextSaid = "point a tracker export at it: `gate attention … --known " + path
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
    mark("spawn:git")
    let p = Process()
    p.executableURL = URL(fileURLWithPath: toolPath("git"))
    p.arguments = ["-C", rootDir, "cat-file", "--batch"]
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
    waitDone(p)
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
    mark("spawn:git")
    let p = Process()
    p.executableURL = URL(fileURLWithPath: toolPath("git"))
    p.arguments = ["-C", rootDir, "log", "--reverse", "-p", "--no-color",
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
                   + "\(median): this exits non-zero by your rule, not by a verdict")
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

// ── AND THE STEP AFTER THE HOOK IS WRITTEN, NOT DESCRIBED. The hook holds a
// commit on the machine that makes it; CI holds what arrives, which is the
// half a reviewer trusts. That step was a paragraph somebody had to translate
// into their own workflow, and a paragraph is where a reader stops. It is a
// file this verb writes now, the same way the hook is: the tool that answers
// `status` is the tool that says how to run `status` on a runner.
//
// The binary is taken from the release rather than built there: a runner with
// no toolchain is the ordinary case, and one download is the whole setup. The
// hash is deliberately not pinned here. Linkers are not byte-stable, so a
// hash pinned in somebody's workflow would be a promise this project cannot
// keep across a rebuild; the honest check is the rebuild itself, and
// docs/DETAILS.md carries that recipe.
let INIT_CI = """
# gate: the claims in this repository are judged on every push.
#
# What this does: takes one binary from the latest release and asks it for a
# verdict. No install, no toolchain, no service. It exits non-zero on a
# refusal, and the refusal names the file and the line.
#
# Written by `gate init --ci`. Yours to edit: this is your workflow now.
name: gate
on: [push, pull_request]

jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: take gate
        run: |
          curl -fsSL -o gate \
            https://github.com/DanielSwift1992/gate/releases/latest/download/gate-linux-x86_64
          chmod +x gate
      - name: the claims hold
        run: ./gate status

"""

func copyItem(_ src: String, _ dst: String) {
    try? FileManager.default.removeItem(atPath: dst)
    try? FileManager.default.copyItem(atPath: src, toPath: dst)
}

func vendorInto(_ rootDir: String) -> (carried: [String], digest: String?, shim: String) {
    // the tool travels WITH the repository, the way ./gradlew does: one person
    // commits .gate/, and everybody who pulls has it
    let here = toolRoot()
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
    // ── AND WHAT IS CARRIED IS WHAT JUDGES. This carried the other carrier's
    // file, which was the tool while it lived; the tool is this binary now, so
    // that is what a repository takes in hand. The node port travels with it
    // because the bench's parse route is still asked of it, and because a
    // platform this binary was not built for still has a court that way.
    for rel in ["bin/judge.js", "bin/judge-where.js", "web/ui.html",
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
    // the tool itself, and its digest: the court is compiled into it, so the
    // hash a vendored README carries names the thing that judges
    for name in ["gate-cli", "gate-cli.exe"] {
        let mine = (here as NSString).appendingPathComponent("bin/" + name)
        if FileManager.default.fileExists(atPath: mine) {
            let there = (dst as NSString).appendingPathComponent("bin/" + name)
            copyItem(mine, there)
            try? FileManager.default.setAttributes([.posixPermissions: 0o755],
                                                   ofItemAtPath: there)
            carried.append("bin/" + name)
        }
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
    let shim = (rootDir as NSString).appendingPathComponent("gatew")
    try? ("#!/bin/sh\n# gate, carried by this repository. Nothing to install.\n"
          + "HERE=\"$(cd \"$(dirname \"$0\")\" && pwd)\"\n"
          + "for C in \"$HERE/.gate/bin/gate-cli\" \"$HERE/.gate/bin/gate-cli.exe\"; do\n"
          + "    [ -x \"$C\" ] && exec \"$C\" \"$@\"\ndone\n"
          + "echo \"gate: the copy in .gate carries no binary for this platform\" >&2\n"
          + "echo \"  take one from the releases, or build with bin/build-cli.sh\" >&2\n"
          + "exit 1\n")
        .write(toFile: shim, atomically: false, encoding: .utf8)
    try? FileManager.default.setAttributes([.posixPermissions: 0o755], ofItemAtPath: shim)
    let readme = "# gate, carried by this repository\n\n"
        + "Run `./gatew status`. Nothing to install: this directory is the tool\n"
        + "itself, pinned by the commit that added it, so every clone judges with\n"
        + "the same judge and an old commit is judged by the judge it was written\n"
        + "with.\n\n"
        + "judge sha256: \(digest ?? "not recorded")\n\n"
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
    let wantCI = a.contains("--ci")
    a = a.filter { $0 != "--vendor" && $0 != "--ci" }
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
    // the CI step, written where that platform reads it. A file already there
    // is left alone: this hands somebody a starting point, it does not own
    // their pipeline.
    var ciRel: String? = nil
    if wantCI {
        let rel = ".github/workflows/gate.yml"
        let at = (rootDir as NSString).appendingPathComponent(rel)
        if FileManager.default.fileExists(atPath: at) {
            ciRel = rel
        } else {
            try? FileManager.default.createDirectory(
                atPath: (at as NSString).deletingLastPathComponent,
                withIntermediateDirectories: true)
            do {
                try INIT_CI.write(toFile: at, atomically: false, encoding: .utf8)
                made.append(rel)
                ciRel = rel
            } catch {
                cannot("the CI step could not be written at \(rel): "
                       + error.localizedDescription.lowercased(),
                       "check the folder is writable, or print it yourself: the same "
                       + "text is what `gate init --ci` writes")
            }
        }
    }
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
    if let ci = ciRel {
        // a file that needs a commit to mean anything is said in words, not
        // left to be counted among "created 6 files"
        lines.append("  ci: " + ci + (made.contains(ci)
            ? ", written for you: commit it and every push is judged, "
              + "one download and no toolchain on the runner"
            : ", left as it was: a step is already there, and this verb does "
              + "not own your pipeline"))
    }
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
    if leavesRoot(absPath(path), d) || leavesWorldHere(rel, d) {
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

    func answer(_ pairs: [(String, StatusJSON)], _ human: [String],
                _ code: Int32 = 0) -> Never {
        if asJson { out(statusDumps(.object(pairs), 0) + "\n") }
        else { out(human.joined(separator: "\n") + "\n") }
        exit(code)
    }
    // ── AND A NAMED ASK THAT WAS NOT DONE EXITS LIKE ONE. Typing the verb
    // bare is a question and answers nought; naming a file, a revision or a
    // range and being turned away is a refusal, and it left nought too, so a
    // hook or a Makefile step reading only the code was told the work was
    // done. The words are unchanged: what changes is what a caller reads.
    func asks(_ note: String, _ next: String, asked: Bool = true) -> Never {
        answer([("command", .text(word)), ("asks", .raw("true")),
                ("note", .text(note)), ("next", .text(next))],
               ["usage: " + note, "  next: " + next], asked ? 1 : 0)
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
                 : "a file you took from somewhere, at the revision you took it at",
                 asked: false)
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
                 "gate \(word): what is in it")
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
                 "gate \(word) \(path).swift: declare the copy you have, or move it "
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
        // a flag left without its word named nothing, and this said so with
        // python's word for nothing: `None` is not a court, and it is not a
        // word this tool speaks either
        cannot(role.map { "`\($0)` is not a court anything here reads" }
               ?? "`--role` names the court that reads a row, and it was given without one",
               "a row says what it is for: "
               + STATUS_ROLES.map { "`\($0.0)`: \($0.1)" }.joined(separator: " · "))
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
               "gate theirs \((path as NSString).lastPathComponent) --at REV: a commit, a "
               + "tag, a release: whatever the source calls the thing you actually took")
    }
    let here = absPath(".")
    let outside = leavesRoot(absPath(path), here)
    if outside && foundsWorld(path) {
        asks("\(path) is not inside the world here, and there is no world around it",
             "a world is founded where you stand: run this from the directory that "
             + "world is in, or bring the file into this one. A world judges what "
             + "is in it")
    }
    let (rows2, _) = layoutRowsFull(worldRootFor(path))
    let rel2 = relPath(absPath(path), worldRootFor(path))
    if let said = rows2.first(where: { $0.path == rel2 }) {
        asks("\(rel2) is already declared, as `\(said.name ?? "a row with no name")` "
             + "(\(said.source), \(said.role ?? "no court"))",
             "gate \(word) \(rel2) --forget, then say it again: a file is declared "
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
        answer(minePairs(file, mp!, role!, roleMeans),
               ["\(word): \(file) · written down in \(mp!)",
                "  role `\(role!)`: \(roleMeans)",
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
            "  role `\(role!)`: \(roleMeans)",
            "  next: " + nextSaid])
}

// ── log: the repository's own history, projected and never judged ──
//
// A commit is closed iff it is reachable from the default branch. The world's
// history is git's own filtering by pathspec over the files the layout declares,
// which is why this needed the reader above; asking for a world's history where
// no file is declared one narrows nothing, and the line says so rather than
// printing the repository under the word `the world`.
// the journal as an object, said once for both surfaces. This was the last
// answer in this vein assembled by concatenating text, and a shape written that
// way cannot be printed a second way without being written twice.
// ── AND THE LAST MILE IS THE DOOR'S. `command_to_run` is added where the
// answer is printed, the way the other carrier's main does it; the bench asks
// for the object alone.
func journalPairs(_ journal: Journal, scope: String, limit: Int, onlyMe: Bool,
                  world: Set<String>, who: [String: String], nextSaid: String,
                  lastMile: Bool) -> [(String, StatusJSON)] {
    var pairs: [(String, StatusJSON)] = [
        ("command", .text("log")),
        ("default_branch", journal.branch.isEmpty ? .null : .text(journal.branch)),
        ("scope", .text(scope)),
        ("limit", .raw(String(limit))),
        ("mine_only", .raw(onlyMe ? "true" : "false")),
        ("narrowed", .raw(journal.narrowed ? "true" : "false")),
        ("next", .text(nextSaid)),
        ("me", .text(journal.me)),
        ("world_files", .list(world.sorted().map { .text($0) })),
        ("commits", .list(journal.commits.map { c in
            .object([
                ("hash", .text(c.hash)),
                ("short", .text(String(c.hash.prefix(8)))),
                ("email", .text(c.email)),
                ("person", who[c.email].map { StatusJSON.text($0) } ?? .null),
                ("when", .text(c.when)),
                ("subject", .text(c.subject)),
                ("files", .list(c.files.map { .text($0) })),
                ("touches_world", .raw(c.touches ? "true" : "false")),
                ("closed", c.closed.map { StatusJSON.raw($0 ? "true" : "false") } ?? .null),
            ])
        })),
    ]
    if lastMile, let ready = commandIn(nextSaid) {
        pairs.append(("command_to_run", .text(ready)))
    }
    return pairs
}

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

    let world = journalWorld(here)
    _ = (rows, manifest, facts)

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

    let journal = repoJournal(base, world, scope: scope, limit: limit, onlyMe: onlyMe)
    let (commits, branch, me, narrowed) = (journal.commits, journal.branch,
                                           journal.me, journal.narrowed)
    let nextSaid = world.isEmpty
        ? "run `gate demo` for a repository to look at, or drop a table you already export "
          + "into tables/ and run `gate status`"
        : "run `gate status` to have the judge read what these commits changed"

    if asJson {
        out(statusDumps(.object(journalPairs(journal, scope: scope, limit: limit,
                                             onlyMe: onlyMe, world: world, who: who,
                                             nextSaid: nextSaid, lastMile: true)), 0) + "\n")
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
    spawnCounted("court")
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
    waitDone(p)
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
    let dir = tempRoot() + "gate-seam-\(ProcessInfo.processInfo.processIdentifier)"
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
        // the advice knows where it is standing, as in import workflows
        ? (ProcessInfo.processInfo.environment["GITHUB_ACTIONS"] == "true"
           ? "this run is that wire: neither side can move without the other seeing"
           : "wire it into CI: neither side can move without the other seeing")
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

// ── THE BENCH, SERVED FROM THIS CARRIER: the socket, the request, the answer.
// The routes are the verbs this vein already carries, said over a wire. The
// contract they answer is written here, and this head is the list this door is
// held to: the battery reads it and the routes below, and refuses a door that
// answers something nobody promised or promises something it does not answer.
// It used to live at the head of the other carrier's `serve`; that carrier is
// gone, and a contract kept in a file that no longer exists is a contract with
// nobody.
//
//   GET  /                     the bench itself
//   GET  /attention            what waits for a word, seam by seam
//   GET  /check/view           does this grant hold, asked without writing
//   GET  /codemirror.css       the editor's own stylesheet, carried here
//   GET  /codemirror.js        the editor, carried here: nothing is fetched
//   GET  /diff/transfer        what a change would do, and nothing done
//   GET  /files                the world's files, their roles and verdicts
//   GET  /gitstatus            what git says about this working copy
//   GET  /judge.js             the ported court, for the page to judge with
//   GET  /ladder.css           the ladder and the palette, as this world says
//   GET  /language             the grammar the page highlights and offers by
//   GET  /log                  the journal of this world
//   GET  /seamside             one side of a seam, read-only
//   GET  /shelf                the shelf's pages, by name
//   GET  /show                 a commit, read as facts
//   GET  /status               the verdict over this world
//   GET  /version              the gate a page is talking to
//   GET  /world                a file of this world, as text
//   POST /verdict              judge the text in the editor, unsaved
//   PUT  /declare              write a row into the layout
//   PUT  /value                write a value into a world you present
//   PUT  /world                write a file of this world back to disk
//
// POSIX and not Network.framework: the latter is Darwin's alone, and this vein
// builds wherever swiftc does. One request at a time, the way the other carrier
// answers, and the loopback address is written here rather than configured:
// nothing about this server is reachable from a network.
//
// WHAT THE BATTERY HOLDS IS THE CODE, THE CONTENT TYPE AND THE BODY, never the
// raw headers: the other carrier's http server writes a Server and a Date line
// of its own, so those two differ by construction and say nothing about either
// answer.

// python's json.dumps(obj, ensure_ascii=False): no indent, and python's own
// separators. The indented spelling of the same pairs is `statusDumps`, and
// both read the one object `statusPairs` assembles.
func compactDumps(_ v: StatusJSON, ascii: Bool = false) -> String {
    func say(_ s: String) -> String { return ascii ? jsonStringASCII(s) : jsonString(s) }
    switch v {
    case .text(let s): return say(s)
    case .raw(let r): return r
    case .null: return "null"
    case .list(let items):
        return "[" + items.map { compactDumps($0, ascii: ascii) }.joined(separator: ", ") + "]"
    case .object(let pairs):
        return "{" + pairs.map { say($0.0) + ": " + compactDumps($0.1, ascii: ascii) }
            .joined(separator: ", ") + "}"
    }
}

// ── AND ONE ANSWER IS SPELLED IN ASCII, because the other carrier spells it
// that way: its verdict route dumps without `ensure_ascii=False`, so a `·` in a
// refusal travels as `\u00b7`. Two spellings of one character are two different
// answers to a page that compares bytes.
func jsonStringASCII(_ s: String) -> String {
    var out = "\""
    for ch in s.unicodeScalars {
        switch ch {
        case "\"": out += "\\\""
        case "\\": out += "\\\\"
        case "\n": out += "\\n"
        case "\t": out += "\\t"
        case "\r": out += "\\r"
        default:
            if ch.value < 0x20 || ch.value > 0x7e {
                if ch.value > 0xFFFF {
                    // python writes a surrogate pair for anything past the
                    // basic plane, which is what json.dumps does by default
                    let v = ch.value - 0x10000
                    out += String(format: "\\u%04x\\u%04x",
                                  0xD800 + (v >> 10), 0xDC00 + (v & 0x3FF))
                } else {
                    out += String(format: "\\u%04x", ch.value)
                }
            } else {
                out.unicodeScalars.append(ch)
            }
        }
    }
    return out + "\""
}

// the version is declared once, in the other carrier's own file, and this reads
// it there. A literal here would be a second copy of one number, which is the
// registry's kind 9 written by hand; when that file goes, the declaration moves
// with it and this reads wherever it lands.
let VERSION = "0.2.3"

func gateVersion() -> String {
    return VERSION
}

// the page a personal world opens with, read where it is declared: the other
// carrier's own file. A copy here would be one text in two places, which is the
// registry's kind 9 written by hand; when that file goes, the text goes to the
// shelf with every other thing this tool writes into somebody's repository.
func personalTemplate() -> String {
    return PERSONAL_PAGE
}

let PERSONAL_PAGE = """
// Yours. It is judged together with the files beside it, and it is never in the
// shared repository: your colleagues and CI do not have it. Write a claim you
// want to keep true, and the judge names the line when somebody else's change
// breaks it. Left as it is, it is not stored anywhere.
//
// It lives on this machine, in a git of its own at ~/.gate/me, and every state
// that holds is kept there. It goes nowhere else: no clone of the shared
// repository will have it, and neither will your other computer, unless you
// give that repository a remote of your own.
//
// One thing about the page: the record below names its theme. Change Dark to
// Light and the page follows on the next keystroke, which is the whole
// mechanism of this place in one line: the file is the panel. Delete the
// record and the page follows this machine's own setting instead. For a
// while these lines were left commented, so that your first word here would
// be yours; written out they show where changing something lands, and that
// is worth more.

public enum MyBench: Bench {
    public typealias Theme = Dark
}

"""

// ── THE LANGUAGE, AND WHERE IT IS DECLARED. These are the words the mechanism
// must know as grammar, so knowing them is the one place a name may sit inside
// a tool by right. They are declared once, in the other carrier's file, and read
// from there for the same reason the version and the personal page are: one
// text, one home, until that file goes.
// ── THE LANGUAGE, AND WHERE IT IS DECLARED. These are the words the mechanism
// must know as grammar: it cannot count without them, so knowing them here is
// the one place a name may sit inside a tool by right. Everything else a world
// says is presented rather than built in.
let LANGUAGE_AT: [(String, Int)] = [("Unit", 283), ("Plus", 287), ("Times", 303), ("Twice", 299), ("Paired", 227), ("Close", 88), ("Open", 87), ("Structure", 86)]
let LANGUAGE_FILE = "Sources/VerificationIsIdentification/Primitive.swift"
// what the court itself is, by name: the two files that decide every verdict
// this tool prints
let COURT_FILES = ["Sources/Tools/Judge.swift", "Sources/Tools/WhereJudge.swift"]

func languageNames() -> [(String, Int)] {
    return LANGUAGE_AT
}

func languageFile() -> String {
    return LANGUAGE_FILE
}

// counted from the checkout when there is one, and said to be uncounted when
// there is not: never a number written here, which would be a claim about
// somebody else's file that nothing checks
func courtShape() -> StatusJSON {
    guard let root = ProcessInfo.processInfo.environment["GATE_CORPUS"], !root.isEmpty
    else { return .null }
    let files = COURT_FILES
    var lines = 0
    var seen: [StatusJSON] = []
    for rel in files {
        let p = (root as NSString).appendingPathComponent(rel)
        guard let body = readText(p) else { return .null }
        // python counts the lines a file iterates: the last line counts only
        // when the file does not end on a newline
        lines += body.components(separatedBy: "\n").count - (body.hasSuffix("\n") ? 1 : 0)
        seen.append(.text(rel))
    }
    return .object([("files", .list(seen)), ("lines", .raw(String(lines)))])
}

// ── SAYING A NUMBER, which is reading one run backwards. These worlds spell a
// value on their own ladder from Unit, so writing 760 means writing the rungs it
// is made of: ascending, right-nested, `Unit` where the ladder has no name for
// one. Without it the bench could show a value and never let anybody say one,
// which is a table you may read and not answer.
func spellNumber(_ n: Int) -> String {
    if n <= 0 { return "Never" }
    var parts: [String] = []
    var bit = 1
    while bit <= n {
        if n & bit != 0 { parts.append(bit == 1 ? "Unit" : "W\(bit)") }
        bit <<= 1
    }
    var said = parts[parts.count - 1]
    for piece in parts.dropLast().reversed() { said = "Plus<\(piece), \(said)>" }
    return said
}

// WHERE A VALUE OF MINE GOES: a row of mine, read by the where court, that is
// not one of the files this tool ships. Writing into those would be editing
// somebody else's world, which is what the mine/theirs split exists to prevent.
// One such file is an answer; none and several are not, and both say so rather
// than picking.
func myFormsFiles(_ w: WorldState) -> [String] {
    let base = layoutDir(w) ?? "."
    let shipped = Set(shelf().map { $0.name + ".swift" })
    return (w.layout?.rows ?? [])
        .filter { $0.role == "forms" && $0.source == "mine"
                  && !shipped.contains(($0.path as NSString).lastPathComponent) }
        .map { (base as NSString).appendingPathComponent($0.path) }
}

// what `mine` answers when a row is written: said once, because the panel
// declares through the very same verb and may not spell its words a second time
func minePairs(_ file: String, _ declaredIn: String, _ role: String,
               _ roleMeans: String) -> [(String, StatusJSON)] {
    return [
        ("command", .text("mine")), ("file", .text(file)),
        ("declared_in", .text(declaredIn)), ("role", .text(role)),
        ("role_means", .text(roleMeans)), ("mutates", .raw("true")),
        ("note", .text("mine: I emit it, it is judged with the rest of my world, and "
                     + "changing it changes the verdict")),
        ("next", .text("gate status: it is judged from here on")),
    ]
}

func personalRootPath() -> String {
    return ProcessInfo.processInfo.environment["GATE_ME"]
        ?? ((NSHomeDirectory() as NSString).appendingPathComponent(".gate/me"))
}

// ── WRITING IS WHAT BRINGS A PERSONAL WORLD INTO BEING, and emptying it takes
// it away: text still equal to the page it started with means nobody wrote
// anything, so there is nothing to keep. It lives in a git of its own, in the
// operator's home, never in the shared clone: colleagues and CI do not have it,
// and privacy here is the repository boundary rather than a policy.
func writePersonal(_ w: WorldState, _ text: String) {
    guard let p = personalPathOf(w) else { return }
    let said = text.trimmingCharacters(in: .whitespacesAndNewlines)
    let page = personalTemplate().trimmingCharacters(in: .whitespacesAndNewlines)
    if said.isEmpty || said == page {
        try? FileManager.default.removeItem(atPath: p)
        return
    }
    let home = personalRootPath()
    try? FileManager.default.createDirectory(
        atPath: (p as NSString).deletingLastPathComponent, withIntermediateDirectories: true)
    if !FileManager.default.fileExists(atPath: (home as NSString).appendingPathComponent(".git")) {
        _ = runGit(["init", "-q", home], home)
    }
    try? text.write(toFile: p, atomically: true, encoding: .utf8)
    // only text that holds is ever written here, so every commit is a state
    // that held: this is gate's own repository, not the operator's
    _ = runGit(["add", "-A"], home)
    _ = runGit(["-c", "user.email=you@localhost", "-c", "user.name=you",
                "-c", "commit.gpgsign=false", "commit", "-qm", "your world"], home)
}

func percentDecoded(_ s: String) -> String {
    let plus = s.replacingOccurrences(of: "+", with: " ")
    return plus.removingPercentEncoding ?? plus
}

// python's `{k: v[0] for k, v in parse_qs(query).items()}`: a name said twice
// answers with its FIRST value, and a name said with no value is empty, which
// every route here reads as absent the same way the other carrier does.
func queryOf(_ raw: String) -> [String: String] {
    var q: [String: String] = [:]
    for part in raw.split(separator: "&", omittingEmptySubsequences: true) {
        let kv = part.split(separator: "=", maxSplits: 1, omittingEmptySubsequences: false)
        let name = percentDecoded(String(kv[0]))
        let said = kv.count > 1 ? percentDecoded(String(kv[1])) : ""
        if q[name] == nil { q[name] = said }
    }
    return q
}

// ── ONE NAME FOR A CONNECTION, THREE PLATFORMS. A socket is an `Int32` where
// the calls come from libc and a 64-bit handle where they come from WinSDK, and
// the reading and writing calls are spelled differently too. The door below is
// written once, in these names.
#if canImport(WinSDK)
typealias GateSocket = SOCKET
let gateNoSocket = INVALID_SOCKET
func gateRead(_ c: GateSocket, _ buf: UnsafeMutableRawPointer?, _ n: Int) -> Int {
    return Int(recv(c, buf?.assumingMemoryBound(to: CChar.self), Int32(n), 0))
}
func gateWrite(_ c: GateSocket, _ buf: UnsafeRawPointer, _ n: Int) -> Int {
    return Int(send(c, buf.assumingMemoryBound(to: CChar.self), Int32(n), 0))
}
func gateClose(_ c: GateSocket) { closesocket(c) }
func gateSocketsReady() {
    var data = WSADATA()
    _ = WSAStartup(0x0202, &data)     // the winsock version this asks for
}
#else
typealias GateSocket = Int32
let gateNoSocket: GateSocket = -1
func gateRead(_ c: GateSocket, _ buf: UnsafeMutableRawPointer?, _ n: Int) -> Int {
    return read(c, buf, n)
}
func gateWrite(_ c: GateSocket, _ buf: UnsafeRawPointer, _ n: Int) -> Int {
    return write(c, buf, n)
}
func gateClose(_ c: GateSocket) { close(c) }
func gateSocketsReady() {}
#endif

func serveRead(_ conn: GateSocket) -> (method: String, path: String,
                                  query: [String: String], body: Data)? {
    var buf = Data()
    var chunk = [UInt8](repeating: 0, count: 4096)
    var head: Range<Data.Index>? = nil
    while head == nil {
        let n = chunk.withUnsafeMutableBytes { gateRead(conn, $0.baseAddress, 4096) }
        if n <= 0 { return nil }
        buf.append(contentsOf: chunk[0..<n])
        head = buf.range(of: Data("\r\n\r\n".utf8))
    }
    guard let mark = head else { return nil }
    let headText = String(decoding: buf[buf.startIndex..<mark.lowerBound], as: UTF8.self)
    let lines = headText.components(separatedBy: "\r\n")
    let said = (lines.first ?? "").split(separator: " ", omittingEmptySubsequences: true)
        .map(String.init)
    guard said.count >= 2 else { return nil }
    // the path is NOT percent-decoded: urlparse does not decode one either, and
    // only the query is read through a parse that does
    var path = said[1], query = ""
    if let q = said[1].firstIndex(of: "?") {
        path = String(said[1][said[1].startIndex..<q])
        query = String(said[1][said[1].index(after: q)...])
    }
    var want = 0
    for line in lines.dropFirst() where line.lowercased().hasPrefix("content-length:") {
        want = Int(line.dropFirst("content-length:".count)
            .trimmingCharacters(in: .whitespaces)) ?? 0
    }
    var body = Data(buf[mark.upperBound...])
    while body.count < want {
        let n = chunk.withUnsafeMutableBytes { gateRead(conn, $0.baseAddress, 4096) }
        if n <= 0 { break }
        body.append(contentsOf: chunk[0..<n])
    }
    return (said[0], path, queryOf(query), body)
}

func serveSay(_ conn: GateSocket, _ code: Int, _ ctype: String?, _ body: Data) {
    let reason = [200: "OK", 400: "Bad Request", 404: "Not Found",
                  409: "Conflict"][code] ?? "OK"
    var head = "HTTP/1.0 \(code) \(reason)\r\n"
    if let c = ctype { head += "Content-Type: \(c)\r\n" }
    // never cached: an updated gate must not be hidden behind a bench the
    // browser kept from the last version
    head += "Cache-Control: no-store\r\n"
    head += "Content-Length: \(body.count)\r\n\r\n"
    var whole = Data(head.utf8)
    whole.append(body)
    whole.withUnsafeBytes { raw in
        var sent = 0
        while sent < raw.count, let base = raw.baseAddress {
            let n = gateWrite(conn, base.advanced(by: sent), raw.count - sent)
            if n <= 0 { break }
            sent += n
        }
    }
}

func serveJSON(_ conn: GateSocket, _ text: String) {
    serveSay(conn, 200, "application/json", Data(text.utf8))
}

// an answer as the bench says it: the object entire, or the refusal as the
// object the other carrier's exception carries. Both leave with a 200, because
// the page asked a question and got one answered.
func benchSaid(_ answered: Answered) -> String {
    switch answered {
    case .said(let pairs):
        return compactDumps(.object(pairs))
    case .cannot(let note, let next):
        var pairs: [(String, StatusJSON)] = [("error", .text(note))]
        if let step = next, !step.isEmpty { pairs.append(("next", .text(step))) }
        return compactDumps(.object(pairs))
    }
}

// ── AND NOTHING LEAVES THIS ROOM WITHOUT WORDS. A file the bench asks for and
// cannot read answers with the sentence the other carrier answers with, rather
// than a bare code: the page's own fetch shows a network error for a dropped
// connection, which reads as "the bench is gone" instead of "that request was
// wrong".
func serveFile(_ conn: GateSocket, _ path: String, _ ctype: String) {
    guard let body = FileManager.default.contents(atPath: path) else {
        serveJSON(conn, compactDumps(.object([
            ("error", .text("this request was not one the bench could read: FileNotFoundError")),
            ("next", .text("the terminal answers the same questions and says more: "
                         + "`gate status`, `gate log`, `gate findings`"))])))
        return
    }
    serveSay(conn, 200, ctype, body)
}

// ── THE WORLDS THE PAGE PAINTS WITH, READ WHERE THEY ARE DECLARED. The
// stylesheet holds no number of its own: every colour, every step and every
// face comes off a world this repository judges, so the page and the verdict
// cannot part.

func presentedWorld(_ w: WorldState, _ shelfName: String) -> String {
    return presentedOver(w, shelfName).text
}

// every number in these worlds is spelled on the file's own ladder from Unit,
// so reading one is walking that spelling, never a table kept beside it.
// ── TWO READINGS, AND BOTH ARE THE OTHER CARRIER'S. The palette and the faces
// read `W12` and `N12` alike and let the FIRST speaker win, because what is
// presented outranks what shipped; the steps read `W12` alone and let the last
// win. Copied as they stand rather than reconciled: one reading here would be
// this vein inventing a rule neither carrier has.
func ladderValues(_ text: String, bothLiterals: Bool, firstWins: Bool) -> [String: Int] {
    var vals: [String: Int] = [:]
    func ev(_ raw: String) -> Int? {
        let e = raw.trimmingCharacters(in: .whitespaces)
        if e == "Unit" { return 1 }
        if e == "Never" { return 0 }
        if let said = vals[e] { return said }
        if let m = matchAt(e, (bothLiterals ? "[WN]" : "W") + "(\\d+)$") { return Int(m[1]) }
        if e.hasPrefix("Twice<") && e.hasSuffix(">") {
            return ev(String(e.dropFirst(6).dropLast())).map { 2 * $0 }
        }
        if e.hasPrefix("Plus<") && e.hasSuffix(">") {
            let inner = Array(String(e.dropFirst(5).dropLast()))
            var depth = 0
            for (i, c) in inner.enumerated() {
                if c == "<" { depth += 1 }
                else if c == ">" { depth -= 1 }
                else if c == "," && depth == 0 {
                    guard let left = ev(String(inner[0..<i])),
                          let right = ev(String(inner[(i + 1)...])) else { return nil }
                    return left + right
                }
            }
        }
        return nil
    }
    for m in matches("^public typealias (\\w+) = (.+)$", text, lines: true) {
        let name = m[0]
        if firstWins && vals[name] != nil { continue }
        let expr = m[1].components(separatedBy: "//")[0].trimmingCharacters(in: .whitespaces)
        if let said = ev(expr) { vals[name] = said }
    }
    return vals
}

// a hex fallback for anything that cannot read color(): a rendering of the
// declared fact, never a second statement of it
func srgbHex(_ x: Double, _ y: Double, _ z: Double) -> String {
    let lin = [3.2406 * x - 1.5372 * y - 0.4986 * z,
               -0.9689 * x + 1.8758 * y + 0.0415 * z,
               0.0557 * x - 0.2040 * y + 1.0570 * z]
    let eight = lin.map { c -> Int in
        let s = c <= 0.0031308 ? 12.92 * c : 1.055 * pow(max(c, 0), 1 / 2.4) - 0.055
        // python's round, which goes to the even neighbour on a half: the
        // number this page has always painted is the other carrier's
        return max(0, min(255, Int((s * 255).rounded(.toNearestOrEven))))
    }
    return String(format: "#%02X%02X%02X", eight[0], eight[1], eight[2])
}

func paletteTokens(_ w: WorldState) -> String {
    let text = presentedWorld(w, "bench-palette")
    let vals = ladderValues(text, bothLiterals: true, firstWins: true)
    let names = Set(matches("^public typealias (\\w+)(?:Lit|Dim)X = ", text, lines: true)
        .map { $0[0] }).sorted()
    func block(_ half: String) -> String {
        var rows: [String] = []
        for n in names {
            guard let x = vals[n + half + "X"], let y = vals[n + half + "Y"],
                  let z = vals[n + half + "Z"] else { continue }
            // the name in the page's own spelling: every capital goes down,
            // which is the whole of the other carrier's substitution
            let varName = "--" + n.lowercased()
            rows.append("  \(varName): "
                      + srgbHex(Double(x) / 1000, Double(y) / 1000, Double(z) / 1000) + ";"
                      + " \(varName): color(xyz-d65 calc(\(x)/1000) calc(\(y)/1000) calc(\(z)/1000));")
        }
        return rows.joined(separator: "\n")
    }
    return ":root {\n" + block("Lit") + "\n}\n"
         + ":root[data-theme=\"dark\"] {\n" + block("Dim") + "\n}\n"
}

func ladderTokens(_ w: WorldState) -> String {
    let vals = ladderValues(presentedWorld(w, "bench-metrics"),
                            bothLiterals: false, firstWins: false)
    // `Line` is left out: the page already spends that name on a border colour,
    // and one word may not mean two things in one document
    var rows: [String] = []
    for name in ["Tight", "Snug", "Near", "Step", "Room", "Apart", "Edge", "Wide", "Indent"] {
        if let said = vals[name] {
            rows.append("  --\(name.lowercased()): calc(var(--u) * \(said));")
        }
    }
    return ":root {\n" + rows.joined(separator: "\n") + "\n}\n"
}

func registerTokens(_ w: WorldState) -> String {
    let text = presentedWorld(w, "bench-registers")
    let vals = ladderValues(text, bothLiterals: true, firstWins: true)
    var faces: [String: String] = [:]
    for m in matches("public enum (\\w+): Register \\{\\s*\\n\\s*public typealias On = (\\w+)",
                     text) {
        faces[m[0]] = m[1]
    }
    // how hard a register is set, read off the same declaration: a register you
    // present is treated exactly like the ones this tool ships, because the
    // declaration says and no name is written into the mechanism
    var stresses: [String: String] = [:]
    for m in matches("public enum (\\w+): Register \\{[^}]*?public typealias Set = (\\w+)",
                     text, dotAll: true) {
        stresses[m[0]] = m[1]
    }
    var rows: [String] = []
    for name in faces.keys.sorted() {
        guard let size = vals[name + "Size"] else { continue }
        let stack = faces[name] == "Mono" ? "ui-monospace,Menlo,monospace"
                                          : "-apple-system,sans-serif"
        let weight = stresses[name] == "Firm" ? "600 " : ""
        let px = String(format: "%g", Double(size) / 10)
        let lead = vals[name + "Lead"] ?? 0
        let leading = lead != 0 ? "/" + String(format: "%g", Double(lead) / 100) : ""
        rows.append("  --\(name.lowercased()): \(weight)\(px)px\(leading) \(stack);")
    }
    // and the two faces on their own, for a rule that changes the face and keeps
    // whatever size it stands in: still a name, never a stack written by hand
    for (face, stack) in [("Mono", "ui-monospace,Menlo,monospace"),
                          ("Sans", "-apple-system,sans-serif")] {
        if text.contains("public enum " + face + ": Face {}") {
            rows.append("  --\(face.lowercased()): \(stack);")
        }
    }
    return ":root {\n" + rows.joined(separator: "\n") + "\n}\n"
}

// only the judged list is servable: the manifest's files, your own world, and a
// file that is here and undeclared, which cannot be judged and can still be
// read. A name this world does not carry is a miss, never another file: the
// door opening on the wrong room while saying nothing is the one thing this
// page may not do. The fallback below is for the question that named nothing.
func servePick(_ w: WorldState, _ query: [String: String]) -> String? {
    let named = Dictionary(benchFilesOf(w).map { ($0.0, $0.1) }, uniquingKeysWith: { a, _ in a })
    let want = query["f"] ?? ""
    if let hit = named[want] { return hit }
    if undeclaredHere(w).contains(want), let dir = layoutDir(w) {
        return (dir as NSString).appendingPathComponent(want)
    }
    if !want.isEmpty { return nil }
    if let facts = w.facts, FileManager.default.fileExists(atPath: facts) { return facts }
    return benchFilesOf(w).first(where: { FileManager.default.fileExists(atPath: $0.1) })?.1
        ?? w.facts
}

// ── WHAT A COMMIT DID, READ AS FACTS WHERE IT CAN BE. This is a world, so
// `Rank: Manager -> Lead` is what changed, never `-`/`+` around plumbing. Lines
// that are not a fact change stay lines; git's own noise (index, ---/+++, @@) is
// never shown, because nobody reads a world through it.
func commitChange(_ base: String, _ sha: String, _ path: String?) -> [(String, StatusJSON)] {
    let said = runGit(["show", "--format=%H%x1f%an%x1f%ae%x1f%aI%x1f%s", "--no-color", sha]
                      + (path.map { ["--", $0] } ?? []), base)
    let lines = said.components(separatedBy: "\n")
    let head = ((lines.first ?? "").components(separatedBy: "\u{1f}") + ["", "", "", "", ""])
        .prefix(5).map { $0 }
    struct Changed { var name: String; var changes: [[(String, StatusJSON)]] }
    var files: [Changed] = []
    var owner: String? = nil
    let skips = ["index ", "--- ", "+++ ", "new file", "deleted file",
                 "old mode", "new mode", "similarity", "rename "]
    for ln in lines.dropFirst() {
        if ln.hasPrefix("diff --git") {
            files.append(Changed(name: (ln.components(separatedBy: " b/").last ?? "")
                .trimmingCharacters(in: .whitespaces), changes: []))
            owner = nil
        } else if files.isEmpty || ln.isEmpty {
            continue
        } else if skips.contains(where: { ln.hasPrefix($0) }) {
            continue
        } else if ln.hasPrefix("@@") {
            let after = matches("@@.*@@\\s*(.*)$", ln).first?.first ?? ""
            owner = matches("(?:enum|protocol|struct)\\s+(\\w+)", after).first?.first
        } else if let sign = ln.first, sign == " " || sign == "-" || sign == "+" {
            let body = String(ln.dropFirst())
            if let named = matches("(?:public\\s+)?(?:enum|protocol|struct)\\s+(\\w+)", body)
                .first?.first {
                owner = named
            }
            if sign == " " { continue }
            files[files.count - 1].changes.append([
                ("kind", .text("line")), ("sign", .text(String(sign))),
                ("text", .text(body.replacingOccurrences(of: "\\s+$", with: "",
                                                         options: .regularExpression))),
                ("owner", owner.map { StatusJSON.text($0) } ?? .null),
            ])
        }
    }
    // pair a removal with the addition that restates the same fact
    func saidName(_ row: [(String, StatusJSON)]) -> [String]? {
        return matchAt(textIn(row, "text") ?? "",
                       "\\s*(?:public\\s+)?typealias\\s+(\\w+)\\s*=\\s*(.+?)\\s*$")
    }
    for i in files.indices {
        var paired: [[(String, StatusJSON)]] = []
        var at = 0
        let cs = files[i].changes
        while at < cs.count {
            let a = cs[at]
            let b = at + 1 < cs.count ? cs[at + 1] : nil
            if let ma = saidName(a), let bb = b, let mb = saidName(bb),
               textIn(a, "sign") == "-", textIn(bb, "sign") == "+", ma[1] == mb[1] {
                paired.append([("kind", .text("fact")),
                               ("owner", a.first(where: { $0.0 == "owner" })?.1 ?? .null),
                               ("key", .text(ma[1])), ("from", .text(ma[2])),
                               ("to", .text(mb[2]))])
                at += 2
                continue
            }
            paired.append(a)
            at += 1
        }
        files[i].changes = paired
    }
    return [
        ("hash", .text(head[0])), ("short", .text(String(head[0].prefix(8)))),
        ("author", .text(head[1])), ("email", .text(head[2])),
        ("date", .text(head[3])), ("subject", .text(head[4])),
        ("files", .list(files.map { f in
            .object([("name", .text(f.name)),
                     ("changes", .list(f.changes.map { .object($0) }))])
        })),
    ]
}

// ── AND THE BENCH REMEMBERS WHAT IT READ. Every route here opened the shelf
// and built the world again, which is right for a command that runs once and
// wrong for a server: the page asks for a dozen things to open one file, and
// each answer paid for a shelf of sixteen pages and a walk of the layout. The
// other carrier keeps both and re-reads the layout only when its BYTES change,
// so the disk stays the authority and the parse is what is skipped. Measured
// before this: `/files` 26 times dearer than the other carrier, `/status` 28,
// and the cover's camera took seven minutes on a runner where it takes fifteen
// seconds here.
var SERVED_WORLD: WorldState? = nil
var SERVED_LAYOUT: Data? = nil
var SHELF_READ = false

func servedWorld() -> WorldState {
    let dir = FileManager.default.currentDirectoryPath
    let mp = (dir as NSString).appendingPathComponent("gate.manifest.swift")
    let raw = FileManager.default.contents(atPath: mp)
    if let held = SERVED_WORLD, raw == SERVED_LAYOUT { return held }
    if !SHELF_READ {
        loadStatusShelf()
        SHELF_READ = true
    }
    let w = discoverWorld()
    SERVED_WORLD = w
    SERVED_LAYOUT = raw
    return w
}

func serveDoor(_ a: [String]) -> Never {
    let nums = a.filter { !$0.isEmpty && $0.allSatisfy { $0.isNumber } }
    let port = nums.first.flatMap { Int($0) } ?? 4744
    let openIt = !a.contains("--no-open")

    gateSocketsReady()
    #if canImport(Glibc)
    let stream = Int32(SOCK_STREAM.rawValue)
    #elseif canImport(WinSDK)
    let stream = Int32(SOCK_STREAM)
    #else
    let stream = SOCK_STREAM
    #endif
    let listener = socket(AF_INET, stream, 0)
    if listener == gateNoSocket {
        cannot("this machine would not give the bench a socket",
               "run `gate status` in the terminal: the same answers, no port needed")
    }
    var yes: Int32 = 1
    setsockopt(listener, SOL_SOCKET, SO_REUSEADDR, &yes,
               socklen_t(MemoryLayout<Int32>.size))
    var addr = sockaddr_in()
    #if canImport(WinSDK)
    addr.sin_family = ADDRESS_FAMILY(AF_INET)
    addr.sin_addr.S_un.S_addr = UInt32(0x7f00_0001).bigEndian        // 127.0.0.1, never a network
    #else
    addr.sin_family = sa_family_t(AF_INET)
    addr.sin_addr = in_addr(s_addr: UInt32(0x7f00_0001).bigEndian)   // 127.0.0.1, never a network
    #endif
    addr.sin_port = UInt16(truncatingIfNeeded: port).bigEndian
    let bound = withUnsafePointer(to: &addr) { raw in
        raw.withMemoryRebound(to: sockaddr.self, capacity: 1) {
            bind(listener, $0, socklen_t(MemoryLayout<sockaddr_in>.size))
        }
    }
    if bound != 0 || listen(listener, 16) != 0 {
        cannot("port \(port) is already spoken for on this machine",
               "run `gate serve PORT` with a port nothing else is holding")
    }

    out(compactDumps(.object([
        ("command", .text("serve")),
        ("url", .text("http://127.0.0.1:\(port)")),
        // every route this door answers is promised here, `/attention` with the
        // rest: a route a caller can reach and the roster does not name is a
        // surface nobody agreed to, and the roster is where they would look
        ("routes", .list([.text("/status"), .text("/log"), .text("/show?hash=&f="),
                          .text("/attention"),
                          .text("/check/view?who=&doc="), .text("/diff/transfer?who=&to=")])),
        ("mutating_routes", .text("none, by design")),
    ])) + "\n")
    fflush(stdout)

    if openIt {
        // the bench is the point of serve, and the listener is already up by
        // this line, so the page has something to reach the moment it opens
        mark("spawn:browser")
        let opener = Process()
        #if canImport(Glibc)
        opener.executableURL = URL(fileURLWithPath: "/usr/bin/xdg-open")
        #elseif canImport(WinSDK)
        opener.executableURL = URL(fileURLWithPath: "C:/Windows/System32/cmd.exe")
        #else
        opener.executableURL = URL(fileURLWithPath: "/usr/bin/open")
        #endif
        #if canImport(WinSDK)
        opener.arguments = ["/c", "start", "", "http://127.0.0.1:\(port)/ui"]
        #else
        opener.arguments = ["http://127.0.0.1:\(port)/ui"]
        #endif
        try? opener.run()
    }

    while true {
        var from = sockaddr()
        var size = socklen_t(MemoryLayout<sockaddr>.size)
        let conn = accept(listener, &from, &size)
        if conn == gateNoSocket { continue }
        let spawnsBefore = SPAWNS
        if let asked = serveRead(conn) {
            switch (asked.method, asked.path) {
            case ("GET", "/"), ("GET", "/ui"):
                serveFile(conn, joinPath(toolRoot(), "web/ui.html"),
                          "text/html; charset=utf-8")
            case ("GET", "/judge.js"):
                // the judge this page reads with, served whole
                serveFile(conn, joinPath(toolRoot(), "bin/judge.js"),
                          "text/javascript")
            case ("GET", "/codemirror.js"):
                serveFile(conn, joinPath(toolRoot(), "web/codemirror.js"),
                          "text/javascript")
            case ("GET", "/codemirror.css"):
                serveFile(conn, joinPath(toolRoot(), "web/codemirror.css"),
                          "text/css")
            case ("GET", "/ladder.css"):
                // the named steps, emitted from the judged worlds so the page
                // can say `var(--apart)` and never a number of its own
                let w = servedWorld()
                let sheet = paletteTokens(w) + ladderTokens(w) + registerTokens(w)
                serveSay(conn, 200, "text/css; charset=utf-8", Data(sheet.utf8))
            case ("GET", "/shelf"):
                // what the shelf carries, and each page's own card: the sort it
                // says it is and the voice it says it speaks in, read off the
                // page itself rather than guessed from the shape of its name
                _ = servedWorld()
                let pages = shelf().map { $0.name }
                if let want = asked.query["m"], !want.isEmpty {
                    if STDLIB_TEXTS[want] == nil {
                        serveSay(conn, 404, nil, Data())
                    } else {
                        // THE WORLD AS IT STANDS, not the text as it shipped:
                        // what governs is your declarations put where the
                        // shelf's stood, and that is what the judge reads
                        let w = servedWorld()
                        serveSay(conn, 200, "text/plain; charset=utf-8",
                                 Data(presentedWorld(w, want).utf8))
                    }
                } else {
                    serveJSON(conn, compactDumps(.object([
                        ("modules", .list(pages.map { .text($0) })),
                        ("roles", .object(pages.map {
                            ($0, shelfHeadLine($0, "// role:").map { StatusJSON.text($0) } ?? .null) })),
                        ("speaks", .object(pages.map {
                            ($0, shelfHeadLine($0, "// speaks-for:").map { StatusJSON.text($0) } ?? .null) })),
                    ])))
                }
            case ("GET", "/log"):
                // ── AND A NUMBER THAT IS NOT ONE IS SAID, NOT DROPPED. `?n=`
                // comes off a URL, which is a place anybody can type into, and
                // reading it straight closed the socket with no response at
                // all: the page's own fetch showed a network error with no
                // words in it. Silence is the thing this tool exists against.
                let saidN = asked.query["n"] ?? "200"
                let n = Int(saidN)
                if !(saidN.allSatisfy { $0.isNumber } && !saidN.isEmpty
                     && (n ?? 0) > 0 && (n ?? 0) <= 100000) {
                    serveJSON(conn, benchSaid(.cannot(
                        note: "the history is read in commits, and `n=\(saidN)` is not a count",
                        next: "ask for a whole number of commits, such as `?n=200`")))
                    break
                }
                let base = FileManager.default.currentDirectoryPath
                let scope = asked.query["scope"] ?? "world"
                let world = journalWorld(base)
                let journal = repoJournal(base, world, scope: scope, limit: n ?? 200,
                                          onlyMe: false)
                let nextSaid = world.isEmpty
                    ? "run `gate demo` for a repository to look at, or drop a table you "
                      + "already export into tables/ and run `gate status`"
                    : "run `gate status` to have the judge read what these commits changed"
                serveJSON(conn, compactDumps(.object(journalPairs(
                    journal, scope: scope, limit: n ?? 200, onlyMe: false, world: world,
                    who: identities(base), nextSaid: nextSaid, lastMile: false))))
            case ("GET", "/show"):
                let w = servedWorld()
                let base = w.facts.map { (absPath($0) as NSString).deletingLastPathComponent }
                    ?? FileManager.default.currentDirectoryPath
                let want = asked.query["f"]
                serveJSON(conn, compactDumps(.object(commitChange(
                    base, asked.query["hash"] ?? "", (want?.isEmpty ?? true) ? nil : want))))
            case ("GET", "/attention"):
                // where nobody has declared anything there is nothing to show
                // and the bench says so: an empty account is a fact, and
                // inventing a specimen to fill it would be the one lie this
                // thing cannot afford
                let w = servedWorld()
                serveJSON(conn, compactDumps(.object([
                    ("command", .text("attention")),
                    ("seams", .list(seamsHere(w).map { .object($0) }))])))
            case ("GET", "/check/view"):
                // ── AND A QUESTION MISSING A WORD IS ANSWERED, NOT DROPPED.
                // These read the query straight, so a request without `who`
                // raised inside the handler and the connection died with no
                // response at all: the page saw a network error where a
                // sentence belonged.
                let w = servedWorld()
                let who = asked.query["who"] ?? "", doc = asked.query["doc"] ?? ""
                if who.isEmpty || doc.isEmpty {
                    serveJSON(conn, benchSaid(.cannot(
                        note: "check view asks who, and about what",
                        next: "/check/view?who=Emp0042&doc=FinanceShare")))
                } else {
                    serveJSON(conn, benchSaid(askViewAnswer(w, who, doc)))
                }
            case ("GET", "/diff/transfer"):
                let w = servedWorld()
                let who = asked.query["who"] ?? "", to = asked.query["to"] ?? ""
                if who.isEmpty || to.isEmpty {
                    serveJSON(conn, benchSaid(.cannot(
                        note: "diff transfer asks who moves, and where to",
                        next: "/diff/transfer?who=Emp0042&to=Sales")))
                } else if let facts = w.facts, FileManager.default.fileExists(atPath: facts) {
                    serveJSON(conn, benchSaid(
                        changeAnswer(w, facts, ["transfer", who, to], applyIt: false)))
                } else {
                    serveJSON(conn, benchSaid(.cannot(
                        note: "this asks its question of a world file, and there is none here",
                        next: "run `gate init .` to start one, or `gate demo` for a repository "
                            + "to look at. A world declared as a layout alone is judged by "
                            + "`gate status`")))
                }
            case ("GET", "/files"):
                let w = servedWorld()
                let named = benchFilesOf(w)
                let names = named.map { $0.0 }
                let rows = w.layout?.rows ?? []
                let factsDir = w.facts.map { (absPath($0) as NSString).deletingLastPathComponent }
                let layoutPath = w.layout?.manifest
                let lay = (layoutPath.flatMap { p -> String? in
                    guard FileManager.default.fileExists(atPath: p), let d = factsDir else { return nil }
                    return relPath(p, d)
                })
                let formsRows = rows.filter { $0.role == "forms" && names.contains($0.path) }
                    .map { $0.path }
                // AND WHICH OF YOUR FILES OVERRULES SOMETHING WE SHIPPED, and
                // what the name was before somebody said otherwise: an override
                // that is judged and invisible is still a surprise, and in a
                // month "why is my colour different" is answered by feel.
                var overridden: [(String, StatusJSON)] = []
                for page in shelf().map({ $0.name }).sorted() {
                    for (name, path) in presentedOver(w, page).placed {
                        // the world a name overrides is the one that SAYS it,
                        // and a name several shelves speak of is ONE row, held
                        // at the place it first took: the other carrier keeps
                        // these in a dictionary, so a later shelf rewrites the
                        // row rather than standing beside it. A list here said
                        // `W2` three times over, which no reader of this page
                        // could make sense of.
                        guard let was = matches("^public typealias " + name + " = (.+)$",
                                                STDLIB_TEXTS[page] ?? "", lines: true).first else { continue }
                        let row = StatusJSON.object([
                            ("file", .text(path)), ("world", .text(page)),
                            ("was", .text(was[0].replacingOccurrences(
                                of: "\\s+$", with: "", options: .regularExpression)))])
                        if let at = overridden.firstIndex(where: { $0.0 == name }) {
                            overridden[at].1 = row
                        } else {
                            overridden.append((name, row))
                        }
                    }
                }
                // AND HOW EACH FILE ASKS TO BE FIRST MET, in its own words
                var opens: [(String, StatusJSON)] = []
                for (name, path) in named
                where FileManager.default.fileExists(atPath: path) {
                    if let view = opensAs(w, path).view { opens.append((name, .text(view))) }
                }
                // ── AND THE SIDES OF A SEAM, which the layout declares: a seam
                // side is not a fragment of this world, and it is still a row of
                // the document on the screen. Read-only, by the route that
                // already exists for exactly this.
                let hereRoot = layoutDir(w) ?? "."
                let seamRows = rows.filter {
                    $0.role == "seam" && FileManager.default.fileExists(
                        atPath: (hereRoot as NSString).appendingPathComponent($0.path))
                }.map { $0.path }
                let personal = personalPathOf(w)
                var pairs: [(String, StatusJSON)] = [
                    ("files", .list(names.map { .text($0) })),
                    ("layout", lay.flatMap { names.contains($0) ? StatusJSON.text($0) : nil } ?? .null),
                    ("forms", .list(formsRows.map { .text($0) })),
                    // here and nobody declared: readable, not judged, and one
                    // gesture from being either
                    ("undeclared", .list(undeclaredHere(w).map { .text($0) })),
                    // and the courts a row may name, said once, here, so the
                    // page never keeps a second list of them to drift from this
                    ("roles", .object(STATUS_ROLES.map { ($0.0, .text($0.1)) })),
                    ("opens", .object(opens)),
                    ("seams", .list(seamRows.map { .text($0) })),
                    ("overridden", .object(overridden)),
                ]
                // WHERE THE COURT WAS TAKEN, so the one line a stranger asks
                // about, "why is this already here, I took nothing", can be
                // clicked through to the row that says so, in their own file
                if let judgeRow = rows.first(where: { $0.role == "judge" }),
                   let p = layoutPath, let factsAt = w.facts {
                    pairs.append(("judge_claim", .object([
                        ("file", .text(relPath(p, (factsAt as NSString).deletingLastPathComponent))),
                        ("line", .raw(String(judgeRow.line)))])))
                } else {
                    pairs.append(("judge_claim", .null))
                }
                pairs.append(("personal", personal != nil && !names.isEmpty
                                          ? .text(names[names.count - 1]) : .null))
                pairs.append(("personal_empty", .raw(
                    personal.map { !FileManager.default.fileExists(atPath: $0) } ?? false
                        ? "true" : "false")))
                serveJSON(conn, compactDumps(.object(pairs)))
            case ("GET", "/world"):
                // the page obeys the declared layout: `?f=` names a file FROM
                // that list, and a name the world does not carry is a miss
                let w = servedWorld()
                guard let p = servePick(w, asked.query) else {
                    serveSay(conn, 404, nil, Data())
                    break
                }
                if FileManager.default.fileExists(atPath: p) {
                    serveFile(conn, p, "text/plain; charset=utf-8")
                } else {
                    // yours, and nobody has written in it yet
                    serveSay(conn, 200, "text/plain; charset=utf-8",
                             Data(personalTemplate().utf8))
                }
            case ("GET", "/gitstatus"):
                // the honest state: a write lands in the working copy and git
                // carries the history, so this says whether the file is
                // committed or has uncommitted changes, never our own save
                let w = servedWorld()
                guard let facts = w.facts else {
                    serveSay(conn, 404, nil, Data())
                    break
                }
                let base = (absPath(facts) as NSString).deletingLastPathComponent
                if let p = servePick(w, asked.query) {
                    let dirty = runGit(["status", "--porcelain", "--", p], base)
                        .trimmingCharacters(in: .whitespacesAndNewlines)
                    let tracked = gitExitCode(["ls-files", "--error-unmatch", p], base)
                    let state = tracked != 0 ? "untracked" : (dirty.isEmpty ? "committed" : "modified")
                    serveJSON(conn, compactDumps(.object([
                        ("file", .text(relPath(p, base))),
                        ("git", .text(state))])))
                } else {
                    // the other carrier hands `None` to a path join here and
                    // meets its own reader with the sentence every unread
                    // request gets: said, never dropped
                    serveJSON(conn, compactDumps(.object([
                        ("error", .text("this request was not one the bench could read: TypeError")),
                        ("next", .text("the terminal answers the same questions and says more: "
                                     + "`gate status`, `gate log`, `gate findings`"))])))
                }
            case ("GET", "/seamside"):
                // one side of a seam, to READ. Every address this bench prints
                // should be reachable: a line you cannot open is a line you are
                // asked to take on trust, which is the one thing nothing here
                // asks for.
                let w = servedWorld()
                let base = w.facts.map { (absPath($0) as NSString).deletingLastPathComponent }
                    ?? FileManager.default.currentDirectoryPath
                let want = (base as NSString).appendingPathComponent(
                    ((asked.query["f"] ?? "") as NSString).lastPathComponent)
                if want.hasSuffix(".swift"), FileManager.default.fileExists(atPath: want),
                   isSeamSide(want) {
                    serveFile(conn, want, "text/plain; charset=utf-8")
                } else {
                    serveSay(conn, 404, nil, Data())
                }
            case ("GET", "/language"):
                let corpus = ProcessInfo.processInfo.environment["GATE_CORPUS"]
                if let want = asked.query["f"], !want.isEmpty {
                    // SHOWN, NOT ONLY TOLD, for whoever has the corpus. gate
                    // still fetches nothing: this reads a checkout already on
                    // the machine and refuses anything outside it rather than
                    // serving a path it was given.
                    let full = ((corpus ?? "") as NSString).appendingPathComponent(want)
                    let real = URL(fileURLWithPath: full).resolvingSymlinksInPath().path
                    let base = corpus.map { URL(fileURLWithPath: $0)
                        .resolvingSymlinksInPath().path } ?? ""
                    if !base.isEmpty, real.hasPrefix(base + "/"),
                       FileManager.default.fileExists(atPath: real) {
                        serveFile(conn, real, "text/plain; charset=utf-8")
                    } else {
                        serveSay(conn, 404, nil, Data())
                    }
                    break
                }
                // the words the mechanism knows by right, and the file that
                // declares them, so a name in a world can point at its floor
                let came = judgeFrom()
                let short = String((came ?? "").prefix(12))
                let here = corpus.map {
                    ($0 as NSString).appendingPathComponent(languageFile()) }
                serveJSON(conn, compactDumps(.object([
                    ("names", .object(languageNames().map { ($0.0, .raw(String($0.1))) })),
                    ("file", .text(languageFile())),
                    ("court", courtShape()),
                    ("at", came.map { StatusJSON.text($0) } ?? .null),
                    ("short", short.isEmpty ? .null : .text(short)),
                    ("present", .raw(here.map {
                        FileManager.default.fileExists(atPath: $0) } ?? false ? "true" : "false")),
                    ("command", .text("git clone https://github.com/DanielSwift1992/"
                                    + "verification-is-identification && cd "
                                    + "verification-is-identification"
                                    + (came != nil ? " && git checkout " + short : ""))),
                ])))
            case ("GET", "/version"):
                // WHAT IS ACTUALLY RUNNING. The bench serves its page off the
                // disk and its answers out of memory, so a gate updated while it
                // runs leaves a new page talking to an old server.
                serveJSON(conn, compactDumps(.object([
                    ("gate", .text(gateVersion())),
                    ("judge_from", judgeFrom().map { StatusJSON.text($0) } ?? .null)])))
            case ("GET", "/status"):
                let answer = statusAnswer()
                var pairs = statusPairs(answer)
                // the ladder, read from this room: whoever is asking is looking
                // at the bench, so the rung that opens the bench is taken. The
                // no-world answer carries its own step and neither names a room.
                if !answer.noWorld, let at = pairs.firstIndex(where: { $0.0 == "next" }) {
                    pairs[at].1 = .text(answer.servingNext)
                }
                let saidNext = answer.noWorld ? answer.next : answer.servingNext
                if let ready = commandIn(saidNext) ?? commandIn(answer.then) {
                    pairs.append(("command_to_run", .text(ready)))
                }
                serveJSON(conn, compactDumps(.object(pairs)))
            case ("POST", "/verdict"):
                // the whole declared list, judged with the active file replaced
                // by the editor's unsaved text: cross-file, on this side, so the
                // page never says holds where a hook would refuse
                let w = servedWorld()
                let text = String(decoding: asked.body, as: UTF8.self)
                let base = w.facts.map { (absPath($0) as NSString).deletingLastPathComponent }
                    ?? FileManager.default.currentDirectoryPath
                let active = servePick(w, asked.query)
                let d = scratchDir("gate-bench-")
                let layout = w.layout?.manifest
                let formsHere = Set((w.layout?.rows ?? []).filter { $0.role == "forms" }
                    .map { $0.path })
                var paths: [String] = []
                for (name, p) in benchFilesOf(w) {
                    if p != active && !FileManager.default.fileExists(atPath: p) { continue }
                    let tp = (d as NSString).appendingPathComponent(
                        name.replacingOccurrences(of: "/", with: "__"))
                    let body = p == active ? text : (readText(p) ?? "")
                    try? body.write(toFile: tp, atomically: false, encoding: .utf8)
                    // the layout declares protocols and the policy carries a
                    // typeName, and the plain court refuses both on sight: each
                    // has a guard of its own, and listing them here turned every
                    // row into a refusal
                    if p != layout && !formsHere.contains(name)
                        && absPath(p) != absPath(policyPathOf(w) ?? "") {
                        paths.append(tp)
                    }
                }
                // `courtSays` names the court itself: passing it again made the
                // judge take `judge` for a file, and a run with a file that is
                // not there says nothing about the files that are
                let raw = courtSays(paths)
                var refusals = judgedRefusals(raw).map {
                    (address: $0.address.replacingOccurrences(of: "__", with: "/"),
                     claim: $0.claim)
                }
                let sources = oneStream(w, benchFilesOf(w))
                    .filter { $0.1 == active || FileManager.default.fileExists(atPath: $0.1) }
                    .map { (($0.0 as NSString).lastPathComponent,
                            $0.1 == active ? text : (readText($0.1) ?? "")) }
                if sources.count > 1 {
                    refusals = attributeRefusals(refusals, sources)
                } else {
                    for (name, src) in sources {
                        refusals = refineAddresses(src, refusals, name)
                    }
                }
                // the same guards the terminal runs, over the text in the editor
                refusals += duplicateGuardsOver(sources)
                refusals += entryGuardsOver(sources)
                let typedLayout = active == layout ? text : nil
                let liveRows = typedLayout.map { layoutRowsFull(base, said: $0).rows }
                var typed: [String: String] = [:]
                for (name, p) in benchFilesOf(w) where p == active && formsHere.contains(name) {
                    typed[name] = text
                }
                var size: [String: Int] = [:]
                refusals += manifestGuards(w, liveRows: liveRows, liveText: typedLayout)
                refusals += formsGuards(w, &size, live: typed)
                refusals += policyGuards(w) + stdlibGuards(w) + vendoredGuards(w)
                refusals += takenJudgeGuard(w) + codeownersPairGuards(w)
                let times = matches("([\\d.]+) ms", raw).compactMap { $0.first }
                // AND THE WIDTH OF IT: the judge counts what it checked and says
                // so, and dropping that left a green over several files saying
                // only `judged together`, which is a verdict with no measure
                let measured = matches("(\\d+) declarations · (\\d+) lookups · (\\d+) premises",
                                       raw).first
                serveJSON(conn, compactDumps(.object([
                    ("verdict", .text(refusals.isEmpty ? "holds" : "refused")),
                    ("refusals", .list(refusals.map {
                        .object([("address", .text($0.address)), ("claim", .text($0.claim))]) })),
                    ("declarations", measured.map { StatusJSON.raw($0[0]) } ?? .null),
                    ("premises", measured.map { StatusJSON.raw($0[2]) } ?? .null),
                    ("judge_ms", times.last.map { StatusJSON.raw($0) } ?? .null)]),
                    ascii: true))
                // ── AND THE PANEL DOES NOT GROW ON SOMEBODY'S DISK: one
                // directory per keystroke, removed none, thirty-four thousand
                // standing in the temp of the machine this was written on
                try? FileManager.default.removeItem(atPath: d)
            case ("PUT", "/declare"):
                // ── AND THE GESTURE IS A ROW, WRITTEN WHERE YOU CAN READ IT.
                // This page may not hold state the files do not hold: a button
                // that changed the world through a channel outside it would be
                // exactly the drift this tool exists against. So declaring is
                // the verb already spelled, and the answer says which file it
                // wrote and at which line, so the panel can put you in front of
                // the line rather than announce it in a bar that fades.
                let w = servedWorld()
                let rel = asked.query["f"] ?? "", role = asked.query["role"] ?? ""
                var pairs: [(String, StatusJSON)] = []
                if !undeclaredHere(w).contains(rel) {
                    pairs = [("asks", .raw("true")),
                             ("note", .text("\(rel) is not an undeclared file here"))]
                } else if !STATUS_ROLES.contains(where: { $0.0 == role }) {
                    pairs = [("asks", .raw("true")),
                             ("roles", .object(STATUS_ROLES.map { ($0.0, .text($0.1)) })),
                             ("note", .text("a row says which court reads the file, and "
                                          + "this says none"))]
                } else {
                    let dir = layoutDir(w) ?? "."
                    let full = (dir as NSString).appendingPathComponent(rel)
                    let (mp, refused) = declareSideHere(full, "Mine", role, nil)
                    if let refused = refused {
                        pairs = [("asks", .raw("true")), ("note", .text(refused))]
                    } else {
                        let means = STATUS_ROLES.first(where: { $0.0 == role })?.1 ?? ""
                        pairs = minePairs((full as NSString).lastPathComponent, mp ?? "",
                                          role, means)
                        let (rows, _) = layoutRowsFull(dir)
                        if let mp = mp, let said = rows.first(where: { $0.path == rel }) {
                            pairs.append(("wrote_in", .text(relPath(mp, dir))))
                            pairs.append(("at_line", .raw(String(said.line))))
                        }
                    }
                }
                let wrote = pairs.contains(where: { $0.0 == "wrote_in" })
                serveSay(conn, wrote ? 200 : 400, "application/json",
                         Data(compactDumps(.object(pairs)).utf8))
            case ("PUT", "/value"):
                // ── SAYING A VALUE IS WRITING A DECLARATION IN A FILE OF MINE.
                // The bench could show what a world holds and never let anybody
                // answer: a table you may read and not write in. Answering does
                // not edit the world that shipped the name, it puts your own
                // declaration in your own file, which is what an override has
                // always been.
                let w = servedWorld()
                let name = asked.query["name"] ?? "", to = asked.query["to"] ?? ""
                func refuseValue(_ why: String) {
                    serveSay(conn, 409, "application/json", Data(compactDumps(.object([
                        ("asks", .raw("true")), ("note", .text(why))])).utf8))
                }
                guard matchAt(name, "\\w+$") != nil, matchAt(to, "-?\\d+$") != nil,
                      let said = Int(to) else {
                    refuseValue("a value is a name and a number")
                    break
                }
                let mine = myFormsFiles(w)
                if mine.isEmpty {
                    refuseValue("no file of yours is read by the where court yet, so there is "
                              + "nowhere for your answer to live. Make one and say so: "
                              + "gate mine my-values.swift --role forms")
                    break
                }
                if mine.count > 1 {
                    refuseValue("you present more than one file to that court, "
                              + mine.map { ($0 as NSString).lastPathComponent }
                                    .joined(separator: ", ")
                              + ", and this cannot choose between them")
                    break
                }
                let path = mine[0]
                let wrote = "public typealias \(name) = \(spellNumber(said))"
                var lines = (readText(path) ?? "").components(separatedBy: "\n")
                let at = lines.firstIndex(where: {
                    matchAt($0.trimmingCharacters(in: .whitespaces),
                            "public typealias " + name + " = ") != nil })
                if let at = at {
                    lines[at] = wrote
                } else if let last = lines.last, last.isEmpty {
                    lines[lines.count - 1] = wrote
                    lines.append("")
                } else {
                    lines.append(wrote)
                }
                try? lines.joined(separator: "\n").write(toFile: path, atomically: true,
                                                         encoding: .utf8)
                serveJSON(conn, compactDumps(.object([
                    ("wrote", .text(wrote)),
                    ("file", .text(relPath(path, layoutDir(w) ?? "."))),
                    ("line", .raw(String((at ?? (lines.count - 1)) + 1)))])))
            case ("PUT", "/world"):
                // ── A WRITE NAMES ITS FILE OR IT DOES NOT HAPPEN. Reading may
                // fall back to something sensible; writing may not. In a world
                // laid out entirely by manifest the fallback is the FIRST file
                // that exists, which is the manifest, so a PUT with an empty
                // name overwrote the document that says what the world is. The
                // writable names are the bench's own list and nothing else.
                let w = servedWorld()
                let text = String(decoding: asked.body, as: UTF8.self)
                let named = Dictionary(benchFilesOf(w).map { ($0.0, $0.1) },
                                       uniquingKeysWith: { a, _ in a })
                guard let p = named[asked.query["f"] ?? ""] else {
                    serveSay(conn, 404, nil, Data())
                    break
                }
                if p == personalPathOf(w) {
                    writePersonal(w, text)      // empty means gone, not an empty file
                } else {
                    try? text.write(toFile: p, atomically: true, encoding: .utf8)
                }
                serveSay(conn, 200, nil, Data())
            default:
                serveSay(conn, 404, nil, Data())
            }
        }
        if ProcessInfo.processInfo.environment["GATE_SPAWN_LEDGER"] == "1" {
            err("gate-cli: spawns \(SPAWNS - spawnsBefore) this request\n")
        }
        gateClose(conn)
    }
}

// ── WHAT IS ACTUALLY RUNNING, said by the thing that runs. The identity of a
// court is its bytes, and the court that sits here is this binary: the vein
// carries the judge in-process, so the digest it names is its own rather than a
// file that judged nothing. The revision beside it is the corpus the court was
// compiled from, and both are checkable: build at that pin and run the battery
// against what you get. The linker is not byte-stable, so the hash names what
// is here and the rebuild is the check.
if args.first == "--version" || args.first == "-v" || args.first == "version" {
    let mine = URL(fileURLWithPath: CommandLine.arguments[0]).resolvingSymlinksInPath().path
    let digest = FileManager.default.contents(atPath: mine).map { sha256Hex($0) } ?? ""
    let short = "sha256:" + String(digest.prefix(12))
    let came = judgeFrom()
    if args.contains("--json") {
        var pairs: [(String, StatusJSON)] = [
            ("command", .text("version")), ("gate", .text(gateVersion())),
            ("judge", .text(short)),
        ]
        pairs.append(("judge_from", came.map { StatusJSON.text($0) } ?? .null))
        out(compactDumps(.object(pairs)) + "\n")
        exit(0)
    }
    var lines = ["gate " + gateVersion() + " · judge " + short + " (canon v2)"]
    if case .object(let shape) = courtShape(),
       case .raw(let count)? = shape.first(where: { $0.0 == "lines" })?.1 {
        lines.append("  the court is " + count + " lines in Judge.swift and WhereJudge.swift"
                   + " and the rest of that repository is worlds it shows itself on, and the "
                   + "theory it comes from")
    }
    if let came = came {
        lines.append("  judge built from verification-is-identification "
                   + String(came.prefix(12)) + ". `bin/build-cli.sh` builds the same court: "
                   + "check yours by running the battery against it. The linker is not "
                   + "byte-stable, so the hash names what is here and is not the check")
    } else {
        // ── AND WHERE THE PROVENANCE IS MISSING, IT IS SAID. Bytes say what a
        // thing IS and never what it was made from, so a judge with no `.from`
        // beside it can name its own hash and nothing else. Printing the hash
        // and stopping there reads as "there is nothing more to tell", which is
        // the one gloss this tool may not make about its own one dependency.
        lines.append("  judge built from verification-is-identification: the revision "
                   + "is not recorded beside this binary. `bin/build-cli.sh` writes it "
                   + "down as it builds; a judge carried in without it names its own "
                   + "bytes and nothing about where they came from")
    }
    out(lines.joined(separator: "\n") + "\n")
    exit(0)
}

if args.first == "serve" {
    serveDoor(args)
}

// an argv this binary never claimed: refuse loudly rather than guess. The
// python side forwards carried veins alone, so reaching here is a defect.
err("gate-cli: uncarried argv: " + args.joined(separator: " ") + "\n")
exit(66)
