#!/usr/bin/env python3
"""Count top-level parameters whose schema is a nullable union (anyOf/oneOf of one type plus null), the pattern
Python type hints such as Optional[str] produce. Usage: python3 c3_optional.py <tools_dir> <out.json>"""
import json, os, sys
from collections import Counter
c = Counter(); tools_with = set(); servers = set()
for fn in sorted(os.listdir(sys.argv[1])):
    d = json.load(open(os.path.join(sys.argv[1], fn)))
    for t in d.get("tools", []):
        for k, p in ((t.get("inputSchema") or {}).get("properties") or {}).items():
            if not isinstance(p, dict): continue
            c["params"] += 1
            u = p.get("anyOf") or p.get("oneOf")
            if isinstance(u, list):
                c["union_params"] += 1
                if any(isinstance(x, dict) and x.get("type") == "null" for x in u):
                    c["nullable_union_params"] += 1; tools_with.add((fn, t["name"])); servers.add(fn[:-5])
            if isinstance(p.get("type"), list): c["type_list_params"] += 1
            if "$ref" in p: c["ref_params"] += 1
out = dict(c); out["tools_with_nullable_union"] = len(tools_with); out["server_configs_with_nullable_union"] = sorted(servers)
json.dump(out, open(sys.argv[2], "w"), indent=1); print(json.dumps(out, indent=1))
