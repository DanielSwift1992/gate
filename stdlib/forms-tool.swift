// gate stdlib forms-tool v1 — the words a tool's own surface is written in
// role: forms
// A verb is a record like any other: what it touches, and which court it calls.
// These are the axes a reference table needs to be a WORLD rather than a list,
// and the one law over them is the promise everything else rests on — that a
// verb which changes nothing may be run on anybody's clone, at any moment.

// WHICH COURT ANSWERS. `plain` reads a world of facts; `where` reads a grammar
// and the certificates over it; some verbs call none at all and say so — an
// observation is not a verdict, and a verb that judges nothing may not wear one.
public protocol Court {}
public enum PlainCourt: Court {}
public enum WhereCourt: Court {}
public enum NoCourt: Court {}

// WHAT IT TOUCHES. Three classes, and the middle one is the honest name for
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

// AN OLDER SPELLING IS NOT A SECOND VERB. A file on somebody's disk is not
// wrong because the tool learned a better word, so the old name stays and says
// what it means — one record, pointing at the one it is a spelling of.
public protocol Spelling {
    associatedtype Means: Verb
}

/// a verb that changes nothing may be run on anybody's clone, at any moment
public protocol Safe {}
public enum Run<V: Verb> {}
extension Run: Safe
where V.Does == Reads {}
