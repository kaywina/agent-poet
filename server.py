import json
import os
import time
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

base = os.path.dirname(os.path.abspath(__file__))

def today_date_str():
    return time.strftime("%Y-%m-%d")

def state_path_for(date_str):
    return os.path.join(base, "state", date_str + ".json")

def load_state(date_str):
    path = state_path_for(date_str)
    if not os.path.exists(path):
        return {"date": date_str, "status": "PENDING", "attempts": 0}
    with open(path) as f:
        return json.load(f)

def load_draft_text(date_str):
    draft_path = os.path.join(base, "drafts", date_str + ".txt")
    if not os.path.exists(draft_path):
        return None
    with open(draft_path) as f:
        return f.read()

def publish_today_via_app():
    # Call the existing publish command in app.py
    os.system("python app.py publish")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        date_str = today_date_str()
        state = load_state(date_str)
        draft = load_draft_text(date_str)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        html = []
        html.append("<html><body>")
        html.append("<h1>Agent Poet</h1>")
        html.append("<p><b>Date:</b> %s</p>" % date_str)
        html.append("<p><b>Status:</b> %s</p>" % state.get("status"))
        html.append("<p><b>Attempts:</b> %s</p>" % state.get("attempts"))

        if draft:
            html.append("<h2>Today's Draft</h2>")
            html.append("<pre>%s</pre>" % draft.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))
            if state.get("status") == "READY":
                html.append('<form method="POST" action="/publish">')
                html.append('<button type="submit">Publish</button>')
                html.append("</form>")
        else:
            html.append("<p>No draft available yet.</p>")

        html.append("</body></html>")
        self.wfile.write("".join(html))

    def do_POST(self):
        if self.path == "/publish":
            publish_today_via_app()
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
            return

        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    port = 8000
    print("Server running at http://localhost:%d" % port)
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
