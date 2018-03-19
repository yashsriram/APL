#!/usr/bin/env bash

for i in {0..21}; do
    echo ---------------------------- t${i}-correct.c ---------------------------------
    python3 Parser.py t${i}-correct.c
    ./Parser t${i}-correct.c
    diff t${i}-correct.c.ast t${i}-correct.c.ast1
    # diff t${i}-correct.c.cfg t${i}-correct.c.cfg1
done
