import json, os, subprocess, time, urllib.parse, sys
H = ["-H", "Accept: application/vnd.github+json", "-H", "X-GitHub-Api-Version: 2022-11-28"]

def api(url):
    out = subprocess.run(["curl", "-s", "-m", "30", url], capture_output=True, text=True).stdout
    try: return json.loads(out)
    except Exception: return {}

QUERIES = [
    "importlinter filename:.importlinter",
    "importlinter layers filename:pyproject.toml",
    "importlinter layers filename:setup.cfg",
    "importlinter layers filename:tox.ini",
]
OLD = [
    'importlinter "type = layers" path:.importlinter',
    'importlinter "type=layers" path:.importlinter',
    'importlinter "type = layers" path:setup.cfg',
    'importlinter layers path:pyproject.toml "tool.importlinter"',
    '"type = \\"layers\\"" path:pyproject.toml importlinter',
    'importlinter "type = layers" path:tox.ini',
]
repos = {}
for q in QUERIES:
    for page in range(1, 11):
        url = f"https://api.github.com/search/code?q={urllib.parse.quote(q)}&per_page=100&page={page}"
        d = api(url)
        items = d.get("items", [])
        if not items:
            if "message" in d: print("  msg:", d["message"][:80], file=sys.stderr)
            break
        for it in items:
            r = it["repository"]
            if r.get("fork"): continue
            repos.setdefault(r["full_name"], it["path"])
        print(f"q={q[:45]!r} page={page} total={d.get('total_count')} collected={len(repos)}", file=sys.stderr)
        if len(items) < 100: break
        time.sleep(7)  # code search: 10 req/min
    time.sleep(7)
json.dump(repos, open("gh_repos.json", "w"), indent=1)
print(len(repos), "non-fork repos with import-linter layers declarations")
