#!/usr/bin/env python3
"""Word counts for paper.md.
total_words: every whitespace-separated token after removing markdown symbols (#*|`>-) and image links,
i.e. tables, references and headings are INCLUDED. Also reports the References section and markdown table rows
separately. Usage: python3 wordcount.py paper.md"""
import re, sys
t = open(sys.argv[1]).read()
def wc(x):
    x = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", x); x = re.sub(r"[#*|`>-]", " ", x)
    return len(re.findall(r"\S+", x))
refs = t.split("\n## References")[1] if "\n## References" in t else ""
table_rows = "\n".join(l for l in t.splitlines() if l.strip().startswith("|"))
print({"total_words": wc(t), "references_words": wc(refs), "table_words": wc(table_rows),
       "body_without_tables_and_refs": wc(t) - wc(refs) - wc(table_rows), "raw_whitespace_tokens": len(t.split())})
