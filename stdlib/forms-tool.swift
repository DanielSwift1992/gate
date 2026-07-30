// gate stdlib forms-tool v1: the types readme.swift and verbs.swift are written in
// role: forms
// A verb is a record like any other: what it touches, and which court it calls.
// These axes make a reference table a world rather than a list. One law stands
// over them: a verb that changes nothing may be run on anybody's clone, at any
// moment.

// Which court a verb calls. `plain` checks facts in a world file. `where`
// checks the grammar and its certificates. Some verbs check nothing and say
// so: an observation is not a verdict, so a verb that judges nothing lists
// no court.
public protocol Court {}
public enum PlainCourt: Court {}
public enum WhereCourt: Court {}
public enum NoCourt: Court {}

// What it touches. Three classes, and the middle one is the honest name for
// what most of this tool does: it writes where you named a file, and nowhere
// else. Reading a repository and leaving it exactly as it was is a claim, so it
// is a class here rather than a habit.
public protocol Touch {}
public enum Reads: Touch {}
public enum Asked: Touch {}
public enum Writes: Touch {}

public protocol Verb {
    associatedtype Does: Touch
    associatedtype Under: Court
}

// An older spelling is not a second verb. A file on somebody's disk is not
// wrong because the tool learned a better word, so the old name stays and says
// what it means: one record, pointing at the one it is a spelling of.
public protocol Spelling {
    associatedtype Means: Verb
}

/// a verb that changes nothing may be run on anybody's clone, at any moment
public protocol Safe {}
public enum Run<V: Verb> {}
extension Run: Safe
where V.Does == Reads {}
