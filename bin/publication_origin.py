"""Build receipts bind delivered bytes; no linked byte gets a vendor waiver.

This is host provenance, not a proof of a compiler or a trusted-build service.
An unidentified linked contribution remains in the complete lexical domain.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
import subprocess

FORMAT = 'gate-publication-build/1'


class Refusal(ValueError):
    pass


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def prepare(root, recipe, compiler):
    files = {p.relative_to(root).as_posix(): sha(p.read_bytes())
             for p in sorted(root.rglob('*')) if p.is_file()}
    if not files:
        raise Refusal('origin:1: empty build inputs')
    compiler_path = shutil.which(compiler)
    if compiler_path is None:
        raise Refusal('origin:1: compiler executable is not identified')
    executable = Path(compiler_path).resolve()
    compiler_info = dict(version=subprocess.check_output([compiler, '--version'], text=True).strip(),
                         executable_sha256=sha(executable.read_bytes()))
    if compiler == 'swiftc':
        target = json.loads(subprocess.check_output([compiler, '-print-target-info']))
        resource = Path(target['paths']['runtimeResourcePath'])
        # Static archives are inputs too. Their hashes do NOT certify their
        # linked contributions as foreign: those still get the full scan.
        compiler_info['static_archives'] = {p.resolve().relative_to(resource.parent.parent.parent.resolve()).as_posix(): sha(p.read_bytes())
                                            for tree in (resource,resource.parent/'swift_static')
                                            for p in sorted(tree.rglob('*')) if p.is_file() and p.suffix in ('.a','.lib')}
        compiler_info['target'] = target['target']['triple']
        frontend = resource.parent.parent/'bin'/('swift-frontend.exe' if executable.suffix == '.exe' else 'swift-frontend')
        if not frontend.is_file():
            raise Refusal('origin:1: Swift frontend input is not identified')
        compiler_info['frontend_sha256'] = sha(frontend.read_bytes())
    elif compiler == 'rustc':
        actual = Path(subprocess.check_output(['rustup','which','rustc'],text=True).strip())
        compiler_info['executable_sha256'] = sha(actual.read_bytes())
        resource = Path(subprocess.check_output(['rustc','--print','sysroot'],text=True).strip())
        libraries = resource/'lib/rustlib/wasm32-unknown-unknown/lib'
        compiler_info['static_archives'] = {p.relative_to(resource).as_posix(): sha(p.read_bytes())
                                            for p in sorted(libraries.glob('*.rlib'))}
        if not compiler_info['static_archives']:
            raise Refusal('origin:1: Rust target standard library is not identified')
    return dict(format=FORMAT, inputs=files, recipe_sha256=sha(recipe.read_bytes()), compiler=compiler_info)


def unchanged(prepared, root, omitted=None):
    actual = {p.relative_to(root).as_posix(): sha(p.read_bytes())
              for p in sorted(root.rglob('*')) if p.is_file() and p != omitted}
    if actual != prepared['inputs']:
        raise Refusal('origin:byte 0: build inputs changed; no receipt issued')


def seal(prepared, raw, mappings, debug):
    result = dict(prepared)
    result.update(sha256=sha(raw), size=len(raw), prefix_mappings=mappings, debug_metadata=debug,
                  regions=[dict(offset=0, size=len(raw), origin='build-derived', lexical=True)],
                  boundary='Entire linked image; no foreign contributions exempted. Host build receipt, not compiler correctness.')
    verify(result, raw)
    return result


def verify(record, raw):
    if record.get('format') != FORMAT or record.get('sha256') != sha(raw) or record.get('size') != len(raw):
        raise Refusal('origin:byte 0: build receipt does not identify delivered bytes')
    import re
    hashes = list(record.get('inputs',{}).values()) + [record.get('recipe_sha256',''),record.get('compiler',{}).get('executable_sha256','')]
    if not hashes or any(not isinstance(h,str) or re.fullmatch('[0-9a-f]{64}',h) is None for h in hashes):
        raise Refusal('origin:byte 0: malformed declared input digest')
    if not record.get('inputs') or not record.get('compiler') or not record.get('prefix_mappings'):
        raise Refusal('origin:byte 0: incomplete declared build inputs or mappings')
    if record.get('debug_metadata') not in ('strip-S', 'strip-debug', 'external-PDB', 'rust-strip-debuginfo'):
        raise Refusal('origin:byte 0: debug metadata removal is not declared')
    # The conservative partition has no gaps, overlaps, or foreign exclusions.
    # A future identity certificate may split it; a region label alone cannot.
    expected = [dict(offset=0, size=len(raw), origin='build-derived', lexical=True)]
    if record.get('regions') != expected:
        raise Refusal('origin:byte 0: unproved region partition or foreign exemption')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare'); p.add_argument('root', type=Path); p.add_argument('recipe', type=Path); p.add_argument('output', type=Path); p.add_argument('--compiler', default='swiftc')
    p = sub.add_parser('seal'); p.add_argument('prepared', type=Path); p.add_argument('binary', type=Path); p.add_argument('--mapping', action='append', required=True); p.add_argument('--debug', required=True); p.add_argument('--inputs-root', type=Path, required=True); p.add_argument('--objects', type=Path); p.add_argument('--link-trace', type=Path)
    args = parser.parse_args()
    if args.command == 'prepare':
        args.output.write_bytes(encode(prepare(args.root, args.recipe, args.compiler)))
    else:
        prepared = json.loads(args.prepared.read_bytes())
        unchanged(prepared,args.inputs_root,args.prepared)
        value = seal(prepared, args.binary.read_bytes(), args.mapping, args.debug)
        if args.objects is not None:
            import publication_identity as identity
            value['identity_inputs'] = identity.capture(prepared, args.objects, args.inputs_root/'outputs.json', args.link_trace)
        Path(str(args.binary) + '.origin.json').write_bytes(encode(value))


if __name__ == '__main__':
    main()
