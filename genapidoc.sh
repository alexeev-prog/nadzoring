#!/usr/bin/env bash
rm docs/*.rst
sphinx-apidoc -o docs/ src/nadzoring/ --full -l -P -a
