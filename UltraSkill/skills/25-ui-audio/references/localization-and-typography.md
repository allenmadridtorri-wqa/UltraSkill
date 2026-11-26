# Localization and Typography

Hardcoding English strings (`button.text = "Start Game"`) inside scene files or scripts makes localization a painful rewrite. Externalize every user-visible string from Day 1.

---

## 1. Key Naming & Placeholder Conventions

Use structured uppercase semantic keys (`DOMAIN_CONTEXT_ELEMENT`):

| Key | `en` (English) | `de` (German) | `es` (Spanish) | `ja` (Japanese) |
|---|---|---|---|---|
| `UI_MAIN_START` | `Start Expedition` | `Expedition starten` | `Iniciar expedición` | `遠征を開始` |
| `HUD_PROMPT_OPEN` | `Open {target}` | `{target} öffnen` | `Abrir {target}` | `{target}を開ける` |
| `COMBAT_DMG_DEALT` | `{attacker} dealt {amount} damage` | `{attacker} verursachte {amount} Schaden` | `{attacker} infligió {amount} de daño` | `{attacker}は{amount}のダメージを与えた` |

### Rules for Translators & Programmers
1. **Named Placeholders (`{target}`, `{amount}`), Never Positional `%s`**:
   - Word order changes across languages (`"Open {target}"` vs `"{target}を開ける"`). Named placeholders allow translators to reorder tokens safely without crashing `printf`.
2. **Never Concatenate Sentence Fragments**:
   - Bad: `tr("WORD_OPEN") + " " + tr("NOUN_DOOR")` (breaks gender agreement, case inflection, and word order).
   - Good: Complete keyed template `tr("HUD_PROMPT_OPEN").format({"target": tr("NOUN_DOOR")})`.

---

## 2. Layout Expansion Budget (`+35%` Rule)

English is compact. German, French, Spanish, and Russian translations are routinely **`30%–45%` wider** than English, while CJK (Chinese/Japanese/Korean) glyphs require **`+15%` taller line height** to prevent vertical clipping.

- Never size a button tightly around its English text (`width = 90 px`). Give buttons at least `35%` horizontal breathing room or flexible `MinSize + Container Padding`, and enable text wrapping or slight auto-fit scaling (`min_font_scale = 0.80`) as a safety net.

---

## 3. Typography Hierarchy (Max 2 Font Families)

1. **Display / Header Font**: High-character display typeface for title cards, boss names, and major section headers (`Bold`, tracking `+0.04em`).
2. **UI & Body Font**: High-legibility sans-serif with distinct `1 / I / l` and `0 / O` glyphs (`Inter`, `Noto Sans`, `Atkinson Hyperlegible`) for subtitles, item stats, and dialogue (`line-height: 1.4`).
3. **Tabular Numerals (`font-variant-numeric: tabular-nums`)**:
   - Mandatory for timers, ammo counters, damage numbers, and currency readouts so digits do not jitter horizontally as numbers tick down.
