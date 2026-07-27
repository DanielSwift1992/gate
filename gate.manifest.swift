// GATE'S OWN WORLD, declared the way gate asks every world to declare itself.
//
// A tool that refuses a world which has not declared itself had not declared
// its own. Its facts about its own surface — the palette it paints with, the
// ladder of lengths its page is spaced on, the atoms its bench is made of —
// sat on a shelf, shown to operators as reference, because there was nowhere
// else to put them. They were never reference. They are this world's records,
// and here they are said to be.
//
// WRITTEN THE WAY EVERY RECORD IS WRITTEN. The columns are AXES to declared
// atoms, and the one string is the `typeName` literal that spells a name — the
// single allowance this world makes. A revision is an atom of its own, so two
// rows taken at the same revision say the same NAME, not the same text.
public protocol Role {}
public enum WorldFile: Role {}
public enum SeamFile: Role {}
public enum FormsFile: Role {}
public enum JudgeFile: Role {}

public protocol Mine {}

// The forms this bench is written in, and the certificates over them. Judged by
// the where court, which reads the equalities: break one and `gate status` in
// this repository refuses at the line, the same as in yours.
public enum BenchAtoms: Mine {
    public typealias Kind = FormsFile
}
extension BenchAtoms { public static var typeName: String { "stdlib/bench-atoms.swift" } }
public enum BenchMetrics: Mine {
    public typealias Kind = FormsFile
}
extension BenchMetrics { public static var typeName: String { "stdlib/bench-metrics.swift" } }
public enum BenchPalette: Mine {
    public typealias Kind = FormsFile
}
extension BenchPalette { public static var typeName: String { "stdlib/bench-palette.swift" } }

// The words this tool hands to whoever uses it: they arrive in an operator's
// repository as the header of whatever gate emits, so they are this world's to
// answer for and not somebody's reference shelf.
public enum FormsContract: Mine {
    public typealias Kind = FormsFile
}
extension FormsContract { public static var typeName: String { "stdlib/genre-contract.swift" } }
public enum FormsGrants: Mine {
    public typealias Kind = FormsFile
}
extension FormsGrants { public static var typeName: String { "stdlib/genre-grants.swift" } }
public enum FormsOrganization: Mine {
    public typealias Kind = FormsFile
}
extension FormsOrganization { public static var typeName: String { "stdlib/genre-organization.swift" } }
public enum FormsReference: Mine {
    public typealias Kind = FormsFile
}
extension FormsReference { public static var typeName: String { "stdlib/genre-reference.swift" } }
public enum GitAtoms: Mine {
    public typealias Kind = FormsFile
}
extension GitAtoms { public static var typeName: String { "stdlib/git-atoms.swift" } }

// AND THE ONE THING THIS WORLD TOOK. The judge is a view of the corpus the way
// this world is a view of these facts — `bin/build-judge.sh` clones at a
// revision, builds, and writes the revision down beside the binary, which is
// the taking verb spelled in sh.
//
// SELF-APPLICATION IS NOT SELF-CERTIFICATION. The judge does not judge the
// judge: no self-reference is the floor this whole theory stands on, and a
// court that certified itself would be worth nothing. This row is accounting,
// not a verdict. What holds it is a build anybody can repeat — take the pin,
// run the script, compare the bytes — and that check lives outside this world
// on purpose. gate lives under its own court everywhere a court is possible,
// and this line is the one place where it is not.
public protocol Theirs {}
public enum Rev_vi_0fd0b38 {}
extension Rev_vi_0fd0b38 { public static var typeName: String { "verification-is-identification@0fd0b38" } }
public enum TheJudge: Theirs {
    public typealias Kind = JudgeFile
    public typealias At = Rev_vi_0fd0b38
}
extension TheJudge { public static var typeName: String { "bin/gate-judge" } }
