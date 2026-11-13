"""DogDex: a localhost-only collector app, using Python's standard library."""
import argparse,json,mimetypes,secrets,sys,threading,urllib.parse,webbrowser
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from .collector import Collection,ValidationError
ROOT=Path(__file__).resolve().parents[1]
def make_server(root=ROOT,port=8765,preview=False,user_dir=None):
    root=Path(root);store=Collection(root,user_dir);token=secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,format,*args):
            if self.command!='GET' or args and str(args[1]) not in ('200','304'):super().log_message(format,*args)
        def send(self,status,raw,mime='application/json',headers=None):
            self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(raw)));self.send_header('X-Content-Type-Options','nosniff');self.send_header('Cache-Control','private, max-age=3600' if mime.startswith('image/') else 'no-store');self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data: blob:; style-src 'self'; script-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'self'")
            for k,v in (headers or {}).items():self.send_header(k,v)
            self.end_headers();self.wfile.write(raw)
        def reply(self,value,status=200):self.send(status,json.dumps(value,ensure_ascii=False).encode())
        def allowed_host(self):return preview or self.headers.get('Host','').split(':')[0] in ('127.0.0.1','localhost')
        def do_GET(self):
            if not self.allowed_host():self.reply(dict(error='Local access only.'),403);return
            path=urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
            if path=='/api/state':
                from .marketplace import price_state
                view=store.editor_view();self.reply(dict(state=store.state(),view=view,prices=price_state(store,view),token=token,conditions=__import__('dogdex.collector',fromlist=['*']).CONDITIONS));return
            if path=='/api/source-inventory.csv':
                from .source_inventory import inventory_csv
                self.send(200,inventory_csv(store),'text/csv; charset=utf-8',{'Content-Disposition':'attachment; filename="DogDex_Source_Inventory.csv"'});return
            if path=='/api/backup':self.send(200,store.backup(),'application/zip',{'Content-Disposition':'attachment; filename="DogDex_Collection_Backup.zip"'});return
            if path=='/catalog.json':target=root/'data/catalog.json';mime='application/json'
            elif path.startswith('/images/'):
                name=path.removeprefix('/images/')
                if not __import__('re').fullmatch(r'[a-f0-9]{64}\.webp',name):self.reply(dict(error='Not found.'),404);return
                target=root/'data/images'/name;mime='image/webp'
            elif path.startswith('/user-images/'):
                name=path.removeprefix('/user-images/')
                if not __import__('re').fullmatch(r'[a-f0-9]{64}\.(png|jpg|gif|webp)',name):self.reply(dict(error='Not found.'),404);return
                target=store.user_dir/'catalog_images'/name;mime=mimetypes.guess_type(name)[0] or 'application/octet-stream'
            else:
                relative='index.html' if path=='/' else path.lstrip('/');target=(root/'static'/relative).resolve()
                if not target.is_relative_to((root/'static').resolve()):self.reply(dict(error='Not found.'),404);return
                mime='text/javascript' if target.suffix in ('.js','.mjs') else mimetypes.guess_type(target)[0] or 'application/octet-stream'
                if mime.startswith('text/') or target.suffix in ('.js','.mjs'):mime+='; charset=utf-8'
            if not target.is_file():self.reply(dict(error='Not found.'),404);return
            self.send(200,target.read_bytes(),mime)
        def do_POST(self):
            if not self.allowed_host() or self.headers.get('X-DogDex-Token')!=token:self.reply(dict(error='Reopen DogDex to reconnect.'),403);return
            origin=self.headers.get('Origin')
            if origin and not preview and urllib.parse.urlsplit(origin).hostname not in ('127.0.0.1','localhost'):self.reply(dict(error='Local access only.'),403);return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=128_000_000:raise ValidationError('Request is too large or empty.')
                raw=self.rfile.read(length);action=urllib.parse.urlsplit(self.path).path.removeprefix('/api/')
                if action=='restore':result=store.restore(raw)
                else:
                    if length>12_000_000:raise ValidationError('Request is too large.')
                    data=json.loads(raw)
                    if not isinstance(data,dict):raise ValidationError('Invalid request.')
                    result=store.mutate(action,data)
                    if action in ('market/search','catalog/printing/audit','catalog/bulk/preview'):self.reply(dict(ok=True,result=result));return
                view=store.editor_view() if action.startswith('catalog/') or action in ('restore','market/confirm','market/unlink') else None
                from .marketplace import price_state
                self.reply(dict(ok=True,result=result,state=store.state(),view=view,prices=price_state(store,view) if view else None))
            except (ValidationError,ValueError,KeyError,TypeError) as e:self.reply(dict(error=str(e)),400)
            except Exception:
                __import__('traceback').print_exc();self.reply(dict(error='Could not save this change. Your earlier records are still stored.'),500)
    server=ThreadingHTTPServer(('0.0.0.0' if preview else '127.0.0.1',port),Handler);server.store=store;return server
def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);p.add_argument('--preview',action='store_true');p.add_argument('--no-browser',action='store_true');p.add_argument('--user-dir');p.add_argument('--host');p.add_argument('--strictPort',action='store_true');a=p.parse_args()
    try:server=make_server(port=a.port,preview=a.preview,user_dir=a.user_dir)
    except OSError:
        if a.preview:raise
        server=make_server(port=0,user_dir=a.user_dir)
    address='http://127.0.0.1:'+str(server.server_port);print('DogDex is ready at '+address,flush=True);print('Your collection is saved in '+str(server.store.user_dir),flush=True)
    if not a.no_browser and not a.preview:threading.Timer(.6,lambda:webbrowser.open(address)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
