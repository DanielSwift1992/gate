"""The physical linker-input transport, not a reader of Swift.

Response v1: UTF-8, one canonical double-quoted absolute .o path per LF;
only quote and backslash escapes, no control characters, options or @nesting.
The recipe passes these very bytes to swiftc. Its digest is held across linking.

Trace v1 (ld -t / --trace): PATH (Darwin ld and ELF), ARCHIVE(MEMBER)
(gold/lld), or (ARCHIVE)MEMBER (GNU ld). Paths are not shell-quoted.
The two captured streams have this same grammar: gold writes its banner
and input paths to stderr, while other linkers can write inputs to stdout.
Known GNU ld/gold and LLD -v banners are metadata, not input paths. Every
other nonempty line must identify an existing file/archive or refuse at its
line. A trace is not required to repeat the response's object list. Both
sources are retained conservatively; extra directory contents are not inputs.
"""
import argparse
import getpass
import json
from pathlib import Path
import re
import sys

from publication_origin import Refusal, encode, sha

FORMAT = 'linker-input-transport/1'
ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC = ROOT/'bin/.publication-origin/last-link-diagnostic.json'
VERSION = re.compile(r'^(GNU (?:ld|gold) \([^\r\n]*\) [0-9][^\r\n]*|(?:Ubuntu )?LLD [0-9][^\r\n]*)$')


def quoted(path):
    value = str(path)
    if any(ord(c) < 32 for c in value):
        raise Refusal('origin:linker.rsp:1: control characters are outside the response path grammar')
    return json.dumps(value, ensure_ascii=False)


def write_response(objects, output):
    paths = sorted(p.resolve() for p in objects.glob('*.o') if p.is_file())
    if not paths:
        raise Refusal('origin:linker.rsp:1: no object inputs to pass to the driver')
    raw = ('\n'.join(quoted(p) for p in paths)+'\n').encode()
    output.write_bytes(raw)
    return sha(raw)


def response_inputs(response, expected_sha):
    if response is None or not isinstance(expected_sha, str) or re.fullmatch('[0-9a-f]{64}', expected_sha) is None:
        raise Refusal('origin:linker.rsp:1: declared response and its pre-link digest are required')
    try: raw = response.read_bytes(); text = raw.decode('utf-8')
    except (OSError, UnicodeError):
        raise Refusal('origin:linker.rsp:1: response is unavailable or not UTF-8') from None
    if sha(raw) != expected_sha:
        raise Refusal('origin:linker.rsp:1: response changed after its arguments were declared')
    if not text.endswith('\n'):
        raise Refusal('origin:linker.rsp:1: response must end with LF')
    result = {}; rows = []
    for number, line in enumerate(text[:-1].split('\n'), 1):
        address = 'origin:linker.rsp:'+str(number)+': '
        try:
            value = json.loads(line)
            if not isinstance(value, str) or quoted(value) != line: raise ValueError()
            path = Path(value)
            if not path.is_absolute() or path.suffix != '.o' or not path.is_file(): raise ValueError()
        except (ValueError, OSError):
            raise Refusal(address+'expected one canonical quoted existing absolute object path') from None
        path = path.resolve()
        if path in result:
            raise Refusal(address+'object is repeated from origin:linker.rsp:'+str(result[path]))
        result[path] = number; rows.append((path, number))
    if not rows:
        raise Refusal('origin:linker.rsp:1: empty response')
    return rows


def trace_inputs(trace, channel='trace', allow_empty=False):
    if channel not in ('trace', 'stderr'):
        raise Refusal('origin:linker:1: undeclared trace channel')
    prefix = 'origin:linker.'+channel+':'
    try: raw = trace.read_bytes(); lines = raw.decode('utf-8').split('\n')
    except (OSError, UnicodeError):
        raise Refusal(prefix+'1: trace is unavailable or not UTF-8') from None
    rows = []; versions = []
    for number, line in enumerate(lines, 1):
        line = line.removesuffix('\r')
        if not line: continue
        address = prefix+str(number)+': '
        path = Path(line); member = None; form = 'path'
        if not path.is_file():
            if VERSION.fullmatch(line):
                versions.append((number, line)); continue
            candidates = []
            if line.endswith(')') and '(' in line:
                name, member_name = line.rsplit('(', 1)
                candidates.append((Path(name), member_name[:-1], 'archive(member)'))
            if line.startswith('(') and ')' in line:
                name, member_name = line[1:].split(')', 1)
                candidates.append((Path(name), member_name, '(archive)member'))
            found = []
            for candidate, member_name, spelling in candidates:
                if member_name and candidate.is_file():
                    try:
                        with candidate.open('rb') as stream: magic = stream.read(8)
                    except OSError:
                        raise Refusal(address+'archive input is unreadable') from None
                    if magic in (b'!<arch>\n', b'!<thin>\n'):
                        found.append((candidate, member_name, spelling))
            if len(found) != 1:
                raise Refusal(address+'line is outside the declared ld/gold/lld input grammar')
            path, member, form = found[0]
        rows.append(dict(path=path.resolve(), line=number, member=member, form=form, channel=channel))
    if not rows and not allow_empty:
        raise Refusal(prefix+'1: no traced inputs; no roster inferred')
    return rows, versions, sha(raw)


def mask(text):
    # Presentation only. Unlike an admission rule, this never exempts bytes.
    component = r'[^/\\\s"\']+'
    text = re.sub(r'/(Users|home)/'+component, r'/\1/<redacted>', text)
    text = re.sub(r'/(?:private/)?var/folders/'+component+'/'+component,
                  '/var/folders/<redacted>/<redacted>', text)
    text = re.sub(r'([A-Za-z]:[\\/](?:Users|Documents and Settings)[\\/])'+component,
                  lambda m: m[1]+'<redacted>', text, flags=re.I)
    try: user = getpass.getuser()
    except (OSError, KeyError): user = ''
    if user: text = re.sub(re.escape(user), '<redacted>', text, flags=re.I)
    return re.sub(r'[^/\\\s@"\']+@', '<redacted>@', text)


def save_diagnostic(trace, response, stderr, reason, output=DIAGNOSTIC):
    value = dict(format=FORMAT, reason=mask(reason), sources=[])
    for label, path, limit in [('linker.trace', trace, 6), ('linker.rsp', response, 6), ('linker.stderr', stderr, 3)]:
        rows = []
        try:
            with path.open('r', encoding='utf-8', errors='replace') as stream:
                for number in range(1, limit+1):
                    line = stream.readline(4096)
                    if not line: break
                    if label == 'linker.rsp':
                        try:
                            decoded = json.loads(line)
                            if isinstance(decoded, str): line = json.dumps(mask(decoded), ensure_ascii=False)+'\n'
                        except ValueError: pass
                    rows.append(dict(line=number, text=mask(line.rstrip('\r\n'))[:160]))
                    if not line.endswith('\n'): break
        except OSError:
            rows.append(dict(line=1, text='not captured'))
        value['sources'].append(dict(address='origin:'+label, rows=rows))
    output.parent.mkdir(parents=True, exist_ok=True); output.write_bytes(encode(value))
    return value


def report(value, annotation=False):
    lines = ['origin:linker:1: '+value['reason']]
    for source in value['sources']:
        lines += [source['address']+':'+str(row['line'])+': '+row['text'] for row in source['rows']]
    text = mask('\n'.join(lines))[:3500]
    if annotation:
        text = '::error title=addressed linker inputs::'+text.replace('%','%25').replace('\r','%0D').replace('\n','%0A')
    print(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('write'); p.add_argument('objects', type=Path); p.add_argument('output', type=Path)
    p = sub.add_parser('diagnose'); p.add_argument('objects', type=Path); p.add_argument('--reason', required=True)
    p = sub.add_parser('report')
    args = parser.parse_args()
    if args.command == 'write': print(write_response(args.objects, args.output))
    elif args.command == 'diagnose':
        report(save_diagnostic(args.objects/'linker.trace', args.objects/'link-inputs.rsp',
                               args.objects/'linker.stderr', args.reason))
    elif DIAGNOSTIC.is_file(): report(json.loads(DIAGNOSTIC.read_bytes()), annotation=True)
    else: print('origin:linker:1: no failed link invocation was captured')


if __name__ == '__main__':
    try: main()
    except Refusal as error: sys.exit(str(error))
