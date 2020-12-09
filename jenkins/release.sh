#!/usr/bin/env bash
set -e

pip3 install setuptools wheel twine
pip3 install -r requirements.txt

python3 setup.py sdist bdist_wheel

twine check dist/*
# Credentials passed via TWINE_USERNAME/TWINE_PASSWORD environment variables
twine upload dist/*
