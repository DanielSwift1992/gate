// gate stdlib readme v1: the letter a repository is met with
// role: forms
// opens: bare
//
// Rule for this page: a line either subtracts a piece of drift, or it is cut.
// Each line says what stops being possible in the repository holding it.
// A word is introduced where it is first used. No line explains the reader to
// themselves.

// ── what this is ──
//
// git verifies bytes: change one and the hash changes, and any clone can check
// it. Nothing verifies the words in a repository. A CODEOWNERS was true on the
// day it was written; the day it stops being true is recorded nowhere. The same
// holds for a schema, a rota, a list of who may deploy.
// Here those words are claims. A program called the judge re-reads every claim
// when a file changes and answers with a line number; it does nothing else. A
// claim that stops holding is named at its line the moment it happens, not
// months later by an audit.
//
// ── the one thing worth running first ──
//
//     gate findings
//
// It translates nothing and uploads nothing: it reads this repository's git
// history and prints what is true of it, in sentences. «Access files were
// touched by three people over five hundred commits; none of those edits was
// checked.» A repository with little history has little to say, and the output
// says that instead. Every sentence is marked read, not judged: no court sat on
// it. It gives you the reading, and leaves the judging to a world you declare.
//
// ── everything here is here because a row says so ──
//
// Entry left five files and one git setting, all six named: this letter, the
// words it is written in, the reference beside it, the layout that declares
// them, a pre-commit hook, and `core.hooksPath`, which points git at that hook.
// The hook re-reads the claims before each commit, so a claim that stopped
// holding stays out of history. The line that restores the setting was printed
// when it changed. Everything else in the repository was left exactly as it
// was, and this tool has no network access at all.
//
// Each of those files is here because a row in the layout names it, and deleting
// the row deletes it. You can do all of this alone: what you write reaches your
// colleagues when you commit it, and the personal world below stays on this
// machine either way.
//
// ── a first word costs nothing here ──
//
// `gate serve` opens the bench: this file on the left, the verdict on the
// right, re-read as you type. Beside this file it lists `my.swift`: your own
// world, kept in a separate git on this machine, never in the repository you
// share. The file does not exist until you write in it; nothing is stored for
// somebody who said nothing. Write one claim and it is judged beside the shared
// world on every keystroke. Clear it and it is gone.
//
// BREAK IT. Trying costs nothing here: a claim that does not hold is never
// written to disk, a refusal names a line and not a person, and the foot of
// this file says how to restore what shipped. Then break the reference beside
// this file: set `Does = Writes` on a verb that promises to change nothing, and
// the certificate under it refuses at its own line.
//
// ── the line that has not been true for months ──
//
// If this repository keeps a CODEOWNERS, `gate import codeowners CODEOWNERS
// --tree .` turns it into records, and the first refusal it prints is usually a
// rule that stopped being true long ago and has been quietly obeyed since.
// Tables arrive the same way: a column is an axis, a row is a record, and
// `gate export` prints them back byte for byte. Rules are translated by hand,
// once; they are small, and they are yours to read.
//
// ── and what this does not touch, said plainly ──
//
// Whether a rule should say what it says is not drift, and nothing here rules
// on it. The judge holds words to each other; it does not know what you meant.
// The day the two disagree, the disagreement is yours to settle, and nothing
// here pretends to settle it for you.
//
// The verbs, what each one touches and which court it calls: `verbs.swift`,
// beside this file, judged with it. The promises at its foot are what let you
// run any of this on a clone you care about.
