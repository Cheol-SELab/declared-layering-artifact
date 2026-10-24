"""Append one agent-usage record: python l4_usage.py <repo> <cond_task_rep> <subagent_tokens> <tool_uses> <duration_ms>"""
import json, sys, time
repo, run, tok, tools, ms = sys.argv[1:6]
c, t, r = run.split("_")
rec = dict(repo=repo, cond=c, task=t, rep=r, subagent_tokens=int(tok), tool_uses=int(tools), duration_ms=int(ms), logged=time.strftime("%Y-%m-%dT%H:%M:%S"))
with open("../l4_usage.jsonl", "a", encoding="utf-8") as fh:
    fh.write(json.dumps(rec) + "\n")
print(rec)
