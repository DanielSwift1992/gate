"""Physical identity of complete printable runs, never a spelling exemption.

The class is fixed before reading: maximal runs of bytes 0x20..0x7e.
Unsupported representations retain their lexical refusal. The host replays
supplier package authentication, archive membership, and absence in the exact
objects linked from this build. This is not compiler correctness.
"""
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import tempfile
import time
import urllib.request

from publication_origin import Refusal, sha, encode

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT/'bin/.publication-origin'
BOUNDARY = 'maximal ASCII printable byte runs [0x20,0x7e]; no minimum length'
KEY_SOURCE = 'https://www.swift.org/keys/all-keys.asc'
SIGNER = '52BB7E3DE28A71BE22EC05FFEF80A866B47A981F'


def capture(prepared, objects, output_map, link_trace, link_response, response_sha):
    """Retain passed objects and actual non-archive traced inputs.

    The recipe freezes the response before linking, then passes its exact
    bytes to swiftc. Trace may report selected inputs instead of repeating that
    list; it adds driver-supplied files. Retain both conservatively. A later
    directory side product is neither an argument nor a traced input.
    """
    declared = json.loads(output_map.read_bytes())
    sources={str((output_map.parent/p).resolve()) for p in prepared['inputs'] if p.endswith('.swift')}
    if set(declared)!=sources or sha(output_map.read_bytes()) != prepared['inputs'].get('outputs.json'):
        raise Refusal('origin:byte 0: compiler output map does not cover the declared Swift sources')
    if link_trace is None:
        raise Refusal('origin:linker.trace:1: actual linker input trace is required')
    target_info=json.loads(subprocess.check_output(['swiftc','-print-target-info']))
    toolchain=Path(target_info['paths']['runtimeResourcePath']).resolve().parent.parent.parent
    archives={(toolchain/p).resolve():h for p,h in prepared['compiler']['static_archives'].items()}
    if any(sha(p.read_bytes())!=h for p,h in archives.items()):
        raise Refusal('origin:byte 0: compiler archive inputs changed during linking')
    import linker_inputs as transport
    passed=transport.response_inputs(link_response,response_sha)
    entries,versions,trace_sha=transport.trace_inputs(link_trace)
    diagnostics=link_trace.with_name('linker.stderr')
    stderr=diagnostics.read_bytes() if diagnostics.is_file() else b''
    banners=[text for _,text in versions]
    banners += [line for line in stderr.decode('utf-8',errors='replace').split('\n') if transport.VERSION.fullmatch(line)]
    kinds={('gold' if v.startswith('GNU gold ') else 'gnu-ld' if v.startswith('GNU ld ') else 'lld') for v in banners}
    if len(kinds)>1:
        raise Refusal('origin:linker.trace:1: conflicting linker version declarations')
    actual={}
    for path,line in passed:
        try: path.relative_to(objects.resolve())
        except ValueError:
            raise Refusal('origin:linker.rsp:'+str(line)+': object is outside the declared output root') from None
        actual[path]=dict(source='response',line=line,trace_lines=[])
    def archive(path):
        with path.open('rb') as stream: return stream.read(8) in (b'!<arch>\n',b'!<thin>\n')
    for entry in entries:
        path=entry['path'];number=entry['line']
        if path in archives and archive(path):
            continue
        actual.setdefault(path,dict(source='trace',line=number,trace_lines=[]))['trace_lines'].append(number)
    digests=[]; roster=[]
    for path,address in actual.items():
        try: data=path.read_bytes()
        except OSError:
            raise Refusal('origin:linker.'+('rsp' if address['source']=='response' else 'trace')+':'+str(address['line'])+': linked input unavailable') from None
        digest=sha(data)
        dest=CACHE/'objects'/digest; dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists() and sha(dest.read_bytes())!=digest:
            raise Refusal('origin:byte 0: damaged retained linker input')
        dest.write_bytes(data)
        if digest not in digests: digests.append(digest)
        roster.append(dict(address,sha256=digest))
    version = re.search(r'\bSwift version ([0-9]+\.[0-9]+(?:\.[0-9]+)?)\b', prepared['compiler']['version'])
    try:
        os_release = dict(line.split('=',1) for line in Path('/etc/os-release').read_text().splitlines() if '=' in line)
    except OSError:
        os_release = {}
    target = prepared['compiler']['target']; arch = target.split('-')[0]
    result=dict(boundary=BOUNDARY,objects=digests,archive_hashes=prepared['compiler']['static_archives'],
                linker_trace_sha256=trace_sha,linker_response_sha256=response_sha,
                linker_stderr_sha256=sha(stderr),linker_kind=next(iter(kinds),'not-reported'),
                linker_grammar=transport.FORMAT,linker_version_lines=[n for n,_ in versions],linker_inputs=roster,
                retained_scope='all response objects and traced inputs except declared compiler archives; no post-link directory inference')
    if not version or os_release.get('ID','').strip('"') != 'ubuntu' or arch not in ('x86_64','aarch64') or 'VERSION_ID' not in os_release:
        return result
    os_version = os_release['VERSION_ID'].strip('"')
    platform = 'ubuntu'+os_version.replace('.','')+('-aarch64' if arch=='aarch64' else '')
    name = 'swift-'+version[1]+'-RELEASE-ubuntu'+os_version+('-aarch64' if arch=='aarch64' else '')
    url = 'https://download.swift.org/swift-'+version[1]+'-release/'+platform+'/swift-'+version[1]+'-RELEASE/'+name+'.tar.gz'
    return dict(result,package=url)


def segment(raw, start, end):
    if not 0 <= start < end <= len(raw) or any(b < 32 or b > 126 for b in raw[start:end]):
        return None
    a,b = start,end
    while a and 32 <= raw[a-1] <= 126: a -= 1
    while b < len(raw) and 32 <= raw[b] <= 126: b += 1
    return a,b


def members(data):
    """ar's byte framing, with GNU long names and BSD extended names."""
    if data[:8] != b'!<arch>\n':
        raise Refusal('origin:byte 0: supplier archive is not an ordinary ar archive')
    offset=8; names=b''; ordinal=0
    while offset < len(data):
        header=data[offset:offset+60]
        if len(header)!=60 or header[58:]!=b'`\n':
            raise Refusal('origin:byte 0: malformed supplier archive member')
        try: size=int(header[48:58]); name=header[:16].decode('ascii').strip()
        except (ValueError,UnicodeError): raise Refusal('origin:byte 0: malformed archive member header')
        begin=offset+60; end=begin+size
        if size<0 or end>len(data): raise Refusal('origin:byte 0: truncated archive member')
        if name=='//': names=data[begin:end]
        elif name not in ('/','/SYM64/'):
            if name.startswith('#1/'):
                try: n=int(name[3:]); name=data[begin:begin+n].decode('utf-8').rstrip('\0')
                except (ValueError,UnicodeError): raise Refusal('origin:byte 0: invalid BSD archive name')
                if n<0 or n>size: raise Refusal('origin:byte 0: invalid BSD archive name size')
                begin+=n
            elif name.startswith('/'):
                try:
                    n=int(name[1:])
                    if not 0<=n<len(names): raise ValueError('name offset')
                    stop=names.index(b'/\n',n); name=names[n:stop].decode('utf-8')
                except (ValueError,UnicodeError): raise Refusal('origin:byte 0: invalid GNU archive name')
            else: name=name.removesuffix('/')
            if not name.startswith('__.SYMDEF'):
                yield dict(member=name,ordinal=ordinal,archive_offset=begin), data[begin:end]
        ordinal+=1; offset=end+(size%2)
    if offset!=len(data): raise Refusal('origin:byte 0: malformed archive padding')


def download(url, destination, deadline):
    try:
        with urllib.request.urlopen(url,timeout=min(30,max(1,deadline-time.monotonic()))) as response, destination.open('wb') as output:
            headers=dict(response.headers)
            while data:=response.read(2**20):
                if time.monotonic()>deadline: raise TimeoutError('supplier delivery deadline')
                output.write(data)
        return headers
    except Exception:
        destination.unlink(missing_ok=True)
        raise Refusal('origin:byte 0: supplier delivery unavailable; static image cannot be published') from None


def supplier_checksum(url, deadline):
    # A cache entry cannot vouch for its own checksum. Read the declared
    # supplier endpoint again; PGP authenticates the corresponding bytes.
    try:
        request=urllib.request.Request(url,method='HEAD')
        with urllib.request.urlopen(request,timeout=min(30,max(1,deadline-time.monotonic()))) as response:
            etag=response.headers.get('ETag','').strip('"').lower()
    except Exception:
        raise Refusal('origin:byte 0: supplier checksum source unavailable; static image cannot be published') from None
    if re.fullmatch('[0-9a-f]{32}',etag) is None:
        raise Refusal('origin:byte 0: supplier publishes no usable package checksum; static image cannot be published')
    return etag


def authenticated_package(url, cache=CACHE):
    # This declares the supplier input, not an exception for its spellings.
    if re.fullmatch(r'https://download\.swift\.org/swift-[0-9.]+-release/ubuntu[0-9]+(?:-aarch64)?/swift-[0-9.]+-RELEASE/swift-[0-9.]+-RELEASE-ubuntu[0-9.]+(?:-aarch64)?\.tar\.gz',url) is None:
        raise Refusal('origin:byte 0: supplier package is not declared')
    deadline=time.monotonic()+110
    published=supplier_checksum(url,deadline)
    folder=cache/'supplier'/sha(url.encode()); folder.mkdir(parents=True,exist_ok=True)
    package=folder/'toolchain.tar.gz'; metadata=folder/'download.json'
    if not package.exists() or not metadata.exists():
        download(url,folder/'download.tmp',deadline)
        (folder/'download.tmp').replace(package)
        metadata.write_bytes(encode(dict(url=url,etag=published)))
    meta=json.loads(metadata.read_bytes()); sha256=hashlib.sha256(); md5=hashlib.md5()
    with package.open('rb') as stream:
        while data:=stream.read(2**20): sha256.update(data); md5.update(data)
    if meta.get('url')!=url or meta.get('etag')!=published or md5.hexdigest()!=published:
        raise Refusal('origin:byte 0: supplier package does not equal its published HTTP ETag checksum')
    for filename,source in [('signature',url+'.sig'),('keys',KEY_SOURCE)]:
        if not (folder/filename).exists():
            download(source,folder/(filename+'.tmp'),deadline)
            data=(folder/(filename+'.tmp')).read_bytes()
            if data.startswith(b'\x1f\x8b') and filename=='keys': data=gzip.decompress(data)
            (folder/filename).write_bytes(data); (folder/(filename+'.tmp')).unlink()
    # An isolated keyring; exact fingerprint is anchored in Swift's published
    # active-key declaration, not in a UID or toolchain name.
    with tempfile.TemporaryDirectory(prefix='origin-gpg-') as temporary:
        home=Path(temporary);home.chmod(0o700)
        imported=subprocess.run(['gpg','--batch','--homedir',str(home),'--import',str(folder/'keys')],capture_output=True,timeout=max(1,deadline-time.monotonic()))
        checked=subprocess.run(['gpg','--batch','--homedir',str(home),'--status-fd','1','--verify',str(folder/'signature'),str(package)],capture_output=True,timeout=max(1,deadline-time.monotonic()))
    status=checked.stdout.decode('utf-8',errors='replace')
    valid=[x.split() for x in status.splitlines() if x.startswith('[GNUPG:] VALIDSIG ')]
    if imported.returncode or checked.returncode or len(valid)!=1 or valid[0][2]!=SIGNER:
        raise Refusal('origin:byte 0: supplier signature not established; static image cannot be published')
    return package,dict(package=url,sha256=sha256.hexdigest(),checksum=dict(algorithm='md5',value=md5.hexdigest(),source=url,field='HTTP ETag'),signature=dict(source=url+'.sig',sha256=sha((folder/'signature').read_bytes()),fingerprint=SIGNER,keys_source=KEY_SOURCE))


def attest(raw, inputs, intervals, cache=CACHE, authenticate=authenticated_package, existing=None):
    if inputs.get('boundary')!=BOUNDARY or not inputs.get('objects') or not inputs.get('archive_hashes'):
        raise Refusal('origin:byte 0: no complete identity inputs')
    stored=[] if existing is None else existing.get('certificates',[])
    if existing is not None and (existing.get('boundary')!=BOUNDARY or existing.get('objects')!=inputs['objects'] or not isinstance(stored,list)):
        raise Refusal('origin:byte 0: stored identity certificate has different inputs')
    runs={}
    for c in stored:
        a,b=c['offset'],c['offset']+c['size']
        if segment(raw,a,b)!=(a,b) or sha(raw[a:b])!=c['sha256']:
            raise Refusal('origin:byte 0: stored identity run is not maximal or changed')
        runs[a,b]=raw[a:b]
    for start,end in intervals:
        bounds=segment(raw,start,end)
        if bounds is None: continue  # The lexical refusal remains.
        runs[bounds]=raw[bounds[0]:bounds[1]]
    # Even a byte-identical vendor run cannot certify an ambiguous run that
    # occurs anywhere in retained linker inputs (not only at their boundaries).
    ambiguous=set()
    for digest in inputs['objects']:
        if not isinstance(digest,str) or re.fullmatch('[0-9a-f]{64}',digest) is None:
            raise Refusal('origin:byte 0: malformed build object digest')
        data=(cache/'objects'/digest).read_bytes()
        if sha(data)!=digest: raise Refusal('origin:byte 0: retained build object changed')
        ambiguous.update(bounds for bounds,text in runs.items() if text in data)
    needed={bounds:text for bounds,text in runs.items() if bounds not in ambiguous}
    if ambiguous.intersection((c['offset'],c['offset']+c['size']) for c in stored):
        raise Refusal('origin:byte 0: stored foreign run is also present in our build')
    if not needed: return dict(boundary=BOUNDARY,certificates=[])
    if not inputs.get('package'):
        raise Refusal('origin:byte 0: supplier package is not declared; no foreign-byte identity established')
    package,authentication=authenticate(inputs['package'],cache)
    if existing is not None and existing.get('supplier')!=authentication:
        raise Refusal('origin:byte 0: stored supplier authentication does not replay')
    archives=inputs['archive_hashes']; found={}; seen=set(); replayed=set()
    with tarfile.open(package,'r|gz') as stream:
        for item in stream:
            if not item.isfile(): continue
            path=PurePosixPath(item.name)
            if '..' in path.parts or path.is_absolute(): raise Refusal('origin:byte 0: unsafe supplier package member')
            relative=PurePosixPath(*path.parts[1:]).as_posix()
            if relative not in archives: continue
            if relative in seen: raise Refusal('origin:byte 0: repeated supplier archive path')
            seen.add(relative); data=stream.extractfile(item).read()
            if sha(data)!=archives[relative]: raise Refusal('origin:byte 0: installed archive differs from supplier package')
            for address,member in members(data):
                for index,c in enumerate(stored):
                    if c['archive']!=relative: continue
                    position=c['member_offset']; text=raw[c['offset']:c['offset']+c['size']]
                    if (all(c.get(k)==v for k,v in address.items()) and c['archive_sha256']==archives[relative]
                            and isinstance(position,int) and position>=0 and member[position:position+len(text)]==text):
                        replayed.add(index)
                for bounds,text in needed.items():
                    offset=member.find(text)
                    if offset>=0 and bounds not in found:
                        found[bounds]=dict(offset=bounds[0],size=bounds[1]-bounds[0],sha256=sha(text),archive=relative,archive_sha256=archives[relative],**address,member_offset=offset)
    if len(replayed)!=len(stored): raise Refusal('origin:byte 0: stored archive member identity does not replay')
    if seen!=set(archives): raise Refusal('origin:byte 0: supplier package does not cover declared archive inputs')
    return dict(boundary=BOUNDARY,supplier=authentication,objects=inputs['objects'],certificates=[found[b] for b in sorted(found)],occurrences=[dict(offset=a,size=b-a,segment=next(k[0] for k in found if k[0]<=a<b<=k[1])) for a,b in sorted(set(intervals)) if any(k[0]<=a<b<=k[1] for k in found)])


def covered(proof, start, end):
    return any(c['offset']<=start<end<=c['offset']+c['size'] for c in proof['certificates'])
