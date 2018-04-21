#!/usr/bin/env bash

for i in {0..11}; do
    echo ---------------------------- t${i}-correct.c
    python3 Parser.py t${i}.c
done

mv *.s *.ast *.cfg *.sym test/my/

#!/usr/bin/env bash

for i in {0..11}; do
    echo ---------------------------- t${i}-correct.c
    ./test.sh t${i}.c
done

mv *.s *.ast *.cfg *.sym test/ref/

echo
echo ---------------------------- Diffs ---------------------------------
echo
for i in {0..11}; do
    echo ---------------------------- t${i}-correct.c ---------------------------------
#     echo ---------------------------- ast
#     diff -wB test/ref/t${i}.c.ast test/my/t${i}.c.ast
#    echo ---------------------------- cfg
#    diff -wB test/ref/t${i}.c.cfg test/my/t${i}.c.cfg
     echo ---------------------------- sym
     diff -wB test/ref/t${i}.c.sym test/my/t${i}.c.sym
#     echo ---------------------------- s
#     diff -wB test/ref/t${i}.c.s test/my/t${i}.c.s
done
