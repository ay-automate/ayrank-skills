# Lists every URL in an llms.txt (a file or the llmsTxt field of the generator's JSON)
# and prints the HTTP status each one answers with, via curl. Python 3.8+, standard library only.
# Usage: python3 check_links.py llms.json   or   python3 check_links.py llms.txt
import json, re, subprocess, sys

path = sys.argv[1]
text = open(path, encoding="utf-8").read()
if path.endswith(".json"):
    text = json.loads(text)["llmsTxt"]

urls = sorted(set(re.findall(r"https?://[^\s)\]>]+", text)))
bad = 0
for url in urls:
    code = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-L", "--max-time", "10", "-w", "%{http_code}", url],
        capture_output=True, text=True,
    ).stdout.strip()
    ok = code.startswith("2")
    bad += not ok
    print(("ok  " if ok else "FIX ") + code + "  " + url)
print(f"{len(urls)} URLs, {bad} to fix")
sys.exit(1 if bad else 0)
