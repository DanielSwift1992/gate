#!/usr/bin/env python3
"""Authorize the trusted inline programs, never inline event handlers.

Only call this on the bench template and JSON-escaped build data. This hashes
program bytes; it is not a sanitizer for an untrusted HTML document.
"""
import base64
import hashlib
import json
import re
import sys
from pathlib import Path


def script_json(value):
    return (json.dumps(value).replace("&", "\\u0026")
            .replace("<", "\\u003c").replace(">", "\\u003e"))


def stamp_csp(page):
    hashes = []
    for attrs, code in re.findall(r"<script\b([^>]*)>(.*?)</script\s*>", page, re.S | re.I):
        if re.search(r"\bsrc\s*=", attrs, re.I):
            continue
        hashes.append("'sha256-" + base64.b64encode(hashlib.sha256(code.encode("utf-8")).digest()).decode("ascii") + "'")
    policy = "script-src 'self' " + " ".join(dict.fromkeys(hashes))
    page, count = re.subn(r"script-src\s+[^;\"]+", lambda _: policy, page, count=1)
    if count != 1:
        raise ValueError("bench page declares no script-src to stamp")
    if "script-src-attr" not in page:
        page = page.replace(policy + ";", policy + "; script-src-attr 'none';", 1)
    return page


if __name__ == "__main__":
    path = Path(sys.argv[1])
    path.write_text(stamp_csp(path.read_text(encoding="utf-8")), encoding="utf-8")
