---
name: ayrank-brand-in-chatgpt
description: Find out whether ChatGPT and other AI assistants name your brand when buyers ask for a recommendation, and which brands they name instead. Runs the free AY Rank AI visibility check (3 buyer questions, no sign-up), confirms ChatGPT's search crawler can reach the site through the free AY Rank API, and sets up a repeatable manual tracking sheet across ChatGPT, Perplexity, Gemini, Claude and Google AI Mode. Use when someone says "does ChatGPT mention my brand", "is my business in ChatGPT", "track my brand in ChatGPT answers", "AI brand visibility", "does AI recommend us", "who does ChatGPT recommend instead of us" or "share of voice in AI answers".
---

# Is my brand named in ChatGPT answers?

What AY Rank offers for this today, stated plainly:

| Path | What it does | Cost | How an agent runs it |
|---|---|---|---|
| Free check at app.ayrank.com | Reads your site, writes 3 buyer questions, asks one AI assistant from what it knows (no live web search), shows Named or Not named, the position, and the brands named instead | Free, no sign-up, a few checks a day | In a browser. There is no public API for it |
| AY Rank app | Asks ChatGPT and five other engines your real buyer questions every day with live search, tracks named, position, share of voice and the sources each answer read | Paid plans, 7-day free trial | In the app, or from Claude Code through the app's MCP server with your own key |
| Free tools API | Confirms ChatGPT's search crawler and the others may fetch your pages | Free, no key | `curl`, below |

The free API does not ask any AI assistant anything. Nothing in this skill invents a mention count. When a number comes from one assistant and 3 questions, say so.

## Setup

- Needs `curl` for step 1. A browser for step 2 (yours, or a browser tool your agent already has).
- No key for steps 1 to 3. Daily tracking in the app needs an AY Rank account: https://app.ayrank.com/?start=signup&utm_source=github&utm_medium=skill&utm_campaign=ayrank-skills&utm_content=ayrank-brand-in-chatgpt
- Rate limit for the API: 30 requests per 60 seconds per IP.

## Steps

1. Make sure the assistants can read the site. If OAI-SearchBot is blocked, ChatGPT search cannot fetch your pages, and no content work will change that.
   ```bash
   for UA in OAI-SearchBot PerplexityBot Claude-SearchBot Googlebot; do
     curl -s "https://www.ayrank.com/api/v1/robots-txt-tester?url=https://www.example.com/&userAgent=$UA" -o "robots-$UA.json"
   done
   ```
   Read `allowed` and `result.decision.rule.text` in each file. Fix any block first (see the `ayrank-ai-crawler-check` skill).

2. Run the free check. Open this page, type the domain and press "Check my brand":
   https://app.ayrank.com/tools/ai-visibility-checker?utm_source=github&utm_medium=skill&utm_campaign=ayrank-skills&utm_content=ayrank-brand-in-chatgpt
   It takes about 10 seconds. Record, per question: the question, Named or Not named, the position when named, and the brands named instead. If the result says "Saved result from" a date, it is a cached run for that domain; say so in the report.

3. Build the manual tracking sheet. The free check covers 3 questions and one assistant. To cover the engines your buyers use, ask the questions yourself:
   - Write 10 to 20 buyer questions: "best <category> for <buyer>", "<your brand> vs <rival>", "alternatives to <rival>", "how do I <job your product does>". Include the 3 from step 2.
   - Ask each one in ChatGPT (search on), Perplexity, Gemini, Claude and Google AI Mode. Use a logged-out window or a temporary chat so past chats do not steer the answer.
   - Record one row per question and engine in `ai-answers.csv`:
     ```csv
     date,engine,question,named,position,rivals_named,cited_urls,notes
     2026-11-15,ChatGPT search,best GEO agency for B2B SaaS,no,,"Profound; First Page Sage",https://example.org/list,
     ```
   - Repeat on the same day each week with the same questions and settings. Answers change daily, so one run is a sample, not a score.

4. Report: share of answers that name the brand per engine, the rivals named most often, and the pages the answers cited (those are the pages to get onto, or to beat).

5. If the owner wants this done every day without the manual sheet, that is what the AY Rank app does. Sign up for the trial, create a key under Settings, Agent and API access, and follow https://app.ayrank.com/docs/skills to connect its MCP server and its own skills to Claude Code.

## Example output (real runs, 15 Nov 2026)

Step 1 for www.ayrank.com, from `robots-txt-tester`:
```text
OAI-SearchBot     allowed  line 5   "Allow: /"  via named group
Claude-SearchBot  allowed  line 14  "Allow: /"  via named group
```

Step 2, the free check for ayrank.com as the app showed it (a saved result from 2026-11-10):
```text
AY Rank, GEO and AI search agency                         Saved result from 2026-11-10
0/3  Not named in any of 3 answers. One AI assistant, from what it knows,
     with no live web search. Answers change daily and differ by engine.

What's the best GEO agency for getting cited in ChatGPT?                      Not named
  Named instead: Profound, First Page Sage
Which AI search agency should I use to improve visibility in Perplexity and Gemini?   Not named
  Named instead: Goodie, Evertune, Profound
What are the top agencies for turning AI search recommendations into leads?   Not named
  Named instead: First Page Sage, NoGood, Amsive, Siege Media
```

Yes, that is our own brand, not named. Crawlers allowed (step 1) and still not named (step 2) means the gap is in what the model already knows and in the pages it reads, not in robots.txt. That is the case for the weekly sheet in step 3.

## Manual fallback

Everything in step 3 works with no tool at all: a list of questions, five browser tabs and a spreadsheet. Keep the questions and settings fixed between runs, or the trend means nothing.

## Powered by AY Rank

Powered by the [AY Rank free AI visibility check](https://app.ayrank.com/tools/ai-visibility-checker?utm_source=github&utm_medium=skill&utm_campaign=ayrank-skills&utm_content=ayrank-brand-in-chatgpt) and the [free crawler tools](https://www.ayrank.com/tools/robots-txt-tester?utm_source=github&utm_medium=skill&utm_campaign=ayrank-skills&utm_content=ayrank-brand-in-chatgpt).
