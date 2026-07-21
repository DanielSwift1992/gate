#!/usr/bin/env python3
# "The client's old system": the script he already has.
# Rule 1: view only within one's own department.
# Rule 2: at most one grant per person.
# exit 0 = clean; exit 1 = violations, one per stdout line.
import csv, sys

people = {p["id"]: p for p in csv.DictReader(open(sys.argv[1]))}
grants = list(csv.DictReader(open(sys.argv[2])))
bad = []
share_home = {"FinanceShare": "Finance", "EngineeringShare": "Engineering",
              "SalesShare": "Sales", "PeopleShare": "People"}
seen = {}
for i, g in enumerate(grants, start=2):
    who, doc = g["who"], g["doc"]
    if who not in people:
        bad.append(f"grants.csv:{i}: unknown person {who}")
        continue
    if doc not in share_home:
        bad.append(f"grants.csv:{i}: unknown doc {doc}")
        continue
    if people[who]["home"] != share_home[doc]:
        bad.append(f"grants.csv:{i}: {who} ({people[who]['home']}) may not view {doc}")
    seen.setdefault(who, []).append(i)
for who, lines in seen.items():
    if len(lines) > 1:
        bad.append(f"grants.csv:{lines[1]}: {who} holds {len(lines)} grants, one allowed")
print("\n".join(bad))
sys.exit(1 if bad else 0)
