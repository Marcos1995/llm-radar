"""Escribe data/items.json. Es LO UNICO especifico de cada proyecto: reemplaza este fichero entero.

Contrato: lista de objetos
  {"slug": "kebab-case", "title": str, "summary": str,
   "facts": [["etiqueta", "valor"], ...],   # >=3 datos propios por pagina o se marca noindex
   "group": str (opcional), "updated": "YYYY-MM-DD" (opcional), "source": url (opcional)}

Reglas: solo fuentes publicas y estables, stdlib (urllib) salvo necesidad real, una peticion
ligera por recurso, sin claves de pago. Si una fuente falla: sys.exit(1) y NO tocar data/.
Historico (tendencias): lee el data/items.json anterior antes de sobrescribirlo.
Escribe con json.dumps(ensure_ascii=False, indent=1).
"""
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
ITEMS_PATH = DATA / "items.json"
HISTORY_PATH = DATA / "history.json"
API = "https://openrouter.ai/api/v1/models"
MILLION = Decimal(1_000_000)
MIN_ITEMS = 100
SLUG_RE = re.compile(r"[a-z0-9][a-z0-9-]*")


def fail(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"no se pudo leer {path.name}: {exc}")


def fetch_models() -> list:
    req = urllib.request.Request(API, headers={"Accept": "application/json", "User-Agent": "llm-radar"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.load(resp)
    except Exception as exc:
        fail(f"OpenRouter no disponible: {exc}")
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list) or not data:
        fail("OpenRouter respondio sin modelos")
    return data


def slugify(model_id: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", model_id.lower()).strip("-")


def provider_of(model_id: str) -> str:
    part = model_id.split("/", 1)[0]
    if part.startswith("~"):
        part = part[1:]
    return part or "otros"


def plain(amount: Decimal) -> str:
    text = format(amount, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def price_label(raw: str) -> str:
    value = Decimal(raw)
    if value < 0:
        return f"variable ({plain(value)})"
    return f"{plain(value * MILLION)} USD"


def price_clause(kind: str, label: str) -> str:
    if label.startswith("variable"):
        return f"el precio de {kind} es {label}"
    return f"el precio de {kind} es {label} por 1M tokens"


def change_phrase(kind: str, old_raw: str, new_raw: str) -> str:
    old, new = Decimal(old_raw), Decimal(new_raw)
    if old == new:
        return f"{kind} sin cambio"
    if old < 0 or new < 0:
        return f"{kind} de {price_label(old_raw)} a {price_label(new_raw)}"
    diff = (new - old) * MILLION
    sign = "+" if diff > 0 else ""
    return f"{kind} {sign}{plain(diff)} USD/1M"


def variation(prev: dict | None, prompt: str, completion: str) -> str:
    if not prev:
        return "sin snapshot anterior"
    try:
        parts = [
            change_phrase("prompt", str(prev["prompt"]), prompt),
            change_phrase("completion", str(prev["completion"]), completion),
        ]
    except (InvalidOperation, KeyError, TypeError):
        return "sin snapshot anterior"
    if parts == ["prompt sin cambio", "completion sin cambio"]:
        return "sin cambio"
    return "; ".join(parts)


def same_price(prev: dict | None, prompt: str, completion: str) -> bool:
    if not prev:
        return False
    try:
        return Decimal(prev["prompt"]) == Decimal(prompt) and Decimal(prev["completion"]) == Decimal(completion)
    except (InvalidOperation, KeyError, TypeError):
        return False


def modality_text(arch: dict) -> str | None:
    inputs, outputs = arch.get("input_modalities"), arch.get("output_modalities")
    if isinstance(inputs, list) and isinstance(outputs, list) and inputs and outputs:
        if all(isinstance(x, str) and x for x in inputs + outputs):
            return "entrada " + ", ".join(inputs) + "; salida " + ", ".join(outputs)
    modality = arch.get("modality")
    if isinstance(modality, str) and modality:
        return modality
    return None


def main() -> None:
    previous_items = load_json(ITEMS_PATH, [])
    history = load_json(HISTORY_PATH, {})
    if not isinstance(previous_items, list):
        fail("data/items.json no es una lista")
    if not isinstance(history, dict):
        fail("data/history.json no es un objeto")
    prev_by_source = {
        item["source"]: item
        for item in previous_items
        if isinstance(item, dict) and isinstance(item.get("source"), str)
    }

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    used: dict[str, str] = {}
    seen_ids: set[str] = set()
    items = []

    for model in fetch_models():
        model_id = model.get("id")
        name = model.get("name")
        pricing = model.get("pricing") if isinstance(model.get("pricing"), dict) else {}
        prompt, completion = pricing.get("prompt"), pricing.get("completion")
        created_ts, ctx = model.get("created"), model.get("context_length")
        modality = modality_text(model.get("architecture") if isinstance(model.get("architecture"), dict) else {})
        if not all(isinstance(v, str) and v for v in (model_id, name, prompt, completion, modality)):
            continue
        if isinstance(ctx, bool) or not isinstance(ctx, (int, float)):
            continue
        if isinstance(created_ts, bool) or not isinstance(created_ts, (int, float)):
            continue
        try:
            prompt_label, completion_label = price_label(prompt), price_label(completion)
        except InvalidOperation:
            continue
        if model_id in seen_ids:
            continue
        seen_ids.add(model_id)
        name = " ".join(name.split())
        base = slugify(model_id)
        if not SLUG_RE.fullmatch(base):
            continue
        slug, n = base, 2
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        used[slug] = model_id

        series = history.get(model_id)
        if not isinstance(series, list):
            series = []
        prev = series[-1] if series and isinstance(series[-1], dict) else None
        var = variation(prev, prompt, completion)
        if not same_price(prev, prompt, completion):
            series.append({"date": today, "prompt": prompt, "completion": completion})
            history[model_id] = series

        created = datetime.fromtimestamp(int(created_ts), timezone.utc).strftime("%Y-%m-%d")
        ctx_label = f"{int(ctx)} tokens"
        hf = model.get("hugging_face_id")
        pesos = hf.strip() if isinstance(hf, str) and hf.strip() else "no publicados"
        summary = (
            f"{name} ({model_id}): {price_clause('prompt', prompt_label)} y "
            f"{price_clause('completion', completion_label)}, con contexto de {ctx_label}. "
            f"Modalidad {modality}; fecha de creacion {created}; "
            f"variacion frente al snapshot anterior: {var}; pesos: {pesos}."
        )
        facts = [
            ["Precio prompt / 1M", prompt_label],
            ["Precio completion / 1M", completion_label],
            ["Contexto", ctx_label],
            ["Modalidades", modality],
            ["Fecha de creacion", created],
            ["Variacion de precio", var],
            ["Pesos", pesos],
        ]
        source = f"https://openrouter.ai/{model_id}"
        updated = today
        old = prev_by_source.get(source)
        if isinstance(old, dict) and old.get("facts") == facts and old.get("summary") == summary and isinstance(old.get("updated"), str):
            updated = old["updated"]
        items.append({
            "slug": slug,
            "title": name,
            "summary": summary,
            "facts": facts,
            "group": provider_of(model_id),
            "updated": updated,
            "source": source,
        })

    if len(items) < MIN_ITEMS:
        fail(f"solo {len(items)} modelos validos; no se escribe data/")

    items.sort(key=lambda it: it["slug"])
    DATA.mkdir(parents=True, exist_ok=True)
    ITEMS_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    HISTORY_PATH.write_text(json.dumps(history, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ok: {len(items)} modelos")


if __name__ == "__main__":
    main()
