for f in $(ls -t /tmp/vdm_*.log | head -4); do echo "== $f $(cat ${f%.log}.rc 2>/dev/null)"; tail -c 800 "$f"; echo; done
ps aux | grep -c "[p]ytest"
