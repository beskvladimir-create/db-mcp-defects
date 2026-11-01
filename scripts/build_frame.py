#!/usr/bin/env python3
"""Build the sampling frame of fix-like merged PRs and draw the labelling sample.
Usage: python3 build_frame.py <gh_raw_dir> <pr_files.json> <outdir> [cap_per_repo=40] [seed=20261101]
Outputs: frame.csv (all fix-like PRs), auto_excluded.csv, sample.jsonl (records to label), frame_stats.json
"""
import csv, json, os, random, re, sys

FIXRE = re.compile(r"\b(fix|fixes|fixed|fixing|bug|bugs|bugfix|hotfix|crash|crashes|panic|broken|regression|incorrect|wrong)\b", re.I)
BOT = re.compile(r"(dependabot|renovate|release-please|github-actions|pre-commit-ci|snyk|mergify|allcontributors)", re.I)
AUTOEX = re.compile(r"^\s*(docs?|ci|test|tests|build|chore|style|release|revert)(\([^)]*\))?!?\s*:", re.I)
DEPS = re.compile(r"^\s*fix\(deps\)|\bbump\b|update dependency|upgrade dependenc", re.I)

def main(raw, prfiles, outdir, cap=40, seed=20261101):
    cap, seed = int(cap), int(seed)
    files = json.load(open(prfiles))
    os.makedirs(outdir, exist_ok=True)
    frame, autoex, stats = [], [], {}
    for fn in sorted(os.listdir(raw)):
        if not fn.endswith(".prs.json"): continue
        repo = fn[:-9]
        prs = json.load(open(os.path.join(raw, fn)))
        issues = {i["number"]: i for i in json.load(open(os.path.join(raw, repo + ".issues.json")))}
        st = {"merged_prs": len(prs), "fixlike": 0, "auto_excluded": 0, "frame": 0}
        for p in prs:
            labels = [l["name"] for l in p.get("labels", [])]
            title = p["title"]
            if not (FIXRE.search(title) or any("bug" in l.lower() for l in labels)):
                continue
            st["fixlike"] += 1
            reason = None
            if BOT.search(p["user"]["login"]): reason = "bot_author"
            elif DEPS.search(title): reason = "deps"
            elif AUTOEX.match(title): reason = "conventional_nonfix_prefix"
            fl = files.get(repo, {}).get(str(p["number"]), {}).get("files")
            rec = {"id": f"{repo}#{p['number']}", "repo": repo.replace("__", "/"), "number": p["number"],
                   "title": title, "author": p["user"]["login"], "created_at": p["created_at"],
                   "merged_at": (p.get("pull_request") or {}).get("merged_at"), "labels": labels,
                   "body": p.get("body") or "", "files": fl}
            if reason:
                rec["auto_reason"] = reason; autoex.append(rec); st["auto_excluded"] += 1; continue
            # attach referenced issues (closes/fixes #N, or bare #N) that exist in the issue set
            cand = re.findall(r"#(\d+)", rec["body"]) + re.findall(r"github\.com/" + re.escape(rec["repo"]) + r"/issues/(\d+)", rec["body"], flags=re.I)
            refs = sorted({int(x) for x in cand if int(x) in issues and int(x) != p["number"]})
            rec["linked_issues"] = [{"number": n, "title": issues[n]["title"], "body": (issues[n].get("body") or "")[:1500],
                                     "labels": [l["name"] for l in issues[n].get("labels", [])]} for n in refs[:3]]
            frame.append(rec); st["frame"] += 1
        stats[repo] = st
    rng = random.Random(seed)
    sample = []
    byrepo = {}
    for r in frame: byrepo.setdefault(r["repo"], []).append(r)
    for repo in sorted(byrepo):
        rs = sorted(byrepo[repo], key=lambda r: r["number"])
        prng = random.Random(f"{seed}:{repo}")  # per-repo RNG: sample independent of other repos
        order = rs[:]; prng.shuffle(order)       # nested samples: larger cap = superset of smaller cap
        for k, r in enumerate(order): r["draw_rank"] = k
        pick = order[:cap]
        for r in sorted(pick, key=lambda r: r["number"]):
            r["frame_size_repo"] = len(rs); r["sampled_repo"] = len(pick)
            sample.append(r)
        stats[repo.replace("/", "__")]["sampled"] = len(pick)
    with open(os.path.join(outdir, "frame.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "repo", "number", "title", "author", "created_at", "merged_at"])
        for r in frame: w.writerow([r["id"], r["repo"], r["number"], r["title"], r["author"], r["created_at"], r["merged_at"]])
    with open(os.path.join(outdir, "auto_excluded.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "title", "author", "auto_reason"])
        for r in autoex: w.writerow([r["id"], r["title"], r["author"], r["auto_reason"]])
    with open(os.path.join(outdir, "sample.jsonl"), "w") as f:
        for r in sample: f.write(json.dumps(r) + "\n")
    json.dump(stats, open(os.path.join(outdir, "frame_stats.json"), "w"), indent=1)
    print(json.dumps({"frame": len(frame), "auto_excluded": len(autoex), "sample": len(sample)}))

if __name__ == "__main__":
    main(*sys.argv[1:])
