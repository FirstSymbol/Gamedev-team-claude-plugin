#!/usr/bin/env python3
"""Validate the studio plugin against AUTHORING.md budgets and integrity rules.

Usage: python tests/validate_pack.py [plugin_dir] [--strict] [--quiet]
Exit 1 on errors (or warnings with --strict).
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "studio")
ROSTER = """producer product-manager tech-lead-architect lead-game-designer qa-lead
business-analyst system-analyst data-analyst game-designer level-designer narrative-designer
economy-monetization-designer ux-ui-designer art-director technical-artist unity-developer
dotnet-backend-developer frontend-developer multiplayer-network-engineer devops-sre-engineer
security-engineer code-reviewer qa-engineer release-platform-manager marketing-manager
liveops-manager compliance-advisor technical-writer""".split()
SHARED = ["team-protocol", "orchestrator", "stack-unity", "stack-dotnet", "domain-igaming",
          "domain-f2p-liveops", "domain-multiplayer", "domain-pc-console"]
WORKFLOWS = ["kickoff", "feature", "bugfix", "release", "status", "risk-review"]
MODELS = {"opus", "sonnet", "haiku", "inherit", "fable"}
TOOLS = {"Read", "Write", "Edit", "Glob", "Grep", "Bash", "PowerShell", "Skill", "WebSearch",
         "WebFetch", "Agent", "NotebookEdit", "TodoWrite"}
LEADS = {"producer", "product-manager", "tech-lead-architect", "lead-game-designer", "qa-lead"}
CYR = re.compile(r"[Ѐ-ӿ]")

errors, warnings = [], []


def err(m):
    errors.append(m)


def warn(m):
    warnings.append(m)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def frontmatter(text, path):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        err(f"{path}: missing YAML frontmatter")
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if mm:
            k, v = mm.group(1), mm.group(2).strip()
            if v[:1] in ("'", '"'):
                v = v[1:-1] if len(v) > 1 and v[-1] == v[0] else v
            elif ": " in v or " #" in v:
                err(f"{path}: frontmatter '{k}' has unquoted ': ' or ' #' (YAML breaks; quote it)")
            fm[k] = v
    return fm, text[m.end():]


def parse_list(v):
    v = v.strip()
    if v.startswith("["):
        v = v.strip("[]")
    return [x.strip().strip("'\"") for x in v.split(",") if x.strip()]


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def main():
    strict = "--strict" in sys.argv
    quiet = "--quiet" in sys.argv
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sdir = os.path.join(PLUGIN, "skills")
    adir = os.path.join(PLUGIN, "agents")
    skills = sorted(d for d in os.listdir(sdir) if os.path.isdir(os.path.join(sdir, d)))
    agents = sorted(f[:-3] for f in os.listdir(adir) if f.endswith(".md"))
    listing_chars = 0
    skill_meta = {}

    for s in skills:
        p = os.path.join(sdir, s, "SKILL.md")
        if not os.path.isfile(p):
            err(f"skills/{s}: no SKILL.md")
            continue
        text = read(p)
        fm, body = frontmatter(text, rel(p))
        skill_meta[s] = fm
        if fm.get("name") != s:
            err(f"{rel(p)}: name '{fm.get('name')}' != folder '{s}'")
        desc = fm.get("description", "")
        hidden = fm.get("disable-model-invocation", "").lower() == "true"
        if not desc:
            err(f"{rel(p)}: empty description")
        if not hidden:
            listing_chars += len(s) + len(desc) + len(fm.get("when_to_use", ""))
            if len(desc) > 250:
                err(f"{rel(p)}: description {len(desc)} chars > 250")
            elif len(desc) > 170:
                warn(f"{rel(p)}: description {len(desc)} chars > 170")
        lines = text.count("\n") + 1
        lim = 160 if s in WORKFLOWS or s in ("orchestrator",) else 130
        if lines > lim + 30:
            err(f"{rel(p)}: {lines} lines > {lim + 30}")
        elif lines > lim:
            warn(f"{rel(p)}: {lines} lines > {lim}")
        if len(text) > 9000:
            err(f"{rel(p)}: {len(text)} chars > 9000")
        elif len(text) > 7000:
            warn(f"{rel(p)}: {len(text)} chars > 7000")
        # referenced local files exist
        for ref in set(re.findall(r"\b((?:references|templates|scripts)/[\w./-]+\.(?:md|py|json|cs|yml|yaml|txt))", body)):
            if not os.path.isfile(os.path.join(sdir, s, ref)) and                     not os.path.isfile(os.path.join(sdir, "team-protocol", ref)):
                err(f"{rel(p)}: references missing file {ref}")
        for sub in ("references", "templates"):
            d = os.path.join(sdir, s, sub)
            if os.path.isdir(d):
                for fn in os.listdir(d):
                    if f"{sub}/{fn}" not in body:
                        warn(f"skills/{s}/{sub}/{fn}: not listed in SKILL.md (unreachable)")
                    fp = os.path.join(d, fn)
                    t = read(fp)
                    n = t.count("\n") + 1
                    if sub == "references":
                        if n > 450:
                            err(f"{rel(fp)}: {n} lines > 450")
                        elif n > 350:
                            warn(f"{rel(fp)}: {n} lines > 350")
                        if "## Sources" not in t:
                            warn(f"{rel(fp)}: no '## Sources' section")
        # cross-skill refs
        for x in set(re.findall(r"studio:([a-z0-9-]+)", body)):
            if x not in skills and x not in agents:
                err(f"{rel(p)}: unknown studio:{x}")
        # handoff targets
        hm = re.search(r"## Handoffs\n(.*?)(\n## |\Z)", body, re.S)
        if hm:
            for tgt in re.findall(r"→\s*([a-z][a-z-]+)", hm.group(1)):
                if tgt not in ROSTER and tgt not in ("orchestrator", "human", "user"):
                    err(f"{rel(p)}: handoff to unknown role '{tgt}'")

    # cyrillic scan
    for dp, _, fns in os.walk(PLUGIN):
        for fn in fns:
            if fn.endswith((".md", ".json", ".py")) and fn != "README.ru.md":
                fp = os.path.join(dp, fn)
                t = read(fp)
                if CYR.search(t):
                    line = next(i for i, l in enumerate(t.splitlines(), 1) if CYR.search(l))
                    warn(f"{rel(fp)}:{line}: Cyrillic text (token cost)")

    orch = read(os.path.join(sdir, "orchestrator", "SKILL.md")) if "orchestrator" in skills else ""
    agent_listing = 0
    for a in agents:
        p = os.path.join(adir, a + ".md")
        text = read(p)
        fm, body = frontmatter(text, rel(p))
        if fm.get("name") != a:
            err(f"{rel(p)}: name '{fm.get('name')}' != file '{a}'")
        desc = fm.get("description", "")
        agent_listing += len(a) + len(desc)
        if len(desc) > 300:
            err(f"{rel(p)}: description {len(desc)} > 300")
        elif len(desc) > 210:
            warn(f"{rel(p)}: description {len(desc)} > 210")
        if fm.get("model") not in MODELS:
            err(f"{rel(p)}: model '{fm.get('model')}' invalid")
        if a in LEADS and fm.get("model") != "opus":
            warn(f"{rel(p)}: lead not on opus")
        tools = parse_list(fm.get("tools", ""))
        bad = [t for t in tools if t not in TOOLS]
        if bad:
            err(f"{rel(p)}: unknown tools {bad}")
        if a in LEADS and "Agent" not in tools:
            warn(f"{rel(p)}: lead without Agent tool")
        for sk in parse_list(fm.get("skills", "")):
            if sk not in skills:
                err(f"{rel(p)}: preloads unknown skill '{sk}'")
            elif skill_meta.get(sk, {}).get("disable-model-invocation", "").lower() == "true":
                err(f"{rel(p)}: preloads '{sk}' which has disable-model-invocation")
        if "team-protocol" not in parse_list(fm.get("skills", "")):
            err(f"{rel(p)}: does not preload team-protocol")
        if body.count("\n") > 32:
            warn(f"{rel(p)}: body {body.count(chr(10))} lines > 32")
        if a not in ROSTER:
            err(f"{rel(p)}: agent not in roster")
        if orch and f"| {a}" not in orch and f" {a} " not in orch:
            err(f"{rel(p)}: agent missing from orchestrator routing table")
        for x in set(re.findall(r"studio:([a-z0-9-]+)", body)):
            if x not in skills and x not in agents:
                err(f"{rel(p)}: unknown studio:{x}")

    missing_agents = [r for r in ROSTER if r not in agents]
    missing_skills = [r for r in ROSTER + SHARED + WORKFLOWS if r not in skills]
    (err if strict else warn)(f"missing agents: {missing_agents}") if missing_agents else None
    (err if strict else warn)(f"missing skills: {missing_skills}") if missing_skills else None

    print(f"skills: {len(skills)}  agents: {len(agents)}")
    print(f"listing cost: skills ~{listing_chars} chars (~{listing_chars // 4} tok), "
          f"agents ~{agent_listing} chars (~{agent_listing // 4} tok) per turn")
    if not quiet:
        for w in warnings:
            print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors or (strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
