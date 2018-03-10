#!/usr/bin/env bash

rm Parser*txt
for i in {0..7}; do
    echo ---------------------------- t${i}-correct.c ---------------------------------
    python3 aplc.py t${i}-incorrect.c
done
