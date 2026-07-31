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
// Your repository is full of sentences that must match something, and nobody
// checks the match. The schema must match the service that writes it. The
// rota must match who actually answers. Each pair held the day somebody
// wrote it down, and nothing tells you the day the two stopped matching.
//
// One case, to be concrete. CODEOWNERS hands `/src/api` to @alice. The folder was
// renamed to `/services/api` in the spring. The rule now matches nothing, reviews
// still go to Alice, and no tool anywhere reports a problem. You find out at an
// audit, or the day somebody merges what nobody reviewed.
//
// That gap has a name: drift. Two records of one fact, coming apart in
// silence, while both still get obeyed.
//
// The usual cure is to pick one place and call it the source of truth. But a
// source has a direction: everything downstream must watch it, and it watches
// nothing. The folder was renamed in a pull request that never read the file.
// A file everyone must keep current is a chore for everyone, so it is a chore
// for nobody, and the chosen file goes stale like any other. gate starts from
// the opposite fact: there is no source, so there is no direction. The team
// that owns the folders declares them, once. The review rule declares the
// folder it points at. Two declarations about one folder cannot differ in
// silence. Either they are equal, or you get the exact point of contact: the
// line, the folder the rule says, and the folder the tree has. A diff compares
// two texts. This compares two claims about one thing.
//
// Today you learn about the rename when reviews land on the wrong person.
// The renaming team learns about your rule at the audit, if ever. Here the
// difference is checked whenever anybody asks: by hand, on a commit, in CI.
//
// So the map of who might break what leaves your head: a break names its own
// line and both sides. A rename that breaks your rule is named inside the
// pull request that renames it. The team can still merge, but knowingly.
//
// And CODEOWNERS is the example. The tool itself is general: two files that
// state one fact, each side declared once, held to each other on every
// change. That is the whole of it. What varies is which pair you point it
// at: a Jira ticket and the TODO that cites it, k8s RBAC and the cluster it
// describes, an API contract and a client in another language.
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
// that prints what shipped, for comparing or restoring by hand.
//
// (Reading this as a plain file instead? Run `gate serve` in this repository:
// it starts a local page in your browser, this file on the left, the live
// verdict on the right.)
//
// Beside this file the page lists `my.swift`: the one file here that is not
// part of this repository. You are already half of several pairs: the things
// you check by hand because nobody else will. my.swift is where your half
// gets written down, and from then on every change here is checked against
// it, with nobody's agreement needed. It lives in a
// separate git on this machine, no clone or colleague ever sees it, and it
// does not exist until you write in it. Clear it and it is gone.
//
// ── find your drift ──
//
// Yours is wherever two places state one fact. Take a thing you shipped
// this month and ask: where is this written down, and where else? Who
// checks the two against each other, and when did anybody last do it? The
// pairs you cannot answer for are your drift, and every team has them: the
// schema and the service that writes it, the contract and the client, the
// rota and the pager, the config nobody dares delete.
//
// You are never looking for an object, only for pairs: one fact always has
// more than one record. And the loudest marker is anything that calls itself
// the source of truth: a self-declared source is the record nobody compares
// to the others any more, so that is usually where drift collects.
//
// The quick first look is one command, over the git history already in
// this clone:
//
//     gate findings
//
// It prints plain sentences: «3 people changed these facts across 500
// commits, and nothing checked those edits: there is no hook and no
// workflow in this repository.» Nothing to set up, and nothing judged
// yet: these are readings, not verdicts.
//
// Something drifts? Gate it.
//
// ── gate it ──
//
// To gate a pair is to state your half of it in records, once, and publish
// it into the judged set. From then on it is checked against everything
// else here on every change, and the other side sees it in their own next
// check.
//
// Where your half already lives in a table, one command translates it. For
// CODEOWNERS:
//
//     gate import codeowners CODEOWNERS --tree .
//
// It reads your file and prints records from it. Your file stays what it
// was, still the input, and `gate export` prints it back byte for byte, so
// the translation provably dropped nothing. The first refusal is usually
// a rule that stopped being true long ago and has been quietly obeyed
// since.
//
// Where there is no table, you write the records yourself. Rules are
// translated by hand, once. They are small, and they are yours to read.
// That is the upkeep, all of it.
//
// Those records are Swift declarations, so the same file is read by the
// judge on every keystroke and, in CI, by the Swift compiler. Two
// independent readers, and both read the file and nothing else.
//
// ── what this does not touch ──
//
// The judge compares records to each other. It does not know what you
// meant, and it never rules on whether a rule should say what it says. When
// a rule and your intention disagree, the disagreement is yours to settle,
// and nothing here settles it for you.
//
// Every command this tool accepts, and what each one changes: `verbs.swift`,
// beside this file, judged with it. The promises at its foot are what let you
// run any of this on a clone you care about.
//
// Something drifts? Gate it.
