#!/usr/bin/env python3
"""Compact summary of the .team/ blackboard (brief, open board rows, open risks, ADRs, handoffs, lessons).

Usage: python team_status.py [project_root] [--init]
--init creates the .team/ skeleton (brief.md, status.md, risks.md, folders) if missing.
"""
import os
import re
import subprocess
import sys

SKELETON = {
    "brief.md": "# Brief\nGoal: <one sentence>\nScope: <in>\nNon-goals: <out>\nConstraints: <tech/platform/time/budget/regulatory>\nStakeholders: <human owner>\nSuccess metrics: <KPIs>\n",
    "status.md": "# Status board\n| ID | Task | Owner | State | Artifact |\n|---|---|---|---|---|\n",
    "risks.md": "# Risk register\n| ID | Risk | P(1-5) | I(1-5) | Owner | Mitigation | State |\n|---|---|---|---|---|---|---|\n",
}
DIRS = ["decisions", "specs", "handoffs", "reports", "lessons"]
DONE = {"done", "closed", "cancelled", "canceled", "resolved", "accepted", "retired"}


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def git(root, *args):
    try:
        r = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def context_line(root, team):
    meta = read(os.path.join(team, "context", "meta.md"))
    if not meta:
        return "- Context cache: none (existing codebase? run /studio:onboard)"
    m = re.search(r"Commit:\s*([0-9a-f]{7,40})", meta)
    d = re.search(r"Date:\s*([\d-]+)", meta)
    line = f"- Context cache: {d.group(1) if d else '?'}"
    if m:
        behind = git(root, "rev-list", "--count", f"{m.group(1)}..HEAD")
        changed = git(root, "diff", "--name-only", f"{m.group(1)}..HEAD")
        n = len(changed.splitlines()) if changed else 0
        if behind:
            line += f", {behind} commits / {n} files behind HEAD"
            if int(behind) >= 30 or n >= 50:
                line += " -> STALE: run /studio:onboard --refresh"
        else:
            line += f" (commit {m.group(1)[:8]} not found)"
    return line


def table_rows(text):
    rows = []
    for line in text.splitlines():
        if line.startswith("|") and not re.match(r"^\|\s*-", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append(cells)
    return rows[1:] if rows else []


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = os.path.abspath(args[0] if args else ".")
    team = os.path.join(root, ".team")
    if "--init" in sys.argv:
        os.makedirs(team, exist_ok=True)
        for d in DIRS:
            os.makedirs(os.path.join(team, d), exist_ok=True)
        for fn, body in SKELETON.items():
            fp = os.path.join(team, fn)
            if not os.path.exists(fp):
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(body)
        print(f"Initialized {team}")
    if not os.path.isdir(team):
        print(f"No .team/ in {root}. Run with --init to create it.")
        return 1
    out = [f"## Team status: {team}"]
    brief = read(os.path.join(team, "brief.md")).strip().splitlines()
    if brief:
        out.append("- Brief: " + " | ".join(l.strip() for l in brief[1:7] if l.strip())[:600])
    out.append(context_line(root, team))
    rows = table_rows(read(os.path.join(team, "status.md")))
    open_rows = [r for r in rows if len(r) >= 4 and r[3].lower() not in DONE]
    out.append(f"- Board: {len(rows)} tasks, {len(open_rows)} open")
    for r in open_rows[:30]:
        out.append("  - " + " | ".join(r[:5]))
    risks = table_rows(read(os.path.join(team, "risks.md")))
    open_risks = [r for r in risks if len(r) >= 7 and r[6].lower() not in DONE]

    def score(r):
        try:
            return int(r[2]) * int(r[3])
        except ValueError:
            return 0
    open_risks.sort(key=score, reverse=True)
    out.append(f"- Risks: {len(risks)} total, {len(open_risks)} open (top by PxI):")
    for r in open_risks[:10]:
        out.append(f"  - {r[0]} [{score(r)}] {r[1]} -> {r[4]}")
    ddir = os.path.join(team, "decisions")
    adrs = sorted(f for f in os.listdir(ddir) if f.endswith(".md")) if os.path.isdir(ddir) else []
    if adrs:
        out.append(f"- ADRs ({len(adrs)}):")
        for a in adrs[-15:]:
            txt = read(os.path.join(ddir, a))
            st = re.search(r"Status:\s*([\w -]+)", txt)
            out.append(f"  - {a} ({st.group(1).strip() if st else '?'})")
    hdir = os.path.join(team, "handoffs")
    hs = sorted(f for f in os.listdir(hdir) if f.endswith(".md")) if os.path.isdir(hdir) else []
    if hs:
        out.append(f"- Handoffs ({len(hs)}), latest: " + ", ".join(hs[-8:]))
    ldir = os.path.join(team, "lessons")
    if os.path.isdir(ldir):
        counts = []
        for fn in sorted(os.listdir(ldir)):
            if fn.endswith(".md"):
                n = sum(1 for l in read(os.path.join(ldir, fn)).splitlines() if l.startswith("| L-"))
                if n:
                    counts.append(f"{fn[:-3]}={n}")
        if counts:
            out.append("- Lessons: " + ", ".join(counts) + " (curate with /studio:retro)")
    for sub in ("specs", "reports"):
        sdir = os.path.join(team, sub)
        files = []
        if os.path.isdir(sdir):
            for dp, _, fns in os.walk(sdir):
                files += [os.path.relpath(os.path.join(dp, f), team).replace("\\", "/") for f in fns]
        if files:
            out.append(f"- {sub} ({len(files)}): " + ", ".join(sorted(files)[-15:]))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
