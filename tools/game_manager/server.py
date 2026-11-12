"""Loopback-only source browser and atomic management notes store (stdlib)."""
import argparse, json, mimetypes, os, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
try:
    from .catalog import ROOT, BOOK, PLAN, generate
except ImportError:
    from catalog import ROOT, BOOK, PLAN, generate
APP = Path(__file__).resolve().parent
STATE = APP/'local-state.json'
LOCK = threading.Lock()
STATUSES={'todo','in_progress','review','done','deferred'}
PRIORITIES={'low','normal','high','urgent'}

def load_state(path=STATE):
    if not path.exists(): return {'revision':0,'records':{}}
    value=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value,dict) or not isinstance(value.get('revision'),int) or not isinstance(value.get('records'),dict): raise ValueError('Invalid management store')
    return value

def update_state(payload, valid_ids, path=STATE):
    if not isinstance(payload,dict) or set(payload)!={'revision','id','changes'}: raise ValueError('Expected revision, id, changes')
    if type(payload['revision']) is not int or payload['revision']<0 or not isinstance(payload['id'],str) or payload['id'] not in valid_ids: raise ValueError('Invalid revision or ID')
    changes=payload['changes']
    if not isinstance(changes,dict) or not changes or set(changes)-{'status','priority','notes'}: raise ValueError('Invalid fields')
    for key,value in changes.items():
        if not isinstance(value,str): raise ValueError('Fields must be strings')
        if key=='status' and value not in STATUSES: raise ValueError('Invalid status')
        if key=='priority' and value not in PRIORITIES: raise ValueError('Invalid priority')
        if key=='notes' and len(value)>12000: raise ValueError('Notes limit is 12000 characters')
    with LOCK:
        current=load_state(path)
        if payload['revision']!=current['revision']: return 409,current
        record=current['records'].setdefault(payload['id'],{})
        record.update(changes);current['revision']+=1
        path.parent.mkdir(parents=True,exist_ok=True)
        temp=path.with_suffix('.tmp')
        with temp.open('w',encoding='utf-8') as f:
            json.dump(current,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
        os.replace(temp,path)
        return 200,current

def permitted_file(raw, allowed):
    value=unquote(raw)
    if '\\' in value or ':' in value or '\x00' in value or value.startswith('/') or any(x in ('..','.git','.env') for x in value.split('/')): return None
    p=(ROOT/value).resolve()
    if not p.is_relative_to(ROOT.resolve()) or not p.is_file(): return None
    if value not in allowed and not (value.startswith(BOOK+'/') and p.suffix.lower() in {'.html','.css','.js','.json','.png','.svg','.webp','.jpg','.jpeg','.wav','.mp4','.glb'}): return None
    if any(x.lower() in ('appdata','user','users','saves','save','.git') for x in p.relative_to(ROOT).parts): return None
    return p

def trusted_request(host, origin, port):
    hosts={'127.0.0.1:'+str(port),'localhost:'+str(port)}
    return host in hosts and (origin is None or origin in {'http://'+h for h in hosts})

class Handler(BaseHTTPRequestHandler):
    def send_json(self,status,value):
        data=json.dumps(value,ensure_ascii=False).encode('utf-8');self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if not trusted_request(self.headers.get('Host'),None,self.server.server_port): return self.send_json(403,{'error':'Untrusted Host'})
        route=urlsplit(self.path).path
        if route=='/api/catalog': return self.send_json(200,self.server.catalog)
        if route=='/api/management': return self.send_json(200,load_state())
        if route.startswith('/files/'):
            p=permitted_file(route[len('/files/'):],self.server.allowed)
        else:
            name=unquote(route.lstrip('/') or 'index.html');p=(APP/name).resolve()
            if not p.is_relative_to(APP) or p.name in {'local-state.json','local-state.tmp'} or p.suffix not in {'.html','.css','.js','.svg','.png'} or not p.is_file(): p=None
        if p is None: return self.send_json(404,{'error':'Not an allowed file'})
        mime=mimetypes.guess_type(str(p))[0] or 'application/octet-stream'
        self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(p.stat().st_size));self.send_header('X-Content-Type-Options','nosniff');self.end_headers()
        with p.open('rb') as f:
            while True:
                chunk=f.read(256*1024)
                if not chunk: break
                self.wfile.write(chunk)
    def do_POST(self):
        if not trusted_request(self.headers.get('Host'),self.headers.get('Origin'),self.server.server_port): return self.send_json(403,{'error':'Untrusted Host or Origin'})
        if self.path!='/api/management': return self.send_json(404,{'error':'Unknown route'})
        if self.headers.get('Content-Type','').split(';')[0]!='application/json': return self.send_json(415,{'error':'application/json required'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=65536: raise ValueError('Invalid payload length')
            payload=json.loads(self.rfile.read(length));status,value=update_state(payload,self.server.valid_ids)
            self.send_json(status,value)
        except (ValueError,UnicodeError) as e: self.send_json(400,{'error':str(e)})

def registered_preview_paths(catalog, root=ROOT):
    allowed=set();root=root.resolve()
    for row in catalog.get('entities',[]):
        for preview in row.get('previews',[]):
            path=preview.get('path','')
            if not isinstance(path,str) or not path.startswith('plans/chapter1-quality04-20261101-01/') or '\\' in path or ':' in path or '..' in Path(path).parts or Path(path).suffix.lower()!='.png':continue
            resolved=(root/path).resolve()
            if resolved.is_relative_to(root) and resolved.is_file():allowed.add(path)
    return allowed

def make_server(port=8781):
    catalog=generate();server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.catalog=catalog;server.valid_ids={r['id'] for r in catalog['entities']+catalog['tasks']}
    server.allowed={r['path'] for r in catalog['files']}|{r['source']['path'] for r in catalog['entities']+catalog['tasks']}|{'PROJECT-GOAL.ko.md',PLAN+'/MANAGER-PLAN.ko.md',catalog['build']['source']}|set(catalog['build'].get('verification_sources',[]))|{r['source'] for r in catalog['build'].get('preserved_builds',[])}
    server.allowed.update(registered_preview_paths(catalog))
    return server

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8781);args=parser.parse_args()
    with make_server(args.port) as server:
        print('Game Manager: http://127.0.0.1:'+str(server.server_port),flush=True)
        server.serve_forever()
