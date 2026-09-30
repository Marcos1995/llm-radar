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
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
MIN_FACTS = 3
SLUG_RE = re.compile(r"[a-z0-9][a-z0-9-]*")

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500'
    '&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">'
)
CSS = """
:root{color-scheme:light;--bg:#f6f4ef;--text:#1c1915;--muted:#6e675f;--subtle:#9c9489;--accent:#1f6b4a;--accent-soft:rgba(31,107,74,.08);--border:#e6e2d8;--hover:#ece8de;--serif:Fraunces,serif;--sans:Inter,system-ui,sans-serif;--mono:"JetBrains Mono",ui-monospace,monospace}
@media (prefers-color-scheme:dark){:root{color-scheme:dark;--bg:#161411;--text:#f3efe6;--muted:#a39b8f;--subtle:#8a8176;--accent:#8fcead;--accent-soft:rgba(143,206,173,.12);--border:#282420;--hover:#221e1a}}
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
.brand-link:focus-visible,.model-row:focus-visible,.footer-link:focus-visible,.meta a:focus-visible,.filter-input:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
@media (min-width:768px){
.container{padding:40px 32px 64px}.facts th,.facts td{display:table-cell;vertical-align:baseline}
.facts th{width:34%;padding:14px 16px 14px 0}.facts td{width:66%;padding:14px 0}
}
@media (min-width:1280px){.container{max-width:960px;padding:56px 40px 80px}}
@media (prefers-reduced-motion:reduce){.brand-link,.model-row,.footer-link,.filter-input{transition:none}}
"""


def esc(value) -> str:
    return html.escape(str(value), quote=True)


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
        f'<footer><a class="footer-link" href="{esc(base)}/api/items.json">JSON</a>'
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
        body = (
            f'<h1 class="page-title">{esc(it["title"])}</h1><p class="lede">{esc(it["summary"])}</p>'
            f'<table class="facts">{rows}</table>{source}'
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
    index_body = (
        f'<section class="hero"><h1 class="hero-title">{esc(cfg["title"])}</h1>'
        f'<p class="hero-desc">{esc(cfg["description"])}</p></section>{search}'
        f'<div class="catalog">{listing}</div><p id="empty" class="no-results" hidden>No se encontraron modelos con ese término.</p>'
    )
    write("index.html", page(cfg, cfg["title"], index_body, "/", cfg["description"], script=script))

    write("api/items.json", json.dumps(items, ensure_ascii=False, indent=1))
    write("health.json", json.dumps({"ok": True, "items": len(items), "indexable": len(indexable), "updated": now.isoformat()}))
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n")
    urls = [f"{base}/"] + [f"{base}/{it['slug']}/" for it in indexable]
    write(
        "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{esc(u)}</loc><lastmod>{today}</lastmod></url>" for u in urls)
        + "</urlset>",
    )
    llms = [f"# {cfg['title']}", "", f"> {cfg['description']}", "", "## Datos", "",
            f"- [items.json]({base}/api/items.json): todos los elementos, JSON",
            f"- [openapi.json]({base}/openapi.json): especificacion de la API",
            f"- [sitemap.xml]({base}/sitemap.xml)", "", "## Paginas", ""]
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
