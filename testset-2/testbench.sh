#!/usr/bin/env bash

for filename in ./testset-2/Not_Working/*; do
    echo ${filename}
    python3 /home/pandu/School/6/Compilers/lab/APL-Compiler/aplc.py ${filename}
done