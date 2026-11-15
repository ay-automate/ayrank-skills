---
name: ayrank-answer-first-page
description: Write an answer-first web page that AI answers and search engines can quote, then check it with free AY Rank tools. The page answers the question in its first 60 words, has a comparison table and an FAQ section with FAQPage JSON-LD. After publishing, the skill checks the heading outline, the JSON-LD and trust signals, and Google AI Overviews eligibility through the free AY Rank API. Use when someone says "write an answer-first page", "write a page AI will cite", "AEO page", "GEO content", "optimize this page for ChatGPT answers", "add an FAQ with schema" or "make this post quotable by AI".
---

# Answer-first page

AI answers quote pages that state the answer early, in plain words, and back it with facts a model can lift: a table, dates, sources. This skill writes that page and then checks the live result.

One honest note on FAQ markup. Google stopped showing FAQ rich results in Search on 7 May 2026. FAQPage JSON-LD still gives machines the questions and answers in a clean form, so keep it, but do not promise a rich result in Google.

## Setup

- Needs `curl` and `python3` 3.8 or later. Nothing to install. `check_page.py` in this folder uses only the standard library.
- No API key. Free public API: https://www.ayrank.com/openapi.json
- Rate limit: 30 requests per 60 seconds per IP across all `/api/v1` tools. The checks make 3 calls per page.

## Steps

1. Pin the question. Get the exact query the page should answer, in the searcher's words, for example "how to rank in ChatGPT". One page, one main question.

2. Collect facts before writing. Every number, price or limit in the table needs a source page read today. Write the source and the date next to it. If a fact cannot be sourced, leave it out.

3. Write the page in this order:
   - **H1** that contains the question or its key phrase.
   - **Answer block, 60 words or fewer**, directly under the H1, before any intro, table of contents, author box or "related reading" line. It answers the question in the question's own words. A reader who stops here has the answer.
   - **Comparison table** with dated facts (options in rows, criteria in columns). Use a real `<table>` with `<th>` headers, not an image.
   - **Body sections** under H2s phrased as the follow-up questions people ask. Each opens with its own one or two sentence answer.
   - **FAQ section**: 4 to 8 questions the main sections did not answer. Each answer 40 to 80 words, self-contained.
   - **Dates**: a visible published date, and an updated date when it changes.

4. Add FAQPage JSON-LD that matches the visible FAQ word for word:
   ```html
   <script type="application/ld+json">
   {
     "@context": "https://schema.org",
     "@type": "FAQPage",
     "mainEntity": [
       {
         "@type": "Question",
         "name": "The question, exactly as shown on the page?",
         "acceptedAnswer": {
           "@type": "Answer",
           "text": "The answer, exactly as shown on the page."
         }
       }
     ]
   }
   </script>
   ```
   For an article, add Article JSON-LD with `author`, `datePublished` and `dateModified`. The free generators at https://www.ayrank.com/tools/faq-schema-generator and https://www.ayrank.com/tools/article-schema-generator write both blocks from a form.

5. Publish, then check the live page. Replace the URL:
   ```bash
   URL="https://www.example.com/blog/your-page"
   B="https://www.ayrank.com/api/v1"
   curl -s "$B/heading-outline-checker?url=$URL" -o headings.json
   curl -s "$B/eeat-checker?url=$URL" -o eeat.json
   curl -s "$B/ai-overview-eligibility-checker?url=$URL" -o aio.json
   curl -s "$URL" -o page.html
   python3 check_page.py page.html
   ```
   Read:
   - `headings.json` `report.counts` and `report.issues`: one h1, no `skipped-level`, `empty` or `image-only` issues.
   - `eeat.json` `report.jsonLd.invalid` must be 0 (it parses every JSON-LD block), `report.jsonLd.types` must include `FAQPage`, and `report.signals[]` lists 11 trust signals found or missing (byline, author link, Article schema, dates shown and in markup, About and Contact links, outbound sources).
   - `aio.json` `report.verdict` must be `eligible`.
   - `check_page.py`: the FAQPage question count, that every Question has an answer, and the words between the h1 and the first h2. If the first 60 words printed are not the answer, move the answer up.

6. Fix what failed and run step 5 again. Report: the answer block word count, table present, FAQ count, JSON-LD types, trust signals found out of 11, eligibility verdict.

## Example output (real run, www.ayrank.com/blog/how-to-rank-in-chatgpt, 15 Nov 2026)

`check_page.py`:
```text
JSON-LD types: ['Organization', 'WebSite', 'Article', 'BreadcrumbList', 'FAQPage']
FAQPage questions: 8 | every Question has acceptedAnswer.text: True
Words between the h1 and the first h2: 599
First 60 words: This post is part of our AI SEO guide . Related reading: Best AI SEO Agencies , How to Choose an AI SEO Agency , Best Reddit Citation Services . About the Author [...]
Tables on the page: 4
```

`heading-outline-checker`, trimmed:
```json
{
  "status": 200,
  "report": {
    "total": 26,
    "counts": {"h1": 1, "h2": 13, "h3": 12, "h4": 0, "h5": 0, "h6": 0},
    "issues": [],
    "title": "How to Rank in ChatGPT in 2026 (Step-by-Step) | AY Rank"
  }
}
```

`eeat-checker`, trimmed:
```json
{
  "report": {
    "found": 8,
    "total": 11,
    "jsonLd": {"blocks": 5, "invalid": 0, "types": ["Organization", "Person", "WebSite", "Article", "WebPage", "BreadcrumbList", "FAQPage", "Question", "Answer"]},
    "signals": [
      {"id": "byline", "found": true},
      {"id": "author_link", "found": false},
      {"id": "article_schema", "found": true},
      {"id": "published_visible", "found": true},
      {"id": "updated_visible", "found": false},
      {"id": "updated_markup", "found": true},
      {"id": "contact_link", "found": false}
    ]
  }
}
```

What the skill reported: headings clean, 5 valid JSON-LD blocks with an 8-question FAQPage, 4 tables, 8 of 11 trust signals. Three fixes: the first 60 words after the h1 are a "related reading" line and the author box, so the answer block sits too low and should move up; the byline has no link to an author page; the updated date is in the markup but not shown on the page.

## Manual fallback

- Paste the page URL into https://validator.schema.org to see every JSON-LD block parsed.
- Count the words under the H1 by hand: select the text up to the first H2 and paste it into any word counter.
- The heading and trust checks run in the browser at https://www.ayrank.com/tools/heading-outline-checker and https://www.ayrank.com/tools/eeat-checker.

## Powered by AY Rank

Powered by [AY Rank free SEO and GEO tools](https://www.ayrank.com/tools?utm_source=github&utm_medium=skill&utm_campaign=ayrank-skills&utm_content=ayrank-answer-first-page): the heading outline checker, the E-E-A-T checker, the AI Overviews eligibility checker and the FAQ schema generator.
