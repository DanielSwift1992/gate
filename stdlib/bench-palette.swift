// gate stdlib bench-palette v1 — the palette as a judged world.
// Levels of light on a 0..100 scale; every pair a reader meets carries a
// contrast certificate. Numbers on this file's own ladder from Unit — the
// built-in U stay symbolic, so a world spells its own ladder. Lower a
// contrast and the slack stops settling: the judge names the pair, in numbers.

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
public typealias W2048 = Twice<W1024>

public typealias N3 = Plus<Unit, W2>
public typealias N7 = Plus<Unit, Plus<W2, W4>>
public typealias N9 = Plus<Unit, W8>
public typealias N10 = Plus<W2, W8>
public typealias N30 = Plus<W2, Plus<W4, Plus<W8, W16>>>
public typealias N35 = Plus<Unit, Plus<W2, W32>>
public typealias N25 = Plus<Unit, Plus<W8, W16>>
public typealias N29 = Plus<Unit, Plus<W4, Plus<W8, W16>>>

public protocol ContrastHolds {}
public enum Legible<Bright, Dark, Slack>: Close {}
extension Legible: ContrastHolds
where Bright == Plus<Times<N7, Dark>, Plus<N30, Slack>> {}
public enum Readable<Bright, Dark, Slack>: Close {}
extension Readable: ContrastHolds
where Bright == Plus<Times<N3, Dark>, Plus<N10, Slack>> {}
public enum ReadableAA<Bright, Dark, Slack>: Close {}
extension ReadableAA: ContrastHolds
where Twice<Bright> == Plus<Times<N9, Dark>, Plus<N35, Slack>> {}
public protocol Ordered {}
public enum Brighter<Hi, Lo, Slack>: Close {}
extension Brighter: Ordered
where Hi == Plus<Lo, Plus<Unit, Slack>> {}
public enum Same<A, B>: Close {}
extension Same: Ordered
where A == B {}
public protocol Achromatic {}
public enum Grey<X, Y, Z, Slo, Shi, Xlo, Xhi>: Close {}
extension Grey: Achromatic
where Z == Plus<Y, Slo>,
      Times<N29, Y> == Plus<Times<N25, Z>, Shi>,
      Times<N10, X> == Plus<Times<N9, Y>, Xlo>,
      Y == Plus<X, Xhi> {}

// ── the light theme the page wears ──
public typealias InkLitX = Unit
public typealias InkLitY = Unit
public typealias InkLitZ = Unit
public typealias PaperLitX = Plus<Unit, Plus<W4, Plus<W8, Plus<W16, W64>>>>
public typealias PaperLitY = Plus<W2, Plus<W32, W64>>
public typealias PaperLitZ = Plus<Unit, Plus<W2, Plus<W8, Plus<W32, W64>>>>
public typealias MistLitX = Plus<W2, Plus<W4, Plus<W16, W64>>>
public typealias MistLitY = Plus<W2, Plus<W8, Plus<W16, W64>>>
public typealias MistLitZ = Plus<W2, Plus<W32, W64>>
public typealias LineLitX = Plus<Unit, W64>
public typealias LineLitY = Plus<W4, W64>
public typealias LineLitZ = Plus<W2, Plus<W8, W64>>
public typealias MutedLitX = Plus<Unit, Plus<W2, Plus<W4, W16>>>
public typealias MutedLitY = Plus<W8, W16>
public typealias MutedLitZ = Plus<W2, Plus<W8, W16>>
public typealias OkLitX = W8
public typealias OkLitY = Plus<Unit, Plus<W2, Plus<W4, W8>>>
public typealias OkLitZ = Plus<W2, W4>
public typealias BadLitX = Plus<W8, W16>
public typealias BadLitY = Plus<Unit, Plus<W2, Plus<W4, W8>>>
public typealias BadLitZ = Plus<Unit, W4>
public typealias ActionLitX = Plus<Unit, W16>
public typealias ActionLitY = Plus<Unit, Plus<W2, Plus<W4, W8>>>
public typealias ActionLitZ = Plus<Unit, Plus<W4, Plus<W8, Plus<W16, W32>>>>
public typealias LawLitX = Plus<W4, W16>
public typealias LawLitY = Plus<Unit, Plus<W2, Plus<W4, W8>>>
public typealias LawLitZ = W2
public typealias LocalTypeLitX = Plus<Unit, Plus<W2, W8>>
public typealias LocalTypeLitY = Plus<Unit, Plus<W2, Plus<W4, W8>>>
public typealias LocalTypeLitZ = Plus<Unit, Plus<W2, Plus<W4, W16>>>
public typealias KnownNameLitX = Plus<Unit, Plus<W8, W16>>
public typealias KnownNameLitY = Plus<Unit, Plus<W2, Plus<W4, W8>>>
public typealias KnownNameLitZ = Plus<Unit, Plus<W2, Plus<W4, Plus<W8, Plus<W16, W32>>>>>
public typealias SeamLitX = Plus<W4, W32>
public typealias SeamLitY = Plus<W2, Plus<W4, W32>>
public typealias SeamLitZ = Plus<Unit, Plus<W8, W32>>
public typealias SelectLitX = Plus<Unit, Plus<W2, W64>>
public typealias SelectLitY = Plus<W4, W64>
public typealias SelectLitZ = Plus<W4, Plus<W8, Plus<W16, W64>>>

// ── the dark theme the dark canvas wears ──
public typealias InkDimX = Plus<Unit, Plus<W4, Plus<W16, W64>>>
public typealias InkDimY = Plus<Unit, Plus<W8, Plus<W16, W64>>>
public typealias InkDimZ = Plus<Unit, Plus<W32, W64>>
public typealias PaperDimX = Unit
public typealias PaperDimY = Unit
public typealias PaperDimZ = Unit
public typealias MistDimX = Plus<Unit, W2>
public typealias MistDimY = Plus<Unit, W2>
public typealias MistDimZ = Plus<Unit, W2>
public typealias LineDimX = Plus<Unit, W4>
public typealias LineDimY = Plus<Unit, W4>
public typealias LineDimZ = Plus<Unit, W4>
public typealias MutedDimX = Plus<Unit, W32>
public typealias MutedDimY = Plus<Unit, Plus<W2, W32>>
public typealias MutedDimZ = Plus<W2, Plus<W4, W32>>
public typealias OkDimX = Plus<Unit, W32>
public typealias OkDimY = Plus<W4, Plus<W8, Plus<W16, W32>>>
public typealias OkDimZ = Plus<W8, W16>
public typealias BadDimX = Plus<W2, W64>
public typealias BadDimY = Plus<W4, Plus<W8, Plus<W16, W32>>>
public typealias BadDimZ = Plus<Unit, Plus<W2, Plus<W4, Plus<W16, W32>>>>
public typealias ActionDimX = Plus<Unit, Plus<W2, Plus<W8, Plus<W16, W32>>>>
public typealias ActionDimY = Plus<W4, Plus<W8, Plus<W16, W32>>>
public typealias ActionDimZ = Plus<Unit, Plus<W4, Plus<W32, W64>>>
public typealias LawDimX = Plus<Unit, W64>
public typealias LawDimY = Plus<W4, Plus<W8, Plus<W16, W32>>>
public typealias LawDimZ = Plus<Unit, Plus<W4, Plus<W8, W32>>>
public typealias LocalTypeDimX = Plus<W4, Plus<W8, W32>>
public typealias LocalTypeDimY = Plus<W4, Plus<W8, Plus<W16, W32>>>
public typealias LocalTypeDimZ = Plus<W2, Plus<W4, Plus<W8, Plus<W16, W64>>>>
public typealias KnownNameDimX = Plus<Unit, W64>
public typealias KnownNameDimY = Plus<W4, Plus<W8, Plus<W16, W32>>>
public typealias KnownNameDimZ = Plus<Unit, Plus<W2, Plus<W32, W64>>>
public typealias SeamDimX = Plus<W4, W16>
public typealias SeamDimY = Plus<Unit, Plus<W4, W16>>
public typealias SeamDimZ = Plus<Unit, Plus<W2, Plus<W4, W16>>>
public typealias SelectDimX = Plus<Unit, W4>
public typealias SelectDimY = W4
public typealias SelectDimZ = Plus<Unit, Plus<W2, W8>>

// ── the ladder is monotone, the pairs clear their bound, the semantic step is level ──
public typealias PaperOverMist_lit = Brighter<PaperLitY, MistLitY, Plus<Unit, Plus<W2, W4>>>
public typealias MistOverLine_lit = Brighter<MistLitY, LineLitY, Plus<Unit, Plus<W4, W16>>>
public typealias LineOverMuted_lit = Brighter<LineLitY, MutedLitY, Plus<Unit, Plus<W2, Plus<W8, W32>>>>
public typealias MutedOverInk_lit = Brighter<MutedLitY, InkLitY, Plus<W2, Plus<W4, W16>>>
public typealias Paper_Ink_lit = Legible<PaperLitY, InkLitY, Plus<Unit, Plus<W4, Plus<W8, Plus<W16, W32>>>>>
public typealias Paper_Muted_lit = Readable<PaperLitY, MutedLitY, W16>
public typealias Paper_Ok_lit = ReadableAA<PaperLitY, OkLitY, Plus<W2, Plus<W8, W16>>>
public typealias Paper_Bad_lit = ReadableAA<PaperLitY, BadLitY, Plus<W2, Plus<W8, W16>>>
public typealias Paper_Action_lit = ReadableAA<PaperLitY, ActionLitY, Plus<W2, Plus<W8, W16>>>
public typealias Paper_Law_lit = ReadableAA<PaperLitY, LawLitY, Plus<W2, Plus<W8, W16>>>
public typealias Paper_LocalType_lit = ReadableAA<PaperLitY, LocalTypeLitY, Plus<W2, Plus<W8, W16>>>
public typealias Paper_KnownName_lit = ReadableAA<PaperLitY, KnownNameLitY, Plus<W2, Plus<W8, W16>>>
public typealias OkEqBad_lit = Same<OkLitY, BadLitY>
public typealias BadEqAction_lit = Same<BadLitY, ActionLitY>
public typealias ActionEqLaw_lit = Same<ActionLitY, LawLitY>
public typealias LawEqLocalType_lit = Same<LawLitY, LocalTypeLitY>
public typealias LocalTypeEqKnownName_lit = Same<LocalTypeLitY, KnownNameLitY>
public typealias InkOverMuted_dim = Brighter<InkDimY, MutedDimY, Plus<Unit, Plus<W4, Plus<W16, W32>>>>
public typealias MutedOverLine_dim = Brighter<MutedDimY, LineDimY, Plus<Unit, Plus<W4, Plus<W8, W16>>>>
public typealias LineOverMist_dim = Brighter<LineDimY, MistDimY, Unit>
public typealias MistOverPaper_dim = Brighter<MistDimY, PaperDimY, Unit>
public typealias Ink_Paper_dim = Legible<InkDimY, PaperDimY, Plus<W4, Plus<W16, W32>>>
public typealias Muted_Paper_dim = Readable<MutedDimY, PaperDimY, Plus<W2, Plus<W4, W16>>>
public typealias Ok_Paper_dim = ReadableAA<OkDimY, PaperDimY, Plus<W4, Plus<W8, W64>>>
public typealias Bad_Paper_dim = ReadableAA<BadDimY, PaperDimY, Plus<W4, Plus<W8, W64>>>
public typealias Action_Paper_dim = ReadableAA<ActionDimY, PaperDimY, Plus<W4, Plus<W8, W64>>>
public typealias Law_Paper_dim = ReadableAA<LawDimY, PaperDimY, Plus<W4, Plus<W8, W64>>>
public typealias LocalType_Paper_dim = ReadableAA<LocalTypeDimY, PaperDimY, Plus<W4, Plus<W8, W64>>>
public typealias KnownName_Paper_dim = ReadableAA<KnownNameDimY, PaperDimY, Plus<W4, Plus<W8, W64>>>
public typealias OkEqBad_dim = Same<OkDimY, BadDimY>
public typealias BadEqAction_dim = Same<BadDimY, ActionDimY>
public typealias ActionEqLaw_dim = Same<ActionDimY, LawDimY>
public typealias LawEqLocalType_dim = Same<LawDimY, LocalTypeDimY>
public typealias LocalTypeEqKnownName_dim = Same<LocalTypeDimY, KnownNameDimY>

// ── a neutral is neutral: X and Z bracket the D65 grey line, so the band
// refuses a drift to blue (Z above the bound) or to brown (Z below Y, X
// below 0.9*Y), and the single integer slot at Y=1..5 is the honest floor ──
public typealias InkGrey_lit = Grey<InkLitX, InkLitY, InkLitZ, Never, W4, Unit, Never>
public typealias PaperGrey_lit = Grey<PaperLitX, PaperLitY, PaperLitZ, Plus<Unit, W8>, Plus<Unit, Plus<W2, Plus<W4, Plus<W32, W128>>>>, Plus<W16, W32>, Plus<Unit, W4>>
public typealias MistGrey_lit = Grey<MistLitX, MistLitY, MistLitZ, W8, Plus<W32, W128>, Plus<W2, Plus<W16, W32>>, W4>
public typealias LineGrey_lit = Grey<LineLitX, LineLitY, LineLitZ, Plus<W2, W4>, Plus<W2, Plus<W8, Plus<W16, Plus<W32, W64>>>>, Plus<W2, Plus<W4, W32>>, Plus<Unit, W2>>
public typealias MutedGrey_lit = Grey<MutedLitX, MutedLitY, MutedLitZ, W2, Plus<W2, Plus<W4, Plus<W8, W32>>>, Plus<W2, Plus<W4, W8>>, Unit>
public typealias SeamGrey_lit = Grey<SeamLitX, SeamLitY, SeamLitZ, Plus<Unit, W2>, Plus<Unit, Plus<W4, Plus<W8, W64>>>, Plus<W2, W16>, W2>
public typealias InkGrey_dim = Grey<InkDimX, InkDimY, InkDimZ, W8, Plus<W4, Plus<W8, Plus<W16, W128>>>, Plus<Unit, Plus<W16, W32>>, W4>
public typealias PaperGrey_dim = Grey<PaperDimX, PaperDimY, PaperDimZ, Never, W4, Unit, Never>
public typealias MistGrey_dim = Grey<MistDimX, MistDimY, MistDimZ, Never, Plus<W4, W8>, Plus<Unit, W2>, Never>
public typealias LineGrey_dim = Grey<LineDimX, LineDimY, LineDimZ, Never, Plus<W4, W16>, Plus<Unit, W4>, Never>
public typealias MutedGrey_dim = Grey<MutedDimX, MutedDimY, MutedDimZ, Plus<Unit, W2>, Plus<Unit, W64>, Plus<Unit, Plus<W2, Plus<W4, W8>>>, W2>
public typealias SeamGrey_dim = Grey<SeamDimX, SeamDimY, SeamDimZ, W2, Plus<W2, W32>, Plus<Unit, Plus<W2, W8>>, Unit>
