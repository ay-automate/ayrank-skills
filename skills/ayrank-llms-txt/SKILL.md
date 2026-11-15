---
name: ayrank-llms-txt
description: Draft an llms.txt file for a site with the free AY Rank llms.txt generator API, check that every URL in it answers 200 before it ships, then confirm the live file is served as plain text. Use when someone says "create an llms.txt", "generate llms.txt", "do I need llms.txt", "llms.txt for my site", "validate my llms.txt", "fix my llms.txt" or "add llms.txt for AI".
---

# llms.txt, drafted and checked

llms.txt is a Markdown file at `/llms.txt` that lists a site's key pages with one line each, so a language model can find them without parsing navigation. The format is a proposal from llmstxt.org.

Be straight with the owner about what it does. No major AI search engine has said it uses llms.txt to pick which pages to cite. It is cheap and harmless, and it helps agents and tools that do read it. Fix crawler access and page content first (see `ayrank-ai-crawler-check` and `ayrank-geo-audit`).

## Setup

- Needs `curl` and `python3` 3.8 or later. `check_links.py` in this folder uses only the standard library.
- No API key. Free public API: https://www.ayrank.com/openapi.json
- Rate limit: 30 requests per 60 seconds per IP across all `/api/v1` tools.

## Steps

1. Check what is there now:
   ```bash
   curl -s -o current-llms.txt -w "%{http_code} %{content_type}\n" https://www.example.com/llms.txt
   ```
   A `200 text/plain` means a file exists: run step 4 on it before replacing anything. A `404`, or an HTML page, means there is none.

2. Collect the inputs from the site itself, not from memory: the company name, a 2 or 3 sentence description, the industry, the services, the 5 to 15 pages that matter most (product, pricing, docs, top guides), what makes the company different and a contact email. Pass lists as JSON arrays.

3. Generate the draft:
   ```bash
   curl -s -X POST "https://www.ayrank.com/api/v1/llms-txt-generator" \
     -H "content-type: application/json" \
     -d '{
       "companyName": "Example Co",
       "websiteUrl": "https://www.example.com",
       "description": "Two or three sentences on what the company does.",
       "industry": "SaaS",
       "services": ["Service one", "Service two"],
       "keyPages": ["https://www.example.com/pricing", "https://www.example.com/docs"],
       "differentiators": ["One concrete thing that sets it apart"],
       "contactEmail": "hello@example.com"
     }' -o llms.json
   ```
   The answer has `llmsTxt` (the file) and `completeness.score` from 0 to 100 with a label. A low score means inputs are missing; add them and run again.

4. Check every URL in the draft before it ships:
   ```bash
   python3 check_links.py llms.json
   ```
   Each URL prints `ok` or `FIX` with its status code. Replace or remove every `FIX` line, then run it again until it prints `0 to fix`. Give each key page a descriptive link title (`[Pricing](...)`), since the generator names links from the URL.

5. Save the file as `llms.txt` at the site root and deploy. Then check it is served as plain text with no redirect:
   ```bash
   curl -s "https://www.ayrank.com/api/v1/http-header-checker?url=https://www.example.com/llms.txt" -o llms-headers.json
   ```
   `status` should be 200, `report.final.contentType` should start with `text/plain` or `text/markdown`, and `report.issues` should be empty. Run `check_links.py` on the live file too: `python3 check_links.py current-llms.txt` after downloading it again.

6. Re-run steps 4 and 5 whenever pages are added, renamed or removed.

## Why this skill is the fifth one

Of the 18 endpoints in the free API, the llms.txt generator is the only one that produces a file the owner can ship in one run, and llms.txt is the GEO file people ask about most. The link check is there because generated files often point at pages that do not exist, which the example below shows.

## Example output (real run, www.ayrank.com, 15 Nov 2026)

`llms.json` from the generator:
```json
{
  "llmsTxt": "# AY Rank\n\n> GEO agency and software that helps brands get named in ChatGPT, Perplexity, Gemini and Google AI Overviews.\n\n## About\n- Industry: Marketing\n- Specialty: GEO optimization, AI visibility tracking, Free SEO and GEO tools\n- Website: https://www.ayrank.com\n\n## Services\n- GEO optimization\n- AI visibility tracking\n- Free SEO and GEO tools\n\n## Key Pages\n- [Tools](https://www.ayrank.com/tools)\n- [Blog](https://www.ayrank.com/blog)\n- [Pricing](https://www.ayrank.com/pricing)\n\n## What Makes AY Rank Different\n- Free JSON API for 18 SEO and GEO checks, no key\n\n## Contact\n- Website: https://www.ayrank.com\n",
  "completeness": {"score": 78, "label": "Good"},
  "poweredBy": {"text": "Powered by AY Rank", "url": "https://www.ayrank.com/tools/llms-txt-generator"}
}
```

`check_links.py llms.json`:
```text
ok  200  https://www.ayrank.com
ok  200  https://www.ayrank.com/blog
FIX 404  https://www.ayrank.com/pricing
ok  200  https://www.ayrank.com/tools
4 URLs, 1 to fix
```

The `/pricing` page was a guess in the inputs and it does not exist on www.ayrank.com, so that line comes out before the file ships.

The live file, from `http-header-checker`:
```text
status 200 | contentType text/plain; charset=utf-8 | issues []
```

## Manual fallback

- Write the file by hand from the llmstxt.org format: an `# H1` with the name, a `>` one-paragraph summary, then `## Sections` of `- [Title](url): one line` entries.
- Open each link in a browser before you publish.
- The generator also runs in the browser at https://www.ayrank.com/tools/llms-txt-generator, and the AY Rank app has a free validator for an existing file at https://app.ayrank.com/tools/llms-txt-validator.

## Powered by AY Rank

Powered by the [AY Rank llms.txt generator](https://www.ayrank.com/tools/llms-txt-generator?utm_source=github&utm_medium=skill&utm_campaign=ayrank-skills&utm_content=ayrank-llms-txt), free and with no sign-up.
