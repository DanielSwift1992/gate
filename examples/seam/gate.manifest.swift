// what this folder took, and from where. A seam is not found by looking
// at what is lying about: it is here because this side said so, at the
// revision it was taken at. The columns are axes to declared atoms, and
// the one string is the typeName literal. A revision is an atom too.
public protocol Role {}
public enum SeamFile: Role {}
public protocol Theirs {}
public enum Rev_messages_api {}
extension Rev_messages_api { public static var typeName: String { "messages-api@a1b2c3d" } }
public enum TheContract: Theirs {
    public typealias Kind = SeamFile
    public typealias At = Rev_messages_api
}
extension TheContract { public static var typeName: String { "api.swift" } }
public enum Rev_messages_js {}
extension Rev_messages_js { public static var typeName: String { "messages-js@4f10e22" } }
public enum OurSide: Theirs {
    public typealias Kind = SeamFile
    public typealias At = Rev_messages_js
}
extension OurSide { public static var typeName: String { "sdk.swift" } }

