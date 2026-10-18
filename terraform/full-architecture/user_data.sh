#!/bin/bash
set -euo pipefail

dnf install -y python3

cat >/opt/health_server.py <<'PYTHON'
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/health", "/origin-health"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"healthy")
            return

        body = b"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Primary application</title></head>
<body><main><h1>Hello from the primary AWS region</h1>
<p>This sample response is served by the Auto Scaling application tier.</p>
</main></body>
</html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))


HTTPServer(("0.0.0.0", 80), Handler).serve_forever()
PYTHON

cat >/etc/systemd/system/portfolio-web.service <<'SERVICE'
[Unit]
Description=Portfolio sample web application
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/health_server.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable --now portfolio-web.service
