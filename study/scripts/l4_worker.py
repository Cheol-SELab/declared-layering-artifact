"""Evaluation queue worker: append '<repo> <cond_task_rep>' lines to C:/vdm/l4/queue.txt; at most N concurrent jobs.
A rep of 'replay' first re-applies the human PR on the per-task base (l4h.py replay), then evaluates it."""
import concurrent.futures as cf, os, subprocess, sys, time
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
Q = sys.argv[2] if len(sys.argv) > 2 else "C:/vdm/l4/queue.txt"
started = set()
ex = cf.ThreadPoolExecutor(N)
PY = [sys.executable, "-B", "-X", "utf8", "l4h.py"]


def ev(repo, run):
    c, t, r = run.split("_")
    log = f"C:/vdm/l4/{repo}/logs/eval_{run}.log"
    with open(log, "w") as fh:
        rc = 0
        if r == "replay":
            rc = subprocess.run(PY + ["replay", repo, c, t], stdout=fh, stderr=subprocess.STDOUT).returncode
        if rc == 0:
            rc = subprocess.run(PY + ["eval", repo, c, t, r], stdout=fh, stderr=subprocess.STDOUT).returncode
    print(time.strftime("%H:%M:%S"), "done", repo, run, "rc", rc, flush=True)


while True:
    if os.path.exists(Q):
        for line in open(Q):
            parts = line.split()
            if len(parts) == 2 and tuple(parts) not in started:
                started.add(tuple(parts)); ex.submit(ev, *parts)
    time.sleep(10)
