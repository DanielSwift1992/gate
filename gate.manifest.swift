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
public enum CarriedFile: Role {}

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
public enum BenchRegisters: Mine {
    public typealias Kind = FormsFile
}
extension BenchRegisters { public static var typeName: String { "stdlib/bench-registers.swift" } }

// The words this tool hands to whoever uses it: they arrive in an operator's
// repository as the header of whatever gate emits, so they are this world's to
// answer for and not somebody's reference shelf.
public enum FormsContract: Mine {
    public typealias Kind = FormsFile
}
extension FormsContract { public static var typeName: String { "stdlib/forms-contract.swift" } }
public enum FormsGrants: Mine {
    public typealias Kind = FormsFile
}
extension FormsGrants { public static var typeName: String { "stdlib/forms-grants.swift" } }
public enum FormsOrganization: Mine {
    public typealias Kind = FormsFile
}
extension FormsOrganization { public static var typeName: String { "stdlib/forms-organization.swift" } }
public enum FormsReference: Mine {
    public typealias Kind = FormsFile
}
extension FormsReference { public static var typeName: String { "stdlib/forms-reference.swift" } }
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

// AND THE EDITOR THIS BENCH IS WRITTEN WITH. It arrived the way anything of
// somebody else's should: named, versioned, and unchanged — its own first line
// says CodeMirror 5.65.16, where it came from, its licence, and that it is
// vendored unmodified. Nothing here judges it and nothing here could: it is
// held by that name and that version, and by a copy anybody can fetch and
// compare. Leaving it unlisted would have meant the one dependency an operator
// actually types into was the one this world never accounted for.
public enum Rev_codemirror_5_65_16 {}
extension Rev_codemirror_5_65_16 { public static var typeName: String { "codemirror@5.65.16" } }
public enum TheEditor: Theirs {
    public typealias Kind = CarriedFile
    public typealias At = Rev_codemirror_5_65_16
}
extension TheEditor { public static var typeName: String { "codemirror.js" } }
public enum TheEditorSheet: Theirs {
    public typealias Kind = CarriedFile
    public typealias At = Rev_codemirror_5_65_16
}
extension TheEditorSheet { public static var typeName: String { "codemirror.css" } }
public enum VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeXwngzrqaVendoredFormsOrganization: Mine {
    public typealias Kind = FormsFile
}
extension VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeXwngzrqaVendoredFormsOrganization { public static var typeName: String { "../../../../var/folders/28/krfcw4517h194r1z99mhh8q80000gn/T/gate-smoke-xwngzrqa/vendored/forms-organization.swift" } }
public enum VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeXwngzrqaDemoworldFormsOrganization: Mine {
    public typealias Kind = FormsFile
}
extension VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeXwngzrqaDemoworldFormsOrganization { public static var typeName: String { "../../../../var/folders/28/krfcw4517h194r1z99mhh8q80000gn/T/gate-smoke-xwngzrqa/demoworld/forms-organization.swift" } }
public enum VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeXwngzrqaDemoFirstFormsOrganization: Mine {
    public typealias Kind = FormsFile
}
extension VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeXwngzrqaDemoFirstFormsOrganization { public static var typeName: String { "../../../../var/folders/28/krfcw4517h194r1z99mhh8q80000gn/T/gate-smoke-xwngzrqa/demo-first/forms-organization.swift" } }
public enum Rev_a1b2c3d {}
extension Rev_a1b2c3d { public static var typeName: String { "a1b2c3d" } }
public enum VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeXwngzrqaSubscribeSdk: Theirs {
    public typealias Kind = SeamFile
    public typealias At = Rev_a1b2c3d
}
extension VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeXwngzrqaSubscribeSdk { public static var typeName: String { "../../../../var/folders/28/krfcw4517h194r1z99mhh8q80000gn/T/gate-smoke-xwngzrqa/subscribe/sdk.swift" } }
public enum VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeH2MtncniVendoredFormsOrganization: Mine {
    public typealias Kind = FormsFile
}
extension VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeH2MtncniVendoredFormsOrganization { public static var typeName: String { "../../../../var/folders/28/krfcw4517h194r1z99mhh8q80000gn/T/gate-smoke-h2mtncni/vendored/forms-organization.swift" } }
public enum VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeH2MtncniDemoworldFormsOrganization: Mine {
    public typealias Kind = FormsFile
}
extension VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeH2MtncniDemoworldFormsOrganization { public static var typeName: String { "../../../../var/folders/28/krfcw4517h194r1z99mhh8q80000gn/T/gate-smoke-h2mtncni/demoworld/forms-organization.swift" } }
public enum VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeH2MtncniDemoFirstFormsOrganization: Mine {
    public typealias Kind = FormsFile
}
extension VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeH2MtncniDemoFirstFormsOrganization { public static var typeName: String { "../../../../var/folders/28/krfcw4517h194r1z99mhh8q80000gn/T/gate-smoke-h2mtncni/demo-first/forms-organization.swift" } }
public enum VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeH2MtncniSubscribeSdk: Theirs {
    public typealias Kind = SeamFile
    public typealias At = Rev_a1b2c3d
}
extension VarFolders28Krfcw4517H194R1Z99Mhh8Q80000GnTGateSmokeH2MtncniSubscribeSdk { public static var typeName: String { "../../../../var/folders/28/krfcw4517h194r1z99mhh8q80000gn/T/gate-smoke-h2mtncni/subscribe/sdk.swift" } }
