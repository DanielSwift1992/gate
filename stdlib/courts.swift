// gate stdlib courts v1: every court this tool ships, as records
// role: forms
// speaks-for: the-tool
//
// The judge exists more than once on purpose: a native binary built from the
// theory corpus, a port of its plain court that runs where the binary cannot,
// in a browser and on Windows, and the contract's Rust sample built for
// wasm32, a second implementation of the certificate and count courts for
// those same machines. Two encodings of one judge agree only under a premise outside
// either of them (v=i §5.4). For the tool's first week that premise lived
// in a test file: the two halves of this system were held together by a
// third system, which is the failure this tool exists against. So the
// premise is written here, in the words the tool asks of every world: each carrier states which
// verdicts it prints and in which canon, the contract states the canon each
// court is in, and the claim that ties them is judged with the rest of the
// shelf on every keystroke of this file. Change the canon on one side alone
// and the claim goes red at its line, in the panel, not in a test log.
//
// What stays in the battery is the one thing no declaration can prove: that
// the bytes the two carriers print actually match. A bridge from file to
// execution is tested; the pair itself is declared and judged, here.
//
// The carriers below are the whole roster. A judge implementation that is
// not a record on this page is not shipped: adding one is a visible act on
// this file, judged, never a quiet copy.

public protocol VerdictCanon {}
public enum CanonV2: VerdictCanon {}
// the certificate court's normalization canon is four since the corpus
// replays source-defined definition reductions; the count court is asked its
// own question, vi.count.unit-never-plus/1, which the where canon does not
// version. The plain court keeps its canon of two.
public enum CanonV4: VerdictCanon {}
public enum CountQuestion1: VerdictCanon {}

// the contract's side: each court names the canon its verdicts are spelled in
public protocol CourtSpoken {
    associatedtype Canon: VerdictCanon
}
public enum PlainVerdicts: CourtSpoken {
    public typealias Canon = CanonV2
}
public enum WhereVerdicts: CourtSpoken {
    public typealias Canon = CanonV4
}
public enum CountVerdicts: CourtSpoken {
    public typealias Canon = CountQuestion1
}

// the carriers' side: what ships, and the file each one is
public protocol CourtCarrier {}
public enum BinaryJudge: CourtCarrier {}
extension BinaryJudge { public static var typeName: String { "bin/gate-judge" } }
// the company's plain court has its own native carrier, built from the
// showcase's OrganizationCourt at the pin bin/organization-court.from names,
// where the policy it reads is declared (bin/build-organization-judge.sh)
public enum OrganizationBinary: CourtCarrier {}
extension OrganizationBinary { public static var typeName: String { "bin/organization-judge" } }
public enum PortPlain: CourtCarrier {}
extension PortPlain { public static var typeName: String { "bin/judge.js" } }
// the fourth carrier is the contract's Rust sample, a second implementation
// built for wasm32 at the pin bin/court-wasm.from records and carried by
// bin/judge-wasm.js for node and by bin/court-wasm/web for the page. The
// premise that it agrees with the binary is asked of the suite (13/13) and
// of the battery's page-for-page parity, not assumed (v=i §5.4).
public enum WasmCourt: CourtCarrier {}
extension WasmCourt { public static var typeName: String { "bin/judge-wasm.js" } }
// the fifth carrier is the strangler's vein: the same judge sources at the
// same pin (bin/gate-judge.from), with the company's plain court from the
// showcase pin (bin/organization-court.from), compiled into the Swift CLI by
// bin/build-cli.sh, so the court runs in the vein's own process. A verb of
// that CLI which needs the TEXT of a verdict asks the same door in a child of
// itself, because the court prints its lines and leaves on a refusal. The row
// names the text: the binary it builds is never committed.
public enum SwiftVein: CourtCarrier {}
extension SwiftVein { public static var typeName: String { "bin/gate-cli.swift" } }

/// a carrier prints a court's verdicts in the canon the contract states
public protocol CourtCarried {}
public enum Carry<Who: CourtCarrier, What: CourtSpoken, As: VerdictCanon> {}
extension Carry: CourtCarried
where What.Canon == As {}

public typealias Organization_carries_plain = Carry<OrganizationBinary, PlainVerdicts, CanonV2>
public typealias Binary_carries_where = Carry<BinaryJudge, WhereVerdicts, CanonV4>
public typealias Binary_carries_count = Carry<BinaryJudge, CountVerdicts, CountQuestion1>
public typealias Port_carries_plain = Carry<PortPlain, PlainVerdicts, CanonV2>
public typealias Wasm_carries_where = Carry<WasmCourt, WhereVerdicts, CanonV4>
public typealias Wasm_carries_count = Carry<WasmCourt, CountVerdicts, CountQuestion1>
public typealias Vein_carries_plain = Carry<SwiftVein, PlainVerdicts, CanonV2>
public typealias Vein_carries_where = Carry<SwiftVein, WhereVerdicts, CanonV4>
public typealias Vein_carries_count = Carry<SwiftVein, CountVerdicts, CountQuestion1>
