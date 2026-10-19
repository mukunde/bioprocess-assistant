"""Loopback-only manual review UI with a per-process CSRF token."""
from __future__ import annotations

import json
import secrets
import io
import re
import threading
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from ingestion.store import check_integrity, decide, list_records

# PDFium is not thread-safe, even for different documents. Share the lock
# across every review server in this process, including cache misses.
_PDFIUM_LOCK = threading.Lock()


def make_server(run: Path, port: int = 8765) -> ThreadingHTTPServer:
    check_integrity(run)
    token = secrets.token_hex(32)
    page = Path(__file__).with_name("review.html").read_text(encoding="utf-8").replace("__TOKEN__", token)

    @lru_cache(maxsize=4)
    def render_page(index: int) -> bytes:
        try:
            import pypdfium2 as pdfium
        except ImportError as exc:
            raise ValueError("Install pypdfium2 from requirements-ingestion.txt for page previews") from exc
        with _PDFIUM_LOCK, pdfium.PdfDocument(run / "source.pdf") as pdf:
            if not 0 <= index < len(pdf):
                raise ValueError("Page index out of bounds")
            pdf_page = pdf[index]
            try:
                bitmap = pdf_page.render(scale=1.5)
                try:
                    image = bitmap.to_pil()
                    try:
                        data = io.BytesIO()
                        image.save(data, format="PNG")
                        return data.getvalue()
                    finally:
                        image.close()
                finally:
                    bitmap.close()
            finally:
                pdf_page.close()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Never log PDF content, notes or query strings.

        def send(self, status: int, data: bytes, content_type: str):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'nonce-" + token + "'; style-src 'self' 'nonce-" + token + "'; frame-ancestors 'none'; object-src 'none'")
            self.end_headers()
            self.wfile.write(data)

        def json(self, status: int, value):
            self.send(status, json.dumps(value, ensure_ascii=False).encode(), "application/json; charset=utf-8")

        def valid_host(self):
            return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

        def do_GET(self):
            if not self.valid_host():
                return self.json(403, {"error": "Invalid Host"})
            try:
                if self.path == "/":
                    self.send(200, page.encode(), "text/html; charset=utf-8")
                elif self.path == "/api/records":
                    self.json(200, {"manifest": check_integrity(run), "records": list_records(run)})
                elif self.path == "/source.pdf":
                    check_integrity(run)
                    self.send(200, (run / "source.pdf").read_bytes(), "application/pdf")
                elif re.fullmatch(r"/pages/[0-9]+\.png", self.path):
                    check_integrity(run)
                    self.send(200, render_page(int(self.path[7:-4])), "image/png")
                else:
                    self.json(404, {"error": "Not found"})
            except (ValueError, OSError) as exc:
                self.json(409, {"error": str(exc)})

        def do_POST(self):
            if not self.valid_host() or self.headers.get("X-Review-Token") != token:
                return self.json(403, {"error": "Invalid review token"})
            origin = self.headers.get("Origin")
            if origin and origin != f"http://127.0.0.1:{self.server.server_port}":
                return self.json(403, {"error": "Invalid origin"})
            if self.path != "/api/decision":
                return self.json(404, {"error": "Not found"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 65536 or self.headers.get_content_type() != "application/json":
                    raise ValueError("Expected a small JSON decision")
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict) or any(not isinstance(data.get(k), str) for k in ("record_id", "action", "reviewer", "note")):
                    raise ValueError("Invalid decision fields")
                decide(run, data["record_id"], data["action"], data["reviewer"], data["note"],
                       source_checked=data.get("source_checked") is True)
                self.json(200, {"status": "recorded"})
            except (ValueError, OSError) as exc:
                self.json(400, {"error": str(exc)})

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def serve(run: Path, port: int = 8765) -> None:
    server = make_server(run, port)
    print(f"Manual review: http://127.0.0.1:{server.server_port} (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
