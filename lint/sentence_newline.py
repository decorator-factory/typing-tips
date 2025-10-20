"""
Usage:

    $ python3 lint/sentence_newline.py ./docs

---

This script ensures that a new sentence in the Markdown sources
always begins on a new line. So this is good:

    I like apples.
    But I like bananas better.

And this is not good:

    I like apples. But I like bananas better.

I invented this rule to simplify editing paragraphs. If your
sentences start at random places in the paragraphs, and you amend
one sentence in the middle, you now have to move the rest of the
paragraph in a cascading way, touching every line of the paragraph
in the diff.

Note that this docstring violates this rule, because it's intended to
be read by a human directly without being rendered as HTML.

You can ignore this rule by using this specific HTML comments:
    <!-- ignore(sentence-newline) -->
    ...
    <!-- unignore(sentence-newline) -->
"""


from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    _ = sys.stderr.write("Expected exactly one argument: the directory to check\n")
    sys.exit(1)


def process_file(src: str) -> None:
    is_codeblock = False

    is_ignoreblock = False
    ignoreblock_lines = 0

    for lineno, line in enumerate(src.splitlines(), start=1):
        if "```" in line:
            is_codeblock = not is_codeblock

        if line.strip() == "<!-- ignore(sentence-newline) -->":
            if is_ignoreblock:
                error("sentence-newline already disabled", lineno)
            is_ignoreblock = True
        elif line.strip() == "<!-- unignore(sentence-newline) -->":
            is_ignoreblock = False

        if is_ignoreblock:
            ignoreblock_lines += 1
            if ignoreblock_lines > 20:
                error("ignoring a rule for more than 20 lines", lineno)
        else:
            ignoreblock_lines = 0

        if is_ignoreblock or is_codeblock:
            continue

        if (violation := get_rule_violation(line)) is not None:
            violation = violation.replace("\n", "\\n")
            error(f"place new sentence on a new line: |``{violation}|", lineno)


REGEX = re.compile(r"""
    (?<!e\.g|i\.e|etc)  # abbreviations don't end a sentence
    (?<![.!?])  # "...", "!!!" etc. shouldn't count. might cause some false negatives
    (?<![0-9])  # ordered list. might cause some false negatives
    [.?!][ ](?!\s)
""", re.VERBOSE)

def get_rule_violation(line: str) -> str | None:
    match = REGEX.search(line)
    if match is None:
        return None

    start = max(0, match.start(0) - 5)
    end = match.end(0) + 5
    return line[start:end]


is_error = False

for path in Path(sys.argv[1]).glob("**/*.md"):
    def error(message: str, lineno: int) -> None:
        global is_error
        _ = sys.stderr.write(f"{path}, line {lineno}: {message}\n")
        is_error = True

    process_file(path.read_text())

if is_error:
    sys.exit(1)