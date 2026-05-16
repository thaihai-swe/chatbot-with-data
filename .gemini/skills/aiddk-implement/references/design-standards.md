# 🎨 Anti-AI Slop: Design Engineering Standards

These standards are mandatory for all implementation tasks involving UI, UX, or Frontend architecture. They are designed to prevent the generic "AI-aesthetic" and ensure production-grade, human-centric design.

## 1. Typography: The Character Mandate
**Avoid generic, overused system fonts.**
- **Banned:** Inter, Roboto, Arial, Open Sans, Segoe UI.
- **Rules:** 
    - Always use a distinctive **Display Font** for headers (e.g., high-contrast serifs, geometric grotesques, or intentional monospaces).
    - Pair with a highly readable, characterful **Body Font**.
    - Use strict type scales (e.g., Major Third) to ensure mathematical harmony.

## 2. Color: The Cohesion Mandate
**Avoid generic gradients and "Magic" brand colors.**
- **Rules:**
    - Use **CSS Variables** (`--color-primary`, `--color-bg`, etc.) for all colors.
    - Prefer intentional, context-specific color palettes over standard "Blue/Purple" tech themes.
    - Implement **High-Contrast Accents** for interactive elements.
    - Use subtle textures (noise, grain, or mesh gradients) instead of flat hex colors.

## 3. Composition: The "Grid-Breaking" Mandate
**Avoid symmetric, centered layouts by default.**
- **Rules:**
    - Use **Asymmetry** to create focal points.
    - Implement **Layered Overlaps** (e.g., text overlapping images) to create depth.
    - Be generous with **Negative Space**. If it feels "airy," add more space.
    - Use **8px Grid** alignment strictly for all padding and margins.

## 4. Motion: The Micro-Interaction Mandate
**Avoid "Decorative" animations. Focus on "Interactive" motion.**
- **Rules:**
    - Use **Staggered Reveals** for lists and grids.
    - Implement **Hover States** that provide tactical feedback (e.g., scale-up + shadow shift).
    - Use **Bezier Easing** for all transitions (no linear animations).
    - Focus on **Scroll-Triggered** interactions to guide the user's eye.

## 5. Implementation Hygiene
- **No Inline Styles:** Use CSS Modules, Vanilla CSS, or the project's established styling library.
- **Component Primitives:** Use semantic HTML and ARIA labels. Accessible code is a design requirement.
- **Responsive-First:** Designs must be "fluid," not just "breakpoint-dependent." Use `clamp()` for font sizes and fluid spacing.
