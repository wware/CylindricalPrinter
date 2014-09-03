#!/bin/bash

if [ "$(uname)" == "Darwin" ]
then
    IPADDR=$(ifconfig | grep -E '^\s+inet ' | grep -v 127.0.0 | head -1 | cut -d ' ' -f 2)
else
    IPADDR=$(ifconfig | grep -E '^\s+inet ' | grep -v 127.0.0 | head -1 | sed 's/.*addr://' | sed 's/\s.*//')
fi

if [ ! -f current_ip.txt ] || [ ! -f static/my_ip_addr.png ] || [ "$(cat current_ip.txxt)" != "$IPADDR" ]
then
    convert -size 1024x768 xc:black  -stroke red  -fill red  -pointsize 60 \
        -draw "rectangle 300,350 400,400" \
        -draw "rectangle 500,350 600,400" \
        -draw "rectangle 300,400 500,450" \
        -draw "rectangle 700,400 750,450" \
        -draw 'text 300,300 "'$IPADDR'"' static/my_ip_addr.png
    echo "$IPADDDR" > current_ip.txt
fi
