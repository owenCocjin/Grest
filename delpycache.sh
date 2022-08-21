#!/bin/bash
for f in $(find ./ -name __pycache__); do rm -rf $f; done
