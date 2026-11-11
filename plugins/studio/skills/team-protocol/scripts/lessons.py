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
  python lessons.py delete <root> --id <ID> --role <role> [--global] [--reason "<why>"]
  python lessons.py move   <root> --id <ID> --role <role> --to <role> [--global]
  python lessons.py export <dir> [--replace]   global store -> <dir> (backup / git sync)
  python lessons.py import <dir>               <dir> -> global store (new machine / teammate)
  python lessons.py pending <source root>                 source rows not yet harvested (or Hits grew)
  python lessons.py mark <source root> --id L-1,L-2 --outcome <embedded|global|project|covered|dropped> [--ref G-012]
export/import merge by rule text (Hits = max, never summed), so repeated syncs are idempotent.
--replace makes <dir> an exact copy of the global store (use after curation deleted rows).
Harvest index (~/.claude/studio/lessons/_harvested.md, synced by export/import): which source
project rows a retro already processed. `list` in that project hides rows carried elsewhere
(embedded/global/covered/dropped) until their Hits grow; `pending` shows only unprocessed rows.
Projects are keyed by an opaque hash (p:<sha256[:16]>) of the git remote without login, else of
the folder path, so the synced index never holds paths, logins or repo names. Old raw keys are
converted on read. Evidence in global rows must not name client projects, paths or commits.
"""
import argparse
import datetime
import hashlib
import os
import re
import subprocess
import sys

HEADER = ("# Lessons: {role}\n"
          "| ID | Date | Sev | Tags | Rule | Evidence | Hits |\n"
          "|---|---|---|---|---|---|---|\n")
GLOBAL_DIR = os.path.join(os.path.expanduser("~"), ".claude", "studio", "lessons")
MAX_RULE = 220
INDEX = "_harvested.md"
INDEX_HEADER = ("# Harvest index (written by team-coach via `lessons.py mark`)\n"
                "| Project | Role | ID | Hits | Outcome | Ref | Date |\n"
                "|---|---|---|---|---|---|---|\n")
OUTCOMES = ("embedded", "global", "project", "covered", "dropped")
HIDDEN = {"embedded", "global", "covered", "dropped"}


def store(root, glob):
    return GLOBAL_DIR if glob else os.path.join(os.path.abspath(root), ".team", "lessons")


def path_for(d, role):
    return os.path.join(d, f"{role}.md")


def is_role_file(fn):
    return fn.endswith(".md") and fn.lower() != "readme.md" and not fn.startswith("_")


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
            if is_role_file(fn):
                ids += [r[0] for r in rows(read(os.path.join(d, fn)))]
    return ids


def next_id(d, prefix):
    return next_id_from(all_ids(d), prefix)


def clean(s):
    return " ".join(s.replace("|", "/").split())


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower())


def hkey(raw):
    """Opaque project key for the git-synced index: never store paths, logins or repo URLs."""
    raw = raw.strip()
    if raw.startswith("p:"):
        return raw
    if raw.startswith("git:"):
        raw = "git:" + re.sub(r"^[^@/]+@", "", raw[4:])
    return "p:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def raw_project_keys(root):
    root = os.path.abspath(root)
    keys = [root.replace("\\", "/").rstrip("/").lower()]
    try:
        r = subprocess.run(["git", "-C", root, "remote", "get-url", "origin"],
                           capture_output=True, text=True, timeout=10)
        url = r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        url = ""
    if url:
        url = re.sub(r"^(https?://|ssh://)", "", url.lower())
        url = re.sub(r"^[^@/]+@", "", url).replace(":", "/")
        keys.insert(0, "git:" + re.sub(r"\.git$", "", url).rstrip("/"))
    return keys


def project_keys(root):
    return {hkey(k) for k in raw_project_keys(root)}


def project_key(root):
    """Primary key: git remote (stable across machines) if any, else the folder path."""
    return hkey(raw_project_keys(root)[0])


def index_rows(d=None):
    out = []
    for line in read(os.path.join(d or GLOBAL_DIR, INDEX)).splitlines():
        if line.startswith("| ") and not line.startswith("| Project") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 7:
                out.append([hkey(cells[0])] + cells[1:7])
    return out


def write_index(rs, d=None):
    d = d or GLOBAL_DIR
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, INDEX), "w", encoding="utf-8") as f:
        f.write(INDEX_HEADER)
        for r in sorted(rs, key=lambda x: (x[0], x[1], x[2])):
            f.write("| " + " | ".join(r) + " |\n")


def harvested(root):
    keys = project_keys(root)
    return {(r[1], r[2]): r for r in index_rows() if r[0] in keys}


def hits(r):
    return int(r[6]) if r[6].isdigit() else 1


def is_hidden(entry, row):
    return entry is not None and entry[4] in HIDDEN and hits(row) <= (int(entry[3]) if entry[3].isdigit() else 1)


def cmd_list(a):
    done = harvested(a.root)
    want = {t.strip().lower() for t in (a.tags or "").split(",") if t.strip()}
    found = []
    for scope, d in (("global", GLOBAL_DIR), ("project", store(a.root, False))):
        for role in dict.fromkeys(["common", a.role]):
            for r in rows(read(path_for(d, role))):
                tags = {t.strip().lower() for t in r[3].split(",")}
                if role == "common" and a.no_common and a.role != "common":
                    continue
                if want and not (want & tags) and role != "common":
                    continue
                if scope == "project" and is_hidden(done.get((role, r[0])), r):
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
            ev = clean(a.evidence or "")
            if ev and ev not in r[5]:
                r[5] = ev if r[5] == "-" else f"{r[5]}; {ev}"
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


def cmd_delete(a):
    p = path_for(store(a.root, a.glob), a.role)
    rs = rows(read(p))
    keep = [r for r in rs if r[0] != a.id]
    if len(keep) == len(rs):
        print(f"ERROR: {a.id} not found in {p}")
        return 1
    write_rows(p, a.role, keep)
    print(f"DELETED {a.id} from {a.role}" + (f" ({a.reason})" if a.reason else ""))
    return 0


def cmd_move(a):
    d = store(a.root, a.glob)
    src = path_for(d, a.role)
    rs = rows(read(src))
    hit = next((r for r in rs if r[0] == a.id), None)
    if not hit:
        print(f"ERROR: {a.id} not found in {src}")
        return 1
    dst = path_for(d, a.to)
    drs = rows(read(dst))
    same = next((x for x in drs if norm(x[4]) == norm(hit[4])), None)
    if same:
        same[6] = str((int(same[6]) if same[6].isdigit() else 1) + (int(hit[6]) if hit[6].isdigit() else 1))
    else:
        drs.append(hit)
    write_rows(dst, a.to, drs)
    write_rows(src, a.role, [r for r in rs if r[0] != a.id])
    print(f"MOVED {a.id} {a.role} -> {a.to}" + (" (merged)" if same else ""))
    return 0


def source_rows(root):
    d = store(root, False)
    out = []
    if os.path.isdir(d):
        for fn in sorted(os.listdir(d)):
            if is_role_file(fn):
                out += [(fn[:-3], r) for r in rows(read(os.path.join(d, fn)))]
    return out


def cmd_pending(a):
    done = harvested(a.root)
    allr = source_rows(a.root)
    todo = []
    for role, r in allr:
        e = done.get((role, r[0]))
        if e is None:
            todo.append(("new", role, r))
        elif hits(r) > (int(e[3]) if e[3].isdigit() else 1):
            todo.append((f"hits {e[3]}->{r[6]}, was {e[4]}", role, r))
    print(f"## Pending in {a.root}: {len(todo)} of {len(allr)} rows ({len(allr) - len(todo)} already harvested)")
    for why, role, r in todo:
        print(f"- {role} {r[0]} [{r[2]}|{r[3]}|x{r[6]}] ({why}) {r[4]}")
    return 0


def cmd_mark(a):
    if a.outcome not in OUTCOMES:
        print(f"ERROR: --outcome must be one of {', '.join(OUTCOMES)}")
        return 1
    keys = project_keys(a.root)
    key = project_key(a.root)
    src = [(role, r) for role, r in source_rows(a.root) if not a.role or role == a.role]
    idx = [r for r in index_rows()]
    today = datetime.date.today().isoformat()
    marked = 0
    for lid in [x.strip() for x in a.id.split(",") if x.strip()]:
        hits = [(role, r) for role, r in src if r[0] == lid]
        if not hits:
            print(f"ERROR: {lid} not found in {store(a.root, False)}" + (f" for {a.role}" if a.role else ""))
            return 1
        if len(hits) > 1:
            print(f"ERROR: {lid} exists in roles {', '.join(h[0] for h in hits)}; pass --role")
            return 1
        role, r = hits[0]
        idx = [x for x in idx if not (x[0] in keys and x[1] == role and x[2] == lid)]
        idx.append([key, role, lid, r[6], a.outcome, clean(a.ref or "-"), today])
        marked += 1
    write_index(idx)
    print(f"MARKED {marked} row(s) as {a.outcome} for {key}")
    return 0


def merge_index(src, dst, replace=False):
    srows = index_rows(src)
    if not srows and not replace:
        return
    merged = {} if replace else {(r[0], r[1], r[2]): r for r in index_rows(dst)}
    for r in srows:
        k = (r[0], r[1], r[2])
        if k not in merged or r[6] >= merged[k][6]:
            merged[k] = r
    if merged or os.path.exists(os.path.join(dst, INDEX)):
        write_index(list(merged.values()), dst)


def merge_dir(src, dst, replace=False):
    if not os.path.isdir(src):
        print(f"Nothing to sync: {src} does not exist")
        return 0
    os.makedirs(dst, exist_ok=True)
    taken = set(all_ids(dst)) if not replace else set()
    added = updated = 0
    for fn in sorted(os.listdir(src)):
        if not is_role_file(fn):
            continue
        role = fn[:-3]
        srows = rows(read(os.path.join(src, fn)))
        dp = path_for(dst, role)
        drows = [] if replace else rows(read(dp))
        for r in srows:
            r = list(r)
            same = next((d for d in drows if norm(d[4]) == norm(r[4])), None)
            if same:
                h = max(int(x) if x.isdigit() else 1 for x in (same[6], r[6]))
                if str(h) != same[6]:
                    same[6] = str(h)
                    updated += 1
                continue
            if r[0] in taken:
                r[0] = next_id_from(taken, "G")
            taken.add(r[0])
            drows.append(r)
            added += 1
        write_rows(dp, role, drows)
    if replace:
        keep = {fn for fn in os.listdir(src) if is_role_file(fn)}
        for fn in os.listdir(dst):
            if is_role_file(fn) and fn not in keep:
                os.remove(os.path.join(dst, fn))
    merge_index(src, dst, replace)
    print(f"SYNC {src} -> {dst}: {added} added, {updated} updated" + (" (replace)" if replace else ""))
    return 0


def next_id_from(ids, prefix):
    nums = [int(m.group(1)) for i in ids if (m := re.match(prefix + r"-(\d+)$", i))]
    return f"{prefix}-{(max(nums) + 1 if nums else 1):03d}"


def cmd_export(a):
    return merge_dir(GLOBAL_DIR, os.path.abspath(a.root), a.replace)


def cmd_import(a):
    return merge_dir(os.path.abspath(a.root), GLOBAL_DIR)


def cmd_stats(a):
    for scope, d in (("project", store(a.root, False)), ("global", GLOBAL_DIR)):
        if not os.path.isdir(d):
            print(f"{scope}: none")
            continue
        parts = []
        for fn in sorted(os.listdir(d)):
            if is_role_file(fn):
                rs = rows(read(os.path.join(d, fn)))
                rep = sum(1 for r in rs if r[6].isdigit() and int(r[6]) > 1)
                parts.append(f"{fn[:-3]}={len(rs)}" + (f"({rep} recurring)" if rep else ""))
        print(f"{scope}: " + (", ".join(parts) or "none"))
    done = harvested(a.root)
    if done:
        print(f"harvest index for this project: {len(done)} rows processed by retro")
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("list", "add", "bump", "promote", "stats", "export", "import", "delete", "move",
                 "pending", "mark"):
        s = sub.add_parser(name)
        s.add_argument("root", nargs="?", default=".")
        if name not in ("stats", "export", "import", "pending", "mark"):
            s.add_argument("--role", required=True)
        if name == "mark":
            s.add_argument("--id", required=True)
            s.add_argument("--outcome", required=True)
            s.add_argument("--ref")
            s.add_argument("--role", help="required when the same ID exists in several roles")
        if name == "export":
            s.add_argument("--replace", action="store_true")
        if name == "list":
            s.add_argument("--tags")
            s.add_argument("--limit", type=int, default=25)
            s.add_argument("--no-common", dest="no_common", action="store_true")
        if name == "add":
            s.add_argument("--sev", choices=["S1", "S2", "S3"], default="S2")
            s.add_argument("--tags")
            s.add_argument("--rule", required=True)
            s.add_argument("--evidence")
        if name in ("bump", "promote", "delete", "move"):
            s.add_argument("--id", required=True)
        if name == "delete":
            s.add_argument("--reason")
        if name == "move":
            s.add_argument("--to", required=True)
        if name in ("add", "bump", "delete", "move"):
            s.add_argument("--global", dest="glob", action="store_true")
    a = ap.parse_args()
    return {"list": cmd_list, "add": cmd_add, "bump": cmd_bump,
            "promote": cmd_promote, "stats": cmd_stats,
            "export": cmd_export, "import": cmd_import,
            "delete": cmd_delete, "move": cmd_move,
            "pending": cmd_pending, "mark": cmd_mark}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
