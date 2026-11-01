#!/usr/bin/env python3
"""Render compact text views of sample records for manual labelling.
Usage: python3 view.py <sample.jsonl> <start> <end> [bodychars=650]
Labels are never shown (blind view)."""
import json, re, sys

def clean(t):
    t = re.sub(r"<!--.*?-->", "", t or "", flags=re.S)
    t = re.split(r"\n#+\s*(PR Checklist|Checklist|Type of change|How Has This Been Tested|Testing)\b", t, flags=re.I)[0]
    t = "\n".join(l for l in t.splitlines() if not re.match(r"\s*- \[[ xX]\]", l))
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "[img]", t)
    return re.sub(r"\s+", " ", t).strip()

recs = [json.loads(l) for l in open(sys.argv[1])]
s, e = int(sys.argv[2]), int(sys.argv[3]); bc = int(sys.argv[4]) if len(sys.argv) > 4 else 650
for i, r in enumerate(recs[s:e], start=s):
    fl = [f[-1] for f in (r.get("files") or [])]
    src = [f for f in fl if not re.search(r"(test|docs?/|\.md$|README|CHANGELOG|package-lock|go\.sum|uv\.lock|\.github/)", f, re.I)]
    print(f"[{i}] {r['id']} | {r['title']} | by {r['author']} | labels={r['labels']}")
    print("  B:", clean(r["body"])[:bc])
    for iss in r.get("linked_issues", [])[:2]:
        print(f"  I#{iss['number']}: {iss['title']} :: {clean(iss['body'])[:300]}")
    print(f"  F({len(fl)}):", src[:7], "" if r.get("files") is not None else "NO-FILE-MAP")
