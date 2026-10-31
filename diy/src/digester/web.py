"""Local read-only dashboard (stdlib only). Binds to 127.0.0.1 by default.
The only write action is 'reset trip', which the controller refuses while unsafe."""
import json, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width">
<title>Digester</title><style>body{font-family:sans-serif;margin:1em}td{padding:2px 8px}
.trip{color:#b00;font-weight:bold}</style><h1>DIY Digester</h1><div id=s>loading</div>
<button onclick="fetch('/reset',{method:'POST'}).then(r=>r.json()).then(j=>alert(JSON.stringify(j)))">Reset trip</button>
<script>async function u(){const j=await (await fetch('/status')).json();let h='';
h+=j.tripped?'<p class=trip>TRIPPED: '+j.trip_reasons.join(', ')+'</p>':'<p>Running</p>';
h+='<p>Alarms: '+(j.alarms.join(', ')||'none')+'</p><table>';
for(const[k,v]of Object.entries(j.readings))h+='<tr><td>'+k+'<td>'+v;
for(const[k,v]of Object.entries(j.outputs))h+='<tr><td>OUT '+k+'<td>'+(v?'ON':'off');
document.getElementById('s').innerHTML=h+'</table>'}setInterval(u,3000);u()</script>"""


def serve(state, host, port):
    """state: dict with 'ctl' and 'last' (latest Readings), guarded by state['lock']."""
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _json(self, obj, code=200):
            b = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            if self.path == "/status":
                with state["lock"]:
                    return self._json(state["ctl"].status(state["last"]))
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(PAGE.encode())

        def do_POST(self):
            if self.path == "/reset":
                with state["lock"]:
                    ok, why = state["ctl"].reset(state["last"])
                return self._json({"reset": ok, "still_unsafe": why})
            self._json({"error": "not found"}, 404)

    srv = ThreadingHTTPServer((host, port), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv
