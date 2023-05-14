#!/bin/bash
yum install mariadb-server.x86_64 -y
systemctl restart mariadb
systemctl enable mariadb