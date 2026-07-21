#!/usr/bin/env python3
# «Старая система клиента»: скрипт, который у него уже есть.
# Правило 1: view только в своём департаменте.
# Правило 2: не больше одного гранта на человека.
# exit 0 = чисто; exit 1 = нарушения, по одному в строке stdout.
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
