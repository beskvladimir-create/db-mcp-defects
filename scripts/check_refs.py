#!/usr/bin/env python3
"""Check every PR reference in paper.md against dataset.csv.
Handles 'owner/repo#N' and continuation references '#M' that follow within the same parenthesis/sentence,
which are attributed to the most recent owner/repo. Prints each reference with its dataset title and labels.
Usage: python3 check_refs.py paper.md analysis/dataset.csv"""
import csv, re, sys
paper = open(sys.argv[1]).read()
paper = paper.split("\n## References")[0]
ds = {(r["repo"], int(r["number"])): r for r in csv.DictReader(open(sys.argv[2]))}
repos = {r for r, _ in ds}
bad = 0; seen = []
for m in re.finditer(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#(\d+)((?:,\s*#\d+)*)", paper):
    repo = m.group(1); nums = [int(m.group(2))] + [int(x) for x in re.findall(r"#(\d+)", m.group(3))]
    for n in nums:
        key = (repo, n)
        if repo not in repos:
            print("NOT A STUDY REPO:", repo, n); bad += 1; continue
        r = ds.get(key)
        if r is None:
            print("MISSING:", repo, n); bad += 1; continue
        seen.append(key)
        print(f"OK {repo}#{n}: {r['title'][:70]} | include={r['include']} {r['element']}/{r['symptom']} {r.get('unsafe_kind','')}")
# bare '#N' references not attached to a repo (e.g. author issue #4332, PR #4359)
for m in re.finditer(r"(?<![\w/])#(\d{2,5})\b", paper):
    ctx = paper[max(0, m.start()-60):m.start()]
    if not re.search(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#\d+[^.]*$", ctx):
        print("BARE (check manually):", m.group(0), "...", ctx[-50:].replace("\n", " "))
print(f"{len(seen)} references matched, {bad} problems")
