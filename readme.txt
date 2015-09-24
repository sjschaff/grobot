crossbar start > log.txt 2>&1 &

sudo svc -u /etc/service/crossbar	#start
sudo svc -d /etc/service/crossbar	#stop
sudo svc -t /etc/service/crossbar	#restart
sudo svstat /etc/service/crossbar	#status
tail -f ~/grobot/.crossbar/log/node.log
