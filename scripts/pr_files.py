#!/usr/bin/env python3
"""Map PR numbers to changed files using bare clones (squash '(#N)' subjects or 'Merge pull request #N').
Usage: python3 pr_files.py <gitdir_root> <out.json>
Output: {"owner__repo": {"N": {"sha":..., "files":[[status,path],...]}}}
For merge commits, files = diff of merge commit vs first parent.
"""
import json, os, re, subprocess, sys

root, out = sys.argv[1], sys.argv[2]
res = {}
SQ = re.compile(r"\(#(\d+)\)\s*$")
MG = re.compile(r"^Merge pull request #(\d+)")
for d in sorted(os.listdir(root)):
    if not d.endswith(".git"): continue
    g = os.path.join(root, d)
    log = subprocess.run(["git","-C",g,"log","--all","--format=%H%x09%P%x09%s"],capture_output=True,text=True).stdout
    m = {}
    for line in log.splitlines():
        sha, parents, subj = line.split("\t", 2)
        n = None
        mm = MG.match(subj)
        if mm: n = mm.group(1)
        else:
            ms = SQ.search(subj)
            if ms: n = ms.group(1)
        if n and n not in m:
            m[n] = sha
    repo = {}
    for n, sha in m.items():
        # diff vs first parent: squash (1 parent) or merge commit (PR changes = parent1..merge)
        par = subprocess.run(["git","-C",g,"rev-list","--parents","-n","1",sha],capture_output=True,text=True).stdout.split()
        base = par[1] if len(par) > 1 else "4b825dc642cb6eb9a060e54bf8d69288fbee4904"  # empty tree for root commit
        r = subprocess.run(["git","-C",g,"diff","--name-status",base,sha],capture_output=True,text=True)
        files = [l.split("\t") for l in r.stdout.splitlines() if "\t" in l]
        repo[n] = {"sha": sha, "files": files}
    res[d[:-4]] = repo
    print(d, len(repo), file=sys.stderr)
json.dump(res, open(out,"w"))
