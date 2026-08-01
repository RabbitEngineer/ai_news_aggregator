"""Render structured digests into a static website.

The LLM returns structured JSON (see SYSTEM_PROMPT in main.py); all presentation
lives here. Because this is a real website rather than an email, there are none
of the email constraints — this uses modern CSS, custom properties, dark mode,
and responsive layout.

Output tree:
    site/index.html            the latest digest
    site/archive/index.html    every past digest, newest first
    site/archive/<date>.html   one page per digest
    site/feed.xml              Atom feed, so a reader can push new editions
"""

import html
import re
from datetime import datetime, timezone

# Browser tab, page header and RSS feed. Plain text: write "&" as "&".
SITE_TITLE = "AI & Azure Digest"

# Sections in page order. The key must match the one the model returns (see
# SYSTEM_PROMPT in main.py) and a `.section.<key>` colour rule in the CSS below.
# main.py reads its section keys from here. The label is free to change.
SECTIONS = [
    ("azure", "Azure Updates"),
    ("general", "General AI News"),
    ("tooling", "Infrastructure & Tooling"),
]

# The badge on each top item. Keys are the exact values the model may use for
# "tag" — a new one needs adding to SYSTEM_PROMPT and a --tag-<key>-bg/-fg pair
# in the CSS below, or it falls back to the neutral "news" style.
TAG_LABELS = {
    "pricing": "Pricing",
    "new": "New",
    "ga": "GA",
    "preview": "Preview",
    "model": "Model",
    "performance": "Benchmark",
    "deprecation": "Deprecation",
    "security": "Security",
    "release": "Release",
    "news": "News",
}


def esc(value) -> str:
    return html.escape(str(value or ""), quote=True)


def domain(url: str) -> str:
    if not url:
        return ""
    host = re.sub(r"^https?://", "", str(url)).split("/")[0]
    return re.sub(r"^www\.", "", host)


def section_of(digest: dict, key: str) -> dict:
    section = digest.get(key) if isinstance(digest.get(key), dict) else {}
    return {"top": section.get("top") or [], "also": section.get("also") or []}


def item_count(digest: dict) -> int:
    return sum(
        len(section_of(digest, k)["top"]) + len(section_of(digest, k)["also"])
        for k, *_ in SECTIONS
    )


def read_time(digest: dict) -> int:
    words = sum(len(str(t).split()) for t in digest.get("tldr") or [])
    for key, *_ in SECTIONS:
        section = section_of(digest, key)
        for i in section["top"]:
            words += len(f"{i.get('title','')} {i.get('summary','')} {i.get('why','')}".split())
        words += sum(len(str(b.get("title", "")).split()) for b in section["also"])
    return max(1, round(words / 200 + 0.5))


def pretty_date(iso: str) -> str:
    try:
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%A, %d %B %Y")
    except ValueError:
        return iso


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{
  --bg:#f5f7fa; --surface:#fff; --raised:#eaf0f8;
  --ink:#151b22; --muted:#44515e; --faint:#5a6b7d;
  --line:#d5dee7; --line-strong:#b6c4d2;
  --azure:#0b5cad; --general:#6431b4; --tooling:#0a7059;
  --shadow:0 1px 2px rgba(16,24,40,.06),0 8px 24px rgba(16,24,40,.06);
  --tag-pricing-bg:#fdf0d9; --tag-pricing-fg:#7a4700;
  --tag-new-bg:#dff4e7;     --tag-new-fg:#0c5c33;
  --tag-ga-bg:#dff4e7;      --tag-ga-fg:#0c5c33;
  --tag-preview-bg:#ece4fd; --tag-preview-fg:#51349a;
  --tag-model-bg:#dfebfb;   --tag-model-fg:#0d3d71;
  --tag-performance-bg:#d8f2f0; --tag-performance-fg:#08544f;
  --tag-deprecation-bg:#fce2e2; --tag-deprecation-fg:#8f1c1c;
  --tag-security-bg:#fce2e2;    --tag-security-fg:#8f1c1c;
  --tag-release-bg:#e6ebf1; --tag-release-fg:#3b4a5d;
  --tag-news-bg:#e6ebf1;    --tag-news-fg:#3b4a5d;
}
@media (prefers-color-scheme:dark){
  :root{
    --bg:#0e1318; --surface:#171e26; --raised:#1c2833;
    --ink:#e4ebf3; --muted:#a6b4c3; --faint:#8090a1;
    --line:#252f3a; --line-strong:#38434f;
    --azure:#5aa7f0; --general:#ad8bf5; --tooling:#3cc0aa;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.3);
    --tag-pricing-bg:#3d2f14; --tag-pricing-fg:#f2c572;
    --tag-new-bg:#12331f;     --tag-new-fg:#79d9a2;
    --tag-ga-bg:#12331f;      --tag-ga-fg:#79d9a2;
    --tag-preview-bg:#2a2145; --tag-preview-fg:#c0a6f7;
    --tag-model-bg:#132844;   --tag-model-fg:#8cbdf2;
    --tag-performance-bg:#0f2f2c; --tag-performance-fg:#68d3c8;
    --tag-deprecation-bg:#3d1b1b; --tag-deprecation-fg:#f09a9a;
    --tag-security-bg:#3d1b1b;    --tag-security-fg:#f09a9a;
    --tag-release-bg:#222c37; --tag-release-fg:#a5b6c8;
    --tag-news-bg:#222c37;    --tag-news-fg:#a5b6c8;
  }
}
html{-webkit-text-size-adjust:100%}
body{
  margin:0;background:var(--bg);color:var(--ink);
  font:400 16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
.wrap{max-width:760px;margin:0 auto;padding:32px 20px 72px}
a{color:var(--azure)}
a:focus-visible,button:focus-visible{outline:2px solid var(--azure);outline-offset:2px;border-radius:3px}

.masthead{display:flex;flex-wrap:wrap;gap:12px 20px;align-items:baseline;
  padding-bottom:18px;border-bottom:2px solid var(--line-strong);margin-bottom:28px}
.masthead h1{margin:0;font-size:1.5rem;line-height:1.2;letter-spacing:-.015em;text-wrap:balance}
.masthead h1 a{color:var(--ink);text-decoration:none}
.masthead nav{margin-left:auto;display:flex;gap:16px;font-size:.88rem}
.dateline{width:100%;color:var(--faint);font-size:.88rem;margin-top:-4px}
.dateline .dot{opacity:.5;padding:0 .45em}

.tldr{background:var(--raised);border-left:4px solid var(--azure);border-radius:8px;
  padding:16px 20px;margin:0 0 34px}
.tldr h2{margin:0 0 10px;font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:var(--azure)}
.tldr ul{margin:0;padding-left:1.15em;display:flex;flex-direction:column;gap:7px}
.tldr li{font-size:1.02rem;line-height:1.55}

.section{margin:0 0 40px}
.section-head{display:flex;align-items:baseline;gap:12px;
  padding-bottom:9px;border-bottom:2px solid var(--accent);margin-bottom:18px}
.section-head h2{margin:0;font-size:.76rem;letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}
.section-head .count{margin-left:auto;color:var(--faint);font-size:.8rem;font-variant-numeric:tabular-nums}
.section.azure{--accent:var(--azure)}
.section.general{--accent:var(--general)}
.section.tooling{--accent:var(--tooling)}

.cards{display:flex;flex-direction:column;gap:14px}
.card{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--accent);
  border-radius:8px;padding:16px 18px;box-shadow:var(--shadow)}
.tag{display:inline-block;font-size:.66rem;font-weight:700;letter-spacing:.09em;
  text-transform:uppercase;padding:4px 9px;border-radius:4px;margin-bottom:9px}
.card h3{margin:0 0 7px;font-size:1.1rem;line-height:1.35;letter-spacing:-.005em;text-wrap:balance}
.card h3 a{color:var(--ink);text-decoration:none}
.card h3 a:hover{text-decoration:underline;text-decoration-color:var(--accent);text-underline-offset:3px}
.card .summary{margin:0;color:var(--muted);font-size:.95rem}
.why{margin-top:12px;padding-top:11px;border-top:1px solid var(--line)}
.why b{display:block;font-size:.68rem;font-weight:700;letter-spacing:.08em;
  text-transform:uppercase;color:var(--accent);margin-bottom:3px}
.why span{color:var(--muted);font-size:.93rem}
.source{display:inline-block;margin-top:13px;font-size:.86rem;font-weight:600;
  color:var(--accent);text-decoration:none;border-bottom:1px solid currentColor;padding-bottom:1px}

.also{margin-top:18px}
.also h3{margin:0 0 8px;font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;color:var(--faint)}
.also ul{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:7px}
.also li{font-size:.92rem;color:var(--muted);padding-left:1.1em;position:relative}
.also li::before{content:"\\2022";position:absolute;left:0;color:var(--accent)}
.also a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line-strong)}
.also a:hover{border-bottom-color:var(--accent)}
.also .src{color:var(--faint)}

.empty{color:var(--faint);font-style:italic;margin:0}

.archive-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:2px}
.archive-list li{border-bottom:1px solid var(--line)}
.archive-list a{display:flex;flex-wrap:wrap;gap:4px 14px;align-items:baseline;
  padding:14px 4px;text-decoration:none;color:var(--ink)}
.archive-list a:hover{background:var(--surface)}
.archive-list .d{font-weight:600}
.archive-list .n{color:var(--faint);font-size:.85rem;font-variant-numeric:tabular-nums;margin-left:auto}
.archive-list .peek{width:100%;color:var(--muted);font-size:.9rem;line-height:1.5}

footer{margin-top:48px;padding-top:18px;border-top:1px solid var(--line);
  color:var(--faint);font-size:.84rem;display:flex;flex-wrap:wrap;gap:6px 14px}

@media (max-width:560px){
  .wrap{padding:24px 16px 56px}
  .masthead nav{margin-left:0;width:100%}
  .card{padding:14px 15px}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""


def _page(title: str, body: str, *, depth: int = 0) -> str:
    up = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{title}</title>
<link rel="alternate" type="application/atom+xml" title="{esc(SITE_TITLE)}" href="{up}feed.xml">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
{body}
</div>
</body>
</html>"""


def _masthead(date_iso: str, digest: dict, *, depth: int) -> str:
    up = "../" * depth
    return f"""<header class="masthead">
  <h1><a href="{up}index.html">{esc(SITE_TITLE)}</a></h1>
  <nav><a href="{up}archive/index.html">Archive</a><a href="{up}feed.xml">Feed</a></nav>
  <div class="dateline">{esc(pretty_date(date_iso))}<span class="dot">&middot;</span>{read_time(digest)} min read<span class="dot">&middot;</span>{item_count(digest)} items</div>
</header>"""


def _card(item: dict) -> str:
    tag = (item.get("tag") or "news").strip().lower()
    if tag not in TAG_LABELS:
        tag = "news"
    url, title = esc(item.get("url")), esc(item.get("title"))
    heading = f'<a href="{url}">{title}</a>' if url else title

    why = ""
    if item.get("why"):
        why = (f'<div class="why"><b>Why it matters</b>'
               f'<span>{esc(item["why"])}</span></div>')
    source = ""
    if url:
        source = (f'<a class="source" href="{url}">'
                  f'Read more at {esc(domain(item.get("url")))} &rarr;</a>')

    return f"""<article class="card">
  <span class="tag" style="background:var(--tag-{tag}-bg);color:var(--tag-{tag}-fg)">{TAG_LABELS[tag]}</span>
  <h3>{heading}</h3>
  <p class="summary">{esc(item.get('summary'))}</p>
  {why}
  {source}
</article>"""


def _also(entries: list) -> str:
    if not entries:
        return ""
    rows = []
    for entry in entries:
        url, title = esc(entry.get("url")), esc(entry.get("title"))
        linked = f'<a class="alt" href="{url}">{title}</a>' if url else title
        # "summary" is the current field; "note" is what older stored editions
        # used, and every edition is re-rendered on each build.
        line = esc(entry.get("summary") or entry.get("note"))
        body = f'<span class="alsum">{line}</span>' if line else ""
        more = (f'<a class="alsrc" href="{url}">Read more at '
                f'{esc(domain(entry.get("url")))} &rarr;</a>') if url else ""
        rows.append(f"<li>{linked}{body}{more}</li>")
    return f'<div class="also"><h3>Also noted</h3><ul>{"".join(rows)}</ul></div>'


def _sections(digest: dict) -> str:
    out = []
    for key, label in SECTIONS:
        section = section_of(digest, key)
        count = len(section["top"]) + len(section["also"])
        if count:
            body = (f'<div class="cards">{"".join(_card(i) for i in section["top"])}</div>'
                    + _also(section["also"]))
        else:
            body = '<p class="empty">No news.</p>'
        # The section key doubles as the CSS class that picks its accent colour.
        out.append(f"""<section class="section {esc(key)}">
  <div class="section-head"><h2>{esc(label)}</h2><span class="count">{count}</span></div>
  {body}
</section>""")
    return "".join(out)


def _tldr(digest: dict) -> str:
    items = digest.get("tldr") or []
    if not items:
        return ""
    lis = "".join(f"<li>{esc(t)}</li>" for t in items)
    return f'<div class="tldr"><h2>TL;DR</h2><ul>{lis}</ul></div>'


def _footer(model: str, *, depth: int = 0) -> str:
    up = "../" * depth
    return (f'<footer><span>Curated daily by {esc(model)}.</span>'
            f'<span><a href="{up}archive/index.html">All past editions</a></span>'
            f'<span><a href="{up}feed.xml">Subscribe via RSS</a></span></footer>')


def render_digest_page(date_iso: str, digest: dict, *, model: str, depth: int = 0) -> str:
    body = (_masthead(date_iso, digest, depth=depth) + _tldr(digest)
            + _sections(digest) + _footer(model, depth=depth))
    return _page(f"{esc(SITE_TITLE)} — {esc(date_iso)}", body, depth=depth)


def render_archive_index(editions: list, *, model: str) -> str:
    rows = []
    for date_iso, digest in editions:
        peek = (digest.get("tldr") or [""])[0]
        rows.append(
            f'<li><a href="{esc(date_iso)}.html">'
            f'<span class="d">{esc(pretty_date(date_iso))}</span>'
            f'<span class="n">{item_count(digest)} items</span>'
            f'<span class="peek">{esc(peek)}</span></a></li>'
        )
    body = f"""<header class="masthead">
  <h1><a href="../index.html">{esc(SITE_TITLE)}</a></h1>
  <nav><a href="../index.html">Latest</a><a href="../feed.xml">Feed</a></nav>
  <div class="dateline">{len(editions)} edition{'s' if len(editions) != 1 else ''}</div>
</header>
<ul class="archive-list">{''.join(rows)}</ul>
{_footer(model, depth=1)}"""
    return _page(f"Archive — {esc(SITE_TITLE)}", body, depth=1)


def render_feed(editions: list, *, site_url: str) -> str:
    base = site_url.rstrip("/")
    updated = (
        f"{editions[0][0]}T06:00:00Z" if editions
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    entries = []
    for date_iso, digest in editions[:30]:
        summary = " ".join(digest.get("tldr") or []) or "Daily AI and Azure digest."
        entries.append(f"""  <entry>
    <title>{esc(SITE_TITLE)} — {esc(pretty_date(date_iso))}</title>
    <link href="{esc(base)}/archive/{esc(date_iso)}.html"/>
    <id>{esc(base)}/archive/{esc(date_iso)}.html</id>
    <updated>{esc(date_iso)}T06:00:00Z</updated>
    <summary>{esc(summary)}</summary>
  </entry>""")
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{esc(SITE_TITLE)}</title>
  <link href="{esc(base)}/"/>
  <link rel="self" href="{esc(base)}/feed.xml"/>
  <id>{esc(base)}/</id>
  <updated>{updated}</updated>
{chr(10).join(entries)}
</feed>"""
