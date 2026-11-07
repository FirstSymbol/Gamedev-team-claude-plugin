#!/usr/bin/env python3
"""Compact .NET solution summary for agents (saves exploration tokens).

Usage: python scan_dotnet_solution.py [root_dir] [--max N]
Prints: global.json SDK, solutions, Directory.Build/Packages props, and per project:
SDK, TFMs, output type, kind (web/test/lib/worker/unity-shared), key props, packages, refs.
Stdlib only. Skips bin/, obj/, node_modules/, Unity Library/.
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

SKIP_DIRS = {"bin", "obj", "node_modules", ".git", ".vs", ".idea", "Library", "Temp", "Logs",
             "packages", "TestResults", "artifacts"}
TEST_PKGS = ("xunit", "nunit", "mstest", "microsoft.net.test.sdk", "tunit")
PROPS = ["TargetFramework", "TargetFrameworks", "OutputType", "Nullable", "LangVersion",
         "ImplicitUsings", "TreatWarningsAsErrors", "AnalysisLevel", "InvariantGlobalization",
         "PublishAot", "UserSecretsId", "IsPackable", "RootNamespace", "ManagePackageVersionsCentrally"]


def strip_ns(tag):
    return tag.split("}", 1)[-1]


def parse_xml(path):
    try:
        return ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return None


def props_of(root):
    vals = {}
    for el in root.iter():
        t = strip_ns(el.tag)
        if t in PROPS and el.text and el.text.strip():
            vals.setdefault(t, el.text.strip())
    return vals


def items_of(root, name):
    res = []
    for el in root.iter():
        if strip_ns(el.tag) == name:
            inc = el.get("Include") or el.get("Update")
            ver = el.get("Version") or el.get("VersionOverride")
            if ver is None:
                for ch in el:
                    if strip_ns(ch.tag) == "Version" and ch.text:
                        ver = ch.text.strip()
            if inc:
                res.append((inc, ver))
    return res


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    max_items = 20
    if "--max" in sys.argv:
        try:
            max_items = int(sys.argv[sys.argv.index("--max") + 1])
            args = [a for a in args if a != str(max_items)]
        except (IndexError, ValueError):
            pass
    root = os.path.abspath(args[0] if args else ".")
    slns, projs, gjson, dprops = [], [], [], []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        if os.path.isfile(os.path.join(dirpath, "ProjectSettings", "ProjectVersion.txt")):
            # Unity project: its generated csproj files are noise
            dirnames[:] = [d for d in dirnames if d in ("Packages",)]
            continue
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            low = fn.lower()
            if low.endswith((".sln", ".slnx", ".slnf")):
                slns.append(full)
            elif low.endswith((".csproj", ".fsproj", ".vbproj")):
                projs.append(full)
            elif low == "global.json":
                gjson.append(full)
            elif low in ("directory.build.props", "directory.packages.props", "directory.build.targets",
                         ".editorconfig", "nuget.config"):
                dprops.append(full)

    rel = lambda x: os.path.relpath(x, root).replace("\\", "/")
    out = [f"## .NET scan: {root}"]
    for g in gjson:
        try:
            j = json.load(open(g, encoding="utf-8"))
            out.append(f"- global.json {rel(g)}: sdk {j.get('sdk', {}).get('version', '?')}"
                       f" rollForward={j.get('sdk', {}).get('rollForward', '-')}")
        except (OSError, json.JSONDecodeError):
            out.append(f"- global.json {rel(g)}: unreadable")
    if slns:
        out.append(f"- Solutions: {', '.join(rel(s) for s in slns)}")
    for d in dprops:
        line = f"- {rel(d)}"
        if d.lower().endswith(".props"):
            r = parse_xml(d)
            if r is not None:
                pv = props_of(r)
                cpm = items_of(r, "PackageVersion")
                if pv:
                    line += ": " + ", ".join(f"{k}={v}" for k, v in pv.items())
                if cpm:
                    line += f"; central versions: {len(cpm)} (" + ", ".join(
                        f"{n} {v}" for n, v in cpm[:max_items]) + (" ..." if len(cpm) > max_items else "") + ")"
        out.append(line)
    if not projs:
        out.append("- No .csproj/.fsproj found.")
        print("\n".join(out))
        return 1
    out.append(f"- Projects ({len(projs)}):")
    for pr in sorted(projs)[: max_items * 3]:
        r = parse_xml(pr)
        if r is None:
            out.append(f"  - {rel(pr)}: UNPARSEABLE")
            continue
        sdk = r.get("Sdk", "")
        if not sdk:
            for el in r:
                if strip_ns(el.tag) == "Sdk":
                    sdk = el.get("Name", "")
        pv = props_of(r)
        pkgs = items_of(r, "PackageReference")
        refs = [os.path.basename(x[0]) for x in items_of(r, "ProjectReference")]
        names = [n.lower() for n, _ in pkgs]
        kind = []
        if "Web" in sdk or any(n.startswith("microsoft.aspnetcore") for n in names):
            kind.append("web")
        if "Worker" in sdk:
            kind.append("worker")
        if any(n.startswith(TEST_PKGS) for n in names) or "MSTest.Sdk" in sdk:
            kind.append("test")
        if "Aspire" in sdk or any(n.startswith("aspire.") for n in names):
            kind.append("aspire")
        tfm = pv.get("TargetFramework") or pv.get("TargetFrameworks") or "?"
        if "netstandard2" in tfm:
            kind.append("unity-shareable")
        if not kind:
            kind.append("exe" if pv.get("OutputType", "").lower() in ("exe", "winexe") else "lib")
        extra = {k: v for k, v in pv.items() if k not in ("TargetFramework", "TargetFrameworks", "RootNamespace")}
        line = f"  - {rel(pr)} [{'/'.join(kind)}] tfm={tfm} sdk={sdk or '?'}"
        if extra:
            line += " " + " ".join(f"{k}={v}" for k, v in extra.items())
        out.append(line)
        if pkgs:
            out.append("    pkgs: " + ", ".join(f"{n}{' ' + v if v else ''}" for n, v in pkgs[:max_items])
                       + (f" (+{len(pkgs) - max_items})" if len(pkgs) > max_items else ""))
        if refs:
            out.append("    refs: " + ", ".join(refs))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
