#!/bin/bash

sudo svc -t /etc/service/crossbar
tail -f ~/grobot/.crossbar/log/node.log
