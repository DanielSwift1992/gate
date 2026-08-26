// WHO IS WHO HERE, said in this world's own words.
//
// git records an author as an email, and an email is not a person: it is a
// string that appears in a commit. This file is the one place that binds the
// two, and the binding is a claim like every other claim in this repository —
// `gate status` reads it and refuses at this line if the person it names is not
// declared by the world. Rename the keeper in CODEOWNERS and forget this file,
// and the tool says so, at the line, on the next commit.
//
// THE PERSON COMES FROM CODEOWNERS, not from here. `ownership.swift` is printed
// by `gate import codeowners CODEOWNERS --tree . --policy owners.csv`, the
// command CODEOWNERS itself names, and it declares `Owner_DanielSwift1992`
// because the rule `* @DanielSwift1992` is what that file says. This world
// invents no keeper: it points at the one already recorded.
//
// AND NO RANK IS INVENTED. A `MergePolicy` would say merging here requires a
// rank, and a rank is a fact about an organisation this repository does not
// have: one keeper, no ladder above them. Writing `Requires = Manager` to make
// a verb light up would be a fact stated for the tool's convenience, which is
// the failure this tool exists against. So what CODEOWNERS states here is
// ownership, a record the forge may read to route review. This repository
// claims no forge-enforced code-owner approval today: one keeper needs no
// ceremony against themselves, and a green seam is no reason to invent one.
// What stands here is the fact that is true: this email is that keeper. `gate guard merge` reads a world with people and ranks in it; this
// one has a keeper and a tree, and says so rather than pretending otherwise.
public enum MailDaniil: Identity {
    public typealias Person = Owner_DanielSwift1992
}
extension MailDaniil { public static var typeName: String { "daniel.swift.1992@gmail.com" } }
