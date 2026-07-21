// printed by gate import rbac — the K8s access world in the domain genre
// (the exemplar: theory corpus Sources/Examples/Grants.swift @ 0fd0b38).
// Realms are namespaces plus the cluster scope. A role is a room stating its
// realm; a binding is a keeper stating its post; the gate's equality is the
// K8s invariant itself: a RoleBinding and its Role live in one namespace.
// Tier one (Who.Key: Writes) is the compiler's; this file is judged by the
// agnostic where-judge (canon v2), which holds the posting equalities.

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

public enum Ns_ci: Realm {}
public enum Ns_prod: Realm {}
public enum Ns_staging: Realm {}
public enum ClusterScope: Realm {}

public enum Role_prod_deployer: Room {
    public typealias Place = Ns_prod
}
public enum Role_staging_reader: Room {
    public typealias Place = Ns_staging
}
public enum CR_ops_admin: Room {
    public typealias Place = ClusterScope
}

public enum B_prod_deploy_bind: Keeper {
    public typealias Post = Ns_prod
    public typealias Key = WriterKey
}
public typealias Bind_prod_deploy_bind = Enter<B_prod_deploy_bind, Role_prod_deployer>
public enum B_staging_read_bind: Keeper {
    public typealias Post = Ns_staging
    public typealias Key = ReaderKey
}
public typealias Bind_staging_read_bind = Enter<B_staging_read_bind, Role_staging_reader>
public enum B_prod_ghost_bind: Keeper {
    public typealias Post = Ns_prod
    public typealias Key = ReaderKey
}
public typealias Bind_prod_ghost_bind = Enter<B_prod_ghost_bind, Role_prod_old_deployer>
public enum B_ci_cross_bind: Keeper {
    public typealias Post = Ns_ci
    public typealias Key = ReaderKey
}
public typealias Bind_ci_cross_bind = Enter<B_ci_cross_bind, Role_prod_deployer>
public enum B_staging_ops_bind: Keeper {
    public typealias Post = ClusterScope
    public typealias Key = WardenKey
}
public typealias Bind_staging_ops_bind = Enter<B_staging_ops_bind, CR_ops_admin>
