#!/usr/bin/env python3
"""Compact Unity project summary for agents (saves exploration tokens).

Usage: python scan_unity_project.py [root_dir] [--max N]
Finds every Unity project under root (dir containing ProjectSettings/ProjectVersion.txt)
and prints: editor version, render pipeline, key packages, player settings, scenes in build,
assembly definitions (refs, platforms, test flag, script counts), folder hot spots.
Stdlib only. Never reads Library/, Temp/, Logs/, obj/, binary assets.
"""
import json
import os
import re
import sys
from collections import Counter

SKIP_DIRS = {"Library", "Temp", "Logs", "obj", "bin", "Build", "Builds", "UserSettings",
             "node_modules", ".git", ".vs", ".idea", "MemoryCaptures", "Recordings"}
KEY_PACKAGES = {
    "com.unity.render-pipelines.universal": "URP",
    "com.unity.render-pipelines.high-definition": "HDRP",
    "com.unity.addressables": "Addressables",
    "com.unity.inputsystem": "Input System",
    "com.unity.netcode.gameobjects": "Netcode for GameObjects",
    "com.unity.netcode": "Netcode for Entities",
    "com.unity.entities": "Entities (DOTS)",
    "com.unity.burst": "Burst",
    "com.unity.test-framework": "Test Framework",
    "com.unity.textmeshpro": "TextMeshPro",
    "com.unity.ugui": "uGUI",
    "com.unity.localization": "Localization",
    "com.unity.services.core": "UGS core",
    "com.unity.purchasing": "IAP",
    "com.unity.cinemachine": "Cinemachine",
    "com.unity.timeline": "Timeline",
    "com.unity.ai.navigation": "AI Navigation",
    "com.cysharp.unitask": "UniTask",
    "jp.hadashikick.vcontainer": "VContainer",
    "com.svermeulen.extenject": "Extenject/Zenject",
    "com.unity.nuget.newtonsoft-json": "Newtonsoft.Json",
    "com.unity.mobile.notifications": "Mobile Notifications",
    "com.unity.ads": "Ads", "com.unity.ads.ios-support": "iOS ATT support",
}
YAML_KEYS = ["productName", "companyName", "bundleVersion", "scriptingBackend",
             "apiCompatibilityLevel", "apiCompatibilityLevelPerPlatform", "il2cppCompilerConfiguration",
             "activeInputHandler", "colorSpace", "gpuSkinning", "managedStrippingLevel",
             "applicationIdentifier", "AndroidMinSdkVersion", "AndroidTargetSdkVersion",
             "iOSTargetOSVersionString", "scriptingDefineSymbols"]


def read(path, limit=None):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read(limit) if limit else f.read()
    except OSError:
        return ""


def find_projects(root):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        if os.path.isfile(os.path.join(dirpath, "ProjectSettings", "ProjectVersion.txt")):
            found.append(dirpath)
            dirnames[:] = []  # don't descend into a project's own tree for more projects
    return found


def yaml_block_values(text, keys):
    out = {}
    for k in keys:
        m = re.search(r"^[ 	]*" + re.escape(k) + r":[ 	]*(.*)$", text, re.M)
        if not m:
            continue
        val = m.group(1).strip()
        if val == "" or val == "{}":
            # nested map: capture following indented lines (max 6)
            start = m.end()
            lines = []
            for line in text[start:].splitlines()[1:8]:
                if re.match(r"^\s{4,}\S", line):
                    lines.append(line.strip())
                else:
                    break
            val = "; ".join(lines) if lines else val
        if val:
            out[k] = val[:160]
    return out


def scan(project, max_items):
    p = project
    out = [f"## Unity project: {os.path.relpath(p) if not os.path.isabs(p) else p}"]
    ver = read(os.path.join(p, "ProjectSettings", "ProjectVersion.txt"))
    m = re.search(r"m_EditorVersion:\s*(\S+)", ver)
    out.append(f"- Editor: {m.group(1) if m else '?'}")

    manifest = {}
    try:
        manifest = json.loads(read(os.path.join(p, "Packages", "manifest.json")) or "{}")
    except json.JSONDecodeError:
        out.append("- manifest.json: INVALID JSON")
    deps = manifest.get("dependencies", {})
    rp = [v for k, v in KEY_PACKAGES.items() if k in deps and v in ("URP", "HDRP")]
    out.append(f"- Render pipeline: {', '.join(rp) if rp else 'Built-in (no SRP package)'}")
    keys = [f"{KEY_PACKAGES[k]} {deps[k]}" for k in deps if k in KEY_PACKAGES]
    if keys:
        out.append(f"- Key packages: {', '.join(keys)}")
    other = [k for k in deps if k not in KEY_PACKAGES and not k.startswith("com.unity.modules.")]
    if other:
        shown = other[:max_items]
        more = f" (+{len(other) - len(shown)} more)" if len(other) > len(shown) else ""
        out.append(f"- Other packages ({len(other)}): {', '.join(shown)}{more}")
    if manifest.get("scopedRegistries"):
        regs = [r.get("name", "?") for r in manifest["scopedRegistries"]]
        out.append(f"- Scoped registries: {', '.join(regs)}")
    embedded = [d for d in os.listdir(os.path.join(p, "Packages"))
                if os.path.isdir(os.path.join(p, "Packages", d))] if os.path.isdir(os.path.join(p, "Packages")) else []
    if embedded:
        out.append(f"- Embedded packages: {', '.join(embedded[:max_items])}")

    ps = read(os.path.join(p, "ProjectSettings", "ProjectSettings.asset"), 400_000)
    vals = yaml_block_values(ps, YAML_KEYS)
    if vals:
        out.append("- PlayerSettings: " + " | ".join(f"{k}={v}" for k, v in vals.items()))
    if "activeInputHandler" in vals:
        out.append("  (activeInputHandler: 0=old Input Manager, 1=Input System, 2=both)")
    if "scriptingBackend" in vals:
        out.append("  (scriptingBackend per platform: 0=Mono, 1=IL2CPP)")
    if "apiCompatibilityLevel" in vals:
        out.append("  (apiCompatibilityLevel: 3=.NET Framework 4.x, 6=.NET Standard 2.1)")

    ebs = read(os.path.join(p, "ProjectSettings", "EditorBuildSettings.asset"))
    scenes = re.findall(r"enabled:\s*(\d)\s*\n\s*path:\s*(\S+)", ebs)
    if scenes:
        out.append(f"- Scenes in build ({len(scenes)}): " + ", ".join(
            (s[1] if s[0] == "1" else s[1] + " [disabled]") for s in scenes[:max_items]))

    assets = os.path.join(p, "Assets")
    asmdefs, cs_by_dir, scene_files, ext_counter = [], Counter(), [], Counter()
    asmdef_dirs = {}
    total_cs = 0
    for root_dir in [assets] + [os.path.join(p, "Packages", e) for e in embedded]:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            for fn in filenames:
                if fn.endswith(".meta"):
                    continue
                ext = os.path.splitext(fn)[1].lower()
                ext_counter[ext] += 1
                full = os.path.join(dirpath, fn)
                if ext == ".asmdef":
                    asmdefs.append(full)
                    asmdef_dirs[dirpath] = full
                elif ext == ".cs":
                    total_cs += 1
                    rel = os.path.relpath(dirpath, p).replace("\\", "/")
                    cs_by_dir["/".join(rel.split("/")[:3])] += 1
                elif ext == ".unity":
                    scene_files.append(os.path.relpath(full, p).replace("\\", "/"))

    # map .cs to owning asmdef (nearest parent dir containing an asmdef)
    cs_per_asm = Counter()
    for root_dir in [assets] + [os.path.join(p, "Packages", e) for e in embedded]:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            n = sum(1 for f in filenames if f.endswith(".cs"))
            if not n:
                continue
            d = dirpath
            owner = None
            while d.startswith(p) and len(d) >= len(p):
                if d in asmdef_dirs:
                    owner = asmdef_dirs[d]
                    break
                parent = os.path.dirname(d)
                if parent == d:
                    break
                d = parent
            cs_per_asm[owner] += n

    out.append(f"- C# scripts: {total_cs}; outside any asmdef (Assembly-CSharp): {cs_per_asm.get(None, 0)}")
    if asmdefs:
        out.append(f"- Assembly definitions ({len(asmdefs)}):")
        for a in asmdefs[:max_items]:
            try:
                j = json.loads(read(a) or "{}")
            except json.JSONDecodeError:
                out.append(f"  - {os.path.relpath(a, p)}: INVALID JSON")
                continue
            refs = [r.replace("GUID:", "guid:")[:40] for r in j.get("references", [])]
            flags = []
            if j.get("includePlatforms"):
                flags.append("only " + "/".join(j["includePlatforms"]))
            if "UNITY_INCLUDE_TESTS" in j.get("defineConstraints", []) or \
                    "nunit.framework.dll" in j.get("precompiledReferences", []):
                flags.append("TEST")
            if j.get("autoReferenced") is False:
                flags.append("noAutoRef")
            if j.get("allowUnsafeCode"):
                flags.append("unsafe")
            out.append(f"  - {j.get('name', '?')} [{cs_per_asm.get(a, 0)} cs]"
                       f"{' (' + ', '.join(flags) + ')' if flags else ''}"
                       f" refs: {', '.join(refs[:8]) or '-'}{' ...' if len(refs) > 8 else ''}")
        if len(asmdefs) > max_items:
            out.append(f"  - ... +{len(asmdefs) - max_items} more")
    if scene_files:
        out.append(f"- Scene files ({len(scene_files)}): {', '.join(scene_files[:max_items])}"
                   f"{' ...' if len(scene_files) > max_items else ''}")
    top_dirs = ", ".join(f"{d} ({n})" for d, n in cs_by_dir.most_common(max_items))
    if top_dirs:
        out.append(f"- Script hot spots: {top_dirs}")
    interesting = [".prefab", ".asset", ".mat", ".shader", ".shadergraph", ".compute", ".uxml",
                   ".uss", ".png", ".psd", ".fbx", ".wav", ".mp3", ".anim", ".controller"]
    counts = ", ".join(f"{e}:{ext_counter[e]}" for e in interesting if ext_counter[e])
    if counts:
        out.append(f"- Asset counts: {counts}")
    flags = []
    if os.path.isdir(os.path.join(assets, "AddressableAssetsData")):
        flags.append("Addressables data present")
    if os.path.isdir(os.path.join(assets, "Resources")):
        flags.append("Assets/Resources used (check size)")
    if os.path.isdir(os.path.join(assets, "StreamingAssets")):
        flags.append("StreamingAssets used")
    if os.path.isdir(os.path.join(assets, "Plugins")):
        flags.append("Assets/Plugins present")
    if os.path.isfile(os.path.join(p, ".gitattributes")):
        ga = read(os.path.join(p, ".gitattributes"))
        flags.append("gitattributes: " + ("LFS" if "lfs" in ga else "no LFS") +
                     (", UnityYAMLMerge" if "unityyamlmerge" in ga.lower() else ""))
    if flags:
        out.append("- Notes: " + "; ".join(flags))
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    max_items = 25
    if "--max" in sys.argv:
        try:
            max_items = int(sys.argv[sys.argv.index("--max") + 1])
            args = [a for a in args if a != str(max_items)]
        except (IndexError, ValueError):
            pass
    root = os.path.abspath(args[0] if args else ".")
    projects = find_projects(root)
    if not projects:
        print(f"No Unity project found under {root} (looked for ProjectSettings/ProjectVersion.txt).")
        return 1
    for pr in projects:
        print("\n".join(scan(pr, max_items)))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
