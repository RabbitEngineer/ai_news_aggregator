"""What the digest reads, which model writes it, and how long it is kept.

Plain values only — no imports, no logic, so nothing here can break. Everything
else lives next to the code that uses it: windows, caps and paths in main.py,
the editorial prompt in main.py (SYSTEM_PROMPT), the site title, section names
and colours in render.py.

MODEL and KEEP_DIGESTS can also be set as a GitHub repo variable of the same
name (Settings -> Secrets and variables -> Actions -> Variables tab), which
overrides the value here for one run without a commit.

Not here: your API key, which is a repo secret named OPENROUTER_API_KEY.
"""

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

# OpenRouter slug, vendor prefix included — check it at openrouter.ai/models, a
# wrong slug 404s. Cost/year on this workload (~4.8K in, ~2.7K out, once a day):
#   openai/gpt-5.6-luna            $1.10-1.55  default: cheapest, and scores
#                                              above Haiku 4.5 on the Artificial
#                                              Analysis Intelligence Index
#   anthropic/claude-haiku-4.5     $4.70-6.65  previous default, excellent prose
#   openai/gpt-5.4-mini            $4.00-5.73  equally defensible
#   google/gemini-3-flash-preview  $2.70-3.82  cheapest of the good tier
#   openai/gpt-5                     ~$11.50   frontier pricing to summarize
# Repo variable: MODEL
MODEL = "openai/gpt-5.6-luna"

# Change only to point at a different OpenAI-compatible gateway.
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ---------------------------------------------------------------------------
# Feeds
# ---------------------------------------------------------------------------
# ("Display name", "url") pairs. Adding one is safe: there is no keyword filter,
# so the LLM decides relevance and a weak source simply never gets picked. Any
# GitHub project has a feed at github.com/<owner>/<repo>/releases.atom.

# News publications rather than blogs or newsletters. Two first-party exceptions:
# OpenAI News (its releases land there first) and Hugging Face (a hub for
# open-weight releases from many labs, not one vendor's product).
AI_FEEDS = [
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("MIT Technology Review AI", "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
    ("Ars Technica AI", "https://arstechnica.com/ai/feed/"),
    ("The Register AI", "https://www.theregister.com/software/ai_ml/headlines.atom"),
    ("SiliconANGLE", "https://siliconangle.com/feed/"),
    ("IEEE Spectrum AI", "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss"),
    ("OpenAI News", "https://openai.com/news/rss.xml"),
    ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml"),
]

# All of Azure, not only the AI services — networking, compute and identity are
# as much this reader's job as Foundry is. The Tech Community boards cover the
# operational ground the product blogs skip. Microsoft Security Blog is left out
# deliberately: threat intelligence, not platform changes, and very high volume.
AZURE_FEEDS = [
    ("Azure Updates", "https://www.microsoft.com/releasecommunications/api/v2/azure/rss"),
    ("Azure Blog", "https://azure.microsoft.com/en-us/blog/feed/"),
    ("Azure AI Foundry Blog", "https://devblogs.microsoft.com/foundry/feed/"),
    ("Azure Architecture Blog", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=AzureArchitectureBlog"),
    ("Azure Infrastructure Blog", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=AzureInfrastructureBlog"),
    ("Azure Networking Blog", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=AzureNetworkingBlog"),
    ("Azure Compute Blog", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=AzureCompute"),
    ("Azure DevOps Blog", "https://devblogs.microsoft.com/devops/feed/"),
    ("Azure Community", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=Azure"),
    ("Azure Governance", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=AzureGovernanceandManagementBlog"),
    ("Azure Storage", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=AzureStorageBlog"),
    ("Azure Migration", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=AzureMigrationBlog"),
    ("Apps on Azure", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=AppsonAzureBlog"),
    ("Azure Integration", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=IntegrationsonAzureBlog"),
]

# General coverage, not one feed per project: per-project feeds only surface
# tools you already track, and are mostly patch noise. Show HN is the exception,
# because that is where new tools launch before any publication covers them.
# Shares no feed with AI_FEEDS, so the same story can't be offered to both.
TOOLING_FEEDS = [
    ("InfoQ AI/ML", "https://feed.infoq.com/ai-ml-data-eng/"),
    ("The New Stack", "https://thenewstack.io/feed/"),
    ("GitHub Blog", "https://github.blog/feed/"),
    ("Show HN", "https://hnrss.org/show?q=AI"),
    ("Hacker News (agents)", "https://hnrss.org/newest?q=AI+agent"),
]

# ---------------------------------------------------------------------------
# Archive
# ---------------------------------------------------------------------------

# Editions kept on disk and on the site; older ones are deleted. Keep it above
# DEDUP_EDITIONS in main.py (7) — a deleted edition can no longer suppress a
# repeat. 0 keeps every edition forever.
# Repo variable: KEEP_DIGESTS
KEEP_DIGESTS = 14
