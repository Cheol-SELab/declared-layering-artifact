@echo off
cd /d "G:\SW\SW-SELab\SELab-Researches\selab-research-papers\2026\publish\[access] Volatility-Driven Modularization\study\scripts"
python -B -X utf8 -u l4_worker.py 4 C:/vdm/l4/queue4.txt > C:\vdm\l4\worker4.log 2> C:\vdm\l4\worker4.err
