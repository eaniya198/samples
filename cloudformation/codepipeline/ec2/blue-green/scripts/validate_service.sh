#!/bin/bash -xe

curl http://localhost:8080/healthcheck --retry 30 --retry-delay 1 --retry-max-time 60 --retry-all-errors

