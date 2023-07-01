#! /bin/bash
cd "$(dirname "$0")"
if [ ! -d "venv" ]; then
    /usr/bin/env python3 -m venv venv
    . ./venv/bin/activate
    pip install requests
fi
. ./venv/bin/activate
python cli.py
