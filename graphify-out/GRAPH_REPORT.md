# Graph Report - llm-radar  (2026-09-30)

## Corpus Check
- 18 files · ~64,674 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: .mdc 2, (none) 1)

## Summary
- 96 nodes · 131 edges · 19 communities (14 shown, 5 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7513da46`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- build.py
- Debug
- Contexto del proyecto
- Verify (UI)
- Web design
- Agent rules
- Build judgments with Laya
- Laya
- Review
- Project
- fetch.py
- LLM Radar
- build
- priced
- card_html
- band_of
- DECISIONES.md

## God Nodes (most connected - your core abstractions)
1. `build()` - 14 edges
2. `main()` - 11 edges
3. `priced()` - 6 edges
4. `Debug` - 6 edges
5. `Contexto del proyecto` - 6 edges
6. `esc()` - 5 edges
7. `plain()` - 5 edges
8. `compact()` - 5 edges
9. `card_html()` - 5 edges
10. `band_of()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `card_html()` --calls--> `esc()`  [EXTRACTED]
  build.py → build.py  _Bridges community 14 → community 16_
- `band_of()` --references--> `Decimal`  [EXTRACTED]
  build.py →   _Bridges community 16 → community 17_
- `parse_usd()` --references--> `Decimal`  [EXTRACTED]
  build.py →   _Bridges community 16 → community 15_
- `build()` --calls--> `fact_map()`  [EXTRACTED]
  build.py → build.py  _Bridges community 15 → community 14_
- `build()` --calls--> `band_of()`  [EXTRACTED]
  build.py → build.py  _Bridges community 17 → community 14_

## Import Cycles
- None detected.

## Communities (19 total, 5 thin omitted)

### Community 0 - "build.py"
Cohesion: 0.22
Nodes (8): Genera el sitio estatico en _site/ desde project.json + data/items.json. Copia…, datetime, html, json, pathlib, re, shutil, sys

### Community 1 - "Debug"
Cohesion: 0.29
Nodes (6): 1. Root cause, 2. Compare, 3. Hypothesis, 4. Fix, Debug, Red flags → back to step 1

### Community 2 - "Contexto del proyecto"
Cohesion: 0.29
Nodes (6): Comandos utiles, Contexto del proyecto, Estado, Notas para el agente, Produccion, Stack

### Community 3 - "Verify (UI)"
Cohesion: 0.40
Nodes (4): 1. Screenshots, 2. Look, 3. Fix and repeat, Verify (UI)

### Community 4 - "Web design"
Cohesion: 0.40
Nodes (4): Before HECHO, Steps, Style = `DESIGN.md`, Web design

### Community 5 - "Agent rules"
Cohesion: 0.50
Nodes (3): Agent rules, Flujo, Think → Simple → Surgical → Verify (Karpathy)

### Community 6 - "Build judgments with Laya"
Cohesion: 0.50
Nodes (3): Build judgments with Laya, Call, Design

### Community 7 - "Laya"
Cohesion: 0.50
Nodes (3): Laya, Reply (decision-only requests), Steps

### Community 8 - "Review"
Cohesion: 0.50
Nodes (3): Check, Do, Review

### Community 9 - "Project"
Cohesion: 0.50
Nodes (3): Docs, Project, Setup

### Community 10 - "fetch.py"
Cohesion: 0.22
Nodes (17): change_phrase(), fail(), fetch_models(), load_json(), main(), modality_text(), plain(), price_clause() (+9 more)

### Community 14 - "build"
Cohesion: 0.47
Nodes (6): bars_html(), build(), esc(), page(), validate(), write()

### Community 15 - "priced"
Cohesion: 0.40
Nodes (5): fact_map(), model_id_of(), parse_ctx(), parse_usd(), priced()

### Community 16 - "card_html"
Cohesion: 0.83
Nodes (4): card_html(), compact(), plain(), Decimal

## Knowledge Gaps
- **28 isolated node(s):** `1. Root cause`, `2. Compare`, `3. Hypothesis`, `4. Fix`, `Red flags → back to step 1` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 48 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `picks_for()` connect `band_of` to `build.py`, `build`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Why does `build()` connect `build` to `build.py`, `band_of`, `card_html`, `priced`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **What connects `1. Root cause`, `2. Compare`, `3. Hypothesis` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._