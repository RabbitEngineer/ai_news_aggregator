# Application Architecture

## What this application does

A **daily AI news digest published as a static website on GitHub Pages**. Once a
day it collects news about AI, Azure AI services, and AI infrastructure tooling,
has an LLM select and summarize the most interesting items, stores the result as
JSON, and rebuilds a static site from every stored edition.

It is built for a specific reader: an **Azure infrastructure architect who
deploys and hosts AI services on Azure**, and who is relatively new to the
architect role — so every featured item carries a plain-language "why it
matters" naming the decision or action it affects.

Three sections:

1. **Azure Updates** — the whole platform, not only the AI services. In priority
   order: AI services and models on Azure; pricing and billing changes anywhere;
   core platform news an infrastructure architect acts on (compute, networking,
   storage, identity, AKS, security, resilience, governance, regions); and
   deprecations or breaking changes, which are high-value because they carry a
   deadline. Dynamics/Power Platform and minor SDK releases are excluded.
2. **General AI News** — model releases and capability jumps; how the new models
   actually perform (benchmarks, head-to-heads, credible regression reports);
   and big industry news. Funding gossip and thin takes are excluded.
3. **AI Infrastructure & Tooling** — the layer between a model and a running
   product: n8n, Kong, LiteLLM, vLLM, Ollama, agent frameworks, vector DBs.
   Only releases that add a notable capability or break something.

Design goal: **near-zero cost**. Free RSS feeds, free GitHub Actions, free
GitHub Pages, and exactly **one LLM call per day** (~$5-7/year on the default
model, measured). The repository must be public: GitHub Pages on a private repo
requires a paid plan, which would cost ten times the rest of the project.
The LLM call goes through OpenRouter, so one API key reaches every vendor and
switching model is one repo variable.

## How it works

```
GitHub Actions cron (daily 06:00 UTC)
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ main.py                                                      │
│                                                              │
│  1. FETCH      Pull all items from 24 RSS feeds, all in      │
│                one concurrent pool                            │
│                • All sections: last 24h (one day per run),   │
│                  stretched if a previous run was missed       │
│                • Azure: no keyword filter, whole platform     │
│                • Tooling: max 4 items/feed                    │
│                • Cap every section at 40 candidates           │
│                                                              │
│  2. DEDUPE     Load digests/*.json, drop any candidate        │
│                whose link appeared in the last 7 editions     │
│                                                              │
│  3. CURATE     ONE LLM call via OpenRouter, returning         │
│                structured JSON: featured items with a         │
│                "why it matters", plus one-line mentions       │
│                                                              │
│  4. STORE      Write digests/<date>.json                      │
│                                                              │
│  5. BUILD      render.py rebuilds the WHOLE site from every   │
│                stored edition: index, per-day archive pages,  │
│                archive list, Atom feed                        │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
Workflow commits digests/, then deploys site/ to GitHub Pages
        │
        ▼
https://<user>.github.io/<repo>/   (+ feed.xml for an RSS reader)
```

Key design decisions:

- **Curation happens in the LLM, not in code.** Everything in the time window
  goes to the model (input tokens are cheap) and *it* decides what matters —
  selection by importance, not recency. This is also how patch-release noise is
  filtered: the prompt says to drop routine releases, rather than trying to
  encode that in keyword matching.
- **The model returns JSON, not prose.** Presentation lives entirely in
  `render.py`. Parsing prose back into styled HTML is fragile, and structured
  data cleanly feeds the page, the archive, and the feed.
- **Stored digests are both the archive and the de-duplication state.** No
  database, no separate state file. The lookback windows overlap the daily
  cadence on purpose so nothing slips through a gap; de-duplication is what
  makes that free of repetition.
- **The whole site rebuilds every run.** A template or palette change reflows
  every past edition, not just today's — the alternative would leave the archive
  frozen at whatever the design was on the day it was written.
- **A full rebuild also runs on quiet days.** When nothing new survives
  de-duplication the LLM call is skipped, but the site is still rebuilt, so a
  design change reaches the site without waiting for news.
- **Tooling is discovered from general sources, not per-project feeds.** The
  section used one GitHub release feed per tool. Two problems: a per-project feed
  can only report on tools already tracked, so nothing new is ever discovered;
  and point releases dominated its volume. General coverage (Show HN, trade
  press) answers both "what appeared" and "what changed materially", and skips
  the patch notes by construction.
- **Publications and official sources only.** Reddit was trialled (r/AZURE for
  outage chatter, r/LocalLLaMA for open-weight launches) and removed: the signal
  came wrapped in opinion, support questions and venting. Azure community ground
  is covered instead by six official Microsoft Tech Community boards. Note there
  is no first-party Azure incident feed to subscribe to — Microsoft retired the
  status RSS feed and every published URL now 404s.
- **No feed appears in two sections, and `drop_cross_section()` enforces it
  anyway.** Sections are assembled from separate lists and de-duplicated
  independently, so a publication covering both AI and tooling would otherwise
  offer the same story to both and the model could place it twice.
- **Per-feed caps keep one busy publication from filling a section.**
  `NEWS_MAX_ITEMS_PER_FEED` (8) and `TOOLING_MAX_ITEMS_PER_FEED` (6); SiliconANGLE
  alone runs ~10 items a day against one or two from the slower sources.
- **No keyword filter on Azure.** The section used to be keyword-filtered to AI
  items, which excluded the rest of the platform — networking, compute, identity,
  deprecations — all squarely this reader's job. Volume is far below the section
  cap, so selection stays where the design puts it: in the LLM, not a keyword list.
- **Sections are fixed and independent.** All three always render, in the same
  order, and none borrows capacity from another. With 24h windows a section is
  empty on roughly a third of days; it keeps its heading and reads "No news."
  rather than disappearing, so a quiet source is visibly distinct from a broken
  one. Each section is judged only on its own candidates.
- **One day per run, with catch-up.** All windows are 24h, matching the daily
  cadence. Measured over 28 days, that leaves a section empty on 28–39% of days,
  because every source publishes in bursts and rests at weekends; the digest
  reports "nothing noteworthy" rather than padding. The windows are env vars, so
  fuller coverage is a config change (240h took Azure from ~0–2 candidates to
  ~28). `effective_window()` stretches a window by a day for each missed edition,
  because scheduled Actions runs are regularly delayed and sometimes dropped —
  without it, a skipped day's news would be lost by every future edition too.
- **De-duplication must outlast the widest window.** `DEDUP_EDITIONS` (7) spans
  more days than a 24h window plus any realistic catch-up stretch. Widening a
  window past that without raising it would make old items resurface.
- **Per-feed cap on the tooling section only.** Release feeds are bursty — one
  project cutting three patch releases could otherwise fill the candidate pool.
  `TOOLING_MAX_ITEMS_PER_FEED` (4) bounds each source there. The news sections
  are deliberately uncapped per feed: a busy day at one outlet is real signal,
  and an early version of this capped away 4 of TechCrunch's 9 AI stories.
- **One provider, every model.** All inference goes through OpenRouter over the
  OpenAI-compatible `/chat/completions` shape, rather than a vendor SDK. One key,
  no per-token markup, day-one access to new models, automatic failover.
- **Both the model's output and the feeds' content are treated as untrusted.**
  RSS is publishable by anyone, so a feed item could attempt prompt injection;
  the system prompt declares candidate text to be data, never instructions.
  Model output is escaped everywhere it is rendered, and the tag value is
  whitelisted before it reaches a `style` attribute.
- **Every URL the model returns is
  checked against the candidate links that were actually sent to it
  (`sanitize_urls`). This closes two holes at once: a `javascript:` or `data:`
  URL would otherwise land in an `href` on a public page, and models
  occasionally invent a plausible URL, which would publish a dead link. An
  unverifiable link is stripped while the item's text is kept.
- **All feeds fetch concurrently.** `prefetch()` warms one cache for all three
  sections before any is assembled, so the run is paced by the single slowest
  feed rather than the sum of three. Measured: 14.4s sequential to 8.6s.
- **Output tokens are capped tightly** (`MAX_OUTPUT_TOKENS`, 4000). Observed
  output is ~1.1K and the prompt caps item counts, so this never truncates a
  real digest, but it bounds worst-case spend if a model tries to ramble.
- **Graceful degradation.** A broken feed is skipped with a warning. Malformed
  JSON is repaired where possible (code fences, prose wrappers) before failing.
  Expected failures print guidance instead of a traceback.

## Files

| File | Purpose |
|---|---|
| `main.py` | Orchestration. Configuration at the top (model, feed lists, keyword filter, caps), then feed fetching, the digest prompt + `summarize` / `parse_digest`, storage (`load_editions`, `save_digest`), de-duplication, and `build_site`. |
| `render.py` | All presentation. Turns stored digests into `index.html`, per-day archive pages, the archive list, and `feed.xml`. The `CSS` constant holds every colour token with a light and dark value. |
| `.github/workflows/daily-digest.yml` | Daily cron + manual trigger. Runs the build, commits `digests/`, then publishes `site/` to GitHub Pages via `upload-pages-artifact` / `deploy-pages`. |
| `digests/<date>.json` | One stored edition. Committed by the workflow — the archive and the de-duplication state. |
| `requirements.txt` | `openai` (the OpenAI-compatible client, pointed at OpenRouter) and `feedparser`. |
| `README.md` | Setup guide, model choice, troubleshooting, cost. |
| `application_architecture.md` | This document. |

### Important places inside `main.py`

| What | Where |
|---|---|
| Model default | `DEFAULT_MODEL` (top of the config block) |
| General AI news sources | `AI_FEEDS` |
| Azure news sources (all of Azure) | `AZURE_FEEDS` |
| Per-feed caps | `NEWS_MAX_ITEMS_PER_FEED` (8), `TOOLING_MAX_ITEMS_PER_FEED` (6) |
| Cross-section de-duplication | `drop_cross_section()` |
| Infrastructure/tooling sources | `TOOLING_FEEDS` |
| Candidate cap per section | `MAX_CANDIDATES_PER_SECTION` (40) |
| Candidate cap per feed (tooling only) | `TOOLING_MAX_ITEMS_PER_FEED` (4) |
| How many past editions de-duplication spans | `DEDUP_EDITIONS` (7) |
| Catch-up after a missed run | `effective_window()` |
| Reader profile / what counts as interesting | `SYSTEM_PROMPT` |
| Items per section | the `Length target:` block inside `SYSTEM_PROMPT` |
| Where digests and the site are written | `DIGEST_DIR`, `SITE_DIR` |

## How to change the model

One environment variable — no code change, no second API key:

| Variable | Default |
|---|---|
| `MODEL` | `anthropic/claude-haiku-4.5` |

Set it as a repo **variable** (Settings → Secrets and variables → Actions →
Variables tab); the next run picks it up with no commit. Locally,
`$env:MODEL = "openai/gpt-5-mini"`. Because everything routes through
OpenRouter, switching vendor is the same operation as switching model. Use
OpenRouter's exact slug — `anthropic/claude-haiku-4.5` is a dot, not a dash.

## How to tune digest length

The per-section counts live in the `Length target:` block of `SYSTEM_PROMPT`:

| Section | Featured | "Also noted" |
|---|---|---|
| Azure Updates | 5 | 6 |
| General AI News | 5 | 6 |
| AI Infrastructure & Tooling | 3 | 4 |

They are ceilings, not quotas. "Also noted" is the cheap dial — each entry costs
one scannable line, so raise those for more awareness without lengthening the
read. Lower the featured counts for a faster read.

## How to change news sources

Edit the feed lists at the top of `main.py`. Each entry is a
`("Display Name", "https://feed-url")` tuple:

- **General AI news** → `AI_FEEDS`. Not keyword-filtered; everything recent is a
  candidate.
- **Azure news** → `AZURE_FEEDS`. No keyword filter: the whole platform is in
  scope and the LLM judges relevance. Eight sources.
- **Infrastructure/tooling** → `TOOLING_FEEDS`. Every GitHub project publishes a
  release feed at `https://github.com/<owner>/<repo>/releases.atom`. Release
  feeds are noisy by nature; `TOOLING_MAX_ITEMS_PER_FEED` and the "skip routine
  patch releases" rule in `SYSTEM_PROMPT` handle that.

Broken feeds are skipped with a warning, so a typo won't break the digest.

## Running and maintaining

### First-time setup

1. Push to GitHub.
2. Add the `OPENROUTER_API_KEY` secret.
3. **Settings → Pages → Source: GitHub Actions.** Do not pick a branch.
4. Actions → Daily AI News Digest → Run workflow.

### Running

- **Automatic:** the cron in the workflow runs daily at 06:00 UTC.
- **Manual:** Actions tab → Run workflow.
- **Locally:** `pip install -r requirements.txt`, set `OPENROUTER_API_KEY`, run
  `python main.py`. Writes `digests/` and `site/`; open `site/index.html` to
  preview. Nothing is published.

### Maintenance

This is low-maintenance — no server, no database. Occasionally:

- **Site not updating?** Check the Actions tab for a red run. The log names the
  cause (missing key, bad model slug, malformed JSON). A green run with "Nothing
  new since the last edition" means there was genuinely no news.
- **First deploy fails?** Almost always Pages source not set to GitHub Actions.
- **Feed warnings** (`WARNING: could not parse ...`): the URL moved or the site
  is down. Update or remove the entry in `main.py`.
- **GitHub disables crons after ~60 days without repo activity.** The workflow
  commits a digest most days, which counts as activity, so this is unlikely —
  but if digests stop and there is a banner in the Actions tab, click "Enable
  workflow".
- **API costs:** visible at [openrouter.ai/activity](https://openrouter.ai/activity).
  Expect cents per year on the default model.
- **Digest quality drifting?** Tune the reader profile in `SYSTEM_PROMPT`, or
  move `MODEL` up a tier.
