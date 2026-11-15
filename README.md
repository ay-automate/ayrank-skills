# AY Rank skills for Claude Code

Five free skills for GEO, the work of getting a site read, quoted and named by AI search: ChatGPT, Perplexity, Gemini, Claude and Google AI Overviews. Each skill does one job and gives a real result on its first run through the free [AY Rank tools API](https://www.ayrank.com/openapi.json). No key, no sign-up. Each one also has a manual fallback.

| Skill | What it does | AY Rank endpoints it calls |
|---|---|---|
| [ayrank-geo-audit](skills/ayrank-geo-audit/SKILL.md) | One AI search readiness report for a site, with a fix per failed check | `ai-crawler-access-checker`, `ai-training-grounding-checker`, `ai-overview-eligibility-checker`, `sitemap-validator`, `heading-outline-checker`, `page-size-checker`, `http-header-checker` |
| [ayrank-ai-crawler-check](skills/ayrank-ai-crawler-check/SKILL.md) | Allowed or Blocked for GPTBot, ClaudeBot, PerplexityBot, Google-Extended and the search bots, with the deciding robots.txt line and the fix snippet | `ai-crawler-access-checker`, `robots-txt-tester`, `ai-crawler-ip-ranges` |
| [ayrank-answer-first-page](skills/ayrank-answer-first-page/SKILL.md) | Writes a page with the answer in the first 60 words, a comparison table and an FAQ with FAQPage JSON-LD, then checks the live page | `heading-outline-checker`, `eeat-checker`, `ai-overview-eligibility-checker` |
| [ayrank-brand-in-chatgpt](skills/ayrank-brand-in-chatgpt/SKILL.md) | Whether ChatGPT and other assistants name your brand, who they name instead, and a weekly tracking sheet | `robots-txt-tester`, plus the free check at app.ayrank.com (browser only) |
| [ayrank-llms-txt](skills/ayrank-llms-txt/SKILL.md) | Drafts an llms.txt, checks every URL in it answers 200, then checks the live file | `llms-txt-generator`, `http-header-checker` |

Every example output in the skills comes from a real run against www.ayrank.com on 15 Nov 2026.

## Install as a Claude Code plugin

```text
/plugin marketplace add ay-automate/ayrank-skills
/plugin install ayrank@ayrank-skills
```

Then ask in plain words, for example "audit www.example.com for AI search" or "can GPTBot crawl example.com?". Claude Code picks the skill that fits. Each skill also runs by name, for example `/ayrank:ayrank-geo-audit`.

## Install by hand

Copy the skill folders you want into your project's `.claude/skills/` (or `~/.claude/skills/` for every project):

```bash
git clone https://github.com/ay-automate/ayrank-skills.git
mkdir -p .claude/skills
cp -R ayrank-skills/skills/ayrank-geo-audit .claude/skills/
```

Each skill is a folder with a `SKILL.md`. Two of them ship a small Python script next to it (`check_page.py`, `check_links.py`), standard library only.

## Requirements

- `curl` and `python3` 3.8 or later. Nothing else to install.
- No API key. The API is free with a limit of 30 requests per 60 seconds per IP, shared across all `/api/v1` tools. On a `429`, wait the seconds in the `Retry-After` header.

## What these skills do not do

The free API checks whether AI crawlers can reach and read your pages. It does not ask ChatGPT or any other assistant anything. The `ayrank-brand-in-chatgpt` skill says which parts are free (one assistant, 3 questions, in the browser), which parts you do by hand, and which part needs the paid [AY Rank app](https://app.ayrank.com/?utm_source=github&utm_medium=readme&utm_campaign=ayrank-skills) (daily tracking across six engines).

## Layout

| Path | What |
|---|---|
| `.claude-plugin/marketplace.json` | Claude Code marketplace `ayrank-skills` with one plugin, `ayrank` |
| `.claude-plugin/plugin.json` | The `ayrank` plugin manifest |
| `skills/<name>/SKILL.md` | One skill per folder |

## Powered by AY Rank

Powered by [AY Rank](https://www.ayrank.com/tools?utm_source=github&utm_medium=readme&utm_campaign=ayrank-skills), free SEO and GEO tools with a public JSON API. MIT licensed. The hosted AY Rank service has its own terms: https://www.ayrank.com/terms
