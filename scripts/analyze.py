#!/usr/bin/env python3
"""All quantitative results of the paper.
Usage: python3 analyze.py <kaggle_dir> [labels_file]
Reads analysis/sample.jsonl, analysis/labels_pass1.csv, analysis/frame_stats.json, analysis/agentic.json,
raw/gh/*.prs.json, analysis/frame.csv. Writes analysis/results.json, analysis/tables.md, analysis/dataset.csv.
"""
import csv, json, math, os, random, sys, glob
from collections import Counter, defaultdict

D = sys.argv[1]
A = os.path.join(D, "analysis")
recs = {json.loads(l)["id"]: json.loads(l) for l in open(f"{A}/sample.jsonl")}
# Optional 2nd argument: a corrected labels file (e.g. the author's reviewed spreadsheet exported as CSV).
# Required columns: id, include, exclude_reason, element, symptom, client_specific, unsafe_kind, note
# (idx optional). Delimiter '|' or ',' is detected from the header line. Default: analysis/labels_pass1.csv.
LABELS = sys.argv[2] if len(sys.argv) > 2 else f"{A}/labels_pass1.csv"
_head = open(LABELS, encoding="utf-8-sig").readline()
lab = list(csv.DictReader(open(LABELS, encoding="utf-8-sig"), delimiter="|" if "|" in _head else ","))
_need = {"id", "include", "exclude_reason", "element", "symptom", "client_specific", "unsafe_kind", "note"}
_miss = _need - set(lab[0].keys())
if _miss: sys.exit(f"labels file {LABELS} lacks columns: {sorted(_miss)}")
for _l in lab:
    for _k in _need: _l[_k] = (_l.get(_k) or "").strip()
_ids = {json.loads(x)["id"] for x in open(f"{A}/sample.jsonl")}
if {l["id"] for l in lab} != _ids or len(lab) != len(_ids):
    sys.exit(f"labels file {LABELS} must contain each of the {len(_ids)} sampled ids exactly once")
stats = json.load(open(f"{A}/frame_stats.json"))
ag = json.load(open(f"{A}/agentic.json"))
R = {}

def wilson(k, n, z=1.96):
    if n == 0: return (0, 0)
    p = k / n; d = 1 + z*z/n; c = p + z*z/(2*n); h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return ((c-h)/d, (c+h)/d)

# ---- dataset table
rows = []
for l in lab:
    r = recs[l["id"]]
    a = ag.get(l["id"], {})
    rows.append({"id": l["id"], "repo": r["repo"], "number": r["number"], "url": f"https://github.com/{r['repo']}/pull/{r['number']}",
                 "title": r["title"], "author": r["author"], "merged_at": r["merged_at"], "include": l["include"],
                 "exclude_reason": l["exclude_reason"], "element": l["element"], "symptom": l["symptom"],
                 "client_specific": l["client_specific"], "unsafe_kind": l.get("unsafe_kind", ""), "agent_authored": a.get("agent_authored", False),
                 "review_assist_only": a.get("review_assist_only", False),
                 "agent_signals": ";".join(sorted(set(a.get("login", [])) | set(a.get("body", [])) | set(a.get("commit", [])))),
                 "frame_size_repo": r["frame_size_repo"], "sampled_repo": r["sampled_repo"], "note": l["note"]})
with open(f"{A}/dataset.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

inc = [r for r in rows if r["include"] == "yes"]
R["n_repos_queried"] = len(stats)
R["n_repos_with_frame"] = sum(1 for s in stats.values() if s["frame"] > 0)
R["merged_prs_total"] = sum(s["merged_prs"] for s in stats.values())
R["fixlike_total"] = sum(s["fixlike"] for s in stats.values())
R["auto_excluded_total"] = sum(s["auto_excluded"] for s in stats.values())
R["frame_total"] = sum(s["frame"] for s in stats.values())
R["sampled_total"] = len(rows)
R["included_total"] = len(inc)
R["included_repos"] = len({r["repo"] for r in inc})
R["exclusion_reasons"] = Counter(r["exclude_reason"] for r in rows if r["include"] == "no")

# ---- weights: each sampled unit represents frame_size/sampled PRs of its repo
for r in rows: r["w"] = r["frame_size_repo"] / r["sampled_repo"]

def dist(field, sub):
    n = len(sub); c = Counter(r[field] for r in sub)
    W = sum(r["w"] for r in sub); cw = defaultdict(float)
    for r in sub: cw[r[field]] += r["w"]
    return {k: {"n": v, "pct": 100*v/n, "ci95": [100*x for x in wilson(v, n)], "weighted_pct": 100*cw[k]/W}
            for k, v in c.most_common()}

R["element"] = dist("element", inc)
R["symptom"] = dist("symptom", inc)

# repo-cluster bootstrap for key proportions (resample repos with replacement)
byrepo = defaultdict(list)
for r in inc: byrepo[r["repo"]].append(r)
repos = sorted(byrepo)
def boot(pred, denom_pred=lambda r: True, B=5000, seed=1):
    rng = random.Random(seed); vals = []
    for _ in range(B):
        s = [x for rp in (rng.choice(repos) for _ in repos) for x in byrepo[rp]]
        d = [x for x in s if denom_pred(x)]
        if d: vals.append(100*sum(pred(x) for x in d)/len(d))
    vals.sort(); return [vals[int(.025*len(vals))], vals[int(.975*len(vals))]]

UND = {"SILENT", "UNSAFE"}; DET = {"MISLEAD", "REJECT", "TOOLS", "UNAVAIL"}
known = [r for r in inc if r["symptom"] in UND | DET]
R["agent_facing_known"] = len(known)
R["undetectable_n"] = sum(r["symptom"] in UND for r in known)
R["undetectable_pct"] = 100*R["undetectable_n"]/len(known)
R["undetectable_ci95_wilson"] = [100*x for x in wilson(R["undetectable_n"], len(known))]
R["undetectable_ci95_repo_bootstrap"] = boot(lambda r: r["symptom"] in UND, lambda r: r["symptom"] in UND | DET)
R["silent_or_mislead_n"] = sum(r["symptom"] in {"SILENT", "UNSAFE", "MISLEAD"} for r in known)
R["silent_or_mislead_pct"] = 100*R["silent_or_mislead_n"]/len(known)
R["silent_or_mislead_ci95_repo_bootstrap"] = boot(lambda r: r["symptom"] in {"SILENT", "UNSAFE", "MISLEAD"}, lambda r: r["symptom"] in UND | DET)
W = sum(r["w"] for r in known)
R["undetectable_weighted_pct"] = 100*sum(r["w"] for r in known if r["symptom"] in UND)/W
R["symptom_operator_unknown"] = {k: sum(r["symptom"] == k for r in inc) for k in ("OPERATOR", "UNKNOWN")}

# crosstab element x symptom
els = [k for k in R["element"]]; sy = ["SILENT", "UNSAFE", "MISLEAD", "REJECT", "TOOLS", "UNAVAIL", "OPERATOR", "UNKNOWN"]
ct = {e: {s: sum(1 for r in inc if r["element"] == e and r["symptom"] == s) for s in sy} for e in els}
R["crosstab"] = ct
# concentration: GUARD/UNSAFE
R["guard_unsafe"] = ct.get("GUARD", {}).get("UNSAFE", 0)
R["unsafe_total"] = sum(r["symptom"] == "UNSAFE" for r in inc)
R["silent_by_element"] = {e: ct[e]["SILENT"] for e in els if ct[e]["SILENT"]}
R["client_specific_n"] = sum(r["client_specific"] == "yes" for r in inc)
R["client_specific_items"] = [(r["id"], r["element"], r["symptom"], r["note"]) for r in inc if r["client_specific"] == "yes"]
R["description_defects"] = [r["id"] for r in inc if "description defect" in r["note"]]
R["oversized_output"] = [r["id"] for r in inc if any(k in r["note"].lower() for k in ("oversized", "bloat", "floods context", "mbs"))]
R["per_repo_included"] = Counter(r["repo"] for r in inc)
R["per_repo_undetectable"] = {rp: [sum(x["symptom"] in UND for x in byrepo[rp]), sum(x["symptom"] in UND | DET for x in byrepo[rp])] for rp in repos}

# ---- agentic authorship over all merged PRs
fr = {row["id"] for row in csv.DictReader(open(f"{A}/frame.csv"))}
allp = []
for fn in glob.glob(f"{D}/raw/gh/*.prs.json"):
    repo = os.path.basename(fn)[:-9]
    for it in json.load(open(fn)):
        k = f"{repo}#{it['number']}"
        allp.append({"id": k, "repo": repo, "merged": (it.get("pull_request") or {}).get("merged_at") or it["closed_at"],
                     "frame": k in fr, "agent": ag[k]["agent_authored"], "review": ag[k]["review_assist_only"]})
R["agentic_all_n"] = len(allp)
R["agentic_all_agent"] = sum(p["agent"] for p in allp)
R["agentic_all_review_only"] = sum(p["review"] for p in allp)
fp = [p for p in allp if p["frame"]]; nf = [p for p in allp if not p["frame"]]
R["agentic_frame"] = [sum(p["agent"] for p in fp), len(fp)]
R["agentic_nonframe"] = [sum(p["agent"] for p in nf), len(nf)]
R["agentic_included"] = [sum(r["agent_authored"] for r in inc), len(inc)]
R["agentic_included_items"] = [(r["id"], r["agent_signals"], r["element"], r["symptom"]) for r in inc if r["agent_authored"]]
R["agentic_repos_with_any"] = sorted({p["repo"] for p in allp if p["agent"]})
half = defaultdict(lambda: [0, 0])
for p in allp:
    y, m = p["merged"][:4], int(p["merged"][5:7]); key = f"{y}H{1 if m <= 6 else 2}"
    half[key][0] += p["agent"]; half[key][1] += 1
R["agentic_by_half"] = dict(sorted(half.items()))
halff = defaultdict(lambda: [0, 0])
for p in fp:
    y, m = p["merged"][:4], int(p["merged"][5:7]); key = f"{y}H{1 if m <= 6 else 2}"
    halff[key][0] += p["agent"]; halff[key][1] += 1
R["agentic_frame_by_half"] = dict(sorted(halff.items()))
R["agentic_by_repo"] = {rp: [sum(p["agent"] for p in allp if p["repo"] == rp), sum(1 for p in allp if p["repo"] == rp)] for rp in sorted({p["repo"] for p in allp})}
# Fisher exact (two-sided) frame vs non-frame
def fisher(a, b, c, d):
    from math import comb
    n = a+b+c+d; r1 = a+b; c1 = a+c
    def p(x): return comb(r1, x)*comb(n-r1, c1-x)/comb(n, c1)
    p0 = p(a); lo, hi = max(0, c1-(n-r1)), min(r1, c1)
    return sum(p(x) for x in range(lo, hi+1) if p(x) <= p0*(1+1e-9))
a, n1 = R["agentic_frame"]; c, n2 = R["agentic_nonframe"]
R["agentic_fisher_p"] = fisher(a, n1-a, c, n2-c)

json.dump(R, open(f"{A}/results.json", "w"), indent=1, default=list)

# ---- markdown tables
L = []
L.append("| Repository | Merged PRs | Fix-like | Auto-excl. | Frame | Sampled | Included |\n|---|---:|---:|---:|---:|---:|---:|")
for k, s in sorted(stats.items(), key=lambda x: -x[1]["frame"]):
    rp = k.replace("__", "/")
    L.append(f"| {rp} | {s['merged_prs']} | {s['fixlike']} | {s['auto_excluded']} | {s['frame']} | {s.get('sampled', 0)} | {R['per_repo_included'].get(rp, 0)} |")
L.append(f"| **Total** | {R['merged_prs_total']} | {R['fixlike_total']} | {R['auto_excluded_total']} | {R['frame_total']} | {R['sampled_total']} | {R['included_total']} |")
L.append("\n| Element \\ Symptom | " + " | ".join(sy) + " | Total |\n|---|" + "---:|"*(len(sy)+1))
for e in els:
    L.append(f"| {e} | " + " | ".join(str(ct[e][s]) for s in sy) + f" | {R['element'][e]['n']} |")
L.append("| **Total** | " + " | ".join(str(sum(ct[e][s] for e in els)) for s in sy) + f" | {len(inc)} |")
open(f"{A}/tables.md", "w").write("\n".join(L) + "\n")
print(json.dumps({k: R[k] for k in ["frame_total", "sampled_total", "included_total", "included_repos", "agent_facing_known",
      "undetectable_n", "undetectable_pct", "undetectable_ci95_wilson", "undetectable_ci95_repo_bootstrap", "undetectable_weighted_pct",
      "silent_or_mislead_n", "silent_or_mislead_pct", "silent_or_mislead_ci95_repo_bootstrap", "symptom_operator_unknown",
      "client_specific_n", "agentic_all_n", "agentic_all_agent", "agentic_all_review_only", "agentic_frame", "agentic_nonframe",
      "agentic_included", "agentic_fisher_p", "agentic_by_half", "agentic_frame_by_half", "exclusion_reasons", "description_defects", "oversized_output"]}, indent=1, default=list))

# ---- extra: agentic robustness excluding the dominant repo, and symptom mix of agent-authored fixes
X = "bytebase__dbhub"
fpx = [p for p in fp if p["repo"] != X]; nfx = [p for p in nf if p["repo"] != X]
E = {"agentic_all_excl_dbhub": [sum(p["agent"] for p in allp if p["repo"] != X), sum(1 for p in allp if p["repo"] != X)],
     "agentic_frame_excl_dbhub": [sum(p["agent"] for p in fpx), len(fpx)],
     "agentic_nonframe_excl_dbhub": [sum(p["agent"] for p in nfx), len(nfx)],
     "agentic_dbhub": R["agentic_by_repo"][X]}
a, n1 = E["agentic_frame_excl_dbhub"]; c, n2 = E["agentic_nonframe_excl_dbhub"]
E["agentic_fisher_p_excl_dbhub"] = fisher(a, n1-a, c, n2-c)
agi = [r for r in inc if r["agent_authored"]]; hum = [r for r in inc if not r["agent_authored"]]
E["agent_fix_repos"] = Counter(r["repo"] for r in agi)
E["agent_fix_element"] = Counter(r["element"] for r in agi)
E["agent_fix_symptom"] = Counter(r["symptom"] for r in agi)
E["agent_fix_guard_share"] = [sum(r["element"] == "GUARD" for r in agi), len(agi)]
E["nonagent_fix_guard_share"] = [sum(r["element"] == "GUARD" for r in hum), len(hum)]
# client-specific breakdown
cs = [r for r in inc if r["client_specific"] == "yes"]
E["client_specific_element"] = Counter(r["element"] for r in cs)
E["tooldef_schema_tools"] = sum(1 for r in inc if r["element"] == "TOOL_DEF" and r["symptom"] == "TOOLS")
E["tooldef_client_specific"] = sum(1 for r in cs if r["element"] == "TOOL_DEF")
E["gemini_mentions_in_included"] = [r["id"] for r in inc if "gemini" in (recs[r["id"]]["body"] + recs[r["id"]]["title"]).lower()]
# detectability among GUARD and by symptom group
E["undetectable_share_excl_guard"] = [sum(r["symptom"] == "SILENT" for r in known if r["element"] != "GUARD"), sum(1 for r in known if r["element"] != "GUARD")]
E["author_own_items_in_sample"] = [r["id"] for r in rows if r["author"].lower().startswith("beskvladimir")]
json.dump(E, open(f"{A}/results_extra.json", "w"), indent=1, default=list)
print(json.dumps(E, indent=1, default=list))


# ---- round 1 additions: UNSAFE split, sensitivity analyses, fix-like denominators, CMH
S = {}
S["unsafe_kind"] = Counter(r["unsafe_kind"] for r in inc if r["symptom"] == "UNSAFE")
pm = {x["id"]: x["mechanism"] for x in csv.DictReader(open(f"{A}/policy_mechanism.csv"), delimiter="|")}
S["policy_mechanism"] = Counter(pm[r["id"]].split(" (")[0] for r in inc if r["unsafe_kind"] == "policy")
S["unsafe_vuln_items"] = [(r["id"], r["note"][:60]) for r in inc if r["unsafe_kind"] == "vuln"]
def headline(sub, und=lambda r: r["symptom"] in UND):
    k = [r for r in sub if r["symptom"] in UND | DET]
    n = sum(und(r) for r in k)
    nm = sum(r["symptom"] in {"SILENT", "UNSAFE", "MISLEAD"} for r in k)
    return {"undetectable": n, "untrustworthy": nm, "denominator": len(k),
            "undetectable_pct": round(100*n/len(k), 1), "untrustworthy_pct": round(100*nm/len(k), 1),
            "undetectable_wilson": [round(100*x, 1) for x in wilson(n, len(k))]}
S["headline_all"] = headline(inc)
S["headline_excl_GUARD"] = headline([r for r in inc if r["element"] != "GUARD"])
S["headline_excl_vuln"] = headline([r for r in inc if r["unsafe_kind"] != "vuln"])
S["headline_excl_oversized"] = headline([r for r in inc if r["id"] not in R["oversized_output"]])
S["boot_excl_GUARD"] = boot(lambda r: r["symptom"] in UND, lambda r: r["symptom"] in UND | DET and r["element"] != "GUARD")
S["boot_excl_vuln"] = boot(lambda r: r["symptom"] in UND, lambda r: r["symptom"] in UND | DET and r["unsafe_kind"] != "vuln")
# de-duplicate follow-up series: one unit per group (modal symptom; ties -> first PR)
grp = {x["id"]: x["group"] for x in csv.DictReader(open(f"{A}/defect_groups.csv"), delimiter="|")}
seen = {}; dedup = []
for r in sorted(inc, key=lambda r: (r["repo"], r["number"])):
    g = grp.get(r["id"])
    if g is None: dedup.append(r); continue
    seen.setdefault(g, []).append(r)
for g, members in seen.items():
    sym = Counter(m["symptom"] for m in members).most_common(1)[0][0]
    rep = dict(next(m for m in members if m["symptom"] == sym)); dedup.append(rep)
S["dedup_units"] = len(dedup)
S["headline_dedup"] = headline(dedup)
# agent share over ALL fix-like PRs (frame + auto-excluded)
ax = {row["id"] for row in csv.DictReader(open(f"{A}/auto_excluded.csv"))}
fl = [p for p in allp if p["frame"] or p["id"] in ax]; nfl = [p for p in allp if not (p["frame"] or p["id"] in ax)]
S["agentic_fixlike_all"] = [sum(p["agent"] for p in fl), len(fl)]
S["agentic_non_fixlike"] = [sum(p["agent"] for p in nfl), len(nfl)]
# Cochran-Mantel-Haenszel across repositories: agent-signed vs not, by group membership, stratified by repository
def cmh(ingroup):
    num = den = 0.0; ORn = ORd = 0.0
    for rp in sorted({p["repo"] for p in allp}):
        P = [p for p in allp if p["repo"] == rp]
        a = sum(p["agent"] and ingroup(p) for p in P); b = sum((not p["agent"]) and ingroup(p) for p in P)
        c = sum(p["agent"] and not ingroup(p) for p in P); d = sum((not p["agent"]) and not ingroup(p) for p in P)
        n = a+b+c+d
        if n < 2: continue
        r1, c1 = a+b, a+c
        num += a - r1*c1/n; den += r1*(n-r1)*c1*(n-c1)/(n*n*(n-1))
        ORn += a*d/n; ORd += b*c/n
    chi = (abs(num)-0.5)**2/den
    return round(chi, 2), math.erfc(math.sqrt(chi/2)), round(ORn/ORd, 2)
S["cmh_chi2"], S["cmh_p"], S["mh_odds_ratio"] = cmh(lambda p: p["frame"])          # frame vs all other merged PRs
S["cmh_fixlike_chi2"], S["cmh_fixlike_p"], S["mh_fixlike_odds_ratio"] = cmh(lambda p: p["frame"] or p["id"] in ax)  # all fix-like vs other
json.dump(S, open(f"{A}/results_round1.json", "w"), indent=1, default=list)
print(json.dumps(S, indent=1, default=list))
