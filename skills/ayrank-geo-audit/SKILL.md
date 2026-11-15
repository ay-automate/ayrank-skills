---
name: ayrank-geo-audit
description: Audit one site for AI search (GEO) in a single pass with the free AY Rank tools API, then write one report with a pass, warning or fail per check and the fix for each. Covers AI crawler access in robots.txt, Bing and Google AI training and grounding controls, Google AI Overviews eligibility, the XML sitemap, the heading outline, page size against Googlebot's 2 MB limit, HTTP headers and llms.txt. Use when someone says "audit my site for AI search", "GEO audit", "AEO audit", "is my site ready for ChatGPT", "why doesn't AI cite my site", "AI search readiness check" or "check my site for AI Overviews".
---

# GEO audit (AI search readiness)

One report on whether AI search engines can reach, read and quote a site. Every check calls a free endpoint of the AY Rank tools API. No key, no sign-up.

What this audit can tell you: whether the crawlers are allowed, whether the page can be indexed and shown with a snippet, whether the sitemap and headings are sound. What it cannot tell you: whether ChatGPT or Gemini actually name the brand. For that, use the `ayrank-brand-in-chatgpt` skill.

## Setup

- Needs `curl` and `python3` (any version from 3.8 on). Nothing to install.
- No API key. The API is free and public: https://www.ayrank.com/openapi.json
- Rate limit: 30 requests per 60 seconds per IP, shared across every `/api/v1` tool. This audit makes 7 calls. On a `429`, wait the number of seconds in the `Retry-After` header and retry once.

## Steps

1. Ask for the site if it was not given. Use the homepage URL, for example `https://www.example.com/`. Set it once:
   ```bash
   SITE="https://www.example.com/"
   HOST="www.example.com"
   B="https://www.ayrank.com/api/v1"
   mkdir -p geo-audit && cd geo-audit
   ```

2. Run the 7 checks. Save each answer to a file and read the files, not the terminal.
   ```bash
   curl -s "$B/ai-crawler-access-checker?domain=$HOST"          -o crawler.json
   curl -s "$B/ai-training-grounding-checker?url=$SITE"         -o training.json
   curl -s "$B/ai-overview-eligibility-checker?url=$SITE"       -o aio.json
   curl -s "$B/sitemap-validator?url=$SITE"                     -o sitemap.json
   curl -s "$B/heading-outline-checker?url=$SITE"               -o headings.json
   curl -s "$B/page-size-checker?url=$SITE"                     -o size.json
   curl -s "$B/http-header-checker?url=$SITE"                   -o headers.json
   curl -s -o llms.txt -w "%{http_code} %{content_type}\n" "${SITE%/}/llms.txt"
   ```

3. Read the fields that decide each check:

   | Check | File and field | Pass when |
   |---|---|---|
   | AI crawlers | `crawler.json` `report.bots[].allowed`, `report.blockedCount` | `blockedCount` is 0, or every block is on purpose |
   | Training and grounding | `training.json` `report.bing`, `report.google.googleExtended` | the values match the owner's choice |
   | AI Overviews eligibility | `aio.json` `report.verdict`, `report.checks[]` | `verdict` is `eligible` |
   | Sitemap | `sitemap.json` `sitemap.report.errors`, `warnings`, `sample[].outcome` | 0 errors and every sampled URL `ok` |
   | Headings | `headings.json` `report.counts`, `report.issues` | one h1, no `skipped-level` or `empty` issues |
   | Page size | `size.json` `report.verdict`, `report.decodedBytes` | `verdict` is `under` |
   | HTTP headers | `headers.json` `report.issues`, `report.final.robots` | no `xrt-noindex` or `xrt-nosnippet`, no redirect chain |
   | llms.txt | curl status line | `200 text/plain` (optional file, see below) |

   A quick summary in one go:
   ```bash
   python3 - <<'PY'
   import json
   j = lambda f: json.load(open(f))
   c = j("crawler.json")["report"]
   print("AI crawlers:", [(b["token"], "allowed" if b["allowed"] else "BLOCKED") for b in c["bots"]])
   print("AI Overviews:", j("aio.json")["report"]["verdict"])
   s = j("sitemap.json")["sitemap"]["report"]
   print("Sitemap:", s["entries"], "entries,", s["errors"], "errors,", s["warnings"], "warnings")
   h = j("headings.json")["report"]
   print("Headings:", h["counts"], [i["code"] for i in h["issues"]])
   print("Page size:", j("size.json")["report"]["verdict"], j("size.json")["report"]["decodedBytes"], "bytes")
   print("Header issues:", [i["code"] for i in j("headers.json")["report"]["issues"]])
   PY
   ```

4. Write the report. One table, worst first: check, result, evidence (the deciding line or value from the JSON), fix. Fixes:
   - A bot blocked by robots.txt: quote the deciding line from `report.bots[].line`, then follow the `ayrank-ai-crawler-check` skill for the exact snippet.
   - `aio.json` not eligible: the failing `checks[].id` names the cause (`robots`, `status`, `noindex`, `snippet`, `data-nosnippet`, `canonical`). Remove the `noindex` or `nosnippet` rule, or fix the status code. Google's own rule: a page must be indexed and eligible to show with a snippet. There is no extra AI Overviews markup.
   - Sitemap errors: each `issues[].code` names the rule broken (wrong namespace, relative `loc`, future `lastmod`). Fix the generator, not the file by hand.
   - `skipped-level` heading: the `at` index points at the heading. Change its level so each heading is at most one level deeper than the one before.
   - Page size `over` or `borderline`: Googlebot reads only the first 2 MB of HTML. `report.html.blocks` shows what is heavy (inline scripts, framework state, SVG).
   - llms.txt missing: optional. Use the `ayrank-llms-txt` skill. No AI engine has said it ranks pages by llms.txt, so list it last.

5. End with the 3 fixes that matter most and who does each (developer, content, owner decision).

## Example output (real run, www.ayrank.com, 15 Nov 2026)

`crawler.json`, trimmed:
```json
{
  "domain": "www.ayrank.com",
  "robots": {"url": "https://www.ayrank.com/robots.txt", "status": 200, "found": true},
  "report": {
    "bots": [
      {"token": "GPTBot", "vendor": "OpenAI", "allowed": true, "line": {"line": 29, "text": "Allow: /"}, "via": "named"},
      {"token": "ClaudeBot", "vendor": "Anthropic", "allowed": true, "line": {"line": 32, "text": "Allow: /"}, "via": "named"},
      {"token": "PerplexityBot", "vendor": "Perplexity", "allowed": true, "line": {"line": 11, "text": "Allow: /"}, "via": "named"},
      {"token": "Google-Extended", "vendor": "Google", "allowed": true, "line": {"line": 38, "text": "Allow: /"}, "via": "named"}
    ],
    "allowedCount": 4,
    "blockedCount": 0
  },
  "poweredBy": {"text": "Powered by AY Rank", "url": "https://www.ayrank.com/tools/ai-crawler-access-checker"}
}
```

`aio.json`, trimmed:
```json
{
  "finalUrl": "https://www.ayrank.com/",
  "status": 200,
  "report": {
    "verdict": "eligible",
    "blocking": [],
    "checks": [
      {"id": "robots", "state": "pass", "reason": "robots-allowed"},
      {"id": "status", "state": "pass", "reason": "status-ok"},
      {"id": "noindex", "state": "pass", "reason": "noindex-none"},
      {"id": "snippet", "state": "pass", "reason": "snippet-allowed"},
      {"id": "canonical", "state": "pass", "reason": "canonical-self"},
      {"id": "indexed", "state": "info", "reason": "indexed-unknown"}
    ]
  }
}
```

The summary script on the same run:
```text
AI crawlers: [('GPTBot', 'allowed'), ('ClaudeBot', 'allowed'), ('PerplexityBot', 'allowed'), ('Google-Extended', 'allowed')]
AI Overviews: eligible
Sitemap: 859 entries, 0 errors, 0 warnings
Headings: {'h1': 1, 'h2': 9, 'h3': 28, 'h4': 0, 'h5': 1, 'h6': 0} ['skipped-level']
Page size: under 843508 bytes
Header issues: []
```

The report the skill wrote from it:

| Check | Result | Evidence | Fix |
|---|---|---|---|
| Headings | Warning | one `skipped-level`: the h5 "AI search growth for B2B SaaS" right after an h3 (heading 38 of 39, `at: [37]` counts from 0) | make it an h4 |
| Page size | Pass, 40% of the limit | 843,508 bytes decoded; 76% of it is framework state (`self.__next_f`) | none needed now, watch it |
| AI crawlers | Pass | GPTBot, ClaudeBot, PerplexityBot, Google-Extended allowed by named groups | none |
| AI Overviews eligibility | Pass | `eligible`; Google indexing itself cannot be seen from outside (`indexed-unknown`) | confirm in Search Console |
| Sitemap | Pass | 859 URLs, 0 errors, 20 of 20 sampled URLs answered 200 | none |
| Training and grounding | Pass | Bing training and grounding `allow` (default), Google-Extended allowed on line 38 | none, unless the owner wants to opt out |
| HTTP headers | Pass | 200, no redirects, no X-Robots-Tag | none |
| llms.txt | Present | `200 text/plain; charset=utf-8` | none |

## Manual fallback

If the API is down or rate limited, each check has a free page at https://www.ayrank.com/tools that runs the same code in the browser. Without any tool:
- Open `https://<site>/robots.txt` and find the group for each bot (`User-agent: GPTBot` and so on, else `User-agent: *`). The longest matching `Allow` or `Disallow` path wins.
- View the page source and search for `noindex`, `nosnippet` and `<link rel="canonical"`.
- Open `https://<site>/sitemap.xml` and check a few `<loc>` URLs answer 200.
- In Search Console, URL Inspection shows whether Google indexed the page.

## Powered by AY Rank

Powered by [AY Rank free SEO and GEO tools](https://www.ayrank.com/tools?utm_source=github&utm_medium=skill&utm_campaign=ayrank-skills&utm_content=ayrank-geo-audit). The free API is described at https://www.ayrank.com/openapi.json.
