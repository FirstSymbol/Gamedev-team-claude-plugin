#!/usr/bin/env python3
"""End-to-end team test: run /studio:feature on a fresh copy of the sandbox and check results.

Usage: python tests/run_e2e.py [--budget 15] [--feature "..."] [--keep]
Copies tests/sandbox -> tests/out/e2e (without bin/obj/.team), runs headless Claude with the
plugin, then checks: .team/ artifacts exist, agents spawned per role, dotnet build + test pass,
Unity-side files changed. Writes tests/out/e2e-report.json and prints a summary.
"""
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "studio")
SRC = os.path.join(ROOT, "tests", "sandbox")
OUT = os.path.join(ROOT, "tests", "out")
WORK = os.path.join(OUT, "e2e")
DEFAULT_FEATURE = (
    "Daily login bonus for the casino app. Server (.NET, server/Casino.Api): endpoint to claim the daily "
    "bonus, once per UTC day per player, streak days 1-7 with escalating coin rewards (config), idempotent "
    "claims, in-memory storage is fine for now, with xUnit tests. Unity client "
    "(client/CasinoClient/Assets/_Project): DailyBonus feature in its own asmdef - service calling the API, "
    "presenter logic in plain C# with EditMode tests, a MonoBehaviour view stub. Social casino coins only "
    "(no real money). Keep it small.")
ALLOWED = ["Read", "Write", "Edit", "Glob", "Grep", "Agent", "Skill", "TodoWrite",
           "Bash(dotnet *)", "Bash(python *)", "Bash(ls *)", "Bash(mkdir *)", "Bash(cat *)", "Bash(git *)"]


def copy_sandbox():
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    shutil.copytree(SRC, WORK, ignore=shutil.ignore_patterns("bin", "obj", ".team", "TestResults"))


def run(cmd, cwd, timeout=900):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=timeout)
    return p.returncode, (p.stdout + p.stderr)[-3000:]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    budget = args[args.index("--budget") + 1] if "--budget" in args else "15"
    feature = args[args.index("--feature") + 1] if "--feature" in args else DEFAULT_FEATURE
    os.makedirs(OUT, exist_ok=True)
    copy_sandbox()
    log_path = os.path.join(OUT, "e2e-stream.jsonl")
    cmd = ["claude", "-p", f"/studio:feature {feature}", "--plugin-dir", PLUGIN,
           "--output-format", "stream-json", "--verbose", "--max-budget-usd", str(budget),
           "--allowedTools", ",".join(ALLOWED)]
    t0 = time.time()
    with open(log_path, "w", encoding="utf-8") as log:
        proc = subprocess.run(cmd, cwd=WORK, stdout=log, stderr=subprocess.STDOUT, timeout=5400)
    secs = round(time.time() - t0)

    agents, skills, result, usage, cost = [], [], None, {}, None
    for line in open(log_path, encoding="utf-8", errors="replace"):
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            for b in ev.get("message", {}).get("content", []):
                if b.get("type") == "tool_use" and b.get("name") in ("Agent", "Task"):
                    agents.append((b["input"].get("subagent_type"), bool(ev.get("parent_tool_use_id"))))
                if b.get("type") == "tool_use" and b.get("name") == "Skill":
                    skills.append(b["input"].get("skill"))
        if ev.get("type") == "result":
            result, usage, cost = ev.get("result"), ev.get("modelUsage", {}), ev.get("total_cost_usd")
            stats = ev.get("subagent_stats")

    team = os.path.join(WORK, ".team")
    team_files = []
    for dp, _, fns in os.walk(team):
        team_files += [os.path.relpath(os.path.join(dp, f), team).replace("\\", "/") for f in fns]
    build_rc, build_out = run(["dotnet", "build", "Casino.sln", "-v", "q", "-nologo"], WORK)
    test_rc, test_out = run(["dotnet", "test", "Casino.sln", "-v", "q", "-nologo"], WORK)
    unity_cs = []
    for dp, _, fns in os.walk(os.path.join(WORK, "client")):
        unity_cs += [os.path.relpath(os.path.join(dp, f), WORK) for f in fns
                     if f.endswith((".cs", ".asmdef")) and "DailyBonus" in os.path.join(dp, f) + f]
    checks = {
        "claude_exit_ok": proc.returncode == 0,
        "team_dir_has_specs": any(f.startswith("specs/") for f in team_files),
        "team_dir_has_reports": any(f.startswith("reports/") for f in team_files),
        "status_board_exists": "status.md" in team_files,
        "spawned_backend": any(a and a.endswith("dotnet-backend-developer") for a, _ in agents),
        "spawned_unity": any(a and a.endswith("unity-developer") for a, _ in agents),
        "spawned_qa_or_review": any(a and a.endswith(("qa-engineer", "code-reviewer")) for a, _ in agents),
        "dotnet_build_ok": build_rc == 0,
        "dotnet_test_ok": test_rc == 0,
        "unity_feature_files": len(unity_cs) > 0,
    }
    report = {"checks": checks, "agents": agents, "skills": skills, "team_files": sorted(team_files),
              "unity_files": unity_cs, "secs": secs, "cost_usd": cost,
              "model_usage": {m: {k: v for k, v in u.items() if k in ("inputTokens", "outputTokens",
                              "cacheReadInputTokens", "cacheCreationInputTokens", "costUSD")}
                              for m, u in (usage or {}).items()},
              "build_tail": build_out[-1200:], "test_tail": test_out[-1200:], "result": (result or "")[-3000:]}
    json.dump(report, open(os.path.join(OUT, "e2e-report.json"), "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    for k, v in checks.items():
        print(f"{'PASS' if v else 'FAIL'} {k}")
    print(f"agents: {[a for a, _ in agents]}")
    print(f"time {secs}s, cost ${cost}")
    for m, u in report["model_usage"].items():
        print(f"  {m}: {u}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
