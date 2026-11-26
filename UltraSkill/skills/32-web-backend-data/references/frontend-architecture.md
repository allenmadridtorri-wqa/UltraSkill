# Frontend Architecture and Web Accessibility

A production web frontend is fast on a 4 GB RAM laptop, resilient to slow networks, and 100% operable via keyboard and screen readers.

---

## 1. The Four Mandatory View States

Every data-driven component or view must explicitly design and render four states:
1. **`Loading` (Skeleton / Spinner after `150 ms` delay)**: Reserve exact layout dimensions (`min-height` or `aspect-ratio`) to prevent Cumulative Layout Shift (`CLS = 0`).
2. **`Empty` (Zero State)**: Clear explanation + primary Call-To-Action button (e.g., *"No render jobs queued yet. [Create First Render Job]"*).
3. **`Error` (Recoverable Failure)**: Human-readable reason + `Retry` button (never leave a blank white screen or silent console error).
4. **`Ready` (Populated Data)**: Virtualized list or paginated table when row count exceeds `200` items.

---

## 2. State Partitioning (Do Not Dump Everything in One Global Store)

| State Category | Examples | Where It Belongs |
|---|---|---|
| **URL / Route State** | Active tab, search query `?q=`, sort column, page cursor, selected item ID | **URL Search Params (`history.pushState`)** so refreshing or sharing the link preserves the exact view |
| **Server Cache State** | Fetched project lists, user profile, job statuses | Dedicated fetch cache with `AbortController`, staleness TTL, and optimistic mutation rollback |
| **Local Ephemeral UI State** | Dropdown open/closed, current unsubmitted input text, hover tooltip | Component-local state |

---

## 3. Accessibility & Performance Baseline

- **Semantic HTML First**: Use real `<button>`, `<a href>`, `<label for="...">`, `<dialog>`, and `<main>` elements before reaching for `aria-*` attributes. Never put `@click` on a bare `<div>` without `role="button"`, `tabindex="0"`, and `Enter`/`Space` key handlers.
- **Visible Focus Ring**: Always style `:focus-visible` with a high-contrast `2px solid` outline (`offset: 2px`). Never write `outline: none` without a replacement focus indicator.
- **Bundle & Asset Budget**: Keep initial JS bundle `< 150 KB` gzipped, lazy-load heavy routes/3D canvases (`import()`), and specify explicit `width`/`height` on all `<img>` tags.
