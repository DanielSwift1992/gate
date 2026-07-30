// gate stdlib verbs v1: every verb this tool accepts, as records
// role: forms
// opens: bare
// written in `gate stdlib show forms-tool`
//
// A prose list of verbs drifts from the dispatch the moment either changes,
// and nothing says when. That is a second copy of one truth, met in this
// tool's own documentation. So each verb is a record, judged with the rest,
// and a guard compares the records to the dispatch by name, in both
// directions: a verb with no record is refused, and a record with no verb is
// refused, each at a line. In your clone the guard reads your clone's
// dispatch, the only copy that can lie to you.
//
// It was seeded once from the dispatch, the way a world is seeded from a
// table. From then on this file is the source, and editing it is how the
// answer changes. Read as far down as your question goes.

// ── what a person runs first ──

/// what disagrees right now: judgement over your declared files, in milliseconds
public enum Status: Verb {
    public typealias Does = Reads
    public typealias Under = PlainCourt
}
extension Status { public static var typeName: String { "status" } }
public typealias StatusIsSafe = Run<Status>

/// the older spelling, from git's own vocabulary
public enum Fsck: Spelling {
    public typealias Means = Status
}
extension Fsck { public static var typeName: String { "fsck" } }

/// a repository with a CODEOWNERS, a policy, and one owner reaching past their zone
public enum Demo: Verb {
    public typealias Does = Writes
    public typealias Under = WhereCourt
}
extension Demo { public static var typeName: String { "demo" } }

/// the hook wires itself, and readme.swift lands, yours
public enum Init: Verb {
    public typealias Does = Writes
    public typealias Under = NoCourt
}
extension Init { public static var typeName: String { "init" } }

/// the bench: your world on the left, the verdict on the right, judged as you type
public enum Serve: Verb {
    public typealias Does = Writes
    public typealias Under = PlainCourt
}
extension Serve { public static var typeName: String { "serve" } }

// ── what is true of a repository before anything is translated ──

/// what is true of this clone, in sentences: needs no world and no configuration
public enum Findings: Verb {
    public typealias Does = Reads
    public typealias Under = NoCourt
}
extension Findings { public static var typeName: String { "findings" } }

/// the repository's own history, with no translation at all: any clone carries it
public enum Log: Verb {
    public typealias Does = Reads
    public typealias Under = NoCourt
}
extension Log { public static var typeName: String { "log" } }

/// unwritten links mined from your own git history, before any translation
public enum Survey: Verb {
    public typealias Does = Reads
    public typealias Under = NoCourt
}
extension Survey { public static var typeName: String { "survey" } }

/// what a library has been, observed and never judged: no check ran, so no verdict
public enum Drift: Verb {
    public typealias Does = Reads
    public typealias Under = NoCourt
}
extension Drift { public static var typeName: String { "drift" } }

// ── asking a world ──

/// may this person read this document, checked against the file itself
public enum Check: Verb {
    public typealias Does = Reads
    public typealias Under = PlainCourt
}
extension Check { public static var typeName: String { "check" } }

/// the older spelling of `check`
public enum Ask: Spelling {
    public typealias Means = Check
}
extension Ask { public static var typeName: String { "ask" } }

/// what would break if this happened, and nothing happens
public enum Diff: Verb {
    public typealias Does = Reads
    public typealias Under = PlainCourt
}
extension Diff { public static var typeName: String { "diff" } }

/// the older spelling, when `diff` and `apply` were one word
public enum Change: Spelling {
    public typealias Means = Diff
}
extension Change { public static var typeName: String { "change" } }

/// edits the world, and writes only where the judge holds, like a commit
public enum Apply: Verb {
    public typealias Does = Writes
    public typealias Under = PlainCourt
}
extension Apply { public static var typeName: String { "apply" } }

/// repo policy by the same gates: the author must hold the rank the policy states
public enum Guard: Verb {
    public typealias Does = Reads
    public typealias Under = PlainCourt
}
extension Guard { public static var typeName: String { "guard" } }

/// the forms and axes of a domain, and what two libraries share
public enum Library: Verb {
    public typealias Does = Asked
    public typealias Under = NoCourt
}
extension Library { public static var typeName: String { "library" } }

// ── the two verbs of the manifest, and the third ──

/// I emit it, it is judged, and changing it changes the verdict
public enum MineVerb: Verb {
    public typealias Does = Writes
    public typealias Under = NoCourt
}
extension MineVerb { public static var typeName: String { "mine" } }

/// I took it, at the revision I took it at. There are no ranges anywhere here
public enum TheirsVerb: Verb {
    public typealias Does = Writes
    public typealias Under = NoCourt
}
extension TheirsVerb { public static var typeName: String { "theirs" } }

/// your own world: a claim kept in your git alone, judged beside the shared one
public enum My: Verb {
    public typealias Does = Writes
    public typealias Under = PlainCourt
}
extension My { public static var typeName: String { "my" } }

// ── two sides, and the one court over the pair ──

/// print your side: what you publish, or what your build carries
public enum Declare: Verb {
    public typealias Does = Asked
    public typealias Under = NoCourt
}
extension Declare { public static var typeName: String { "declare" } }

/// the one court over a pair: refused at an address when two declarations part
public enum Seam: Verb {
    public typealias Does = Reads
    public typealias Under = WhereCourt
}
extension Seam { public static var typeName: String { "seam" } }

/// what waits for a word, not what changed: who owes whom a sentence
public enum Attention: Verb {
    public typealias Does = Reads
    public typealias Under = WhereCourt
}
extension Attention { public static var typeName: String { "attention" } }

/// say a divergence is meant, naming what will end it, and it returns by itself
public enum Aside: Verb {
    public typealias Does = Writes
    public typealias Under = NoCourt
}
extension Aside { public static var typeName: String { "aside" } }

// ── carrying facts in and out ──

/// a mechanical translation of your own tables into the world's records
public enum Import: Verb {
    public typealias Does = Writes
    public typealias Under = WhereCourt
}
extension Import { public static var typeName: String { "import" } }

/// the round trip, byte for byte: what came in comes back out
public enum Export: Verb {
    public typealias Does = Asked
    public typealias Under = NoCourt
}
extension Export { public static var typeName: String { "export" } }

/// seeds violations to prove the rule translation against your old checker
public enum Verify: Verb {
    public typealias Does = Reads
    public typealias Under = PlainCourt
}
extension Verify { public static var typeName: String { "verify" } }

// ── what a world says about itself, outward ──

/// claims judged, and how long every commit that touched them has held, replayed
public enum Badge: Verb {
    public typealias Does = Asked
    public typealias Under = PlainCourt
}
extension Badge { public static var typeName: String { "badge" } }

/// the printable audit page
public enum Report: Verb {
    public typealias Does = Asked
    public typealias Under = PlainCourt
}
extension Report { public static var typeName: String { "report" } }

/// the words a world may be written in, printed. Editing a printout adds no word
public enum Stdlib: Verb {
    public typealias Does = Asked
    public typealias Under = NoCourt
}
extension Stdlib { public static var typeName: String { "stdlib" } }

/// the tool, and the revision its judge was built from
public enum Version: Verb {
    public typealias Does = Reads
    public typealias Under = NoCourt
}
extension Version { public static var typeName: String { "version" } }

/// the flag spelling, and `-v`
public enum V: Spelling {
    public typealias Means = Version
}
extension V { public static var typeName: String { "v" } }

// ── and the promise everything else rests on ──
//
// Each line below is a certificate that the verb above it changes nothing.
// Say `Does = Writes` on any of them and its line here is refused: a verb
// cannot be listed among the safe ones and admit to writing in the same file.
// The battery runs every one of them in a world and holds the working copy
// byte-identical afterwards, which is the half no declaration can prove.
//
// `Asked` is the third class and it carries the same promise with one word
// added: nothing is written unless you name a file with `-o`. The battery runs
// those without one and holds the working copy byte-identical too, so the
// difference between `Reads` and `Asked` is what you typed and never what the
// verb decided.
public typealias CheckIsSafe = Run<Check>
public typealias DiffIsSafe = Run<Diff>
public typealias LogIsSafe = Run<Log>
public typealias FindingsIsSafe = Run<Findings>
public typealias SurveyIsSafe = Run<Survey>
public typealias DriftIsSafe = Run<Drift>
public typealias SeamIsSafe = Run<Seam>
public typealias AttentionIsSafe = Run<Attention>
public typealias GuardIsSafe = Run<Guard>
public typealias VerifyIsSafe = Run<Verify>
public typealias VersionIsSafe = Run<Version>
