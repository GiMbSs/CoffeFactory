--- 
applyTo: '**/*'
---

access mcp servers to get more context

## Purpose

Copilot must create a **Django + DRF backend** and an **HTML/CSS/JS frontend** following robust architecture, clean code, and industry best practices. Every output must respect the rules below.

---

## Core Principles

* ✅ **Robustness** over speed: secure, maintainable, production-ready code.
* ✅ **Consistency** across backend, API, and templates.
* ✅ **Follow Django & DRF conventions strictly**.
* ✅ **HTML-first approach** for frontend; minimal, clean, accessible design.
* ✅ **All templates must share the same design tokens and structure**.

---

## Backend (Django + DRF)

* Always use **Django ≥ 5** and **DRF ≥ 3.15**.
* Use **PostgreSQL** (psycopg3).
* Split settings: `base.py`, `dev.py`, `prod.py`.
* Use environment variables for secrets. Never hardcode credentials.
* Use **UUID** as primary keys and a base abstract model with timestamps.
* Add **DRF API** at `/api/v1/` (versioned).
* Implement **pagination**, **filtering**, **ordering**, and **search**.
* Standardize error responses:

```json
{
  "error": {"code": "error_code", "message": "Readable summary", "details": {}}
}
```

* Always provide **OpenAPI docs** using `drf-spectacular`.
* Tests: pytest + coverage ≥ 90%.

---

## Frontend (HTML + CSS + JS)

* **All templates extend `base.html`** and include consistent header/footer/flash messages.
* Use **partials**: `_header.html`, `_footer.html`, `_flash.html`.
* **Design rules:**

  * Use **CSS variables** for colors, spacing, typography.
  * Follow **BEM** naming convention.
  * Ensure **symmetry** and spacing rhythm using predefined scale.
  * No inline styles or inline JS.
* **Accessibility:** semantic HTML, visible focus states, labels for inputs.

---

### Example Template Structure

```
base.html → blocks: title, meta, styles, content, scripts
partials/: _header.html, _footer.html, _flash.html
static/css/main.css → tokens + layout + utilities
static/js/main.js → modular, no globals
```

---

## JS Rules

* ES modules only, single entry file `main.js`.
* No jQuery or external libraries unless absolutely required.
* Use `data-*` attributes for DOM hooks.

---

## Quality

* Use **Black**, **isort**, **Ruff**, **mypy**.
* Configure **pre-commit hooks**.
* CI pipeline runs lint, format check, and tests.

---

## Must-Have Pages

* Home page with grid-based layout (cards, typography consistent with tokens).
* API docs at `/api/docs/`.

---

## Never Do

* ❌ Hardcode secrets or credentials.
* ❌ Use inconsistent template structure.
* ❌ Inline styles or JS.
* ❌ Global variables in JS.

---

## Deliverables

* Full Django project with apps: `core`, `accounts`, `api`.
* Base template and partials.
* CSS design tokens and utilities.
* Tests for models, serializers, and views.
* OpenAPI schema and docs.
* README with setup instructions.

---

## Advanced Prompting for Copilot (MCPS)

### 1. Role + Goal Prompting

```
You are a senior Python/Django engineer. Your goal is to build a production-ready Django + DRF project with consistent frontend templates (HTML/CSS/JS), following best practices and clean architecture.
```

### 2. Output Format Constraints

```
Always generate complete files with proper imports, docstrings, and comments when creating Python modules.
```

### 3. Few-Shot Examples

Provide examples of templates or CSS tokens inside the context so Copilot follows them.

### 4. Checklist Mode

```
Before writing code:
- Verify app name follows Django conventions.
- Ensure BEM naming in CSS.
- Ensure design tokens are applied.
```

### 5. Role-Specific Mode Switching

Use explicit section headers like:

```
### BACKEND TASK: Create Django model for X
### FRONTEND TASK: Build HTML template extending base.html
```

### 6. Explicit Constraints

```
Do not use jQuery or Bootstrap. Use vanilla JS with ES modules and CSS grid.
```

### 7. Step-by-Step Execution

Break tasks into steps:

```
Step 1: Initialize Django project.
Step 2: Configure settings split.
Step 3: Implement templates with tokens.
```

### 8. Consistency Enforcement

```
All files must:
- Follow PEP8 and Black formatting.
- Include docstrings for public functions/classes.
- Pass mypy type checks.
```

---
## Final Note