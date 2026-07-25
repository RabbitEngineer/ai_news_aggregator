# AI News Aggregator

A daily digest for an Azure infrastructure architect, published as a **free
GitHub Pages website** that rebuilds itself every morning. Three sections:
**Azure updates** across the whole platform — AI services, pricing, networking,
compute, identity, deprecations — plus **general AI news** (what's new and how
new models actually perform) and **AI infrastructure tooling** (n8n, Kong,
LiteLLM, vLLM and friends).

Runs free on GitHub Actions. The only cost is one LLM call per day — about
**$5–7 a year** with the default model.

## How it works

1. **Fetch** — pulls recent items from free RSS feeds. No news API keys needed.
   - *Azure*: Azure Updates, Azure Blog, Azure AI Foundry Blog, plus the Azure
     Architecture, Infrastructure, Networking, Compute and DevOps blogs, plus
     six **official Microsoft Tech Community boards** (Azure Community,
     Governance, Storage, Migration, Apps on Azure, Integration). The whole
     platform is in scope, not just AI, and **Azure OpenAI is the
     highest-priority topic** within it.
   - *General AI*: TechCrunch, The Verge, VentureBeat, MIT Tech Review, Ars
     Technica, The Register, SiliconANGLE, IEEE Spectrum — news publications —
     plus OpenAI News and Hugging Face as first-party sources.
   - *Infrastructure & tooling*: InfoQ AI/ML, The New Stack, GitHub Blog, and
     Hacker News / Show HN for discovery. See below for why.

No Reddit, no personal blogs, no per-project release feeds. No source appears in
two sections, and a story picked up by one section is excluded from the others.
2. **De-duplicate** — anything covered by the last 7 editions is dropped, so a
   story is reported once even if a window stretches to cover a missed run.
3. **Curate + summarize** — all remaining candidates (up to 40 per section) go to
   one LLM call, which returns structured JSON: what to feature, what to merely
   list, and a plain-language *"why it matters"* for each featured item.
4. **Publish** — the digest is saved to `digests/<date>.json`, the whole site is
   rebuilt from every stored edition, and GitHub Pages serves it.

## What you get

| URL | |
|---|---|
| `/` | today's digest |
| `/archive/` | every past edition, newest first |
| `/archive/<date>.html` | one page per edition |
| `/feed.xml` | Atom feed — subscribe in any RSS reader to get a notification |

Each section has two tiers, so you get depth on what matters *and* still see
everything else. Target read time is **3–4 minutes**.

| Section | Featured | "Also noted" |
|---|---|---|
| Azure Updates | up to 5 | up to 6 |
| General AI News | up to 5 | up to 6 |
| AI Infrastructure & Tooling | up to 3 | up to 4 |

These are ceilings, not quotas — the prompt forbids padding, so an item has to
earn its place and a quiet day produces a genuinely short digest. A realistic
weekday lands around 12–18 items.

**"Also noted" is not just a list of headlines** — each entry carries a
one-sentence summary of what the item actually says, plus its own "Read more"
link, so you can decide from that line alone whether to open it.

**The three sections are fixed and independent.** All three always appear, in the
same order. A section with nothing in the last 24 hours simply reads *"No news."*
and the digest moves on to the next one — sections never borrow from each other,
so each is judged only on its own candidates.

The site follows your system light/dark preference and is readable on a phone.

## Getting started

Roughly 15 minutes, most of it waiting for GitHub. You need a GitHub account and
about €4 of OpenRouter credit to cover the first year.

### Step 1 — Get an OpenRouter API key

1. Sign up at [openrouter.ai](https://openrouter.ai).
2. Add credit at [openrouter.ai/credits](https://openrouter.ai/credits). **€5 is
   plenty** — this app costs about €3.90 a year. (OpenRouter charges ~5.5% when
   you top up, so €5 becomes about €4.72 of usable credit.)
3. Go to [openrouter.ai/keys](https://openrouter.ai/keys) → **Create Key**, name
   it something like `ai-news-digest`, and copy the value. It starts with
   `sk-or-v1-`.

   **Copy it now** — OpenRouter shows a key once and never again. If you lose it,
   delete the key and make a new one.

### Step 2 — Put this code in your own GitHub repository

Create an empty repo on GitHub (**New repository**, no README, no .gitignore),
then from this folder:

```bash
git init -b main                 # skip if this is already a git repo
git add -A
git commit -m "AI news digest"
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

**Make the repository public.** On GitHub's Free plan, Pages only works from
public repositories — publishing from a private repo requires GitHub Pro
(~$4/month, i.e. ~$48/year, far more than everything else here combined). The
site only ever contains links to public news articles, so there is nothing
sensitive in it. Your API key lives in Actions secrets, which stay private even
on a public repo.

A public repo is also free for unlimited Actions minutes; private repos draw
from a 2,000-minute monthly allowance (this app uses roughly 60).

### Step 3 — Add your API key as a repository secret

In your repo on GitHub: **Settings → Secrets and variables → Actions →
New repository secret**

| Field | Value |
|---|---|
| Name | `OPENROUTER_API_KEY` |
| Secret | the `sk-or-v1-...` key from step 1 |

Click **Add secret**. This is the only credential the project needs — everything
else uses the `GITHUB_TOKEN` that Actions provides automatically.

> A secret is write-only: GitHub will never show it back to you, and it is not
> visible in logs. To change it later, overwrite it here.

### Step 4 — Turn on GitHub Pages

**Settings → Pages → Build and deployment → Source**, and choose
**GitHub Actions**.

> This is the step people miss. Pick the *source*, not a branch — do **not**
> select "Deploy from a branch". If you skip this, everything runs fine and the
> final deploy step fails.

### Step 5 — Run it once by hand

**Actions** tab → **Daily AI News Digest** in the left sidebar → **Run workflow**
→ **Run workflow**.

> If the Actions tab shows "Workflows aren't being run on this forked
> repository", click the button to enable them.

It takes about a minute. Click into the run to watch. A healthy log looks like:

```
Using model: anthropic/claude-haiku-4.5
Collected 15 AI items, 28 Azure items, and 27 tooling items
LLM call: model=anthropic/claude-haiku-4.5 in=8200 out=1200 tokens
Saved digests/2026-07-25.json
Built site/ with 1 edition(s)
Site will publish at https://<you>.github.io/<your-repo>/
```

### Step 6 — Open your site

`https://<your-username>.github.io/<your-repo>/`

The first deploy can take a couple of minutes to go live. The URL is also shown
on the workflow run page and under **Settings → Pages**.

That's it — from now on it runs itself every day at 06:00 UTC. Day one has a
single edition; the archive fills in as it goes.

### Optional — get notified instead of remembering to look

The site publishes an Atom feed at `/feed.xml`. Add that URL to any RSS reader
(Feedly, NetNewsWire, Thunderbird, Outlook) and new editions come to you.

### Optional — change the time

Edit the `cron` line in `.github/workflows/daily-digest.yml`. It is UTC, and
does not follow daylight saving:

```yaml
- cron: "0 6 * * *"   # 06:00 UTC = 07:00 German winter, 08:00 summer
```

### If something goes wrong

See [When something goes wrong](#when-something-goes-wrong) below — the run
prints a plain-language explanation rather than a stack trace.

## Choosing the model

Default is `anthropic/claude-haiku-4.5`, measured at **$4.70/yr on a typical day
and $6.65/yr if every digest is completely full** — inside a €7 budget, though
not by much once OpenRouter's top-up fee is added. To change it, set a repo
**variable** named `MODEL` (Settings → Secrets and variables → Actions →
*Variables* tab), or edit `DEFAULT_MODEL` at the top of `main.py`. The variable
wins.

**Why not spend the whole budget?** This job is curation and short editorial
writing, not hard reasoning. Quality here is decided by instruction adherence
(respecting the caps, the tag list, the "don't pad" rule) and natural English in
the "why it matters" line. Frontier reasoning models are built for a different
problem and hit sharply diminishing returns — `openai/gpt-5` does fit at
$6.89/yr, but you would be paying reasoning prices for summarization.

Costs are **per year** for this workload (~5.5K in / 1.2K out, once a day),
priced from OpenRouter's live model list:

| Slug | $/year | |
|---|---|---|
| `anthropic/claude-haiku-4.5` | **4.70 – 6.65** | the default — strong instruction adherence, good editorial prose, reliable JSON |
| `openai/gpt-5.4-mini` | 4.00 – 5.73 | equally defensible, different vendor |
| `google/gemini-3-flash-preview` | 2.70 – 3.82 | cheapest of the genuinely good tier |
| `google/gemini-3.6-flash` | ~8.50 | newest Gemini Flash — now over a €7 budget |
| `openai/gpt-5` | ~11.50 | frontier pricing for a summarisation task |

The range is typical day to completely-full digest. Earlier versions of this
table were based on a smaller output estimate; the "also noted" summaries
roughly doubled output tokens, which is where the increase comes from.

Use OpenRouter's exact slug including punctuation — `anthropic/claude-haiku-4.5`
is a **dot**, not a dash. Check [openrouter.ai/models](https://openrouter.ai/models);
a wrong slug returns a 404 and the run says so.

## Why tooling is sourced from general sites

The tooling section originally tracked one GitHub release feed per project (n8n,
Kong, vLLM, Ollama, LangChain and friends). That was replaced, for two reasons:

- **Nothing new could ever be discovered.** A per-project feed only tells you
  about tools you already track. It cannot surface the framework that did not
  exist last month.
- **Almost all of it was patch noise.** Point releases and dependency bumps
  dominated the volume, and the digest spent its budget filtering them out.

General sources answer the two questions that actually matter — *what has
appeared* and *what changed materially* in the established tools. The trade press
covers major versions and licence changes while ignoring point releases.

Hacker News / Show HN is the one community source kept, because publications
rarely cover a tool on the day it launches — without it the section can only
report on tools that are already established. It is a general aggregator rather
than any project's own feed. Remove those two lines from `TOOLING_FEEDS` if you
want the digest sourced purely from publications.

## Empty sections, and how to get fuller ones

Windows are 24 hours, matching the daily run. All three sources publish in
bursts and go quiet at weekends, so a section will regularly have nothing in it.
Measured over 28 days on the live feeds:

| Section | Days with zero items | Median items/day |
|---|---|---|
| Azure | 10 of 28 (**35%**) | 2 |
| General AI | 8 of 28 (**28%**) | 3 |
| Tooling | 11 of 28 (**39%**) | 1 |

An empty section keeps its heading and simply reads **"No news."**, then the
digest continues to the next section. That is honest rather than padded, and it
tells you the source was checked — as opposed to something being broken.

**If you would rather have fuller sections,** widen the window for that section
with a repo variable — no code change:

| Variable | Try | Effect (measured) |
|---|---|---|
| `AZURE_MAX_AGE_HOURS` | `240` | Azure goes from ~0–2 candidates to ~28 |
| `TOOLING_MAX_AGE_HOURS` | `72` | covers a typical release lull |
| `MAX_AGE_HOURS` | `48` | covers a quiet weekend |

De-duplication means a wider window never repeats an item — it only adds
coverage. If you go past 7 days, raise `DEDUP_EDITIONS` in `main.py` to span it.

**Missed runs are handled automatically.** Scheduled Actions runs are sometimes
delayed or dropped under load. If yesterday's edition is missing, the window
stretches by a day to cover the gap, so nothing is silently lost.

## Security

The model's output is treated as untrusted input, because it is:

- **Every URL is checked against the candidates actually sent to the model.**
  These links land in `href` on a public page, so a `javascript:` or `data:` URL
  would be an XSS vector. Models also invent plausible URLs, which would publish
  dead links. Anything unverifiable loses its link and keeps its text.
- **All model text is HTML-escaped** in every output — page, archive, and Atom
  feed. Verified by parsing the rendered HTML after feeding it script and
  event-handler payloads: zero injected elements.
- **The tag is whitelisted** before it reaches a `style` attribute; an unknown
  value falls back to the neutral style.
- **RSS content is declared untrusted in the prompt.** Anyone can publish an RSS
  item, so a feed entry could try prompt injection. The system prompt tells the
  model that candidate text is data, never instructions.
- **Digest filenames must be a plain ISO date** before they become output paths.

## Why OpenRouter

One key reaches every vendor, so there is never a second account to set up. It
adds no per-token markup (the ~5.5% is charged when you top up credits, so a €10
top-up costs ~€10.55), gets new models on launch day, and fails over
automatically when a provider has a bad minute.

## Running locally

```powershell
pip install -r requirements.txt
$env:OPENROUTER_API_KEY = "sk-or-v1-..."
python main.py
```

This writes `digests/` and `site/` exactly as CI does — open `site/index.html`
in a browser to preview design changes. Nothing is published.

## When something goes wrong

The run explains itself rather than dumping a traceback:

| Symptom in the Actions log | Meaning |
|---|---|
| `OPENROUTER_API_KEY is not set` | Secret missing or misnamed — fails in under a second, before fetching anything |
| `OpenRouter rejected the API key` | Key is wrong or revoked |
| `OpenRouter is out of credits` | Top up at [openrouter.ai/credits](https://openrouter.ai/credits) |
| `OpenRouter has no model called ...` | Bad slug — usually wrong punctuation or a missing `vendor/` prefix |
| `The model did not return JSON` | The chosen model lacks reliable JSON mode; switch to one from the table above |
| `dropped N link(s) the model invented` | Normal and harmless — a hallucinated URL was removed before publishing |
| `ignoring <file> — not a YYYY-MM-DD digest` | A stray file in `digests/`; safe to delete |
| `WARNING: could not parse <feed>` | One feed is down; the digest still ships without it |
| Deploy step fails on the first run | Pages source is not set to **GitHub Actions** (step 3) |

## Cost

**Roughly $5–7 a year, all in.** That is the LLM; everything else is free.

| | Cost |
|---|---|
| GitHub Actions | **Free.** Unlimited minutes on public repos. (A private repo draws on 2,000 free Linux minutes/month; this app uses ~60.) |
| GitHub Pages | **Free** — on a **public** repo. Private repos need GitHub Pro, ~$48/year. |
| News sources | **Free.** Plain RSS, no keys, no quotas. |
| LLM | **~$5–7/year.** One call per day. |

**Measured** token usage per run: ~4,800 input (2,200 of it the prompt, the rest
candidates) and up to ~2,700 output for a completely full digest.

| Model | Full digest every day | Typical day |
|---|---|---|
| `anthropic/claude-haiku-4.5` (default) | $6.65/yr | ~$4.70/yr |
| `openai/gpt-5.4-mini` | $5.73/yr | ~$4.00/yr |
| `google/gemini-3-flash-preview` | $3.82/yr | ~$2.70/yr |

Add ~5.5% for OpenRouter's credit top-up fee, so the default lands near **$7/yr
worst case**. Output is capped at 4,000 tokens, which bounds it.

These are estimates from character counts (~4 chars/token); check the real
figure at [openrouter.ai/activity](https://openrouter.ai/activity) after a week
and switch model if it matters. A €5–10 top-up covers a year comfortably.

## Customizing

- **Feeds**: edit `AI_FEEDS` / `AZURE_FEEDS` / `TOOLING_FEEDS` at the top of
  `main.py`. Any GitHub project exposes a release feed at
  `https://github.com/<owner>/<repo>/releases.atom`. There is no keyword filter
  any more — the LLM decides what is relevant, so adding a source is safe.
- **Lookback windows**: `MAX_AGE_HOURS`, `AZURE_MAX_AGE_HOURS` and
  `TOOLING_MAX_AGE_HOURS`, all **24h** by default to match the daily run. See
  *Empty sections* below before widening — and if you set one past 7 days, raise
  `DEDUP_EDITIONS` to match or old items will resurface.
- **How many items per section**: the caps live in the `Length target:` block of
  `SYSTEM_PROMPT`. "Also noted" is the cheap dial — one line each.
- **What counts as interesting**: edit the reader profile in `SYSTEM_PROMPT` —
  that drives selection, not any code-level filter.
- **Look and feel**: `render.py`. The `CSS` constant holds every colour token,
  with a light and a dark value for each. A full rebuild runs every day, so a
  design change reflows every past edition too.
