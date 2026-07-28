// gate stdlib forms-grants v1 — the domain genre, one page
// role: forms
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
/// whoever enters a place must be posted to it, and carry a key that writes
public protocol Entered {}
public enum Enter<
    Who: Keeper,
    Into: Room
> {}
extension Enter: Entered
where Who.Key: Writes, Who.Post == Into.Place {}

// Ownership is entry at the warden's threshold: whoever may administer a place
// owns what stands in it. One gated form, not another crystal — CODEOWNERS,
// Kubernetes RBAC and an org's grants are the same question about the same
// atoms: who may do what, where.
/// an owner and the path they own must share one zone
public protocol Owned {}
public enum Owns<
    Who: Keeper,
    What: Room
> {}
extension Owns: Owned
where Who.Key: Administers, Who.Post == What.Place {}
