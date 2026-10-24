"""D4 follow-up: files added between the snapshot and a task parent may still name moved modules; rewrite those
references in refactored-condition bases with the same move-map translation used for acceptance specs."""
import pathlib, sys
import l4h
REPO, COND = sys.argv[1], sys.argv[2]
mv = l4h.moves(REPO, COND)
for t in l4h.TASKS[REPO]:
    d = l4h.L4 / REPO / "bases" / f"{COND}_{t}"
    changed = []
    for p in d.rglob("*.py"):
        if ".git" in p.parts:
            continue
        s = p.read_text(encoding="utf-8")
        n = l4h.fix_from_imports(l4h.translate(s, mv), mv)
        if n != s:
            p.write_text(n, encoding="utf-8", newline="\n"); changed.append(str(p.relative_to(d)))
    if changed:
        l4h.git(d, "add", "-A"); l4h.git(d, "commit", "-q", "-m", "translate moved-module references")
    print(t, changed)
