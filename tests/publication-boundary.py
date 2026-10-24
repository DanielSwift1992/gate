#!/usr/bin/env python3
"""Refuse machine identity in the declared, finite publication byte class."""
import argparse
import base64
from bisect import bisect_left
import getpass
import json
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
import publication_origin as origin

ROOT = Path(__file__).resolve().parents[1]
CONFIG = 'tests/publication-boundary.json'


def load():
    policy = json.loads((ROOT / CONFIG).read_bytes())
    if policy.get('format') != 'publication-boundary/3':
        raise ValueError(CONFIG + ':1: unsupported publication policy')
    return policy


def public_label(policy, label, builder_names):
    services = {name.casefold() for name in policy['service_builder_accounts']}
    for name in builder_names:
        if name and name.casefold() not in services:
            label = re.sub(re.escape(name),'<redacted>',label,flags=re.I)
    # Mask a mailbox local part in an address as well as in a sample. This
    # changes only presentation, never the declared finding class.
    return re.sub(r'[^/\\\s@]+@','<redacted>@',label)


def publication_content(policy, name, content, builder_names=(), check_emails=True):
    subject_name = name
    name = public_label(policy,name,builder_names)
    # Root boundaries distinguish filesystem roots from URL path components.
    # Unicode word characters include account letters and numbers; dots and
    # hyphens retain their previous spelling. Invalid bytes are not letters.
    component = r'[\w.-]+'
    root_boundary = r'(?<![A-Za-z0-9_-])'
    homes = re.compile(root_boundary + r'(?:/(?:Users|home)/' + component
                       + r'|/' + 'root' + r'/(?=[\w.-])'
                       + r'|(?:/private)?/var/folders/' + component + r'/' + component
                       + r'|[A-Za-z]:[\\/](?i:Users|Documents and Settings)[\\/]' + component
                       + r'|\\\\[^\\/\s]+[\\/](?i:Users)[\\/]' + component + r')')
    emails = re.compile(rb'(?<![A-Za-z0-9_.+%-])[A-Za-z0-9_.+%-]{1,64}@'
                        rb'[A-Za-z0-9-]{1,63}(?:\.[A-Za-z0-9-]{1,63}){0,8}'
                        rb'(?![A-Za-z0-9-])(?!\.[A-Za-z0-9-])')
    service_accounts = {value.casefold() for value in policy['service_builder_accounts']}
    names = [re.compile(rb'(?<![A-Za-z0-9])' + re.escape(value.encode())
                        + rb'(?![A-Za-z0-9])', re.I) for value in builder_names
             if value and value.casefold() not in service_accounts]
    findings = []

    def private_name_mask(value):
        raw = value.encode('utf-8')
        for value in builder_names:
            if value and value.casefold() not in service_accounts:
                raw = re.sub(re.escape(value.encode()),b'<redacted>',raw,flags=re.I)
        return raw.decode('utf-8')

    def path_sample(value):
        # Only the recognized root and masked account components travel.
        # Neither the account nor a suffix from a private tree is echoed.
        if value.startswith('\\\\'):
            return r'\\<redacted>\Users\<redacted>'
        if '/var/folders/' in value:
            return value.split('/var/folders/', 1)[0] + '/var/folders/<redacted>/<redacted>'
        if value.startswith(('/Users/', '/home/', '/root/')):
            return '/' + value.split('/')[1] + '/<redacted>'
        # A drive-qualified Windows account home (including its legacy root).
        return re.sub(component + r'$', '<redacted>', value)

    def email_spans(raw):
        # P1: boundaries are declared by the byte class, never chosen around a
        # match. A binary's instructions are not treated as arbitrary text.
        spans = []; start = 0
        for part in raw.split(b'\0'):
            try:
                text = part.decode('utf-8')
            except UnicodeDecodeError:
                text = ''
            if text and all(c.isprintable() or c in '\t\r\n' for c in text):
                spans.append((start, start + len(part)))
            start += len(part) + 1
        return spans

    def scan(raw, label, offsets, valid):
        text = raw.decode('utf-8', errors='surrogateescape')
        for match in homes.finditer(text):
            # Shared is macOS's shared directory, not an account home.
            if match[0] == '/Users/Shared':
                continue
            start = len(text[:match.start()].encode('utf-8', errors='surrogateescape'))
            end = start + len(match[0].encode('utf-8', errors='surrogateescape'))
            if valid(start, end):
                sample = json.dumps(path_sample(match[0]))
                findings.append(f'{label}:byte {offsets[start]}: publication boundary refused: absolute home or account-temporary path; sample={sample}')
        for pattern in names:
            for match in pattern.finditer(raw):
                if valid(match.start(), match.end()):
                    findings.append(f'{label}:byte {offsets[match.start()]}: publication boundary refused: local builder name; sample="<redacted>"')
        text_spans = email_spans(raw) if check_emails else ()
        for match in emails.finditer(raw) if check_emails else ():
            if not any(start <= match.start() and match.end() <= end for start,end in text_spans):
                continue
            account, domain = match[0].decode('ascii').rsplit('@', 1)
            # SCP-style repository addresses have a declared service user and
            # a nonempty path. A bare mailbox or another user is still email.
            if account in policy['scp_repository_users'] and re.match(rb':[^\s<>"\']+', raw[match.end():]):
                continue
            domain = domain.lower()
            if domain in policy['example_email_domains'] or any(domain.endswith(suffix) for suffix in policy['example_email_suffixes']):
                continue
            # A DNS address or localhost-style mailbox, not repo@SHA pins.
            if not re.search(r'\.[A-Za-z]{2,63}$', domain):
                continue
            if valid(match.start(), match.end()):
                sample = json.dumps(private_name_mask(domain))
                findings.append(f'{label}:byte {offsets[match.start()]}: publication boundary refused: email address; domain={sample}')

    def escaped(raw, label, offsets, valid):
        scan(raw, label, offsets, valid)
        if b'\\' not in raw:
            return
        matches = list(re.finditer(rb'\\[\\/]', raw))
        if not matches:
            return
        pieces = []; previous = 0; positions = []
        for index, match in enumerate(matches):
            pieces += [raw[previous:match.start()], match[0][1:]]
            positions.append(match.start() - index)
            previous = match.end()
        pieces.append(raw[previous:])
        class MappedOffsets:
            def __getitem__(self, index):
                return offsets[index + bisect_left(positions, index)]
        scan(b''.join(pieces), label + ' [slash-unescaped]', MappedOffsets(),
             lambda start,end: valid(start + bisect_left(positions, start), end + bisect_left(positions, end)))


    def representations(raw, label):
        escaped(raw, label, range(len(raw)), lambda start,end: True)
        for alignment in (0, 1):
            for little in (True, False):
                encoding = 'utf-16le' if little else 'utf-16be'
                end = alignment + (max(0, len(raw)-alignment)//2)*2
                # Decode actual code units, not just their ASCII byte. This
                # keeps Unicode account names, including surrogate pairs.
                projected = raw[alignment:end].decode(encoding, errors='surrogatepass').encode('utf-8', errors='surrogatepass')
                class CodeUnitOffsets:
                    def __getitem__(self, index):
                        prefix = projected[:index].decode('utf-8', errors='surrogatepass')
                        return alignment + len(prefix.encode(encoding, errors='surrogatepass'))
                escaped(projected, label + (' [UTF-16LE]' if little else ' [UTF-16BE]'),
                        CodeUnitOffsets(), lambda start,end: True)

    representations(content, name)
    carrier = re.compile(rb'\b' + re.escape(policy['base64_binding'].encode()) + rb'\s*=\s*"([A-Za-z0-9+/=]*)"')
    matches = list(carrier.finditer(content))
    if subject_name == policy['base64_file'] and len(matches) != 1:
        findings.append(name + ':byte 0: publication boundary refused: missing or ambiguous base64 carrier')
    for match in matches:
        try:
            decoded = base64.b64decode(match[1], validate=True)
            if not decoded:
                raise ValueError('empty carrier')
        except (ValueError, base64.binascii.Error):
            findings.append(f'{name}:byte {match.start(1)}: publication boundary refused: invalid base64 carrier')
            continue
        representations(decoded, f'{name}:byte {match.start(1)} [base64 decoded]')
    return sorted(set(findings))


def delivered_origin(path, label, raw):
    # Exact executable formats, not a filename or a username heuristic.
    native = raw[:4] in (b'\x7fELF', b'\xcf\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xce\xfa\xed\xfe', b'\xfe\xed\xfa\xce') or raw[:2] == b'MZ'
    wasm = raw[:4] == b'\0asm'
    carrier = re.search(rb'VI_COURT_WASM_BASE64\s*=\s*"([A-Za-z0-9+/=]+)"',raw)
    if not (native or wasm or carrier):
        return []
    try:
        if native:
            origin.verify(json.loads(Path(str(path)+'.origin.json').read_bytes()),raw)
        else:
            if path.resolve() in ((ROOT/'bin/court-wasm/node/vi_court_bg.wasm').resolve(), (ROOT/'bin/court-wasm/web/vi_court_bytes.js').resolve()):
                record_path = ROOT/'bin/court-wasm.build.json'
            else:
                record_path = path.parent/'court-wasm.build.json'
            if not record_path.is_file():
                raise ValueError('missing carried wasm build receipt')
            record = json.loads(record_path.read_bytes())
            if record.get('source_mode') != 'public-fetch':
                raise origin.Refusal('origin:byte 0: local source receipt is not a public build')
            if carrier:
                origin.verify(record['origin_web'],base64.b64decode(carrier[1],validate=True))
            elif path.name == 'vi_court_bg.wasm':
                origin.verify(record['origin_node'],raw)
            else:
                raise ValueError('wasm artifact is not bound to a declared output')
    except origin.Refusal as error:
        return [label+':byte 0: publication origin refused: '+str(error).split(': ',2)[-1]]
    except (KeyError,ValueError,OSError,TypeError,AttributeError) as error:
        # Exceptions can contain host paths. Only the subject's public address
        # leaves here; lexical samples are masked separately below.
        return [label+':byte 0: publication origin refused: missing, damaged or unproved build receipt ('+type(error).__name__+')']
    return []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact', action='append', default=[], type=Path)
    parser.add_argument('--publication-tree', action='append', default=[], type=Path)
    parser.add_argument('--repository', action='store_true', help='also check Git-tracked files (default with no explicit inputs)')
    arguments = parser.parse_args()
    policy = load(); inputs = []
    if arguments.repository or not (arguments.artifact or arguments.publication_tree):
        tracked = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '-z']).split(b'\0')
        inputs += [(ROOT / name.decode(), name.decode(), (), False) for name in tracked if name]
    for path in arguments.artifact:
        inputs.append((path, path.name, (getpass.getuser(),), True))
    for tree in arguments.publication_tree:
        if not tree.is_dir() or not any(tree.iterdir()):
            raise ValueError(tree.name + ':byte 0: publication boundary refused: missing or empty publication tree')
        inputs += [(path, tree.name + '/' + str(path.relative_to(tree)), (getpass.getuser(),), True) for path in sorted(tree.rglob('*')) if path.is_file() or path.is_symlink()]
    findings = []
    for path, label, builder_names, check_emails in inputs:
        if path.is_symlink() or not path.is_file():
            findings.append(label + ':byte 0: publication boundary refused: missing file or symbolic link')
            continue
        display_label = public_label(policy,label,builder_names)
        raw = path.read_bytes()
        executable = raw[:4] in (b'\x7fELF',b'\0asm',b'\xcf\xfa\xed\xfe',b'\xfe\xed\xfa\xcf',b'\xce\xfa\xed\xfe',b'\xfe\xed\xfa\xce') or raw[:2] == b'MZ'
        if check_emails or executable:
            origin_findings = delivered_origin(path,display_label,raw)
            findings += origin_findings
            if origin_findings:
                continue
        findings += publication_content(policy, display_label + ' [filename]', label.encode(), builder_names, check_emails=check_emails)
        findings += publication_content(policy, display_label, raw, builder_names, check_emails=check_emails or executable)
    if findings:
        print('\n'.join(sorted(set(findings))))
        return 1
    print('PUBLICATION BOUNDARY HOLDS: ' + str(len(inputs)) + ' files; declared path, local-name and email byte classes')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(CONFIG + ':1: publication boundary refused: ' + str(error), file=sys.stderr)
        sys.exit(2)
