#!/bin/bash
amazon-linux-extras install nginx1 -y
systemctl restart nginx
systemctl enable nginx