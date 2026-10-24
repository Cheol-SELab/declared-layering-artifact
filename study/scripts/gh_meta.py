import json, subprocess, concurrent.futures as cf, re, sys, os
H = ["-H", "Accept: application/vnd.github+json"]
repos = json.load(open("gh_repos.json"))
meta = json.load(open("gh_meta.json")) if os.path.exists("gh_meta.json") else {}
todo = [r for r in repos if r not in meta]
def get(r):
    out = subprocess.run(["curl", "-s", "-m", "20", f"https://api.github.com/repos/{r}"], capture_output=True, text=True).stdout
    try:
        d = json.loads(out)
        if "full_name" not in d: return r, {"err": d.get("message", "?")[:40]}
        return r, {"stars": d["stargazers_count"], "created": d["created_at"][:10], "pushed": d["pushed_at"][:10],
                   "fork": d["fork"], "archived": d["archived"], "lang": d.get("language")}
    except Exception as e:
        return r, {"err": str(e)[:40]}
with cf.ThreadPoolExecutor(12) as ex:
    for i, (r, m) in enumerate(ex.map(get, todo)):
        meta[r] = m
        if i % 200 == 0:
            json.dump(meta, open("gh_meta.json", "w")); print(i, file=sys.stderr)
json.dump(meta, open("gh_meta.json", "w"))
ok = {r: m for r, m in meta.items() if "err" not in m}
mature = {r: m for r, m in ok.items() if m["created"] <= "2024-10-05" and m["pushed"] >= "2025-10-05" and not m["archived"] and not m["fork"]}
print(f"total={len(meta)} ok={len(ok)} created>=2y & active & not archived: {len(mature)}")
for thr in [0, 10, 50, 200, 1000]:
    print(f"  stars>={thr}: {sum(1 for m in mature.values() if m['stars']>=thr)}")
json.dump(mature, open("gh_mature.json", "w"), indent=1)
