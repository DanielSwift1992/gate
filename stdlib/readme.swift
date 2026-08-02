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
// rota must match who actually answers. Each pair held the day you or a
// colleague wrote it down, and nothing tells you the day the two stopped
// matching.
//
// One case, to be concrete. CODEOWNERS hands `/src/api` to @alice. The folder was
// renamed to `/services/api` in the spring. The rule now matches nothing, reviews
// still go to Alice, and no tool reports a problem. You find out at an
// audit, or the day a colleague merges what nobody reviewed.
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
// Five files and one git setting, and nothing else was read, moved or
// rewritten. The tool has no network access: no upload, no phoning home.
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
// each other by name. Every line stays inside a small subset of Swift, and
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
// Beside this file the page lists `my.swift`: the one file here that is not
// part of this repository. You are already half of several pairs: the things
// you check by hand because nobody else will. my.swift is where your half
// gets written down. From then on the checking is the judge's, not yours.
// It lives in a separate git on this machine, no clone or colleague sees
// it, and it does not exist until you write in it. Clear it and it is
// gone.
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
// You are looking for pairs, not objects: one fact always has more than
// one record. And the loudest marker is anything that calls itself
// the source of truth: a self-declared source is the record nobody compares
// to the others any more, so that is usually where drift collects.
//
// Gate first the pairs that cross a boundary: two teams, two repositories,
// two languages. A fact drifts where it changes hands.
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
// Something drifts? Gate it
//
// ── gate it ──
//
// To gate a pair: put your half of it in a file here, once. From then on
// every change is checked against it, and the other side sees it the next
// time they check.
//
// If your half is already a table (CODEOWNERS, a CSV), one command puts it
// in. For CODEOWNERS:
//
//     gate import codeowners CODEOWNERS --tree .
//
// Your file stays in place, and whatever read it keeps reading it: what
// enters gate is a second record of the same fact, the kind of pair this
// tool exists to hold. A CSV round-trips: `gate export` prints the tables
// back, and the diff against the originals is empty. A CODEOWNERS is
// judged against your tree as it lands, and the two stay compared: the
// world names its source on its own `from:` line, and every `gate status`
// translates the file again and holds the two together. The first refusal
// is usually a rule that stopped being true long ago and has been quietly
// obeyed since.
//
// If it is not a table, you write it as a file yourself: the same kind of
// file you are reading right now. Rules are translated by hand, once. They
// are small, and they are yours to read. That is the upkeep, all of it.
//
// The same move works between teams. You do not test my API, and I do not
// mock yours. Each side states its half in its own repository, the seam is
// judged, and a disagreement is named at its address on both sides. What
// used to be an integration test is a verdict.
//
// And because it is plain Swift, a second, independent reader exists
// whenever you want one: `swiftc -typecheck` passes on these files as they
// are, with no project and no build.
//
// ── what this does not touch ──
//
// A drifted record is one problem: two spellings of one fact, and the
// judge names the line where they part. What two people mean by a record
// is another problem, and no check turns two readings into one. gate does
// not try. Its one move is to put the agreement in writing before the
// argument: each side states its half in its own file, the judge does the
// comparing from then on, and a meeting is what you hold when the verdict
// says you differ. If CODEOWNERS hands the payments folder to an intern,
// the rule holds and every record agrees with it. Whether it should is a
// claim you can state too: write it as policy, let the other side write
// theirs, and the verdict says if you agree. Agreement here is not
// assumed. It is stated twice, and confirmed.
//
// Every gate command, what it reads and what it writes: `verbs.swift`,
// beside this file, judged with it. Twelve commands carry a certificate at
// its foot saying they change no files, which is why you can run them on a
// clone you care about.
//
// ── death to drift ──
//
// Every pair you gate is one thing you stop keeping in your head. The
// checking does not pile up: each claim is one lookup, so a hundred pairs
// cost what ten did. Once your pairs are in, the picture is concrete: the
// rename goes red on the renamer's screen, not on yours. A new hire's
// access is a one-line diff an owner has to approve. Deleting the old
// config takes an afternoon, not a season of asking around, because the
// readers it still has are a list, not a guess. Nothing got faster. What
// went away is the asking.
//
// Something drifts? Gate it

// Each `== phrase` line below lights that phrase where it stands in this
// page: the words that carry it, for a reader moving fast.
//
// == sentences that must match something
// == That gap has a name: drift.
// == there is no source, so there is no direction
// == checked whenever anybody asks
// == milliseconds on a real
// == Nothing here is built to keep you.
// == half of several pairs
// == the loudest marker
// == Something drifts? Gate it
// == put your half of it in a file here, once
// == That is the upkeep, all of it.
// == rename goes red on the renamer's screen, not on yours.
// == went away is the asking.
