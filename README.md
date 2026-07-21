# gate

A static layer of logical integrity over git. The world of facts lives in
your own repository; the judge answers in milliseconds; a refusal names
the line of your own file. Nothing runs, nothing is hosted, nothing leaves
your repo.

    gate init            # a world skeleton in your repo (hook wires itself)
    gate survey          # t0, read-only: unwritten links from your own history
    gate import ...      # your CSV tables -> the facts world
    gate status          # what disagrees right now (judged in ms)
    gate check / diff / apply / verify / guard / library / report / serve / ui
    gate import rbac rbac.json   # floor 2: a K8s RBAC world in the domain genre
                                 # (kubectl get roles,clusterroles,rolebindings -A -o json);
                                 # a stale roleRef and a cross-namespace binding are named
                                 # by their k8s source in milliseconds

Internal working notes live in private/ (untracked; see .gitignore) —
spec, theory map, scenarios, the rule-form catalogue. Client-facing
documentation will be written separately.

The judge binary (bin/gate-judge) is built from the public theory corpus:
bin/build-judge.sh [pin]. Tests: python3 tests/smoke.py (16 checks).

Private working notes and the experimental record live outside this repo.
