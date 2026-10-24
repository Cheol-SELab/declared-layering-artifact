"""Pilot: compare declared layering, static imports and observed co-change.
Usage: python cochange_pilot.py <repo> <worktree_at_t> <since> <until> <unit_regexes...>
A 'unit' is a module group identified by a regex over file paths (first match wins).
"""
import ast, collections, itertools, pathlib, re, subprocess, sys

repo, tree, since, until = sys.argv[1:5]
UNITS = [(u.split("=")[0], re.compile(u.split("=")[1])) for u in sys.argv[5:]]
tree = pathlib.Path(tree)

def unit_of(path: str):
    for name, rx in UNITS:
        if rx.search(path):
            return name
    return None

# ---- 1. co-change ---------------------------------------------------------
log = subprocess.run(
    ["git", "-C", repo, "log", f"--since={since}", f"--until={until}", "--no-merges",
     "--name-only", "--format=---%H %s"], capture_output=True, text=True).stdout
commits, pair, unit_count = [], collections.Counter(), collections.Counter()
for block in log.split("---")[1:]:
    lines = block.strip().splitlines()
    files = [l for l in lines[1:] if l.endswith(".py") and "migrations/" not in l and "/tests/" not in l and not l.startswith("tests/")]
    units = sorted({u for u in map(unit_of, files) if u})
    if not units:
        continue
    commits.append((lines[0], units))
    unit_count.update(units)
    pair.update(itertools.combinations(units, 2))

# ---- 2. static imports at t -----------------------------------------------
def py_files(root):
    for p in root.rglob("*.py"):
        s = str(p.relative_to(tree))
        if "migrations/" in s or "/tests/" in s or s.startswith("tests/"):
            continue
        yield s, p

imports = collections.Counter()
for rel, p in py_files(tree):
    src_u = unit_of(rel)
    if not src_u:
        continue
    try:
        t = ast.parse(p.read_text())
    except SyntaxError:
        continue
    for n in ast.walk(t):
        mods = []
        if isinstance(n, ast.Import):
            mods = [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            if n.level:  # relative import
                base = rel.rsplit("/", 1)[0].replace("/", ".")
                parts = base.split(".")
                base = ".".join(parts[: len(parts) - n.level + 1])
                mods = [base + ("." + n.module if n.module else "")]
            elif n.module:
                mods = [n.module]
        for m in mods:
            mp = m.replace(".", "/") + "/"
            dst_u = unit_of(mp) or unit_of("src/" + mp)
            if dst_u and dst_u != src_u:
                imports[(src_u, dst_u)] += 1

# ---- 3. report ------------------------------------------------------------
N = len(commits)
print(f"window {since}..{until}: {N} commits touching tracked units\n")
print("unit               commits")
for u, c in unit_count.most_common():
    print(f"  {u:18s} {c:4d}")

print("\n== co-change pairs (support = commits touching both; conf = support/min(n_a,n_b)) ==")
print(f"{'pair':40s} {'sup':>4s} {'conf':>5s}  static-import  ")
rows = []
for (a, b), s in pair.most_common():
    conf = s / min(unit_count[a], unit_count[b])
    ab, ba = imports.get((a, b), 0), imports.get((b, a), 0)
    static = f"{a}->{b}:{ab}" if ab else ""
    static += (" " if static and ba else "") + (f"{b}->{a}:{ba}" if ba else "")
    rows.append((a, b, s, conf, static or "NONE"))
for a, b, s, conf, static in rows:
    flag = "  <-- co-change without static dependency" if static == "NONE" and s >= 3 else ""
    print(f"{a+' ~ '+b:40s} {s:4d} {conf:5.2f}  {static}{flag}")

print("\n== static import edges between units (count of import statements) ==")
for (a, b), c in sorted(imports.items(), key=lambda x: -x[1]):
    print(f"  {a:18s} -> {b:18s} {c}")
