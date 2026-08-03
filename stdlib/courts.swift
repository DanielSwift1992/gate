// gate stdlib courts v1: every court this tool ships, as records
// role: forms
//
// The judge exists twice on purpose: a native binary built from the theory
// corpus, and a port that runs where the binary cannot, in a browser and on
// Windows. Two encodings of one judge agree only under a premise outside
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

// the contract's side: each court names the canon its verdicts are spelled in
public protocol CourtSpoken {
    associatedtype Canon: VerdictCanon
}
public enum PlainVerdicts: CourtSpoken {
    public typealias Canon = CanonV2
}
public enum WhereVerdicts: CourtSpoken {
    public typealias Canon = CanonV2
}

// the carriers' side: what ships, and the file each one is
public protocol CourtCarrier {}
public enum BinaryJudge: CourtCarrier {}
extension BinaryJudge { public static var typeName: String { "bin/gate-judge" } }
public enum PortPlain: CourtCarrier {}
extension PortPlain { public static var typeName: String { "bin/judge.js" } }
public enum PortWhere: CourtCarrier {}
extension PortWhere { public static var typeName: String { "bin/judge-where.js" } }

/// a carrier prints a court's verdicts in the canon the contract states
public protocol CourtCarried {}
public enum Carry<Who: CourtCarrier, What: CourtSpoken, As: VerdictCanon> {}
extension Carry: CourtCarried
where What.Canon == As {}

public typealias Binary_carries_plain = Carry<BinaryJudge, PlainVerdicts, CanonV2>
public typealias Binary_carries_where = Carry<BinaryJudge, WhereVerdicts, CanonV2>
public typealias Port_carries_plain = Carry<PortPlain, PlainVerdicts, CanonV2>
public typealias Port_carries_where = Carry<PortWhere, WhereVerdicts, CanonV2>
