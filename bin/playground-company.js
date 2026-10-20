// The generated tab, carried from playground 400b667. Its seed is the pinned organization page.
"use strict";
function thousands(value) { return String(value).replace(/\B(?=(\d{3})+(?!\d))/g, "\u2009"); }
const givenPool = [
    ["Ada", "Female"], ["Grace", "Female"], ["Alan", "Male"], ["Edsger", "Male"],
    ["Barbara", "Female"], ["John", "Male"], ["Margaret", "Female"], ["Donald", "Male"],
    ["Radia", "Female"], ["Ken", "Male"], ["Frances", "Female"], ["Niklaus", "Male"],
];
const familyPool = ["Lovelace", "Hopper", "Turing", "Dijkstra", "Liskov", "Backus",
    "Hamilton", "Knuth", "Perlman", "Thompson", "Allen", "Wirth"];
const bornPool = ["Y1815", "Y1906", "Y1912", "Y1930", "Y1936", "Y1938", "Y1939", "Y1943"];
const rankPool = ["IndividualContributor", "Lead", "Manager"];
const departmentPool = ["Finance", "Engineering", "Sales", "People"];
const sitePool = ["OnSite", "Hybrid", "Remote"];

function mustReplace(view, from, to) {
    if (!view.includes(from)) throw new Error("makeBigCompany anchor lost: " + from.slice(0, 48));
    return view.replace(from, to);
}

function makeBigCompany(count, organizationFile) {
    const organizationView = organizationFile.slice(0, organizationFile.indexOf("// ── the data the page reads"));
    const lines = [];
    // the same three modules the seed names: the people below are the domain's
    // own types, so the generated file builds where the seed builds
    lines.push("import VerificationIsIdentification", "import DocumentKit",
        "import Organization", "");
    lines.push("// A generated company of " + count + " people. Every field is computed from the");
    lines.push("// person's index, so no person depends on another. The cards above count");
    lines.push("// this list live: edit anyone, and the judge re-checks the file as you type.", "");
    let view = organizationView.slice(organizationView.indexOf("// ── the display strings"));
    view = mustReplace(view, '"The Organization"', '"The Organization, N = ' + thousands(count) + '"');
    // the same paragraph layout as the organization: five sentences swapped 1:1
    view = mustReplace(view,
        '"Four people, their departments and shares, written as types in the file on the left."',
        '"This file is the same organization, written out for ' + thousands(count) + ' people."');
    view = mustReplace(view,
        '"Every number below is read out of the file on every edit: nothing is stored beside it."',
        '"A compiler computes what each line means from the other lines. Here that takes 199 seconds."');
    view = mustReplace(view,
        '"Press Hire one more: a fifth person is written into the file, and every number follows."',
        '"The judge computes nothing: every fact is there in full, and a check is one read."');
    view = mustReplace(view,
        '"Plant a lie writes one false line: the judge refuses the file and names the line."',
        '"So on every edit the judge re-reads the whole file, @LINES@ lines, in 0.2 seconds."');
    view = mustReplace(view,
        '"Press Table under the preview: the same people appear as rows."',
        '"Press Plant a lie deep: it breaks one line near the bottom, and the judge names its number."');
    view = mustReplace(view,
        '"Break it by hand: change one Finance to Sales on the left. The judge refuses the share lines."',
        '"The editor shows this file in pages. The judge reads all pages at once."');
    lines.push(view, "// gate-company-data");
    for (let i = 0; i < givenPool.length; i += 1) {
        lines.push("public enum " + givenPool[i][0] + ": GivenNameCycle {");
        lines.push("    public typealias Next = " + givenPool[(i + 1) % givenPool.length][0]);
        lines.push("    public typealias Sex = " + givenPool[i][1], "}");
    }
    for (let i = 0; i < familyPool.length; i += 1) {
        lines.push("public enum " + familyPool[i] + ": FamilyNameCycle {");
        lines.push("    public typealias Next = " + familyPool[(i + 1) % familyPool.length], "}");
    }
    for (let i = 0; i < bornPool.length; i += 1) {
        lines.push("public enum " + bornPool[i] + ": BirthYearCycle {");
        lines.push("    public typealias Next = " + bornPool[(i + 1) % bornPool.length], "}");
    }
    lines.push("");
    const width = String(count - 1).length;
    const handle = (i) => "Emp" + String(i).padStart(width, "0");
    for (let i = 0; i < count; i += 1) {
        lines.push("public enum " + handle(i) + ": Employee, Person {");
        lines.push("    public typealias Rank = " + rankPool[i % 3]);
        lines.push("    public typealias Home = " + departmentPool[i % 4]);
        lines.push("    public typealias Given = " + givenPool[i % 12][0]);
        lines.push("    public typealias Family = " + familyPool[Math.floor(i / 12) % 12]);
        lines.push("    public typealias Born = " + bornPool[Math.floor(i / 144) % 8]);
        lines.push("    public typealias Site = " + sitePool[i % 3]);
        lines.push("    public typealias Sex = Given.Sex", "}");
    }
    lines.push("", "public enum Company: Roster {", "    @StructureBuilder",
        "    public static var body: some Structure {");
    for (let i = 0; i < count; i += 8) {
        const row = [];
        for (let j = i; j < Math.min(i + 8, count); j += 1) row.push(handle(j) + ".self;");
        lines.push("        " + row.join(" "));
    }
    lines.push("    }", "}");
    for (const [team, department, offset] of
        [["FinanceTeam", "Finance", 0], ["EngineeringTeam", "Engineering", 1]]) {
        lines.push("", "public enum " + team + ": Team {", "    @StructureBuilder",
            "    public static var body: some Structure {");
        for (let i = offset; i < count; i += 4) {
            lines.push("        VerifiedInDepartment<" + handle(i) + ", " + department + ">.self;");
        }
        lines.push("    }", "}");
    }
    lines.push("", "public enum AllAccesses: AccessLedger {", "    @StructureBuilder",
        "    public static var body: some Structure {");
    for (let i = 0; i < count; i += 1) {
        lines.push("        VerifiedView<" + handle(i) + ", "
            + departmentPool[i % 4] + "Share>.self;");
    }
    lines.push("    }", "}", "");
    const full = lines.join("\n");
    return full.replace("@LINES@", thousands(full.split("\n").length));
}

if (typeof module !== "undefined") module.exports = { makeBigCompany };
