#!/usr/bin/env python3
# Remove the equivalences (`name:,EQU,expr`) that DTRAN generates: every use
# of the name is replaced by its definition and constant sums are evaluated.
#
#     degak.py [-o] [file]      (standard input if no file)
#
# Octal constants (`123B`) become decimal so that they can be summed; with -o
# they are left as they are. A comment that only repeats the operand after
# the replacement (`,UTC,GAL/3.D33143+56` -> `,UTC,D33143+56`) is dropped.
import sys
import re

KEEP_OCTAL = False

# an operand followed by a comment that repeats it
SAME_RE = re.compile(r'^(.*,)([^,.]+)\.\2$')

# ----------------------------------------------------------------------
# Regular expressions

# definition line (ignoring leading blanks)
DEF_RE = re.compile(r'^\s*([A-Za-z0-9*/]+):,EQU,(.*)$')

# an identifier token (letters, digits, * or /)
ID_RE = re.compile(r'[A-Za-z0-9*/]+')

# a constant arithmetic expression: series of integers with + / - operators,
# not preceded/followed by identifier characters.
CONST_EXPR_RE = re.compile(
    r'(?<![A-Za-z0-9*/])'          # not part of a larger identifier
    r'([0-9]+(?:[+-][0-9]+)+)'     # e.g. 12+3-5+10
    r'(?![A-Za-z0-9*/])'           # not part of a larger identifier
)

# ----------------------------------------------------------------------
def expand(text: str, macros: dict) -> str:
    """
    Replace all defined identifiers in `text` by their definitions,
    recursively, until a full pass makes no change.
    """
    # Because a replacement can introduce new identifiers, we repeat
    # until a pass does not modify the string.
    while True:
        # function used by re.sub to replace a single identifier token
        def repl(m):
            token = m.group(0)
            return macros.get(token, token)

        new_text = ID_RE.sub(repl, text)
        if new_text == text:          # nothing changed – finished
            break
        text = new_text
    return text


def evaluate_arith(text: str) -> str:

    # Define the regular expression pattern to find octal numbers followed by 'B'
    octal_pattern = r'(?<=[,+])[0-7]+B'

    # Use re.sub with a lambda function for the replacement
    # The lambda function takes a match object and returns the decimal equivalent as a string
    replaced_string = text if KEEP_OCTAL else re.sub(
        octal_pattern,
        lambda m: str(int(m.group()[:-1], 8)),
        text
    )

    """
    Find every constant integer expression (only + and -) and replace it
    by its integer value.
    """
    def compute(m):
        expr = m.group(1)
        # Python can evaluate the expression safely because it contains only
        # integers and +/- operators.
        value = eval(expr)            # noqa: S307  (intended)
        return str(value)
    return CONST_EXPR_RE.sub(compute, replaced_string)


# ----------------------------------------------------------------------
def process_stream(stream):
    macros = {}          # identifier -> fully expanded definition
    out_lines = []

    for raw_line in stream:
        line = raw_line.rstrip('\n')        # keep possible leading spaces
        m_def = DEF_RE.match(line)
        if m_def:
            identifier, raw_def = m_def.group(1), m_def.group(2)
            # Expand the definition using macros defined earlier
            expanded_def = expand(raw_def, macros)
            macros[identifier] = expanded_def
            # definition lines are omitted from output
            continue

        # Ordinary line: expand macros, then evaluate constant arithmetic
        # Do nothing to ,ASN, lines
        if ',ASN,' in line:
            final = line
        else:
            expanded = expand(line, macros)
            final = evaluate_arith(expanded)
            if final != line:
                final = SAME_RE.sub(r'\1\2', final)
        out_lines.append(final)

    return out_lines


# ----------------------------------------------------------------------
def main():
    global KEEP_OCTAL
    if len(sys.argv) > 1 and sys.argv[1] == '-o':
        KEEP_OCTAL = True
        del sys.argv[1]
    # If a filename is given as the first argument, read from it,
    # otherwise read from standard input.
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            result = process_stream(f)
    else:
        result = process_stream(sys.stdin)

    for l in result:
        print(l)


if __name__ == '__main__':
    main()
