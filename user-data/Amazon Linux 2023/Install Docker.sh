#!/bin/bash
sudo dnf install docker -y
sudo systemctl restart docker
sudo usermod -aG docker ec2-user