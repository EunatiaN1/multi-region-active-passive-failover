#!/bin/bash
set -euo pipefail

dnf install -y python3
useradd --system --no-create-home --shell /sbin/nologin webapp

cat >/opt/health_server.py <<'PYTHON'
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ("/health", "/origin-health"):
            self.respond(200, b"healthy", "text/plain; charset=utf-8")
            return

        if path != "/":
            self.send_error(404)
            return

        body = b"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Primary application</title></head>
<body><main><h1>Hello from the primary AWS region</h1>
<p>This sample response is served by the Auto Scaling application tier.</p>
</main></body>
</html>"""
        self.respond(200, body, "text/html; charset=utf-8")

    def respond(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))


class WebServer(ThreadingHTTPServer):
    daemon_threads = True


WebServer(("0.0.0.0", 80), Handler).serve_forever()
PYTHON

cat >/etc/systemd/system/portfolio-web.service <<'SERVICE'
[Unit]
Description=Portfolio sample web application
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=webapp
Group=webapp
ExecStart=/usr/bin/python3 /opt/health_server.py
Restart=on-failure
RestartSec=3
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=strict
RestrictAddressFamilies=AF_INET AF_INET6
RestrictRealtime=true

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable --now portfolio-web.service
