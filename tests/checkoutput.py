#!/bin/env python3
import os
import string
import sys
import re
from pprint import pprint



class CheckException(Exception):
    pass



CHECK_SIMPLE = ''
CHECK_NEXT = '-NEXT'
CHECK_SAME = '-SAME'
CHECK_NOT = '-NOT'
CHECK_BETWEEN = '-BETWEEN'  # check without order
CHECK_LABEL = 'LABEL'



def _apply_check(c, m, variables, nline):
    c['found'] = True
    c['nline'] = nline
    variables.update(m.groupdict())



_var_entry_re = re.compile(r'(?P<name>[A-Za-z0-9_]+)(:(?P<regexp>.+))?')
def _build_pattern(content, variables):
    pattern = ''
    pos = 0
    while pos < len(content):
        re_start = string.find(content, '{{', pos)
        var_start = string.find(content, '[[', pos)
        if re_start != -1 and var_start != -1:
            if re_start < var_start:
                var_start = -1
            else:
                re_start = -1
        if re_start != -1:
            re_end = string.find(content, '}}', re_start)
            assert re_end != -1, "Invalid {{...}} entry"
            pattern += re.escape(content[pos:re_start])
            pattern += content[re_start+2:re_end]
            pos = re_end + 2
        elif var_start != -1:
            var_end = string.find(content, ']]', var_start)
            assert var_end != -1, "Invalid [[...]] entry"
            pattern += re.escape(content[pos:var_start])
            var_entry = content[var_start+2:var_end]
            m = _var_entry_re.match(var_entry)
            assert m
            name = m.group('name')
            regexp = m.group('regexp')
            if regexp is None:
                assert name in variables, 'Variable "%s" is not found' % name
                v = variables[name]
                pattern += re.escape(v)
            else:
                pattern += r'(?P<' + name + r'>' + regexp + ')'
            pos = var_end + 2
        else:
            pattern += re.escape(content[pos:])
            break
    pattern = r'(^| |\t)' + pattern + r'($| |\t)'
    return pattern



class Checker():

    ''' Output check prefix '''
    prefix = 'CHECK'


    def __init__(self, prefix=None, file=None, lines=None):
        if prefix is not None:
            self.prefix = prefix
        self._build_regexp()
        if file is not None:
            assert isinstance(file, str)
            self.build_from_file(file)
        if lines is not None:
            self.build_from_lines(lines)


    def _build_regexp(self):
        assert isinstance(self.prefix, str)
        self.check_re = re.compile(
            r'^[^A-Za-z0-9]*' + re.escape(self.prefix) +
            '(?P<type>(|-NEXT|-SAME|-NOT|-BETWEEN|-LABEL)): ?(?P<content>.*)$'
        )



    def build_from_file(self, filePath):
        if not os.path.exists(filePath):
            raise Exception("Can't find file: " + filePath)
        raw_checks = []
        with open(filePath, "rb") as f:
            for line in f:
                if isinstance(line, bytes):
                    line = line.decode('utf-8')
                if len(line) > 0 and line[-1] == '\r':
                    line = line[:-1]
                if len(line) > 0 and line[-1] == '\n':
                    line = line[:-1]
                if len(line) == 0:
                    continue
                m = self.check_re.match(line)
                if m:
                    raw_checks.append(dict(type=m.group('type'), content=m.group('content')))
        self._compile(raw_checks)


    def build_from_lines(self, lines):
        raw_checks = []
        for line in lines:
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            if len(line) > 0 and line[-1] == '\r':
                line = line[:-1]
            if len(line) > 0 and line[-1] == '\n':
                line = line[:-1]
            if len(line) == 0:
                continue
            m = self.check_re.match(line)
            if m:
                raw_checks.append(dict(type=m.group('type'), content=m.group('content')))
        self._compile(raw_checks)


    checks_list = None # list of separated check blocks
    nrules = 0


    def _compile(self, raw_checks):
        if self.checks_list is None:
            self.checks_list = []
        current_check_sequence = []
        current_label = None
        for c in raw_checks:
            self.nrules += 1
            type = c['type']
            if type == CHECK_SIMPLE:
                pass
            elif type == CHECK_NEXT:
                assert len(current_check_sequence) > 0, "Invalid usage of NEXT check"
            elif type == CHECK_SAME:
                assert len(current_check_sequence) > 0, "Invalid usage of SAME check"
            elif type == CHECK_NOT:
                pass
            elif type == CHECK_BETWEEN:
                pass
            elif type == CHECK_LABEL:
                if len(current_check_sequence) > 0:
                    self.checks_list.append(dict(label=current_label, sequence=current_check_sequence))
                    current_check_sequence = []
                current_label = content.strip()
                if len(current_label) == 0:
                    currennt_label = None
                continue
            else:
                assert False, 'Invalid check type: ' + type
            current_check_sequence.append(dict(content=c['content'], type=type))
        if len(current_check_sequence) > 0:
            self.checks_list.append(dict(label=current_label, sequence=current_check_sequence))


    def _validate(self, lines, check_sequence):
        variables = {}
        def found(c, m, nline):
            return _apply_check(c, m, variables, nline)
        def get_regexp(content):
            return re.compile(_build_pattern(content, variables))
        nline = -1
        nline_prev = -1
        not_check = None
        between_checks = []
        for c in check_sequence:
            if c['type'] == CHECK_SIMPLE:
                nline += 1
                while nline < len(lines):
                    m = get_regexp(c['content']).search(lines[nline])
                    if m is not None:
                        found(c, m, nline)
                        break
                    nline += 1
                else:
                    raise CheckException("Failed check: " + c['content'])
            elif c['type'] == CHECK_NEXT:
                nline += 1
                if not nline < len(lines):
                    raise CheckException("EOF for NEXT check: " + c['content'])
                m = get_regexp(c['content']).search(lines[nline])
                if m is not None:
                    found(c, m, nline)
                else:
                    raise CheckException("Failed NEXT check: " + c['content'] + '\n\tline: ' + lines[nline])
            elif c['type'] == CHECK_SAME:
                m = get_regexp(c['content']).search(lines[nline])
                if m is not None:
                    found(c, m, nline)
                else:
                    raise CheckException("Failed SAME check: " + c['content'] + '\n\tline: ' + lines[nline])
            elif c['type'] == CHECK_NOT:
                assert len(between_checks) == 0, "Invalid mix of NOT and BETWEEN checks: " + c['content']
                not_check = c
                continue
            elif c['type'] == CHECK_BETWEEN:
                assert not_check is None, "Invalid mix of NOT and BETWEEN checks: " + c['content']
                between_checks.append(c)
                continue
            else:
                assert False, "Internal error"
            if not_check is not None:
                lastline = nline
                if c['type'] == CHECK_SAME:
                    lastline = nline + 1
                for nl in range(nline_prev, lastline):
                    m = get_regexp(not_check['content']).search(lines[nl])
                    if m is not None:
                        raise CheckException("Failed NOT check: " + not_check['content'] + '\n\tline: ' + lines[nline])
                not_check = None
            if len(between_checks) > 0:
                regexp = []
                for c in between_checks:
                    regexp.append(get_regexp(c['content']))
                nfound = 0
                for nl in range(nline_prev, nline):
                    for i, r in enumerate(regexp):
                        m = r.search(lines[nl])
                        if m is not None:
                            found(between_checks[i], m, nl)
                            nfound += 1
                            break
                if nfound != len(between_checks):
                    failed = []
                    for c in between_checks:
                        if 'found' not in c:
                            failed.append(c['content'])
                    raise CheckException("Failed BETWEEN checks:\n\t" + failed.join('\n\t'))
                between_checks = []
            nline_prev = nline


    def validate(self, lines):
        filtered_lines = []  # ignore lines with CHECK directives
        for line in lines:
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            if len(line) > 0 and line[-1] == '\r':
                line = line[:-1]
            if len(line) > 0 and line[-1] == '\n':
                line = line[:-1]
            if len(line) == 0:
                continue
            m = self.check_re.match(line)
            if m is None:
                filtered_lines.append(line)

        errors = 0
        for check_sequence in self.checks_list:
            try:
                self._validate(filtered_lines, check_sequence['sequence'])
            except CheckException, e:
                msg = '[%s] %s' % (check_sequence['label'] or '-', e.args[0])
                print(msg)
                errors += 1
        return errors


    def __str__(self):
        return 'checks %d, rules %d' % (len(self.checks_list), self.nrules)



if __name__ == '__main__':
    lines = '''
; CHECK: foo
; CHECK-NEXT: foo3
foo3
foo
foo3
// CHECK: bar1
// CHECK-SAME: baz
bar1 baz
# CHECK: bar2
# CHECK-NOT: foo
# CHECK-SAME: baz
bar2 baz
// CHECK: foo
// CHECK-BETWEEN: e1
// CHECK-BETWEEN: e2
// CHECK-BETWEEN: e3
// CHECK: end
foo
e2
q
e1
q
e3
q
end
'''.split('\n')
    c = Checker(lines=lines)
    errors = c.validate(lines)
    print(errors)

    lines = '''
; CHECK: foo{{.+}}
foo3
; CHECK: foo[[ID:[0-9]+]]
; CHECK-NEXT: bar[[ID]]
foo3
bar3
'''.split('\n')
    c = Checker(lines=lines)
    errors = c.validate(lines)
    print(errors)
