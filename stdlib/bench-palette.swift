// gate stdlib bench-palette v1: the colours the page may use, with contrast checks
// role: gate's own
// speaks-for: the-bench
// Levels of light on a 0..1000 scale (a tenth of a percent), spelled on this
// file's own ladder from Unit: the built-in U stay symbolic, so a world
// spells its own ladder. The scale is a tenth of a percent and not a percent
// because at a percent the darkest nodes cannot land on the grey line at all:
// the nearest integer sat in the warm corner and the canvas came out pink.
//
// Judged here, as a count: the ladder is monotone, text clears a contrast
// bound, ink and the names at 4.5:1, the secondary registers (muted, and the
// seam the ceremony is set in) at the 3:1 bound П1 declares, the verdict's two
// poles stand on opposite sides of red-green, and the channels a reader must
// tell apart stand apart. Lower any of it and the reading's answer is wrong:
// the count court names the claim, in numbers.
//
// Stated and not judged: a neutral is neutral, its X and Z held within two
// percent of the D65 grey line, and every semantic atom stands outside that
// band, on the side it leans. Those laws multiply by the D65 coefficients and
// outgrow the count court's budget; the section that states them says so.
//
// The floor, named: at a tenth of a percent of light one step is the whole
// resolution, and 0.95 of one step is not a number. Those nodes state X == Y
// and hold the same band on Z. It is the scale's floor, not a chosen colour.
//
// And across the two themes: a role stands as loud on one canvas as on the
// other. The light theme's contrast is the bound its dark rung answers to,
// so neither canvas can drift into shouting while the other whispers. The
// dark ladder used to be a plain inversion, and inversion is not a relation.
//
// Not judged, and said plainly rather than dressed as a result: the exact
// angle of the teal, the violet, the blue and the warm yellow is chosen by eye
// inside the box those rules leave, and perceptual equality of chroma between
// them is not judged at all: XYZ is not perceptually uniform, and a number
// that looked like a certificate without being one would be worse than none.

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
public typealias W4096 = Twice<W2048>
public typealias W8192 = Twice<W4096>
public typealias W16384 = Twice<W8192>
public typealias W32768 = Twice<W16384>
public typealias W65536 = Twice<W32768>
public typealias W131072 = Twice<W65536>

public typealias N3 = Plus<Unit, W2>
public typealias N7 = Plus<Unit, Plus<W2, W4>>
public typealias N9 = Plus<Unit, W8>
public typealias N23 = Plus<Unit, Plus<W2, Plus<W4, W16>>>
public typealias N24 = Plus<W8, W16>
public typealias N25 = Plus<Unit, Plus<W8, W16>>
public typealias N27 = Plus<Unit, Plus<W2, Plus<W8, W16>>>
public typealias N28 = Plus<W4, Plus<W8, W16>>
public typealias N100 = Plus<W4, Plus<W32, W64>>
public typealias N300 = Plus<W4, Plus<W8, Plus<W32, W256>>>
public typealias N350 = Plus<W2, Plus<W4, Plus<W8, Plus<W16, Plus<W64, W256>>>>>

// ── WHAT THE LAWS BELOW ASK IS A COUNT. A level is a number of tenths of a
// percent, so a law between two levels is a law between two numbers, and the
// where court reads Twice and Plus as names: two names that count the same are
// still two names (canon four). The count court reads them as the corpus's
// Primitive defines them, Unit one, Never none, Plus the sum, and checks each
// reading's declared answer. A product by a stated constant is a sum of
// doublings, so no multiplication is asked of it ──
public enum BenchLight: Close {}
public enum LevelQuestion: Close {}
public enum Luminance<Measured: Structure, Declared: Structure>: PredicateReading {
    public typealias Left = Measured
    public typealias Right = Declared
    public typealias Sigma = BenchLight
    public typealias Encoding = UnaryArithmeticEncoding
    public typealias Predicate = LevelQuestion
    public typealias Answer = Declared
}
public typealias Thrice<X: Structure> = Plus<X, Twice<X>>
public typealias Sevenfold<X: Structure> = Plus<X, Plus<Twice<X>, Twice<Twice<X>>>>
public typealias Ninefold<X: Structure> = Plus<X, Twice<Twice<Twice<X>>>>
public typealias Legible<Bright: Structure, Dark: Structure, Slack: Structure> = Luminance<Bright, Plus<Sevenfold<Dark>, Plus<N300, Slack>>>
public typealias Readable<Bright: Structure, Dark: Structure, Slack: Structure> = Luminance<Bright, Plus<Thrice<Dark>, Plus<N100, Slack>>>
public typealias ReadableAA<Bright: Structure, Dark: Structure, Slack: Structure> = Luminance<Twice<Bright>, Plus<Ninefold<Dark>, Plus<N350, Slack>>>
public typealias Brighter<Hi: Structure, Lo: Structure, Slack: Structure> = Luminance<Hi, Plus<Lo, Plus<Unit, Slack>>>
public typealias Same<A: Structure, B: Structure> = Luminance<A, B>
// a channel that leans: one coordinate stands over the other by one step and
// the slack declared, which is how each pole of the verdict says its side
public typealias Leans<More: Structure, Less: Structure, Slack: Structure> = Luminance<More, Plus<Less, Plus<Unit, Slack>>>

// ── STATED AND NOT JUDGED, AND SAID SO: the neutral and the hue laws. Each
// multiplies a level near a thousand by a D65 coefficient from 23 to 28, and
// the count court of question vi.count.unit-never-plus/1 spells a sum of
// doublings out in full: past about ten thousand on a side it stops at its
// normalization budget and infers nothing (PaperGrey_lit asks 52,920 in one
// reading). Some of these would fit and some would not, and a law judged on
// one theme and not the other would be a split by budget, not by meaning, so
// the whole class waits for a count court that counts a named definition once.
// The laws, as they stood under the court that read Times as a product:
//   Grey<X, Y, Z, Slo, Shi, Xlo, Xhi>:  25·Z == 27·Y + Slo,  28·Y == 25·Z + Shi,
//                                       25·X == 23·Y + Xlo,  24·Y == 25·X + Xhi
//   GreyFloor<X, Y, Z, Slo, Shi>:       X == Y,  25·Z == 27·Y + Slo,  28·Y == 25·Z + Shi
//   TowardBlue<Y, Z, Margin>:           25·Z == 28·Y + 1 + Margin
//   TowardWarm<Y, Z, Margin>:           27·Y == 25·Z + 1 + Margin
// Each claim below still names its numbers, and the page paints them, but no
// court here says they hold ──
public enum Grey<X, Y, Z, Slo, Shi, Xlo, Xhi>: Close {}
public enum GreyFloor<X, Y, Z, Slo, Shi>: Close {}
public enum TowardBlue<Y, Z, Margin>: Close {}
public enum TowardWarm<Y, Z, Margin>: Close {}
// ── AND TWO CHANNELS THAT MUST BE TOLD APART STAND APART. Every hue here was
// certified for its side (toward blue, toward warm) and for its lightness,
// and nothing ever certified the DISTANCE between two of them. So a channel
// could drift until it nearly met another and no certificate would say a word:
// mine and theirs are 400 apart on Z in the lit half and 35 in the dim one, an
// eleven-fold collapse that left the whole mine/theirs distinction resting on
// an axis no law looked at. A pair the eye must separate is a pair the world
// must hold apart, and by a stated amount.
public typealias Apart<A: Structure, B: Structure, Margin: Structure> = Luminance<A, Plus<B, Plus<Unit, Margin>>>

// ── the light theme ──
public typealias InkLitX = Plus<W2, W8>
public typealias InkLitY = Plus<W2, W8>
public typealias InkLitZ = Plus<Unit, Plus<W2, W8>>
public typealias PaperLitX = Plus<W2, Plus<W128, Plus<W256, W512>>>
public typealias PaperLitY = Plus<Unit, Plus<W16, Plus<W32, Plus<W128, Plus<W256, W512>>>>>
public typealias PaperLitZ = Plus<Unit, Plus<W4, W1024>>
public typealias MistLitX = Plus<W2, Plus<W4, Plus<W16, Plus<W32, Plus<W256, W512>>>>>
public typealias MistLitY = Plus<Unit, Plus<W32, Plus<W64, Plus<W256, W512>>>>
public typealias MistLitZ = Plus<W2, Plus<W4, Plus<W8, Plus<W32, Plus<W128, Plus<W256, W512>>>>>>
public typealias LineLitX = Plus<Unit, Plus<W4, Plus<W32, Plus<W64, W512>>>>
public typealias LineLitY = Plus<Unit, Plus<W4, Plus<W128, W512>>>
public typealias LineLitZ = Plus<W2, Plus<W4, Plus<W8, Plus<W16, Plus<W32, Plus<W128, W512>>>>>>
public typealias MutedLitX = Plus<W4, Plus<W32, Plus<W64, W128>>>
public typealias MutedLitY = Plus<W16, Plus<W32, Plus<W64, W128>>>
public typealias MutedLitZ = Plus<Unit, Plus<W4, W256>>
public typealias OkLitX = Plus<W16, W64>
public typealias OkLitY = Plus<W2, Plus<W4, Plus<W16, W128>>>
public typealias OkLitZ = Plus<W4, Plus<W8, Plus<W16, W32>>>
public typealias BadLitX = Plus<W16, Plus<W32, Plus<W64, W128>>>
public typealias BadLitY = Plus<W2, Plus<W4, Plus<W16, W128>>>
public typealias BadLitZ = Plus<W2, Plus<W16, W32>>
public typealias ActionLitX = Plus<W2, Plus<W8, Plus<W32, W128>>>
public typealias ActionLitY = Plus<W2, Plus<W4, Plus<W16, W128>>>
public typealias ActionLitZ = Plus<W2, Plus<W32, Plus<W64, W512>>>
public typealias LawLitX = Plus<W8, Plus<W64, W128>>
public typealias LawLitY = Plus<W2, Plus<W4, Plus<W16, W128>>>
public typealias LawLitZ = Plus<W4, W16>
public typealias LocalTypeLitX = Plus<W4, Plus<W8, Plus<W16, Plus<W32, W64>>>>
public typealias LocalTypeLitY = Plus<W2, Plus<W4, Plus<W16, W128>>>
public typealias LocalTypeLitZ = Plus<W2, Plus<W8, Plus<W16, Plus<W64, W256>>>>
public typealias KnownNameLitX = Plus<W2, Plus<W8, Plus<W16, Plus<W32, Plus<W64, W128>>>>>
public typealias KnownNameLitY = Plus<W2, Plus<W4, Plus<W16, W128>>>
public typealias KnownNameLitZ = Plus<W2, Plus<W4, Plus<W16, Plus<W32, Plus<W64, W512>>>>>
public typealias SeamLitX = Plus<W8, W256>
public typealias SeamLitY = Plus<W2, Plus<W4, Plus<W16, W256>>>
public typealias SeamLitZ = Plus<Unit, Plus<W2, Plus<W4, Plus<W8, Plus<W32, W256>>>>>
public typealias SelectLitX = Plus<W2, Plus<W4, Plus<W128, W512>>>
public typealias SelectLitY = Plus<W8, Plus<W32, Plus<W128, W512>>>
public typealias SelectLitZ = Plus<W4, Plus<W32, Plus<W64, Plus<W128, W512>>>>

// ── the dark theme ──
public typealias InkDimX = Plus<W2, Plus<W4, Plus<W8, Plus<W64, W512>>>>
public typealias InkDimY = Plus<Unit, Plus<W4, Plus<W8, Plus<W32, Plus<W64, W512>>>>>
public typealias InkDimZ = Plus<W4, Plus<W32, Plus<W128, W512>>>
public typealias PaperDimX = Plus<W2, W8>
public typealias PaperDimY = Plus<W2, W8>
public typealias PaperDimZ = Plus<Unit, Plus<W2, W8>>
public typealias MistDimX = Plus<W4, Plus<W8, W16>>
public typealias MistDimY = Plus<W2, Plus<W4, Plus<W8, W16>>>
public typealias MistDimZ = Plus<Unit, W32>
public typealias LineDimX = Plus<W16, W32>
public typealias LineDimY = Plus<W2, Plus<W16, W32>>
public typealias LineDimZ = Plus<W2, Plus<W4, Plus<W16, W32>>>
public typealias MutedDimX = Plus<W8, Plus<W32, Plus<W64, W128>>>
public typealias MutedDimY = Plus<W4, Plus<W16, Plus<W32, Plus<W64, W128>>>>
public typealias MutedDimZ = Plus<W2, Plus<W8, W256>>
public typealias OkDimX = Plus<W2, Plus<W4, Plus<W32, Plus<W64, W128>>>>
public typealias OkDimY = Plus<Unit, Plus<W2, Plus<W32, Plus<W128, W256>>>>
public typealias OkDimZ = Plus<W8, Plus<W32, W128>>
public typealias BadDimX = Plus<Unit, Plus<W4, Plus<W8, Plus<W64, Plus<W128, W256>>>>>
public typealias BadDimY = Plus<Unit, Plus<W2, Plus<W32, Plus<W128, W256>>>>
public typealias BadDimZ = Plus<W8, Plus<W32, W128>>
public typealias ActionDimX = Plus<W4, Plus<W8, Plus<W16, Plus<W128, W256>>>>
public typealias ActionDimY = Plus<Unit, Plus<W2, Plus<W32, Plus<W128, W256>>>>
public typealias ActionDimZ = Plus<Unit, Plus<W64, Plus<W128, W512>>>
public typealias LawDimX = Plus<W2, Plus<W4, Plus<W64, Plus<W128, W256>>>>
public typealias LawDimY = Plus<Unit, Plus<W2, Plus<W32, Plus<W128, W256>>>>
public typealias LawDimZ = Plus<W2, Plus<W32, W64>>
public typealias LocalTypeDimX = Plus<Unit, Plus<W2, Plus<W16, Plus<W32, W256>>>>
public typealias LocalTypeDimY = Plus<Unit, Plus<W2, Plus<W32, Plus<W128, W256>>>>
public typealias LocalTypeDimZ = Plus<W16, Plus<W128, W512>>
public typealias KnownNameDimX = Plus<W2, Plus<W4, Plus<W64, Plus<W128, W256>>>>
public typealias KnownNameDimY = Plus<Unit, Plus<W2, Plus<W32, Plus<W128, W256>>>>
public typealias KnownNameDimZ = Plus<Unit, Plus<W2, Plus<W16, Plus<W32, Plus<W128, W512>>>>>
public typealias SeamDimX = Plus<W4, Plus<W8, W128>>
public typealias SeamDimY = Plus<Unit, Plus<W2, Plus<W16, W128>>>
public typealias SeamDimZ = Plus<W32, W128>
public typealias SelectDimX = Plus<W2, Plus<W4, W32>>
public typealias SelectDimY = Plus<W8, W32>
public typealias SelectDimZ = Plus<W4, Plus<W8, W32>>

// ── the ladder is monotone, the pairs clear their bound, the semantic step is level ──
public typealias PaperOverMist_lit = Brighter<PaperLitY, MistLitY, Plus<Unit, Plus<W2, Plus<W4, Plus<W8, W64>>>>>
public typealias MistOverLine_lit = Brighter<MistLitY, LineLitY, Plus<Unit, Plus<W2, Plus<W8, Plus<W16, Plus<W64, W128>>>>>>
public typealias LineOverMuted_lit = Brighter<LineLitY, MutedLitY, Plus<W4, Plus<W16, Plus<W128, W256>>>>
public typealias MutedOverInk_lit = Brighter<MutedLitY, InkLitY, Plus<Unit, Plus<W4, Plus<W32, Plus<W64, W128>>>>>
public typealias Paper_Ink_lit = Legible<PaperLitY, InkLitY, Plus<Unit, Plus<W2, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W512>>>>>>>
public typealias Paper_Muted_lit = Readable<PaperLitY, MutedLitY, Plus<Unit, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W64>>>>>>
public typealias Paper_Ok_lit = ReadableAA<PaperLitY, OkLitY, Plus<W2, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W128>>>>>>
public typealias Paper_Bad_lit = ReadableAA<PaperLitY, BadLitY, Plus<W2, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W128>>>>>>
public typealias Paper_Action_lit = ReadableAA<PaperLitY, ActionLitY, Plus<W2, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W128>>>>>>
public typealias Paper_Law_lit = ReadableAA<PaperLitY, LawLitY, Plus<W2, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W128>>>>>>
public typealias Paper_LocalType_lit = ReadableAA<PaperLitY, LocalTypeLitY, Plus<W2, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W128>>>>>>
public typealias Paper_KnownName_lit = ReadableAA<PaperLitY, KnownNameLitY, Plus<W2, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W128>>>>>>
public typealias OkEqBad_lit = Same<OkLitY, BadLitY>
public typealias BadEqAction_lit = Same<BadLitY, ActionLitY>
public typealias ActionEqLaw_lit = Same<ActionLitY, LawLitY>
public typealias LawEqLocalType_lit = Same<LawLitY, LocalTypeLitY>
public typealias LocalTypeEqKnownName_lit = Same<LocalTypeLitY, KnownNameLitY>
public typealias InkOverMuted_dim = Brighter<InkDimY, MutedDimY, Plus<W8, Plus<W16, Plus<W32, Plus<W64, W256>>>>>
public typealias MutedOverLine_dim = Brighter<MutedDimY, LineDimY, Plus<Unit, Plus<W64, W128>>>
public typealias LineOverMist_dim = Brighter<LineDimY, MistDimY, Plus<Unit, Plus<W2, W16>>>
public typealias MistOverPaper_dim = Brighter<MistDimY, PaperDimY, Plus<Unit, Plus<W2, W16>>>
public typealias Ink_Paper_dim = Legible<InkDimY, PaperDimY, Plus<Unit, Plus<W2, Plus<W8, Plus<W16, Plus<W32, Plus<W64, W128>>>>>>>
public typealias Muted_Paper_dim = Readable<MutedDimY, PaperDimY, Plus<W2, Plus<W16, Plus<W32, W64>>>>
public typealias Ok_Paper_dim = ReadableAA<OkDimY, PaperDimY, Plus<W2, Plus<W4, Plus<W8, Plus<W128, W256>>>>>
public typealias Bad_Paper_dim = ReadableAA<BadDimY, PaperDimY, Plus<W2, Plus<W4, Plus<W8, Plus<W128, W256>>>>>
public typealias Action_Paper_dim = ReadableAA<ActionDimY, PaperDimY, Plus<W2, Plus<W4, Plus<W8, Plus<W128, W256>>>>>
public typealias Law_Paper_dim = ReadableAA<LawDimY, PaperDimY, Plus<W2, Plus<W4, Plus<W8, Plus<W128, W256>>>>>
public typealias LocalType_Paper_dim = ReadableAA<LocalTypeDimY, PaperDimY, Plus<W2, Plus<W4, Plus<W8, Plus<W128, W256>>>>>
public typealias KnownName_Paper_dim = ReadableAA<KnownNameDimY, PaperDimY, Plus<W2, Plus<W4, Plus<W8, Plus<W128, W256>>>>>
public typealias OkEqBad_dim = Same<OkDimY, BadDimY>
public typealias BadEqAction_dim = Same<BadDimY, ActionDimY>
public typealias ActionEqLaw_dim = Same<ActionDimY, LawDimY>
public typealias LawEqLocalType_dim = Same<LawDimY, LocalTypeDimY>
public typealias LocalTypeEqKnownName_dim = Same<LocalTypeDimY, KnownNameDimY>

// ── a neutral is neutral: X and Z stay within two percent of the D65 grey
// line, so neither a blue nor a warm tint can creep back. At the floor of
// the scale one step is the whole resolution, and that is said, not hidden ──
public typealias InkGrey_lit = GreyFloor<InkLitX, InkLitY, InkLitZ, Plus<Unit, W4>, Plus<Unit, W4>>
public typealias PaperGrey_lit = Grey<PaperLitX, PaperLitY, PaperLitZ, Plus<W2, Plus<W16, Plus<W64, W128>>>, Plus<Unit, Plus<W2, Plus<W4, Plus<W8, Plus<W16, Plus<W64, Plus<W128, W512>>>>>>>, Plus<Unit, Plus<W2, Plus<W8, Plus<W64, Plus<W128, W512>>>>>, Plus<W2, Plus<W4, Plus<W32, Plus<W64, W128>>>>>
public typealias MistGrey_lit = Grey<MistLitX, MistLitY, MistLitZ, Plus<Unit, Plus<W2, Plus<W64, W128>>>, Plus<W2, Plus<W4, Plus<W8, Plus<W16, Plus<W128, W512>>>>>, Plus<Unit, Plus<W2, Plus<W4, Plus<W8, Plus<W128, W512>>>>>, Plus<W2, Plus<W16, Plus<W64, W128>>>>
public typealias LineGrey_lit = Grey<LineLitX, LineLitY, LineLitZ, Plus<Unit, Plus<W2, Plus<W4, W128>>>, Plus<W2, Plus<W4, Plus<W8, Plus<W16, Plus<W32, Plus<W64, Plus<W128, W256>>>>>>>, Plus<W2, Plus<W8, Plus<W32, Plus<W64, Plus<W128, W256>>>>>, Plus<Unit, Plus<W2, Plus<W8, Plus<W16, W128>>>>>
public typealias MutedGrey_lit = Grey<MutedLitX, MutedLitY, MutedLitZ, Plus<Unit, Plus<W4, Plus<W8, W32>>>, Plus<Unit, Plus<W2, Plus<W64, W128>>>, Plus<W4, Plus<W16, Plus<W32, W128>>>, Plus<W4, Plus<W8, Plus<W16, W32>>>>
public typealias SeamGrey_lit = Grey<SeamLitX, SeamLitY, SeamLitZ, Plus<Unit, Plus<W4, W64>>, Plus<Unit, Plus<W16, Plus<W64, W128>>>, Plus<W2, Plus<W4, Plus<W8, Plus<W64, W128>>>>, Plus<W8, W64>>
public typealias SelectGrey_lit = Grey<SelectLitX, SelectLitY, SelectLitZ, Plus<W4, Plus<W8, W128>>, Plus<W4, Plus<W8, Plus<W16, W512>>>, Plus<W2, Plus<W4, Plus<W8, Plus<W16, Plus<W32, Plus<W64, Plus<W128, W256>>>>>>>, Plus<W2, Plus<W8, Plus<W32, W128>>>>
public typealias InkGrey_dim = Grey<InkDimX, InkDimY, InkDimZ, Plus<Unit, Plus<W4, W128>>, Plus<W8, Plus<W32, Plus<W64, Plus<W128, W256>>>>, Plus<Unit, Plus<W2, Plus<W16, Plus<W64, Plus<W128, W256>>>>>, Plus<W2, Plus<W8, Plus<W16, W128>>>>
public typealias PaperGrey_dim = GreyFloor<PaperDimX, PaperDimY, PaperDimZ, Plus<Unit, W4>, Plus<Unit, W4>>
public typealias MistGrey_dim = Grey<MistDimX, MistDimY, MistDimZ, Plus<Unit, Plus<W2, Plus<W4, W8>>>, Plus<Unit, Plus<W2, Plus<W4, W8>>>, Plus<W2, W8>, Plus<W4, W16>>
public typealias LineGrey_dim = Grey<LineDimX, LineDimY, LineDimZ, Never, Plus<W2, Plus<W16, W32>>, Plus<W2, Plus<W16, W32>>, Never>
public typealias MutedGrey_dim = Grey<MutedDimX, MutedDimY, MutedDimZ, Plus<W2, Plus<W4, Plus<W8, Plus<W16, W32>>>>, Plus<W2, Plus<W4, Plus<W16, Plus<W32, W128>>>>, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W128>>>>, Plus<W8, Plus<W16, W32>>>
public typealias SeamGrey_dim = Grey<SeamDimX, SeamDimY, SeamDimZ, Plus<Unit, Plus<W2, Plus<W4, Plus<W8, W16>>>>, Plus<W4, Plus<W16, Plus<W32, W64>>>, Plus<Unit, Plus<W2, Plus<W4, Plus<W16, Plus<W32, W64>>>>>, Plus<W4, Plus<W8, W16>>>
public typealias SelectGrey_dim = Grey<SelectDimX, SelectDimY, SelectDimZ, Plus<W4, W16>, Plus<W4, W16>, Plus<W2, Plus<W4, Plus<W8, W16>>>, Plus<W2, W8>>

// ── and colour is spent only where it means: every semantic atom stands
// OUTSIDE that same band, on the side it leans, while every neutral stands
// inside it, and the verdict's own two poles stand apart on red-green ──
public typealias OkChroma_lit = TowardWarm<OkLitY, OkLitZ, Plus<Unit, Plus<W4, Plus<W16, Plus<W32, Plus<W64, Plus<W128, Plus<W256, W2048>>>>>>>>
public typealias BadChroma_lit = TowardWarm<BadLitY, BadLitZ, Plus<Unit, Plus<W2, Plus<W4, Plus<W8, Plus<W32, Plus<W64, Plus<W128, Plus<W512, W2048>>>>>>>>>
public typealias ActionChroma_lit = TowardBlue<ActionLitY, ActionLitZ, Plus<Unit, Plus<W8, Plus<W32, Plus<W256, Plus<W512, Plus<W2048, W8192>>>>>>>
public typealias LawChroma_lit = TowardWarm<LawLitY, LawLitZ, Plus<Unit, Plus<W4, Plus<W8, Plus<W16, Plus<W64, Plus<W128, Plus<W256, Plus<W1024, W2048>>>>>>>>>
public typealias LocalTypeChroma_lit = TowardBlue<LocalTypeLitY, LocalTypeLitZ, Plus<Unit, Plus<W32, Plus<W64, Plus<W256, W4096>>>>>
public typealias KnownNameChroma_lit = TowardBlue<KnownNameLitY, KnownNameLitZ, Plus<Unit, Plus<W4, Plus<W8, Plus<W16, Plus<W256, Plus<W1024, Plus<W2048, W8192>>>>>>>>
public typealias OkChroma_dim = TowardWarm<OkDimY, OkDimZ, Plus<W8, Plus<W64, Plus<W128, Plus<W256, Plus<W512, Plus<W2048, W4096>>>>>>>
public typealias BadChroma_dim = TowardWarm<BadDimY, BadDimZ, Plus<W8, Plus<W64, Plus<W128, Plus<W256, Plus<W512, Plus<W2048, W4096>>>>>>>
public typealias ActionChroma_dim = TowardBlue<ActionDimY, ActionDimZ, Plus<W4, Plus<W256, Plus<W512, Plus<W1024, W4096>>>>>
public typealias LawChroma_dim = TowardWarm<LawDimY, LawDimZ, Plus<W2, Plus<W4, Plus<W8, Plus<W16, Plus<W128, Plus<W512, W8192>>>>>>>
public typealias LocalTypeChroma_dim = TowardBlue<LocalTypeDimY, LocalTypeDimZ, Plus<Unit, Plus<W2, Plus<W8, Plus<W16, Plus<W32, Plus<W512, W4096>>>>>>>
public typealias KnownNameChroma_dim = TowardBlue<KnownNameDimY, KnownNameDimZ, Plus<W2, Plus<W4, Plus<W32, Plus<W128, Plus<W256, Plus<W1024, W4096>>>>>>>
public typealias VerdictPoleOk_lit = Leans<OkLitY, OkLitX, Plus<Unit, Plus<W4, W64>>>
public typealias VerdictPoleBad_lit = Leans<BadLitX, BadLitY, Plus<Unit, Plus<W8, Plus<W16, W64>>>>
public typealias VerdictPoleOk_dim = Leans<OkDimY, OkDimX, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W128>>>>>
public typealias VerdictPoleBad_dim = Leans<BadDimX, BadDimY, Plus<Unit, Plus<W8, W32>>>

// ── the seam is read, so it clears the bound П1 declares for secondary
// text, and stays quieter than speech. The selection is a surface, so it
// stands on the grey line and is more present than a hover ──
public typealias Paper_Seam_lit = Readable<PaperLitY, SeamLitY, Plus<Unit, Plus<W2, W8>>>
public typealias Seam_Paper_dim = Readable<SeamDimY, PaperDimY, Plus<Unit, W16>>
public typealias SeamUnderMuted_lit = Brighter<SeamLitY, MutedLitY, Plus<Unit, Plus<W4, W32>>>
public typealias SeamUnderMuted_dim = Brighter<MutedDimY, SeamDimY, Plus<W32, W64>>
public typealias SelectOverMist_lit = Brighter<MistLitY, SelectLitY, Plus<W8, Plus<W16, Plus<W32, W128>>>>
public typealias SelectOverMist_dim = Brighter<SelectDimY, MistDimY, Plus<Unit, W8>>

// ── the two questions a name's hue is read for, held apart by name. Whose source it
// is (mine against theirs) and, where a verdict is shown, that against theirs:
// these are the pairs a reader must never confuse, so they are the pairs the
// world states a floor for. The floors are today's distances: a drift below any
// of them turns this repository red at the line rather than in somebody's eye.
public typealias MineApartTheirs_X_lit = Apart<KnownNameLitX, LocalTypeLitX, Plus<Unit, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W64>>>>>>
public typealias MineApartTheirs_X_dim = Apart<KnownNameDimX, LocalTypeDimX, Plus<W2, Plus<W16, W128>>>
public typealias MineApartTheirs_Z_lit = Apart<KnownNameLitZ, LocalTypeLitZ, Plus<Unit, Plus<W2, Plus<W8, Plus<W16, W256>>>>>
// The weak one, said out loud rather than left unsaid: 35 where its twin is 400.
// The distinction survives here on X alone, and this line is what will notice
// if that last thread thins too.
public typealias MineApartTheirs_Z_dim = Apart<KnownNameDimZ, LocalTypeDimZ, Plus<W2, W32>>
public typealias TheirsApartBad_Z_lit = Apart<KnownNameLitZ, BadLitZ, Plus<Unit, Plus<W2, Plus<W64, W512>>>>
public typealias TheirsApartBad_Z_dim = Apart<KnownNameDimZ, BadDimZ, Plus<W2, Plus<W8, W512>>>

// ── AND EVERY PAIR OF NAME CHANNELS, MEASURED. All six sit on ONE luminance by
// the Same chain above, deliberately: only hue is meant to tell them apart. So
// hue is the whole of the distinction and it had one floor for one pair. The
// rest, measured across X and Z: in the light half the pairs stand 100 to 740
// apart. In the dark half four of them fall inside a box 182 wide,
// Action↔KnownName 56, Bad↔Law 77, Action↔LocalType 154, LocalType↔KnownName
// 182, where the same pairs in light are 100, 70, 440 and 540.
//
// At a luminance of 419 nothing can be saturated, so every channel comes out a
// pale variant and four of them crowd. That is a design decision about the dark
// half: moving one channel puts it on top of another, measured three ways,
// and it is left open ON PURPOSE. What is not left open is drift: these floors
// are today's distances, so the crowding cannot quietly get worse.
public typealias ActionApartTheirs_X_dim = Apart<KnownNameDimX, ActionDimX, Plus<Unit, Plus<W8, W32>>>
public typealias ActionApartMine_X_dim = Apart<ActionDimX, LocalTypeDimX, Plus<W8, Plus<W32, W64>>>
public typealias BadApartLaw_Z_dim = Apart<BadDimZ, LawDimZ, Plus<Unit, Plus<W4, W64>>>
