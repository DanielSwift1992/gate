// gate stdlib genre-reference v1 — a reference and the thing it refers to, as
// role: forms
// one judged world.
//
// The drift here is the one everybody has and nobody checks: code cites a
// ticket, a ticket is closed, and the citation stays. Nothing in either system
// can see the other — the tracker does not read the repository, and the
// repository does not read the tracker — so the two copies of "this is still
// open" pull apart quietly, and a reader of the code is told something that
// stopped being true months ago.
//
// A tracked thing becomes a RECORD whose state is an axis; a place in the code
// that cites it becomes a SITE; the citation itself is the seam. It refuses in
// two ways, and both fall out of the grammar rather than a rule written for
// them: a citation of something CLOSED says which state it found against the
// one it needed, and a citation of something that does not exist at all cannot
// read the axis and says so by name.
//
// Deliberately absent: any way to write "this citation is exempt". An exemption
// is a seam a citation could declare itself out of, and then it holds nothing.

public protocol Standing {}
public enum Open: Standing {}
public enum Closed: Standing {}

public protocol Tracked {
    associatedtype State: Standing
}

// where in the code the citation stands — one per site, so a refusal has an
// address in the reader's own file rather than in a generated one
public protocol Site {}

public protocol Cited {}
public enum Cites<Where: Site, What: Tracked>: Close {}
extension Cites: Cited
where What.State == Open {}
