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

CSS = """body{font:16px/1.5 system-ui,sans-serif;max-width:860px;margin:0 auto;padding:1rem;color:#1a1a1a}
a{color:#0b5fff}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ddd;padding:.4rem;text-align:left}
input{width:100%;padding:.5rem;margin:.5rem 0}li{margin:.2rem 0}small{color:#666}footer{margin-top:2rem;color:#666}"""


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


def page(cfg: dict, title: str, body: str, path: str, desc: str, ld: dict | None = None, index: bool = True) -> str:
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
        f'{robots}<style>{CSS}</style>{ld_tag}{cfg.get("head_html", "")}{analytics}</head><body>'
        f'<header><a href="{esc(base)}/">{esc(cfg["title"])}</a></header><main>{body}</main>'
        f'<footer><a href="{esc(base)}/api/items.json">JSON</a> · <a href="{esc(base)}/openapi.json">OpenAPI</a> · '
        f'<a href="{esc(base)}/llms.txt">llms.txt</a></footer></body></html>'
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
        source = f'<p><small>Fuente: <a href="{esc(it["source"])}" rel="nofollow">{esc(it["source"])}</a></small></p>' if it.get("source") else ""
        body = (
            f"<h1>{esc(it['title'])}</h1><p>{esc(it['summary'])}</p><table>{rows}</table>{source}"
            f"<p><small>Actualizado: {esc(updated)} · <a href=\"{esc(base)}/api/{esc(it['slug'])}.json\">JSON</a></small></p>"
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
        f"<h2>{esc(g)}</h2><ul>" + "".join(f'<li><a href="{esc(base)}/{esc(i["slug"])}/">{esc(i["title"])}</a></li>' for i in its) + "</ul>"
        for g, its in sorted(groups.items())
    )
    search = (
        '<input id="q" placeholder="Filtrar..." oninput="for(const l of document.querySelectorAll(\'li\'))'
        'l.hidden=!l.textContent.toLowerCase().includes(this.value.toLowerCase())">'
    )
    write("index.html", page(cfg, cfg["title"], f"<h1>{esc(cfg['title'])}</h1><p>{esc(cfg['description'])}</p>{search}{listing}", "/", cfg["description"]))

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
