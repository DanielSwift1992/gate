// gate stdlib bench-registers v1: the faces this page speaks in.
// role: gate's own
// A register is what a thing IS, said once: a face, a size, and how far one
// line stands from the next. The page had been restating them instead:
// nineteen font declarations where four registers were declared, half of them
// the same register written again with the line-height a hair different. A
// second statement of a thing either drifts or coarsens; these drifted.
//
// Sizes are spelled in TENTHS of a pixel and leadings in HUNDREDTHS of their
// own size, because a world spells its numbers on its own ladder from Unit and
// 12.5 is not a whole anything. What is written here is what the page renders
// today, to the last tenth: the point is not to change how it looks but to
// make it impossible to say twice.

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

// ── the forms this file holds itself to ──
public protocol Ordered {}
public enum Taller<Hi, Lo, Slack>: Close {}
extension Taller: Ordered
where Hi == Plus<Lo, Plus<Unit, Slack>> {}
public enum AtLeast<Have, Floor, Slack>: Close {}
extension AtLeast: Ordered
where Have == Plus<Floor, Slack> {}

public protocol Face {}
public enum Mono: Face {}
public enum Sans: Face {}

// And how hard a register is set. This was a list of three names inside the
// tool: `Brand`, `Headline`, `Headsmall` got weight, everything else did not,
// which is a world's names living in a mechanism, the one thing no layer here
// is allowed to do. A register that is set firm says so itself, on the same
// axis as its face, and a name this file never mentions gets no special
// treatment from anywhere.
public protocol Stress {}
public enum Plain: Stress {}
public enum Firm: Stress {}

public protocol Register {
    associatedtype On: Face
    associatedtype Set: Stress
}

public typealias BrandSize = Plus<W2, Plus<W4, Plus<W16, W128>>>
public typealias BrandLead = Plus<W8, Plus<W16, Plus<W32, W64>>>
public enum Brand: Register {
    public typealias On = Sans
    public typealias Set = Firm
}

public typealias CaptionSize = Plus<W2, Plus<W4, Plus<W8, Plus<W32, W64>>>>
public typealias CaptionLead = Plus<W4, Plus<W8, W128>>
public enum Caption: Register {
    public typealias On = Sans
    public typealias Set = Plain
}

public typealias CaptionbareSize = Plus<W2, Plus<W4, Plus<W8, Plus<W32, W64>>>>
public enum Captionbare: Register {
    public typealias On = Sans
    public typealias Set = Plain
}

public typealias CaptionlineSize = Plus<W2, Plus<W4, Plus<W8, Plus<W32, W64>>>>
public typealias CaptionlineLead = Plus<Unit, Plus<W16, W128>>
public enum Captionline: Register {
    public typealias On = Sans
    public typealias Set = Plain
}

public typealias CaptionlooseSize = Plus<W2, Plus<W4, Plus<W8, Plus<W32, W64>>>>
public typealias CaptionlooseLead = Plus<W2, Plus<W4, Plus<W16, W128>>>
public enum Captionloose: Register {
    public typealias On = Sans
    public typealias Set = Plain
}

public typealias CodeinlineSize = Plus<W8, Plus<W16, Plus<W32, W64>>>
public typealias CodeinlineLead = Plus<W4, Plus<W8, W128>>
public enum Codeinline: Register {
    public typealias On = Mono
    public typealias Set = Plain
}

public typealias ControlSize = Plus<W2, W128>
public enum Control: Register {
    public typealias On = Sans
    public typealias Set = Plain
}

public typealias ControlsmallSize = Plus<Unit, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W64>>>>>
public enum Controlsmall: Register {
    public typealias On = Sans
    public typealias Set = Plain
}

public typealias FactSize = Plus<Unit, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W64>>>>>
public typealias FactLead = Plus<Unit, Plus<W16, W128>>
public enum Fact: Register {
    public typealias On = Mono
    public typealias Set = Plain
}

public typealias FactbareSize = Plus<Unit, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W64>>>>>
public enum Factbare: Register {
    public typealias On = Mono
    public typealias Set = Plain
}

// the same fact, said firm, which is what a selected row in the panel is. The
// weight had been a number beside a background colour, so nothing stopped it
// from being given a size of its own, and a list that changes size when you
// click it is a list that moves under the hand.
public typealias FactfirmSize = Plus<Unit, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W64>>>>>
public typealias FactfirmLead = Plus<Unit, Plus<W16, W128>>
public enum Factfirm: Register {
    public typealias On = Mono
    public typealias Set = Firm
}

public typealias HeadlineSize = Plus<W2, Plus<W4, Plus<W16, W128>>>
public typealias HeadlineLead = Plus<W2, W128>
public enum Headline: Register {
    public typealias On = Sans
    public typealias Set = Firm
}

public typealias HeadsmallSize = Plus<W2, W128>
public typealias HeadsmallLead = Plus<W4, Plus<W32, W64>>
public enum Headsmall: Register {
    public typealias On = Sans
    public typealias Set = Firm
}

public typealias KeycapSize = Plus<W2, Plus<W4, Plus<W8, Plus<W32, W64>>>>
public enum Keycap: Register {
    public typealias On = Mono
    public typealias Set = Plain
}

public typealias MonolineSize = Plus<W2, Plus<W4, Plus<W8, Plus<W32, W64>>>>
public typealias MonolineLead = Plus<Unit, Plus<W16, W128>>
public enum Monoline: Register {
    public typealias On = Mono
    public typealias Set = Plain
}

public typealias ProseSize = Plus<W2, W128>
public typealias ProseLead = Plus<W2, Plus<W4, Plus<W16, W128>>>
public enum Prose: Register {
    public typealias On = Sans
    public typealias Set = Plain
}

public typealias ProselooseSize = Plus<W2, W128>
public typealias ProselooseLead = Plus<W32, W128>
public enum Proseloose: Register {
    public typealias On = Sans
    public typealias Set = Plain
}

public typealias SourceSize = Plus<Unit, Plus<W4, Plus<W8, Plus<W16, Plus<W32, W64>>>>>
public typealias SourceLead = Plus<W8, Plus<W16, W128>>
public enum Source: Register {
    public typealias On = Mono
    public typealias Set = Plain
}

// ── AND THE VOICE THE LEFT PANEL SPEAKS IN, which it had been speaking without
// being declared anywhere: a section label, set firm at caption size. There was
// a second (the line under it, set half) declared the same day for the
// journal's blurb and the judge's caption; the journal left the panel and the
// last speaker went with it. A register nobody speaks in is a word kept in a
// vocabulary for its own sake, and three certificates over it look like weight
// being carried.
public typealias RubricSize = Plus<W2, Plus<W4, Plus<W8, Plus<W32, W64>>>>
public typealias RubricLead = Plus<W4, Plus<W8, W128>>
public enum Rubric: Register {
    public typealias On = Sans
    public typealias Set = Firm
}

public typealias SpeechSize = Plus<W2, W128>
public typealias SpeechLead = Plus<Unit, Plus<W16, W128>>
public enum Speech: Register {
    public typealias On = Sans
    public typealias Set = Plain
}

// ── AND THE LAWS. A size ladder that only goes up, so `caption` can never
// quietly become the size of `speech`; and a leading at least as tall as the
// letters it sets, because a line that overlaps the next is not a line. These
// are today's numbers as a floor: drift below one and this repository refuses
// at the line rather than in somebody's eye a week later.

public typealias CodeinlineOverCaption = Taller<CodeinlineSize, CaptionSize, Plus<Unit, W8>>
public typealias FactOverCodeinline = Taller<FactSize, CodeinlineSize, W4>
public typealias SpeechOverFact = Taller<SpeechSize, FactSize, W4>
public typealias BrandOverSpeech = Taller<BrandSize, SpeechSize, Plus<Unit, Plus<W2, W16>>>
public typealias BrandLeadClearsItsLetters = AtLeast<BrandLead, Plus<W4, Plus<W32, W64>>, Plus<W4, W16>>
public typealias CaptionLeadClearsItsLetters = AtLeast<CaptionLead, Plus<W4, Plus<W32, W64>>, Plus<W8, W32>>
public typealias CaptionlineLeadClearsItsLetters = AtLeast<CaptionlineLead, Plus<W4, Plus<W32, W64>>, Plus<Unit, Plus<W4, Plus<W8, W32>>>>
public typealias CaptionlooseLeadClearsItsLetters = AtLeast<CaptionlooseLead, Plus<W4, Plus<W32, W64>>, Plus<W2, Plus<W16, W32>>>
public typealias CodeinlineLeadClearsItsLetters = AtLeast<CodeinlineLead, Plus<W4, Plus<W32, W64>>, Plus<W8, W32>>
public typealias FactLeadClearsItsLetters = AtLeast<FactLead, Plus<W4, Plus<W32, W64>>, Plus<Unit, Plus<W4, Plus<W8, W32>>>>
public typealias HeadlineLeadClearsItsLetters = AtLeast<HeadlineLead, Plus<W4, Plus<W32, W64>>, Plus<W2, Plus<W4, Plus<W8, W16>>>>
public typealias HeadsmallLeadClearsItsLetters = AtLeast<HeadsmallLead, Plus<W4, Plus<W32, W64>>, Never>
public typealias MonolineLeadClearsItsLetters = AtLeast<MonolineLead, Plus<W4, Plus<W32, W64>>, Plus<Unit, Plus<W4, Plus<W8, W32>>>>
public typealias ProseLeadClearsItsLetters = AtLeast<ProseLead, Plus<W4, Plus<W32, W64>>, Plus<W2, Plus<W16, W32>>>
public typealias ProselooseLeadClearsItsLetters = AtLeast<ProselooseLead, Plus<W4, Plus<W32, W64>>, Plus<W4, Plus<W8, Plus<W16, W32>>>>
public typealias SourceLeadClearsItsLetters = AtLeast<SourceLead, Plus<W4, Plus<W32, W64>>, Plus<W4, Plus<W16, W32>>>
public typealias RubricLeadClearsItsLetters = AtLeast<RubricLead, Plus<W4, Plus<W32, W64>>, Plus<W8, W32>>
// a label and its note are the page's quiet size, said once: let either drift up
// and the panel starts shouting in a corner nobody chose to make loud
public typealias FactfirmIsFactSized = AtLeast<FactfirmSize, FactSize, Never>
public typealias FactfirmLeadsLikeFact = AtLeast<FactfirmLead, FactLead, Never>
public typealias FactfirmLeadClearsItsLetters = AtLeast<FactfirmLead, Plus<W4, Plus<W32, W64>>, Plus<Unit, Plus<W4, Plus<W8, W32>>>>
public typealias RubricIsCaptionSized = AtLeast<RubricSize, CaptionSize, Never>
public typealias SpeechLeadClearsItsLetters = AtLeast<SpeechLead, Plus<W4, Plus<W32, W64>>, Plus<Unit, Plus<W4, Plus<W8, W32>>>>
