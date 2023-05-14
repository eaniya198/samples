#!/bin/bash

# exit on error
set -eu 

curl http://localhost:5000/greet --retry 30 --retry-delay 1 --retry-max-time 60 --retry-all-errors
