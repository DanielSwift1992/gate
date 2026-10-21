// gate stdlib manifest v1: the head a layout is born with
// role: gate's own
// speaks-for: the-tool
//
// This page keeps the installed Kind bindings and the text this tool WRITES
// when a world needs a layout. The template lives here so that both carriers
// write the same one: a template kept in two places is two texts the day
// somebody improves one of them.
//
// The card above is the shelf's, not the world's: `role:` and
// `speaks-for:` are how a page tells this tool what it is. The line below
// says where the card ends, so what travels is read by a mark in the page
// rather than by counting lines, and `gate stdlib show manifest` shows you
// both halves as they are.
//
// The installed Kind bindings stay on the shelf, above the world template.
public enum FormsReaderV1: Role {}
public enum OrganizationReaderV1: Role {}
public enum CarriedReaderV1: Role {}
public enum FormsFile: Role {
    public typealias Reader = FormsReaderV1
}
public enum WorldFile: Role {
    public typealias Reader = OrganizationReaderV1
}
public enum CarriedFile: Role {
    public typealias Reader = CarriedReaderV1
}

// The publication reader takes a pinned catalog of doors and worlds.
public enum CatalogReaderV1: Role {}
public enum CatalogFile: Role {
    public typealias Reader = CatalogReaderV1
}

// ── what is written into a world begins here ──
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
