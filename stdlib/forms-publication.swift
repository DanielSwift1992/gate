// gate stdlib forms-publication v1: the declared door of a publication
// role: gate's own
// speaks-for: the-tool
//
// publication/1. A Publication in the root gate.manifest.swift has six axes:
// Id, Entry, Catalog, DraftPolicy, DrawingProfile and Aliases. Id names an atom
// with a typeName literal. Catalog names a Theirs row with Kind = CatalogFile;
// its six-field v2 input record pins the catalog's bytes. Entry names a catalog
// door. Names of the publication, rows and palette are the owner's.
//
// Aliases is (), a single PublicationAlias, or a tuple of those references.
// An alias has Path (an atom spelling a site-relative directory) and To (a door).
// A door has Id, Group, Title, Shown, Reads, Caption, as in the existing catalog.
// Group has Name. Reads names a world with File and Name: File is relative to
// the selected repository and names its manifest directory. Shown names one of
// that world's declared files. Literal atoms keep their text in typeName.
//
// DraftPolicy selects reading only (ReadOnly) or permits browser drafts for the
// plan's writable inputs (ReaderDraft). DrawingProfile is NoDrawing or a pinned
// DrawingProfileFile carrying an owner's resolved CSS/input receipt.
// ReaderDraft carries text and its current reading, including refusals. It never
// grants a disk write or a change to publication structure or taken inputs.
// Count also needs its declared definition context; the delivery
// supplies no implicit Primitive. It makes no claim to complete Language/import/scope semantics.
// A snapshot's structure and sources are read-only. Change the repository and
// publish it again to produce another plan. serve and publish build that plan
// and its responses through the same reader.
public protocol Publication {}
public protocol PublicationAlias {}
public enum ReadOnly {}
public enum ReaderDraft {}
public enum NoDrawing {}
