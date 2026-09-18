# Global Aerosols Website — Remediation Report

**Date:** 2026-09-18
**Companion to:** `SITE_AUDIT_2026-09-18.md` (the original findings this report resolves)
**Scope:** 33 commits, all local, nothing pushed to `origin/main`. Every commit was verified with a full rebuild (and in most cases a targeted re-scan or rendered-output check) before moving to the next.

---

## Executive summary

Of the ~150 findings in the original audit, the large majority are now fixed and verified. A handful were deliberately left open with a documented reason — either because fixing them safely wasn't possible from this environment (no CDN/asset access, no browser to visually test animation), or because they need something only you can provide (a real author photo) or decide (a dependency major-version bump). Nothing was pushed anywhere; all 33 commits sit locally on `main`, ready for you to review and push when ready.

**Headline numbers:**
- npm vulnerabilities: 14 → 8 at time of the dependency-bump commit (a 9th, unrelated advisory has since appeared in npm's live database — see Dependencies section)
- Dead-weight images removed: ~69.5 MB, `dist/client` dropped from 230 MB → 161 MB
- Pages with zero `<h1>`: 9 → 0
- Pages with a heading-hierarchy skip: 60 → 0
- Internal links missing a trailing slash: 230 → 0
- Pages with duplicated migration-artifact markup: 8 → 0 (plus a duplicated title-suffix bug on 6 of them)
- Titles/descriptions outside target length: 61 pages → 1 (a deliberate exception, see below)
- Blog posts with a `Blog` schema entity: 0/61 → 61/61
- Blog posts with figure/figcaption on the hero image: ~2/61 (sampled) → 61/61
- `<img>` tags sitewide with no `loading` decision: 26 → 0
- GSAP-animated components respecting `prefers-reduced-motion`: 4 → 45 (4 pre-existing + 41 newly fixed)

One thing worth knowing up front: **the plan changed once, mid-flight, by your own choice.** You initially asked to purge the dead-weight images from every commit in git history; when I explained that meant rewriting all 106 commit hashes and force-pushing, you chose instead to just remove them going forward. `.git` still carries that ~69.5MB in its history (currently ~351MB total) — untouched, exactly as you asked.

---

## 1. Infrastructure & security — fixed

- **Dependency patch bumps**: `astro` 6.4.2→6.4.8, `@astrojs/sitemap` 3.7.3→3.7.4, `lenis` 1.3.23→1.3.26, plus a non-breaking `npm audit fix` for `js-yaml`, `nanoid`, `postcss`, `smol-toml`, `svgo`. Vulnerability count dropped 14→8 at the time. **As of this report, a fresh `npm audit` shows 9** (1 low, 2 moderate, 5 high, 1 critical) — npm's advisory database is live and a new advisory appears to have been published since; this is not a regression from anything changed here.
  - **Still open, by your decision**: the remaining vulnerabilities trace to `wrangler`/`miniflare`/`vite`/`undici`, fixable only via the `@astrojs/cloudflare` 13→14 major-version bump you asked to defer. `npm audit` in this repo will show you the exact current list at any time.
- **Real HTTP security headers** added to `public/_headers`: `Content-Security-Policy`, `X-Frame-Options`, `Strict-Transport-Security`, `Referrer-Policy`, `X-Content-Type-Options`. The CSP allowlist was built from an actual grep of every external origin the site uses — this caught that the CanWrap 3D pages load BabylonJS, Three.js, and esm.sh modules, which a guessed policy would have silently broken.
  - **One thing to verify yourself**: CSP is the one fix in this whole pass that a local build can't fully confirm. Open the site in a real browser after your next deploy and check the console for any CSP violation reports, particularly on the two CanWrap 3D pages.
- **Semantic `<main>` + working skip-links** added across all three layout components (previously: two of three had no `<main>` at all, and the only skip-link anywhere on the site pointed at an id that didn't exist).
- **Branded `src/pages/404.astro`** added (previously none existed).
- **`robots.txt`** now has `Disallow` rules matching the sitemap's own exclusion filter.
- **Stray root files** (`can wrap3d aluminium`, `canwrap 3d`, `model pic.jpg`) — I want to flag a near-miss here: I initially deleted these assuming they were untracked clutter, based on a `head -30`-truncated grep that missed they were actually tracked in git. I caught this before committing, restored all three from git, and left them alone. They're real, tracked, historical files outside the audit's scope — not touched.

## 2. On-page SEO — fixed

- **6 pages** had a literal `"... | Global Aerosols | Global Aerosols"` duplicated in their `<title>` — fixed.
- **49 pages'** "Guide Contents" TOC heading promoted from `<h3>` to `<h2>`, closing the H1→H3 skip.
- **9 category pages** had their visible page title coded as `<h2>` — promoted to `<h1>` (kept the same `id`/`class` so the existing reveal animation and CSS are untouched).
- **Homepage** H1/H2 were inverted (a decorative corner label was the H1, the real title was an H2) — swapped.
- **61 pages** had their title and/or description rewritten to the ~45–65 / ~140–165 character targets — every new value was checked programmatically against the target range, not eyeballed, and the handful that missed on the first pass were caught by that check and corrected before committing.
  - **One deliberate exception**: `login.astro`'s title stayed short. It's `noindex`, SSR-only, and (per the internal-linking audit) has zero on-site links anywhere — padding its title for SEO would be artificial for a page nobody can currently reach by clicking.
- **19 pages** got an explicit `canonical` prop where none existed before (not a live bug — the layout already normalized the fallback correctly — but now consistent and auditable).
- **4 keyword-cannibalization clusters** (8 pages) got reciprocal cross-links with differentiated anchor text, plus one title tweak (`formulations-and-technology.astro`) to reduce a word-order collision with its counterpart page. No pages were merged or redirected, per your choice.

## 3. Blog content & structured data — mostly fixed, two items partial by necessity

- **`Blog` entity added to all 61 posts** via an inline `isPartOf` object on each `BlogPosting` node. **This one had a real bug I caught before it shipped**: my first attempt used a regex that broke on the ~23 posts using a JS template literal (`` `https://.../${slug}/` ``) for their URL — the `}` closing the `${...}` interpolation isn't the object's real closing brace, and the naive pattern matched the wrong spot, corrupting those files' JavaScript. Nothing had been committed yet, so I reverted the whole batch and reapplied with a template-literal-aware regex, then verified by parsing the actual rendered JSON-LD from all 61 posts' built output (not just checking the build succeeded).
- **Image dimensions added to `BlogPosting.image` schema on 28 of 61 posts** — real pixel dimensions read via Pillow from local copies of the hero images. **The other 33 posts reference CDN-only images with no local copy in this repo to measure.** I confirmed dimensions are genuinely inconsistent across the corpus (a mix of 1200×630 and 1024×1024 depending on generation batch), so I could not safely assume a standard size for the unverified ones without risking wrong data in your structured markup. This needs either a local copy of those 33 images or direct CDN access to finish.
- **`dateModified` corrected on 4 posts** where it had drifted from the actual last content edit (per git history).
- **Figure/figcaption added to all 61 posts'** hero images, with a real, specific caption derived from each image's already-good alt text (not a generic placeholder). Three different underlying markup patterns needed three different approaches — one (`hero-img-wrap`, 15 posts) has `overflow:hidden` + a fixed `max-height` + `object-fit:cover`, so I placed the caption as a sibling outside that box rather than nesting it inside, where it risked being silently clipped.
- **`meta.json` link counts corrected** for the 3 files the audit specifically confirmed as inaccurate (internal build metadata only — not used by the live site).
- **Not fixed — needs you**: every sampled post uses a text-initials avatar ("AK") instead of a real author photo for the E-E-A-T author box. I can't fabricate a photo of a real person. If you send one, I can wire it in.
- **Noticed, not fixed** (outside this pass's scope, flagged for your awareness): while cleaning up `understanding-sds-tds-and-coa-for-aerosol-products.astro`'s duplicate-header bug, I noticed its introduction paragraph appears to repeat itself (the same sentence twice in adjacent `<p>` tags). This is a content-duplication issue distinct from the markup-duplication bug I was fixing there, so I left it for you to review rather than editing article prose I wasn't asked to touch.

## 4. Performance & assets — fixed

- **6 category-page hero images converted from PNG to WebP.** Two already had a webp sibling on disk; the other four (automotive, arts-and-crafts, industrial, paints-and-coatings) had none, so I generated one via Pillow — 758KB→106KB, 875KB→153KB, 812KB→135KB, 653KB→62KB, consistent with the ~85–90% reduction already seen on the existing pairs. All six now have `width`/`height`/`loading="eager"`/`fetchpriority="high"` (correct, since these are genuinely above-the-fold LCP images).
- **Navbar's Formulations mega-menu** (10 images, renders on every page) switched from `loading="eager"` to `loading="lazy"`, matching the other two mega-menus in the same file.
- **14 ProcessParallax components** switched their scroll-gallery images from `eager` to `lazy`. Did not add `width`/`height` here — these images are `position:absolute; inset:0` filling a parent card, so they carry no real CLS risk regardless of intrinsic-size attributes.
- **19 more `<img>` tags sitewide** (homepage hero, Welcome.astro's background, 3 more category-page heroes, and several body-content images) given an explicit `loading` decision. **Sitewide, 0 of 333 `<img>` tags are now missing a `loading` attribute** (was 26).
- **Not fixed**: 86 of 333 `<img>` tags (44 files) are still missing `width`/`height`. Checked and confirmed most are CDN-only dynamic images with no local file to measure — unlike the schema-dimension case, a *wrong* width/height here would visibly distort layout, so I chose not to guess.

## 5. Accessibility — fixed

- **Contact form**: the form panel's background was only 4% opaque white over a moving video — meaning no fixed text color could have a reliable contrast ratio, regardless of which one was picked. Strengthened the panel to a real, computable dark background, then picked a lighter blue (`#6ba3ff`) verified at 7.66:1 against it (the old color was ~3.8:1 even against the new darker panel). Also added `role="alert" aria-live="polite"` to the submit-status message, and a visible "(required)" indicator to all 3 required field labels.
- **Footer** copyright/tagline/credit text recolored to `#94a3b8` (already used elsewhere in the same footer), verified at 7.86:1 against the real `hsl(224,71%,4%)` background — computed directly, not estimated.
- **`prefers-reduced-motion` support added to 41 components** (ProcessParallax/TripleReveal/IndustriesWeServe families). These elements start invisible via CSS and are only ever revealed by GSAP ScrollTrigger — so I deliberately did *not* just skip the animation script under reduced motion, since that would leave real content permanently hidden, which is worse than doing nothing. Instead added a CSS override that forces the genuine scroll-reveal elements (4 shared class names) to their settled, visible state regardless of whether the JS runs. Left one class (`.step-arrow-box`) alone — it's a plain CSS `:hover` reveal on a small UI icon, not a scroll-linked animation, so it isn't a motion concern.
  - Worth noting: this specific item maps to WCAG 2.3.3, which is AAA, not the AA level the rest of this audit targeted — included anyway since it was in scope of the full completionist pass.

## 6. Site architecture & internal linking — fixed

- **3 orphan pages** (`laboratory-analysis`, `scale-up-support`, `troubleshooting`) linked from the global footer's Services column — reachable from every page now.
- **1 broken internal link** (pointing to a page that was never created) removed; the dangling "Related Articles" card that linked to it was dropped too, leaving 3 legitimate related links in that grid.
- **230 internal links missing their trailing slash** fixed across 22 files.
- **8 pages with duplicated breadcrumb/nav/header markup** from a past content migration cleaned up — each had its own specific flavor of the bug (a stray dead skip-link, a malformed `<div><header>` nesting, a non-functional text-only "breadcrumb", a full duplicate mini-navbar, or a second non-functional table of contents). Several of these pages also had **dead, unreferenced `<section id="...">` stub tags** (confirmed via grep that nothing linked to them before removing).
- **`login.astro`** — confirmed it's `noindex`, SSR-only, and genuinely has zero on-site links anywhere. Treated this as an intentional, dormant feature rather than adding a nav entry to "fix" it. If sign-in is meant to be live and discoverable, that's a product decision, not something I should guess at.

---

## Everything still open, in one place

| Item | Why it's open | What would close it |
|---|---|---|
| `@astrojs/cloudflare` 13→14 major bump | Explicitly deferred by your choice | Your call on when to take the compatibility risk |
| 33 blog posts' `BlogPosting.image` dimensions | No local copy of the image to measure; corpus dimensions aren't uniform, so guessing risks wrong schema data | A local copy of those 33 images, or CDN access from this environment |
| Real author photo (replacing "AK" initials avatar) | Can't fabricate a photo of a real person | You send a photo |
| Duplicated intro paragraph on `understanding-sds-tds-and-coa-for-aerosol-products.astro` | Discovered incidentally; it's a content issue, not the markup bug I was fixing there | A quick look and edit next time you're in that file |
| 86 `<img>` tags (44 files) missing width/height | Mostly CDN-only images with no local file to measure; wrong values would visibly distort layout | Same as the blog-image-dimension item — local copies or CDN access |
| CSP header | Built correctly from actual code, but a local build can't verify browser-side enforcement | One visual check of the browser console on your next deploy, especially the two CanWrap 3D pages |
| `.git` history size (~351MB) | You chose not to rewrite it | Available any time if you change your mind — would need `git filter-repo` + a coordinated force-push, since this repo has a GitHub remote |

---

## How to review

All 33 commits are on `main`, unpushed. `git log a74155d..HEAD` (excluding your own `55b4a77` commit that landed just before this session, which I didn't touch) shows them in order — each one's message explains what it fixed, why, and how it was verified. Nothing here was pushed to `origin/main`; that's your call to make whenever you're ready.
