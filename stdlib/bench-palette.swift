// gate stdlib bench-palette v1 — the palette as a judged world.
// Colours are not constants borrowed from a device; they are levels of
// light on a 0..100 scale, and every pair a reader meets carries a
// certificate of its contrast. Numbers are spelled on THIS file's own
// ladder from Unit (Twice doublings) — the built-in U-numerals stay
// symbolic to the judge, so a world spells its own ladder. Lower a
// background here and the slack stops settling: the judge names the pair,
// in numbers. (Neutrals only in this first cut; semantics follow.)

// the ladder: W2 = 2, W4 = 4, ... each a doubling of the last
public typealias W2 = Twice<Unit>
public typealias W4 = Twice<W2>
public typealias W8 = Twice<W4>
public typealias W16 = Twice<W8>
public typealias W32 = Twice<W16>
public typealias W64 = Twice<W32>
public typealias W128 = Twice<W64>
public typealias W256 = Twice<W128>
public typealias W512 = Twice<W256>
public typealias W1024 = Twice<W512>

// contrast on the 0..100 scale, cross-multiplied so it clears denominators:
// 7:1  ->  Bright == 7*Dark + 30 + Slack      (AAA, primary text)
// 3:1  ->  Bright == 3*Dark + 10 + Slack      (an honestly-stated secondary)
// brighter -> Hi == Lo + 1 + Slack            (a strict step of the ladder)
public typealias N7 = Plus<Unit, Plus<W2, W4>>
public typealias N30 = Plus<W2, Plus<W4, Plus<W8, W16>>>
public typealias N3 = Plus<Unit, W2>
public typealias N10 = Plus<W2, W8>

public protocol ContrastHolds {}
public enum Legible<Bright, Dark, Slack>: Close {}
extension Legible: ContrastHolds
where Bright == Plus<Times<N7, Dark>, Plus<N30, Slack>> {}
public enum Readable<Bright, Dark, Slack>: Close {}
extension Readable: ContrastHolds
where Bright == Plus<Times<N3, Dark>, Plus<N10, Slack>> {}
public protocol Ordered {}
public enum Brighter<Hi, Lo, Slack>: Close {}
extension Brighter: Ordered
where Hi == Plus<Lo, Plus<Unit, Slack>> {}

// the neutral ladder — one hue, chroma ~0, only lightness changes
public typealias PaperY = Plus<W2, Plus<W32, W64>>
public typealias MistY = Plus<Unit, Plus<W2, Plus<W4, Plus<W8, Plus<W16, W64>>>>>
public typealias LineY = Plus<W4, W64>
public typealias MutedY = Plus<W4, Plus<W8, W16>>
public typealias InkY = Plus<Unit, W4>

// the ladder is monotone, judged step by step (Paper > Mist > Line > Muted > Ink)
public typealias PaperOverMist = Brighter<PaperY, MistY, W2>
public typealias MistOverLine = Brighter<MistY, LineY, Plus<W2, Plus<W8, W16>>>
public typealias LineOverMuted = Brighter<LineY, MutedY, Plus<Unit, Plus<W2, Plus<W4, W32>>>>
public typealias MutedOverInk = Brighter<MutedY, InkY, Plus<W2, Plus<W4, W16>>>

// the pairs a reader meets, each holding its bound with slack to spare
public typealias InkOnPaper = Legible<PaperY, InkY, Plus<Unit, W32>>
public typealias MutedOnPaper = Readable<PaperY, MutedY, W4>
