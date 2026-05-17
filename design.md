# DESIGN_PRO.md

A complete design system for building polished, modern, AI-ready product interfaces.

This design combines the strongest patterns from premium SaaS, developer tools, productivity apps, and AI platforms: Vercel-like precision, Linear-like restraint, Stripe-like gradient polish, Apple-like whitespace, Notion-like warmth, Supabase-like developer clarity, and Figma-like collaborative friendliness.

Use this file as the source of truth for UI generation, frontend implementation, design critique, and visual consistency.

---

## 1. Visual Theme & Atmosphere

### Core Direction

The interface should feel:

- **Premium but approachable**
- **Minimal but not empty**
- **Technical but humane**
- **Calm, fast, and trustworthy**
- **Sharp in structure, soft in details**

The product should look like a modern AI-native SaaS or developer platform: precise typography, quiet surfaces, strong hierarchy, tasteful gradients, subtle motion, and very clear actions.

### Design Personality

| Trait | Direction |
|---|---|
| Primary mood | Calm confidence |
| Visual density | Medium-low, with strong rhythm |
| Surface style | Clean cards, soft depth, crisp borders |
| Brand feel | Intelligent, modern, useful |
| Interaction feel | Fast, responsive, intentional |
| Best suited for | SaaS apps, dashboards, AI tools, productivity products, landing pages, dev tools |

### Design Philosophy

1. **Clarity first.** Every screen should make the next action obvious.
2. **One primary action per area.** Avoid competing CTAs.
3. **Whitespace is structure.** Spacing should guide attention, not merely separate items.
4. **Surfaces should layer gently.** Use borders and soft shadows before heavy fills.
5. **Color should signal meaning.** Accent colors should be rare and purposeful.
6. **Motion should explain.** Animate state changes, not decoration.
7. **The UI should feel built, not themed.** Components must share proportions, radius, type scale, and behavior.

---

## 2. Color Palette & Roles

The system uses a neutral-first palette with one vivid primary accent, one secondary gradient family, and semantic status colors.

### Light Theme

| Token | Hex | Role |
|---|---:|---|
| `background` | `#FAFAF8` | Main page background, warm off-white |
| `surface` | `#FFFFFF` | Cards, panels, sheets |
| `surface-muted` | `#F4F4F1` | Secondary cards, inactive regions |
| `surface-raised` | `#FFFFFF` | Floating menus, modals |
| `border` | `#E6E4DE` | Default borders |
| `border-strong` | `#D4D0C7` | Focused or emphasized borders |
| `text-primary` | `#111111` | Main text |
| `text-secondary` | `#55524C` | Body copy, descriptions |
| `text-muted` | `#8A867C` | Hints, timestamps, placeholders |
| `text-inverse` | `#FFFFFF` | Text on dark surfaces |
| `primary` | `#111111` | Primary CTA, core brand anchor |
| `primary-hover` | `#2A2A2A` | Primary CTA hover |
| `accent` | `#635BFF` | Links, focus rings, selected states |
| `accent-soft` | `#EFEEFF` | Accent background |
| `accent-strong` | `#4F46E5` | High-emphasis accent |
| `success` | `#16A34A` | Positive state |
| `success-soft` | `#DCFCE7` | Positive background |
| `warning` | `#F59E0B` | Warning state |
| `warning-soft` | `#FEF3C7` | Warning background |
| `danger` | `#DC2626` | Error/destructive state |
| `danger-soft` | `#FEE2E2` | Error background |
| `info` | `#0284C7` | Informational state |
| `info-soft` | `#E0F2FE` | Informational background |

### Dark Theme

| Token | Hex | Role |
|---|---:|---|
| `background` | `#08090A` | Main page background |
| `surface` | `#111214` | Cards, panels |
| `surface-muted` | `#181A1D` | Secondary cards |
| `surface-raised` | `#1D1F23` | Modals, popovers |
| `border` | `#2A2D33` | Default borders |
| `border-strong` | `#3A3F47` | Emphasized borders |
| `text-primary` | `#F7F7F5` | Main text |
| `text-secondary` | `#B7B8BC` | Body copy |
| `text-muted` | `#7D828A` | Hints, placeholders |
| `text-inverse` | `#111111` | Text on light surfaces |
| `primary` | `#FFFFFF` | Primary CTA on dark |
| `primary-hover` | `#EDEDED` | Primary hover |
| `accent` | `#8B7CFF` | Links, focus rings, selected states |
| `accent-soft` | `#1D1A3D` | Accent background |
| `accent-strong` | `#A799FF` | High-emphasis accent |
| `success` | `#22C55E` | Positive state |
| `success-soft` | `#0F2E1A` | Positive background |
| `warning` | `#FBBF24` | Warning state |
| `warning-soft` | `#3A2A0A` | Warning background |
| `danger` | `#F87171` | Error/destructive state |
| `danger-soft` | `#3A1212` | Error background |
| `info` | `#38BDF8` | Informational state |
| `info-soft` | `#082F49` | Informational background |

### Gradient Tokens

Use gradients sparingly for hero moments, feature highlights, and active states.

| Token | Value | Usage |
|---|---|---|
| `gradient-primary` | `linear-gradient(135deg, #635BFF 0%, #8B5CF6 45%, #06B6D4 100%)` | Hero glow, premium CTA background |
| `gradient-warm` | `linear-gradient(135deg, #FF7A59 0%, #F59E0B 50%, #FDE68A 100%)` | Warm highlights, announcements |
| `gradient-cool` | `linear-gradient(135deg, #06B6D4 0%, #635BFF 55%, #111827 100%)` | AI/productivity visuals |
| `gradient-subtle-light` | `radial-gradient(circle at 20% 10%, rgba(99,91,255,.14), transparent 34%), radial-gradient(circle at 80% 0%, rgba(6,182,212,.12), transparent 30%)` | Light page background accent |
| `gradient-subtle-dark` | `radial-gradient(circle at 20% 10%, rgba(139,124,255,.22), transparent 34%), radial-gradient(circle at 80% 0%, rgba(6,182,212,.16), transparent 30%)` | Dark page background accent |

### Color Rules

- Use neutral colors for 80–90% of the interface.
- Use `accent` for selected states, focus, inline links, and key metrics.
- Use gradients only for hero, onboarding, empty states, and signature moments.
- Avoid using multiple saturated colors in the same component unless it is a data visualization.
- Status colors should never be used as decorative accents.

---

## 3. Typography Rules

### Font Stack

Use a modern sans-serif system stack by default.

```css
--font-sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
--font-mono: "JetBrains Mono", "SF Mono", Consolas, "Liberation Mono", monospace;
--font-display: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
```

### Typography Style

- Headings should be tight, confident, and slightly compressed in rhythm.
- Body text should be readable and relaxed.
- Labels and metadata should be compact, often medium-weight.
- Use monospace for code, IDs, keyboard shortcuts, technical metadata, command snippets, and logs.

### Type Scale

| Token | Size | Line Height | Weight | Usage |
|---|---:|---:|---:|---|
| `display-xl` | `72px` | `1.00` | `700` | Large landing page hero |
| `display-lg` | `56px` | `1.04` | `700` | Standard hero |
| `display-md` | `44px` | `1.08` | `650` | Page headline |
| `heading-xl` | `36px` | `1.12` | `650` | Section headline |
| `heading-lg` | `28px` | `1.18` | `650` | Major panel title |
| `heading-md` | `22px` | `1.25` | `600` | Card title |
| `heading-sm` | `18px` | `1.35` | `600` | Small section title |
| `body-lg` | `18px` | `1.65` | `400` | Hero supporting copy |
| `body-md` | `16px` | `1.6` | `400` | Default body |
| `body-sm` | `14px` | `1.55` | `400` | Secondary copy |
| `label-md` | `13px` | `1.25` | `600` | Buttons, tabs |
| `label-sm` | `12px` | `1.2` | `600` | Eyebrows, badges |
| `caption` | `11px` | `1.2` | `500` | Fine metadata |

### Letter Spacing

| Element | Letter Spacing |
|---|---:|
| Display headings | `-0.055em` |
| Section headings | `-0.035em` |
| Body | `-0.01em` |
| Labels | `-0.005em` |
| Eyebrows | `0.08em`, uppercase |

### Typography Rules

- Keep hero headlines under 12 words.
- Use sentence case for most UI text.
- Use uppercase only for short labels, badges, or technical metadata.
- Avoid thin font weights below `400`.
- Do not center-align long paragraphs.
- Use maximum text widths:
  - Hero copy: `720px`
  - Article text: `760px`
  - Form descriptions: `540px`
  - Card copy: `420px`

---

## 4. Layout Principles

### Grid

Use a 12-column responsive grid.

| Breakpoint | Width | Columns | Gutter | Margin |
|---|---:|---:|---:|---:|
| Mobile | `< 640px` | 4 | `16px` | `20px` |
| Tablet | `640–1023px` | 8 | `24px` | `32px` |
| Desktop | `1024–1439px` | 12 | `28px` | `48px` |
| Wide | `1440px+` | 12 | `32px` | `80px` |

### Container Widths

| Token | Width | Usage |
|---|---:|---|
| `container-sm` | `720px` | Forms, auth, narrow content |
| `container-md` | `960px` | Docs, settings, simple pages |
| `container-lg` | `1180px` | Marketing sections |
| `container-xl` | `1320px` | Dashboards, data-heavy layouts |
| `container-full` | `100%` | App shell |

### Spacing Scale

Use an 8px base scale with occasional 4px micro spacing.

| Token | Value |
|---|---:|
| `space-0` | `0` |
| `space-1` | `4px` |
| `space-2` | `8px` |
| `space-3` | `12px` |
| `space-4` | `16px` |
| `space-5` | `20px` |
| `space-6` | `24px` |
| `space-8` | `32px` |
| `space-10` | `40px` |
| `space-12` | `48px` |
| `space-16` | `64px` |
| `space-20` | `80px` |
| `space-24` | `96px` |
| `space-32` | `128px` |

### Layout Rules

- Use generous vertical spacing between major sections: `80–128px`.
- Use compact spacing inside functional app panels: `12–24px`.
- Align content to a strong left edge unless the layout is a marketing hero.
- Favor asymmetric layouts for landing pages.
- Favor strict alignment for dashboards and settings.
- Use cards to group decisions, not to decorate every block.
- Keep primary content visually dominant and secondary controls quiet.

---

## 5. Radius, Borders & Shape Language

### Radius Scale

| Token | Value | Usage |
|---|---:|---|
| `radius-xs` | `4px` | Small tags, code pills |
| `radius-sm` | `6px` | Inputs, compact buttons |
| `radius-md` | `10px` | Default controls |
| `radius-lg` | `14px` | Cards |
| `radius-xl` | `20px` | Feature panels |
| `radius-2xl` | `28px` | Hero media, large containers |
| `radius-full` | `999px` | Pills, avatars |

### Border Rules

- Default border width: `1px`.
- Use borders instead of heavy shadows for structure.
- In dark mode, borders should be visible but low-contrast.
- Interactive components should strengthen border color on hover/focus.
- Avoid fully borderless cards unless the background contrast is obvious.

---

## 6. Depth & Elevation

Depth should be subtle. The design should feel premium and restrained, not floating everywhere.

### Shadows

| Token | Value | Usage |
|---|---|---|
| `shadow-xs` | `0 1px 2px rgba(0,0,0,.05)` | Buttons, small controls |
| `shadow-sm` | `0 4px 12px rgba(0,0,0,.06)` | Cards |
| `shadow-md` | `0 12px 32px rgba(0,0,0,.10)` | Popovers, menus |
| `shadow-lg` | `0 24px 80px rgba(0,0,0,.16)` | Modals, hero visuals |
| `shadow-glow` | `0 0 48px rgba(99,91,255,.24)` | Hero accent, selected AI state |

### Elevation Rules

- Flat surfaces should use borders.
- Raised surfaces should use both border and shadow.
- Modals should dim the page with a soft overlay.
- Glows should be rare and tied to brand/AI moments.
- Avoid neumorphism, glassmorphism-heavy panels, and harsh shadows.

---

## 7. Component Styling

## Buttons

### Primary Button

Use for the main action.

```css
background: var(--primary);
color: var(--text-inverse);
border: 1px solid var(--primary);
border-radius: var(--radius-md);
height: 40px;
padding: 0 16px;
font-size: 14px;
font-weight: 600;
box-shadow: var(--shadow-xs);
```

Behavior:

- Hover: slightly lighten/darken background.
- Active: scale to `0.98`.
- Focus: `2px` accent ring with `2px` offset.
- Disabled: `opacity: .45`, no shadow, no pointer.

### Secondary Button

Use for supporting actions.

```css
background: var(--surface);
color: var(--text-primary);
border: 1px solid var(--border);
border-radius: var(--radius-md);
height: 40px;
padding: 0 16px;
font-size: 14px;
font-weight: 600;
```

Behavior:

- Hover: background becomes `surface-muted`.
- Focus: accent ring.
- Keep secondary buttons visually quieter than primary buttons.

### Ghost Button

Use in toolbars, sidebars, and low-emphasis contexts.

```css
background: transparent;
color: var(--text-secondary);
border: 1px solid transparent;
border-radius: var(--radius-md);
height: 36px;
padding: 0 12px;
```

Hover: use `surface-muted`.

### Destructive Button

Use only for irreversible actions.

```css
background: var(--danger);
color: #FFFFFF;
border: 1px solid var(--danger);
```

Always pair destructive actions with clear copy.

---

## Cards

### Default Card

```css
background: var(--surface);
border: 1px solid var(--border);
border-radius: var(--radius-lg);
box-shadow: var(--shadow-xs);
padding: 24px;
```

### Feature Card

```css
background: linear-gradient(180deg, var(--surface), var(--surface-muted));
border: 1px solid var(--border);
border-radius: var(--radius-xl);
padding: 28px;
```

### Interactive Card

Behavior:

- Hover: translate `Y(-2px)`.
- Hover border: `border-strong`.
- Hover shadow: `shadow-sm`.
- Transition: `160ms ease`.

### Card Rules

- Card title should appear before supporting copy.
- Place primary card action at bottom or top-right.
- Do not nest more than one card level deep.
- Avoid using cards for every line item; use lists or tables instead.

---

## Inputs

### Text Input

```css
height: 40px;
background: var(--surface);
border: 1px solid var(--border);
border-radius: var(--radius-md);
padding: 0 12px;
font-size: 14px;
color: var(--text-primary);
```

States:

- Placeholder: `text-muted`
- Hover: `border-strong`
- Focus: accent ring + accent border
- Error: danger border + danger-soft background
- Disabled: muted background + muted text

### Textarea

```css
min-height: 112px;
padding: 12px;
resize: vertical;
line-height: 1.5;
```

### Select

- Match input height and radius.
- Use subtle chevron.
- Keep option lists raised with `shadow-md`.

### Form Rules

- Labels above fields.
- Helper text below fields.
- Error copy must be specific and human.
- Required indicators should be subtle.
- Group related fields in cards or sections.

---

## Navigation

### Top Navigation

Use for marketing pages and simple SaaS layouts.

```css
height: 64px;
background: color-mix(in srgb, var(--background) 86%, transparent);
backdrop-filter: blur(16px);
border-bottom: 1px solid var(--border);
```

Rules:

- Logo left.
- Primary nav center or left.
- CTA right.
- Sticky only when helpful.
- Reduce height to `56px` on mobile.

### Sidebar Navigation

Use for apps and dashboards.

```css
width: 260px;
background: var(--surface);
border-right: 1px solid var(--border);
padding: 16px;
```

Nav item:

```css
height: 36px;
border-radius: var(--radius-md);
padding: 0 10px;
font-size: 14px;
font-weight: 500;
color: var(--text-secondary);
```

Active item:

```css
background: var(--accent-soft);
color: var(--accent-strong);
```

Rules:

- Keep sidebar groups short.
- Use icons at `16–18px`.
- Collapse to icon rail on medium screens.
- Convert to drawer on mobile.

---

## Badges & Pills

Use badges for status, metadata, categories, and short signals.

```css
height: 24px;
padding: 0 8px;
border-radius: var(--radius-full);
font-size: 12px;
font-weight: 600;
border: 1px solid var(--border);
background: var(--surface-muted);
color: var(--text-secondary);
```

Variants:

- Success: `success-soft` background, `success` text.
- Warning: `warning-soft` background, `warning` text.
- Danger: `danger-soft` background, `danger` text.
- Accent: `accent-soft` background, `accent-strong` text.

Rules:

- Badges should be short: 1–3 words.
- Never use badges as buttons unless clearly interactive.
- Use icons only when they clarify meaning.

---

## Tables

Tables should feel precise, quiet, and scannable.

```css
font-size: 14px;
border-collapse: separate;
border-spacing: 0;
```

Rules:

- Header row: muted text, `12px`, uppercase optional.
- Row height: `48–56px`.
- Use bottom borders only.
- Align numbers right.
- Align text left.
- Use tabular numerals for metrics.
- Use hover background for row affordance.
- Keep bulk actions sticky or clearly visible.

---

## Modals & Dialogs

```css
background: var(--surface-raised);
border: 1px solid var(--border);
border-radius: var(--radius-xl);
box-shadow: var(--shadow-lg);
max-width: 560px;
padding: 24px;
```

Overlay:

```css
background: rgba(0,0,0,.42);
backdrop-filter: blur(4px);
```

Rules:

- Title first.
- One clear primary action.
- Secondary action should be cancel/close.
- Destructive modals require explicit confirmation copy.
- Close on escape and outside click unless destructive or critical.

---

## Toasts & Alerts

### Toast

```css
background: var(--surface-raised);
border: 1px solid var(--border);
border-radius: var(--radius-lg);
box-shadow: var(--shadow-md);
padding: 12px 14px;
```

Rules:

- Keep toast copy under 90 characters.
- Include action only when useful.
- Auto-dismiss success toasts.
- Persist error toasts until addressed.

### Inline Alert

Use for contextual feedback inside a page or form.

```css
border-radius: var(--radius-lg);
padding: 14px 16px;
border: 1px solid var(--border);
background: var(--surface-muted);
```

---

## Empty States

Empty states should guide action, not just announce absence.

Structure:

1. Small icon or illustration
2. Clear headline
3. One-sentence explanation
4. Primary action
5. Optional secondary link

Rules:

- Keep the tone helpful, never apologetic.
- Use subtle accent gradient only for important empty states.
- Avoid large decorative illustrations in dense apps.

---

## Code Blocks & Technical Surfaces

Use a developer-friendly style.

```css
background: #0B0D10;
color: #F7F7F5;
border: 1px solid #24272E;
border-radius: var(--radius-lg);
font-family: var(--font-mono);
font-size: 13px;
line-height: 1.6;
padding: 16px;
```

Rules:

- Use monospace for code only.
- Include copy button on hover or always visible.
- Keep command snippets compact.
- Add syntax highlighting with muted, accessible colors.
- Use terminal-style blocks for CLI instructions.

---

## 8. Motion & Interaction

### Timing

| Token | Duration | Usage |
|---|---:|---|
| `motion-fast` | `100ms` | Button press, small hover |
| `motion-base` | `160ms` | Default hover/focus |
| `motion-slow` | `240ms` | Panels, dropdowns |
| `motion-page` | `360ms` | Page/hero transitions |

### Easing

```css
--ease-standard: cubic-bezier(.2, .8, .2, 1);
--ease-out: cubic-bezier(.16, 1, .3, 1);
--ease-in-out: cubic-bezier(.65, 0, .35, 1);
```

### Motion Rules

- Hover movement should not exceed `2–4px`.
- Use opacity and transform, not layout-changing animation.
- Respect `prefers-reduced-motion`.
- Animate entrances only when they clarify hierarchy.
- Do not animate every element on page load.

---

## 9. Iconography & Illustration

### Icons

- Use simple line icons.
- Stroke width: `1.75–2px`.
- Default size: `16px` in controls, `20px` in cards, `24px` in feature sections.
- Icons should inherit text color unless they communicate status.
- Avoid mixing icon families.

### Illustrations

Preferred style:

- Abstract but functional.
- Soft gradients.
- Geometric forms.
- Product screenshots or UI fragments.
- Lightweight 3D only for hero/marketing moments.

Avoid:

- Generic cartoon people.
- Overly playful mascots unless brand-specific.
- Complex illustrations that compete with the interface.

---

## 10. Data Visualization

Charts should be clear, not decorative.

### Chart Colors

Use this sequence:

1. `#635BFF`
2. `#06B6D4`
3. `#16A34A`
4. `#F59E0B`
5. `#DC2626`
6. `#8B5CF6`
7. `#64748B`

### Rules

- Use direct labels when possible.
- Keep gridlines very subtle.
- Use tabular numerals.
- Avoid 3D charts.
- Avoid rainbow palettes.
- Highlight the key series and mute the rest.
- Always include units.
- Empty/loading/error chart states must be designed.

---

## 11. Responsive Behavior

### Breakpoints

```css
--breakpoint-sm: 640px;
--breakpoint-md: 768px;
--breakpoint-lg: 1024px;
--breakpoint-xl: 1280px;
--breakpoint-2xl: 1536px;
```

### Mobile Rules

- Minimum touch target: `44px`.
- Collapse nav into drawer or bottom sheet.
- Stack multi-column layouts.
- Reduce hero display type to `40–48px`.
- Increase vertical spacing between tappable items.
- Keep primary action visible.
- Avoid horizontal scrolling except for tables with clear affordance.

### Tablet Rules

- Use 8-column grid.
- Sidebars may collapse to rail.
- Cards can use 2-column layouts.
- Modals should use nearly full width with margin.

### Desktop Rules

- Use full 12-column grid.
- Keep dashboards information-dense but calm.
- Make secondary panels sticky when useful.
- Avoid line lengths over `760px`.

---

## 12. Accessibility

### Contrast

- Text must meet WCAG AA contrast.
- Do not rely on color alone for state.
- Focus states must be visible.
- Disabled states must remain readable enough to understand.

### Keyboard

- Every interactive element must be reachable by keyboard.
- Focus order must match visual order.
- Escape should close modals/popovers.
- Enter/Space should activate controls.

### Screen Readers

- Use semantic HTML first.
- Provide `aria-label` for icon-only buttons.
- Use `aria-live` for toasts and async feedback.
- Associate labels and errors with form controls.

### Reduced Motion

When `prefers-reduced-motion` is enabled:

```css
* {
  animation-duration: 0.001ms !important;
  animation-iteration-count: 1 !important;
  transition-duration: 0.001ms !important;
}
```

---

## 13. Content & Voice

### Voice

The product voice should be:

- Clear
- Calm
- Direct
- Helpful
- Slightly warm
- Never gimmicky

### UI Copy Rules

- Use verbs for actions.
- Prefer “Create project” over “New”.
- Prefer “Invite teammate” over “Add user”.
- Explain errors in plain language.
- Avoid exclamation marks except for celebratory moments.
- Avoid vague labels like “Submit”, “Okay”, or “Proceed”.

### Microcopy Examples

| Context | Good Copy |
|---|---|
| Empty project | “Create your first project to start organizing work.” |
| Loading | “Preparing your workspace…” |
| Save success | “Changes saved.” |
| Permission error | “You do not have permission to edit this workspace.” |
| Delete confirmation | “This action permanently removes the project and its data.” |
| Invite helper | “They’ll receive an email invitation with access instructions.” |

---

## 14. Page Patterns

## Landing Page

Structure:

1. Announcement pill
2. Hero headline
3. Supporting paragraph
4. Primary CTA + secondary CTA
5. Product visual or dashboard preview
6. Social proof
7. Feature grid
8. Use-case section
9. Integrations or workflow
10. Pricing/CTA
11. Footer

Rules:

- Hero should be visually dominant.
- Product screenshot should look real, not generic.
- Use gradient background sparingly.
- Keep above-the-fold CTA clear.
- Use strong contrast between sections.

## Dashboard

Structure:

1. App shell
2. Sidebar
3. Top bar with search/action
4. Page title and description
5. Primary metric cards
6. Main data/table area
7. Secondary insights panel

Rules:

- Prioritize scanning.
- Keep actions close to affected data.
- Use consistent row heights.
- Avoid overusing cards.
- Make filters obvious and reversible.

## Settings Page

Structure:

1. Left settings navigation
2. Page heading
3. Grouped sections
4. Field labels + helper copy
5. Save/cancel action region

Rules:

- Group destructive settings separately.
- Show current state clearly.
- Confirm risky changes.
- Avoid hiding important settings behind too many tabs.

## Auth Page

Structure:

1. Centered card or split layout
2. Logo
3. Short headline
4. Auth fields or provider buttons
5. Legal/helper links

Rules:

- Keep auth pages minimal.
- Use one primary action.
- Provide clear error states.
- Avoid marketing clutter near forms.

---

## 15. Do’s and Don’ts

### Do

- Use strong typographic hierarchy.
- Keep layouts aligned and intentional.
- Use neutral surfaces with subtle borders.
- Reserve accent color for meaningful moments.
- Make primary actions unmistakable.
- Design loading, empty, error, and success states.
- Use real product-like content in mockups.
- Prefer practical elegance over decoration.
- Use consistent radius and spacing.
- Make dark mode feel native, not inverted.

### Don’t

- Don’t use more than one primary CTA in the same visual area.
- Don’t overuse gradients.
- Don’t use heavy shadows everywhere.
- Don’t center-align dense content.
- Don’t mix too many typefaces.
- Don’t use low-contrast gray text.
- Don’t create cards inside cards inside cards.
- Don’t use color without semantic purpose.
- Don’t rely on animation to explain functionality.
- Don’t make dashboards look like marketing pages.

---

## 16. Implementation Tokens

Use these CSS variables as the implementation base.

```css
:root {
  color-scheme: light;

  --background: #FAFAF8;
  --surface: #FFFFFF;
  --surface-muted: #F4F4F1;
  --surface-raised: #FFFFFF;

  --border: #E6E4DE;
  --border-strong: #D4D0C7;

  --text-primary: #111111;
  --text-secondary: #55524C;
  --text-muted: #8A867C;
  --text-inverse: #FFFFFF;

  --primary: #111111;
  --primary-hover: #2A2A2A;

  --accent: #635BFF;
  --accent-soft: #EFEEFF;
  --accent-strong: #4F46E5;

  --success: #16A34A;
  --success-soft: #DCFCE7;
  --warning: #F59E0B;
  --warning-soft: #FEF3C7;
  --danger: #DC2626;
  --danger-soft: #FEE2E2;
  --info: #0284C7;
  --info-soft: #E0F2FE;

  --font-sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: "JetBrains Mono", "SF Mono", Consolas, "Liberation Mono", monospace;
  --font-display: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;

  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-xl: 20px;
  --radius-2xl: 28px;
  --radius-full: 999px;

  --shadow-xs: 0 1px 2px rgba(0,0,0,.05);
  --shadow-sm: 0 4px 12px rgba(0,0,0,.06);
  --shadow-md: 0 12px 32px rgba(0,0,0,.10);
  --shadow-lg: 0 24px 80px rgba(0,0,0,.16);
  --shadow-glow: 0 0 48px rgba(99,91,255,.24);

  --ease-standard: cubic-bezier(.2, .8, .2, 1);
  --ease-out: cubic-bezier(.16, 1, .3, 1);
  --ease-in-out: cubic-bezier(.65, 0, .35, 1);
}

[data-theme="dark"] {
  color-scheme: dark;

  --background: #08090A;
  --surface: #111214;
  --surface-muted: #181A1D;
  --surface-raised: #1D1F23;

  --border: #2A2D33;
  --border-strong: #3A3F47;

  --text-primary: #F7F7F5;
  --text-secondary: #B7B8BC;
  --text-muted: #7D828A;
  --text-inverse: #111111;

  --primary: #FFFFFF;
  --primary-hover: #EDEDED;

  --accent: #8B7CFF;
  --accent-soft: #1D1A3D;
  --accent-strong: #A799FF;

  --success: #22C55E;
  --success-soft: #0F2E1A;
  --warning: #FBBF24;
  --warning-soft: #3A2A0A;
  --danger: #F87171;
  --danger-soft: #3A1212;
  --info: #38BDF8;
  --info-soft: #082F49;

  --shadow-xs: 0 1px 2px rgba(0,0,0,.22);
  --shadow-sm: 0 4px 12px rgba(0,0,0,.28);
  --shadow-md: 0 12px 32px rgba(0,0,0,.36);
  --shadow-lg: 0 24px 80px rgba(0,0,0,.48);
  --shadow-glow: 0 0 56px rgba(139,124,255,.30);
}
```

---

## 17. Agent Prompt Guide

When asking an AI coding/design agent to build UI with this file, use prompts like:

### General UI

“Use `DESIGN.md` as the design source of truth. Build this interface with a premium SaaS/developer-product feel: clean hierarchy, neutral surfaces, subtle borders, strong typography, restrained accent color, and polished responsive behavior.”

### Landing Page

“Create a landing page following `DESIGN.md`: calm premium hero, clear primary CTA, product visual, soft gradient accent, feature cards, social proof, and responsive layout.”

### Dashboard

“Create a dashboard following `DESIGN.md`: app shell, sidebar navigation, precise table layout, metric cards, subtle borders, clear filters, and strong empty/loading/error states.”

### Form

“Create this form following `DESIGN.md`: labels above fields, helpful helper text, accessible error states, clear primary action, and a calm card-based layout.”

### Dark Mode

“Implement the design with full light and dark theme support using the tokens in `DESIGN.md`. Dark mode should feel native, not like a simple inversion.”

---

## 18. Quality Checklist

Before shipping any UI, verify:

- [ ] The primary action is obvious.
- [ ] Typography hierarchy is clear.
- [ ] Spacing follows the 8px scale.
- [ ] Color usage is restrained and semantic.
- [ ] Borders and shadows are subtle.
- [ ] Components use consistent radius.
- [ ] Hover, focus, active, disabled states exist.
- [ ] Empty, loading, error, and success states exist.
- [ ] Mobile layout is intentional.
- [ ] Keyboard navigation works.
- [ ] Contrast meets accessibility standards.
- [ ] Dark mode is visually balanced.
- [ ] Copy is clear and human.
- [ ] No section feels over-decorated.
- [ ] The result feels coherent across pages.

---

## 19. Final Design Summary

This design system should produce interfaces that feel:

- Minimal like Vercel
- Precise like Linear
- Polished like Stripe
- Spacious like Apple
- Warm like Notion
- Technical like Supabase
- Collaborative like Figma
- AI-native without looking gimmicky

The final result should be a refined, highly usable, modern product interface that feels trustworthy, fast, and thoughtfully crafted.

## 20. AI Coding Agent Rules

These rules are mandatory when using this design system with AI builders, coding agents, UI generators, or design assistants.

### Source-of-Truth Rule

When generating UI:

- Do not invent new colors unless explicitly requested.
- Do not invent new shadows, radii, spacing scales, or typography scales unless explicitly requested.
- Use the tokens in this file as the default design language.
- If a component needs a new variant, derive it from existing tokens.
- Prefer production-ready UI over decorative mockups.
- Prioritize accessibility, responsiveness, and realistic content.

### Agent Behavior

An AI agent should:

1. Read this file before generating UI.
2. Identify the page type or component type.
3. Select the closest matching page pattern or component rules.
4. Apply the token system consistently.
5. Generate all important states:
   - Default
   - Hover
   - Focus
   - Active
   - Disabled
   - Loading
   - Empty
   - Error
   - Success
6. Check mobile and desktop layouts.
7. Avoid decorative complexity unless the page is marketing-oriented.
8. Use realistic copy instead of placeholder text.
9. Keep the interface visually calm and functionally clear.

### Agent Output Quality

Generated UI should feel:

- Complete, not partial.
- Intentional, not randomly styled.
- Product-specific, not template-like.
- Accessible by default.
- Responsive without afterthought.
- Consistent across components.
- Easy for a developer to maintain.

### Default Stack Assumptions

Unless told otherwise, assume:

- React or Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui-compatible primitives
- Lucide-style icons
- CSS variables for theme tokens
- Responsive mobile-first implementation

---

## 21. Tailwind Mapping

Use this mapping when implementing the design system in Tailwind CSS.

### Color Mapping

| Design Token | Tailwind Concept | Usage |
|---|---|---|
| `background` | `bg-background` | Page background |
| `surface` | `bg-card` or `bg-popover` | Cards, panels |
| `surface-muted` | `bg-muted` | Secondary areas |
| `surface-raised` | `bg-popover` | Menus, dialogs |
| `border` | `border-border` | Default borders |
| `border-strong` | `border-input` or custom | Strong borders |
| `text-primary` | `text-foreground` | Primary text |
| `text-secondary` | `text-muted-foreground` | Secondary text |
| `text-muted` | `text-muted-foreground/70` | Hints |
| `primary` | `bg-primary text-primary-foreground` | Primary actions |
| `accent` | `text-accent-foreground bg-accent` | Selected states |
| `danger` | `text-destructive bg-destructive` | Destructive states |

### Radius Mapping

| Design Token | Tailwind Class |
|---|---|
| `radius-xs` | `rounded-sm` |
| `radius-sm` | `rounded-md` |
| `radius-md` | `rounded-lg` |
| `radius-lg` | `rounded-xl` |
| `radius-xl` | `rounded-2xl` |
| `radius-2xl` | `rounded-3xl` |
| `radius-full` | `rounded-full` |

### Spacing Mapping

| Design Token | Tailwind Class |
|---|---|
| `space-1` | `p-1`, `gap-1`, `m-1` |
| `space-2` | `p-2`, `gap-2`, `m-2` |
| `space-3` | `p-3`, `gap-3`, `m-3` |
| `space-4` | `p-4`, `gap-4`, `m-4` |
| `space-6` | `p-6`, `gap-6`, `m-6` |
| `space-8` | `p-8`, `gap-8`, `m-8` |
| `space-12` | `p-12`, `gap-12`, `m-12` |
| `space-16` | `p-16`, `gap-16`, `m-16` |

### Common Tailwind Patterns

#### Page Shell

```tsx
<div className="min-h-screen bg-background text-foreground">
  <main className="mx-auto w-full max-w-7xl px-6 py-10 lg:px-8">
    {children}
  </main>
</div>
```

#### Card

```tsx
<div className="rounded-xl border bg-card p-6 shadow-sm">
  {children}
</div>
```

#### Primary Button

```tsx
<Button className="h-10 rounded-lg px-4 font-semibold">
  Create project
</Button>
```

#### Secondary Button

```tsx
<Button variant="outline" className="h-10 rounded-lg px-4 font-semibold">
  View docs
</Button>
```

#### Muted Section

```tsx
<section className="rounded-2xl border bg-muted/50 p-8">
  {children}
</section>
```

---

## 22. shadcn/ui Mapping

Use shadcn/ui primitives as the base component layer.

### Recommended Component Defaults

| Component | Default Treatment |
|---|---|
| `Button` | Use `default`, `secondary`, `outline`, `ghost`, `destructive` |
| `Card` | Use for grouped decisions, metrics, settings, feature blocks |
| `Input` | Use with visible label and helper/error text |
| `Textarea` | Use for multi-line content with clear minimum height |
| `Dialog` | Use for focused tasks and confirmations |
| `Sheet` | Use for mobile nav and side workflows |
| `Tabs` | Use for peer-level views, not hidden settings overload |
| `DropdownMenu` | Use for secondary actions |
| `Command` | Use for search, command palettes, quick navigation |
| `Table` | Use for structured data; keep rows calm and scannable |
| `Badge` | Use for status and metadata |
| `Toast/Sonner` | Use for async feedback |

### shadcn Theme Guidance

When configuring shadcn CSS variables:

- Keep `background` warm off-white in light mode.
- Keep `foreground` near black, not pure gray.
- Keep `card` white in light mode.
- Use the accent color for selected states, not every button.
- Keep destructive red semantically reserved.
- Use border contrast enough to define structure.

### Component Rules

- Prefer shadcn primitives over custom one-off components.
- Wrap primitives in product-specific components only when the pattern repeats.
- Do not over-customize shadcn defaults to the point that components become inconsistent.
- Maintain visible focus states.
- Preserve keyboard and screen-reader behavior.

---

## 23. Page Blueprints

Use these as direct recipes for generating complete pages.

---

### 23.1 SaaS Landing Page Blueprint

#### Purpose

Convert visitors by clearly explaining what the product does, why it matters, and what action to take next.

#### Structure

1. Sticky or simple top nav
2. Announcement pill
3. Hero headline
4. Supporting paragraph
5. Primary CTA and secondary CTA
6. Product screenshot or interactive visual
7. Logo/social proof row
8. Feature grid
9. Workflow section
10. Use cases
11. Testimonials or proof
12. Pricing preview or final CTA
13. Footer

#### Visual Rules

- Hero uses `display-lg` or `display-xl`.
- Supporting copy max width: `720px`.
- Use one subtle gradient background.
- Product visual should be framed in a rounded card/browser shell.
- Feature cards should be 2 or 3 columns on desktop.
- Mobile layout should stack cleanly.

#### CTA Rules

- One primary CTA above the fold.
- One secondary CTA allowed.
- CTA copy should be specific:
  - Good: “Start building”
  - Good: “View live demo”
  - Avoid: “Learn more” as the only CTA

#### Landing Page Prompt

```md
Build a premium SaaS landing page using DESIGN_PRO.md. Use a calm hero, one clear primary CTA, a polished product visual, feature cards, social proof, workflow explanation, and responsive mobile behavior. Keep the design minimal, precise, and trustworthy.
```

---

### 23.2 AI Chat Interface Blueprint

#### Purpose

Create a focused AI assistant experience that feels fast, trustworthy, and useful.

#### Structure

1. App shell
2. Sidebar with conversations/projects
3. Main chat area
4. Message list
5. Composer
6. Tool/status area
7. Optional right-side context panel

#### Message Design

User message:

- Right-aligned or clearly distinguished.
- Compact width.
- Neutral surface.
- Avoid overly bright color.

Assistant message:

- Left-aligned.
- More spacious.
- Supports Markdown, code, tables, citations, and tool output.
- Use clear spacing between reasoning sections and final answer.

Composer:

- Fixed or sticky at bottom.
- Rounded large container.
- Supports attachments, model/tools, send action.
- Focus state must be obvious.
- Placeholder should be helpful:
  - Good: “Ask about your project, data, or workflow…”
  - Avoid: “Type something…”

#### AI-Specific States

Design states for:

- Thinking
- Searching
- Reading files
- Running code
- Generating output
- Tool error
- Partial result
- Citation available
- Unsafe/unavailable request

#### AI Chat Prompt

```md
Build an AI chat interface using DESIGN_PRO.md. Include sidebar conversations, a polished message area, assistant/user message styles, a powerful composer, tool status states, empty state, loading state, and mobile behavior.
```

---

### 23.3 Admin Dashboard Blueprint

#### Purpose

Help users monitor, filter, inspect, and act on operational data.

#### Structure

1. Sidebar navigation
2. Top bar with search, actions, user menu
3. Page heading
4. Metric cards
5. Filter/search row
6. Main table or chart
7. Detail drawer or side panel
8. Pagination/bulk actions

#### Metric Cards

Each metric card should include:

- Label
- Value
- Change indicator
- Small contextual note
- Optional mini-chart

#### Table Rules

- Row height: `48–56px`.
- Use sticky table header for long tables.
- Include empty and loading states.
- Filters must be easy to clear.
- Bulk actions must appear only when rows are selected.

#### Dashboard Prompt

```md
Build an admin dashboard using DESIGN_PRO.md. Include sidebar navigation, top bar, metric cards, filters, a precise data table, empty/loading/error states, and a responsive detail drawer.
```

---

### 23.4 Pricing Page Blueprint

#### Purpose

Help users compare plans and choose confidently.

#### Structure

1. Page headline
2. Short value statement
3. Billing toggle
4. Pricing cards
5. Feature comparison
6. FAQ
7. Final CTA

#### Pricing Card Rules

- Highlight one recommended plan.
- Use clear price hierarchy.
- Keep feature bullets short.
- Use one CTA per plan.
- Avoid visually overwhelming the cheapest plan.
- Enterprise/custom plan should feel serious, not vague.

#### Pricing Prompt

```md
Build a pricing page using DESIGN_PRO.md. Include billing toggle, three plan cards, a highlighted recommended plan, comparison table, FAQ, and final CTA. Keep copy clear and decision-focused.
```

---

### 23.5 Settings Page Blueprint

#### Purpose

Let users configure account, workspace, billing, integrations, or preferences without confusion.

#### Structure

1. Settings sidebar
2. Page title and description
3. Grouped settings sections
4. Forms with labels/helper text
5. Save/cancel action bar
6. Destructive zone, separated

#### Rules

- Use sections instead of one giant form.
- Show saved/current state.
- Disable save until changes exist.
- Confirm destructive actions.
- Use helper text for complex settings.
- Keep dangerous actions visually separated.

#### Settings Prompt

```md
Build a settings page using DESIGN_PRO.md. Include left settings nav, grouped sections, accessible forms, helper text, save/cancel behavior, and a clearly separated destructive zone.
```

---

### 23.6 Documentation Page Blueprint

#### Purpose

Help users learn quickly and copy implementation details.

#### Structure

1. Docs shell
2. Left navigation
3. Main article content
4. Right table of contents
5. Code blocks
6. Callouts
7. Previous/next navigation

#### Rules

- Article max width: `760px`.
- Code blocks must include copy buttons.
- Use callouts sparingly.
- Keep headings descriptive.
- Provide runnable examples when possible.
- Keep docs visually quieter than marketing pages.

#### Docs Prompt

```md
Build a documentation page using DESIGN_PRO.md. Include docs navigation, article content, right-side table of contents, code blocks with copy buttons, callouts, and previous/next links.
```

---

### 23.7 Mobile App / Responsive Web App Blueprint

#### Purpose

Provide a touch-friendly version of the product without losing core functionality.

#### Structure

1. Top app bar or compact header
2. Main content stack
3. Primary action
4. Bottom navigation or drawer
5. Sheets for secondary workflows

#### Rules

- Minimum tap target: `44px`.
- Use bottom sheets for complex controls.
- Avoid tiny icon-only actions.
- Keep filters collapsed but discoverable.
- Use sticky primary actions when needed.
- Test with long content and narrow screens.

#### Mobile Prompt

```md
Build a mobile-first version using DESIGN_PRO.md. Use touch-friendly controls, stacked layout, bottom navigation or drawer, bottom sheets for filters/actions, and clear empty/loading/error states.
```

---

### 23.8 Auth Flow Blueprint

#### Purpose

Help users sign in, sign up, recover access, or join a workspace with minimal friction.

#### Structure

1. Logo
2. Short headline
3. Auth provider buttons
4. Divider
5. Email/password or magic-link form
6. Error/helper text
7. Legal and support links

#### Rules

- Keep auth pages quiet.
- Avoid unnecessary marketing content.
- Show exact errors.
- Support keyboard submission.
- Make provider buttons visually consistent.
- Use secure, reassuring copy.

#### Auth Prompt

```md
Build an auth page using DESIGN_PRO.md. Include logo, clear headline, provider buttons, email form, accessible errors, legal links, and responsive layout.
```

---

## 24. Anti-Patterns: Never Generate This

These rules prevent generic, inconsistent, or low-quality UI.

### Visual Anti-Patterns

Never generate:

- Random purple-gradient startup UI everywhere.
- Excessive glassmorphism.
- Heavy shadows on every card.
- Low-contrast gray text.
- Giant icons in dense dashboards.
- Decorative blobs behind every section.
- Multiple unrelated accent colors.
- Overly rounded controls mixed with sharp cards.
- Cards inside cards inside cards.
- Centered long-form text.
- Hero sections with three or more CTAs.
- Pricing cards where every plan looks equally emphasized.
- Dashboards that look like marketing landing pages.
- Marketing pages that look like admin panels.
- UI that only looks good in light mode.

### Content Anti-Patterns

Never use:

- “Lorem ipsum”
- “Get started today!” as generic filler everywhere
- “Submit” when a specific verb is available
- “Click here”
- “Error occurred”
- “Something went wrong” without recovery guidance
- Fake testimonials without making them obviously placeholder
- Vague empty states like “No data”
- Placeholder metrics that look real without context

### Layout Anti-Patterns

Never:

- Place primary and destructive actions next to each other without separation.
- Hide the only primary action below the fold.
- Use inconsistent horizontal padding between sections.
- Mix unrelated alignment systems on the same page.
- Make mobile layouts by simply shrinking desktop.
- Let tables overflow on mobile without controls.
- Use modals for long multi-step workflows.
- Make every section full-width without content max width.

### Interaction Anti-Patterns

Never:

- Remove focus outlines without replacing them.
- Use hover-only controls for essential actions.
- Animate layout in a way that causes content jumps.
- Make loading states look broken.
- Trigger destructive actions instantly.
- Use disabled buttons without explaining why when context is unclear.

---

## 25. UX Writing System

### Voice Principles

The voice should be:

- Direct
- Calm
- Useful
- Specific
- Respectful of the user’s time

### Button Copy

Buttons should usually begin with a verb.

Good:

- Create project
- Invite teammate
- Save changes
- Connect GitHub
- Export report
- Start analysis
- View usage
- Open settings

Avoid:

- Submit
- Click here
- Continue, when the destination is unclear
- OK, when an action can be named

### Empty State Copy

Empty states should answer:

1. What is missing?
2. Why does it matter?
3. What can the user do next?

Example:

```md
No projects yet

Create your first project to organize work, invite teammates, and track progress in one place.

[Create project]
```

Avoid:

```md
No data found.
```

### Error Copy

Errors should explain:

1. What happened
2. Why, if known
3. What to do next

Good:

```md
We could not save your changes because the connection timed out. Check your internet connection and try again.
```

Avoid:

```md
Error: failed.
```

### Confirmation Copy

For destructive actions, be explicit.

Good:

```md
Delete workspace?

This permanently removes the workspace, including projects, members, and settings. This action cannot be undone.
```

Avoid:

```md
Are you sure?
```

### Loading Copy

Good:

- Preparing your workspace…
- Importing your data…
- Checking permissions…
- Generating summary…
- Syncing integrations…

Avoid:

- Loading…
- Please wait…
- Working…

### Success Copy

Good:

- Changes saved.
- Project created.
- Invite sent.
- Export ready.
- Integration connected.

Avoid overly excited language unless the brand calls for it.

---

## 26. Component Acceptance Criteria

A component is not complete until these are addressed.

### Button

- [ ] Has default, hover, active, focus, disabled, and loading states.
- [ ] Uses correct variant.
- [ ] Has accessible name.
- [ ] Does not rely on icon alone unless labeled.
- [ ] Maintains minimum touch target on mobile.

### Card

- [ ] Has clear purpose.
- [ ] Uses consistent padding and radius.
- [ ] Does not contain unnecessary nested cards.
- [ ] Has responsive behavior.
- [ ] Uses action placement consistently.

### Form Field

- [ ] Has visible label.
- [ ] Has helper text when needed.
- [ ] Has error state.
- [ ] Error is linked to field for assistive tech.
- [ ] Required/optional status is clear.
- [ ] Input has focus state.

### Modal/Dialog

- [ ] Has title.
- [ ] Has clear primary and secondary actions.
- [ ] Focus is trapped inside.
- [ ] Escape key behavior is defined.
- [ ] Destructive actions require explicit copy.
- [ ] Works on mobile.

### Table

- [ ] Columns are clearly labeled.
- [ ] Numbers align right.
- [ ] Empty state exists.
- [ ] Loading state exists.
- [ ] Sorting/filtering is clear if available.
- [ ] Mobile overflow behavior is designed.

### Navigation

- [ ] Current location is obvious.
- [ ] Navigation works on mobile.
- [ ] Icon-only items have labels/tooltips.
- [ ] Groups are not too long.
- [ ] Keyboard navigation works.

### Toast

- [ ] Message is short.
- [ ] Status is clear.
- [ ] Error toasts remain visible long enough.
- [ ] Optional action is useful.
- [ ] Toast does not block critical UI.

---

## 27. Page Acceptance Criteria

A page is not complete until these are addressed.

### Universal

- [ ] Clear page title.
- [ ] Clear primary action.
- [ ] Responsive mobile layout.
- [ ] Loading state.
- [ ] Empty state.
- [ ] Error state.
- [ ] Accessible focus states.
- [ ] Realistic content.
- [ ] No visual token drift.
- [ ] Dark mode support.

### Landing Page

- [ ] Hero explains product clearly.
- [ ] CTA is visible above fold.
- [ ] Product visual feels real.
- [ ] Feature sections are scannable.
- [ ] Social proof is credible.
- [ ] Mobile hero is not cramped.

### Dashboard

- [ ] Key metrics are visible.
- [ ] Filters are understandable.
- [ ] Table/chart is scannable.
- [ ] Detail actions are near relevant data.
- [ ] Bulk actions are contextual.
- [ ] Long data states are handled.

### Settings

- [ ] Sections are grouped logically.
- [ ] Save/cancel behavior is clear.
- [ ] Destructive actions are separated.
- [ ] Current state is visible.
- [ ] Complex settings include helper text.

### AI Chat

- [ ] Empty state suggests useful prompts.
- [ ] Composer is easy to find.
- [ ] Tool/status states are visible.
- [ ] Messages support rich content.
- [ ] Long conversations remain usable.
- [ ] Mobile chat does not hide input.

---

## 28. Product-Specific Pattern Library

Use these reusable patterns to keep the product coherent.

### Feature Card Pattern

```md
[Icon]
Feature title
One-sentence benefit-oriented description.
Optional link or small action.
```

Rules:

- Title should be 2–5 words.
- Description should be one sentence.
- Icon should be subtle.
- Avoid equal visual weight for every card if one feature is primary.

### Metric Card Pattern

```md
Metric label
Large value
Change indicator
Context note
```

Example:

```md
Active users
12,480
+8.2% from last month
Updated 4 minutes ago
```

Rules:

- Use tabular numerals.
- Do not show percentages without baseline.
- Use status color only for meaningful change.

### Settings Section Pattern

```md
Section title
Short explanation

[Field group]
[Field group]

[Save changes]
```

Rules:

- Keep each section focused.
- Separate destructive settings.
- Explain consequences before action.

### Command Palette Pattern

```md
Search input
Recent actions
Suggested navigation
Available commands
```

Rules:

- Use keyboard shortcuts.
- Highlight matched text.
- Keep command names action-oriented.

### Empty State Pattern

```md
Icon or visual
Clear headline
Helpful explanation
Primary action
Optional secondary link
```

Rules:

- Avoid sad or blameful tone.
- Provide a path forward.
- Match the visual weight to the importance of the page.

---

## 29. Advanced Theming Guidance

### Brand Flexibility

This design can adapt to different brand personalities while keeping the same system.

#### More Enterprise

- Use less gradient.
- Increase border clarity.
- Reduce playful illustration.
- Use more structured layouts.
- Prefer blue or neutral accent.

#### More Creator-Friendly

- Use warmer surfaces.
- Add soft illustrations.
- Use slightly larger radius.
- Make empty states more expressive.
- Use more conversational copy.

#### More Developer-Oriented

- Use more monospace metadata.
- Show technical details clearly.
- Use denser tables and code blocks.
- Keep gradients minimal.
- Prioritize CLI/API examples.

#### More AI-Native

- Add subtle glow to AI-active states.
- Use status chips for tool use.
- Show provenance/citations clearly.
- Design for partial/progressive results.
- Keep trust and transparency central.

### Accent Swapping

The system supports changing the accent color if needed.

Recommended accent alternatives:

| Name | Accent | Accent Soft | Accent Strong |
|---|---:|---:|---:|
| Indigo | `#635BFF` | `#EFEEFF` | `#4F46E5` |
| Blue | `#2563EB` | `#EFF6FF` | `#1D4ED8` |
| Emerald | `#059669` | `#ECFDF5` | `#047857` |
| Violet | `#7C3AED` | `#F5F3FF` | `#6D28D9` |
| Rose | `#E11D48` | `#FFF1F2` | `#BE123C` |

Rules:

- Swap accent tokens globally.
- Do not mix multiple accent families.
- Recheck contrast after changing accent.
- Keep semantic colors unchanged.

---

## 30. Design Review Rubric

Score generated UI from 1 to 5 in each category.

| Category | 1 | 3 | 5 |
|---|---|---|---|
| Visual hierarchy | Confusing | Mostly clear | Instantly clear |
| Token consistency | Random styles | Minor drift | Fully consistent |
| Accessibility | Poor | Basic | Strong |
| Responsiveness | Broken | Works | Thoughtful |
| Copy quality | Generic | Acceptable | Specific and useful |
| Component states | Missing | Partial | Complete |
| Product fit | Template-like | Somewhat relevant | Purpose-built |
| Polish | Rough | Decent | Premium |

### Minimum Shipping Bar

Do not ship if any category scores below 3.

Target score: 4 or higher across all categories.

---

## 31. “Generate Like This” Examples

### Good Hero Section

```md
Headline:
Build internal tools your team actually wants to use

Supporting copy:
Create fast, reliable workflows with clean permissions, live data, and AI-assisted automation.

Primary CTA:
Start building

Secondary CTA:
View demo
```

Why it works:

- Clear value.
- Specific audience.
- Action-oriented CTA.
- No generic hype.

### Good Empty State

```md
No reports yet

Generate your first report to summarize activity, identify trends, and share updates with your team.

[Generate report]
```

Why it works:

- Explains what is missing.
- Explains why it matters.
- Provides a clear next step.

### Good Error State

```md
Could not connect GitHub

The authorization window was closed before access was granted. Reopen GitHub and approve the connection to continue.

[Try again]
```

Why it works:

- Explains the problem.
- Explains likely cause.
- Gives recovery action.

### Good Dashboard Header

```md
Workspace activity

Monitor usage, recent changes, and team activity across your workspace.

[Export report] [Invite teammate]
```

Why it works:

- Clear purpose.
- Useful actions.
- No vague labels.

---

## 32. “Never Generate Like This” Examples

### Bad Hero

```md
Unlock the future of productivity

Experience the next generation of innovation with our revolutionary platform.

[Get Started] [Learn More] [Contact Us]
```

Problems:

- Generic.
- Hype-heavy.
- No specific value.
- Too many CTAs.

### Bad Empty State

```md
No data.
```

Problems:

- No context.
- No next step.
- Feels broken.

### Bad Error

```md
Something went wrong.
```

Problems:

- No cause.
- No recovery path.
- Creates user anxiety.

### Bad Dashboard

```md
Dashboard

[Card] [Card] [Card] [Card]
```

Problems:

- No hierarchy.
- No context.
- No clear actions.
- Template-like.

---

## 33. Final Agent Instruction

When using this document to generate UI, follow this priority order:

1. User’s explicit request
2. Product/page purpose
3. Accessibility and usability
4. DESIGN_PRO.md tokens and rules
5. Existing component conventions
6. Visual polish

Never sacrifice clarity for decoration.

Never sacrifice accessibility for aesthetics.

Never sacrifice consistency for novelty.

The best result should look like a real product built by a careful senior product designer and frontend engineer.
