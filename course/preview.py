"""Loopback-only preview of owned course output at /course/."""

from __future__ import annotations

import argparse
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from course.build import CSP


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        path = unquote(urlsplit(self.path).path)
        if not path.startswith("/course/") or ".." in path.split("/"):
            self.send_error(404)
            return
        self.path = self.path[len("/course") :]
        super().do_GET()

    def do_HEAD(self) -> None:
        if not self.path.startswith("/course/") or ".." in unquote(self.path).split("/"):
            self.send_error(404)
            return
        self.path = self.path[len("/course") :]
        super().do_HEAD()

    def end_headers(self) -> None:
        self.send_header("Content-Security-Policy", CSP + "; frame-ancestors 'none'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8099)
    ap.add_argument("--output", default="build/course")
    args = ap.parse_args()
    if not re.fullmatch(r"build/course(?:-[a-z0-9-]+)?", args.output):
        raise ValueError("preview requires dedicated build/course[-label] directory")
    repository = Path(__file__).resolve().parents[1]
    root = repository / args.output
    if (repository / "build").is_symlink():
        raise ValueError("symlink build directory")
    if root.is_symlink() or not (root / ".course-build.json").is_file():
        raise ValueError("run make course-build first; preview requires owned output")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=str(root)))
    print(f"Course preview: http://127.0.0.1:{args.port}/course/", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
