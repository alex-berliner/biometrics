cd /mnt/sdcard/code/headlog
tsu -c "cp /data/data/net.daylio/databases/entries.db* /mnt/sdcard/code/headlog/head_backup/data/data/net.daylio/databases/"
python headlog.py
git reset --hard
git clean -xdf

