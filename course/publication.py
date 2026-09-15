"""Trusted contributor publication receipts; not automated editorial truth verification."""

from __future__ import annotations

import argparse
import hashlib
import re
from datetime import datetime
from pathlib import Path

from course.check import contained, input_digest, load_json

INPUTS = (
    "course/build.py",
    "course/site.py",
    "course/publication.py",
    "course/check.py",
    "course/preview.py",
    "course/static/site.css",
    "course/static/viewer.js",
    "course/static/favicon.svg",
    "course/package-lock.json",
    "uv.lock",
)
PASSES = (
    "desktop",
    "mobile",
    "light",
    "dark",
    "no_js",
    "keyboard",
    "print",
    "accessibility_tree",
    "subpath",
    "csp",
    "links",
    "visual",
)


def receipt_path(lecture: dict) -> str:
    return f"course/reviews/PUBLICATION-{lecture['id']:04d}.json"


def publication_digest(root: Path, lecture: dict) -> str:
    names = (*INPUTS, lecture["review"])
    digest = hashlib.sha256(input_digest(root, lecture).encode())
    for name in sorted(names):
        digest.update(name.encode() + b"\0")
        digest.update(hashlib.sha256(contained(root, name).read_bytes()).digest())
    return digest.hexdigest()


def check_publication(root: Path, lecture: dict) -> dict:
    receipt = load_json(root, receipt_path(lecture))
    if receipt.get("schema_version") != 1 or receipt.get("lecture_id") != lecture["id"]:
        raise ValueError("publication identity mismatch")
    if not receipt.get("reviewer"):
        raise ValueError("missing publication reviewer")
    date = datetime.fromisoformat(receipt.get("checked_at", "").replace("Z", "+00:00"))
    if date.utcoffset() is None or date.utcoffset().total_seconds() != 0:
        raise ValueError("publication timestamp must be UTC")
    if receipt.get("publication_digest") != publication_digest(root, lecture):
        raise ValueError("stale publication receipt")
    if any(receipt.get("passes", {}).get(name) is not True for name in PASSES):
        raise ValueError("incomplete publication passes")
    if receipt.get("assistive_technology", {}).get("tested") not in (True, False):
        raise ValueError("missing actual assistive technology scope")
    if not receipt["assistive_technology"].get("scope"):
        raise ValueError("missing assistive technology limitation")
    if not isinstance(receipt.get("renderer"), dict) or not receipt["renderer"]:
        raise ValueError("missing actual renderer fingerprint")
    artifacts = receipt.get("artifacts_sha256")
    if not isinstance(artifacts, dict):
        raise ValueError("missing publication artifact hashes")
    hashes = [receipt.get("rendered_sha256"), *artifacts.values()]
    if len(hashes) < 2 or any(
        not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value) for value in hashes
    ):
        raise ValueError("missing publication artifact hashes")
    return receipt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--digest", type=int, required=True)
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    lecture = next(
        x for x in load_json(root, "course/manifest.json")["lectures"] if x["id"] == args.digest
    )
    print(publication_digest(root, lecture))


if __name__ == "__main__":
    main()
