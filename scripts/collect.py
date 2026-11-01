#!/usr/bin/env python3
"""Collect merged PRs and issues for the study repos via the GitHub Search API (gh api).
Usage: python3 collect.py <outdir>
Writes <outdir>/<owner>__<repo>.prs.json and .issues.json (raw search items).
Date window: created 2024-11-01 .. 2026-10-31 (inclusive). Splits windows so each query < 1000 hits.
"""
import json, subprocess, sys, time, os

REPOS = [
 "googleapis/mcp-toolbox","bytebase/dbhub","crystaldba/postgres-mcp","supabase/mcp",
 "benborla/mcp-server-mysql","qdrant/mcp-server-qdrant","designcomputer/mysql_mcp_server",
 "mongodb-js/mongodb-mcp-server","neo4j-contrib/mcp-neo4j","Anarkh-Lee/universal-db-mcp",
 "ClickHouse/mcp-clickhouse","alexander-zuev/supabase-mcp-server","elastic/mcp-server-elasticsearch",
 "neondatabase/mcp-server-neon","redis/mcp-redis","chroma-core/chroma-mcp","centralmind/gateway",
 "subnetmarco/pgmcp","motherduckdb/mcp-server-motherduck","FreePeak/db-mcp-server",
 "runekaagaard/mcp-alchemy","RichardHan/mssql_mcp_server","executeautomation/mcp-database-server",
 "cr7258/elasticsearch-mcp-server","neo4j/mcp","Snowflake-Labs/mcp",
]
START, END = "2024-11-01", "2026-10-31"
last_call = [0.0]

def search(q, page):
    # Search API: 30 req/min authenticated-equivalent; keep >=2.1 s spacing
    wait = 2.1 - (time.time() - last_call[0])
    if wait > 0: time.sleep(wait)
    for attempt in range(6):
        r = subprocess.run(["gh","api","-X","GET","search/issues","-f",f"q={q}","-f","per_page=100","-f",f"page={page}"],
                           capture_output=True, text=True)
        last_call[0] = time.time()
        if r.returncode == 0:
            return json.loads(r.stdout)
        sys.stderr.write(f"retry {attempt} {q} p{page}: {r.stderr[:200]}\n"); time.sleep(20*(attempt+1))
    raise RuntimeError(q)

def fetch_window(base, a, b, out):
    q = f"{base} created:{a}..{b}"
    first = search(q, 1)
    tot = first["total_count"]
    if tot >= 1000 and a != b:
        from datetime import date
        da, db = date.fromisoformat(a), date.fromisoformat(b)
        mid = da + (db - da)//2
        from datetime import timedelta
        fetch_window(base, a, mid.isoformat(), out)
        fetch_window(base, (mid+timedelta(days=1)).isoformat(), b, out)
        return
    out.extend(first["items"])
    pages = (min(tot,1000)+99)//100
    for p in range(2, pages+1):
        out.extend(search(q, p)["items"])

def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    log = []
    for r in REPOS:
        fn = r.replace("/","__")
        for kind, base in (("prs", f"repo:{r} is:pr is:merged"), ("issues", f"repo:{r} is:issue")):
            path = f"{outdir}/{fn}.{kind}.json"
            if os.path.exists(path): continue
            items = []
            fetch_window(base, START, END, items)
            uniq = {it["number"]: it for it in items}
            json.dump(list(uniq.values()), open(path,"w"))
            log.append((r, kind, len(uniq)))
            print(r, kind, len(uniq), flush=True)
    json.dump(log, open(f"{outdir}/collect_log.json","a"))

if __name__ == "__main__":
    main(sys.argv[1])
