echo "Remember to connect your phone"
echo ""
echo "Connect phone over USB"
echo "adb tcpip 5555"
echo "Disconnect USB"
echo "adb connect x.x.x.x"

adb shell "\
su -c \
tar -zcvf /mnt/sdcard/head_backup.tar.gz  /data/data/net.daylio;"
adb pull /mnt/sdcard/head_backup.tar.gz
dtrx -o -n head_backup.tar.gz
