#!/bin/bash
dnf install nginx -y


systemctl start nginx
systemctl enable nginx