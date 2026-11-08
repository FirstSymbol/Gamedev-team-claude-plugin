#!/usr/bin/env python3
"""Studio lessons log: mistakes the team hit, turned into rules so they are not repeated.

Stores one markdown table per role:
  project: <root>/.team/lessons/<role>.md          (this project only)
  global:  ~/.claude/studio/lessons/<role>.md      (all projects; promoted by /studio:retro)
Role "common" holds lessons for every role.

Usage:
  python lessons.py list <root> --role <role> [--tags a,b] [--limit 25]
  python lessons.py add  <root> --role <role> --sev <S1|S2|S3> --tags a,b \
                         --rule "<do/don't X when Y>" --evidence "<path:line, test, ADR>" [--global]
  python lessons.py bump <root> --id <L-NNN> --role <role> [--global]
  python lessons.py promote <root> --id <L-NNN> --role <role>
  python lessons.py stats <root>
"""
import argparse
import datetime
import os
import re
import sys

HEADER = ("# Lessons: {role}\n"
          "| ID | Date | Sev | Tags | Rule | Evidence | Hits |\n"
          "|---|---|---|---|---|---|---|\n")
GLOBAL_DIR = os.path.join(os.path.expanduser("~"), ".claude", "studio", "lessons")
MAX_RULE = 220


def store(root, glob):
    return GLOBAL_DIR if glob else os.path.join(os.path.abspath(root), ".team", "lessons")


def path_for(d, role):
    return os.path.join(d, f"{role}.md")


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def rows(text):
    out = []
    for line in text.splitlines():
        if line.startswith("| L-") or line.startswith("| G-"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 7:
                out.append(cells[:7])
    return out


def write_rows(p, role, rs):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(HEADER.format(role=role))
        for r in rs:
            f.write("| " + " | ".join(r) + " |\n")


def all_ids(d):
    ids = []
    if os.path.isdir(d):
        for fn in os.listdir(d):
            if fn.endswith(".md"):
                ids += [r[0] for r in rows(read(os.path.join(d, fn)))]
    return ids


def next_id(d, prefix):
    nums = [int(m.group(1)) for i in all_ids(d) if (m := re.match(prefix + r"-(\d+)$", i))]
    return f"{prefix}-{(max(nums) + 1 if nums else 1):03d}"


def clean(s):
    return " ".join(s.replace("|", "/").split())


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower())


def cmd_list(a):
    want = {t.strip().lower() for t in (a.tags or "").split(",") if t.strip()}
    found = []
    for scope, d in (("global", GLOBAL_DIR), ("project", store(a.root, False))):
        for role in dict.fromkeys(["common", a.role]):
            for r in rows(read(path_for(d, role))):
                tags = {t.strip().lower() for t in r[3].split(",")}
                if want and not (want & tags) and role != "common":
                    continue
                found.append((scope, role, r))
    if not found:
        print(f"No lessons for {a.role}.")
        return 0

    def key(x):
        r = x[2]
        hits = int(r[6]) if r[6].isdigit() else 1
        return (r[2], -hits)
    found.sort(key=key)
    print(f"## Lessons for {a.role} ({len(found)}; apply the relevant ones)")
    for scope, role, r in found[: a.limit]:
        print(f"- {r[0]} [{r[2]}|{r[3]}|x{r[6]}] {r[4]}")
    if len(found) > a.limit:
        print(f"- ... {len(found) - a.limit} more; narrow with --tags")
    return 0


def cmd_add(a):
    rule = clean(a.rule)
    if not rule:
        print("ERROR: --rule is required")
        return 1
    if len(rule) > MAX_RULE:
        print(f"ERROR: rule {len(rule)} chars > {MAX_RULE}; make it one actionable sentence")
        return 1
    d = store(a.root, a.glob)
    p = path_for(d, a.role)
    rs = rows(read(p))
    for r in rs:
        if norm(r[4]) == norm(rule):
            r[6] = str(int(r[6]) + 1 if r[6].isdigit() else 2)
            write_rows(p, a.role, rs)
            print(f"DUPLICATE: bumped {r[0]} to x{r[6]}")
            return 0
    lid = next_id(d, "G" if a.glob else "L")
    tags = ",".join(t.strip().lower() for t in (a.tags or "").split(",") if t.strip()) or "-"
    rs.append([lid, datetime.date.today().isoformat(), a.sev, tags, rule,
               clean(a.evidence or "-"), "1"])
    write_rows(p, a.role, rs)
    print(f"ADDED {lid} -> {p}")
    return 0


def cmd_bump(a):
    d = store(a.root, a.glob)
    p = path_for(d, a.role)
    rs = rows(read(p))
    for r in rs:
        if r[0] == a.id:
            r[6] = str(int(r[6]) + 1 if r[6].isdigit() else 2)
            write_rows(p, a.role, rs)
            print(f"BUMPED {a.id} to x{r[6]}")
            return 0
    print(f"ERROR: {a.id} not found in {p}")
    return 1


def cmd_promote(a):
    src = path_for(store(a.root, False), a.role)
    rs = rows(read(src))
    hit = next((r for r in rs if r[0] == a.id), None)
    if not hit:
        print(f"ERROR: {a.id} not found in {src}")
        return 1
    gp = path_for(GLOBAL_DIR, a.role)
    grs = rows(read(gp))
    if any(norm(g[4]) == norm(hit[4]) for g in grs):
        print("Already global; nothing to do")
        return 0
    gid = next_id(GLOBAL_DIR, "G")
    grs.append([gid, datetime.date.today().isoformat(), hit[2], hit[3], hit[4],
                f"from {a.id}", hit[6]])
    write_rows(gp, a.role, grs)
    hit[5] = f"{hit[5]}; promoted {gid}"
    write_rows(src, a.role, rs)
    print(f"PROMOTED {a.id} -> {gid} ({gp})")
    return 0


def cmd_stats(a):
    for scope, d in (("project", store(a.root, False)), ("global", GLOBAL_DIR)):
        if not os.path.isdir(d):
            print(f"{scope}: none")
            continue
        parts = []
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".md"):
                rs = rows(read(os.path.join(d, fn)))
                rep = sum(1 for r in rs if r[6].isdigit() and int(r[6]) > 1)
                parts.append(f"{fn[:-3]}={len(rs)}" + (f"({rep} recurring)" if rep else ""))
        print(f"{scope}: " + (", ".join(parts) or "none"))
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("list", "add", "bump", "promote", "stats"):
        s = sub.add_parser(name)
        s.add_argument("root", nargs="?", default=".")
        if name != "stats":
            s.add_argument("--role", required=True)
        if name == "list":
            s.add_argument("--tags")
            s.add_argument("--limit", type=int, default=25)
        if name == "add":
            s.add_argument("--sev", choices=["S1", "S2", "S3"], default="S2")
            s.add_argument("--tags")
            s.add_argument("--rule", required=True)
            s.add_argument("--evidence")
        if name in ("bump", "promote"):
            s.add_argument("--id", required=True)
        if name in ("add", "bump"):
            s.add_argument("--global", dest="glob", action="store_true")
    a = ap.parse_args()
    return {"list": cmd_list, "add": cmd_add, "bump": cmd_bump,
            "promote": cmd_promote, "stats": cmd_stats}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
