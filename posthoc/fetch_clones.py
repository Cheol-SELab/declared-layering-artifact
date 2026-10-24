"""Recreate the clones of the subject repositories at the commits used by the study (not part of the package).

The scanner (study/scripts/blind_scan.py) reads snapshots by date from the history reachable from HEAD, so each
clone is checked out at the HEAD it had when the study scanned it (2026-10-05). The clones are needed only by
posthoc_s2n_variants.py and posthoc_rq2.py, and by the study's own scanner scripts.
Usage: python fetch_clones.py <empty-or-new directory>
"""
import pathlib
import subprocess
import sys

CLONES = {
    "bk-user": ("https://github.com/TencentBlueKing/bk-user.git", "bd804645e39a3173d046d8e0e56a8ab0ef4afd80"),
    "ggshield": ("https://github.com/GitGuardian/ggshield.git", "cefc56cccf414eac690b14619c493aef8b9f9733"),
    "import-linter": ("https://github.com/seddonym/import-linter.git", "31927f1457e3df673912cb5efb0afa6dbc37585f"),
    "kedro": ("https://github.com/kedro-org/kedro.git", "e8677ac2fc531cb9157cefa54c89ea50c28ff2fd"),
    "kopf": ("https://github.com/nolar/kopf.git", "7850627dfff997fdd2f10f5948b66fc9267bbd16"),
    "legadilo": ("https://github.com/JujensGh/legadilo.git", "1ce06229d52148ee587c4b6230fcf4814bb3d81d"),
    "openedx-learning": ("https://github.com/openedx/openedx-learning.git", "f2ae44631662a4e2b48af7ea6bf5bd2dddd202f5"),
    "ophyd-async": ("https://github.com/bluesky/ophyd-async.git", "afe63952944ca7c1560a7b9150d077d8c05c6527"),
    "sqlfluff": ("https://github.com/sqlfluff/sqlfluff.git", "b7ab9473ee15efcf8ca787ac05e0bfc26c8d52b0"),
    "wemake-python-styleguide": ("https://github.com/wemake-services/wemake-python-styleguide.git",
                                 "f35992a2a0f697bc90c23e1ab7e3ae4edbbcbb30"),
}


def main():
    root = pathlib.Path(sys.argv[1])
    root.mkdir(parents=True, exist_ok=True)
    for name, (url, head) in CLONES.items():
        dst = root / name
        if dst.exists():
            sys.exit(f"{dst} exists; use a new directory")
        subprocess.run(["git", "-c", "core.autocrlf=false", "clone", "-q", url, str(dst)], check=True)
        subprocess.run(["git", "-C", str(dst), "checkout", "-q", "--detach", head], check=True)
        got = subprocess.run(["git", "-C", str(dst), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        print(f"{'OK  ' if got == head else 'DIFF'} {name} {got}")


if __name__ == "__main__":
    main()
