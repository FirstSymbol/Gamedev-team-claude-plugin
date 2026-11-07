#!/usr/bin/env python3
"""Routing/trigger test: does a natural request reach the right studio agent or skill?

Usage: python tests/run_triggers.py [--cases tests/trigger_cases.json] [--jobs 4] [--only id1,id2]
For each case runs `claude -p <prompt> --plugin-dir plugins/studio --output-format stream-json`
in tests/sandbox and stops the process at the first routing decision: an Agent call with a
studio:* subagent_type, or a Skill call to a studio role skill (orchestrator is skipped since it
only leads to a later Agent call). Pass if the routed role is in the case's `expect` list.
Results: tests/out/triggers.json + summary on stdout.
"""
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "studio")
SANDBOX = os.path.join(ROOT, "tests", "sandbox")
OUT = os.path.join(ROOT, "tests", "out")
NON_ROUTING_SKILLS = {"orchestrator", "team-protocol", "stack-unity", "stack-dotnet", "domain-igaming",
                      "domain-f2p-liveops", "domain-multiplayer", "domain-pc-console"}


def run_case(case, timeout=240):
    cmd = ["claude", "-p", case["prompt"], "--plugin-dir", PLUGIN, "--output-format", "stream-json",
           "--verbose", "--max-turns", "10", "--allowedTools",
           "Agent,Skill,Read,Glob,Grep,Write,Edit,Bash(python *),PowerShell(python *),Bash(ls *),Bash(mkdir *)"]
    t0 = time.time()
    proc = subprocess.Popen(cmd, cwd=SANDBOX, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            text=True, encoding="utf-8", errors="replace")
    timer = threading.Timer(timeout, proc.kill)
    timer.start()
    routed, trail, plugin_ok = None, [], None
    try:
        for line in proc.stdout:
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "system" and ev.get("subtype") == "init":
                plugin_ok = not ev.get("plugin_errors") and any(
                    (p.get("name") if isinstance(p, dict) else p) == "studio" for p in ev.get("plugins", []))
            if ev.get("type") != "assistant" or ev.get("parent_tool_use_id"):
                continue
            for block in ev.get("message", {}).get("content", []):
                if block.get("type") != "tool_use":
                    continue
                name, inp = block.get("name"), block.get("input", {})
                if name in ("Agent", "Task"):
                    st = inp.get("subagent_type", "") or ""
                    trail.append(f"Agent:{st}")
                    routed = st.split(":", 1)[-1] if st else "general"
                elif name == "Skill":
                    sk = (inp.get("skill") or inp.get("command") or "").lstrip("/")
                    trail.append(f"Skill:{sk}")
                    short = sk.split(":", 1)[-1]
                    if short not in NON_ROUTING_SKILLS:
                        routed = short
                if routed:
                    break
            if routed:
                break
    finally:
        timer.cancel()
        if proc.poll() is None:
            proc.kill()
    ok = routed in case["expect"]
    return {"id": case["id"], "ok": ok, "routed": routed, "expect": case["expect"], "trail": trail,
            "plugin_loaded": plugin_ok, "secs": round(time.time() - t0, 1)}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    cases_path = os.path.join(ROOT, "tests", "trigger_cases.json")
    jobs = 4
    only = None
    if "--cases" in args:
        cases_path = args[args.index("--cases") + 1]
    if "--jobs" in args:
        jobs = int(args[args.index("--jobs") + 1])
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))
    cases = json.load(open(cases_path, encoding="utf-8"))
    if only:
        cases = [c for c in cases if c["id"] in only]
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(jobs) as ex:
        results = list(ex.map(run_case, cases))
    import shutil
    shutil.rmtree(os.path.join(SANDBOX, ".team"), ignore_errors=True)
    json.dump(results, open(os.path.join(OUT, "triggers.json"), "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    passed = sum(r["ok"] for r in results)
    for r in results:
        mark = "PASS" if r["ok"] else "FAIL"
        print(f"{mark} {r['id']:<28} routed={r['routed']!s:<30} expect={'/'.join(r['expect'])}"
              f"  trail={' > '.join(r['trail'])}  {r['secs']}s"
              + ("" if r["plugin_loaded"] in (True, None) else "  [PLUGIN NOT LOADED]"))
    print(f"\n{passed}/{len(results)} passed ({100 * passed // max(1, len(results))}%)")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
