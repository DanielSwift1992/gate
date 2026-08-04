// gate stdlib grammar v1: the scopes and atoms the bench walks, as records
// role: forms
//
// The walk is agnostic: a scope opens, a scope closes, that is all it
// knows, and swift is what it reads. WHICH scopes exist, how each one is
// spelled, and which may stand inside which: that is grammar, ours, and
// grammar is records judged with the rest of the shelf. A scope is an
// atom, first class; nesting is a relation between two of them, so
// nesting is claims, one per allowed pair. No claim admits anything into
// a note or into a string, and that silence IS their opacity: nothing to
// flag, just no record saying otherwise. An empty stack admits every
// scope; the file itself is the one place that needs no admitting.
// Two closers carry no spelling a literal can hold, the line's end and
// the quote; they are named, and the walk knows those two names.

public protocol Glyph {}
public enum SlashSlash: Glyph {}
extension SlashSlash { public static var typeName: String { "//" } }
public enum BraceOpen: Glyph {}
extension BraceOpen { public static var typeName: String { "{" } }
public enum BraceClose: Glyph {}
extension BraceClose { public static var typeName: String { "}" } }
public enum AngleOpen: Glyph {}
extension AngleOpen { public static var typeName: String { "<" } }
public enum AngleClose: Glyph {}
extension AngleClose { public static var typeName: String { ">" } }
public enum LineEnd: Glyph {}
public enum QuoteGlyph: Glyph {}

public protocol Walked {
    associatedtype Opens: Glyph
    associatedtype Closes: Glyph
}
public enum NoteScope: Walked {
    public typealias Opens = SlashSlash
    public typealias Closes = LineEnd
}
public enum StringScope: Walked {
    public typealias Opens = QuoteGlyph
    public typealias Closes = QuoteGlyph
}
public enum BodyScope: Walked {
    public typealias Opens = BraceOpen
    public typealias Closes = BraceClose
}
public enum GateScope: Walked {
    public typealias Opens = AngleOpen
    public typealias Closes = AngleClose
}

/// one scope may stand inside another only where a record says so
public enum Nests<Inner: Walked, Outer: Walked> {}

public typealias Body_in_body = Nests<BodyScope, BodyScope>
public typealias Gate_in_body = Nests<GateScope, BodyScope>
public typealias Gate_in_gate = Nests<GateScope, GateScope>
public typealias Note_in_body = Nests<NoteScope, BodyScope>
public typealias Note_in_gate = Nests<NoteScope, GateScope>
public typealias String_in_body = Nests<StringScope, BodyScope>
public typealias String_in_gate = Nests<StringScope, GateScope>

// an atom may be scoped: legal inside one scope and nowhere else. The
// letter's mark is the first: `==` opens a lit phrase, and only a note
// may hold it, which is why a mark survives every reprint of the letter.
public protocol ScopedAtom {
    associatedtype Home: Walked
}
public enum Mark: ScopedAtom {
    public typealias Home = NoteScope
}
extension Mark { public static var typeName: String { "==" } }

// The words of a world are atoms too, with the spelling each one wears.
// A line opens with a word only where a claim grants it: the file's top
// and a record's body are the two homes, and a word with no claim for a
// home may not open a line there. What may FOLLOW an opener is the
// line's form, already read elsewhere: the walk carries scopes, these
// claims carry openings, and nothing here is a second reading of either.
public protocol Word {}
// a modifier stands before an opener and does not use the opening up:
// `public enum` is one opening, not two
public protocol LineModifier {}
public enum PublicWord: Word, LineModifier {}
extension PublicWord { public static var typeName: String { "public" } }
public enum EnumWord: Word {}
extension EnumWord { public static var typeName: String { "enum" } }
public enum TypealiasWord: Word {}
extension TypealiasWord { public static var typeName: String { "typealias" } }
public enum ExtensionWord: Word {}
extension ExtensionWord { public static var typeName: String { "extension" } }

// the two homes a line can open in, and one claim per granted pair
public enum TopHome {}
public enum BodyHome {}
public enum OpensLine<W: Word, H> {}

public typealias Enum_opens_top = OpensLine<EnumWord, TopHome>
public typealias Typealias_opens_top = OpensLine<TypealiasWord, TopHome>
public typealias Extension_opens_top = OpensLine<ExtensionWord, TopHome>
public typealias Typealias_opens_body = OpensLine<TypealiasWord, BodyHome>

// After an opener the rest of the line is the form: an ordered row of
// slots. The rows are records here, and the offer branches that used to
// know each row by heart are its readers now: cut a row and its
// question dies with it. An answer slot names the kind of answer a
// position takes; a structural slot wears the glyph it is, as a record,
// so the walker reads the row and no branch keeps a regex of its own.
public protocol LineSlot {}
public enum NameSlot: LineSlot {}
public enum AxisNameSlot: LineSlot {}
public enum ExistingSlot: LineSlot {}
public enum EqualsSlot: LineSlot {}
extension EqualsSlot { public static var typeName: String { "=" } }
public enum ValueSlot: LineSlot {}
public enum ColonSlot: LineSlot {}
extension ColonSlot { public static var typeName: String { ":" } }
public enum ProtosSlot: LineSlot {}

public enum LineForm<W: Word, S1: LineSlot, S2: LineSlot, S3: LineSlot> {}

public typealias Typealias_form = LineForm<TypealiasWord, AxisNameSlot, EqualsSlot, ValueSlot>
public typealias Enum_form = LineForm<EnumWord, NameSlot, ColonSlot, ProtosSlot>
public typealias Extension_form = LineForm<ExtensionWord, ExistingSlot, ColonSlot, ProtosSlot>

// THE FORMS DIALECT. A forms page opens lines with words of its own,
// granted the same way: one claim per word per home. Four homes stand
// beside the world's two, told apart by what the body frame's head
// opened: the page's top, a record's body, a protocol's body, an
// extension's body. A modifier is granted per home too, and a home no
// claim names stays silent: static is no word of a world.
public enum FormsTopHome {}
public enum FormsRecordHome {}
public enum FormsProtocolHome {}
public enum FormsExtensionHome {}

public enum ProtocolWord: Word {}
extension ProtocolWord { public static var typeName: String { "protocol" } }
public enum AssociatedtypeWord: Word {}
extension AssociatedtypeWord { public static var typeName: String { "associatedtype" } }
public enum VarWord: Word {}
extension VarWord { public static var typeName: String { "var" } }
public enum StaticWord: Word, LineModifier {}
extension StaticWord { public static var typeName: String { "static" } }

public typealias Protocol_opens_formstop = OpensLine<ProtocolWord, FormsTopHome>
public typealias Enum_opens_formstop = OpensLine<EnumWord, FormsTopHome>
public typealias Typealias_opens_formstop = OpensLine<TypealiasWord, FormsTopHome>
public typealias Extension_opens_formstop = OpensLine<ExtensionWord, FormsTopHome>
public typealias Typealias_opens_formsrecord = OpensLine<TypealiasWord, FormsRecordHome>
public typealias Associatedtype_opens_formsprotocol = OpensLine<AssociatedtypeWord, FormsProtocolHome>
public typealias Var_opens_formsextension = OpensLine<VarWord, FormsExtensionHome>

// the modifiers' homes: public stands in five, static in one
public typealias Public_stands_top = OpensLine<PublicWord, TopHome>
public typealias Public_stands_body = OpensLine<PublicWord, BodyHome>
public typealias Public_stands_formstop = OpensLine<PublicWord, FormsTopHome>
public typealias Public_stands_formsrecord = OpensLine<PublicWord, FormsRecordHome>
public typealias Public_stands_formsextension = OpensLine<PublicWord, FormsExtensionHome>
public typealias Static_stands_formsextension = OpensLine<StaticWord, FormsExtensionHome>

// a word may CONTINUE an open line instead of opening one: a broken
// extension head carries its `where` to the next line, and the court
// judges the pair as one sentence. A continuer opens nothing, so the
// floor never offers it, and the moment's marker steps over it and
// leaves the sentence to the court.
public enum WhereWord: Word {}
extension WhereWord { public static var typeName: String { "where" } }
public enum ContinuesLine<W: Word> {}
public typealias Where_continues = ContinuesLine<WhereWord>
