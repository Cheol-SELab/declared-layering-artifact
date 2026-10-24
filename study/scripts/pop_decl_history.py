"""Population: declaration first-appearance and revision history for the mature repositories in gh_decl.json.

For each repository with a >= 3-layer contract (106): blobless clone, list commits touching the declaration file,
find the first commit whose file contains an importlinter layers contract, and record every later change of the
layers lists (net per commit, contract names ignored). Output: data/pop_decl_history.json (exclusive create).
Usage: python pop_decl_history.py <clone_root> <gh_decl.json> <out.json>
"""
import concurrent.futures as cf, configparser, json, os, subprocess, sys
import tomllib

ROOT, DECL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]


def git(d, *a, timeout=1800):
    r = subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    return r.returncode, r.stdout


def layers_sig(txt, path):
    """Signature of layers contracts (layer lists only), or None if no layers contract."""
    if not txt or "importlinter" not in txt:
        return None
    out = []
    try:
        if path.endswith("pyproject.toml"):
            t = tomllib.loads(txt).get("tool", {}).get("importlinter", {})
            for c in t.get("contracts", []):
                if c.get("type") == "layers":
                    lay = c.get("layers") or []
                    lay = lay if isinstance(lay, list) else [lay]
                    cont = c.get("containers") or []
                    cont = [cont] if isinstance(cont, str) else cont
                    out.append((tuple(sorted(cont)), tuple(tuple(sorted(x.strip() for x in l.split("|"))) for l in lay)))
        else:
            cp = configparser.ConfigParser(strict=False, allow_no_value=True, interpolation=None)
            cp.read_string(txt)
            for s in cp.sections():
                if s.startswith("importlinter:contract") and cp.get(s, "type", fallback="") == "layers":
                    lay = [l.strip() for l in cp.get(s, "layers", fallback="").splitlines() if l.strip() and not l.strip().startswith("#")]
                    cont = tuple(sorted(l.strip() for l in cp.get(s, "containers", fallback="").splitlines() if l.strip()))
                    out.append((cont, tuple(tuple(sorted(x.strip().strip("()") for x in l.split("|"))) for l in lay)))
    except Exception:
        return "PARSE_ERROR"
    return tuple(sorted(out)) if out else None


def one(item):
    repo, meta = item
    d = os.path.join(ROOT, repo.replace("/", "__"))
    if not os.path.isdir(d):
        rc, _ = git(ROOT, "clone", "-q", "--filter=blob:none", "--no-checkout", f"https://github.com/{repo}.git", d)
        if rc:
            return repo, {"err": "clone failed"}
    path = meta["decl"]
    rc, log = git(d, "log", "--format=%H %cs", "--follow", "--", path) if False else git(d, "log", "--format=%H %cs", "HEAD", "--", path)
    commits = [l.split() for l in log.splitlines()][::-1]  # oldest first
    sigs = []
    for h, day in commits:
        rc, txt = git(d, "show", f"{h}:{path}")
        sigs.append((day, h, layers_sig(txt if rc == 0 else None, path)))
    first = next(((day, h) for day, h, s in sigs if s and s != "PARSE_ERROR"), None)
    revisions, prev = [], None
    for day, h, s in sigs:
        if s in (None, "PARSE_ERROR"):
            continue
        if prev is not None and s != prev:
            revisions.append(day)
        prev = s
    rc, n = git(d, "rev-list", "--count", "HEAD")
    return repo, dict(decl=path, decl_first=first[0] if first else None, decl_first_commit=first[1][:9] if first else None,
                      decl_file_commits=len(commits), layer_revisions=revisions, n_commits=int(n.strip() or 0),
                      created=meta["created"], pushed=meta["pushed"], stars=meta["stars"], max_layers=meta["max_layers"])


decl = json.load(open(DECL))
items = [(r, m) for r, m in decl.items() if m.get("max_layers", 0) >= 3 and not m["fork"] and not m["archived"]]
os.makedirs(ROOT, exist_ok=True)
res = {}
with cf.ThreadPoolExecutor(8) as ex:
    for repo, r in ex.map(one, items):
        res[repo] = r
        print(repo, r.get("decl_first"), len(r.get("layer_revisions", [])), r.get("err", ""), flush=True)
with open(OUT, "x", encoding="utf-8") as fh:
    json.dump(res, fh, indent=1, sort_keys=True)
