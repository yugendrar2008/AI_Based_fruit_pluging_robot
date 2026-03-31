Python 3.12.0b4 (tags/v3.12.0b4:97a6a41, Jul 11 2023, 13:49:15) [MSC v.1935 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

PI5_IP = "192.168.1.100"  

HTML = """
<h1>Robot Control</h1>

<button onclick="cmd('F')">Forward</button>
<button onclick="cmd('B')">Backward</button>
<button onclick="cmd('L')">Left</button>
<button onclick="cmd('R')">Right</button>
<button onclick="cmd('S')">Stop</button>

<h2>Motor A</h2>
<input id="a"><button onclick="moveA()">Move</button>

<h2>Motor B</h2>
<input id="b"><button onclick="moveB()">Move</button>
... 
... <script>
... function cmd(c){
...  fetch('/control?c=' + c);
... }
... function moveA(){
...  let v=document.getElementById('a').value;
...  fetch('/moveA?cm=' + v);
... }
... function moveB(){
...  let v=document.getElementById('b').value;
...  fetch('/moveB?cm=' + v);
... }
... </script>
... """
... 
... @app.route("/")
... def home():
...     return render_template_string(HTML)
... 
... @app.route("/control")
... def control():
...     c = request.args.get("c")
...     requests.get(f"http://{PI5_IP}:5000/control?cmd={c}")
...     return "OK"
... 
... @app.route("/moveA")
... def moveA():
...     cm = request.args.get("cm")
...     requests.get(f"http://{PI5_IP}:5000/moveA?cm={cm}")
...     return "OK"
... 
... @app.route("/moveB")
... def moveB():
...     cm = request.args.get("cm")
...     requests.get(f"http://{PI5_IP}:5000/moveB?cm={cm}")
...     return "OK"
... 
... if __name__ == "__main__":
