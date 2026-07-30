// gate stdlib readme v1: the letter a repository is met with
// role: forms
// opens: bare
//
// Rule for this page: a line either subtracts a piece of drift, or it is cut.
// Each line says what stops being possible in the repository holding it.
// A word is introduced where it is first used. No line explains the reader to
// themselves.

// ── what this is, and why you are reading it ──
//
// Your repository is full of sentences nobody checks. CODEOWNERS says who owns
// which folder. A schema says what a field holds. A rota says who is on call.
// Each was true the day somebody wrote it, and nothing tells you the day it
// stopped.
//
// One case, to be concrete. CODEOWNERS hands `/src/api` to @alice. The folder was
// renamed to `/services/api` in the spring. The rule now matches nothing, reviews
// still go to Alice, and no tool anywhere reports a problem. You find out at an
// audit, or the day somebody merges what nobody reviewed.
//
// That gap has a name: drift. A sentence that was true, quietly stopped being
// true, and still gets obeyed.
//
// The usual cure is to pick one place and call it the source of truth. But the
// folder was renamed in a pull request that never read CODEOWNERS; a file everyone
// must keep current is a chore that belongs to everyone, so it belongs to nobody;
// and the chosen file goes stale like any other. gate starts from the opposite
// fact: there is no source. The team that owns the folders declares them, once.
// The review rule declares the folder it points at. Two declarations about one
// folder cannot differ in silence: they are equal, or you get the line and both
// names.
//
// That changes who has to notice. Today you learn about the rename when reviews
// start landing on the wrong person, and the renaming team learns about your rule
// at the audit, if ever. Here the difference is checked whenever anybody asks: by
// hand, on a commit, in CI. A break names its line and both names, so the map of
// who might break what leaves your head. And the rename that would break your rule
// meets your rule inside the pull request that makes the rename. They can still
// merge it, but not without knowing. Being forgotten is what stops being possible
// here.
//
// The check is one lookup per claim and nothing else: no search, no solver, no
// build. It takes milliseconds on a real repository, and it still takes
// milliseconds when the repository is ten times the size.
//
// ── what gate put in your repository, and how to take it out ──
//
// Five files and one git setting. Nothing else was read, moved or rewritten, and
// this tool has no network access at all.
//
//     readme.swift          this letter
//     verbs.swift           every verb, and what each one touches
//     forms-tool.swift      the words those two are written in
//     gate.manifest.swift   the layout: one row per file, and nothing is here
//                           without a row
//     .githooks/pre-commit  re-reads the claims before a commit, so one that
//                           stopped holding stays out of history
//     core.hooksPath        the git setting pointing at that hook; the line that
//                           restores it was printed the moment it changed
//
// Delete a file and its row and it is gone, with nothing left behind. Commit the
// five and the entry is part of this repository's history. None of
// this needed anybody's permission, and nothing you write reaches your
// colleagues until you commit it.
//
// ── a first word costs nothing here ──
//
// If you are reading this in the bench (`gate serve`: this file on the left, the
// verdict on the right, re-read as you type), the cheapest thing to try is on the
// screen already. Beside this file it lists `my.swift`, your own world, kept in a
// separate git on this machine and never in the repository you share. That file
// does not exist until you write in it; nothing is stored for somebody who said
// nothing. Write one claim and it is judged, with everything else here, on every
// keystroke. Clear it and it is gone.
//
// BREAK IT. Trying costs nothing here: a claim that does not hold is never written
// to disk, and a refusal from the judge (the program that reads the claims) names
// a line and not a person. The foot of this file says how to restore what shipped.
// Then break the reference beside this file: set `Does = Writes` on a verb that
// promises to change nothing, and the certificate under it refuses at its own line.
//
// ── what this repository already says, before anything is translated ──
//
//     gate findings
//
// It translates nothing and uploads nothing: it reads this repository's git
// history and prints what is true of it, in sentences. «Access files were
// touched by three people over five hundred commits; none of those edits was
// checked.» A repository with little history has little to say, and the output
// says that instead. Every sentence is marked read, not judged: no court sat on
// it. It hands you the reading; the judging waits for facts you declare.
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
// Those records are Swift declarations, which is why two arbiters can read the
// same file: the judge on every keystroke, and the Swift compiler in your CI when
// you want the slow, total answer. Neither can be talked round.
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
