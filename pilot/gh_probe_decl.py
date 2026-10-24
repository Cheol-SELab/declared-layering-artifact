import json, subprocess, concurrent.futures as cf, configparser, tomllib, re
mature = json.load(open("gh_mature.json"))
repos = json.load(open("gh_repos.json"))

def fetch(r, path):
    out = subprocess.run(["curl", "-s", "-m", "15", "-H", "Accept: application/vnd.github.raw+json",
                          f"https://api.github.com/repos/{r}/contents/{path}"], capture_output=True, text=True).stdout
    return out if out and not out.startswith('{"message"') else None

def layers_info(path, txt):
    best = 0; names = []
    try:
        if path.endswith("pyproject.toml"):
            t = tomllib.loads(txt).get("tool", {}).get("importlinter", {})
            for c in t.get("contracts", []):
                if c.get("type") == "layers":
                    L = c["layers"] if isinstance(c["layers"], list) else [c["layers"]]
                    if len(L) > best: best, names = len(L), L
        else:
            cp = configparser.ConfigParser(strict=False, allow_no_value=True); cp.read_string(txt)
            for s in cp.sections():
                if s.startswith("importlinter:contract") and cp.get(s, "type", fallback="") == "layers":
                    L = [l.strip() for l in cp.get(s, "layers").splitlines() if l.strip() and not l.strip().startswith("#")]
                    if len(L) > best: best, names = len(L), L
    except Exception as e:
        return -1, [str(e)[:30]]
    return best, names

def probe(r):
    path = repos[r]
    txt = fetch(r, path)
    if txt is None:
        for p in [".importlinter", "setup.cfg", "pyproject.toml", "tox.ini"]:
            txt = fetch(r, p)
            if txt and "importlinter" in txt: path = p; break
    if not txt: return r, None
    n, names = layers_info(path, txt)
    return r, {"decl": path, "max_layers": n, "layers": names[:12]}

out = {}
with cf.ThreadPoolExecutor(12) as ex:
    for r, info in ex.map(probe, list(mature)):
        if info: out[r] = {**mature[r], **info}
json.dump(out, open("gh_decl.json", "w"), indent=1)
good = {r: m for r, m in out.items() if m["max_layers"] >= 3}
print(f"probed={len(out)}  with >=3-layer contract: {len(good)}")
for r, m in sorted(good.items(), key=lambda x: -x[1]["stars"]):
    print(f"  {m['stars']:6d} {m['created']} {r:45s} layers={m['max_layers']:2d} {m['decl']}")
