#!/usr/bin/env python3
"""Intra-annotator agreement between pass 1 and pass 2 on the re-label subset.
Usage: python3 agreement.py <labels_pass1.csv> <labels_pass2.csv> <relabel_indices.json> <out.json>"""
import csv, json, sys
from collections import Counter
p1 = {int(r["idx"]): r for r in csv.DictReader(open(sys.argv[1]), delimiter="|")}
p2 = {int(r["k"]): r for r in csv.DictReader(open(sys.argv[2]), delimiter="|")}
idx = json.load(open(sys.argv[3]))
def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0
out = {}
pairs = [(p1[i], p2[k]) for k, i in enumerate(idx)]
a = [x["include"] for x, _ in pairs]; b = [y["include"] for _, y in pairs]
out["include"] = dict(zip(["agreement", "kappa"], kappa(a, b)), n=len(a))
both = [(x, y) for x, y in pairs if x["include"] == "yes" and y["include"] == "yes"]
for f in ["element", "symptom", "client_specific"]:
    a = [x[f] for x, _ in both]; b = [y[f] for _, y in both]
    out[f] = dict(zip(["agreement", "kappa"], kappa(a, b)), n=len(a))
    out[f]["disagreements"] = [(x["id"], x[f], y[f]) for x, y in both if x[f] != y[f]]
json.dump(out, open(sys.argv[4], "w"), indent=1)
print(json.dumps(out, indent=1))
