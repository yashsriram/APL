#!/usr/bin/env bash

for i in {0..11}; do
    echo ---------------------------- t${i}-correct.c ---------------------------------
    python3 Parser.py t${i}.c
    # diff t${i}-correct.c.cfg t${i}-correct.c.cfg1
done

mv *.s /home/pandu/School/6/I.P.L/lab/2018.04.11/test/my/