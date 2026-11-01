#!/usr/bin/env python3
"""Detect coding-agent involvement in merged PRs.
Usage: python3 agentic.py <gh_raw_dir> <git_root> <out.json>
Signals (any => agent-involved), recorded separately:
  login  : PR author login is a coding-agent account
  body   : PR body contains an agent signature
  commit : merged (squash/merge) commit message contains an agent co-author/signature trailer
"""
import json, os, re, subprocess, sys

AGENT_LOGINS = {
    "copilot": "copilot", "copilot-swe-agent[bot]": "copilot", "copilot-swe-agent": "copilot",
    "devin-ai-integration[bot]": "devin", "devin-ai-integration": "devin",
    "google-labs-jules[bot]": "jules", "google-labs-jules": "jules",
    "cursor[bot]": "cursor", "cursoragent": "cursor",
    "claude[bot]": "claude", "claude": "claude",
    "codex[bot]": "codex", "chatgpt-codex-connector[bot]": "codex",
    "gemini-code-assist[bot]": "gemini_review", "gemini-cli[bot]": "gemini_cli",
    "sweep-ai[bot]": "sweep", "openhands-agent": "openhands",
}
PATTERNS = [
    ("claude", re.compile(r"generated with \[?claude code|claude\.ai/code|co-authored-by:\s*claude|noreply@anthropic\.com", re.I)),
    ("codex", re.compile(r"chatgpt\.com/codex|codex task|co-authored-by:\s*codex", re.I)),
    ("copilot", re.compile(r"copilot coding agent|copilot-swe-agent", re.I)),
    ("copilot_coauthor", re.compile(r"co-authored-by:\s*copilot\b", re.I)),
    ("cursor", re.compile(r"cursor\.com/(agents|background-agent)|co-authored-by:\s*cursor\s*agent|cursoragent@cursor\.com", re.I)),
    ("devin", re.compile(r"app\.devin\.ai|devin-ai-integration", re.I)),
    ("jules", re.compile(r"jules\.google|google-labs-jules", re.I)),
    ("gemini_cli", re.compile(r"generated (with|by) gemini( cli)?|co-authored-by:\s*gemini[- ]cli", re.I)),
    ("gemini_review", re.compile(r"co-authored-by:\s*gemini-code-assist", re.I)),
    ("openhands", re.compile(r"openhands", re.I)),
]

REVIEW_ONLY = {"gemini_review", "copilot_coauthor"}

def scan(text):
    return sorted({name for name, p in PATTERNS if p.search(text or "")})

def main(raw, gitroot, out):
    res = {}
    for fn in sorted(os.listdir(raw)):
        if not fn.endswith(".prs.json"): continue
        repo = fn[:-9]
        g = os.path.join(gitroot, repo + ".git")
        # full messages of commits keyed by PR number
        msgs = {}
        log = subprocess.run(["git","-C",g,"log","--all","--format=%x1e%B"],capture_output=True,text=True).stdout
        for m in log.split("\x1e"):
            subj = m.strip().split("\n",1)[0]
            mm = re.match(r"^Merge pull request #(\d+)", subj) or re.search(r"\(#(\d+)\)\s*$", subj)
            if mm and mm.group(1) not in msgs:
                msgs[mm.group(1)] = m
        for it in json.load(open(os.path.join(raw, fn))):
            n = str(it["number"]); login = it["user"]["login"]
            sig = {"login": [AGENT_LOGINS[login.lower()]] if login.lower() in AGENT_LOGINS else [],
                   "body": scan(it.get("body")), "commit": scan(msgs.get(n, ""))}
            allsig = set(sig["login"]) | set(sig["body"]) | set(sig["commit"])
            # agent_authored: an autonomous coding agent opened the PR or authored its change;
            # review_assist only: co-author trailer from an AI review bot / Copilot suggestion (weaker signal)
            sig["agent_authored"] = bool(allsig - REVIEW_ONLY)
            sig["review_assist_only"] = bool(allsig) and not sig["agent_authored"]
            res[f"{repo}#{n}"] = sig
    json.dump(res, open(out,"w"))

if __name__ == "__main__":
    main(*sys.argv[1:])
