// gate stdlib genre-grants v1 — the domain genre, one page
// (exemplar: theory corpus Sources/Examples/Grants.swift @ 0fd0b38).
// Realms are declared atoms (the fourth is one line, not a schema change);
// a verb set is a protocol class, containment is conformance; one gate
// carries two tiers: the compiler holds the key's class, the judge holds
// the posting equality.

public protocol Reads {}
public protocol Writes: Reads {}
public protocol Administers: Writes {}
public enum ReaderKey: Reads {}
public enum WriterKey: Writes {}
public enum WardenKey: Administers {}

public protocol Realm {}
public protocol Keeper {
    associatedtype Post: Realm
    associatedtype Key
}
public protocol Room {
    associatedtype Place: Realm
}
public protocol Entered {}
public enum Enter<
    Who: Keeper,
    Into: Room
> {}
extension Enter: Entered
where Who.Key: Writes, Who.Post == Into.Place {}
