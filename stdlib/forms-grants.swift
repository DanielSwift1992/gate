// gate stdlib forms-grants v1: who may read which document, as records
// role: forms
// speaks-for: a-domain
// (exemplar: theory corpus Sources/Examples/Grants.swift @ 0fd0b38).
// Realms are declared atoms, and the fourth is one line rather than a schema change.
// A verb set is a protocol class, containment is conformance, and one gate
// carries both halves: this judge holds the posting equality and the key's
// class alike, the second by walking the ladder declared right here. The
// compiler holds that same class when somebody builds the world as Swift,
// which is the second reader rather than the only one. This head said the
// opposite for as long as it was true, and the day the court arrived it was
// the last page still saying it.

public protocol Reads {}
public protocol Writes: Reads {}
public protocol Administers: Writes {}
public enum ReaderKey: Reads {}
public enum WriterKey: Writes {}
public enum WardenKey: Administers {}

public protocol Realm {}
public protocol Keeper {
    associatedtype Post: Realm
    associatedtype Key: Reads
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

// Ownership is entry whose key administers: whoever may administer a place
// owns what stands in it. One gated form, not a second vocabulary: CODEOWNERS,
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
