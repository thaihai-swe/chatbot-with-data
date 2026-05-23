# DESIGN_BEST.md

A stack-agnostic design system for building polished, accessible, modern product interfaces.

This file is the source of truth for UI generation, product design, implementation planning, visual QA, and AI coding agents. It combines disciplined tokens, strong product UX, warm editorial polish, developer clarity, and strict anti-drift rules without depending on any framework, language, component kit, styling library, icon package, or design tool.

Use this file as `DESIGN.md` in a project root, design workspace, implementation brief, or AI agent context.

---

## 0. Machine-Readable Design Brief

```yaml
version: 2.0
name: Best Stack-Agnostic Product Design System
purpose: Generate polished, accessible, production-ready product interfaces.
stack_policy:
  dependency: none
  rule: Do not assume any framework, runtime, styling library, component kit, icon package, or design tool.
  implementation_target: Any web, native mobile, desktop, embedded, low-code, no-code, or design-tool environment.
  adapter_requirement: Map tokens and component specs into the project's existing primitives instead of introducing new dependencies.
  prohibited_assumptions:
    - a specific JavaScript framework
    - a specific backend or frontend runtime
    - a specific CSS methodology or utility framework
    - a specific UI component library
    - a specific icon library
    - a specific package manager
    - a specific design tool
personality:
  mood: calm confidence
  density: medium-low by default, medium-high for dashboards and operational tools
  brand_feel: premium, useful, intelligent, trustworthy
  interaction_feel: fast, precise, intentional
  visual_style: neutral-first surfaces, crisp borders, soft depth, restrained accent
priority_order:
  - user explicit request
  - product and page purpose
  - accessibility and usability
  - token consistency
  - responsive/adaptive behavior
  - platform conventions
  - visual polish
hard_rules:
  - Do not invent colors, radii, shadows, typography, or spacing unless explicitly requested.
  - Use one primary action per visual area.
  - Use accent color for meaning, not decoration.
  - Use product-like content, never lorem ipsum.
  - Generate default, hover or press, focus, active, disabled, loading, empty, error, and success states where relevant.
  - Respect keyboard navigation, assistive technology, touch targets, and reduced motion.
  - Dark mode must be designed, not inverted.
  - Implement with the host project's existing stack and primitives.
```

---

## 1. Stack-Agnostic Contract

### Core rule

This document defines design intent, tokens, behavior, quality bars, and page patterns. It does not prescribe implementation technology.

An implementer or AI agent must translate the guidance into the current project environment, such as:

- Web apps
- Native iOS apps
- Native Android apps
- Desktop apps
- Cross-platform apps
- Design tools
- Low-code or no-code builders
- Internal UI frameworks
- Server-rendered apps
- Component systems already present in the project

### What this file may define

| Area | Allowed guidance |
|---|---|
| Colors | Token names, values, contrast roles, semantic usage |
| Typography | Scale, weights, line heights, rhythm, max text widths |
| Layout | Grids, spacing, hierarchy, density, responsive behavior |
| Components | Anatomy, states, sizing, placement, behavior, accessibility |
| Motion | Durations, easing feel, purpose, reduced-motion behavior |
| Content | Voice, labels, empty states, error messages, confirmations |
| Quality | Acceptance criteria, anti-patterns, review rubric |

### What this file must not require

| Do not require | Reason |
|---|---|
| A named framework | The same design must work across web, native, desktop, and design tools. |
| A named UI kit | Existing project primitives should be adapted first. |
| A named styling system | Tokens can become variables, constants, theme values, resources, or design-tool variables. |
| A named icon set | Use the icon style, not a package dependency. |
| A named font package | Use brand fonts when present; otherwise use high-quality platform defaults. |
| A named build tool | The design system is not tied to a delivery pipeline. |

### Adapter rule

If the project needs platform-specific implementation, create a separate adapter outside this file.

Examples:

- `design.tokens.json`
- `theme.adapter`
- `platform-style-guide.md`
- `component-mapping.md`
- design-tool variables
- native resource files
- project-specific theme objects

The adapter may reference this file, but this file must remain portable.

---

## 2. Design DNA

The interface should feel like a real product built by a careful senior product designer and implementation engineer.

### Combined strengths

- Vercel-like precision: black/white restraint, crisp hairlines, technical labels, minimal decoration.
- Linear-like discipline: one accent color, dark-mode surface ladder, product visuals as proof, dense but calm layouts.
- Stripe-like polish: tasteful atmospheric gradients, tabular numerics, premium cards, clear conversion paths.
- Apple-like whitespace: generous rhythm, strong scale, calm hierarchy, no visual clutter.
- Notion-like warmth: approachable copy, warm surfaces, friendly empty states, soft content cards.
- Supabase-like developer clarity: code-first surfaces, API or workflow examples, restrained technical presentation.
- Figma-like collaboration: useful color moments, friendly details, clear shared-work patterns.
- Claude/Cursor-like editorial warmth: human tone, warm canvas option, product intelligence without AI gimmicks.

### Core feeling

The product should be:

- Premium but approachable.
- Minimal but not empty.
- Technical but humane.
- Calm, fast, and trustworthy.
- Sharp in structure, soft in detail.
- AI-native without looking like a generic purple-gradient startup template.

### Design philosophy

1. Clarity is the highest aesthetic.
2. The next action must be obvious.
3. Whitespace should create structure, not emptiness.
4. Borders and surface contrast come before heavy shadows.
5. Accent color is a signal, not decoration.
6. Gradients appear only in signature moments.
7. Motion explains change; it never distracts.
8. Product UI evidence is stronger than abstract decoration.
9. Every generated screen must include important states.
10. The system should feel coherent across marketing, app, docs, and mobile.

---

## 3. Usage Boundaries

### Best suited for

- AI SaaS products
- Developer tools
- Productivity platforms
- Admin dashboards
- Analytics products
- Internal tools
- Documentation experiences
- Pricing pages
- Auth flows
- Landing pages
- Mobile companion apps

### Not suited for without adaptation

- Highly playful consumer apps
- Children's products
- Luxury fashion or hospitality
- Photo-first travel or lifestyle apps
- Games or entertainment-heavy interfaces

### Brand adaptation modes

Use one mode per project. Do not mix all modes at once.

| Mode | When to use | Adjustments |
|---|---|---|
| `default-product` | SaaS, AI tools, dashboards | Neutral palette, indigo accent, subtle gradients |
| `developer` | APIs, dev tools, docs | More mono, more code blocks, less decoration |
| `enterprise` | B2B, security, finance, compliance | Less gradient, stronger structure, clearer borders |
| `creator` | Creator tools, collaboration, content apps | Warmer surfaces, friendlier copy, softer cards |
| `ai-native` | AI agents, copilots, automation tools | Tool-status chips, provenance, progressive result states |
| `data-heavy` | Analytics, ops, admin, finance | Denser tables, tabular numerals, fewer decorative cards |

---

## 4. Color System

### Color strategy

Use a neutral-first palette with one vivid accent family and semantic status colors. Neutral colors should carry most of the interface. Color should help users understand state, hierarchy, and action.

### Light theme tokens

| Token | Value | Role |
|---|---:|---|
| `background` | `#FAFAF8` | Main page canvas, warm off-white |
| `background-cool` | `#F7F8FA` | Optional cooler canvas for enterprise/data products |
| `surface` | `#FFFFFF` | Cards, panels, sheets |
| `surface-muted` | `#F4F4F1` | Secondary panels and inactive regions |
| `surface-raised` | `#FFFFFF` | Menus, dialogs, floating panels |
| `surface-inset` | `#F1F1EE` | Recessed inputs, code frames, wells |
| `border` | `#E6E4DE` | Default border |
| `border-strong` | `#D4D0C7` | Hover, focus-adjacent, emphasized structure |
| `border-subtle` | `#EFEEE9` | Dividers and low-emphasis lines |
| `text-primary` | `#111111` | Main text |
| `text-secondary` | `#55524C` | Body copy, descriptions |
| `text-muted` | `#8A867C` | Hints, timestamps, placeholders |
| `text-disabled` | `#AAA69C` | Disabled text |
| `text-inverse` | `#FFFFFF` | Text on dark fills |
| `primary` | `#111111` | Main CTA fill in light mode |
| `primary-hover` | `#2A2A2A` | Primary hover or pressed variant |
| `primary-active` | `#000000` | Primary active variant |
| `accent` | `#635BFF` | Links, focus, selected states, key metrics |
| `accent-hover` | `#574FE8` | Accent hover |
| `accent-soft` | `#EFEEFF` | Accent background |
| `accent-strong` | `#4F46E5` | High-emphasis accent text or icon |
| `success` | `#16A34A` | Positive state |
| `success-soft` | `#DCFCE7` | Positive background |
| `warning` | `#F59E0B` | Warning state |
| `warning-soft` | `#FEF3C7` | Warning background |
| `danger` | `#DC2626` | Error or destructive state |
| `danger-soft` | `#FEE2E2` | Error background |
| `info` | `#0284C7` | Informational state |
| `info-soft` | `#E0F2FE` | Informational background |
| `code-bg` | `#0B0D10` | Technical surface background |
| `code-border` | `#24272E` | Technical surface border |
| `code-text` | `#F7F7F5` | Technical surface text |

### Dark theme tokens

| Token | Value | Role |
|---|---:|---|
| `background` | `#08090A` | Main page canvas |
| `background-cool` | `#090B0F` | Optional cooler app canvas |
| `surface` | `#111214` | Cards and panels |
| `surface-muted` | `#181A1D` | Secondary panels |
| `surface-raised` | `#1D1F23` | Floating panels and dialogs |
| `surface-inset` | `#0D0F12` | Recessed inputs, code frames, wells |
| `border` | `#2A2D33` | Default border |
| `border-strong` | `#3A3F47` | Stronger border |
| `border-subtle` | `#202329` | Dividers and low-emphasis lines |
| `text-primary` | `#F7F7F5` | Main text |
| `text-secondary` | `#B7B8BC` | Body copy |
| `text-muted` | `#7D828A` | Hints and metadata |
| `text-disabled` | `#5F656E` | Disabled text |
| `text-inverse` | `#111111` | Text on light fills |
| `primary` | `#FFFFFF` | Main CTA fill in dark mode |
| `primary-hover` | `#EDEDED` | Primary hover variant |
| `primary-active` | `#DADADA` | Primary active variant |
| `accent` | `#8B7CFF` | Links, focus, selected states |
| `accent-hover` | `#A799FF` | Accent hover |
| `accent-soft` | `#1D1A3D` | Accent background |
| `accent-strong` | `#A799FF` | High-emphasis accent text or icon |
| `success` | `#22C55E` | Positive state |
| `success-soft` | `#0F2E1A` | Positive background |
| `warning` | `#FBBF24` | Warning state |
| `warning-soft` | `#3A2A0A` | Warning background |
| `danger` | `#F87171` | Error or destructive state |
| `danger-soft` | `#3A1212` | Error background |
| `info` | `#38BDF8` | Informational state |
| `info-soft` | `#082F49` | Informational background |
| `code-bg` | `#0B0D10` | Technical surface background |
| `code-border` | `#24272E` | Technical surface border |
| `code-text` | `#F7F7F5` | Technical surface text |

### Gradient tokens

Use gradients sparingly for hero moments, onboarding, important empty states, and signature AI/product moments.

| Token | Direction | Stops | Usage |
|---|---|---|---|
| `gradient-primary` | 135 degrees | `#635BFF 0%`, `#8B5CF6 45%`, `#06B6D4 100%` | Premium CTA, hero glow |
| `gradient-cool` | 135 degrees | `#06B6D4 0%`, `#635BFF 55%`, `#111827 100%` | AI/productivity visual |
| `gradient-warm` | 135 degrees | `#FF7A59 0%`, `#F59E0B 50%`, `#FDE68A 100%` | Announcement, warm highlight |
| `gradient-subtle-light` | radial blend | indigo at top-left, cyan at top-right, both low opacity | Light page atmosphere |
| `gradient-subtle-dark` | radial blend | violet at top-left, cyan at top-right, both low opacity | Dark page atmosphere |
| `gradient-mesh-soft` | radial blend | indigo, cyan, and warm amber at very low opacity | Large marketing hero only |

### AI status colors

These are for AI tool/status visualization only. Do not use them as general brand colors.

| Status | Token | Color | Use |
|---|---|---:|---|
| Thinking | `ai-thinking` | `#D8C6FF` | Assistant planning or thinking state |
| Searching | `ai-searching` | `#BDEBFF` | Web or file search state |
| Reading | `ai-reading` | `#C7E9D0` | Reading documents or context |
| Running | `ai-running` | `#FFE3B0` | Tool, automation, or code execution |
| Writing | `ai-writing` | `#FFD0E1` | Generating content |
| Done | `ai-done` | `#DCFCE7` | Completed action |

### Color rules

- Use neutral colors for 80-90% of the interface.
- Use `accent` for selected states, focus, inline links, and key metrics.
- Use `primary` for primary CTAs, not every highlighted element.
- Use gradients only for hero, onboarding, empty states, and signature AI moments.
- Status colors must never be decorative.
- Do not use more than one saturated accent in the same component unless it is a data visualization or AI status timeline.
- In dark mode, prioritize surface separation and text contrast over saturation.

---

## 5. Typography System

### Typeface guidance

| Role | Preferred quality | Fallback rule |
|---|---|---|
| Display | Modern, confident, slightly condensed rhythm | Use the product brand font or platform default heading style. |
| Body | Highly readable neutral sans | Use the platform default sans if no brand font exists. |
| Mono | Clear technical monospace | Use the platform default monospace for code, IDs, logs, and commands. |

Do not require a downloadable font package. Typography should work with brand fonts, system fonts, or design-tool text styles.

### Typography personality

- Display type is confident, tight, and modern.
- Body text is readable, calm, and relaxed.
- Labels are compact and medium-weight.
- Monospace is reserved for code, IDs, shortcuts, logs, terminal output, technical metadata, and short technical eyebrows.
- Use tabular numerals for metrics, prices, counts, percentages, timestamps, and table numeric cells.

### Type scale

Use these values as visual targets. Translate units to the host platform, such as px, rem, sp, pt, dp, or design-tool styles.

| Token | Size | Line Height | Weight | Letter Spacing | Usage |
|---|---:|---:|---:|---:|---|
| `display-xl` | `72` | `1.00` | `700` | `-0.055em` | Large marketing hero |
| `display-lg` | `56` | `1.04` | `700` | `-0.050em` | Standard hero |
| `display-md` | `44` | `1.08` | `650` | `-0.045em` | Page headline |
| `heading-xl` | `36` | `1.12` | `650` | `-0.035em` | Section headline |
| `heading-lg` | `28` | `1.18` | `650` | `-0.030em` | Major panel title |
| `heading-md` | `22` | `1.25` | `600` | `-0.020em` | Card title |
| `heading-sm` | `18` | `1.35` | `600` | `-0.010em` | Small section title |
| `body-lg` | `18` | `1.65` | `400` | `-0.010em` | Hero supporting copy |
| `body-md` | `16` | `1.60` | `400` | `-0.005em` | Default body |
| `body-sm` | `14` | `1.55` | `400` | `0` | Secondary copy |
| `label-md` | `13` | `1.25` | `600` | `-0.005em` | Buttons, tabs |
| `label-sm` | `12` | `1.20` | `600` | `0` | Badges, metadata |
| `caption` | `11` | `1.20` | `500` | `0` | Fine metadata |
| `mono-sm` | `13` | `1.55` | `400` | `0` | Code, logs, CLI |
| `mono-xs` | `12` | `1.40` | `500` | `0.04em` | Technical labels |

### Text width rules

| Content | Max width target |
|---|---:|
| Hero headline | `920` |
| Hero supporting copy | `720` |
| Article content | `760` |
| Form descriptions | `540` |
| Card copy | `420` |
| Toast copy | `360` |

### Typography rules

- Keep hero headlines under 12 words.
- Use sentence case for most UI text.
- Use uppercase only for short labels, badges, or technical metadata.
- Do not use font weights below `400` unless a brand mode explicitly asks for editorial thin display.
- Do not center-align long paragraphs.
- Avoid mixing more than two type families in one product.

---

## 6. Layout System

### Responsive/adaptive model

The system supports both breakpoint-based layouts and platform-native adaptive layouts. Use the values below as design targets, not framework requirements.

| Size class | Width range | Columns | Gutter | Outer margin |
|---|---:|---:|---:|---:|
| Compact | `< 640` | 4 | `16` | `20` |
| Medium | `640-1023` | 8 | `24` | `32` |
| Expanded | `1024-1439` | 12 | `28` | `48` |
| Wide | `1440+` | 12 | `32` | `80` |

### Container width targets

| Token | Width | Usage |
|---|---:|---|
| `container-sm` | `720` | Forms, auth, narrow content |
| `container-md` | `960` | Docs, settings, simple pages |
| `container-lg` | `1180` | Marketing sections |
| `container-xl` | `1320` | Dashboards, data-heavy layouts |
| `container-full` | `100%` | App shell and native full-screen views |

### Spacing scale

Use an 8-unit base scale with occasional 4-unit micro spacing. Translate the unit to the host platform.

| Token | Value |
|---|---:|
| `space-0` | `0` |
| `space-1` | `4` |
| `space-2` | `8` |
| `space-3` | `12` |
| `space-4` | `16` |
| `space-5` | `20` |
| `space-6` | `24` |
| `space-8` | `32` |
| `space-10` | `40` |
| `space-12` | `48` |
| `space-16` | `64` |
| `space-20` | `80` |
| `space-24` | `96` |
| `space-32` | `128` |

### Spacing relationships

| Relationship | Target |
|---|---:|
| Label to field | `6-8` |
| Field to helper/error text | `6-8` |
| Icon to label | `8` |
| Button group gap | `8-12` |
| Form field group | `16-24` |
| Card internal padding | `20-28` |
| Section internal padding | `48-80` |
| Major section gap | `80-128` |

### Layout rules

- Use generous vertical spacing between major sections: `80-128`.
- Use compact spacing inside functional app panels: `12-24`.
- Align content to a strong left edge unless the layout is a marketing hero.
- Favor asymmetric layouts for landing pages.
- Favor strict alignment for dashboards and settings.
- Use cards to group decisions, not to decorate every block.
- Keep primary content visually dominant and secondary controls quiet.
- On small screens, stack content intentionally and keep primary actions visible.

---

## 7. Shape, Borders, and Elevation

### Radius scale

| Token | Value | Usage |
|---|---:|---|
| `radius-xs` | `4` | Small tags, code pills |
| `radius-sm` | `6` | Inputs, compact buttons |
| `radius-md` | `10` | Default controls |
| `radius-lg` | `14` | Cards |
| `radius-xl` | `20` | Feature panels |
| `radius-2xl` | `28` | Hero media, large containers |
| `radius-full` | `999` | Pills, avatars, round controls |

### Border rules

- Default border width: `1`.
- Use borders instead of heavy shadows for structure.
- In dark mode, borders should be visible but low contrast.
- Interactive components should strengthen border color on hover, focus, or press.
- Avoid fully borderless cards unless the background contrast is obvious.

### Elevation scale

Treat the values below as visual targets. Native platforms may translate them into elevation, shadow layers, blur, or surface depth.

| Token | Visual value | Usage |
|---|---|---|
| `shadow-xs` | subtle 1-2 unit shadow | Buttons, small controls |
| `shadow-sm` | soft 4-12 unit shadow | Cards |
| `shadow-md` | clear 12-32 unit shadow | Popovers, menus |
| `shadow-lg` | broad 24-80 unit shadow | Modals, hero visuals |
| `shadow-stack` | layered low + medium shadow | Premium product mockups |
| `shadow-glow` | soft accent glow around 48-56 units | Signature AI or hero accent only |

### Elevation rules

- Flat surfaces should use borders.
- Raised surfaces should use both border and shadow or platform-native depth.
- Modals should dim the page with a soft overlay.
- Glows should be rare and tied to brand or AI moments.
- Avoid neumorphism, heavy glassmorphism, and harsh shadows.

---

## 8. Component System

All component specs are platform-neutral. Use the host project's existing primitives and adapt them to these states, sizes, and behaviors.

### 8.1 Buttons

#### Variants

| Variant | Role | Fill | Text | Border | Typical height | Horizontal padding |
|---|---|---|---|---|---:|---:|
| Primary | Main action | `primary` | `text-inverse` | `primary` | `40` | `16` |
| Secondary | Supporting action | `surface` | `text-primary` | `border` | `40` | `16` |
| Ghost | Toolbar or low emphasis | transparent | `text-secondary` | transparent | `36` | `12` |
| Destructive | Irreversible action | `danger` | white or inverse | `danger` | `40` | `16` |
| Icon | Compact icon action | surface or transparent | inherited | border or transparent | `36-40` | square |

#### Button behavior

- Hover or pointer-over: increase surface contrast subtly.
- Pressed or active: reduce scale or elevation slightly without layout shift.
- Focus: show a visible accent ring or platform-native focus indicator.
- Disabled: reduce opacity and remove elevation; keep label readable.
- Loading: keep button width stable and show progress indicator.
- Destructive: pair with clear copy and confirmation when irreversible.

#### Button copy

Use specific verbs:

- Create project
- Invite teammate
- Save changes
- Connect account
- Export report
- Start analysis

Avoid vague labels such as Submit, OK, Click here, or Continue when the destination is unclear.

### 8.2 Cards and Surfaces

| Surface | Background | Border | Radius | Padding | Elevation | Usage |
|---|---|---|---|---:|---|---|
| Default card | `surface` | `border` | `radius-lg` | `24` | `shadow-xs` | Grouped content |
| Feature card | subtle surface blend | `border` | `radius-xl` | `28` | none or `shadow-xs` | Marketing/product feature |
| Interactive card | `surface` | `border` to `border-strong` | `radius-lg` | `20-24` | hover to `shadow-sm` | Selectable item |
| Raised panel | `surface-raised` | `border` | `radius-xl` | `24` | `shadow-md` | Popover, drawer, modal inner panel |
| Inset surface | `surface-inset` | `border-subtle` | `radius-md` | `12-16` | none | Code, preview, input well |

Rules:

- Card title should appear before supporting copy.
- Place primary card action at the bottom or top-right.
- Do not nest more than one card level deep.
- Avoid using cards for every line item; use lists or tables instead.
- Interactive cards should move no more than `2` units on hover or press.

### 8.3 Inputs and Forms

| Element | Target spec |
|---|---|
| Text input height | `40` |
| Text input radius | `radius-md` |
| Text input horizontal padding | `12` |
| Textarea min height | `112` |
| Label placement | Above field |
| Helper/error placement | Below field |
| Focus treatment | Accent ring or visible focused border |
| Error treatment | Danger border plus specific error copy |
| Disabled treatment | Muted surface and readable disabled text |

Form rules:

- Labels must be visible, not placeholder-only.
- Helper text should explain why the input matters or what format is expected.
- Error copy must be specific and human.
- Required indicators should be subtle.
- Group related fields in sections or cards.
- Disable save only when the reason is clear.

### 8.4 Navigation

#### Top navigation

| Property | Target |
|---|---|
| Height | `64` on desktop, `56` on compact screens |
| Background | mostly `background` or `surface`, optionally translucent if platform supports it |
| Border | bottom `border` |
| Layout | logo left, nav center or left, actions right |

Rules:

- Keep nav item labels short.
- Use one clear header action.
- Sticky navigation is optional and should be used only when helpful.
- On compact screens, convert to drawer, sheet, menu, or platform-native navigation.

#### Sidebar navigation

| Property | Target |
|---|---|
| Width | `240-280` |
| Background | `surface` |
| Border | right `border` |
| Padding | `16` |
| Item height | `36` |
| Item radius | `radius-md` |

Active item:

- Background: `accent-soft`
- Text/icon: `accent-strong`
- Use only one active style per nav group.

Rules:

- Keep sidebar groups short.
- Use simple line icons at `16-20` units when useful.
- Collapse to rail or drawer on smaller screens.
- Current location must be obvious.

### 8.5 Badges and Pills

| Property | Target |
|---|---|
| Height | `24` |
| Padding | `0 8` equivalent |
| Radius | `radius-full` |
| Text | `label-sm` |
| Border | `border` |
| Background | `surface-muted` |
| Text color | `text-secondary` |

Variants:

- Success: `success-soft` background, `success` text.
- Warning: `warning-soft` background, `warning` text.
- Danger: `danger-soft` background, `danger` text.
- Accent: `accent-soft` background, `accent-strong` text.

Rules:

- Badges should be short: 1-3 words.
- Never use badges as buttons unless the interaction is visually clear.
- Use icons only when they clarify meaning.

### 8.6 Tables and Lists

Tables should feel precise, quiet, and scannable.

| Element | Target |
|---|---|
| Default text | `body-sm` |
| Header text | muted `label-sm`, uppercase optional |
| Row height | `48-56` |
| Dividers | bottom borders only |
| Numeric alignment | right |
| Text alignment | left |
| Hover/selection | subtle surface change |

Rules:

- Use tabular numerals for metrics.
- Use direct labels when possible.
- Keep bulk actions sticky or clearly visible.
- Show empty, loading, and error states.
- Mobile tables need a designed behavior: horizontal scroll with affordance, stacked cards, summary rows, or column priority.

### 8.7 Dialogs, Modals, Drawers, and Sheets

| Element | Target |
|---|---|
| Surface | `surface-raised` |
| Border | `border` |
| Radius | `radius-xl` |
| Max width | `560` for focused dialogs |
| Padding | `24` |
| Elevation | `shadow-lg` or platform modal depth |
| Overlay | dim background, optional soft blur if supported |

Rules:

- Title first.
- One clear primary action.
- Secondary action should usually be cancel or close.
- Destructive dialogs require explicit consequence copy.
- Focus must be trapped in modal experiences where the platform supports it.
- Escape, back, or outside-click behavior must be defined.
- Long multi-step flows should use pages, drawers, or wizards, not small modals.

### 8.8 Toasts and Inline Alerts

#### Toast

| Property | Target |
|---|---|
| Surface | `surface-raised` |
| Border | `border` |
| Radius | `radius-lg` |
| Padding | `12-14` |
| Elevation | `shadow-md` |
| Max copy length | about 90 characters |

Rules:

- Auto-dismiss success toasts.
- Keep error toasts visible long enough to read and act.
- Include an action only when it is useful.
- Toasts must not block critical controls.

#### Inline alert

Use alerts for contextual feedback inside a page or form.

| Variant | Background | Text/icon | Use |
|---|---|---|---|
| Neutral | `surface-muted` | `text-secondary` | General information |
| Info | `info-soft` | `info` | Helpful note |
| Success | `success-soft` | `success` | Positive confirmation |
| Warning | `warning-soft` | `warning` | Risk or incomplete setup |
| Danger | `danger-soft` | `danger` | Error or destructive warning |

### 8.9 Empty States

Empty states should guide action, not just announce absence.

Structure:

1. Small icon, illustration, or product-like visual
2. Clear headline
3. One-sentence explanation
4. Primary action
5. Optional secondary link

Rules:

- Keep the tone helpful, never apologetic.
- Use subtle accent gradient only for important empty states.
- Avoid large decorative illustrations in dense apps.
- Empty states should answer what is missing, why it matters, and what to do next.

### 8.10 Code Blocks and Technical Surfaces

Technical surfaces should be clear and developer-friendly across platforms.

| Property | Target |
|---|---|
| Background | `code-bg` |
| Text | `code-text` |
| Border | `code-border` |
| Radius | `radius-lg` |
| Text style | `mono-sm` |
| Padding | `16` |
| Line height | `1.55-1.65` |

Rules:

- Include a copy action when the platform supports it.
- Keep command snippets compact.
- Use syntax highlighting with muted, accessible colors.
- Use terminal-style blocks for CLI instructions.
- Do not overuse code visuals on non-technical pages.

---

## 9. Motion and Interaction

### Timing tokens

| Token | Duration | Usage |
|---|---:|---|
| `motion-fast` | `100ms` | Button press, small hover |
| `motion-base` | `160ms` | Default hover, focus, selection |
| `motion-slow` | `240ms` | Panels, dropdowns, sheets |
| `motion-page` | `360ms` | Page or hero transitions |

### Easing feel

| Token | Feel | Usage |
|---|---|---|
| `ease-standard` | quick start, smooth settle | default interaction |
| `ease-out` | natural deceleration | entrances, sheets, popovers |
| `ease-in-out` | symmetrical movement | mode changes, page transitions |

### Motion rules

- Hover or press movement should not exceed `2-4` units.
- Prefer opacity and transform-like movement over layout-changing animation.
- Respect reduced-motion preferences or platform accessibility settings.
- Animate entrances only when they clarify hierarchy.
- Do not animate every element on page load.
- Never rely on motion as the only explanation of a state change.

---

## 10. Iconography and Illustration

### Icons

- Use simple line icons.
- Stroke width target: `1.75-2` units.
- Default size: `16` in controls, `20` in cards, `24` in feature sections.
- Icons should inherit text color unless they communicate status.
- Avoid mixing icon families.
- Do not require a specific icon library.

### Illustrations

Preferred:

- Product screenshots or UI fragments.
- Abstract but functional diagrams.
- Soft gradients used sparingly.
- Geometric forms.
- Lightweight 3D only for hero or marketing moments.

Avoid:

- Generic cartoon people.
- Overly playful mascots unless brand-specific.
- Complex illustrations that compete with the interface.
- AI-generated blobs behind every section.

---

## 11. Data Visualization

Charts should be clear, not decorative.

### Chart color sequence

| Order | Color |
|---:|---:|
| 1 | `#635BFF` |
| 2 | `#06B6D4` |
| 3 | `#16A34A` |
| 4 | `#F59E0B` |
| 5 | `#DC2626` |
| 6 | `#8B5CF6` |
| 7 | `#64748B` |

### Data visualization rules

- Use direct labels when possible.
- Keep gridlines very subtle.
- Use tabular numerals.
- Avoid 3D charts.
- Avoid rainbow palettes.
- Highlight the key series and mute the rest.
- Always include units.
- Design empty, loading, and error chart states.
- Do not use chart colors as general UI accents.

---

## 12. Accessibility

### Contrast

- Text must meet WCAG AA or the platform's equivalent accessibility standard.
- Do not rely on color alone for state.
- Focus states must be visible.
- Disabled states must remain readable enough to understand.

### Keyboard and non-pointer input

- Every interactive element must be reachable by keyboard or platform equivalent.
- Focus order must match visual order.
- Escape, back, or cancel actions should close modal surfaces where appropriate.
- Enter, Space, tap, click, or equivalent activation must work consistently.

### Assistive technology

- Use semantic platform controls before custom controls.
- Provide accessible names for icon-only actions.
- Announce async feedback where the platform supports live regions or equivalent mechanisms.
- Associate labels and errors with form controls.
- Maintain logical heading order.

### Touch and pointer

- Minimum touch target: `44` units.
- Do not rely on hover-only controls for essential actions.
- Increase spacing between tappable items on compact screens.

### Reduced motion

When reduced motion is requested:

- Remove non-essential animation.
- Preserve instant state changes.
- Keep transitions extremely short if needed for orientation.
- Avoid parallax, large zooms, and continuous ambient movement.

---

## 13. Responsive and Adaptive Behavior

### Compact screens

- Stack multi-column layouts.
- Reduce hero display type to `40-48`.
- Collapse nav into drawer, sheet, menu, or platform-native navigation.
- Use bottom sheets or focused pages for filters and secondary workflows.
- Keep primary actions visible.
- Avoid horizontal scrolling except for tables with clear affordance.

### Medium screens

- Use 8-column or two-pane layouts.
- Sidebars may collapse to rails.
- Cards can use 2-column layouts.
- Dialogs and sheets should use nearly full width with safe margins.

### Expanded screens

- Use full 12-column layouts.
- Keep dashboards information-dense but calm.
- Make secondary panels sticky when useful.
- Avoid line lengths over `760`.

### Native platform adaptation

- Respect safe areas, system navigation, platform back behavior, and platform text scaling.
- Use platform-native controls when they better support accessibility and user expectations.
- Keep token roles and visual hierarchy consistent even when component implementation differs.

---

## 14. Content and Voice

### Voice principles

The product voice should be:

- Clear
- Calm
- Direct
- Helpful
- Slightly warm
- Never gimmicky

### UI copy rules

- Use verbs for actions.
- Prefer specific labels over generic ones.
- Explain errors in plain language.
- Avoid exclamation marks except for rare celebratory moments.
- Avoid vague labels like Submit, OK, or Proceed.
- Use realistic product copy in generated interfaces.

### Microcopy examples

| Context | Good copy |
|---|---|
| Empty project | Create your first project to start organizing work. |
| Loading | Preparing your workspace... |
| Save success | Changes saved. |
| Permission error | You do not have permission to edit this workspace. |
| Delete confirmation | This action permanently removes the project and its data. |
| Invite helper | They will receive an invitation with access instructions. |

### Error copy formula

Good errors explain:

1. What happened
2. Why, if known
3. What to do next

Example:

> We could not save your changes because the connection timed out. Check your connection and try again.

Avoid:

> Something went wrong.

---

## 15. Page Blueprints

### 15.1 SaaS Landing Page

Purpose: Convert visitors by clearly explaining what the product does, why it matters, and what action to take next.

Structure:

1. Sticky or simple top nav
2. Announcement pill
3. Hero headline
4. Supporting paragraph
5. Primary CTA and secondary CTA
6. Product screenshot, mockup, or interactive visual
7. Logo or social proof row
8. Feature grid
9. Workflow section
10. Use cases
11. Testimonials or proof
12. Pricing preview or final CTA
13. Footer

Rules:

- Hero should be visually dominant.
- Hero supporting copy max width: `720`.
- Use one subtle gradient background.
- Product visual should look real, not generic.
- Feature cards should be 2 or 3 columns on expanded screens.
- Compact layouts should stack cleanly.
- One primary CTA above the fold; one secondary CTA is allowed.

Prompt:

```md
Build a premium SaaS landing page using DESIGN.md. Implement it with the project's existing stack. Use a calm hero, one clear primary CTA, a polished product visual, feature cards, social proof, workflow explanation, and responsive behavior. Keep the design minimal, precise, and trustworthy.
```

### 15.2 AI Chat Interface

Purpose: Create a focused AI assistant experience that feels fast, trustworthy, and useful.

Structure:

1. App shell
2. Conversation or project navigation
3. Main chat area
4. Message list
5. Composer
6. Tool/status area
7. Optional context panel

Message rules:

- User messages are compact and clearly distinguished.
- Assistant messages are more spacious and support rich content.
- Messages may include Markdown-like text, code, tables, citations, tool output, and attachments when the platform supports them.
- Long conversations must remain navigable.

Composer rules:

- Keep composer easy to find.
- Support attachments and send action if relevant.
- Focus state must be obvious.
- Placeholder should be helpful, such as: Ask about your project, data, or workflow.

AI-specific states:

- Thinking
- Searching
- Reading files
- Running tools
- Generating output
- Tool error
- Partial result
- Citation available
- Unsafe or unavailable request

Prompt:

```md
Build an AI chat interface using DESIGN.md. Implement it with the project's existing stack. Include conversation navigation, polished message styles, a strong composer, tool status states, empty state, loading state, and compact-screen behavior.
```

### 15.3 Admin Dashboard

Purpose: Help users monitor, filter, inspect, and act on operational data.

Structure:

1. App navigation
2. Top bar with search, actions, and user menu
3. Page heading
4. Metric cards
5. Filter/search row
6. Main table or chart
7. Detail drawer, sheet, or side panel
8. Pagination and contextual bulk actions

Rules:

- Prioritize scanning.
- Keep actions close to affected data.
- Use consistent row heights.
- Avoid overusing cards.
- Make filters obvious and reversible.
- Bulk actions appear only when rows are selected.

Prompt:

```md
Build an admin dashboard using DESIGN.md. Implement it with the project's existing stack. Include navigation, top bar, metric cards, filters, precise data table, empty/loading/error states, and a responsive detail surface.
```

### 15.4 Pricing Page

Purpose: Help users compare plans and choose confidently.

Structure:

1. Page headline
2. Short value statement
3. Billing toggle if needed
4. Pricing cards
5. Feature comparison
6. FAQ
7. Final CTA

Rules:

- Highlight one recommended plan.
- Use clear price hierarchy.
- Keep feature bullets short.
- Use one CTA per plan.
- Avoid visually overwhelming the cheapest plan.
- Enterprise/custom plan should feel serious, not vague.

Prompt:

```md
Build a pricing page using DESIGN.md. Implement it with the project's existing stack. Include plan cards, one highlighted recommended plan, comparison table, FAQ, and final CTA. Keep copy clear and decision-focused.
```

### 15.5 Settings Page

Purpose: Let users configure account, workspace, billing, integrations, or preferences without confusion.

Structure:

1. Settings navigation
2. Page title and description
3. Grouped settings sections
4. Forms with labels and helper text
5. Save/cancel action region
6. Destructive zone, separated

Rules:

- Use sections instead of one giant form.
- Show saved/current state.
- Disable save until changes exist, or explain why saving is unavailable.
- Confirm destructive actions.
- Use helper text for complex settings.
- Keep dangerous actions visually separated.

Prompt:

```md
Build a settings page using DESIGN.md. Implement it with the project's existing stack. Include settings navigation, grouped sections, accessible forms, helper text, save/cancel behavior, and a clearly separated destructive zone.
```

### 15.6 Documentation Page

Purpose: Help users learn quickly and copy implementation details.

Structure:

1. Docs shell
2. Left navigation or index
3. Main article content
4. Optional table of contents
5. Code blocks
6. Callouts
7. Previous/next navigation

Rules:

- Article max width: `760`.
- Code blocks should include copy actions when supported.
- Use callouts sparingly.
- Keep headings descriptive.
- Provide runnable or realistic examples when possible.
- Keep docs visually quieter than marketing pages.

Prompt:

```md
Build a documentation page using DESIGN.md. Implement it with the project's existing stack. Include docs navigation, article content, table of contents, code blocks with copy actions, callouts, and previous/next links.
```

### 15.7 Mobile or Compact App

Purpose: Provide a touch-friendly version of the product without losing core functionality.

Structure:

1. Top app bar or compact header
2. Main content stack
3. Primary action
4. Bottom navigation, drawer, or platform-native navigation
5. Sheets or focused screens for secondary workflows

Rules:

- Minimum tap target: `44`.
- Use bottom sheets or focused screens for complex controls.
- Avoid tiny icon-only actions.
- Keep filters collapsed but discoverable.
- Use sticky primary actions when needed.
- Test with long content and narrow screens.

Prompt:

```md
Build a compact/mobile-first experience using DESIGN.md. Implement it with the project's existing stack. Use touch-friendly controls, stacked layout, platform-appropriate navigation, secondary workflow surfaces, and clear empty/loading/error states.
```

### 15.8 Auth Flow

Purpose: Help users sign in, sign up, recover access, or join a workspace with minimal friction.

Structure:

1. Logo or product mark
2. Short headline
3. Auth provider actions if relevant
4. Divider when mixing auth methods
5. Email/password or magic-link form
6. Error/helper text
7. Legal and support links

Rules:

- Keep auth pages quiet.
- Avoid unnecessary marketing content.
- Show exact errors.
- Support keyboard or platform equivalent submission.
- Make provider buttons visually consistent.
- Use secure, reassuring copy.

Prompt:

```md
Build an auth page using DESIGN.md. Implement it with the project's existing stack. Include logo, clear headline, provider actions if relevant, email form, accessible errors, legal links, and responsive behavior.
```

---

## 16. Product-Specific Pattern Library

### Feature card pattern

```md
[Icon]
Feature title
One-sentence benefit-oriented description.
Optional link or small action.
```

Rules:

- Title should be 2-5 words.
- Description should be one sentence.
- Icon should be subtle.
- Avoid equal visual weight for every card if one feature is primary.

### Metric card pattern

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

### Settings section pattern

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

### Command palette pattern

```md
Search input
Recent actions
Suggested navigation
Available commands
```

Rules:

- Use keyboard shortcuts where the platform supports them.
- Highlight matched text.
- Keep command names action-oriented.

### Product evidence pattern

Use when the page must prove the product is real.

Structure:

1. Framed product screenshot or UI fragment
2. One clear workflow moment
3. Minimal chrome
4. A few realistic labels or metrics
5. No fake clutter

Rules:

- Product visuals should support the value proposition.
- Data must look plausible and contextual.
- Avoid generic dashboards with random cards.

### AI tool timeline pattern

Use when showing AI work, automation, or agent activity.

Structure:

1. User request or trigger
2. Status sequence with AI status colors
3. Tool or source labels
4. Partial result preview
5. Final result and next action

Rules:

- Make progress legible.
- Distinguish thinking, searching, reading, running, writing, and done states.
- Show provenance when available.
- Avoid fake chain-of-thought; show user-safe progress summaries only.

---

## 17. Platform-Agnostic Implementation Guidance

### Token translation

Translate design tokens into the project's existing system.

| Design token category | Can become in a project |
|---|---|
| Color tokens | theme values, native color resources, constants, design-tool variables |
| Type tokens | text styles, typography scale, native text appearances, theme definitions |
| Spacing tokens | layout constants, sizing resources, grid variables, design-tool spacing styles |
| Radius tokens | shape styles, corner radius constants, component defaults |
| Elevation tokens | shadow styles, native elevation values, layered surface styles |
| Motion tokens | animation constants, transition presets, platform motion specs |
| Component specs | local components, design-tool components, native views, existing UI kit variants |

### Component primitive mapping

Map these generic primitives to whatever the project already uses.

| Generic primitive | Required behavior |
|---|---|
| Action | Button-like element with clear variants, states, focus, disabled, loading |
| Text field | Labeled input with helper, error, focus, disabled states |
| Surface | Card/panel/sheet with tokenized background, border, radius, elevation |
| Navigation item | Active state, label, optional icon, accessible name |
| Dialog surface | Modal/focused surface with title, actions, focus management |
| List row | Scannable row with selection, hover/press, metadata support |
| Table | Structured data with labels, alignment, sorting/filter states if relevant |
| Badge | Short status or metadata signal with semantic variants |
| Toast/alert | Async or contextual feedback with status and recovery action when needed |
| Code surface | Technical content area with monospace text and copy action when supported |

### Dependency rule

- First use the project's existing primitives.
- If an equivalent primitive does not exist, create the smallest local primitive needed.
- Do not introduce a new UI library just to satisfy this design document.
- Do not introduce a new icon package just to match examples.
- Do not introduce a new styling framework just to use the tokens.
- Do not convert this guide into framework-specific code inside `DESIGN.md`.

### Agent implementation rule

When an AI agent generates UI from this file, it should say or infer:

> I will implement this using the project's existing stack and map DESIGN.md tokens into local theme, style, component, or resource primitives.

It should not say:

> I will use a specific framework, styling library, UI kit, or icon package.

unless the user or project files explicitly require that stack.

---

## 18. Agent Rules

### Source-of-truth rule

When generating UI:

- Do not invent new colors unless explicitly requested.
- Do not invent new shadows, radii, spacing scales, or typography scales unless explicitly requested.
- Use tokens in this file as the default design language.
- If a component needs a new variant, derive it from existing tokens.
- Prefer production-ready UI over decorative mockups.
- Prioritize accessibility, responsiveness, and realistic content.
- Use the host project's existing stack and component conventions.

### Agent workflow

An AI agent should:

1. Read this file before generating UI.
2. Identify page type or component type.
3. Inspect the existing project stack, if project files are available.
4. Select the closest matching blueprint or component rule.
5. Map tokens into the project's existing theme, styles, resources, or components.
6. Generate all important states.
7. Check compact, medium, and expanded layouts.
8. Avoid decorative complexity unless the page is marketing-oriented.
9. Use realistic copy instead of placeholder text.
10. Verify output against the quality checklist.

### Agent output must feel

- Complete, not partial.
- Intentional, not randomly styled.
- Product-specific, not template-like.
- Accessible by default.
- Responsive/adaptive without afterthought.
- Consistent across components.
- Easy for developers to maintain.
- Compatible with the existing project stack.

### Prompt templates

General UI:

```md
Use DESIGN.md as the design source of truth. Implement with this project's existing stack and primitives. Build a polished product interface with clean hierarchy, neutral surfaces, subtle borders, strong typography, restrained accent color, complete states, and responsive/adaptive behavior.
```

Landing page:

```md
Create a landing page following DESIGN.md. Implement with the existing project stack. Use a calm premium hero, clear primary CTA, product visual, soft gradient accent, feature cards, social proof, and responsive/adaptive layout.
```

Dashboard:

```md
Create a dashboard following DESIGN.md. Implement with the existing project stack. Use app navigation, precise table layout, metric cards, subtle borders, clear filters, complete states, and responsive/adaptive behavior.
```

Form:

```md
Create this form following DESIGN.md. Implement with the existing project stack. Use visible labels, helpful helper text, accessible error states, clear primary action, and a calm section-based layout.
```

Dark mode:

```md
Implement full light and dark theme support using DESIGN.md tokens. Use the existing project stack. Dark mode should feel native and designed, not like a simple inversion.
```

---

## 19. Anti-Patterns: Never Generate This

### Visual anti-patterns

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

### Content anti-patterns

Never use:

- Lorem ipsum.
- Generic hype such as Get started today everywhere.
- Submit when a specific verb is available.
- Click here.
- Error occurred.
- Something went wrong without recovery guidance.
- Fake testimonials unless they are clearly placeholder content.
- Vague empty states like No data.
- Placeholder metrics that look real without context.

### Layout anti-patterns

Never:

- Place primary and destructive actions next to each other without separation.
- Hide the only primary action below the fold.
- Use inconsistent horizontal padding between sections.
- Mix unrelated alignment systems on the same page.
- Make compact layouts by simply shrinking expanded layouts.
- Let tables overflow on compact screens without controls.
- Use modals for long multi-step workflows.
- Make every section full-width without content max width.

### Interaction anti-patterns

Never:

- Remove focus outlines without replacing them.
- Use hover-only controls for essential actions.
- Animate layout in a way that causes content jumps.
- Make loading states look broken.
- Trigger destructive actions instantly.
- Use disabled buttons without explaining why when context is unclear.

### Stack anti-patterns

Never:

- Add a new framework because this design guide mentioned a component.
- Add a new UI kit because an example pattern resembles one.
- Add a new styling framework to implement token names.
- Add a new icon library to match icon style.
- Generate code examples in `DESIGN.md` that only work in one stack.
- Rename the design system around a framework-specific vocabulary.

---

## 20. Component Acceptance Criteria

### Button

- [ ] Has default, hover or press, active, focus, disabled, and loading states.
- [ ] Uses the correct variant.
- [ ] Has an accessible name.
- [ ] Does not rely on icon alone unless labeled.
- [ ] Maintains minimum touch target on compact/touch screens.

### Card

- [ ] Has clear purpose.
- [ ] Uses consistent padding and radius.
- [ ] Does not contain unnecessary nested cards.
- [ ] Has responsive/adaptive behavior.
- [ ] Uses action placement consistently.

### Form field

- [ ] Has visible label.
- [ ] Has helper text when needed.
- [ ] Has error state.
- [ ] Error is associated with the field where the platform supports it.
- [ ] Required/optional status is clear.
- [ ] Input has visible focus state.

### Dialog

- [ ] Has title.
- [ ] Has clear primary and secondary actions.
- [ ] Focus behavior is defined.
- [ ] Escape/back/cancel behavior is defined.
- [ ] Destructive actions require explicit copy.
- [ ] Works on compact screens.

### Table

- [ ] Columns are clearly labeled.
- [ ] Numbers align right.
- [ ] Empty state exists.
- [ ] Loading state exists.
- [ ] Sorting/filtering is clear if available.
- [ ] Compact-screen behavior is designed.

### Navigation

- [ ] Current location is obvious.
- [ ] Navigation works on compact screens.
- [ ] Icon-only items have accessible labels or tooltips.
- [ ] Groups are not too long.
- [ ] Keyboard or platform equivalent navigation works.

### Toast

- [ ] Message is short.
- [ ] Status is clear.
- [ ] Error toasts remain visible long enough.
- [ ] Optional action is useful.
- [ ] Toast does not block critical UI.

---

## 21. Page Acceptance Criteria

### Universal

- [ ] Clear page title.
- [ ] Clear primary action.
- [ ] Responsive/adaptive layout.
- [ ] Loading state.
- [ ] Empty state.
- [ ] Error state.
- [ ] Accessible focus states.
- [ ] Realistic content.
- [ ] No visual token drift.
- [ ] Dark mode support when the product supports dark mode.
- [ ] No stack dependency introduced by the design guide.

### Landing page

- [ ] Hero explains product clearly.
- [ ] CTA is visible above the fold.
- [ ] Product visual feels real.
- [ ] Feature sections are scannable.
- [ ] Social proof is credible.
- [ ] Compact hero is not cramped.

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

### AI chat

- [ ] Empty state suggests useful prompts.
- [ ] Composer is easy to find.
- [ ] Tool/status states are visible.
- [ ] Messages support rich content where the platform supports it.
- [ ] Long conversations remain usable.
- [ ] Compact chat does not hide input.

---

## 22. Advanced Theming Guidance

### Brand flexibility

This design can adapt to different brand personalities while keeping the same system.

#### More enterprise

- Use less gradient.
- Increase border clarity.
- Reduce playful illustration.
- Use more structured layouts.
- Prefer blue or neutral accent.

#### More creator-friendly

- Use warmer surfaces.
- Add soft illustrations.
- Use slightly larger radius.
- Make empty states more expressive.
- Use more conversational copy.

#### More developer-oriented

- Use more monospace metadata.
- Show technical details clearly.
- Use denser tables and code blocks.
- Keep gradients minimal.
- Prioritize CLI/API examples.

#### More AI-native

- Add subtle glow to AI-active states.
- Use status chips for tool use.
- Show provenance/citations clearly.
- Design for partial/progressive results.
- Keep trust and transparency central.

### Accent swapping

The system supports changing the accent color if needed.

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

## 23. Design Review Rubric

Score generated UI from 1 to 5 in each category.

| Category | 1 | 3 | 5 |
|---|---|---|---|
| Visual hierarchy | Confusing | Mostly clear | Instantly clear |
| Token consistency | Random styles | Minor drift | Fully consistent |
| Accessibility | Poor | Basic | Strong |
| Responsiveness/adaptivity | Broken | Works | Thoughtful |
| Copy quality | Generic | Acceptable | Specific and useful |
| Component states | Missing | Partial | Complete |
| Product fit | Template-like | Somewhat relevant | Purpose-built |
| Polish | Rough | Decent | Premium |
| Stack independence | Introduces dependencies | Mostly portable | Fully stack-agnostic |

Minimum shipping bar: do not ship if any category scores below 3.

Target score: 4 or higher across all categories.

---

## 24. Good Examples

### Good hero section

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

### Good empty state

```md
No reports yet

Generate your first report to summarize activity, identify trends, and share updates with your team.

[Generate report]
```

Why it works:

- Explains what is missing.
- Explains why it matters.
- Provides a clear next step.

### Good error state

```md
Could not connect GitHub

The authorization window was closed before access was granted. Reopen GitHub and approve the connection to continue.

[Try again]
```

Why it works:

- Explains the problem.
- Explains likely cause.
- Gives recovery action.

### Good dashboard header

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

## 25. Bad Examples

### Bad hero

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

### Bad empty state

```md
No data.
```

Problems:

- No context.
- No next step.
- Feels broken.

### Bad error

```md
Something went wrong.
```

Problems:

- No cause.
- No recovery path.
- Creates user anxiety.

### Bad stack-specific instruction

```md
Build this only with a specific framework, a specific UI kit, a specific styling library, and a specific icon package.
```

Problems:

- Not portable.
- Forces dependencies the project may not need.
- Makes the design guide less reusable.
- Confuses design rules with implementation choices.

---

## 26. Final Agent Instruction

When using this document to generate UI, follow this priority order:

1. User's explicit request
2. Product/page purpose
3. Accessibility and usability
4. DESIGN.md tokens and rules
5. Existing project stack, components, and conventions
6. Platform conventions
7. Visual polish

Never sacrifice clarity for decoration.

Never sacrifice accessibility for aesthetics.

Never sacrifice consistency for novelty.

Never introduce a technology dependency just because this design guide describes a component, token, or pattern.

The best result should look like a real product built by a careful senior product designer and implementation engineer, while remaining fully portable across stacks.
