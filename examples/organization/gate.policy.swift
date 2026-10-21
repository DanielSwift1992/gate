// who someone is, and what an action demands: facts of yours,
// beside the world and yours to change.
public enum MailYou: Identity {
    public typealias Person = Emp9000
}
extension MailYou { public static var typeName: String { "you@example.com" } }

public enum MergePolicy {
    public typealias Requires = Manager
}
