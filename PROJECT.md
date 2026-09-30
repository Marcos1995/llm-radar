<!-- managed-by-telegram-cursor-bot:agent-kit -->
# Contexto del proyecto

## Produccion
- URL: https://github.com/Marcos1995/llm-radar
- Vista: https://marcos1995.github.io/llm-radar/ (repo público; Chrome)
- Vista local: `index.html`

## Estado
- Portada con ganadores por gama, pesos publicados y tokens por dólar, más `/comparar/` para dos modelos. Sin índice de inteligencia: OpenRouter no publica tests.
- Un modelo por pagina: precio, contexto, modalidades, fecha, variacion y si hay pesos en Hugging Face.
- `fetch.py` lee la API publica, reescribe `data/items.json` y solo anade en `data/history.json` cuando cambia el precio (la primera observacion tambien se guarda).
- `build.py` genera `_site/` con el estilo de DESIGN.md (Stitch). La logica de datos del kit no cambia. Mas de 100 paginas indexables.

## Stack
- Python 3.11, stdlib (`urllib`, `json`). Sin dependencias ni APIs de pago.
- Sitio estatico: `project.json` + `data/items.json` + `build.py`.

## Comandos utiles
- Instalar: no hace falta
- Test: `python fetch.py && python build.py` (indexables en `_site/health.json`)
- Dev: `python build.py` y abrir `_site/index.html`

## Notas para el agente
- No editar `.github/workflows/update.yml`. En `build.py`, la presentacion sigue DESIGN.md; la logica de datos queda la del kit.
- Si OpenRouter falla o hay menos de 100 modelos validos, `fetch.py` sale 1 y no toca `data/`.
- El prefijo `~` de un id es un alias; el grupo es el proveedor sin esa tilde. Precio `-1` = variable.
- Lean kit (ver AGENTS.md)
