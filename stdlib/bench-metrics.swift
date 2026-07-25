// gate stdlib bench-metrics v1 — distance as a judged relation.
// The base is the reading line: an instrument for reading measures its
// spacing in the letter it sets. One step is a tenth of that line, and every
// gap on the page is a WHOLE number of steps — so a length is spelled the way
// a number is, on this file's own ladder from Unit, and can be judged like one.
//
// JUDGED HERE: the ladder is monotone; the law of proximity — what belongs
// together stands closer than what does not, and the deeper the kinship the
// tighter the gap; the air is whole reading lines; and the indent is the sum
// of the steps it is made of, not a number of its own.
//
// NOT JUDGED, and said plainly: the price of one step (how dense the page
// reads) and which step a given seam takes are chosen by eye inside the box
// these rules leave. The rules say a section must stand further off than a
// row; they do not say by how much it pleases.

public typealias W2 = Twice<Unit>
public typealias W4 = Twice<W2>
public typealias W8 = Twice<W4>
public typealias W16 = Twice<W8>
public typealias W32 = Twice<W16>

// ── the steps, named for the work each does ──
public typealias Tight = Unit                          // inside one mark
public typealias Snug = W2                             // inside one row
public typealias Near = Plus<Unit, W2>                 // between parts of one thing
public typealias Step = W4                             // between rows
public typealias Room = Plus<Unit, W4>                 // inside a panel
public typealias Apart = Plus<W2, W4>                  // between groups
public typealias Edge = Plus<Unit, Plus<W2, W4>>       // the rail's shared edge
public typealias Wide = W8                             // the widest seam of a view
public typealias Line = Plus<W2, W8>                   // one reading line

// ── air is measured in whole lines, and the indent in the steps it is made of ──
public typealias Indent = Plus<Line, Step>             // a note hangs clear of its mark
public typealias TwoLines = Twice<Line>
public typealias Runway = Twice<TwoLines>

public protocol Ordered {}
public enum Wider<Hi, Lo, Slack>: Close {}
extension Wider: Ordered
where Hi == Plus<Lo, Plus<Unit, Slack>> {}
public enum Same<A, B>: Close {}
extension Same: Ordered
where A == B {}

// ── the ladder is monotone ──
public typealias SnugOverTight = Wider<Snug, Tight, Never>
public typealias NearOverSnug = Wider<Near, Snug, Never>
public typealias StepOverNear = Wider<Step, Near, Never>
public typealias RoomOverStep = Wider<Room, Step, Never>
public typealias ApartOverRoom = Wider<Apart, Room, Never>
public typealias EdgeOverApart = Wider<Edge, Apart, Never>
public typealias WideOverEdge = Wider<Wide, Edge, Never>
public typealias LineOverWide = Wider<Line, Wide, Unit>

// ── the law of proximity: kinship is nearness, and it tightens with depth.
// A group stands off from a group by more than a row stands off from a row,
// and a row by more than the parts inside it — each with its slack declared,
// so narrowing one below the other stops the settling and the judge says so ──
public typealias GroupsStandOffFurtherThanRows = Wider<Apart, Step, Unit>
public typealias RowsStandOffFurtherThanParts = Wider<Step, Near, Never>
public typealias PartsStandOffFurtherThanMarks = Wider<Near, Tight, Unit>

// ── the air is whole lines, and the indent is a sum of named steps ──
public typealias AirIsTwoLines = Same<TwoLines, Plus<Line, Line>>
public typealias RunwayIsFourLines = Same<Runway, Plus<TwoLines, TwoLines>>
public typealias IndentIsLineAndStep = Same<Indent, Plus<Line, Step>>
