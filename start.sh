#!/bin/bash
command -v python2 > /dev/null || { echo "python2 not found"; exit 1; }

python2 elmo-display.py
