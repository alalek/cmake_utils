#!/bin/bash
do_test()
{
  echo "CHECK: $1..."
  cmake -DCMAKE_MODULE_PATH=../cmake/cmake_utils/ -P $1 | python checkoutput.py --prefix=EXPECTED -c $1
  [[ $? == 0 ]] && echo "       OK" || echo "       FAILED"
}

for d in *.cmake; do
  do_test $d
done
