"""All relations of every original D65 ID, with an addressed false answer.

The old page is gate 61422112396ff7e3406c2cf1c1c6fe3bc9da213e verbatim.
Its arguments give an independent integer oracle for the stated D65 laws.
The present page supplies the sum definitions and the readings actually run.
"""
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import re
import subprocess

OLD_SHA256 = "e196c6c7ce83fbab29d5e1b5e1da78677583d3f7705b7ad1a0eee5c0af2ca69f"


def term(text):
    tokens = re.findall(r'[A-Za-z_]\w*|[<>,]', text)
    assert ''.join(tokens) == re.sub(r'\s+', '', text), text
    i = 0
    def read():
        nonlocal i
        name = tokens[i]; i += 1
        args = []
        if i < len(tokens) and tokens[i] == '<':
            i += 1
            while True:
                args.append(read())
                if tokens[i] == '>':
                    i += 1
                    break
                assert tokens[i] == ','
                i += 1
        return name, tuple(args)
    value = read()
    assert i == len(tokens)
    return value


def written(t):
    name, args = t
    return name + ('<' + ', '.join(map(written, args)) + '>' if args else '')


def definitions(text):
    found = {}
    for name, params, body in re.findall(r'^public typealias (\w+)(?:<([^>]+)>)? = ([^\n]+)', text, re.M):
        found[name] = (tuple(p.split(':')[0].strip() for p in params.split(',')) if params else (), term(body))
    return found


def evaluator(defs):
    @lru_cache(None)
    def value(t, env=()):
        name, args = t
        if name in dict(env):
            assert not args
            return dict(env)[name]
        if name in ('Unit', 'Never'):
            assert not args
            return int(name == 'Unit')
        if name == 'Plus':
            assert len(args) == 2
            return value(args[0], env) + value(args[1], env)
        params, body = defs[name]
        assert len(params) == len(args)
        return value(body, tuple(zip(params, [value(a, env) for a in args])))
    return value


def expected(kind, a):
    if kind == 'Grey':
        x, y, z, lo, hi, xlo, xhi = a
        return [(25*z, 27*y+lo), (28*y, 25*z+hi), (25*x, 23*y+xlo), (24*y, 25*x+xhi)]
    if kind == 'GreyFloor':
        x, y, z, lo, hi = a
        return [(x, y), (25*z, 27*y+lo), (28*y, 25*z+hi)]
    y, z, margin = a
    assert kind in ('TowardBlue', 'TowardWarm')
    return [(25*z, 28*y+1+margin)] if kind == 'TowardBlue' else [(27*y, 25*z+1+margin)]


def case_records(here):
    """Enumerate the original IDs and their relations before running a court."""
    root = Path(here)
    old = (root / 'tests/fixtures/bench-palette-before-dag.swift').read_text()
    defs = definitions((root / 'stdlib/bench-palette.swift').read_text())
    defs['Twice'] = (('S',), term('Plus<S, S>'))
    evaluate = evaluator(defs)
    records = []
    for ident in re.findall(r'^// gate-unsupported: (\w+) \|', old, re.M):
        params, (kind, args) = defs[ident]
        assert not params, ident
        records.append((ident, kind, args, expected(kind, [evaluate(a) for a in args])))
    return records


def checks(here, scratch, premise):
    root = Path(here)
    old_bytes = (root / 'tests/fixtures/bench-palette-before-dag.swift').read_bytes()
    old = old_bytes.decode()
    body = (root / 'stdlib/bench-palette.swift').read_text()
    ledger = json.loads((root / 'tests/fixtures/bench-obligations.json').read_text())['pages']['bench-palette']['claims']
    ids = re.findall(r'^// gate-unsupported: (\w+) \|', old, re.M)
    defs, before = definitions(body), definitions(old)
    defs['Twice'] = (('S',), term('Plus<S, S>'))
    evaluate = evaluator(defs)
    forms = {}
    for name, params, fields in re.findall(r'public enum (\w+)<([^>]+)>: Close\s*\{([^}]+)\}', body):
        forms[name] = (tuple(p.split(':')[0].strip() for p in params.split(',')),
                       {n: term(t) for n, t in re.findall(r'typealias (R\d+) = ([^\n]+)', fields)})
    yield ('the former D65 page is the pinned source of all 26 outstanding IDs',
           hashlib.sha256(old_bytes).hexdigest() == OLD_SHA256 and len(ids) == 26)
    ledger_by_id = {row['id']: row for row in ledger}
    records = case_records(here)
    for ident, kind, args, pairs in records:
        params, expr = defs[ident]
        kind, args = expr
        assert not params and before[ident] == defs[ident], ident
        numbers = [evaluate(a) for a in args]
        pairs = expected(kind, numbers)
        names, fields = forms[kind]
        env = tuple(zip(names, numbers))
        actual = []
        for i in range(1, len(pairs)+1):
            head, sides = fields['R'+str(i)]
            assert head == 'Luminance' and len(sides) == 2
            actual.append(tuple(evaluate(t, env) for t in sides))
        targets = [ident+'.R'+str(i) for i in range(1, len(pairs)+1)]
        assert actual == pairs and all(a == b for a, b in pairs), (ident, actual, pairs)
        assert ledger_by_id[ident]['route'] == 'count' and ledger_by_id[ident]['targets'] == targets
    yield ('all 66 D65 relations agree with independent integer arithmetic on unchanged arguments',
           sum(len(row[3]) for row in records) == 66 and 'gate-unsupported:' not in body)
    words = ['judge', 'count', '', str(premise), '--predicate', 'LevelQuestion',
             '--encoding', 'UnaryArithmeticEncoding', '--sigma', 'BenchLight']
    commands = [[str(root/'bin/gate-judge')], ['node', str(root/'bin/judge-cli.js')]]
    def both(path):
        words[2] = str(path)
        a, b = [subprocess.run(cmd+words, capture_output=True, text=True) for cmd in commands]
        return a, (a.returncode, a.stdout, a.stderr) == (b.returncode, b.stdout, b.stderr)
    claim_ids = {name.split('.')[0] for row in ledger for name in [row['id'], *row['targets']]}
    for ident, kind, args, pairs in records:
        # Read just this ID, with the very same definitions, so an omitted field
        # cannot hide behind the total for somebody else's checked relations.
        isolated = re.sub(r'^public typealias (\w+) = [^\n]+\n',
                          lambda m: '' if m[1] in claim_ids and m[1] != ident else m[0], body, flags=re.M)
        path = Path(scratch)/(ident+'.swift')
        path.write_text(isolated)
        answer, same = both(path)
        yield (ident+' checks all '+str(len(pairs))+' relations through native and wasm',
               same and answer.returncode == 0 and f'{len(pairs)} source-bound readings checked' in answer.stdout)
        indices = {'Grey': [3, 4, 5, 6], 'GreyFloor': [0, 3, 4], 'TowardBlue': [2], 'TowardWarm': [2]}[kind]
        for i, index in enumerate(indices, 1):
            wrong = list(args)
            wrong[index] = ('Plus', (('Unit', ()), wrong[index]))
            changed = re.sub(r'^public typealias '+ident+r' = [^\n]+$',
                             'public typealias '+ident+' = '+written((kind, tuple(wrong))), isolated, flags=re.M)
            path.write_text(changed)
            answer, same = both(path)
            left, right = expected(kind, [evaluate(a) for a in wrong])[i-1]
            needle = f"'{ident}.R{i}' count Left = {left}, but Answer = {right}"
            yield (ident+'.R'+str(i)+' refuses a changed number at its own address through both carriers',
                   changed != isolated and same and answer.returncode == 1 and needle in answer.stdout)

    # A field refusal belongs to the original ID. Put that declaration in a
    # different file from the definitions so a fallback to the first file is
    # observably wrong, through the shipped CLI and its compiled-in court.
    world = Path(scratch)/'d65-address'
    world.mkdir()
    ident = 'PaperGrey_lit'
    line = re.search(r'^public typealias '+ident+r' = [^\n]+$', body, re.M).group()
    kind, args = defs[ident][1]
    changed_args = list(args)
    changed_args[4] = ('Plus', (('Unit', ()), changed_args[4]))
    changed_line = 'public typealias '+ident+' = '+written((kind, tuple(changed_args)))
    (world/'palette.swift').write_text(body.replace(line+'\n', ''))
    (world/'claim.swift').write_text(changed_line+'\n')
    gate = str(root/'gate')
    for name in ('palette.swift', 'claim.swift'):
        subprocess.run([gate, 'mine', name, '--role', 'forms'], cwd=world,
                       capture_output=True, text=True, check=True)
    refused = subprocess.run([gate, 'status', '--json'], cwd=world, capture_output=True, text=True)
    answer = json.loads(refused.stdout)
    rows = [r for r in answer.get('refusals', []) if 'PaperGrey_lit.R2' in r.get('claim', '')]
    yield ('a D65 field refusal names the file containing its original claim across file boundaries',
           refused.returncode == 1 and rows and all(r['address'].split(':')[0] == 'claim.swift' for r in rows))
