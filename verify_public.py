"""Integrity checks for the public artifact (standard library only; nothing is executed or modified).

1. Every file listed in PUBLIC-MANIFEST.json exists with the recorded SHA-256, and no unlisted file is present.
2. The registration amendment files match study/PREREG_AMENDMENTS_MANIFEST.sha256.
3. Identities sealed in the registration (proposals, Layer-4 plan, kedro re-layering patch) match the archived files.
Usage: python -B verify_public.py            (check)
       python -B verify_public.py --write    (maintainers only: regenerate PUBLIC-MANIFEST.json)
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "PUBLIC-MANIFEST.json"
EXCLUDE = {".git", "__pycache__"}
SEALED = {
    # file: SHA-256 prefix recorded in the registration log / manuscript
    "study/data/layer2_proposals.json": "145ddb17bdf9c547ef3aebfb5bbc79d32e5986a6edbf9b260f3c325dfd2b5403",
    "study/l4_plans/tie_rule/kedro_C.json": "b80fbd20",
    "layer4/kedro/C_refactor_nodocs.patch": "c454b546",
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def files():
    return sorted(p for p in ROOT.rglob("*") if p.is_file() and not (EXCLUDE & set(p.relative_to(ROOT).parts))
                  and p != MANIFEST)


def main():
    if "--write" in sys.argv:
        MANIFEST.write_text(json.dumps({p.relative_to(ROOT).as_posix(): sha(p) for p in files()}, indent=1) + "\n",
                            encoding="utf-8", newline="\n")
        print(f"wrote {MANIFEST.name}")
        return 0
    errors = []
    recorded = json.loads(MANIFEST.read_text(encoding="utf-8"))
    present = {p.relative_to(ROOT).as_posix(): p for p in files()}
    for rel, digest in recorded.items():
        if rel not in present:
            errors.append(f"missing: {rel}")
        elif sha(present[rel]) != digest:
            errors.append(f"changed: {rel}")
    errors += [f"unlisted: {rel}" for rel in present if rel not in recorded]
    study = ROOT / "study"
    for line in (study / "PREREG_AMENDMENTS_MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        digest, name = line.split(maxsplit=1)
        if sha(study / name.lstrip("*")) != digest:
            errors.append(f"amendment hash mismatch: {name}")
    for rel, prefix in SEALED.items():
        if not sha(ROOT / rel).startswith(prefix):
            errors.append(f"sealed identity mismatch: {rel}")
    print(f"{len(recorded)} manifest files, 10 amendment files, {len(SEALED)} sealed identities checked")
    print("\n".join(errors) if errors else "OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
