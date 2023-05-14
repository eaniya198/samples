#!/bin/bash
dnf update -y
dnf install mariadb105-server -y
systemctl restart mariadb