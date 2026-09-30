---
name: web-design
description: Any page, landing, dashboard or component (HTML/CSS/JSX), or "diseño", "web bonita", "UI", "landing". Google Stitch designs, you integrate.
---

# Web design

Stitch (MCP `stitch`, Gemini) designs; you do not design from scratch.

## Style = `DESIGN.md`

- The repo's `DESIGN.md` holds the style and the Stitch ids. Missing: create it with this default and the user's wishes on top:
  `Minimal y moderno, estilo estudio actual. Mucho aire, jerarquía clara, 1 color de acento, tipografía con carácter. Claro y oscuro. Nada de degradados morados, emojis como iconos, todo centrado ni plantillas genéricas.`
- Existing design (Stitch/Figma export, tokens, components): follow it.

## Steps

1. New page or full restyle: `create_project` once (reuse the project id from `DESIGN.md`; only this repo's project), then `generate_screen_from_text` with purpose, real content, the `DESIGN.md` style, `deviceType: MOBILE` and `modelId: GEMINI_3_8_FLASH` (always; the proxy forces it too). Always mobile-first, one screen: the prompt must say the same layout starts at 360px and scales to tablet (768) and desktop (1280+). Do not generate extra DESKTOP, TABLET or AGNOSTIC screens. Changes to an existing screen: `edit_screens` with the same rule.
   Generate/edit/variants always through `stitch_long` (`tool` + its normal `arguments`), never directly: direct calls die at 60 s and Stitch needs 1-4 min. If it returns `status: running`, call `stitch_wait(job)` again until the result arrives. Only over 10 min is something wrong: report FALLO.
2. `get_screen`: download its HTML and screenshot. Keep layout, palette and type; adapt to the repo stack (static: one HTML + CSS, no build; React: Tailwind v4 + shadcn/ui). No unused CSS/JS, real text.
3. Write the project/screen ids in `DESIGN.md`.
4. Small tweaks (a button, a color, spacing): edit directly, no Stitch.
5. Stitch missing or failing: hand-build following `DESIGN.md`.

## Before HECHO

Responsive 360-1440px without horizontal scroll, WCAG AA contrast, visible focus, `alt` on images, `prefers-reduced-motion`. Look at it with skill `verify`.
