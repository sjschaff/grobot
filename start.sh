#!/bin/bash

sudo svc -u /etc/service/crossbar
tail -f ~/grobot/.crossbar/log/node.log
