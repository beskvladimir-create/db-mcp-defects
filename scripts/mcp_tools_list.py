#!/usr/bin/env python3
"""Start an MCP server over stdio, run initialize + tools/list (with pagination), save the tools as JSON.
Usage: python3 mcp_tools_list.py <out.json> <timeout_s> -- <command> [args...]
Environment variables for the server are taken from the current environment.
Exit code 0 and a JSON file {"server_info":..., "tools":[...]} on success; otherwise the error is written."""
import json, os, subprocess, sys, threading, time, queue

def main():
    out, timeout = sys.argv[1], float(sys.argv[2])
    cmd = sys.argv[sys.argv.index("--") + 1:]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    q = queue.Queue()
    def reader():
        for line in p.stdout:
            q.put(line)
    threading.Thread(target=reader, daemon=True).start()
    errbuf = []
    threading.Thread(target=lambda: [errbuf.append(l) for l in p.stderr], daemon=True).start()
    def send(obj):
        p.stdin.write(json.dumps(obj) + "\n"); p.stdin.flush()
    def wait(id_, deadline):
        while time.time() < deadline:
            try:
                line = q.get(timeout=0.5)
            except queue.Empty:
                if p.poll() is not None: raise RuntimeError("server exited: " + "".join(errbuf)[-800:])
                continue
            line = line.strip()
            if not line.startswith("{"): continue
            try: msg = json.loads(line)
            except Exception: continue
            if msg.get("id") == id_: return msg
        raise TimeoutError("timeout; stderr tail: " + "".join(errbuf)[-800:])
    deadline = time.time() + timeout
    result = {"command": cmd}
    try:
        send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18",
              "capabilities": {}, "clientInfo": {"name": "schema-audit", "version": "0.1"}}})
        init = wait(1, deadline)
        result["server_info"] = init.get("result", {}).get("serverInfo")
        result["protocol_version"] = init.get("result", {}).get("protocolVersion")
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        tools, cursor, i = [], None, 2
        while True:
            params = {"cursor": cursor} if cursor else {}
            send({"jsonrpc": "2.0", "id": i, "method": "tools/list", "params": params})
            r = wait(i, deadline)
            if "error" in r: raise RuntimeError("tools/list error: " + json.dumps(r["error"]))
            tools += r["result"].get("tools", [])
            cursor = r["result"].get("nextCursor"); i += 1
            if not cursor: break
        result["tools"] = tools
        ok = True
    except Exception as e:
        result["error"] = str(e)[:2000]; ok = False
    finally:
        try: p.kill()
        except Exception: pass
    json.dump(result, open(out, "w"), indent=1)
    print(("OK %d tools" % len(result["tools"])) if ok else ("FAIL " + result["error"][:300]))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
