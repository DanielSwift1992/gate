// gate stdlib readme v1: the letter a repository is met with
// role: forms
// opens: bare
//
// EVERY LINE BELOW SUBTRACTS SOMETHING, or it is not here. This page does not
// describe a tool: it says what stops being possible in the repository holding it.
// A word is introduced where it is first used, and no line explains the reader to
// themselves.

// ── what stops being possible here ──
//
// git keeps every byte of a repository honest: change one and the hash says so.
// The WORDS of a repository have no such guarantee. A CODEOWNERS says what was
// true on the day somebody wrote it, and nothing anywhere says the day it
// stopped being true. The same goes for a schema, a rota, a list of who may
// deploy. From here on those words are claims, and every claim is re-read each
// time anything near it is touched, by a reader called the judge: it reads, it
// answers with a line number, and it does nothing else. A word cannot go stale
// here without saying so, at a line.
//
// ── the one thing worth running first ──
//
//     gate findings
//
// Nothing needs translating for that, and nothing is uploaded: it reads this
// repository's own history and says what is true of it in sentences, like «access
// files were touched by three people over five hundred commits, and none of those
// edits was checked». A repository with little history has little to say and says
// that instead. Every sentence is marked read, never judged, because no court sat
// on it: what is subtracted is the reading nobody had time for, not the judging
// nobody asked for.
//
// ── nothing appears here that nobody said ──
//
// Five files and one git setting arrived, all six named: this letter, the words
// it is written in, the whole reference beside it, the layout that declares them,
// a pre-commit hook, and `core.hooksPath`, which points git at that hook. The
// hook re-reads the claims before a commit is made, so a word that stopped
// holding does not get committed; the line that puts the setting back was printed
// the moment it moved. Nothing else was read for its meaning, moved or rewritten,
// and nothing here reaches the network, at any time, for any reason.
//
// A file appearing in a repository with nobody's name on it is the thing being
// subtracted: what is here is here because a row in the layout says so, and
// dropping the row drops it. Nobody else has to agree to any of this. Nothing is
// shared until you commit it, and the personal world below is never shared at all.
//
// ── a first word costs nothing here ──
//
// `gate serve` opens the bench: this file on the left, the verdict on the right,
// re-read as you type. Beside this file it shows `my.swift`, your own world, kept
// in your own git on this machine and never in the repository you share. Until
// you write in it there is no such file: nothing is kept for somebody who has not
// said anything. Write one claim and it is judged beside the shared world on every
// keystroke; clear it and it is gone again.
//
// BREAK IT. What is subtracted here is the cost of trying: a claim that does not
// hold is never written to disk, the judge names a line rather than a person, and
// the foot of every file taken from the shelf says how to put it back. Try the
// reference beside this file too — say `Does = Writes` on a verb that promises to
// change nothing, and the certificate under it refuses at its own line.
//
// ── the line that has not been true for months ──
//
// If this repository keeps a CODEOWNERS, `gate import codeowners CODEOWNERS
// --tree .` turns it into records, and what it usually prints first is a rule
// that stopped being true long ago and has been quietly obeyed since. Tables
// arrive the same way: a column is an axis, a row is a record, and `gate export`
// prints them back byte for byte. Rules are the one thing translated by hand,
// once, because they are small and they are yours to read.
//
// ── and what is not subtracted, said plainly ──
//
// Whether a rule SHOULD have said what it says is not drift and is not touched
// here. This holds words to each other, and it does not know what you meant. The
// day the two disagree, the disagreement is yours to settle: nothing here will
// pretend to have settled it for you.
//
// The verbs, what each one touches and which court it calls: `verbs.swift`, beside
// this file, judged with it. The promises at its foot are what let you run any of
// this on a clone you care about.
