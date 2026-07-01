---

version: 1.1.0
name: universal-design-framework
description: 'Stack-agnostic design-to-code framework synthesized from 73+ brand analyses. Maps into any framework via adapter pattern. VoltAgent-verified: electric-green accent, near-black canvas, hairline-on-dark
  components, composite example recipes.'
stack_policy: {dependency: none, rule: 'Do not assume any framework, runtime, styling library, component kit, icon package, or design tool.', adapter_requirement: Map tokens and specs into the project's
    existing primitives.}
colors: {primary: '#0066cc', primary-hover: '#0052a3', primary-pressed: '#003d7a', primary-subtle: '#e5f0ff', on-primary: '#ffffff', accent: '#7c3aed', accent-hover: '#6d28d9', accent-subtle: '#ede9fe',
  on-accent: '#ffffff', canvas: '#ffffff', canvas-soft: '#f5f5f7', canvas-warm: '#f8f5f0', surface-1: '#fafafa', surface-2: '#f0f0f0', surface-inverse: '#0a0a0a', surface-inverse-soft: '#1a1a1a', dark-canvas: '#0a0a0a',
  dark-surface-1: '#141414', dark-surface-2: '#1a1a1a', dark-surface-elevated: '#242424', dark-border: '#2a2d33', dark-border-strong: '#3a3f47', ink: '#0d0d0d', ink-secondary: '#555555', ink-muted: '#888888',
  ink-faint: '#aaaaaa', ink-on-dark: '#ffffff', ink-on-dark-muted: '#999999', success: '#16a34a', success-soft: '#dcfce7', warning: '#f59e0b', warning-soft: '#fef3c7', error: '#dc2626', error-soft: '#fee2e2',
  info: '#2563eb', info-soft: '#dbeafe', hairline: '#e5e5e5', hairline-strong: '#d4d4d4', hairline-on-dark: '#2a2a2a', hairline-on-dark-strong: '#3a3a3a', code-bg: '#0b0d10', code-border: '#24272e', code-text: '#f7f7f5',
  gradient-primary-start: '#0066cc', gradient-primary-mid: '#7c3aed', gradient-primary-end: '#ec4899', gradient-cool-start: '#06b6d4', gradient-cool-end: '#635bff'}
# ─── Process-State Palette ──────────────────────────
process_states:
  thinking: {tint: '#e8dcff', strong: '#9b7cff'}
  searching: {tint: '#d9f0dc', strong: '#5fa866'}
  reading: {tint: '#d6e4f4', strong: '#4f7fbf'}
  editing: {tint: '#e8d9f0', strong: '#9b6bc4'}
  running: {tint: '#ffe3b0', strong: '#c08532'}
  done: {tint: '#dcfce7', strong: '#16a34a'}
# ─── Typography ────────────────────────────────────
typography:
  families: {display: 'Inter, system-ui, -apple-system, sans-serif', body: 'Inter, system-ui, -apple-system, sans-serif', mono: 'JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, monospace'}
  opentype: kern, liga, calt, ss01, tnum, cv11 enabled globally
  scale:
    display-2xl: {size: 72, weight: 700, lineHeight: 1.05, letterSpacing: -2.5, family: display, use: Hero}
    display-xl: {size: 56, weight: 700, lineHeight: 1.08, letterSpacing: -2, family: display, use: Section openers}
    display-lg: {size: 40, weight: 600, lineHeight: 1.12, letterSpacing: -1, family: display, use: Headlines}
    display-md: {size: 32, weight: 600, lineHeight: 1.2, letterSpacing: -0.5, family: display, use: Card titles}
    display-sm: {size: 24, weight: 600, lineHeight: 1.3, letterSpacing: -0.3, family: display, use: Compact titles}
    headline: {size: 20, weight: 600, lineHeight: 1.35, family: display, use: Sub-headings}
    body-lg: {size: 18, weight: 400, lineHeight: 1.55, family: body, use: Lead paragraphs}
    body-md: {size: 16, weight: 400, lineHeight: 1.5, family: body, use: Default body}
    body-sm: {size: 14, weight: 400, lineHeight: 1.45, family: body, use: Secondary text}
    body-xs: {size: 12, weight: 400, lineHeight: 1.4, family: body, use: Captions}
    button: {size: 14, weight: 500, lineHeight: 1, family: body, use: Button labels}
    button-lg: {size: 16, weight: 500, lineHeight: 1, family: body, use: Large button}
    code: {size: 13, weight: 400, lineHeight: 1.55, letterSpacing: 0, family: mono, use: Code blocks}
    eyebrow-mono: {size: 12, weight: 500, lineHeight: 1.2, letterSpacing: 1, family: mono, use: Section eyebrows}
    numeric: {size: 48, weight: 700, lineHeight: 1, letterSpacing: -1.5, family: display, use: Stat callouts}
    keycap: {size: 11, weight: 500, lineHeight: 1.2, letterSpacing: 0.4, family: mono, use: Keyboard shortcuts}
# ─── Display Tracking ──────────────────────────────
display_tracking:
  rule: Tighter tracking at larger sizes differentiates premium from generic.
  sizes:
  - {max: 24, tracking: -0.005em to 0}
  - {min: 24, max: 44, tracking: -0.020em to -0.045em}
  - {min: 44, max: 72, tracking: -0.045em to -0.055em}
  - {min: 72, tracking: -0.055em to -0.060em}
text_width: {hero_headline: 920px, hero_supporting: 720px, article_content: 760px, form_descriptions: 540px, card_copy: 420px}
rounded: {none: 0, xs: 4, sm: 6, md: 8, lg: 12, xl: 16, xxl: 24, pill: 9999, full: 50%}
spacing: {xxs: 2, xs: 4, sm: 8, md: 12, lg: 16, xl: 24, xxl: 32, 3xl: 48, 4xl: 64, 5xl: 96, 6xl: 128}
spacing_relationships: {label_to_field: 6-8, field_to_helper: 6-8, icon_to_label: '8', button_group_gap: 8-12, form_field_group: 16-24, card_internal_padding: 20-28, section_padding: 48-80, major_section_gap: 80-128}
breakpoints: {mobile: 480, tablet: 768, desktop: 1024, wide: 1280, ultra: 1440}
grid:
  columns: {compact: 4, medium: 8, expanded: 12, wide: 12}
  gutter: {compact: 16, medium: 24, expanded: 28, wide: 32}
  margin: {compact: 20, medium: 32, expanded: 48, wide: 80}
containers: {sm: 720, md: 960, lg: 1180, xl: 1320, full: 100%}
shadows: {level-0: none, level-1: '0 1px 2px rgba(0,0,0,0.04)', level-2: '0 1px 3px rgba(0,0,0,0.06), 0 2px 6px rgba(0,0,0,0.04)', level-3: '0 4px 12px rgba(0,0,0,0.08)', level-4: '0 8px 24px rgba(0,0,0,0.10)',
  level-5: '0 16px 48px rgba(0,0,0,0.12)', product: 'rgba(0,0,0,0.20) 0 8px 30px', glow: soft accent glow 48-56px (AI/hero only), modal-overlay: 'rgba(0,0,0,0.5)', voltagent-hairline: '0 0 0 1px {colors.hairline-on-dark}',
  voltagent-glow: '0 0 15px rgba(92,88,85,0.2)', voltagent-modal: '0 20px 60px rgba(0,0,0,0.7), 0 0 0 1px rgba(148,163,184,0.1) inset'}
motion: {fast: 100, base: 160, slow: 240, page: 360, easing_standard: 'cubic-bezier(0.2,0,0,1)', easing_out: 'cubic-bezier(0,0,0.2,1)', easing_in_out: 'cubic-bezier(0.4,0,0.2,1)', press_scale: 0.96, press_opacity: 0.9}
# ─── Components ────────────────────────────────────
components:
# State pattern: hover=opacity 0.9+scale 0.96, pressed=scale(0.96), disabled=opacity 0.5
  button-primary:
    background: '{colors.primary}'
    text: '{colors.on-primary}'
    typography: '{typography.button}'
    rounded: '{rounded.md}'
    padding: '{spacing.sm} {spacing.lg}'
    height: 40
    shadow: '{shadows.level-0}'
    hover: {background: '{colors.primary-hover}'}
    pressed: {transform: 'scale({motion.press_scale})'}
    disabled: {background: '{colors.hairline}', text: '{colors.ink-faint}'}
  button-secondary:
    background: transparent
    text: '{colors.ink}'
    border: 1px solid {colors.hairline-strong}
    padding: '{spacing.sm} {spacing.lg}'
    height: 40
    rounded: '{rounded.md}'
    pressed: {background: '{colors.canvas-soft}'}
  button-ghost:
    background: transparent
    text: '{colors.ink}'
    padding: '{spacing.xs} {spacing.sm}'
    height: 36
    rounded: '{rounded.md}'
    pressed: {background: '{colors.surface-1}'}
  button-destructive:
    background: '{colors.error}'
    text: '{colors.on-primary}'
    padding: '{spacing.sm} {spacing.lg}'
    height: 40
    rounded: '{rounded.md}'
    pressed: {background: '#b91c1c'}
  button-on-dark: {background: '{colors.on-primary}', text: '{colors.ink}', padding: '{spacing.sm} {spacing.lg}', height: 40, rounded: '{rounded.md}'}
  button-primary-pill:
    background: '{colors.primary}'
    text: '{colors.on-primary}'
    rounded: '{rounded.pill}'
    padding: '{spacing.sm} {spacing.lg}'
    height: 40
    pressed: {background: '{colors.primary-pressed}'}
  icon-button: {background: '{colors.canvas}', text: '{colors.ink}', rounded: '{rounded.full}', size: 44, border: '1px solid {colors.hairline}'}
  button-outline-on-dark:
    background: '{colors.dark-canvas}'
    text: '{colors.ink-on-dark}'
    border: 1px solid {colors.hairline-on-dark}
    rounded: '{rounded.sm}'
    padding: '{spacing.md} {spacing.lg}'
    height: 44
    pressed: {background: '{colors.dark-surface-1}'}
  button-ghost-green:
    background: transparent
    text: '{colors.primary}'
    rounded: '{rounded.sm}'
    padding: '{spacing.sm} {spacing.lg}'
    height: 40
    pressed: {opacity: 0.8}
  button-pill-tag: {background: transparent, text: '{colors.ink}', border: '1px solid {colors.hairline}', rounded: '{rounded.pill}', padding: '{spacing.xs} {spacing.md}', typography: '{typography.body-sm}',
    height: 28}
  card-base: {background: '{colors.canvas}', text: '{colors.ink}', rounded: '{rounded.lg}', padding: '{spacing.xl}', border: '1px solid {colors.hairline}', shadow: '{shadows.level-1}'}
  card-feature: {background: '{colors.canvas}', text: '{colors.ink}', rounded: '{rounded.lg}', padding: '{spacing.xxl}', border: '1px solid {colors.hairline}', shadow: '{shadows.level-2}'}
  card-elevated: {background: '{colors.canvas}', text: '{colors.ink}', rounded: '{rounded.lg}', padding: '{spacing.xl}', shadow: '{shadows.level-3}'}
  card-dark: {background: '{colors.surface-inverse-soft}', text: '{colors.ink-on-dark}', rounded: '{rounded.lg}', padding: '{spacing.xl}'}
  card-pricing: {background: '{colors.canvas}', text: '{colors.ink}', border: '1px solid {colors.hairline}', padding: '{spacing.xxl}', rounded: '{rounded.lg}'}
  card-pricing-featured: {background: '{colors.surface-inverse}', text: '{colors.ink-on-dark}', border: '2px solid {colors.primary}', padding: '{spacing.xxl}', rounded: '{rounded.lg}'}
  card-soft: {background: '{colors.canvas-soft}', text: '{colors.ink}', padding: '{spacing.xl}', rounded: '{rounded.lg}'}
  card-product-mockup: {background: '{colors.canvas}', text: '{colors.ink}', padding: '{spacing.lg}', rounded: '{rounded.lg}', shadow: '{shadows.product}'}
  card-interactive:
    background: '{colors.canvas}'
    text: '{colors.ink}'
    border: 1px solid {colors.hairline}
    padding: '{spacing.lg}'
    rounded: '{rounded.lg}'
    hover: {border: '{colors.hairline-strong}', shadow: '{shadows.level-2}'}
  card-feature-emphasized: {background: '{colors.canvas}', text: '{colors.ink}', border: '3px solid {colors.hairline}', padding: '{spacing.xl}', rounded: '{rounded.md}'}
  text-input:
    background: '{colors.canvas}'
    text: '{colors.ink}'
    border: 1px solid {colors.hairline-strong}
    rounded: '{rounded.md}'
    padding: '{spacing.sm} {spacing.md}'
    height: 44
    typography: '{typography.body-md}'
    focus: {border: '2px solid {colors.primary}'}
    error: {border: '2px solid {colors.error}'}
  textarea: {background: '{colors.canvas}', text: '{colors.ink}', border: '1px solid {colors.hairline-strong}', rounded: '{rounded.md}', padding: '{spacing.md}', minHeight: 112}
  search-input: {background: '{colors.canvas-soft}', text: '{colors.ink}', border: '1px solid {colors.hairline}', rounded: '{rounded.pill}', padding: '{spacing.sm} {spacing.lg}', height: 44}
  nav-bar-light: {background: '{colors.canvas}', text: '{colors.ink}', typography: '{typography.body-sm}', height: 64, border: '0 0 1px {colors.hairline} solid', padding: '{spacing.sm} {spacing.xl}'}
  nav-bar-dark: {background: '{colors.surface-inverse}', text: '{colors.ink-on-dark}', typography: '{typography.body-sm}', height: 64, padding: '{spacing.sm} {spacing.xl}'}
  sidebar:
    background: '{colors.canvas}'
    text: '{colors.ink}'
    width: 260
    border: 0 1px 0 0 {colors.hairline} solid
    padding: '{spacing.lg}'
    itemHeight: 36
    itemRadius: '{rounded.md}'
    itemActive: {background: '{colors.accent-subtle}', text: '{colors.accent}'}
  badge-primary: {background: '{colors.primary}', text: '{colors.on-primary}', typography: '{typography.body-xs}', rounded: '{rounded.pill}', padding: '2px {spacing.sm}', height: 24}
  badge-secondary: {background: '{colors.canvas-soft}', text: '{colors.ink-secondary}', typography: '{typography.body-xs}', rounded: '{rounded.pill}', padding: '2px {spacing.sm}', height: 24}
  badge-success: {background: '{colors.success-soft}', text: '{colors.success}', typography: '{typography.body-xs}', rounded: '{rounded.pill}', padding: '2px {spacing.sm}', height: 24}
  badge-warning: {background: '{colors.warning-soft}', text: '{colors.warning}', rounded: '{rounded.pill}', padding: '2px {spacing.sm}', height: 24}
  badge-error: {background: '{colors.error-soft}', text: '{colors.error}', rounded: '{rounded.pill}', padding: '2px {spacing.sm}', height: 24}
  code-block: {background: '{colors.code-bg}', text: '{colors.code-text}', typography: '{typography.code}', rounded: '{rounded.lg}', padding: '{spacing.lg}', border: '1px solid {colors.code-border}'}
  code-inline: {background: '{colors.canvas-soft}', text: '{colors.ink}', typography: '{typography.code}', rounded: '{rounded.xs}', padding: '1px {spacing.xs}'}
  code-mockup: {background: '{colors.code-bg}', text: '{colors.code-text}', typography: '{typography.code}', rounded: '{rounded.lg}', padding: '{spacing.xl}', border: '1px solid {colors.code-border}', chrome: 'window
      dots, file tab, breadcrumb'}
  code-inline-chip: {background: '{colors.canvas-soft}', text: '{colors.ink}', typography: '{typography.code}', rounded: '{rounded.sm}', padding: '{spacing.xxs} {spacing.sm}'}
  keycap: {background: '{colors.canvas-soft}', text: '{colors.ink-secondary}', typography: '{typography.keycap}', rounded: '{rounded.sm}', padding: '2px {spacing.xs}', minWidth: 20, height: 22, border: '1px
      solid {colors.hairline}'}
  inline-alert-neutral: {background: '{colors.canvas-soft}', text: '{colors.ink-secondary}', typography: '{typography.body-sm}', rounded: '{rounded.md}', padding: '{spacing.md} {spacing.lg}'}
  inline-alert-info: {background: '{colors.info-soft}', text: '{colors.info}', rounded: '{rounded.md}', padding: '{spacing.md} {spacing.lg}'}
  inline-alert-success: {background: '{colors.success-soft}', text: '{colors.success}', rounded: '{rounded.md}', padding: '{spacing.md} {spacing.lg}'}
  inline-alert-warning: {background: '{colors.warning-soft}', text: '{colors.warning}', rounded: '{rounded.md}', padding: '{spacing.md} {spacing.lg}'}
  inline-alert-error: {background: '{colors.error-soft}', text: '{colors.error}', rounded: '{rounded.md}', padding: '{spacing.md} {spacing.lg}'}
  table-header: {background: '{colors.canvas-soft}', text: '{colors.ink-secondary}', typography: '{typography.body-sm}', padding: '{spacing.sm} {spacing.md}'}
  table-row: {background: '{colors.canvas}', text: '{colors.ink}', typography: '{typography.body-sm}', padding: '{spacing.sm} {spacing.md}', border: '0 0 1px {colors.hairline} solid'}
  modal: {background: '{colors.canvas}', text: '{colors.ink}', rounded: '{rounded.xl}', padding: '{spacing.xxl}', shadow: '{shadows.level-5}', maxWidth: 560}
  toast-success: {background: '{colors.success}', text: '{colors.on-primary}', typography: '{typography.body-sm}', rounded: '{rounded.md}', padding: '{spacing.md} {spacing.lg}', shadow: '{shadows.level-3}'}
  toast-error: {background: '{colors.error}', text: '{colors.on-primary}', typography: '{typography.body-sm}', rounded: '{rounded.md}', padding: '{spacing.md} {spacing.lg}', shadow: '{shadows.level-3}'}
  hero-band-light: {background: '{colors.canvas}', text: '{colors.ink}', padding: '{spacing.5xl} {spacing.xl}'}
  hero-band-dark: {background: '{colors.surface-inverse}', text: '{colors.ink-on-dark}', padding: '{spacing.5xl} {spacing.xl}'}
  hero-band-gradient: {background: 'linear-gradient(135deg, {colors.gradient-primary-start}, {colors.gradient-primary-mid}, {colors.gradient-primary-end})', text: '{colors.ink-on-dark}', padding: '{spacing.5xl}
      {spacing.xl}'}
  section-band-light: {background: '{colors.canvas}', text: '{colors.ink}', padding: '{spacing.4xl} {spacing.xl}'}
  section-band-soft: {background: '{colors.canvas-soft}', text: '{colors.ink}', padding: '{spacing.4xl} {spacing.xl}'}
  section-band-dark: {background: '{colors.surface-inverse}', text: '{colors.ink-on-dark}', padding: '{spacing.4xl} {spacing.xl}'}
  cta-band: {background: '{colors.primary}', text: '{colors.on-primary}', padding: '{spacing.4xl} {spacing.xl}', rounded: '{rounded.lg}'}
  green-divider-band: {background: '{colors.dark-canvas}', borderTop: '2px solid {colors.primary}', borderBottom: '2px solid {colors.primary}'}
  footer: {background: '{colors.canvas-soft}', text: '{colors.ink-muted}', typography: '{typography.body-sm}', padding: '{spacing.4xl} {spacing.xl}', border: '1px solid {colors.hairline}'}
  divider: {border: '1px solid {colors.hairline}'}
  divider-strong: {border: '1px solid {colors.hairline-strong}'}
  divider-dashed: {border: '1px dashed rgba(79,93,117,0.4)'}
  spinner: {borderColor: '{colors.hairline}', borderTopColor: '{colors.primary}', size: 24, speed: 600ms}
  skeleton: {background: '{colors.hairline}', rounded: '{rounded.sm}', animation: pulse 1.5s infinite}
  avatar: {rounded: '{rounded.full}', size: 40}
  avatar-sm: {rounded: '{rounded.full}', size: 32}
  avatar-lg: {rounded: '{rounded.full}', size: 56}
  empty-state: {background: '{colors.canvas}', text: '{colors.ink}', typography: '{typography.body-md}', padding: '{spacing.xxl}', icon_size: 48}
  link: {text: '{colors.primary}', typography: '{typography.body-md}', underline: hover}
  link-on-dark: {text: '{colors.info}', typography: '{typography.body-md}', underline: hover}
  breadcrumb: {text: '{colors.ink-muted}', typography: '{typography.body-sm}'}
  breadcrumb-active: {text: '{colors.ink}'}
  stat-number: {text: '{colors.primary}', typography: '{typography.numeric}'}
  stat-label: {text: '{colors.ink-secondary}', typography: '{typography.body-sm}'}
  logo-strip: {background: '{colors.canvas}', text: '{colors.ink-muted}', padding: '{spacing.xl}'}
  ex-pricing-tier: {background: '{colors.canvas-soft}', rounded: '{rounded.md}', padding: '{spacing.xxl}'}
  ex-pricing-tier-featured: {background: '{colors.surface-inverse}', text: '{colors.ink-on-dark}', rounded: '{rounded.md}', padding: '{spacing.xxl}'}
  ex-product-selector: {background: '{colors.canvas-soft}', rounded: '{rounded.md}', padding: '{spacing.xxl}'}
  ex-cart-drawer: {background: '{colors.canvas}', rounded: '{rounded.md}', padding: '{spacing.xxl}', itemDivider: '{colors.hairline}'}
  ex-app-shell-row: {background: '{colors.canvas}', rounded: '{rounded.sm}', padding: '{spacing.md} {spacing.lg}', activeIndicator: '{colors.primary}'}
  ex-data-table-cell: {headerBackground: '{colors.canvas-soft}', headerTypography: '{typography.caption}', bodyTypography: '{typography.body-sm}', cellPadding: '{spacing.md} {spacing.lg}', rowBorder: '{colors.hairline}'}
  ex-auth-form-card: {background: '{colors.canvas-soft}', rounded: '{rounded.md}', padding: '{spacing.xxl}'}
  ex-modal-card: {background: '{colors.canvas}', rounded: '{rounded.md}', padding: '{spacing.xxl}'}
  ex-empty-state-card: {background: '{colors.canvas-soft}', rounded: '{rounded.md}', padding: '{spacing.xxl}', captionTypography: '{typography.body-md}'}
  ex-toast: {background: '{colors.canvas}', rounded: '{rounded.md}', padding: '{spacing.md} {spacing.lg}', typography: '{typography.body-sm}'}
---

# Design System: Universal Framework v2

> Stack-agnostic design-to-code framework synthesized from 73+ brand analyses.
> Source of truth for UI generation, product design, and AI coding agents.
> VoltAgent-verified: includes electric-green accent, near-black canvas,
> hairline-on-dark components, and composite example recipes for UI consistency.

**License:** MIT. **Version:** 1.1.0 (see `kit/manifest.json`).
**How to use:** Read the YAML frontmatter for exact tokens. Use narrative sections for behavioral rules. Map into your framework via the adapter pattern in §0.

---

## 0. Stack-Agnostic Contract

This document defines design intent, tokens, behavior, and patterns — never a framework or dependency.

| Allowed                             | Not allowed                       |
| ----------------------------------- | --------------------------------- |
| Token names, values, contrast roles | Named framework or runtime        |
| Type scale, weights, line heights   | Named UI kit or component library |
| Spacing, grids, density, responsive | Named styling system              |
| Component anatomy, states, behavior | Named icon or font package        |
| Motion durations, easing feel       | Named build tool                  |

**Adapter Rule:** Map tokens into whatever the host project already uses. No new dependencies.

| Token category | Becomes in a project                                        |
| -------------- | ----------------------------------------------------------- |
| Color          | Theme values, CSS custom properties, native color resources |
| Type           | Text styles, typography scale, native text appearances      |
| Spacing        | Layout constants, sizing resources, grid variables          |
| Radius         | Shape styles, corner radius constants                       |
| Elevation      | Shadow styles, native elevation values                      |
| Motion         | Animation constants, transition presets                     |
| Components     | Local components, design-tool components, native views      |

---

## 1. Design DNA

**10 Principles:**
1. Clarity is the highest aesthetic.
2. The next action must be obvious.
3. Whitespace creates structure, not emptiness.
4. Borders and surface contrast come before heavy shadows.
5. Accent color is a signal, not decoration.
6. Gradients appear only in signature moments.
7. Motion explains change; it never distracts.
8. Product UI evidence is stronger than abstract decoration.
9. Every screen includes all important states (default, hover, press, focus, disabled, loading, empty, error, success).
10. The system feels coherent across marketing, app, docs, and mobile.

**Hierarchy cascade:** Brand accent → Surface contrast → Type weight+size → Spacing rhythm → Radius → Shadow.

---

## 2. Usage Boundaries

**Best suited for:** AI SaaS, developer tools, productivity, dashboards, analytics, internal tools, docs, pricing, auth, landing pages, mobile companions.

**Not without adaptation:** Playful consumer apps, children's products, luxury fashion, photo-first lifestyle apps, games.

**Brand Modes** — pick one:

| Mode              | Use                    | Key adjustments                                   |
| ----------------- | ---------------------- | ------------------------------------------------- |
| `default-product` | SaaS, AI, dashboards   | Neutral, indigo accent, subtle gradients          |
| `developer`       | APIs, dev tools, docs  | More mono, code blocks, less decoration           |
| `enterprise`      | B2B, security, finance | Less gradient, stronger structure                 |
| `creator`         | Collaboration tools    | Warmer surfaces, friendlier copy                  |
| `ai-native`       | AI agents, copilots    | Tool-status chips, provenance, progressive states |
| `data-heavy`      | Analytics, ops         | Denser tables, tabular numerals, fewer cards      |

---

## 3. Visual Archetypes

| Archetype            | Canvas                 | Accent                | Best for                              |
| -------------------- | ---------------------- | --------------------- | ------------------------------------- |
| **Dark Immersive**   | #0a0a0a–#121212        | Single bright         | Developer tools, media, entertainment |
| **Clean White**      | #ffffff–#fafafa        | Single subdued        | Fintech, B2B, docs                    |
| **Premium Gallery**  | Alternating light/dark | Single voltage        | Luxury, product marketing             |
| **Colorful Playful** | Pastel tints           | Multiple brand colors | Creative, consumer, collaboration     |

---

## 4. Color System

Neutral-first palette (80-90% of interface), one vivid accent family, semantic status colors.

**Validated brand accents:**

| Name               | Light   | Dark    | Source    |
| ------------------ | ------- | ------- | --------- |
| Indigo voltage     | #635BFF | #8B7CFF | Stripe    |
| Coral warmth       | #CC785C | #E89B82 | Anthropic |
| Lavender-blue      | #5E6AD2 | #828FFF | Linear    |
| Action blue        | #0066CC | #2997FF | Apple     |
| Emerald functional | #3ECF8E | #22C55E | Supabase  |
| Electric green     | #00D992 | #00D992 | VoltAgent |
| Notion purple      | #5645D4 | #8B7CFF | Notion    |
| Spotify green      | #1ED760 | #1ED760 | Spotify   |

**Color contrast rules:**
- Text on white canvas: ink (#0d0d0d) = 19.6:1 (AAA). ink-secondary (#555555) = 7.3:1 (AAA). ink-muted (#888888) = 3.7:1 (AA large text).
- Text on dark canvas (#0a0a0a): ink-on-dark (#ffffff) = 19.4:1 (AAA). ink-on-dark-muted (#999999) = 8.6:1 (AAA).
- Interactive elements must maintain 3:1 minimum against adjacent colors.
- Never use ink-faint (#aaaaaa) for body text — reserved for disabled states and placeholder only.
- On dark surfaces, prefer ink-on-dark for primary text, body (#bdbdbd from VoltAgent palette) for secondary.

**Gradient tokens:**

| Token              | Direction | Stops                                                                                                 |
| ------------------ | --------- | ----------------------------------------------------------------------------------------------------- |
| `gradient-primary` | 135°      | `{colors.gradient-primary-start}` → `{colors.gradient-primary-mid}` → `{colors.gradient-primary-end}` |
| `gradient-cool`    | 135°      | `{colors.gradient-cool-start}` → `{colors.gradient-cool-end}`                                         |

**Rules:**
- Neutrals carry 80-90% of the interface.
- `accent` for selected, focus, inline links, key metrics.
- `primary` for primary CTAs only — not every highlight.
- Gradients only for hero, onboarding, empty states, AI moments.
- Status colors are never decorative.
- One saturated accent per component (exception: data viz).
- In dark mode, prioritize surface separation and text contrast over saturation.

---

## 5. Typography

**Families:** Inter (display+body), JetBrains Mono / SF Mono (code).

**OpenType:** Enable globally: `kern`, `liga`, `calt`, `ss01`, `tnum` (mandatory on monetary cells, percentages, timestamps, counts, numeric columns), `cv11`.

**Display Tracking Rule:**

| Size    | Tracking             |
| ------- | -------------------- |
| < 24px  | -0.005em to 0        |
| 24-44px | -0.020em to -0.045em |
| 44-72px | -0.045em to -0.055em |
| > 72px  | -0.055em to -0.060em |

**Eyebrow-Mono Pattern:** Small all-caps mono label with positive tracking above section headlines. Creates a "technical-layer" voice.

```
LATENCY · REGION US-EAST
Built for production traffic
```

Use `{typography.eyebrow-mono}`, color `{colors.ink-muted}` or `{colors.accent}`, under 6 words. Never inside running prose.

**Font substitutes:**

| If primary is       | Use instead                    | Adjustments                                 |
| ------------------- | ------------------------------ | ------------------------------------------- |
| SF Pro / Apple      | Inter, system-ui               | -0.01em tracking on display                 |
| Sohne (Stripe)      | Inter 300, ss01                | Negative tracking across all sizes          |
| Circular (Supabase) | Inter or Satoshi 500           | -1.92px at 64px                             |
| Geist (Vercel)      | Inter or Satoshi 600           | Approximates weight for weight              |
| Linear custom       | SF Pro Display / Inter 500-700 | Aggressive negative tracking (-3px at 80px) |

---

## 6. Layout & Grid

**Spacing:** Base 4px (structural snaps to 8px). Key relationships:

| Relationship             | Target   |
| ------------------------ | -------- |
| Label to field           | 6-8px    |
| Field to helper/error    | 6-8px    |
| Icon to label            | 8px      |
| Button group gap         | 8-12px   |
| Form field group         | 16-24px  |
| Card internal padding    | 20-28px  |
| Section internal padding | 48-80px  |
| Major section gap        | 80-128px |

**Grid:** 4/8/12 columns. Gutters 16-32px. Margins 20-80px.

| Class    | Width       | Cols | Gutter | Margin |
| -------- | ----------- | ---- | ------ | ------ |
| Compact  | < 640px     | 4    | 16px   | 20px   |
| Medium   | 640-1023px  | 8    | 24px   | 32px   |
| Expanded | 1024-1439px | 12   | 28px   | 48px   |
| Wide     | 1440+px     | 12   | 32px   | 80px   |

**Containers:** sm 720px (forms), md 960px (docs), lg 1180px (marketing), xl 1320px (dashboards), full 100%.

**Philosophy:** "Make generous space, then fill it with intent." 80-128px between marketing sections. 12-24px inside app panels. Strong left-edge alignment unless marketing hero. On compact screens stack intentionally; primary action stays visible.

---

## 7. Elevation & Depth

| Level      | Token     | Treatment             | Use                     |
| ---------- | --------- | --------------------- | ----------------------- |
| 0 — Flat   | `level-0` | None + 1px hairline   | Default cards, sections |
| 1 — Subtle | `level-1` | 1-2px offset          | Inline cards            |
| 2 — Light  | `level-2` | Stacked small offsets | Feature cards           |
| 3 — Medium | `level-3` | 4-12px blur           | Pricing cards           |
| 4 — High   | `level-4` | 8-24px blur           | Dropdowns, panels       |
| 5 — Modal  | `level-5` | 16-48px blur          | Modals, dialogs         |
| Product    | `product` | 8-30px blur           | Product imagery         |

**Philosophy:** Flat surfaces use borders. Raised surfaces use border + shadow. Stacked shadows (multiple small offsets) over single heavy blurs. Modals dim with soft overlay. Glows are rare and tied to brand or AI moments only. Avoid neumorphism, heavy glassmorphism, harsh shadows.

**VoltAgent elevation:** Hairline (1px solid `{colors.hairline-on-dark}` on `{colors.dark-canvas}`) is the default for every card and button — no shadow. Inset Glow (0 0 15px rgba(92,88,85,0.2), `voltagent-glow`) for hover or featured cards. Modal Stack (0 20px 60px rgba(0,0,0,0.7) + inset ring, `voltagent-modal`) for dialogs. No drop shadows on cards — the brand uses hairlines as its only elevation system.

---

## 8. Shapes & Border Radius

| Token            | Value  | Use                          |
| ---------------- | ------ | ---------------------------- |
| `{rounded.none}` | 0px    | Full-bleed sections, luxury  |
| `{rounded.xs}`   | 4px    | Inline code, small tags      |
| `{rounded.sm}`   | 6px    | Compact buttons, inputs      |
| `{rounded.md}`   | 8px    | Standard buttons — default   |
| `{rounded.lg}`   | 12px   | Cards, pricing tiers         |
| `{rounded.xl}`   | 16px   | Dialog containers            |
| `{rounded.pill}` | 9999px | Pill buttons, badges, search |
| `{rounded.full}` | 50%    | Avatars, circular controls   |

**Dual-pill scale:** Marketing = `pill` (confident, conversion). In-app = `md`/`sm` (quiet, dense). Never mix on same page.

**Hard-corner luxury:** For luxury/automotive/editorial-fashion: `{rounded.none}` on hero buttons and feature cards. Pair with strong typography contrast (uppercase labels, tight tracking). Inputs stay at `{rounded.sm}` for usability.

**VoltAgent radius usage:** Buttons = `sm` (6px). Cards = `md` (8px). Code blocks = `md` (8px). Inline chips = `sm` (6px). Status tags = `pill` (9999px). Never use pill radius on primary buttons — VoltAgent's brand is defined by tight 6px rectangles, not pill shapes.

---

## 9. Motion & Interaction

| Token  | Duration | Use                             |
| ------ | -------- | ------------------------------- |
| `fast` | 100ms    | Button press, small hover       |
| `base` | 160ms    | Default hover, focus, selection |
| `slow` | 240ms    | Panels, dropdowns, sheets       |
| `page` | 360ms    | Page/hero transitions           |

**Easing:** `standard` (cubic-bezier(0.2,0,0,1)) default. `out` (0,0,0.2,1) for entrances/sheets. `in-out` (0.4,0,0.2,1) for mode/page transitions.

**Press interaction:** `scale(0.96)` + `opacity 0.9` on press. Apply to every interactive surface. Never combine with translate — the press compresses in place. Reduced-motion: skip transform, keep opacity.

**Rules:** Hover/press movement ≤ 2-4px. Prefer opacity/transform over layout animation. Respect reduced-motion. Animate only when it clarifies hierarchy. Never rely on motion as the only state-change explanation.

**Transition defaults:** Interactive elements use `transition: all {motion.fast} {motion.easing_standard}` for hover/press. Panels and sheets use `{motion.slow}` with `easing_out`. Page transitions use `{motion.page}` with `easing_in_out`. Never animate width/height/position on interactive elements — use opacity and transform only.

**Reduced motion:** `@media (prefers-reduced-motion: reduce)` disables all transforms and opacity transitions. Fall back to instant state changes. Never rely on motion for critical feedback.

---

## 10. Component System

Full specs in YAML frontmatter. Key rules and behaviors below.

**State pattern:** Default, hover, press, active, focus, disabled, loading. Each interactive component must implement all. Accessible name required. Touch target ≥ 44×44px.

| Variant          | Fill          | Text          | Border                 | Height | Radius |
| ---------------- | ------------- | ------------- | ---------------------- | ------ | ------ |
| Primary          | `primary`     | `on-primary`  | —                      | 40     | md     |
| Secondary        | transparent   | `ink`         | 1px `hairline-strong`  | 40     | md     |
| Ghost            | transparent   | `ink`         | —                      | 36     | md     |
| Destructive      | `error`       | white         | —                      | 40     | md     |
| Pill (marketing) | `primary`     | `on-primary`  | —                      | 40     | pill   |
| Icon             | `canvas`      | `ink`         | 1px `hairline`         | 44     | full   |
| Outline-on-dark  | `dark-canvas` | `ink-on-dark` | 1px `hairline-on-dark` | 44     | sm     |
| Ghost-green      | transparent   | `primary`     | —                      | 40     | sm     |
| Pill-tag         | transparent   | `ink`         | 1px `hairline`         | 28     | pill   |

**Buttons:** Copy uses specific verbs (Create, Invite, Save) — never Submit/OK/Click here. VoltAgent-specific variants: `button-outline-on-dark` (hairline on dark canvas), `button-ghost-green` (green accent ghost), `button-pill-tag` (inline pill with body-sm). Copy: specific verbs (Create, Invite, Save) — never Submit/OK/Click here.

| Surface          | Background             | Border                           | Radius | Padding |
| ---------------- | ---------------------- | -------------------------------- | ------ | ------- |
| Default          | `canvas`               | 1px `hairline`                   | lg     | 24      |
| Feature          | `canvas`               | 1px `hairline`                   | lg     | 32      |
| Interactive      | `canvas`               | 1px → `hairline-strong` on hover | lg     | 20      |
| Raised           | `canvas`               | —                                | lg     | 24      |
| Soft             | `canvas-soft`          | —                                | lg     | 24      |
| Dark             | `surface-inverse-soft` | —                                | lg     | 24      |
| Pricing-featured | `surface-inverse`      | 2px `primary`                    | lg     | 32      |
| Emphasized       | `canvas`               | 3px `hairline`                   | md     | 24      |

**Cards:** On dark canvas, use hairline-only elevation (no shadow).

**Inputs:** 44px height (40px desktop-only). Focus = 2px primary border. Error = error border + specific copy. Labels above field, always visible. Helper/error below field. Search uses pill radius `{rounded.pill}`. Textarea min-height 112px.

**Navigation:** Top nav 64px (56px compact). `canvas` or `surface-inverse` background. Bottom border. Logo left, actions right. Sidebar 240-280px. Active item: accent-subtle + accent text. Collapse to rail or drawer on smaller screens.

**Badges:** Height 24, radius full, soft background + matching text. 1-3 words. Never as buttons unless interaction is visually clear.

**Code mockup:** Embed real UI/code directly in hero. Window dots, breadcrumb optional. Highlight one line with accent-soft. Always include copy action. Code mockups use code-mockup component with SF Mono or JetBrains Mono at 13px/400.

**Inline alerts:** Five variants (neutral, info, success, warning, error). Each uses soft background + matching text color. Neutral for general info, info for helpful notes, success for positive confirmations, warning for risks, error for problems. Never nest inline alerts inside other cards.

**AI Process Timeline:** Each chip uses one `{process_states}` tint. Show duration for completed, subtle pulse on running. Collapse past 6 entries. Never fabricate intermediate "thinking" — show only verifiable transitions.

**Dialogs:** Surface `canvas`, radius xl, max width 560px, padding 24px, shadow level 5. Overlay dims background. Title first, one clear primary action, secondary is cancel/close. Destructive requires consequence copy.

**Data tables:** `table-header` uses `{colors.canvas-soft}` background with `{typography.body-sm}` (muted). `table-row` uses `{colors.canvas}` with bottom border. Row height 48-56px. Numerics right-aligned, text left-aligned. Hover/selection produces subtle surface change. Sticky bulk actions bar. Empty, loading, and error states required.

**Empty state:** Structure: small icon/visual → headline → one-sentence explanation → primary action → optional secondary link. Helpful, never apologetic. Answer: what's missing, why it matters, what to do next.

**Skeleton loading:** Use `skeleton` component with pulse animation for content areas during data fetch. Match skeleton shape to final content shape (rectangle for text, circle for avatars, rectangle for images). Never show skeleton for more than 3 seconds — prefer a simplified static state after timeout.

**Breadcrumbs:** Current page → Parent section → Grandparent. Use `{colors.ink-muted}` for inactive links, `{colors.ink}` for active/current. Truncate at 4 levels with ellipsis. Last item (current page) is non-clickable text.

**Keyboard navigation:** All interactive elements must be reachable and operable via keyboard. Focus order follows visual order (left-to-right, top-to-bottom). Focus indicators use 2px `{colors.primary}` ring with 2px offset. Never use `outline: none` without providing an alternative focus style. Tab stops on interactive elements only (not static text). Enter/Space activates buttons and links. Escape closes modals, dropdowns, and menus. Arrow keys navigate within radio groups, tab lists, and menus.

**Component state matrix:** Every interactive element must handle these states:

| State          | Button                  | Input            | Card                | Link        |
| -------------- | ----------------------- | ---------------- | ------------------- | ----------- |
| Default        | primary fill            | border + bg      | border + shadow     | accent text |
| Hover          | primary-hover bg        | —                | hover-border        | underline   |
| Focus          | ring 2px primary        | ring 2px primary | —                   | ring        |
| Active/Pressed | scale(0.96)             | —                | —                   | color shift |
| Disabled       | hairline bg, faint text | faded bg         | n/a                 | muted text  |
| Loading        | spinner overlay         | —                | skeleton            | —           |
| Empty          | n/a                     | n/a              | illustration + text | n/a         |
| Error          | n/a                     | error border     | n/a                 | n/a         |
| Success        | n/a                     | n/a              | checkmark           | n/a         |

Apply to all components in the YAML frontmatter.

**Statistics:** `stat-number` in `{typography.numeric}` (48px/700/-1.5px), always in `{colors.primary}`. `stat-label` in `{typography.body-sm}`, `{colors.ink-secondary}`. Tabular numerals required.

---

## 11. Page Blueprints

Each blueprint lists structure and rules. Follow order; adapt spacing per brand mode.

### 11.1 SaaS Landing
**Structure (12 parts):** Nav → announcement pill → hero (headline + sub + primary CTA + secondary CTA + product visual) → social proof → feature grid → workflow → use cases → testimonials → pricing preview → footer.
**Rules:** Hero supporting copy max 720px. One gradient maximum. Real product visual (screenshot, code mockup, or dashboard). Feature cards 2-3 columns expanded, 1-up compact. Section backgrounds alternate (light → soft → dark → light). Primary CTA is `{colors.primary}` filled; secondary is `button-secondary`. Hero band uses hero-band-light or hero-band-dark.

### 11.2 AI Chat
**Structure (6 parts):** App shell → conversation nav → message list → composer → tool/status area → optional context panel.
**Rules:** User messages compact (card-base with sm padding), assistant messages spacious with rich content (card-feature). Composer always in focus. Render AI process timeline for multi-stage operations using `{process_states}` chips. Long conversations stay navigable with collapse. Compact view never hides input.

### 11.3 Admin Dashboard
**Structure (8 parts):** App nav → top bar → page heading → metric cards → filter row → main table/chart → detail drawer → pagination + bulk actions.
**Rules:** Prioritize scanning. Consistent row heights. Tabular numerals on metrics (use `{typography.numeric}`). Actions live near affected data. Bulk actions appear only on selection. Filters obvious and reversible. Metric cards use stat-number + stat-label composition.

### 11.4 Pricing
**Structure (7 parts):** Headline → value statement → billing toggle → pricing cards (one featured with polarity flip) → comparison table → FAQ → final CTA.
**Rules:** One featured plan uses `card-pricing-featured` (polarity flip). One CTA per plan. Clear price hierarchy with `{typography.numeric}` for prices. Short feature bullets. Enterprise plan: specific, not vague. FAQ uses inline-alert-neutral for common questions.

### 11.5 Settings
**Structure (5 parts):** Settings nav → grouped sections → forms with helpers → save/cancel → destructive zone (separated by spacing).
**Rules:** Show current/saved state. Disable save until changes exist. Confirm destructive actions with explicit consequence copy. Destructive zone separated from other sections by spacing and optional divider-strong. Forms use text-input + inline-alert-error/neutral composition.

### 11.6 Documentation
**Structure (7 parts):** Docs shell → left nav → article (max 760px) → TOC → code blocks with copy → callouts sparingly → previous/next.
**Rules:** Quieter than marketing pages. Runnable or realistic examples in code-block components. Descriptive headings. Callouts use inline-alert-info/neutral. Code blocks include copy action. Previous/next links at article bottom.

### 11.7 Auth
**Structure (7 parts):** Product mark → headline → provider actions → divider → email form → error/helper text → legal/support links.
**Rules:** Quiet page. No marketing content. Specific exact errors. Provider buttons visually consistent (use button-outline-on-dark for dark mode, button-secondary for light mode). Reassuring secure copy in the legal/support links area. Forms use text-input + inline-alert-error.

---

## 12. Content & Voice

**Voice:** Clear, calm, direct, helpful, slightly warm, never gimmicky.

**Rules:** Verbs for actions. Specific labels over generic. Plain-language errors. Avoid exclamation marks except rare celebration. Realistic product copy in generated UI.

**Error formula:** What happened → why (if known) → what to do next. Never "Something went wrong."

| Context          | Good copy                                                 |
| ---------------- | --------------------------------------------------------- |
| Empty project    | Create your first project to start organizing work.       |
| Loading          | Preparing your workspace…                                 |
| Save success     | Changes saved.                                            |
| Permission error | You do not have permission to edit this workspace.        |
| Delete confirm   | This action permanently removes the project and its data. |
| Invite helper    | They will receive an invitation with access instructions. |

---

## 13. Do's and Don'ts

**Do:**
- For VoltAgent brand: use `#101010` canvas, `#00D992` primary, `#3d3a39` hairline, weight-400 display at 60px.
- Reserve `{colors.primary}` for CTAs and brand mark only. Scarcity = power.
- Use the surface ladder for hierarchy before reaching for shadows.
- Set display type in 600-700 weight with aggressive negative tracking.
- Lead every section with a product UI screenshot or code block.
- Alternate section backgrounds (light → soft → dark → light).
- Keep one radius grammar per component type.
- Use stacked shadows over single heavy blurs.
- Default body to `{typography.body-md}` (16px/400/1.5).
- Apply `scale(0.96)` as press micro-interaction on every button.
- Enable OpenType features globally (`kern`, `liga`, `calt`, `ss01`, `tnum`).
- Use `tnum` on every monetary cell, percentage, timestamp, count.

**Don't:**
- For VoltAgent brand: don't introduce a light-mode counterpart. Don't use pill-radius buttons (status tags are the only pill elements). Don't use drop shadows on cards. Don't render hero headline above weight 400.
- Don't introduce a second accent color. Most top brands have exactly one.
- Don't use brand accent for body text or large background fills.
- Don't ship light-mode-only if brand is dark-mode native (and vice versa).
- Don't add atmospheric gradients if brand doesn't have one — surface contrast is sufficient.
- Don't mix pill and non-pill buttons on the same page.
- Don't set body paragraphs in the mono face. Mono is for code.
- Don't use weight 500 for headlines (400 body / 600-700 display).
- Don't add pure black `#000000` as canvas (except video overlays and global nav).
- Don't invent hover states — document default and pressed only.
- Don't sacrifice accessibility for aesthetics, clarity for decoration, or consistency for novelty.
- Don't add a framework dependency just because a token or pattern was mentioned here.

---

## 14. Responsive Behavior

**Breakpoints:** Mobile ≤480 (4 cols), Tablet 481-768 (8 cols), Desktop 769-1024 (12 cols), Wide 1025-1280, Ultra >1280.

**Touch targets:** Buttons 44×44px (WCAG 2.2 AA). Icon buttons 44px circle. Inputs 44px height. Nav links 32px hit area (padding-based on mobile).

**Collapsing strategy:**

| Element      | Desktop → Tablet → Mobile                  |
| ------------ | ------------------------------------------ |
| -------      | -------------------------                  |
| Top nav      | Full → secondary hidden → hamburger + logo |
| Card grids   | 3-up → 2-up → 1-up                         |
| Pricing      | 4-up → 2-up → 1-up (vertical stack)        |
| Hero split   | Side-by-side → stacked                     |
| Footer       | 6-col → 3-col → accordion                  |
| Display type | 72px → 56px → 40px → 32px                  |

**Images:** Product screenshots maintain aspect ratio; stack below text on mobile. Hero photography may switch art-direction crop at mobile. Customer logos at consistent 24-32px height; row wraps on compact. Customer logos at consistent 24-32px height; row wraps. Code blocks use horizontal scroll on mobile; fixed font-size.

---

## 15. Universal Premium Patterns

The seven patterns that separate premium product UI from generic templates. Missing any = reads generic.

- [ ] Aggressive negative tracking on display sizes (4-5% of font size at hero)
- [ ] One brand voltage color, used scarcely — primary CTA, brand mark, focus ring
- [ ] Surface ladder for hierarchy — dim surfaces for elevation before shadows
- [ ] Real product UI screenshots — composited dashboards beat marketing illustrations
- [ ] Body at 16-18px, not 14px — generous reading sizes signal editorial confidence
- [ ] OpenType features enabled globally — kern, liga, calt, tnum, ss01
- [ ] Polarity-flipped featured tier — dark-fill recommended pricing card on a light page

---

## 16. Anti-Patterns

**Visual:** Random purple-gradient startup UI, excessive glassmorphism, heavy shadows on every card, low-contrast gray text, giant icons in dense dashboards, decorative blobs everywhere, multiple unrelated accents, mixed-radius controls, cards-inside-cards, centered long-form text, 3+ CTAs in hero, equally-emphasized pricing plans, light-mode-only UI, font-stacking without fallbacks, pure black `#000000` as canvas.

**Content:** Lorem ipsum, generic hype, Submit/Click here/Error occurred, "Something went wrong" without recovery, fake testimonials, vague empty states ("No data"), placeholder metrics that look real without context.

**Layout:** Primary and destructive adjacent without separation, primary CTA below fold, inconsistent section padding, mixed alignment systems, compact = shrunken expanded, tables overflowing on compact without controls.

**Interaction:** Removed focus outlines, hover-only essential controls, layout-jumping animations, instant destructive actions, disabled buttons without explanation.

**Stack:** Adding a framework because a component was mentioned, adding a UI kit because a pattern resembles one, adding an icon library to match icon style.

---

## 17. Quality Bar

**Universal checklist:**
- [ ] Clear page title and primary action
- [ ] Responsive/adaptive layout
- [ ] Loading, empty, error states
- [ ] Accessible focus states
- [ ] Realistic content (no lorem ipsum)
- [ ] No token drift — all values reference YAML
- [ ] Dark mode designed (when supported)
- [ ] No stack dependency introduced

**Component checklist:** Every interactive component must have: default, hover/press, active, focus, disabled, loading states. Accessible name. Touch target met on compact/touch screens.

**Review rubric (1-5, min ship ≥ 3):**

| Category           | 1               | 3               | 5                |
| ------------------ | --------------- | --------------- | ---------------- |
| Visual hierarchy   | Confusing       | Mostly clear    | Instantly clear  |
| Token consistency  | Random          | Minor drift     | Fully consistent |
| Accessibility      | Poor            | Basic           | Strong           |
| Responsiveness     | Broken          | Works           | Thoughtful       |
| Copy quality       | Generic         | Acceptable      | Specific, useful |
| Component states   | Missing         | Partial         | Complete         |
| Product fit        | Template-like   | Somewhat        | Purpose-built    |
| Polish             | Rough           | Decent          | Premium          |
| Stack independence | Introduces deps | Mostly portable | Fully agnostic   |

---

## 18. Brand Personality Recipes

Four cohesive token clusters synthesized from production design systems. Pick exactly one.

### 18.1 Warm Editorial (Anthropic, Cursor, Notion)

For literary, considered, humanist tone. The typography is generous, the radius is soft, and the single accent color arrives like a meaningful event rather than a brand splash.

- Canvas: #FAF9F5 (cream). Accent: #CC785C (coral) or #5E6AD2 (lavender).
- Card radius: lg (12px). Display weight: 400-500. Tracking: -0.045em to -0.055em.
- Hero rhythm: cream → cream-card → dark-mockup → coral-callout.
- Body: 17-18px for generous reading. Warm surfaces, friendlier copy.
- Type: Inter or system serif for body. Display: weight 400-500 with loose tracking.
- Motion: slower easings (base=200ms) for a more deliberate feel.
- Key traits: Chips instead of badges. Inline code uses code-inline-chip. Authentication flows use ex-auth-form-card.

### 18.2 Near-Black Craft Tool (Linear, Raycast, VoltAgent, Spotify)

For developer/creator/AI tools that want quiet density.

- Canvas: #101010 (VoltAgent verified) to #0A0A0B (Linear).
- Surface ladder: #141414 / #1A1A1A / #242424.
- Accent: #00D992 (electric green, VoltAgent) or #5E6AD2 (lavender-blue, Linear).
- Drop shadow: none — use surface ladder + hairlines.
- Display weight: 400 at hero (60px), 400 at section (36px), 700 at card title (24px).
- Eyebrow-mono: 14px, weight 600, tracking 2.52px, Inter, uppercase.
- Body: 16px Inter at line-height 1.65. Ink: #f2f2f2, ink-strong: #ffffff, body: #bdbdbd, mute: #8b949e.
- Hairline: #3d3a39 on dark canvas.
- Mono: SF Mono (Apple systems) or JetBrains Mono / Geist Mono (free substitute).
- Button radius: sm (6px) — never pill except for inline status tags.
- VoltAgent-specific components: button-outline-on-dark, button-ghost-green, button-pill-tag, card-feature-emphasized, code-inline-chip, green-divider-band, dividers (dashed).
- Elevation: `voltagent-hairline` for default cards, `voltagent-glow` for hover/featured, `voltagent-modal` for dialogs.
- Component preference: card-feature-emphasized over card-elevated, button-outline-on-dark over button-secondary on dark bands, code-inline-chip for any inline command reference.
- Page patterns: hero-band-dark + code-mockup for hero, section-band-dark + card-feature-emphasized for feature grids, green-divider-band between major sections.

### 18.3 Stark Editorial Density (Vercel, Stripe, Figma, Apple)

For platforms that want engineered calm with one chromatic event. The page is almost entirely white — the one color event is intentionally isolated.

- Canvas: #FAFAFA to #FFFFFF (binary). Accent: #635BFF (Stripe) or #0066CC (Apple).
- Single chromatic event: mesh gradient hero, color block, polarity-flipped pricing tier, or CTA band.
- Body: 17-18px (instead of 16). Display weight: 300-500 (never 700).
- Marketing CTA: pill. In-app: sm (6px). Structure over decoration.
- Shadows preferred over hairlines for card elevation (use card-elevated, not card-feature).
- Key traits: card-pricing-featured for recommended tier, search-input for nav search, badge-success for live status indicators.

### 18.4 Photography-First (Apple, Nike, Ferrari, Airbnb)

For products where the artifact is the protagonist. The product imagery does the storytelling — the UI steps back.

- Canvas: #F5F5F7 (parchment) or #181818 (cinema dark). Accent: single voltage (e.g., #DA291C Ferrari red, #FF385C Airbnb rausch).
- Hero: edge-to-edge photography or product render, full-bleed. No card chrome on hero images.
- Card radius: lg for warmth, or none for luxury (Ferrari uses 0px radius).
- Display: uppercase 96px line-height 0.9-1.0, or delicate weight 300.
- Drop shadow: reserved for product imagery only — UI elements remain flat.
- Key traits: hero-band-light alternating with hero-band-dark for gallery rhythm, card-product-mockup for product shots, minimal navigation.

---

## 19. Agent Rules

**Source of truth:** Don't invent colors, shadows, radii, spacing, or type scales unless requested. Use tokens here as default language. Derive new variants from existing tokens. Use the host project's existing stack and conventions.

**Workflow:**
1. Read DESIGN.md YAML → extract tokens.
2. Identify page or component type.
3. Inspect the existing project stack.
4. Select the closest blueprint or component rule.
5. Map tokens into the project's existing primitives.
6. Generate all important states.
7. Check compact, medium, expanded layouts.
8. Use realistic copy (no lorem ipsum).
9. Verify against rubric (§17).

**Priority order:**
1. User's explicit request
2. Product/page purpose
3. Accessibility and usability
4. DESIGN.md tokens and rules
5. Existing project stack and conventions
6. Platform conventions
7. Visual polish

**Implementation rule:** "I will implement this using the project's existing stack and map DESIGN.md tokens into local theme, style, component, or resource primitives." Never say a specific framework, styling library, UI kit, or icon package unless the user or project files explicitly require that stack.

---

## 20. Known Gaps

- Dark mode tokens not documented for every component. Add `-on-dark` variants where `{colors.primary}` < 4.5:1 on `{surface-inverse}`.
- Form validation states partially documented — extend for your framework.
- Font loading strategy not specified (`@font-face` or `next/font`). Use `font-display: swap` for Inter and JetBrains Mono.
- Minimum contrast ratios noted but not enforced in tokens. Validate with @axe-core against WCAG 2.2 AA.
- Data visualization chart colors not included. Add a `charts:` section with series colors, bar fills, and pie segment tokens if needed.
- Print styles and RTL not covered. Add `@media print` overrides separately if needed.
- **This file is a template.** Every value is an example. Replace with your brand's actual tokens before use.
