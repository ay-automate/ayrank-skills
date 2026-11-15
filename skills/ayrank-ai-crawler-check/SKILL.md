---
name: ayrank-ai-crawler-check
description: Check whether GPTBot, ClaudeBot, PerplexityBot and Google-Extended may crawl a site, explain each Allowed or Blocked result with the robots.txt line that decided it, test the search bots (OAI-SearchBot, Claude-SearchBot) too, and hand back the exact robots.txt, meta robots or firewall snippet to fix it. Uses the free AY Rank AI crawler access API, no key. Use when someone says "can ChatGPT crawl my site", "is GPTBot blocked", "check AI crawler access", "block AI bots", "allow ClaudeBot", "robots.txt for AI", "Perplexity can't see my site" or "AI crawler checker".
---

# AI crawler check

Answers one question per bot: may this AI crawler fetch the homepage, and which line says so. Then it writes the fix.

## Setup

- Needs `curl`. Nothing to install.
- No API key. Free public API: https://www.ayrank.com/openapi.json
- Rate limit: 30 requests per 60 seconds per IP across all `/api/v1` tools. This skill makes 2 to 4 calls.

## What each bot does

Blocking a training bot does not remove a site from that company's search answers. They are separate tokens.

| Token | Company | Used for | Checked by |
|---|---|---|---|
| GPTBot | OpenAI | model training | `ai-crawler-access-checker` |
| OAI-SearchBot | OpenAI | ChatGPT search results | `robots-txt-tester` |
| ClaudeBot | Anthropic | model training | `ai-crawler-access-checker` |
| Claude-SearchBot | Anthropic | Claude search results | `robots-txt-tester` |
| PerplexityBot | Perplexity | Perplexity search index | `ai-crawler-access-checker` |
| Google-Extended | Google | Gemini training and grounding. Not Google Search, not AI Overviews | `ai-crawler-access-checker` |

Google AI Overviews and AI Mode use Googlebot, so blocking Google-Extended does not take a site out of them.

## Steps

1. Get the domain, for example `example.com`. Run the main check:
   ```bash
   curl -s "https://www.ayrank.com/api/v1/ai-crawler-access-checker?domain=example.com" -o crawler.json
   ```

2. Read `report.bots[]`. For each bot:
   - `allowed`: true or false for the homepage path `/`.
   - `line.text` and `line.line`: the robots.txt line that decided it. `reason` is `rule` when a line matched; other values (`no-rule-matched`, `no-group`, `file-unavailable`, `file-unreachable`) explain a default.
   - `via`: `named` (a `User-agent: GPTBot` group) or `wildcard` (the `User-agent: *` group).
   - `pageRules`: meta robots and X-Robots-Tag rules on the homepage that apply to all robots or name the bot. A `noindex` here keeps the page out of answers even when robots.txt allows the crawl.
   - `robots.status`: a 4xx robots.txt allows everything, a 5xx or no answer blocks everything (RFC 9309).

3. Test the search bots and any path that matters (a blog post, `/pricing`) with the robots.txt tester:
   ```bash
   curl -s "https://www.ayrank.com/api/v1/robots-txt-tester?url=https://example.com/&userAgent=OAI-SearchBot" -o oai-search.json
   curl -s "https://www.ayrank.com/api/v1/robots-txt-tester?url=https://example.com/&userAgent=Claude-SearchBot" -o claude-search.json
   ```
   Read `allowed` and `result.decision.rule.text`.

4. Explain each result in one line: bot, Allowed or Blocked, the deciding line, what it means for that company's answers.

5. Give the fix the owner asked for. Ask first if it is not clear whether they want AI training allowed. Snippets:

   Allow search bots, block training bots (the common middle ground):
   ```text
   User-agent: OAI-SearchBot
   Allow: /

   User-agent: Claude-SearchBot
   Allow: /

   User-agent: PerplexityBot
   Allow: /

   User-agent: GPTBot
   Disallow: /

   User-agent: ClaudeBot
   Disallow: /

   User-agent: Google-Extended
   Disallow: /
   ```

   Allow every AI bot on a site that blocks them under `*`: add a named group per bot with `Allow: /`. A named group replaces the `*` group for that bot. It does not add to it, so copy any `Disallow` lines you still want (admin, cart, search pages) into each named group.

   A homepage `noindex` the owner did not mean to set: remove `<meta name="robots" content="noindex">` from the page head, or the `X-Robots-Tag: noindex` header from the server or CDN config.

6. Warn about what the API cannot see. It sends an AY Rank user agent, not the bots' own, so a CDN or firewall rule that only fires for the real GPTBot is invisible to it. To allow the real bots through a firewall, allowlist their published IP ranges, which this endpoint collects from each vendor's own file:
   ```bash
   curl -s "https://www.ayrank.com/api/v1/ai-crawler-ip-ranges" -o ip-ranges.json
   ```
   `lists[].id` names the list (`openai-gptbot`, `perplexity-bot` and so on), `lists[].prefixes` holds the CIDR ranges and `lists[].url` the vendor's source file.

## Example output (real run, www.ayrank.com, 15 Nov 2026)

`crawler.json`, trimmed:
```json
{
  "domain": "www.ayrank.com",
  "homepage": {"url": "https://www.ayrank.com/", "status": 200, "readable": true, "xRobotsTag": []},
  "robots": {"url": "https://www.ayrank.com/robots.txt", "status": 200, "found": true},
  "report": {
    "bots": [
      {
        "token": "GPTBot", "vendor": "OpenAI", "kind": "training",
        "allowed": true, "reason": "rule", "via": "named",
        "line": {"line": 29, "text": "Allow: /"},
        "agentLines": [{"line": 28, "text": "User-agent: GPTBot"}],
        "pageRules": [{"source": "meta", "scope": "all", "rule": "index", "raw": "<meta name=\"robots\" content=\"index, follow\">"}]
      },
      {"token": "ClaudeBot", "allowed": true, "via": "named", "line": {"line": 32, "text": "Allow: /"}},
      {"token": "PerplexityBot", "allowed": true, "via": "named", "line": {"line": 11, "text": "Allow: /"}},
      {"token": "Google-Extended", "robotsOnly": true, "allowed": true, "via": "named", "line": {"line": 38, "text": "Allow: /"}}
    ],
    "allowedCount": 4,
    "blockedCount": 0,
    "groupCount": 16
  },
  "checkedAt": "2026-11-15T15:17:44.891Z",
  "poweredBy": {"text": "Powered by AY Rank", "url": "https://www.ayrank.com/tools/ai-crawler-access-checker"}
}
```

Search bots, from `robots-txt-tester`:
```text
OAI-SearchBot     allowed  line 5   "Allow: /"  via named group
Claude-SearchBot  allowed  line 14  "Allow: /"  via named group
```

One finding the same run turned up. The site's `User-agent: *` group has `Disallow: /api/`, but GPTBot has its own group with only `Allow: /`. Testing `https://www.ayrank.com/api/v1/title-scorer` for GPTBot:
```json
{"path": "/api/v1/title-scorer", "userAgent": "GPTBot", "allowed": true,
 "decision": {"reason": "rule", "rule": {"pattern": "/", "line": 29, "text": "Allow: /"}, "via": "named"}}
```
The `/api/` block applies only to bots with no group of their own. The fix is to repeat `Disallow: /api/` inside each named group that should respect it.

## Manual fallback

- Open `https://<site>/robots.txt`. For each bot, find a group whose `User-agent` line names it (case does not matter). If none, use the `User-agent: *` group. Within that group the longest matching path wins, and `Allow` wins a tie.
- View the homepage source and search for `name="robots"`. Check response headers with `curl -sI https://<site>/ | grep -i x-robots-tag`.
- The same check runs in the browser at https://www.ayrank.com/tools/ai-crawler-access-checker.

## Powered by AY Rank

Powered by the [AY Rank AI Crawler Access Checker](https://www.ayrank.com/tools/ai-crawler-access-checker?utm_source=github&utm_medium=skill&utm_campaign=ayrank-skills&utm_content=ayrank-ai-crawler-check), free and with no sign-up.
