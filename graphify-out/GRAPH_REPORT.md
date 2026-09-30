# Graph Report - llm-radar  (2026-09-30)

## Corpus Check
- 14 files · ~3,091 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: .mdc 2, (none) 1)

## Summary
- 62 nodes · 54 edges · 13 communities (10 shown, 3 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

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

## God Nodes (most connected - your core abstractions)
1. `Debug` - 6 edges
2. `Contexto del proyecto` - 6 edges
3. `build()` - 5 edges
4. `Verify (UI)` - 4 edges
5. `Web design` - 4 edges
6. `esc()` - 3 edges
7. `page()` - 3 edges
8. `Build judgments with Laya` - 3 edges
9. `Laya` - 3 edges
10. `Review` - 3 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (13 total, 3 thin omitted)

### Community 0 - "build.py"
Cohesion: 0.20
Nodes (13): build(), esc(), page(), Genera el sitio estatico en _site/ desde project.json + data/items.json. Copia…, validate(), write(), datetime, html (+5 more)

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

## Knowledge Gaps
- **26 isolated node(s):** `1. Root cause`, `2. Compare`, `3. Hypothesis`, `4. Fix`, `Red flags → back to step 1` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 47 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `1. Root cause`, `2. Compare`, `3. Hypothesis` to the rest of the system?**
  _26 weakly-connected nodes found - possible documentation gaps or missing edges._