// One list, three columns: whose source a file is, which court reads it,
// and, for anything taken, the revision it was taken at. gate obeys this
// document and never guesses at a row.
//
// If you are looking for the import: a row is the import. The judged set is
// what this document lists, so a file is read because it has a line here and
// for no other reason. The words the rows are written in are declared below,
// in this file, which is why nothing is fetched.
//
// It is written the way every record in this world is written: each column
// is an axis to a declared atom, and the one string is the `typeName`
// literal that spells a name. A revision is an atom of its own, so two
// rows taken at the same revision say the same name, not merely the same
// text. `Written` names another row: the words a page is written in, so the
// two are read together.
// A row may declare Language: the key of its format 2 namespace, definitions,
// imports and vi-owned scope map. Language cannot replace the Kind's reader.
// docs/LANGUAGES.md states the supported context and the old null-map boundary.
public protocol Role {}
// Each Kind names its installed reader. A world's declaration keeps this choice.
public enum DrawingProfileReaderV1: Role {}
public enum DrawingProfileFile: Role {
    public typealias Reader = DrawingProfileReaderV1
}
//
// ── what a world says when it first takes something begins here ──

// What this world took from somewhere else. A file is listed because this
// side said so, and a row here says which file and whose it is. Every taken
// row names the revision it was taken at. This tool has no ranges, so
// nothing here needs a solver.
public protocol Theirs {}
public enum FormsFile: Role {}
public protocol View {}
public enum Bare: View {}

public protocol Mine {}
public enum Readme: Mine {
    public typealias Kind = FormsFile
    public typealias Opens = Bare
}
extension Readme { public static var typeName: String { "readme.swift" } }
public enum FormsTool: Mine {
    public typealias Kind = FormsFile
}
extension FormsTool { public static var typeName: String { "forms-tool.swift" } }
public enum Verbs: Mine {
    public typealias Kind = FormsFile
    public typealias Written = FormsTool
    public typealias Opens = Bare
}
extension Verbs { public static var typeName: String { "verbs.swift" } }
public enum Ownership: Mine {
    public typealias Kind = FormsFile
}
extension Ownership { public static var typeName: String { "ownership.swift" } }
