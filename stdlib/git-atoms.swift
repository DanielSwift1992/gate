// gate stdlib git-atoms v1: the git world itself, as declarations.
// role: forms
// The substrate's own objects become atoms: judged records reference them.
// Enforcement stays with git and the platform. These are the names.

/// A person behind an email: tables/identities.csv maps email -> person.
public protocol Identity {}

/// A zone a recognizer may search. An atom is declared outside scopes, and
/// occurrences are looked for only in declared scopes: no line, no search.
public protocol Scope {}
public enum CommitMessage: Scope {}
public enum CommitAuthor: Scope {}
public enum BranchName: Scope {}
public enum FilePath: Scope {}

/// The repository's own objects, as places records may reference.
public protocol GitPlace {}
public enum TheBranch: GitPlace {}
public enum TheFile: GitPlace {}
public enum TheCommit: GitPlace {}
