#!/usr/bin/env python3
"""The one writer of the cover's roster facts.

stdlib/verbs.swift owns the roster. This tool reads that record through
the projection the product itself prints (`gate bare`), renders every
sentence of the cover that carries a roster fact, and writes each in
place. Nothing here parses prose back into facts: the direction is
record -> rendered sentence -> bytes on the page, and `--check`
re-renders and compares instead of writing, so the battery can hold the
page byte-identical to a regeneration.

What is rendered, and the law of each:
  README.md            the porcelain list, in record order; a spelling
                       rides its meaning as word/spelling; a one-letter
                       spelling is a flag alias and stays off the cover;
                       the version verb is typed --version and is
                       rendered the way it is typed
  stdlib/readme.swift  the number word before "commands carry a
                       certificate", counted from the `Run` certificates
"""
import re
import subprocess
import sys

WIDTH = 78
PREFIX = "The porcelain is deliberately git-shaped: `"
NUMBER_WORDS = {10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen",
                14: "Fourteen", 15: "Fifteen", 16: "Sixteen",
                17: "Seventeen", 18: "Eighteen", 19: "Nineteen",
                20: "Twenty"}


def observed(tool):
    """The record, read once, through the product's own projection."""
    p = subprocess.run([tool, "bare", "stdlib/verbs.swift"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit("the projection refused: " + p.stderr.strip())
    verbs, spellings, certs = [], {}, 0
    current = kind = None
    for ln in p.stdout.split("\n"):
        m = re.match(r"^(\w+): (Verb|Spelling)$", ln)
        if m:
            current, kind = m.group(1), m.group(2)
            continue
        m = re.match(r'^\s+"([^"]+)"$', ln)
        if m and current:
            if kind == "Verb":
                verbs.append((current, m.group(1)))
            else:
                spellings.setdefault(current, m.group(1))
            continue
        m = re.match(r"^\s+Means = (\w+)$", ln)
        if m and current and kind == "Spelling":
            word = spellings.pop(current, None)
            if word is not None:
                spellings.setdefault(m.group(1), []).append(word)
            continue
        if re.match(r"^\w+IsSafe = Run<\w+>$", ln):
            certs += 1
    return verbs, {k: v for k, v in spellings.items() if isinstance(v, list)}, certs


def porcelain(verbs, spellings):
    words = []
    for enum, word in verbs:
        tails = [s for s in spellings.get(enum, []) if len(s) > 1]
        spelt = word + "".join("/" + t for t in tails)
        if word == "version":
            spelt = "--" + spelt
        words.append(spelt)
    lines, line, budget = [], "", WIDTH - len(PREFIX)
    for i, w in enumerate(words):
        piece = w if not line else line + " · " + w
        probe = piece + (" ·" if i < len(words) - 1 else "")
        if len(probe) > budget and line:
            lines.append(line + " ·")
            line, budget = w, WIDTH
        else:
            line = piece
    lines.append(line)
    return "\n".join(lines)


def render(tool):
    verbs, spellings, certs = observed(tool)
    if certs not in NUMBER_WORDS:
        sys.exit("the certificate count " + str(certs)
                 + " has no word in this renderer: teach it the word first")
    cover = open("README.md", encoding="utf-8").read()
    span = re.compile(r"(The porcelain is deliberately git-shaped: `)[^`]*(`)")
    if not span.search(cover):
        sys.exit("README.md no longer says the porcelain sentence: "
                 + "the renderer lost its subject")
    cover2 = span.sub(lambda m: m.group(1) + porcelain(verbs, spellings)
                      + m.group(2), cover)
    letter = open("stdlib/readme.swift", encoding="utf-8").read()
    numeral = re.compile(r"(judged with it\. )\w+( commands carry a certificate)")
    if not numeral.search(letter):
        sys.exit("stdlib/readme.swift no longer says the certificate "
                 + "sentence: the renderer lost its subject")
    letter2 = numeral.sub(lambda m: m.group(1) + NUMBER_WORDS[certs]
                          + m.group(2), letter)
    return [("README.md", cover, cover2),
            ("stdlib/readme.swift", letter, letter2)]


def main():
    check = "--check" in sys.argv
    tool = "./gate"
    if "--tool" in sys.argv:
        tool = sys.argv[sys.argv.index("--tool") + 1]
    strayed = []
    for path, held, rendered in render(tool):
        if held != rendered:
            strayed.append(path)
            if not check:
                open(path, "w", encoding="utf-8").write(rendered)
    if check and strayed:
        for path in strayed:
            print(path + ": the page differs from what the record renders")
        sys.exit(1)
    if not check:
        print("rendered: " + (", ".join(strayed) if strayed else "already identical"))


main()
