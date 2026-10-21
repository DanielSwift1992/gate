"""The announced address is listening; an occupied port announces no readiness."""
from pathlib import Path
import json, socket, subprocess, sys, queue, threading, urllib.request
cli,world=sys.argv[1:]
def start(port,*flags):
 return subprocess.Popen([cli,'serve',world,str(port),'--no-open',*flags],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
def line(p):
 q=queue.Queue();threading.Thread(target=lambda:q.put(p.stdout.readline()),daemon=True).start()
 return q.get(timeout=15)
with socket.socket() as occupied:
 occupied.bind(('127.0.0.1',0));occupied.listen(1);port=occupied.getsockname()[1]
 p=start(port);out,err=p.communicate(timeout=15)
 assert p.returncode and 'Ready:' not in out and 'already spoken for' in err,(out,err)
for flags in [(),('--json',)]:
 with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
 p=start(port,*flags)
 try:
  first=json.loads(line(p));assert first['url']==f'http://127.0.0.1:{port}'
  if not flags:assert line(p).strip()=='Ready: '+first['url']
  with urllib.request.urlopen(first['url']+'/version',timeout=15) as r:assert r.status==200
 finally:
  p.terminate();out,err=p.communicate(timeout=15)
 assert 'Ready:' not in out,'JSON mode remains a single route record'
print('SERVE READY GREEN: immediately reachable address, occupied-port refusal, JSON preserved')
