// gate stdlib bench-atoms v1: the bench's own settings, as declarations
// role: gate's own
// The bench is not configured by a toggle but by a claim in your personal world:
// MyBench says which theme the page uses, MyJournal says what the history
// shows. The values live here, and a value from nowhere else is named on its
// line the way any other claim is: the bench judged by its own rules.

/// A theme the page uses. Chosen by declaration, never by a button.
public protocol BenchTheme {}
public enum Light: BenchTheme {}
public enum Dark: BenchTheme {}

/// The bench itself. Your MyBench conforms to it to choose a theme:
///
///     public enum MyBench: Bench {
///         public typealias Theme = Dark
///     }
public protocol Bench {
    associatedtype Theme: BenchTheme
}

/// What the journal counts as its world: the files of this layout, or the
/// whole repository.
public protocol JournalScope {}
public enum World: JournalScope {}
public enum AllRepo: JournalScope {}

/// Whose commits the journal shows: only yours, or everyone's.
public protocol JournalAuthor {}
public enum Me: JournalAuthor {}
public enum Anyone: JournalAuthor {}

/// The journal dashboard. Your MyJournal conforms to it to say what it shows:
///
///     public enum MyJournal: Journal {
///         public typealias Scope = AllRepo
///     }
public protocol Journal {
    associatedtype Scope: JournalScope
    associatedtype Author: JournalAuthor
}
