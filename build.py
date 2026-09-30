"""Genera el sitio estatico en _site/ desde project.json + data/items.json.

Copia de templates/site-kit: no editar en cada repo (mejora en el kit y recopia). Solo stdlib.
Pagina con menos de MIN_FACTS datos propios: noindex y fuera del sitemap (anti contenido escaso).
"""
import html
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
MIN_FACTS = 3
SLUG_RE = re.compile(r"[a-z0-9][a-z0-9-]*")

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500'
    '&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">'
)
CSS = """
:root{color-scheme:light;--bg:#f6f4ef;--card:#fcfbfa;--text:#1c1915;--muted:#5f584f;--subtle:#6e675f;--accent:#1f6b4a;--border:#e6e2da;--hover:#eeebe3;--bar:#e5e1d7;--serif:Fraunces,serif;--sans:Inter,system-ui,sans-serif;--mono:"JetBrains Mono",ui-monospace,monospace}
@media (prefers-color-scheme:dark){:root{color-scheme:dark;--bg:#161411;--card:#1e1b17;--text:#f3efe6;--muted:#c4bbb0;--subtle:#a39b8f;--accent:#8fcead;--border:#2e2a24;--hover:#26221d;--bar:#2b2721}}
*{box-sizing:border-box}[hidden]{display:none !important}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 var(--sans);min-height:100vh;overflow-x:clip}
.container{width:100%;max-width:880px;margin:0 auto;padding:24px 20px 48px;min-height:100vh;display:flex;flex-direction:column}
main,.catalog,.provider-group,.model-list,.model-item,.model-row,.hero-desc,.lede{min-width:0;max-width:100%}
header{margin-bottom:36px}.brand-link{display:inline-flex;align-items:center;gap:8px;color:var(--text);text-decoration:none;font-weight:500}
.brand-mark{width:8px;height:8px;border-radius:50%;background:var(--accent)}
.hero{margin-bottom:32px}.hero-title,.page-title{font-family:var(--serif);font-weight:400;letter-spacing:-.03em;line-height:1.08;margin:0 0 12px}
.hero-title{font-size:clamp(2.4rem,6vw,3.8rem)}.page-title{font-size:clamp(1.8rem,4vw,2.75rem)}
.hero-desc,.lede{color:var(--muted);max-width:40rem;margin:0}
.filter-wrapper{position:relative;margin:32px 0 36px}
.filter-input{width:100%;padding:14px 7.5rem 14px 16px;font:inherit;color:var(--text);background:transparent;border:1px solid var(--border);border-radius:6px}
.filter-input::placeholder{color:var(--subtle)}
.filter-count{position:absolute;right:14px;top:50%;transform:translateY(-50%);font:500 .75rem/1 var(--mono);color:var(--muted)}
.catalog{display:flex;flex-direction:column;gap:32px}
.provider-label{margin:0 0 8px;padding-bottom:6px;border-bottom:1px solid var(--border);font:500 .75rem/1.2 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.model-list{list-style:none;margin:0;padding:0}
.model-row{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:0;padding:14px 4px;border-radius:6px;color:var(--text);text-decoration:none;font-weight:500;overflow-wrap:anywhere}
.model-row::after{content:"";width:7px;height:7px;border-right:1.5px solid var(--subtle);border-top:1.5px solid var(--subtle);transform:rotate(45deg);flex:none}
.model-row:hover{background:var(--hover);color:var(--accent)}
.model-row:hover::after{border-color:var(--accent)}
.no-results{color:var(--muted);margin:0}
.facts{width:100%;border-collapse:collapse;margin-top:28px}
.facts th,.facts td{display:block;padding:0;border:0;text-align:left;font-weight:400}
.facts tr{border-bottom:1px solid var(--border)}
.facts th{padding-top:14px;font:500 .72rem/1.2 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.facts td{padding:4px 0 14px;overflow-wrap:anywhere}
.meta{color:var(--muted);font-size:.85rem;margin:1.15rem 0 0;overflow-wrap:anywhere}
.meta a{color:var(--accent)}
footer{margin-top:auto;padding-top:24px;border-top:1px solid var(--border);display:flex;gap:20px}
.footer-link{color:var(--muted);font:500 .8rem/1 var(--mono);text-decoration:none}
.brand-link:hover,.footer-link:hover,.meta a:hover{color:var(--accent)}
.brand-link:focus-visible,.model-row:focus-visible,.model-card:focus-visible,.footer-link:focus-visible,.meta a:focus-visible,.filter-input:focus-visible,.compare-controls select:focus-visible,.section-head a:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
@media (min-width:768px){
.container{padding:40px 32px 64px}.facts th,.facts td{display:table-cell;vertical-align:baseline}
.facts th{width:34%;padding:14px 16px 14px 0}.facts td{width:66%;padding:14px 0}
}
@media (min-width:1280px){.container{max-width:960px;padding:56px 40px 80px}}
.cards{display:grid;grid-template-columns:1fr;gap:12px;margin:28px 0 8px}
.model-card{display:flex;flex-direction:column;position:relative;min-width:0;padding:1.15rem 1.25rem 1.3rem;background:var(--card);border:1px solid var(--border);border-radius:6px;color:var(--text);text-decoration:none}
.model-card:hover{background:var(--hover);border-color:var(--accent)}
.card-top{display:flex;justify-content:space-between;gap:12px;margin-bottom:.7rem}
.card-tag,.card-vendor,.section-title,.metric-note{font-family:var(--mono);letter-spacing:.06em;text-transform:uppercase}
.card-tag{font-size:.68rem;color:var(--muted)}.card-vendor{font-size:.68rem;color:var(--subtle)}
.card-name{font-weight:500;line-height:1.3;margin-bottom:.35rem}
.card-why{color:var(--muted);font-size:.82rem;max-width:92%}
.card-figure{margin-top:1rem;padding-right:1.5rem;font:600 1.35rem/1.2 var(--mono);color:var(--accent);letter-spacing:-.02em}
.card-arrow{position:absolute;right:1.1rem;bottom:1.15rem;color:var(--subtle)}
.model-card:hover .card-arrow{color:var(--accent)}
.board{margin:36px 0 12px}
.section-head{display:flex;justify-content:space-between;gap:12px;align-items:baseline;border-bottom:1px solid var(--border);padding-bottom:.7rem;margin-bottom:1.1rem}
.section-title{font-size:.75rem;color:var(--subtle)}
.section-head a{color:var(--accent);font-size:.85rem;text-decoration:none}
.metric-grid{display:flex;flex-direction:column;gap:16px}
.metric{min-width:0;background:var(--card);border:1px solid var(--border);border-radius:6px;padding:1rem 1.1rem}
.metric h3{margin:0 0 .2rem;font-size:.9rem}
.metric-note{font-size:.68rem;color:var(--subtle);text-transform:none;letter-spacing:0;margin-bottom:.9rem}
.bar-row{display:block;margin:0 0 .85rem;color:inherit;text-decoration:none;min-width:0}
.bar-meta{display:flex;justify-content:space-between;gap:8px;font-size:.82rem;margin-bottom:.3rem}
.bar-model{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bar-value{flex:none;font:500 .75rem/1.3 var(--mono);color:var(--muted)}
.bar-track{display:block;height:6px;background:var(--bar);border-radius:3px;overflow:hidden}
.bar-fill{display:block;height:100%;background:var(--accent);border-radius:3px}
.pick-note{color:var(--muted);font-size:.85rem;margin:8px 0 0}
.compare-controls{display:grid;gap:10px;margin:20px 0 8px}
.compare-controls select{width:100%;padding:12px;font:inherit;color:var(--text);background:var(--card);border:1px solid var(--border);border-radius:6px}
@media (min-width:768px){.cards{grid-template-columns:1fr 1fr;gap:14px}.compare-controls{grid-template-columns:1fr 1fr}}
@media (min-width:1024px){.metric-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
@media (prefers-reduced-motion:reduce){.brand-link,.model-row,.footer-link,.filter-input,.model-card,.card-arrow{transition:none}}
"""


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def plain(amount: Decimal) -> str:
    text = format(amount, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def compact(amount: Decimal) -> str:
    value, suffix = amount, ""
    if amount >= 1_000_000:
        value, suffix = amount / Decimal(1_000_000), " M"
    elif amount >= 10_000:
        value, suffix = amount / Decimal(1_000), " k"
    shown = value.quantize(Decimal("0.1")) if suffix else value.quantize(Decimal("1"))
    return plain(shown) + suffix


def fact_map(item: dict) -> dict:
    return {pair[0]: pair[1] for pair in item.get("facts") or [] if isinstance(pair, list) and len(pair) == 2}


def parse_usd(text) -> Decimal | None:
    if not isinstance(text, str) or not text.endswith(" USD"):
        return None
    try:
        return Decimal(text[:-4].strip())
    except InvalidOperation:
        return None


def parse_ctx(text) -> int | None:
    if not isinstance(text, str) or not text.endswith(" tokens"):
        return None
    try:
        return int(text.split()[0])
    except ValueError:
        return None


def model_id_of(item: dict) -> str:
    source = item.get("source") or ""
    prefix = "https://openrouter.ai/"
    return source[len(prefix):] if source.startswith(prefix) else ""


def priced(item: dict) -> dict | None:
    facts = fact_map(item)
    prompt, completion = parse_usd(facts.get("Precio prompt / 1M")), parse_usd(facts.get("Precio completion / 1M"))
    context = parse_ctx(facts.get("Contexto"))
    if prompt is None or completion is None or context is None or prompt <= 0 or completion <= 0:
        return None
    if model_id_of(item).startswith("~"):
        return None
    return {
        "item": item,
        "prompt": prompt,
        "completion": completion,
        "context": context,
        "open": facts.get("Pesos") not in (None, "", "no publicados"),
        "per_dollar": Decimal(context) / prompt,
        "prompt_tokens": Decimal(1_000_000) / prompt,
        "output_tokens": Decimal(1_000_000) / completion,
    }


def band_of(prompt: Decimal) -> str:
    if prompt < Decimal("0.5"):
        return "baja"
    if prompt < 3:
        return "media"
    if prompt < 15:
        return "alta"
    return "maxima"


def picks_for(rows: list[dict]) -> list[tuple[str, dict, str, str]]:
    def best(pool, key):
        return max(pool, key=key) if pool else None

    specs = [
        ("Pesos publicados", [row for row in rows if row["open"]], "per_dollar", "Más contexto por cada dólar de prompt"),
        ("Sin pesos públicos", [row for row in rows if not row["open"]], "per_dollar", "Más contexto por cada dólar de prompt"),
        ("Gama baja", [row for row in rows if band_of(row["prompt"]) == "baja"], "per_dollar", "Prompt bajo 0,5 USD/1M"),
        ("Gama media", [row for row in rows if band_of(row["prompt"]) == "media"], "per_dollar", "Prompt de 0,5 a 3 USD/1M"),
        ("Gama alta", [row for row in rows if band_of(row["prompt"]) == "alta"], "per_dollar", "Prompt de 3 a 15 USD/1M"),
        ("Gama máxima", [row for row in rows if band_of(row["prompt"]) == "maxima"], "per_dollar", "Prompt desde 15 USD/1M"),
        ("Eficiencia de prompt", rows, "prompt_tokens", "Más tokens de entrada por dólar"),
        ("Eficiencia de salida", rows, "output_tokens", "Más tokens de salida por dólar"),
    ]
    chosen = []
    for label, pool, key, why in specs:
        winner = best(pool, lambda row, key=key: row[key])
        if winner:
            chosen.append((label, winner, key, why))
    return chosen


def card_html(base: str, label: str, row: dict, key: str, why: str) -> str:
    item = row["item"]
    if key == "prompt_tokens":
        figure = f"{compact(row['prompt_tokens'])} tok/$"
    elif key == "output_tokens":
        figure = f"{compact(row['output_tokens'])} tok/$"
    else:
        figure = f"{plain(row['prompt'])} USD"
    return (
        f'<a class="model-card" href="{esc(base)}/{esc(item["slug"])}/">'
        f'<span class="card-top"><span class="card-tag">{esc(label)}</span><span class="card-vendor">{esc(item.get("group", ""))}</span></span>'
        f'<span class="card-name">{esc(item["title"])}</span><span class="card-why">{esc(why)}</span>'
        f'<span class="card-figure">{esc(figure)}</span><span class="card-arrow" aria-hidden="true">→</span></a>'
    )


def bars_html(base: str, rows: list[dict], key: str, value) -> str:
    top = max(row[key] for row in rows)
    parts = []
    for row in sorted(rows, key=lambda item: item[key], reverse=True):
        width = 0 if top == 0 else float(row[key] / top * 100)
        parts.append(
            f'<a class="bar-row" href="{esc(base)}/{esc(row["item"]["slug"])}/">'
            f'<span class="bar-meta"><span class="bar-model">{esc(row["item"]["title"])}</span>'
            f'<span class="bar-value">{esc(value(row))}</span></span>'
            f'<span class="bar-track"><span class="bar-fill" style="width:{width:.1f}%"></span></span></a>'
        )
    return "".join(parts)


def validate(items: list) -> list[str]:
    errors, seen = [], set()
    for i, item in enumerate(items):
        for key in ("slug", "title", "summary", "facts"):
            if not item.get(key):
                errors.append(f"item {i}: falta '{key}'")
        slug = str(item.get("slug", ""))
        if not SLUG_RE.fullmatch(slug):
            errors.append(f"item {i}: slug invalido '{slug}'")
        if slug in seen:
            errors.append(f"item {i}: slug repetido '{slug}'")
        seen.add(slug)
        for fact in item.get("facts") or []:
            if not (isinstance(fact, list) and len(fact) == 2):
                errors.append(f"item {i}: fact invalido {fact!r}")
    return errors


def page(cfg: dict, title: str, body: str, path: str, desc: str, ld: dict | None = None, index: bool = True, script: str = "") -> str:
    base = cfg["site_url"].rstrip("/")
    analytics = (
        f'<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
        f"data-cf-beacon='{{\"token\": \"{esc(cfg['analytics_token'])}\"}}'></script>"
        if cfg.get("analytics_token")
        else ""
    )
    ld_tag = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ""
    robots = "" if index else '<meta name="robots" content="noindex">'
    return (
        f'<!doctype html><html lang="{esc(cfg.get("lang", "es"))}"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>'
        f'<meta name="description" content="{esc(desc[:160])}"><link rel="canonical" href="{esc(base + path)}">'
        f'{robots}{FONTS}<style>{CSS}</style>{ld_tag}{cfg.get("head_html", "")}{analytics}</head><body>'
        f'<div class="container"><header><a class="brand-link" href="{esc(base)}/"><span class="brand-mark" aria-hidden="true"></span>{esc(cfg["title"])}</a></header><main>{body}</main>'
        f'<footer><a class="footer-link" href="{esc(base)}/comparar/">Comparar</a>'
        f'<a class="footer-link" href="{esc(base)}/api/items.json">JSON</a>'
        f'<a class="footer-link" href="{esc(base)}/openapi.json">OpenAPI</a>'
        f'<a class="footer-link" href="{esc(base)}/llms.txt">llms.txt</a></footer></div>{script}</body></html>'
    )


def write(rel: str, content: str) -> None:
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build() -> int:
    cfg = json.loads((ROOT / "project.json").read_text("utf-8"))
    items = json.loads((ROOT / "data" / "items.json").read_text("utf-8"))
    errors = validate(items)
    if errors:
        print("\n".join(errors[:20]), file=sys.stderr)
        return 1

    base = cfg["site_url"].rstrip("/")
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    indexable = [it for it in items if len(it["facts"]) >= MIN_FACTS]
    if OUT.exists():
        shutil.rmtree(OUT)

    for it in items:
        updated = it.get("updated", today)
        rows = "".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in it["facts"])
        source = f'<p class="meta">Fuente: <a href="{esc(it["source"])}" rel="nofollow">{esc(it["source"])}</a></p>' if it.get("source") else ""
        row = priced(it)
        if row:
            gama = {"baja": "Gama baja", "media": "Gama media", "alta": "Gama alta", "maxima": "Gama máxima"}[band_of(row["prompt"])]
            place = (
                f'<p class="meta">{esc(gama)} · {esc(plain(row["per_dollar"]))} tokens de contexto por dólar de prompt'
                f' · <a href="{esc(base)}/comparar/?a={esc(it["slug"])}">Comparar</a></p>'
            )
        else:
            place = f'<p class="meta">Precio cero o variable: fuera de las gamas. <a href="{esc(base)}/comparar/?a={esc(it["slug"])}">Comparar</a></p>'
        body = (
            f'<h1 class="page-title">{esc(it["title"])}</h1><p class="lede">{esc(it["summary"])}</p>'
            f'<table class="facts">{rows}</table>{source}{place}'
            f'<p class="meta">Actualizado: {esc(updated)} · <a href="{esc(base)}/api/{esc(it["slug"])}.json">JSON del modelo</a></p>'
        )
        ld = {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "name": it["title"],
            "description": it["summary"],
            "dateModified": updated,
            "url": f"{base}/{it['slug']}/",
        }
        if it.get("source"):
            ld["isBasedOn"] = it["source"]
        write(f"{it['slug']}/index.html", page(cfg, f"{it['title']} | {cfg['title']}", body, f"/{it['slug']}/", it["summary"], ld, len(it["facts"]) >= MIN_FACTS))
        write(f"api/{it['slug']}.json", json.dumps(it, ensure_ascii=False, indent=1))

    groups: dict[str, list] = {}
    for it in indexable:
        groups.setdefault(it.get("group", "Todos"), []).append(it)
    listing = "".join(
        f'<section class="provider-group" data-provider="{esc(g.lower())}"><h2 class="provider-label">{esc(g)}</h2><ul class="model-list">'
        + "".join(f'<li class="model-item"><a class="model-row" href="{esc(base)}/{esc(i["slug"])}/">{esc(i["title"])}</a></li>' for i in its)
        + "</ul></section>"
        for g, its in sorted(groups.items())
    )
    search = (
        f'<div class="filter-wrapper"><input id="q" class="filter-input" placeholder="Filtrar..." '
        f'aria-label="Filtrar modelos" autocomplete="off" spellcheck="false">'
        f'<span class="filter-count" id="count">{len(indexable)} modelos</span></div>'
    )
    script = (
        "<script>const q=document.getElementById('q'),groups=document.querySelectorAll('.provider-group'),"
        "empty=document.getElementById('empty'),count=document.getElementById('count'),"
        "total=document.querySelectorAll('.model-item').length;"
        "q.addEventListener('input',()=>{const v=q.value.toLowerCase().trim();let n=0;"
        "for(const g of groups){let show=false;for(const li of g.querySelectorAll('.model-item')){"
        "const ok=!v||li.textContent.toLowerCase().includes(v)||g.dataset.provider.includes(v);"
        "li.hidden=!ok;if(ok){show=true;n++}}g.hidden=!show}"
        "empty.hidden=n!==0;count.textContent=n===total?total+' modelos':n+' de '+total});</script>"
    )
    ranked = [row for it in indexable if (row := priced(it))]
    chosen = picks_for(ranked)
    cards = "".join(card_html(base, label, row, key, why) for label, row, key, why in chosen)
    unique, seen = [], set()
    for _, row, _, _ in chosen:
        slug = row["item"]["slug"]
        if slug not in seen:
            seen.add(slug)
            unique.append(row)
    board = ""
    if unique:
        board = (
            '<section class="board"><div class="section-head"><h2 class="section-title">Comparativa</h2>'
            f'<a href="{esc(base)}/comparar/">Comparar dos</a></div><div class="metric-grid">'
            f'<section class="metric"><h3>Precio de prompt</h3><p class="metric-note">USD por 1M tokens</p>{bars_html(base, unique, "prompt", lambda row: plain(row["prompt"]) + " USD")}</section>'
            f'<section class="metric"><h3>Contexto</h3><p class="metric-note">tokens</p>{bars_html(base, unique, "context", lambda row: compact(Decimal(row["context"])) + " tokens")}</section>'
            f'<section class="metric"><h3>Tokens por dólar</h3><p class="metric-note">entrada</p>{bars_html(base, unique, "prompt_tokens", lambda row: compact(row["prompt_tokens"]) + " tok/$")}</section>'
            '</div><p class="pick-note">La barra larga es el valor mayor. No es un test de inteligencia.</p></section>'
        )
    lede = "Precio, contexto y tokens por dólar. OpenRouter no publica notas de tests, así que aquí no hay un índice de inteligencia."
    index_body = (
        f'<section class="hero"><h1 class="hero-title">{esc(cfg["title"])}</h1><p class="hero-desc">{esc(lede)}</p></section>'
        f'<div class="cards">{cards}</div>{board}'
        f'<section class="board"><div class="section-head"><h2 class="section-title">Catálogo</h2></div>{search}'
        f'<div class="catalog">{listing}</div><p id="empty" class="no-results" hidden>No se encontraron modelos con ese término.</p></section>'
    )
    write("index.html", page(cfg, cfg["title"], index_body, "/", lede, script=script))
    compare_desc = "Compara dos modelos por precio, contexto y tokens por dólar."
    compare_body = (
        f'<section class="hero"><h1 class="page-title">Comparar</h1><p class="lede">{esc(compare_desc)} '
        f'No es un índice de inteligencia.</p></section>'
        '<div class="compare-controls"><select id="a" aria-label="Primer modelo"></select>'
        '<select id="b" aria-label="Segundo modelo"></select></div><div id="board"></div>'
        '<script type="application/json" id="models">MODELS</script>'
    )
    payload = []
    for it in indexable:
        row = priced(it)
        facts = fact_map(it)
        payload.append({
            "slug": it["slug"],
            "title": it["title"],
            "group": it.get("group") or "Otros",
            "prompt": plain(row["prompt"]) if row else ("0" if facts.get("Precio prompt / 1M") == "0 USD" else None),
            "completion": plain(row["completion"]) if row else ("0" if facts.get("Precio completion / 1M") == "0 USD" else None),
            "context": row["context"] if row else parse_ctx(facts.get("Contexto")),
            "promptTokens": plain(row["prompt_tokens"]) if row else None,
            "outputTokens": plain(row["output_tokens"]) if row else None,
        })
    compare_script = (
        "<script>const models=JSON.parse(document.getElementById('models').textContent);"
        "const a=document.getElementById('a'),b=document.getElementById('b'),board=document.getElementById('board');"
        "const groups={};for(const m of models){(groups[m.group]||=[]).push(m)}"
        "for(const name of Object.keys(groups).sort()){const og=document.createElement('optgroup');og.label=name;"
        "for(const m of groups[name]){const op=document.createElement('option');op.value=m.slug;op.textContent=m.title;og.append(op)}"
        "a.append(og.cloneNode(true));b.append(og)}"
        "const slugs=models.map(m=>m.slug);const q=new URLSearchParams(location.search);"
        "function pick(sel,slug,fallback){sel.value=[...sel.options].some(o=>o.value===slug)?slug:fallback}"
        "pick(a,q.get('a'),slugs[0]);pick(b,q.get('b'),slugs[1]||slugs[0]);"
        "function esc(s){return String(s).replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]))}"
        "function metric(title,note,key,suffix){const pair=[a.value,b.value].map(slug=>models.find(m=>m.slug===slug));"
        "const nums=pair.map(m=>m&&m[key]!=null?Number(m[key]):null);const top=Math.max(...nums.filter(n=>n>0),0);"
        "return '<section class=\"metric\"><h3>'+title+'</h3><p class=\"metric-note\">'+note+'</p>'+pair.map((m,i)=>{"
        "const n=nums[i],width=n&&top?n/top*100:0,label=n==null?'—':(suffix.indexOf('tok')===0?(n>=1e6?(Math.round(n/1e5)/10)+' M':n>=10000?(Math.round(n/100)/10)+' k':Math.round(n))+' '+suffix:(Math.round(n*1000)/1000)+' '+suffix);"
        "return '<a class=\"bar-row\" href=\"../'+m.slug+'/\"><span class=\"bar-meta\"><span class=\"bar-model\">'+esc(m.title)+'</span><span class=\"bar-value\">'+esc(label)+'</span></span><span class=\"bar-track\"><span class=\"bar-fill\" style=\"width:'+width.toFixed(1)+'%\"></span></span></a>'}).join('')+'</section>'}"
        "function render(){const url=new URL(location.href);url.searchParams.set('a',a.value);url.searchParams.set('b',b.value);try{history.replaceState(null,'',url)}catch(e){}"
        "board.innerHTML='<div class=\"metric-grid\">'+metric('Precio de prompt','USD por 1M tokens','prompt','USD')+metric('Precio de salida','USD por 1M tokens','completion','USD')+metric('Contexto','tokens','context','tokens')+metric('Tokens de prompt por dólar','entrada','promptTokens','tok/$')+metric('Tokens de salida por dólar','salida','outputTokens','tok/$')+'</div>'}"
        "a.addEventListener('change',render);b.addEventListener('change',render);render();</script>"
    )
    write(
        "comparar/index.html",
        page(cfg, f"Comparar | {cfg['title']}", compare_body.replace("MODELS", json.dumps(payload, ensure_ascii=True)), "/comparar/", compare_desc, script=compare_script),
    )

    write("api/items.json", json.dumps(items, ensure_ascii=False, indent=1))
    write("health.json", json.dumps({"ok": True, "items": len(items), "indexable": len(indexable), "updated": now.isoformat()}))
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n")
    urls = [f"{base}/", f"{base}/comparar/"] + [f"{base}/{it['slug']}/" for it in indexable]
    write(
        "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{esc(u)}</loc><lastmod>{today}</lastmod></url>" for u in urls)
        + "</urlset>",
    )
    llms = [f"# {cfg['title']}", "", f"> {cfg['description']}", "", "## Datos", "",
            f"- [items.json]({base}/api/items.json): todos los elementos, JSON",
            f"- [openapi.json]({base}/openapi.json): especificacion de la API",
            f"- [sitemap.xml]({base}/sitemap.xml)",
            f"- [comparar]({base}/comparar/): dos modelos, por precio, contexto y tokens por dólar", "", "## Paginas", ""]
    llms += [f"- [{it['title']}]({base}/{it['slug']}/): {it['summary'][:100]}" for it in indexable[:50]]
    write("llms.txt", "\n".join(llms) + "\n")
    ok = {"200": {"description": "OK", "content": {"application/json": {}}}}
    write("openapi.json", json.dumps({
        "openapi": "3.0.3",
        "info": {"title": cfg["title"], "description": cfg["description"], "version": today},
        "servers": [{"url": base}],
        "paths": {
            "/api/items.json": {"get": {"summary": "Todos los elementos", "responses": ok}},
            "/api/{slug}.json": {"get": {"summary": "Un elemento", "parameters": [{"name": "slug", "in": "path", "required": True, "schema": {"type": "string"}}], "responses": ok}},
            "/health.json": {"get": {"summary": "Estado", "responses": ok}},
        },
    }, ensure_ascii=False, indent=1))
    print(f"ok: {len(items)} paginas, {len(indexable)} indexables -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(build())
