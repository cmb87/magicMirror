#!/bin/sh
docker rm grafana
docker run -d --name=grafana -v /home/pi/projects/magicMirror/grafana:/var/lib/grafana -p 3000:3000 -e GF_SECURITY_ADMIN_USER=xxx -e GF_SECURITY_ADMIN_PASSWORD=test grafana/grafana
sleep 10
/usr/bin/grafana-kiosk --URL http://localhost:3000/playlists/play/1 --login-method local --username xxx --password test --kiosk-mode tv
