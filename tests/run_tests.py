#!/bin/env python3
from __future__ import print_function
import os
import sys
import re
import subprocess
from pprint import pprint

from checkoutput import Checker

work_dir = os.getcwd()

def capture_output(command_args):
    p = subprocess.Popen(command_args,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        universal_newlines=True)
    (stdoutdata, stderrdata) = p.communicate()
    res = []
    lines = stdoutdata.split('\n')
    for line in lines:
        if isinstance(line, bytes):
            line = line.decode('utf-8')
        if len(line) > 0 and line[-1] == '\r':
            line = line[:-1]
        if len(line) > 0 and line[-1] == '\n':
            line = line[:-1]
        if len(line) == 0:
            continue
        res.append(line.strip())
    return (res, stdoutdata, stderrdata)

tests = os.listdir('.')
tests = [t for t in tests if len(t) >= 6 and t[-6:] == '.cmake']
tests = sorted(tests)
total_failed_tests = 0
total_passed_tests = 0
for test_name in tests:
    errors = 0
    c = Checker(prefix='EXPECTED', file=test_name)
    print("[   RUN] %s" % test_name)
    (output, stdoutdata, stderrdata) = capture_output(['cmake', '-DCMAKE_MODULE_PATH=%s' % os.path.abspath(os.path.join(work_dir, '../cmake/cmake_utils')), '-P', test_name])
    errors = c.validate(output)
    if errors > 0:
        if len(stdoutdata) > 0:
            print("STDOUT:\n%s" % stdoutdata)
        else:
            print("Empty STDOUT")
        if stderrdata is not None and len(stderrdata) > 0:
            print("STDERR:\n%s" % stderrdata)
        print("[FAILED] %s" % test_name)
        total_failed_tests += 1
    else:
        print("[  DONE] %s (%s)" % (test_name, c))
        total_passed_tests += 1

print()
print("#PASSED: %d tests" % total_passed_tests)
print("#FAILED: %d tests" % total_failed_tests)
print()
print("#FAILURE" if total_failed_tests > 0 else "#SUCCESS")
print()

exit(1 if total_failed_tests > 0 else 0)
