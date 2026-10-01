#!/usr/bin/env python3
"""
Lightweight API server exposing:
    POST /screen   (Trigger screening on a folder)
    GET  /results  (Retrieve latest screening results)
"""
import os
import json
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from src.pipeline import run_screening_pipeline

# Latest in-memory results store
LATEST_RESULTS = {"status": "No screening run executed yet"}

class ScreeningAPIHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: dict):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload, indent=2).encode('utf-8'))

    def do_GET(self):
        if self.path == "/results":
            self._send_json(200, LATEST_RESULTS)
        elif self.path == "/health":
            self._send_json(200, {"status": "healthy", "service": "Resume Screening API"})
        else:
            self._send_json(404, {"error": "Not Found. Available endpoints: POST /screen, GET /results, GET /health"})

    def do_POST(self):
        global LATEST_RESULTS
        if self.path == "/screen":
            content_length = int(self.headers.get('Content-Length', 0))
            input_dir = "./resumes"
            if content_length > 0:
                try:
                    body = json.loads(self.rfile.read(content_length).decode('utf-8'))
                    input_dir = body.get("input_dir", input_dir)
                except Exception:
                    pass

            if not os.path.exists(input_dir):
                self._send_json(400, {"error": f"Directory not found: {input_dir}"})
                return

            try:
                output = run_screening_pipeline(input_dir)
                LATEST_RESULTS = {
                    "batch_summary": output.summary.model_dump(),
                    "ranked_candidates": [c.model_dump(exclude_none=True) for c in output.ranked_candidates],
                    "rejected_candidates": [c.model_dump(exclude_none=True) for c in output.rejected_candidates]
                }
                self._send_json(200, LATEST_RESULTS)
            except Exception as e:
                self._send_json(500, {"error": f"Screening pipeline error: {str(e)}"})
        else:
            self._send_json(404, {"error": "Not Found"})


def run_server(port: int = 8000, host: str = "0.0.0.0"):
    server_address = (host, port)
    httpd = HTTPServer(server_address, ScreeningAPIHandler)
    print(f"🚀 Resume Screening API running on http://{host}:{port}")
    print(f"   Endpoints: POST /screen, GET /results, GET /health")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resume Screening API Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind server (default: 8000)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind server (default: 127.0.0.1)")
    args = parser.parse_args()
    run_server(port=args.port, host=args.host)
