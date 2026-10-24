ps -eo pid,etime,args | grep "[p]ython.*pytest" | grep -v "xdist\|-c import" | cut -c1-200
for f in $(ls -t /tmp/vdm_*.log | head -6); do echo "== $f $(wc -c < $f)"; tail -c 150 $f | tr -d '\n'; echo; done
