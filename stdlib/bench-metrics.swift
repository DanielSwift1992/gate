// gate stdlib bench-metrics v1: the spacing steps, and a check on every gap
// role: gate's own
// The base is the reading line: an instrument for reading measures its
// spacing in the letter it sets. One step is a tenth of that line, and every
// gap on the page is a whole number of steps, so a length is spelled the way
// a number is, on this file's own ladder from Unit, and can be judged like one.
//
// Judged here: the ladder is monotone, the law of proximity, what belongs
// together stands closer than what does not, and the deeper the kinship the
// tighter the gap. The air is whole reading lines, and the indent is the sum
// of the steps it is made of, not a number of its own.
//
// Not judged, and said plainly: the price of one step (how dense the page
// reads) and which step a given seam takes are chosen by eye inside the box
// these rules leave. The rules say a section must stand further off than a
// row. They do not say by how much it pleases.

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

// ── air is measured in whole lines, and an indent belongs to a column ──
public typealias Indent = Twice<Edge>                  // a note hangs one edge past the edge
public typealias TwoLines = Twice<Line>
public typealias Runway = Twice<TwoLines>

// ── THE MAP OF SEAMS, read off the page and not assigned to it: which step does
// which work, and where it stands. Every count below is measured in web/ui.html,
// as `calc(var(--u)*N)` plus a bare `var(--u)` for one unit, and the battery
// counts the same way and refuses this table when the page moves on: a step
// that stops being used shows up as a zero here, or not at all.
//   Tight     1u  ×13  inside one mark          (a caret, a badge's own room)
//   Snug      2u  ×24  inside one row           (a row's own height)
//   Near      3u  ×14  between parts of a thing (a name and its tag)
//   Step      4u  ×13  between rows             (a header's foot)
//   Room      5u  ×13  inside a panel           (a button, a cell)
//   Apart     6u  ×9   between groups           (a section's head)
//   Edge      7u  ×9   the rail's shared edge   (every row on the rail, one edge)
//   Wide      8u  ×5   the widest seam of a view (the editor's own margin)
//   Line     10u  ×4   one reading line of air
//   Indent   14u  ×1   one edge past the edge   (a note hanging under its flag)
//   TwoLines 20u  ×1   the air above an empty page
//   Runway   40u  ×2   four lines, so the last line is not the last pixel

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
// and a row by more than the parts inside it, each with its slack declared,
// so narrowing one below the other stops the settling and the judge says so ──
public typealias GroupsStandOffFurtherThanRows = Wider<Apart, Step, Unit>
public typealias RowsStandOffFurtherThanParts = Wider<Step, Near, Never>
public typealias PartsStandOffFurtherThanMarks = Wider<Near, Tight, Unit>

// ── the air is whole lines, and the indent is a sum of named steps ──
public typealias AirIsTwoLines = Same<TwoLines, Plus<Line, Line>>
public typealias RunwayIsFourLines = Same<Runway, Plus<TwoLines, TwoLines>>
// belonging is a shared edge: the hanging note starts one edge past the rail's
// own, so it reads as a second column of the same page rather than a loose inset
public typealias IndentIsTwiceTheEdge = Same<Indent, Twice<Edge>>
