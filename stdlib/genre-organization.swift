// gate stdlib genre-organization v1 — people, the places they work, and the
// documents those places own. This is the vocabulary `gate import` prints a
// world in: the forms and the axes, with no facts of anyone's in it.
//
// A genre is the unit that ships. Everything a world of this kind can say is
// here, so a reader can see the whole language before reading a single fact,
// and a translator has something to translate INTO.

/// A place in the organization. Departments are its atoms.
public protocol Department {}
public enum Finance: Department {}
public enum Engineering: Department {}
public enum Sales: Department {}
public enum People: Department {}

/// What somebody is trusted with. The ladder is stated, never inferred.
public protocol Rank {}
public enum IndividualContributor: Rank {}
public enum Lead: Rank {}
public enum Manager: Rank {}

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
    associatedtype Rank
    associatedtype Site: Workplace
}

/// The gates. A claim of one of these forms is what the judge reads: it holds
/// when the two sides agree, and refuses with both names when they do not.
///
///     VerifiedView<Emp9001, FinanceShare>     — may this person read this?
///     VerifiedInDepartment<Emp9001, Finance>  — do they work there?
///     VerifiedAtRank<Emp9001, Manager>        — do they hold that rank?
///     VerifiedAtWorkplace<Emp9001, OnSite>    — do they work there?
///
/// An access ledger is a list of such claims, and a team is a list of the
/// people in it: one file, judged whole.
public protocol AccessLedger {}
public protocol Team {}
