# Global Aerosols Website — Full Site Audit

**Date:** 2026-09-18
**Scope:** Astro 6.4 static site (`output: 'static'`, Cloudflare Pages adapter), 94 page routes under `src/pages/**`, ~58 blog posts, deployed at `https://www.globalaerosols.com`.
**Method:** Read-only. No files were modified, fixed, or auto-corrected as part of this audit. Findings were gathered directly (infrastructure/config/dependencies) and via five parallel read-only sub-audits (on-page SEO, blog/structured data, performance/assets, accessibility, internal linking), cross-checked against the project's own `SEO CHECKLIST.txt` spec. All attribute/tag-presence counts were verified with whole-file, multiline-safe parsing — not line-based `grep` — per a known false-positive risk in this repo's `.astro` files (see Methodology Notes at the end).

---

## Executive Summary — Top 10 by impact

1. **Critical dependency vulnerability.** `npm audit` reports 14 vulnerabilities (1 critical, 12 high, 1 low) in the dependency tree, including a critical-range Astro advisory. Astro is 2 minor patches behind even on the installed major (6.4.2 → 6.4.8) and 2 majors behind latest (7.3.3).
2. **Three divergent layout components** (`src/layouts/Layout.astro`, `src/lc/layouts/Layout.astro`, `src/layouts/BlogLayout.astro`) produce inconsistent output depending on which of the 94 pages uses which: 62 pages render with **no `<main>` landmark**, and 63 of 94 pages never receive the sitewide Organization/Manufacturer JSON-LD that the other 29 get automatically.
3. **No functioning "skip to content" link exists anywhere on the site**, despite the project's own checklist requiring one. The one page that has a skip-link markup points to an `id` that doesn't exist.
4. **9 pages render with zero `<h1>`** (found independently by two separate audits), and **60 of 94 pages (64%) have a heading-hierarchy skip** (H1 straight to H3 via a "Guide Contents" box).
5. **~100 MB of dead-weight images ship on every production build** — backup folders, space-named directories, and stray files with zero references anywhere in the codebase, sitting in `public/` and copied verbatim into `dist/client/`.
6. **No real HTTP security headers.** `public/_headers` only sets cache-control rules; there is no `Content-Security-Policy`, `X-Frame-Options`, or `Strict-Transport-Security`, and the `X-Content-Type-Options` header the layouts *think* they're setting is a `<meta>` tag, which browsers ignore entirely for that header.
7. **No custom 404 page** — a mistyped URL or stale backlink hits Cloudflare's generic platform 404, not a branded page with navigation.
8. **Blog schema is structurally correct but incomplete sitewide**: 0 of 15 sampled posts include image width/height in their `BlogPosting` schema, and every post uses a text-initials avatar instead of a real author photo, undermining the E-E-A-T signal the checklist calls for.
9. **230 internal links are missing the mandatory trailing slash** (site is configured `trailingSlash: 'always'`), causing an avoidable redirect on every click — 90% trace to one reused "related articles" template, so it's a single-template fix.
10. **3 pages are true orphans** (zero inbound links from anywhere), **1 internal link is broken** (points to a page that doesn't exist), and **6 pages have a literal duplicated `" | Global Aerosols | Global Aerosols"` string baked into their `<title>`**.

No autofixes were applied. Everything below is diagnostic only.

---

## 1. Technical Infrastructure & Security

*(Verified directly — build config, dependency scan, HTTP headers, layouts, git history.)*

### Critical
- **`npm audit`: 14 vulnerabilities (1 critical, 12 high, 1 low)** in the full dependency tree. The critical/high items concentrate in build tooling pulled in by the Cloudflare adapter (`wrangler` → `miniflare`, `ws`, `undici`, `vite`) plus direct Astro advisories:
  - Astro: XSS via unescaped spread-attribute names (moderate, `<6.4.6`), incomplete fix for the same (moderate, `<7.0.6`), reflected XSS via View Transition animation properties (moderate, `<=7.0.9`), and a **Host-header SSRF in prerendered error-page fetch** (high, CVSS 7.5).
  - `ws`: memory-exhaustion DoS from tiny fragments (high).
  - `vite`: `server.fs.deny` bypass on Windows alternate paths (high) — notable since this is a Windows dev machine.
  - `undici`: 9 separate advisories (cache poisoning, cookie/CRLF injection, SSRF-adjacent proxy reuse) — all high.
  - Fix path exists for all 14 (`npm audit fix`), but per audit scope this was reported only, not applied.

### High
- **Package currency:** `astro` 6.4.2 installed (6.4.8 available in the same major, 7.3.3 is latest major); `@astrojs/cloudflare` 13.7.0 installed vs. 14.3.2 latest; `@astrojs/sitemap` 3.7.3 vs. 3.7.4; `lenis` 1.3.23 vs. 1.3.26.
- **Three layout components with materially different output**, confirmed by import-count grep across all 94 pages:

  | Layout file | Pages using it | Has `<main>`? | Sitewide Organization/Manufacturer JSON-LD? | Has (non-functional) `X-Content-Type-Options` meta? |
  |---|---|---|---|---|
  | `src/layouts/Layout.astro` | 62 | ❌ (`<div class="content-wrapper">` only) | ❌ | ✅ (present, but inert as a meta tag) |
  | `src/lc/layouts/Layout.astro` | 29 | ✅ | ✅ | ❌ (correctly omitted, since it never worked here either) |
  | `src/layouts/BlogLayout.astro` | 1 (`blog/index.astro`) | ❌ | ❌ | ✅ (inert) |

  Practical effect: two-thirds of the site lacks a semantic `<main>` region and the sitewide Manufacturer/Organization structured data; a whole ~200-line layout file (`BlogLayout.astro`) exists to serve exactly one page and has already drifted from its near-twin (`content-wrapper` padding 88px vs. 60px, different font stack).
- **`X-Content-Type-Options` is set as `<meta http-equiv="X-Content-Type-Options" content="nosniff">`** in `src/layouts/Layout.astro` and `BlogLayout.astro`. This header is **only honored by browsers when sent as a real HTTP response header** — the meta-tag form does nothing. Combined with finding below, the site currently ships this protection nowhere, on any page.
- **`public/_headers` sets only `Cache-Control` rules** (for `/_astro/*`, `/images/*`, fonts, icons). There is no `Content-Security-Policy`, `X-Frame-Options`, `Strict-Transport-Security`, or header-level `Referrer-Policy`/`X-Content-Type-Options` — despite the project's own `SEO CHECKLIST.txt` (lines 532–536) explicitly mandating all of these.
- **No `src/pages/404.astro`** and no `public/404.html`. Confirmed no Cloudflare Functions/`_routes.json` fallback either. Any unmatched route falls through to the platform's generic 404.

### Medium
- **`robots.txt` has no `Disallow` rules** — just `Allow: /` plus the sitemap reference. The sitemap integration's own filter (excluding `/admin/`, `/login/`, `/dashboard/`, `/cart/`, `/checkout/`, `/store/search/`) has no `robots.txt` backstop; sitemap omission does not equal noindex. (`login.astro` correctly sets `robots="noindex, nofollow"` itself, so it's not currently exposed — but this is the only page doing so, and it relies on that one page remembering to opt out.)
- **`middleware.ts`** rewrites `cdn.globalaerosols.com` URLs to relative paths in HTML responses when `import.meta.env.DEV` or the request host looks local. This is correctly scoped to dev/local and not a production concern, but it does mean every local/dev HTML response is fully buffered and re-serialized — noted for completeness, not a defect.

### Low / Info
- **Secrets hygiene is clean**: `.env`, `.env.production`, and `.dev.vars` are gitignored and confirmed **never committed** in git history.
- **Local-only clutter** (not shipped, not tracked by git — confirmed via `git status`): stray root files `can wrap3d aluminium` (32 KB), `canwrap 3d` (20 KB), `model pic.jpg` (576 KB), an empty `nul` artifact file, and a 211 MB local `scratch/` directory. Zero production impact; worth a local cleanup pass only.
- Sitemap (`dist/client/sitemap-0.xml`) contains 93 URLs against 94 page files — the one-URL gap is `login.astro`, which sets `export const prerender = false` (the site's only SSR route) and is correctly absent from both the static build and the sitemap.

---

## 2. On-Page SEO

*(94 pages audited for title/description/canonical/H1/schema coverage and content overlap.)*

### Critical
- **6 pages carry a literal duplicated brand suffix inside the `<title>` string itself** — `" | Global Aerosols | Global Aerosols"`: `aerosol-air-freshener-dispersion-and-odour-control.astro`, `aerosol-contact-cleaners.astro`, `aerosol-sunscreen-spray.astro`, `aerosol-vs-pump-spray-vs-trigger-spray-technical-comparison.astro`, `automotive-aerosol-products.astro`, `understanding-sds-tds-and-coa-for-aerosol-products.astro`.
- **9 pages render with no `<h1>` at all** — confirmed independently by both the on-page SEO and accessibility audits (see §5). The visible page title on each is coded as `<h2 class="hero-massive-title">`: `adhesives-and-sealants.astro`, `arts-and-crafts.astro`, `automotive.astro`, `cosmetics.astro`, `cosmetics-and-personal-care.astro`, `household-and-industrial-cleaners.astro`, `industrial.astro`, `paints-and-coatings.astro`, `pharmaceuticals-and-health-care.astro`.
- **Heading-hierarchy skip (H1 → H3, no H2) on 60 of 94 pages (64%)**, caused by a "Guide Contents" table-of-contents box coded as `<h3>` immediately after the H1. Affects the majority of long-form guide and blog-topic pages built on `src/layouts/Layout.astro`.

### High
- **`src/lc/layouts/Layout.astro` (29 pages) has no `schemaJson` prop at all** — it's not in the `Props` interface and never rendered. Pages on this layout (about, all `services/*`, category pillar pages) can *never* carry page-specific JSON-LD, only the baked-in Organization schema.
- **Homepage H1/H2 are inverted**: the real H1 (`src/lc/components/Hero.astro`) is a small decorative corner label, "Aerosol Consultants," while the dominant, keyword-relevant title "GLOBAL AEROSOLS" is coded as an H2.
- **Keyword-cannibalization risk across near-duplicate topic pages** (overlapping search intent, no clear differentiation):
  - `from-lab-to-commercial-launch.astro` vs. `from-lab-to-market.astro`
  - `aerosol-propellants-explained-lpg-vs-dme-vs-hfc-vs-n2-vs-co2.astro` vs. `propellant-influence-on-aerosol-performance.astro`
  - `aerosol-technology-and-formulations.astro` (blog hub page, 10 inbound links) vs. `formulations-and-technology.astro` (nav-linked pillar page) — near-identical, word-order-swapped title/slug
  - `hfo-1234ze-propellant-low-gwp-alternative.astro` vs. `compressed-air-duster-aerosols-hfo-alternatives-esd.astro` (partial chemistry overlap)

### Medium
- **Title length outside the ~50–60 char target on 62/92 pages (67%)**; several run 90–130 characters (e.g., `automotive-aerosol-products.astro` at 130 chars).
- **Meta description outside the ~150–160 char target on 59/92 pages (64%)**; several run 190–226 characters.
- **Homepage has no custom meta description** — it only passes a `title` prop and falls back to the generic layout default.
- **20 pages omit an explicit `canonical` prop**, relying on `Astro.url.href`. Assessed as **low functional risk**: because the site is `output: 'static'` with `trailingSlash: 'always'`, the canonical is resolved at build time with no query-string contamination possible — flagged for consistency, not because it's currently broken.
- `services/canwrap-3d-aluminium.astro` has its own independent H1→H3 heading skip (same "Guide Contents" pattern).

### Low / Info
- **No exact duplicate titles or descriptions** found across all 94 pages.
- `canwrap3d.astro` correctly issues a redirect to `/services/canwrap-3d/` rather than duplicating content — good practice.
- `how-aerosol-cans-are-manufatured.astro` has a permanent slug typo ("manufatured"); not worth breaking existing backlinks/indexing to fix now.
- `aerosol-can-corrosion-1.astro` doesn't label itself "Part 1" while `aerosol-can-corrosion-2.astro` does say "Part 2" — minor labeling inconsistency, not cannibalization (legitimately a two-part series).
- The valve/BOV/propellant long-tail cluster (6 related pages) and the two CanWrap 3D configurator pages (tinplate vs. aluminium) were checked and are legitimately differentiated — not duplicates.
- 62/94 pages (66%) already carry a rich per-page JSON-LD graph where the layout supports it (BlogPosting + FAQPage + BreadcrumbList + Person + Organization + WebPage).
- `robots` override is used correctly and exactly once (`login.astro`) — no accidental noindex elsewhere.

---

## 3. Blog Content, Structured Data & E-E-A-T

*(15-post representative sample from the 58-post blog corpus, spanning 2023–2026 publish dates; date-logic checks run across all 58 posts.)*

### Compliance snapshot

| Check | Result |
|---|---|
| `BlogPosting` schema present | 15/15 (100%) |
| `BlogPosting` schema **fully complete** (image w/h + `isPartOf: Blog`) | **0/15 (0%)** |
| `BreadcrumbList` schema + visible breadcrumb nav | 15/15 (100%) |
| `FAQPage` schema (of posts with an FAQ section) | 14/14 (100%) |
| Author box with credentials + LinkedIn link | 15/15 (100%) |
| Author box with a **real photo** (vs. text-initials avatar) | **0/15 (0%)** |
| Visible published + modified dates | 15/15 (100%) |
| External link `rel="noopener noreferrer"` correctness | 15/15 (100%) |
| External link count in the checklist's 3–5 band | 9/15 (60%) |
| Internal link count in a *literal* 3–5 band | 0/15 (0%) — but see note below |
| Images wrapped in `<figure>+<figcaption>` | 2/15 (13%) |
| `dateModified` earlier than `datePublished`, across all 58 posts | 0/58 — clean |
| Blog-index `publishDate` vs. schema `datePublished` mismatch, across all 58 posts | 0/58 — clean |

### Critical
- **No `BlogPosting.image` schema node anywhere in the sample includes `width`/`height`**, only a bare `url` — the checklist requires full `ImageObject` dimensions.

### High
- **No `Blog` entity (`@type: "Blog"`) exists anywhere in the codebase.** Where `isPartOf` appears at all, it's attached to a separate `WebPage` node, never to the `BlogPosting` itself — so the checklist's `isPartOf` requirement is never actually satisfied.
- **Every sampled post (2023 through 2026) uses a colored-circle text-initials avatar ("AK") instead of a real author photo** in the "About the Author" box — full credentials and a working LinkedIn link are present, but the photo requirement is unmet sitewide.
- **Internal-link volume looks compliant on paper but isn't in spirit**: raw counts run 14–24 links per post, but manual inspection shows only ~2–4 are genuinely woven into prose; the rest come from a repeated "Related Articles" block and dense link-dump paragraphs (e.g., one paragraph in `aerosol-valve-gasket-explained.astro` stuffs 7 links, duplicated by an 8-link list right after it).

### Medium
- **6 of 15 sampled posts fall outside the 3–5 external-link band** — most notably `aerosol-sunscreen-spray.astro`, which has exactly one external link (the standard author LinkedIn reference) and no FAQ section.
- **`dateModified` drifts from actual git history on at least 4 posts** — e.g., `aluminium-vs-tinplate-aerosol-cans.astro` and `how-contract-aerosol-filling-works.astro` both declare `dateModified: 2026-08-10`, but git shows both were edited again on `2026-08-28` (an image/alt-text migration commit) without the schema date being bumped.
- **Only 2 of 15 posts wrap images in `<figure>+<figcaption>`**; the other 13 use bare `<img>` (alt text itself is fine, captions are missing).
- **`meta.json` link-count fields undercount the live page by 2–4x** in all 4 spot-checked cases (e.g., one `meta.json` claims 9 total links where the shipped page has 33 `<a>` tags) — `wordCount`, FAQ count, and dates matched exactly in the same spot-checks, so only the link counters are unreliable.

### Low / Info
- TOC anchor `id`s sit on the wrapping `<section>` rather than the heading itself in 13/15 sampled posts, and there's no `scroll-margin-top` accounting for the fixed navbar — TOC clicks likely land headings partially under the sticky header (not visually confirmed).
- Newer posts increasingly use `target="_top"` on internal links where older posts don't — an inconsistency, not a checklist violation.
- Date logic is otherwise clean across the entire 58-post corpus: no post has a `dateModified` before its `datePublished`, and no post's schema date disagrees with the blog index.

---

## 4. Performance & Asset Optimization

### Critical
None found at the code level (see High for the closest analogues).

### High
1. **Six category pages hard-code a local, non-CDN, non-webp PNG hero image (700–900 KB each)**, with no `width`/`height`/`loading` attributes: `automotive.astro`, `arts-and-crafts.astro`, `household-and-industrial-cleaners.astro`, `industrial.astro`, `paints-and-coatings.astro`, `pharmaceuticals-and-health-care.astro`. These are plausible LCP-critical images being served in the heaviest possible format.
2. **14 near-identical "ProcessParallax" components each mark ~5 below-the-fold, scroll-revealed images `loading="eager"`** with no `width`/`height` — roughly 70 unnecessary eager loads spread across every category page that uses one of these components.
3. **The sitewide Navbar's "Formulations & Technology" mega-menu marks all ~9 dropdown images `loading="eager"`**, even though the menu is hidden (`opacity:0`, `visibility:hidden`) until hover/click — and since `Navbar.astro` renders on every page, this is 9 extra eager fetches on every single page load, sitewide. The other two mega-menus in the same file correctly use `loading="lazy"`.

### Medium
4. **~99.5 MB of fully orphaned image assets are deployed on every build**, confirmed to have zero references anywhere in `src/`:

   | Path | Size | Files |
   |---|---|---|
   | `public/original_backups/` | 31 MB | 69 |
   | `public/formulations and technology/` | 20 MB | 9 |
   | `public/images/Book images/` | 9.8 MB | 5 |
   | `public/Services/` | 4.0 MB | 2 |
   | `public/hero image/` | 404 KB | 4 |
   | `public/image r55.png`, `public/image x22.png` | 4.3 MB | 2 |

   All three space/mixed-case folders also produce non-clean URLs if ever linked. Recommend deleting all of the above — pure dead weight inflating repo size and Cloudflare Pages build/upload time.
5. **122 MB of additional PNG/JPG images over 100 KB live in `public/images/`** (210 files); 145 already have an unused `.webp` sibling sitting next to them — worth a pass to confirm which copy is actually served before removing either.
6. **The CDN-image-fallback rewrite script is duplicated verbatim** between `src/layouts/Layout.astro` and `src/layouts/BlogLayout.astro`, while the third layout (`src/lc/layouts/Layout.astro`, 29 pages) has no fallback at all. Code-quality item, not a functional bug.

### Low
7. **27.6% of all `<img>` tags sitewide (92 of 333) are missing `width`/`height`** — a CLS risk, concentrated in the ProcessParallax components above plus `Hero.astro`, `HorizontalParallax.astro`, `LifestyleShowcase.astro`, `Navbar.astro`.
8. **7.8% of `<img>` tags (26 of 333) have no explicit `loading` attribute**, falling back to browser-default eager behavior by omission rather than decision.
9. **Homepage ships 11 separate per-component `<script type="module">` tags** (vs. 5 on a services page, 3 on a blog post) — one per Astro component with an inline script block. GSAP itself is *not* duplicated (Vite correctly splits it into shared chunks, ~116 KB total), so this is a request-count concern, not a payload-duplication one.
10. The `setInterval(scanAndRewrite, 300)` polling fallback (used only when `MutationObserver` is unavailable) in the CDN-fallback script is a negligible footnote given near-universal `MutationObserver` support.

### Info — build spot-check

| Route | HTML | Referenced JS | Referenced CSS | `<img>` count |
|---|---|---|---|---|
| Home | 102.7 KB | 42.5 KB | 70.1 KB | 42 |
| `services/aerosol-cans` | 106.9 KB | 28.6 KB | 44.9 KB | 30 |
| Blog post (tilt-valve) | 87.3 KB | 23.9 KB | 39.4 KB | 22 |

Code-only weight (~215 KB on the homepage) is well within the checklist's 2–5 MB budget, but the homepage's discrete resource count (11 scripts + 4 stylesheets + 42 images + preconnects ≈ 62) already exceeds the checklist's own "<50 HTTP requests recommended" target (`SEO CHECKLIST.txt:549`) — before fonts, analytics, or CDN image requests are even counted. True total byte weight can't be fully confirmed locally since images are CDN-hosted, outside this repo.

---

## 5. Accessibility (WCAG 2.1 AA)

### Critical
1. **No functioning "Skip to main content" link exists anywhere on the site.** The *only* skip-link markup in the entire codebase is on one page (`aluminium-vs-tinplate-aerosol-cans.astro:184`, `href="#main-content"`), and no element anywhere in the codebase has `id="main-content"` — it's dead even on the one page that has it. *(WCAG 2.4.1 Bypass Blocks)*
2. **9 pages have zero `<h1>`** — the same 9 pages identified independently in §2 (`adhesives-and-sealants.astro`, `arts-and-crafts.astro`, `automotive.astro`, `cosmetics.astro`, `cosmetics-and-personal-care.astro`, `household-and-industrial-cleaners.astro`, `industrial.astro`, `paints-and-coatings.astro`, `pharmaceuticals-and-health-care.astro`). *(WCAG 1.3.1 / 2.4.6)*

### High
3. **Leftover/duplicated markup from a past content migration creates colliding landmark labels** on at least 8 pages — two `<nav aria-label="Breadcrumb">` regions on the same page, a redundant `<nav aria-label="Site Navigation">` duplicating the real Navbar, and malformed overlapping header/logo markup. Confirmed in `aluminium-vs-tinplate-aerosol-cans.astro`, `aerosol-sunscreen-spray.astro`, `aerosol-air-freshener-dispersion-and-odour-control.astro`, `aerosol-contact-cleaners.astro`, `aerosol-vs-pump-spray-vs-trigger-spray-technical-comparison.astro`, `automotive-aerosol-products.astro`, `propellant-influence-on-aerosol-performance.astro`, `understanding-sds-tds-and-coa-for-aerosol-products.astro`. *(WCAG 4.1.2 / 1.3.1)*
   - *(Note: this is the same set of pages flagged for the duplicated title-suffix bug in §2 — strongly suggests all 6–8 of these pages came through the same faulty content-import pass and would benefit from one shared cleanup.)*
4. **Contact form contrast failures on the dark panel**: idle floating label ≈2.67:1, typed input/textarea text ≈3.96:1 — both below the 4.5:1 minimum. *(WCAG 1.4.3, `src/lc/components/ContactFormVideo.astro`)*
5. **Contact form's submission status message has no `aria-live`/`role="alert"`** — screen-reader users get no notification after submitting, success or failure. *(WCAG 4.1.3, `ContactFormVideo.astro` line ~125 markup, ~683–717 JS)*

### Medium
6. **~49 long-form guide pages skip a heading level** via the same "Guide Contents" `<h3>` box flagged in §2 (WCAG framing: 1.3.1 / 2.4.6).
7. **The main site `<nav>` has no `aria-label`**, while the breadcrumb and table-of-contents navs on the same pages correctly do — with 2–3 nav landmarks typically present per page, the primary nav is the unlabeled outlier. *(WCAG 4.1.2 / 2.4.1)*
8. **Footer `.credit` text (`#475569`) on the dark footer background is ≈2.66:1**, and the adjacent `.copyright`/`.tagline` text (`#64748b`) is ≈4.23:1 — both fail the 4.5:1 minimum. *(WCAG 1.4.3, `Footer.astro`)*
9. **Contact form's required fields have no visible required-indicator** (asterisk or "(required)" text) even though they're marked `required` in HTML. *(WCAG 3.3.2)*
10. **48 of 52 GSAP-animated components have zero `prefers-reduced-motion` handling** — only `Hero.astro`, `WhatsAppFloat.astro`, `SmoothScroll.astro`, and `Footer.astro` check it; all `ProcessParallax`/`IndustriesWeServe`/`TripleReveal` components run scroll-scrubbed animation unconditionally. *(Maps to WCAG 2.3.3, which is AAA rather than AA — included for completeness, not a strict AA failure.)*

### Low / Info
- `lang="en"` is set correctly and consistently across all three layouts — no issue.
- Home page heading DOM order is technically correct (H1 precedes H2) despite the visual size mismatch noted in §2 — a styling issue, not a structural one.
- Sampled contrast pairs that **pass**: `.mega-desc` (≈4.76:1), TOC "In This Article" label (≈4.83:1), dropdown menu links (≈10.8:1) — two of these are close enough to the 4.5:1 line to watch if colors change later.
- All three `ContactFormVideo` fields have correctly associated `<label for="...">` elements — a genuine pass.

---

## 6. Site Architecture, Internal Linking & Crawlability

### High
1. **3 pages have zero inbound links from anywhere** — not nav, not footer, not the blog hub, not any other page's body content, not any shared component: `/laboratory-analysis/`, `/scale-up-support/`, `/troubleshooting/`. They're reachable only by direct URL, the sitemap, or organic search.
2. **One broken internal link**: `aerosol-insect-repellent-deet-picaridin-comparison.astro` (lines 408 and 475) links to `/industrial-aerosol-insecticides-registration-efficacy/`, a page that does not exist anywhere in the codebase.
3. `/formulations-and-technology/` is reachable via exactly one link, buried in `PortfolioGrid.astro` — not a true orphan, but a fragile single point of failure for an otherwise well-linked page.

### Medium
4. **230 internal links across 22 files are missing the mandatory trailing slash** (site is `trailingSlash: 'always'`), forcing an avoidable 308 redirect on every click. ~90% concentrate in one reused "related articles" block used across ~16 long-form guide pages — heaviest offenders: `aerosol-propellants-explained-...` (17), `flash-point-explained.astro` (15), `how-aerosol-cans-work.astro` (15), `why-do-aerosol-cans-leak.astro` (15). Fixing the one shared template resolves the bulk of this in a single change.
5. **`robots.txt` has no `Disallow` backstop** for the paths the sitemap filter excludes (see §1) — repeated here because it's specifically relevant to crawl-budget management for excluded paths.
6. **`/login/` has zero on-site links anywhere** — checked nav, footer, every page body, and shared components. If sign-in is meant to be a live, discoverable feature, there's currently no way for a real visitor to reach it by clicking.

### Low
7. **No custom 404 page** (repeated from §1 — included here because it's specifically a crawlability/recovery-path concern: a stale backlink or typo currently dead-ends users with no site navigation).

### Info (checked, confirmed clean — included to show verification, not because they're issues)
- No accidental `noindex`/`nofollow`: only `login.astro` sets a non-default `robots` value anywhere in the 94 pages.
- 5 pages pass a `canonical` prop without a trailing slash (`aerosol-manufacturing-101-guide.astro`, `formulations-and-technology.astro`, `laboratory-analysis.astro`, `scale-up-support.astro`, `troubleshooting.astro`) — **confirmed not a bug**: `Layout.astro`'s canonical-normalization logic always appends the trailing slash before rendering, so the final output is correct regardless of what's passed in.
- The blog hub's 58-entry post array has zero dangling links — every card resolves to a real page.
- Reachability math: 94 total routes → 83 directly reachable from nav + footer + blog hub → 7 more confirmed reachable via in-body contextual links → 4 genuine zero-inbound-link pages (`laboratory-analysis`, `scale-up-support`, `troubleshooting`, `login`).

---

## Methodology Notes

- **Multiline-tag risk**: this repo's `.astro` files routinely wrap HTML tags and attributes across multiple lines. A prior audit (2026-07-29) used naive line-based `grep` and produced a confidently-wrong finding ("10 of 51 posts missing `rel="noopener noreferrer"`") that a whole-file, multiline-aware re-check corrected to the true value of 0/51. Every sub-audit in this report was explicitly instructed to read whole files and match tags with multiline-safe regex (or the `Read` tool) rather than per-line `grep`, and to verify any "N of M" style claim this way before reporting it. Two independent agents cross-validating the same finding (e.g., the "9 pages with no H1" result, found separately by the on-page SEO and accessibility audits) is a strong confidence signal that this methodology held.
- **Sampling**: the on-page SEO and site-architecture audits covered all 94 pages exhaustively. The blog/structured-data and accessibility audits worked from representative samples (15 of 58 posts; ~10–15 pages across templates, respectively) for the deeper manual checks, while running mechanical checks (date-logic consistency, `robots` prop usage) across the full corpus. Findings phrased as "N of 94/58" are exhaustive; findings phrased as "N of 15" are sample-based and may not capture every instance sitewide.
- **No fixes were applied.** This document is diagnostic only, per the request that produced it.
