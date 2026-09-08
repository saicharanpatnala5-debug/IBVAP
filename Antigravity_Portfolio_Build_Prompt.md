# Prompt for Antigravity — Build This in Phases, Verify Each One

Paste this whole thing in. Do not generate everything in one pass — the scroll-driven
animation sections are the most failure-prone part of this build, and they need to be
verified working before you move on, not just written and assumed correct.

**General rule for this task: after every phase below, run the dev server, open the
browser console, and confirm there are zero errors AND the described behavior actually
happens when you scroll/hover/click. If something doesn't work, fix it before starting
the next phase. Report what is and isn't working after each phase — do not silently
skip a requirement or claim something is done if you haven't verified it renders.**

---

## Phase 0 — Setup (verify before continuing)

- Scaffold: React + Vite + TypeScript + Tailwind CSS.
- Install: `gsap`, `framer-motion`, `hls.js`, `react-router-dom`, `tailwindcss-animate`.
- Add Google Fonts: Inter (300–700), Instrument Serif (italic, 400).
- Set up the CSS custom properties, Tailwind color extensions, and the
  `.accent-gradient` utility class exactly as specified in the design system below.
- Force dark theme (no toggle): `body` gets `bg-bg text-text-primary`.

**Verify:** dev server runs, Tailwind classes using the custom colors (`bg-bg`,
`text-text-primary`, `bg-surface`, `text-muted`, `border-stroke`) actually apply.

```
--bg: 0 0% 4%;
--surface: 0 0% 8%;
--text: 0 0% 96%;
--muted: 0 0% 53%;
--stroke: 0 0% 12%;
--accent: 0 0% 96%;
```
Accent gradient: `linear-gradient(90deg, #89AACC 0%, #4E85BF 100%)`.

---

## Phase 1 — Loading Screen + Hero (no scroll animation yet)

Build:
- Full-screen loading overlay with the 000→100 counter (requestAnimationFrame,
  ~2700ms), rotating words ["Design","Create","Inspire"] every 900ms via
  Framer Motion AnimatePresence, and the progress bar with `.accent-gradient`.
- Hero section with the HLS background video (`https://stream.mux.com/Aa02T7oM1wH5Mk5EEVDYhbZ1ChcdhRsS2m1NYyx4Ua1g.m3u8`),
  floating pill navbar, name/role/description content, and the two CTA buttons.
- GSAP entrance timeline for `.name-reveal` and `.blur-in` (this is a simple
  on-mount timeline, not scroll-linked — it should be reliable).

**Verify:** video plays muted/looped in the background, loading screen transitions
into the hero, entrance animation plays once on load, nav pill scroll-shadow triggers
past `scrollY > 100`.

---

## Phase 2 — Selected Works + Journal (Framer Motion `whileInView` only)

Build the bento grid and journal list sections using **Framer Motion's `whileInView`**
(not GSAP ScrollTrigger) — this is simpler and more reliable for basic fade/slide-in
reveals.

**Verify:** cards fade/slide in the first time they scroll into view, hover states on
the bento cards work (scale, overlay, gradient-border pill label).

---

## Phase 3 — Explorations section (pinned parallax — THE part that failed before)

This is GSAP ScrollTrigger with pinning, which is the most likely place the previous
attempt broke. Before writing any code, follow this checklist — most failures come
from missing one of these:

1. Register the plugin once, before any `ScrollTrigger.create` call:
   `import { ScrollTrigger } from "gsap/ScrollTrigger"; gsap.registerPlugin(ScrollTrigger);`
2. Do DOM setup in `useLayoutEffect`, not `useEffect`.
3. Wrap all GSAP creation in `gsap.context(() => {...}, sectionRef)` and call
   `ctx.revert()` in the cleanup function. **This is required** — without it, React
   18 StrictMode's dev-mode mount→unmount→remount cycle leaves duplicate or dead
   triggers and the pin does nothing.
4. Check that **no ancestor** of the pinned section has `overflow: hidden`,
   `overflow: auto`, or a `transform` set. Any of these silently break pinning
   because they create a new containing block. Check the page root, any layout
   wrapper, and any `overflow-hidden` used elsewhere in the app.
5. Call `ScrollTrigger.refresh()` after the `window` `load` event — images and the
   Instrument Serif webfont loading late will shift section height and desync the
   pin's start/end points if you don't.
6. After building, actually scroll the page in the browser and confirm the center
   content visually stays pinned while the two columns move at different speeds.
   Check the console for GSAP warnings.

A working reference implementation of this exact pattern is attached
(`ScrollGallery.reference.tsx`) — adapt its structure, ref pattern, and cleanup logic
to this project's real content/images and design tokens. Don't just copy it verbatim;
make sure you understand why each part is there.

**If ScrollTrigger pinning still does not work after following the checklist above,
do not leave the section static and move on silently.** Fall back to a
`position: sticky` + `IntersectionObserver`-driven parallax instead, and tell me you
did so and why.

---

## Phase 4 — Stats + Contact/Footer

- Stats 3-column grid.
- Footer with the flipped/darkened HLS video background, GSAP marquee
  (`xPercent: -50`, duration 40, repeat -1, ease "none"), mailto CTA, and social
  links + "Available for projects" pulsing dot.

**Verify:** marquee scrolls continuously without a visible seam/jump at the loop
point, footer video plays.

---

## Phase 5 — Final pass

- Add smooth scroll nav (clicking "Home"/"Work"/"Resume" scrolls to the right
  section) and basic page-transition polish.
- Full scroll-through test from top to bottom, confirm every animation from Phases
  1–4 still works together (especially re-check Phase 3 after adding anything else
  to the layout, since new elements can reintroduce an `overflow`/`transform`
  ancestor that breaks the pin again).
- Report a final section-by-section status: what's fully working, what's partial,
  what (if anything) needed the sticky/IntersectionObserver fallback instead of
  GSAP pinning.

---

## Design System Reference

Fonts: Inter → `font-body`, Instrument Serif italic → `font-display`.

Custom animations (`index.css`):
- `@keyframes scroll-down` — translateY(-100%) → translateY(200%), 1.5s ease-in-out infinite
- `@keyframes role-fade-in` — opacity 0 + translateY(8px) → opacity 1 + translateY(0), 0.4s ease-out
- `@keyframes gradient-shift` — background-position 0% 50% → 100% 50% → 0% 50%, 6s ease infinite

(Full section-by-section content spec — copy, layout, exact classes — is in the
original build prompt; use that for content/styling details. This document only
governs build order and the scroll-animation verification process.)
