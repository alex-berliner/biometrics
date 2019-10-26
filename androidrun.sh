cd /mnt/sdcard/code/headlog
git fetch origin
git rebase origin/master
tsu -c "cp /data/data/net.daylio/databases/entries.db* /mnt/sdcard/code/headlog/head_backup/data/data/net.daylio/databases/"
python headlog.py
git add -A
git commit -m "HTML update $(date)"
git push
