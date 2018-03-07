#!/usr/bin/env bash

rm Parser*txt
for i in {0..21}; do
    echo ---------------------------- t${i}-correct.c ---------------------------------
    python3 aplc.py t${i}-correct.c
done
