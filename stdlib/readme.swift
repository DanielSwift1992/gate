// gate stdlib readme v1: the readme a repository is met with
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
// The usual cure is to pick one place and call it the source of truth. But a
// source has a direction: everything downstream must watch it, and it watches
// nothing. The folder was renamed in a pull request that never read CODEOWNERS.
// A file everyone must keep current is a chore for everyone, so it is a chore
// for nobody, and the chosen file goes stale like any other. gate starts from
// the opposite fact: there is no source, so there is no direction. The team
// that owns the folders declares them, once. The review rule declares the
// folder it points at. Two declarations about one folder cannot differ in
// silence. Either they are equal, or you get the exact point of contact: the
// line, the folder the rule says, and the folder the tree has. A diff compares
// two texts. This compares two claims about one thing.
//
// That changes who has to notice. Today you learn about the rename when
// reviews land on the wrong person. The renaming team learns about your rule
// at the audit, if ever. Here the difference is checked whenever anybody
// asks: by hand, on a commit, in CI.
//
// So the map of who might break what leaves your head: a break names its own
// line and both sides. A rename that breaks your rule is named inside the
// pull request that renames it. The team can still merge, but knowingly.
//
// The check is one lookup per claim and nothing else: no search, no solver, no
// build. The cost is linear in the number of claims: milliseconds on a real
// repository, and still milliseconds when the repository is ten times the size.
// That is what lets it run on every keystroke and in every commit, with nobody
// waiting on it.
//
// ── what gate put in your repository, and how to take it out ──
//
// Five files and one git setting. Nothing else was read, moved or rewritten.
// The tool has no network access: nothing is uploaded, nothing phones home,
// ever.
//
//     readme.swift          the file you are reading
//     verbs.swift           every gate command, and whether it changes files
//     forms-tool.swift      the Swift types used by the two files above
//     gate.manifest.swift   the list of files the judge reads. No row here,
//                           and the file is not judged
//     .githooks/pre-commit  runs `gate status` before every commit. A red
//                           verdict stops the commit
//     core.hooksPath        the git setting that points at that hook. The
//                           undo command was printed when it was set
//
// Right now all of this exists only on your machine: no sign-off happened,
// and your colleagues see nothing until you commit. To keep it, commit. To
// remove it, delete the five files and run `git config --unset
// core.hooksPath`. Nothing here is built to keep you.
//
// ── break something first ──
//
// The left half of this page is the file you are reading. The right half is
// the verdict, re-read on every keystroke. The file is valid Swift and it
// compiles, but nothing in it runs: there are no functions here, only type
// declarations. Each line that says `X = Y` is a claim, and claims refer to
// each other by name. Everything stays inside a small subset of Swift, and
// the judge reads that subset directly, in milliseconds. No compiler runs
// while you type.
//
// BREAK IT, to watch the check happen.
//
//     1. Open verbs.swift and find `Log`. Its record says `Does = Reads`:
//        the log command reads and never writes.
//     2. Change `Reads` to `Writes`. The record is now false, and the judge
//        refuses on that keystroke: `Writes against Reads`, with the line
//        number. While the verdict is red nothing is saved: on disk the
//        file stays as it was.
//     3. Change it back. Green, and the keystroke is saved: the file on
//        disk changes, `git status` shows it as a normal edit, and you
//        commit it with git as usual. There is no other storage.
//
// readme.swift, verbs.swift and forms-tool.swift each end with the command
// that prints their original, for comparing or restoring by hand.
//
// (Reading this as a plain file instead? Run `gate serve` in this repository:
// it starts a local page in your browser, this file on the left, the live
// verdict on the right.)
//
// Beside this file the page lists `my.swift`: the one file here that is not
// part of this repository. It is for the claims only you care about: write
// down the thing you now check by hand, and every change here is checked
// against it from then on, with nobody's agreement needed. It lives in a
// separate git on this machine, no clone or colleague ever sees it, and it
// does not exist until you write in it. Clear it and it is gone.
//
// ── ask the repository first ──
//
//     gate findings
//
// This is the zero-work look at the problem. It runs on what is already
// here, the git history this clone carries, and prints what is true of it,
// in sentences. «Access files were
// touched by three people over five hundred commits, and none of those edits was
// checked.» A repository with little history has little to say, and the output
// says that instead. Every sentence is marked read, not judged: no check ran on
// it. You get the reading. Judging starts when you declare facts.
//
// ── the line that has not been true for months ──
//
// If this repository keeps a CODEOWNERS, `gate import codeowners CODEOWNERS
// --tree .` turns it into records, and the first refusal it prints is usually a
// rule that stopped being true long ago and has been quietly obeyed since.
// Tables arrive the same way, and `gate export` prints your file back byte for
// byte, to prove the translation lost nothing. Rules are translated by hand,
// once. They are small, and they are yours to read.
//
// Those records are Swift declarations, so two arbiters can read the
// same file: the judge on every keystroke, and the Swift compiler in your CI when
// you want the slow, total answer. Both answer from the file alone.
//
// ── and what this does not touch, said plainly ──
//
// Whether a rule should say what it says is not drift, and nothing here rules
// on it. The judge holds words to each other and does not know what you meant.
// The day the two disagree, the disagreement is yours to settle, and nothing
// here settles it for you.
//
// Every command this tool accepts, and what each one changes: `verbs.swift`,
// beside this file, judged with it. The promises at its foot are what let you
// run any of this on a clone you care about.
