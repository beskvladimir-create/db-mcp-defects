#!/usr/bin/env python3
"""Generate APPENDIX.md from analysis outputs. Usage: python3 appendix.py <analysis_dir> <out.md>"""
import json, csv, sys
A, OUT = sys.argv[1], sys.argv[2]
R=json.load(open(f'{A}/results.json')); S=json.load(open(f'{A}/results_round1.json')); E=json.load(open(f'{A}/results_extra.json'))
tab=open(f'{A}/tables.md').read().split('\n\n')[0]
rows=list(csv.DictReader(open(f'{A}/dataset.csv')))
L=["# Appendix to \"Silent, Unsafe or Misleading\"","","All numbers are produced by `scripts/analyze.py` (results.json, results_extra.json, results_round1.json).","",
"## A. Sampling frame and sample by repository","","Window: PRs created 2024-11-01..2026-10-31, merged by collection on 2026-11-01.","",tab,"",
"## B. Agent-facing symptom examples (all included fixes with these symptoms)",""]
for sym in ["SILENT","UNSAFE","MISLEAD"]:
    L.append(f"### {sym}")
    for r in rows:
        if r['include']=='yes' and r['symptom']==sym:
            k=f" ({r['unsafe_kind']})" if r['unsafe_kind'] else ""
            L.append(f"- [{r['repo']}#{r['number']}]({r['url']}) {r['element']}{k}: {r['note']}")
    L.append("")
L+=["## C. Client- or toolchain-specific fixes",""]
for r in rows:
    if r['include']=='yes' and r['client_specific']=='yes':
        L.append(f"- [{r['repo']}#{r['number']}]({r['url']}) {r['element']}/{r['symptom']}: {r['note']}")
L+=["","## D. Agent authorship by half-year (all merged PRs)","","| Half | Agent-signed | Merged PRs |","|---|---:|---:|"]
for h,(a,n) in R['agentic_by_half'].items(): L.append(f"| {h} | {a} | {n} |")
L+=["",f"Fix-like (all 1,051): {S['agentic_fixlike_all'][0]}/{S['agentic_fixlike_all'][1]}; other merged PRs: {S['agentic_non_fixlike'][0]}/{S['agentic_non_fixlike'][1]}. Frame: {R['agentic_frame'][0]}/{R['agentic_frame'][1]}; non-frame: {R['agentic_nonframe'][0]}/{R['agentic_nonframe'][1]}. Mantel-Haenszel across repositories (frame vs other merged PRs): OR {S['mh_odds_ratio']}, chi2 {S['cmh_chi2']}, p {S['cmh_p']:.2g}. Without bytebase/dbhub: frame {E['agentic_frame_excl_dbhub'][0]}/{E['agentic_frame_excl_dbhub'][1]}, other {E['agentic_nonframe_excl_dbhub'][0]}/{E['agentic_nonframe_excl_dbhub'][1]}.",
"","## E. Sensitivity of the headline","","| Variant | Undetectable | Not trustworthy | Denominator |","|---|---:|---:|---:|"]
for k,lab in [("headline_all","All"),("headline_excl_vuln","Without attacker-facing UNSAFE"),("headline_excl_GUARD","Without GUARD"),("headline_excl_oversized","Without oversized-output fixes"),("headline_dedup","Follow-up series merged")]:
    h=S[k]; L.append(f"| {lab} | {h['undetectable']} ({h['undetectable_pct']}%) | {h['untrustworthy']} ({h['untrustworthy_pct']}%) | {h['denominator']} |")
L+=["","## F. Label corrections after review round 1 (2026-11-01)","",
"| PR | Before | After | Reason |","|---|---|---|---|",
"| FreePeak/db-mcp-server#66 | GUARD/UNSAFE | EXEC/SILENT | regression fix of #63, not an injection fix |",
"| neondatabase/mcp-server-neon#250 | ERROR/MISLEAD | CONFIG/UNAVAIL | rule 5: OAuth callback failure |",
"| mongodb-js/mongodb-mcp-server#1121 | CONFIG/REJECT | CONFIG/UNAVAIL | rule 5: authentication failure in connect tool |",
"| FreePeak/db-mcp-server#70 | SESSION/REJECT | SESSION/UNAVAIL | codebook: call times out |",
"| supabase/mcp#410 | GUARD/UNSAFE | TOOL_DEF/TOOLS | rule 3: description-only change |",
"| Snowflake-Labs/mcp#35 | EXEC/REJECT | EXEC/UNKNOWN | no error text in the record |",
"","History files (not reported in the paper): `labels_pass1_v1.csv` is an earlier draft; `labels_pass2.csv` and `agreement*.json` are an LLM self-consistency pass."]
open(OUT,'w').write("\n".join(L)+"\n")
