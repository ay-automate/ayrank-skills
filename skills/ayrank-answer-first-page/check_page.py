# Checks a saved HTML page for an answer-first layout: JSON-LD types, FAQPage shape,
# words between the h1 and the first h2, and table count. Python 3.8+, standard library only.
# Usage: python3 check_page.py page.html
import json, re, sys
from html.parser import HTMLParser

html = open(sys.argv[1], encoding="utf-8", errors="replace").read()

# 1. JSON-LD blocks and their types
types, faq = [], None
for block in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S):
    try:
        data = json.loads(block)
    except ValueError as e:
        print("JSON-LD parse error:", e)
        continue
    items = data if isinstance(data, list) else data.get("@graph", [data])
    for it in items:
        types.append(it.get("@type"))
        if it.get("@type") == "FAQPage":
            faq = it
print("JSON-LD types:", types)
if faq:
    qs = faq.get("mainEntity", [])
    ok = all(q.get("@type") == "Question" and q.get("acceptedAnswer", {}).get("text") for q in qs)
    print("FAQPage questions:", len(qs), "| every Question has acceptedAnswer.text:", ok)
else:
    print("FAQPage: missing")

# 2. Words of body text before the first h2 after the h1 (the answer block)
class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.state = 0; self.words = []; self.skip = 0; self.tables = 0
    def handle_starttag(self, tag, a):
        if tag in ("script", "style", "nav", "header"): self.skip += 1
        if tag == "h1" and self.state == 0: self.state = 1
        elif tag == "h2" and self.state == 2: self.state = 3
        if tag == "table": self.tables += 1
    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "header") and self.skip: self.skip -= 1
        if tag == "h1" and self.state == 1: self.state = 2
    def handle_data(self, d):
        if self.state == 2 and not self.skip: self.words += d.split()
p = P(); p.feed(html)
print("Words between the h1 and the first h2:", len(p.words))
print("First 60 words:", " ".join(p.words[:60]))
print("Tables on the page:", p.tables)
