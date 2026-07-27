// gate stdlib genre-contract v1 — a contract and the clients that carry it,
// role: forms
// as one judged world.
//
// A contract is written once and copied into a server and into every client
// library, and the copies drift apart quietly. Types do not prevent it: they
// make each side self-consistent and say nothing at all about the other, so a
// hand-written client can lag a contract for releases while its own type
// checker stays perfectly happy. The one thing that ties the copies today is a
// code generator, which means owning a pipeline per language and letting it
// dictate the shape of the client. This genre ties them the other way — with a
// seam that refuses, leaving the client hand-written.
//
// A field the contract declares becomes a RECORD whose shape is an axis; a
// client library becomes a CARRIER; carrying is the claim. What is judged here
// is agreement of shape: a client that carries `waitFor` as text where the
// contract calls it a number is refused, and the judge names both shapes.
//
// What is NOT judged here, and is said plainly rather than hidden: ABSENCE. A
// field a client does not carry states no claim at all, and a claim that was
// never made cannot be refused — so absence is reported beside the judgement,
// at the address in the contract that declares the field. The same division the
// ownership door already draws: a rule reaching outside its zone is judged, a
// pattern matching no file is named beside it.
//
// AND BOTH SIDES ARE DECLARED, NEVER READ. This grammar waits for an act of
// entry: somebody says, in these words, what their library carries. It was once
// fed by a reader that went out and inferred the client's side from its source,
// and that was a court reasoning about a world nobody had spoken for — honest
// certificates over invented premises. Judgement has no jurisdiction outside the
// gate. What can be had from outside is observation, and `gate drift` prints
// that with no verdict at all.

public protocol Shape {}
public enum Text: Shape {}
public enum Count: Shape {}
public enum Flag: Shape {}
public enum Many: Shape {}
public enum Nested: Shape {}

public protocol Declared {
    associatedtype Of: Shape
}
public protocol Carrier {}

public protocol Carried {}
public enum Carries<Who: Carrier, What: Declared, As: Shape>: Close {}
extension Carries: Carried
where What.Of == As {}
