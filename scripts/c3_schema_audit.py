#!/usr/bin/env python3
"""C3 audit: how MCP tool input schemas survive translation into Gemma 4 function declarations.

Reference: the Gemma 4 chat template (`gemma4_v5.jinja` in huggingface/trl, a copy of the template shipped with
google/gemma-4-E2B-it at revision 8995379; header "Google Gemma 4 Canonical Chat Template ... Published 2026-07-09").
Its `format_parameters` macro renders, per property: description; type (a single string, upper-cased); enum (only
when type is STRING); items (only when type is ARRAY; item keys are rendered generically); nullable; properties and
required (only when type is OBJECT). Every other JSON-Schema keyword is not rendered.

Measurements per tool, on the raw schema and on the schema after the proposed C3 normaliser (normalise()):
 (1) static: which schema features would be dropped or mis-rendered (rules below, mirroring the macro);
 (2) rendered: the tool is rendered through the template with jinja2; we record template errors and empty
     `type:<|"|><|"|>` fields in the output.
Usage: python3 c3_schema_audit.py <tools_dir> <template.jinja> <out.json> <out_rows.csv>
"""
import csv, json, os, re, sys
from collections import Counter, defaultdict

RENDERED = {"description", "type", "enum", "items", "nullable", "properties", "required"}
CONSTRAINTS = {"default", "format", "pattern", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
               "minLength", "maxLength", "minItems", "maxItems", "uniqueItems", "const", "additionalProperties",
               "multipleOf", "propertyNames", "patternProperties", "examples", "minProperties", "maxProperties"}
UNIONS = {"anyOf", "oneOf", "allOf", "$ref", "not", "if", "then", "else"}
COSMETIC = {"title"}

def audit_property(name, p, path, issues):
    if not isinstance(p, dict):
        issues["non_object_schema"].append(path); return
    t = p.get("type")
    keys = set(p)
    if any(k in keys for k in UNIONS):
        issues["union_or_ref"].append(path)
    if not isinstance(t, str):
        issues["no_single_type"].append(path)   # missing type, list of types, or union -> empty/garbled TYPE
    if not p.get("description"):
        issues["param_no_description"].append(path)
    lost = sorted(k for k in keys & CONSTRAINTS)
    if "enum" in keys and (not isinstance(t, str) or t.upper() != "STRING"):
        lost.append("enum(non-string)")
    if lost:
        issues["constraint_dropped"].append(path + ":" + ",".join(lost))
    other = sorted(k for k in keys - RENDERED - CONSTRAINTS - UNIONS - COSMETIC)
    if other:
        issues["other_key_dropped"].append(path + ":" + ",".join(other))
    if isinstance(t, str) and t.upper() == "OBJECT":
        props = p.get("properties")
        if isinstance(props, dict) and props:
            for k, v in props.items(): audit_property(k, v, f"{path}.{k}", issues)
        else:
            issues["object_without_properties"].append(path)
    if isinstance(t, str) and t.upper() == "ARRAY":
        it = p.get("items")
        if not isinstance(it, dict) or not it:
            issues["array_without_items"].append(path)
        else:
            # item keys are rendered generically (key:value): a union inside items is passed through verbatim (not lost);
            # a $ref inside items is passed through unresolved, so its target structure is lost
            if "$ref" in it: issues["items_ref_unresolved"].append(path + "[]")
            elif any(k in it for k in UNIONS): issues["items_union_passthrough"].append(path + "[]")

def normalise(schema):
    """Proposed check C3: rewrite anyOf/oneOf [T, null] -> T + nullable:true, list types [T,'null'] -> T + nullable,
    and inline local $ref targets from $defs/definitions. Everything else is left unchanged."""
    import copy
    s = copy.deepcopy(schema or {})
    defs = {**(s.get("$defs") or {}), **(s.get("definitions") or {})}
    def fix(node, depth=0):
        if isinstance(node, list): return [fix(x, depth) for x in node]
        if not isinstance(node, dict) or depth > 20: return node
        if "$ref" in node and isinstance(node["$ref"], str):
            name = node["$ref"].split("/")[-1]
            if name in defs:
                extra = {k: v for k, v in node.items() if k != "$ref"}
                node = {**defs[name], **extra}
        for key in ("anyOf", "oneOf"):
            u = node.get(key)
            if isinstance(u, list):
                nonnull = [x for x in u if not (isinstance(x, dict) and x.get("type") == "null")]
                if len(nonnull) == 1 and len(nonnull) < len(u):
                    merged = {**nonnull[0], **{k: v for k, v in node.items() if k != key}}
                    merged["nullable"] = True
                    node = merged
                elif len(nonnull) == 1:
                    node = {**nonnull[0], **{k: v for k, v in node.items() if k != key}}
        t = node.get("type")
        if isinstance(t, list):
            nn = [x for x in t if x != "null"]
            if len(nn) == 1:
                node = {**node, "type": nn[0]}
                if len(nn) < len(t): node["nullable"] = True
        return {k: fix(v, depth + 1) for k, v in node.items()}
    out = fix(s)
    out.pop("$defs", None); out.pop("definitions", None)
    return out

def audit_tool(tool):
    issues = defaultdict(list)
    s = tool.get("inputSchema") or {}
    if not tool.get("description"): issues["tool_no_description"].append(tool.get("name"))
    if s.get("type") != "object": issues["top_not_object"].append(str(s.get("type")))
    top_other = sorted(k for k in s if k not in {"type", "properties", "required", "$schema", "additionalProperties", "title", "description", "$defs", "definitions"})
    if any(k in s for k in ("$defs", "definitions")): issues["defs_present"].append("$defs")
    if top_other: issues["top_key_dropped"].append(",".join(top_other))   # e.g. $defs: referenced definitions lost
    props = s.get("properties")
    if isinstance(props, dict):
        for k, v in props.items(): audit_property(k, v, k, issues)
    return issues

def render(env, tmpl, tool):
    t = {"type": "function", "function": {"name": tool["name"], "description": tool.get("description") or "",
                                          "parameters": tool.get("inputSchema") or {}}}
    try:
        out = tmpl.render(messages=[{"role": "user", "content": "x"}], tools=[t], add_generation_prompt=True,
                          bos_token="<bos>")
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"[:200]
    m = re.search(r"<\|tool>(.*?)<tool\|>", out, re.S)
    return (m.group(1) if m else out), None

KEYS = ["union_or_ref", "no_single_type", "constraint_dropped", "other_key_dropped", "object_without_properties",
        "array_without_items", "items_union_passthrough", "items_ref_unresolved", "param_no_description",
        "tool_no_description", "top_key_dropped", "defs_present", "top_not_object", "non_object_schema"]

def main(tools_dir, template, out_json, out_csv):
    import jinja2
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(template)), extensions=["jinja2.ext.loopcontrols"])
    env.filters.setdefault("tojson", lambda x, **k: json.dumps(x))
    tmpl = env.get_template(os.path.basename(template))
    servers, rows = {}, []
    for fn in sorted(os.listdir(tools_dir)):
        d = json.load(open(os.path.join(tools_dir, fn)))
        sid = fn[:-5]
        if "tools" not in d:
            servers[sid] = {"status": "failed", "reason": d.get("error", "")[-300:]}; continue
        srv = {"status": "ok", "server_info": d.get("server_info"), "n_tools": len(d["tools"]), "tools_with": Counter()}
        for tool in d["tools"]:
            for variant, t in (("raw", tool), ("norm", {**tool, "inputSchema": normalise(tool.get("inputSchema"))})):
                iss = audit_tool(t)
                rendered, err = render(env, tmpl, t)
                empty_type = rendered.count('type:<|"|><|"|>') if rendered else 0
                row = {"server": sid, "tool": tool["name"], "variant": variant,
                       "n_params": len((t.get("inputSchema") or {}).get("properties") or {}),
                       "render_error": err or "", "rendered_empty_type": empty_type}
                for k in KEYS:
                    row[k] = "; ".join(iss.get(k, []))
                    if iss.get(k): srv["tools_with"][variant + ":" + k] += 1
                row["type_lost"] = bool(iss.get("no_single_type") or iss.get("union_or_ref") or iss.get("non_object_schema") or iss.get("items_ref_unresolved") or empty_type or err)
                row["structure_misrendered"] = bool(iss.get("object_without_properties"))
                row["type_or_structure_lost"] = row["type_lost"] or row["structure_misrendered"]
                row["constraint_lost"] = bool(iss.get("constraint_dropped") or iss.get("top_key_dropped"))
                for k in ["type_lost", "structure_misrendered", "type_or_structure_lost", "constraint_lost"]:
                    if row[k]: srv["tools_with"][variant + ":" + k] += 1
                if err: srv["tools_with"][variant + ":render_error"] += 1
                if empty_type: srv["tools_with"][variant + ":rendered_empty_type"] += 1
                rows.append(row)
        servers[sid] = srv
    ok = {k: v for k, v in servers.items() if v["status"] == "ok"}
    repo = lambda sid: sid.split("__")[0] + "/" + sid.split("__")[1]
    repos = sorted({repo(k) for k in ok})
    tot = Counter()
    for v in ok.values(): tot.update(v["tools_with"])
    n_tools = sum(v["n_tools"] for v in ok.values())
    def repos_with(variant, key): return sorted({repo(r["server"]) for r in rows if r["variant"] == variant and r[key]})
    per_cfg = {k: {"n_tools": v["n_tools"], "type_or_structure_lost_raw": v["tools_with"].get("raw:type_or_structure_lost", 0),
                   "type_or_structure_lost_norm": v["tools_with"].get("norm:type_or_structure_lost", 0)} for k, v in ok.items()}
    top = sorted(per_cfg.items(), key=lambda x: -x[1]["type_or_structure_lost_raw"])[:3]
    summary = {"attempt_files": len(servers), "server_configs_ok": len(ok), "repos_covered": repos, "n_repos_covered": len(repos),
               "n_tools": n_tools, "tools_with": dict(sorted(tot.items())),
               "repos_with_type_or_structure_lost_raw": repos_with("raw", "type_or_structure_lost"),
               "repos_with_type_or_structure_lost_norm": repos_with("norm", "type_or_structure_lost"),
               "top3_configs_raw": [(k, v["type_or_structure_lost_raw"], v["n_tools"]) for k, v in top],
               "top3_share_of_raw_losses": sum(v["type_or_structure_lost_raw"] for _, v in top),
               "failed": {k: v["reason"] for k, v in servers.items() if v["status"] != "ok"},
               "per_config": per_cfg,
               "server_info": {k: v["server_info"].get("name") + " " + str(v["server_info"].get("version")) if v["server_info"] else None for k, v in ok.items()}}
    summary["n_repos_type_or_structure_lost_raw"] = len(summary["repos_with_type_or_structure_lost_raw"])
    summary["n_repos_type_or_structure_lost_norm"] = len(summary["repos_with_type_or_structure_lost_norm"])
    json.dump(summary, open(out_json, "w"), indent=1)
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(json.dumps({k: summary[k] for k in ["attempt_files", "server_configs_ok", "n_repos_covered", "n_tools", "tools_with", "n_repos_type_or_structure_lost_raw", "n_repos_type_or_structure_lost_norm", "top3_configs_raw", "top3_share_of_raw_losses", "repos_with_type_or_structure_lost_norm"]}, indent=1))

if __name__ == "__main__":
    main(*sys.argv[1:])
