// gate stdlib forms-organization v1: people, departments, and who reads what
// role: forms
// This is the vocabulary `gate import` prints a
// world in: the forms and the axes, with no facts of anyone's in it.
//
// A domain's forms are the unit that ships. Everything a world of this kind can say is
// here, so a reader can see the whole language before reading a single fact,
// and a translator has something to translate INTO.

/// A place in the organization. Departments are its atoms.
public protocol Department {}
public enum Finance: Department {}
public enum Engineering: Department {}
public enum Sales: Department {}
public enum People: Department {}

/// What somebody is trusted with. The ladder is stated, never inferred.
public protocol Ranked {}
public enum IndividualContributor: Ranked {}
public enum Lead: Ranked {}
public enum Manager: Ranked {}

/// Where the work happens.
public protocol Workplace {}
public enum OnSite: Workplace {}
public enum Hybrid: Workplace {}
public enum Remote: Workplace {}

/// A document belongs to exactly one department: that is the fact every
/// access claim is read against.
public protocol Document {
    associatedtype Home: Department
}
public enum FinanceShare: Document { public typealias Home = Finance }
public enum EngineeringShare: Document { public typealias Home = Engineering }
public enum SalesShare: Document { public typealias Home = Sales }
public enum PeopleShare: Document { public typealias Home = People }

/// A person: a department, a rank, a workplace. Names and birth years are
/// carried as their own cycles, so a roster stays a roster.
public protocol Employee {
    associatedtype Home: Department
    associatedtype Rank: Ranked
    associatedtype Site: Workplace
}

/// Who somebody is, apart from where they work. A name is not a string here:
/// each one is an atom, and the atoms of a kind form a ring, so a roster can
/// be walked and a generated one never runs out of names.
public protocol Person {
    associatedtype Given: GivenNameCycle
    associatedtype Family: FamilyNameCycle
    associatedtype Born: BirthYearCycle
    associatedtype Sex: Sexed
}
public protocol GivenNameCycle {
    associatedtype Next: GivenNameCycle
    associatedtype Sex: Sexed
}
public protocol FamilyNameCycle {
    associatedtype Next: FamilyNameCycle
}
public protocol BirthYearCycle {
    associatedtype Next: BirthYearCycle
}

/// The two the roster records, as atoms like every other value here.
public protocol Sexed {}
public enum Male: Sexed {}
public enum Female: Sexed {}

/// The gates. A claim of one of these forms is what the judge reads: it holds
/// when the two sides agree, and refuses with both names when they do not.
///
///     VerifiedView<Emp9001, FinanceShare>       may this person read this?
///     VerifiedInDepartment<Emp9001, Finance>    do they work there?
///     VerifiedAtRank<Emp9001, Manager>          do they hold that rank?
///     VerifiedAtWorkplace<Emp9001, OnSite>      do they work at that site?
///
/// An access ledger is a list of such claims, and a team is a list of the
/// people in it: one file, judged whole.
public protocol Verified {}

public enum VerifiedView<Who: Employee, What: Document> {}
extension VerifiedView: Verified
where Who.Home == What.Home {}

public enum VerifiedInDepartment<Who: Employee, At: Department> {}
extension VerifiedInDepartment: Verified
where Who.Home == At {}

public enum VerifiedAtRank<Who: Employee, At: Ranked> {}
extension VerifiedAtRank: Verified
where Who.Rank == At {}

public enum VerifiedAtWorkplace<Who: Employee, At: Workplace> {}
extension VerifiedAtWorkplace: Verified
where Who.Site == At {}

/// A ledger is a list of claims, a team is a list of the people in it. One
/// file, judged whole.
public protocol AccessLedger {}
public protocol Team {}
