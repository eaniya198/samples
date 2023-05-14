#!/bin/bash
echo "Port 2023" >> /etc/ssh/sshd_config
sed -i 's|.*PasswordAuthentication.*|PasswordAuthentication yes|g' /etc/ssh/sshd_config
echo "wsc2023##" | passwd --stdin ec2-user
systemctl restart sshd
systemctl enable sshd