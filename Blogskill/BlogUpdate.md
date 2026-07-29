---
name: BlogUpdate
description: >
  Enhances the oldest 5 not-yet-enhanced blog posts per invocation — technical
  SEO, schema completeness, internal/external link hygiene, and natural
  keyword enrichment. Triggered by the user typing /BlogUpdate or saying
  "execute BlogUpdate". Edits files in place, never commits or pushes.
---

# BlogUpdate Skill — Technical & SEO Enhancement of Existing Blog Posts

This skill goes back over already-published blog posts and brings them up to
the site's current technical/SEO standard. It does **not** write new posts
(see `Blogskill/BlogSkill.md` for that) and does **not** touch any
`Blog/{slug}/` source folders or R2-hosted image assets. One run enhances
exactly the oldest 5 posts that haven't been enhanced in the current cycle.

---

## TRIGGER COMMAND

When the user says **"execute BlogUpdate"** or types **`/BlogUpdate`**:
→ Run the full pipeline below once, end to end, for 5 posts.

There is no numbered/batch invocation variant — always exactly one run = one
batch of (up to) 5 posts. With 51 posts currently published, a full cycle is
roughly 10-11 runs; keep the batch small so each run stays reviewable in one
`git diff` and a broken post is easy to isolate.

---

## Step 1 — Load state and select the target posts

1. Read `src/pages/blog/index.astro`. Extract every entry in the `allPosts`
   array as `{ title, url, publishDate, category, author, tags, readingTime }`.
   **The array is NOT stored in chronological order** — posts are prepended
   at the top when written, so "oldest" must be computed by parsing
   `publishDate`, never by reading from the bottom of the array.
2. Read `Blogskill/blogupdate-state.json` (sibling to the existing
   `Blogskill/state.json` used by the creation skill — a separate file, never
   share or overwrite that one). If it does not exist, create it with:
   ```json
   { "cycle": 1, "enhanced": {} }
   ```
3. Compute the candidate set: every post whose slug (the `url` with the
   leading and trailing `/` stripped) is **missing** from `enhanced`, or
   present with `enhanced[slug].pass < cycle`.
4. If the candidate set is **empty** (every post already has
   `pass >= cycle`), increment `cycle` by 1 and recompute the candidate set
   against the new `cycle` — this is the automatic loop-back into a new
   enhancement pass over all posts. Do this before selecting, not after.
5. Parse `publishDate` (format `"Mon D, YYYY"`, e.g. `"Jul 29, 2026"`) into a
   real date for every candidate, sort ascending (oldest first), and take the
   first 5 (fewer than 5 only if fewer than 5 candidates remain — this is
   expected right after a cycle rollover and is not an error).
6. Report to the user before doing any editing: the list of 5 (or fewer)
   `title` / `url` pairs selected, the current `cycle` number, and overall
   progress (e.g. "12/51 enhanced in cycle 1").

---

## Step 2 — Per-post pipeline

Run **Steps 2a–2j** in order for each of the 5 selected posts, one post at a
time. Read the full file at `src/pages/<slug>.astro` before touching anything.

### 2a — Schema & meta audit
Check the page's `<Layout ...>` props and every object in the schema
(`blogSchema` / `@graph` array on newer posts, a flatter `schemaJson` object
on older ones — handle either shape as found, don't force a rewrite of one
into the other):
- `title` prop: 44–59 characters, contains the primary keyword. Confirmed
  directly in `Layout.astro`: `<title>{title}</title>` renders the prop
  verbatim with no brand suffix appended, so there's no "strip the suffix"
  step needed here — just keep new/edited titles inside the length budget.
- `description` prop: 140–160 characters, contains the primary keyword plus a
  concrete benefit/hook — rewrite if it's outside this range or reads as
  generic filler.
- The `@graph` should contain all of: Organization, WebSite, Person,
  BreadcrumbList, BlogPosting, FAQPage, WebPage. Add any that are missing,
  modeled on the shape already used in a recently-written post (e.g.
  `src/pages/compressed-vs-liquefied-gas-aerosols-pressure-profiles.astro`
  has the complete current 6-block `@graph` to copy from).
- `BlogPosting.headline` must exactly match the page's `<h1>` and the
  `title` prop. `BlogPosting.description` must exactly match the
  `description` prop. Fix any drift.
- `BlogPosting.dateModified`: set to today's actual date whenever this pass
  makes a material content change to the post (any edit beyond a trivial
  metadata-only fix such as adding a missing `wordCount` field). Leave
  `datePublished` untouched always.
- `BlogPosting.keywords`: expand to reflect the fuller keyword set produced
  in Step 2d below.
- `BlogPosting.wordCount`: recompute the post's actual current body word
  count and set/add this field every pass — not only when Step 2g materially
  expands content. A site check on 2026-07-29 found only 28 of the 51 blog
  posts have this field at all.
- `FAQPage.mainEntity` must mirror the on-page FAQ exactly — same questions,
  same answers, same count. If the on-page FAQ has fewer than 6 questions,
  add enough new ones (grounded per Step 2g) to reach 6, and mirror them into
  the schema.
- **Author consistency check:** newer posts show `author: "Global Aerosols
  Team"` in the blog index and on the visible byline, but the schema's
  `Person` block is still hard-coded to `"name": "Absar Khan"` (carried over
  from the BlogSkill.md template). Do not silently pick one — if the on-page
  byline and the schema `Person.name` disagree for a post, normalize the
  schema's `Person.name` to match whatever the visible byline and the blog
  index `author` field say for that post, and note the fix in the Step 6
  report. Never invent a byline that isn't already in the blog index entry.
- Confirm exactly **one** `<h1>` exists on the page.
- `canonical` prop: **must end with a trailing slash**
  (`https://www.globalaerosols.com/<slug>/`) — `astro.config.mjs` sets
  `trailingSlash: 'always'`, so a canonical without the trailing slash points
  at a URL that immediately redirects rather than the URL actually served.
  A 2026-07-29 check found this is true of **all 51** current posts, without
  exception. Fix it on every post touched by this pass; do not mass-edit
  untouched posts just for this.
- **Category taxonomy check (report, don't silently mass-fix):** the blog
  index's client-side category filter (`src/pages/blog/index.astro`, the
  `categories` array and `data-category` filter logic) generates one filter
  button per entry in `categories` — but several declared categories
  (`Lubricants`, `Household`, `Industrial Cleaners`, `Adhesives & Sealants`,
  `Adhesives & Polymer Care`, `Pharmaceuticals & Healthcare`, `Construction
  Chemicals`, `Agrochemicals`, `Green Chemistry`, `MaaS & Strategy`,
  `Formulation Chemistry`) currently match **zero** posts — 11 dead filter
  buttons that always show "0 articles". Most are non-aerosol category names
  left over from the site's pre-aerosol era and were never cleaned out of
  the `categories` array; they are **not** categories to move posts into.
  Separately, `"Cosmetics & Personal Care"` and `"Personal Care & Cosmetic
  Aerosols"` look like the same category under two different names. If this
  post's `category` is a
  **minority-spelling variant** of a category most other posts use,
  normalize it to the majority spelling and note the change in the Step 6
  report — this touches shared taxonomy beyond just this post, so it must be
  visible, not silent. Never invent a new category name, and never rename a
  post into a currently-empty/dead category just to "fill" it — that's a
  site-wide taxonomy decision for the user, not something to do post-by-post.
- When `dateModified` changes (per the rule above), also add or update a
  visible **"Updated: `<date>`"** label on the page next to the existing
  "By ... · `<date>` · `<n> min read"` meta row — this is a real
  freshness/trust signal for readers, not just crawlers, and is currently
  absent from every post.

### 2b — Internal link audit (topic-cluster linking, doubled targets)
With 51 posts clustered into a handful of categories, most posts have
several genuinely related siblings already published — this is a
topic-cluster/hub-and-spoke linking opportunity, not just a boilerplate
footer requirement. Internal linking between topically related content is a
well-established, low-risk SEO practice (it helps distribute page authority
and signals topical relationships to search engines) — unlike keyword
density, there is no established stuffing penalty for a reasonable number of
genuine, relevant internal links in long-form content, so the targets below
are intentionally higher than Step 2c's external-link targets.

- **Find real candidates first, don't just check a fixed count:** read
  `src/pages/blog/index.astro`'s `allPosts` array and build a candidate pool
  of other posts sharing this post's `category` (and/or overlapping `tags`).
  Pick from that pool for every link added below — never link to an
  unrelated post just to hit a number. With only 51 posts total, some
  categories (e.g. `Aerosol Regulatory & Safety`, 3 posts) may not have 6-8
  genuinely relevant siblings — if so, say so in the Step 6 report instead of
  padding with a weak match.
- **In-body contextual links: minimum 6–8**, woven naturally into body prose
  across different sections (not clustered in one paragraph), including at
  least one link to the post's category/landing page. Use the mapping
  `Blogskill/BlogSkill.md` Section C already defines for this site rather
  than inventing a new one — Aerosol Technology & Engineering →
  `/aerosol-technology-and-formulations`, Aerosol Propellants & Valves →
  `/aerosols`, Industrial & Specialty Aerosols → `/industrial`, Personal
  Care & Cosmetic Aerosols → `/cosmetics-and-personal-care-aerosols-guide`,
  Aerosol Regulatory & Safety → `/aerosol-can-safety-explained`. For the
  older `Aerosols & Gas Dosing` bucket (21 posts, predates the current
  5-category rotation) pick whichever of those five best fits the post's
  actual subject. If the post's current prose
  doesn't have 6–8 genuine places for a related link, that's a signal to
  expand content under Step 2g first (more real paragraphs naturally create
  more legitimate anchor points) rather than forcing a link into an
  unrelated sentence.
- **Related Articles footer block: 2 topic-related links** drawn from the
  same category/tag candidate pool as above, distinct from whichever posts
  were already linked in-body where possible — **plus** the 6 fixed
  cornerstone links already mandated in `Blogskill/BlogSkill.md` Section C,
  unchanged: `/aerosol-manufacturing-101-guide`, `/how-aerosol-cans-work`,
  `/aerosol-propellants-explained-lpg-vs-dme-vs-hfc-vs-n2-vs-co2`,
  `/aerosol-chemistry-101`, `/from-lab-to-commercial-launch`,
  `/choosing-the-right-product-consultant`. Footer total is 8 links (2
  topic-related + 6 cornerstone). Add any missing cornerstone link.
- **Broken-link check:** for every internal link to another blog post,
  confirm the target slug actually exists as a file at
  `src/pages/<slug>.astro` (or is a known non-blog route, e.g. a category
  landing page like `/aerosols` or `/industrial`). If a linked post was
  renamed or removed, fix the link to the correct current slug or remove it
  — never leave a link pointing to a 404.

**Leave link `target` attributes exactly as they are.** Do not add, remove,
or normalize `target="_top"`, `target="_blank"`, or any other `target`
value on existing links. Match whatever convention the post already uses
when adding a new link. Link-attribute mechanics are out of scope for this
skill.

### 2c — External authority links
- **Minimum 4 external authority links** woven into body prose. Use the
  reference library already curated in `Blogskill/BlogSkill.md` Section H
  (ASTM, ISO, NFPA, EPA, OSHA, FDA, IEC, USP, or a specific Wikipedia
  technical article) — don't invent or guess a source URL that isn't in that
  library or independently verified. If the post has fewer than 4, add
  enough to reach 4, spread across different sections rather than clustered
  together, each at a genuinely relevant point in the existing text. Never
  pad toward the count with a marginally-relevant citation — if a post's
  topic genuinely only supports 2–3 authority citations, say so in the
  Step 6 report rather than forcing a 4th.
- **Broken-link check:** for any new external link added in this step, don't
  assume the URL resolves — use `WebFetch` to confirm the target page
  actually loads before adding it. This check is for newly-added links only;
  it is not required for external links that were already present and
  unchanged.

### 2d — Keyword enrichment (natural density + semantic variants only)
This is **not** keyword stuffing, and stuffing is explicitly prohibited —
Google's spam policies penalize it and it degrades the reader experience;
`Blogskill/SEO_CHECKLIST.md` already caps primary-keyword density at 1–2%.
- Identify the post's primary keyword (from its title/H1) and existing
  supporting keywords (from `tags` in the blog index entry and the
  `BlogPosting.keywords` schema field).
- Identify natural semantic/LSI variants and closely related phrases a
  reader or search engine would associate with the topic (use web search for
  this when it helps surface real related terminology, not to fabricate
  technical content).
- Weave these variants into: additional H2/H3 phrasing where a heading is
  currently generic, a few body sentences, image `alt` text (Step 2e), and
  FAQ questions/answers — always inside natural, grammatical sentences.
  Never repeat the exact-match primary keyword phrase back-to-back or insert
  it in a way that breaks sentence flow.
- Update `BlogPosting.keywords` to include the expanded set.
- **Cannibalization check:** before finalizing, confirm this post's primary
  keyword doesn't already exactly match (or near-duplicate) another post's
  primary keyword or title in `src/pages/blog/index.astro` — several
  propellant/regulatory topics are close enough (e.g.
  `aerosol-propellants-explained-lpg-vs-dme-vs-hfc-vs-n2-vs-co2` vs
  `propellant-influence-on-aerosol-performance`) that this is a real risk
  here, not just a theoretical one. If found, note the potential
  cannibalization in the Step 6 report rather than silently proceeding — do
  not edit the other post to resolve it.

### 2e — Image alt text and attributes (no image regeneration)
- Rewrite every `<img>` `alt` attribute to be descriptive and keyword-rich,
  ending in `— Global Aerosols` per the site's existing convention (see
  `Blogskill/SEO_CHECKLIST.md`), and accurately describing the actual image
  content — never describe something the image doesn't show.
- Ensure every `<img>` has `src`, `alt`, `width`, `height`, and `loading`
  (`eager` for the hero/first image, `lazy` for the rest).
- **Never** regenerate, replace, re-crop, or re-upload any image file, and
  never change an `src` URL. A 2026-07-29 check found 29 of 51 posts still
  reference the old `assets.zyrosite.com` host instead of the current
  `cdn.globalaerosols.com` R2 CDN used by newer posts — if this post is one
  of them, note it in the Step 6 report as a regeneration/migration
  candidate for a future, separate task; do not act on it here.

### 2f — Bullet points, numbered lists, and tables
Audit list and table usage against the same formatting rules
`Blogskill/BlogSkill.md` (Section D, rules 6–7) enforces at creation time,
and fix any violations found:
- Bullet points are for unordered sets (ingredient classes, properties,
  conditions, applications); numbered lists are for ordered/sequential
  content (steps, ranked factors, decision sequences). Convert any existing
  list that uses the wrong type for its content.
- Bold only the lead term/label of each bullet
  (e.g. `<strong>Vapor pressure</strong> — determines spray force and...`),
  never the full line. Fix any bullet that bolds an entire sentence.
- A list with only 2 items is a formatting violation, not a style choice —
  rewrite it as a single flowing sentence instead.
- Lists and tables must never replace a section's opening explanatory
  paragraph (see Step 2g) — a section that is bullets/table-only with no
  lead-in prose is a violation to fix, not something to leave alone.
- Add a comparison table wherever the body already discusses comparison data
  — types, grades, standards, properties, specs — as prose or an ad hoc list
  that would read more clearly as rows/columns. Match the existing
  `.data-table` / `table-wrap` markup pattern already used across the site
  (see the template in `Blogskill/BlogSkill.md` Section G) so styling stays
  consistent.
- Never invent comparison data to populate a table — only tabulate content
  that's already in the post or added under the established-science gate in
  Step 2g.

### 2g — Content depth and structure (established-science gate applies)
- If an H2/H3 section lacks its opening 3–4 sentence explanatory paragraph
  before any bullets/tables, add one (see Step 2f for how those bullets/
  tables themselves should be formatted).
- If the post is materially under the site's stated 1200-word hard floor
  (`Blogskill/BlogSkill.md` Section D1), expand thin sections with
  genuinely useful, verifiable technical content.
- If Step 2b/2c can't reach their link targets without forcing an unrelated
  link, treat that as a signal to expand content here first — genuine new
  paragraphs create genuine new places for a related internal or external
  link to belong naturally. Do this in that order (expand content, then
  link it), never the reverse (find a link, then write a sentence just to
  hold it).
- **Hard gate, no exceptions:** every sentence added or rewritten in this
  step must be traceable to established chemistry, peer-reviewed research, or
  a recognised standard (ASTM, ISO, NFPA, IEC, EPA, OSHA, FDA, UN/DOT). No
  hedging language ("may", "could", "is believed to", "typically") used to
  soften an unverifiable claim — hedged speculation is treated exactly the
  same as outright speculation and is prohibited. If a section is thin and
  no verifiable content can be added, **leave it thin and say so in the
  report** rather than padding it with invented or hedged filler. Hitting a
  word count is never a reason to write an unverifiable sentence.
- Never reveal exact formulation dosages, percentages, active loadings, or
  proprietary ratios — matches `Blogskill/BlogSkill.md` Section D4's IP
  protection rule exactly; this update skill inherits it, not relaxes it.

### 2h — FAQ depth
- Minimum 6 FAQ items, each a genuinely complete answer (minimum 2–4
  sentences per `Blogskill/SEO_CHECKLIST.md`) a skimming reader could rely on
  without reading the body. Add questions if short of 6, subject to the same
  established-science gate as Step 2g.

### 2i — Readability polish
Apply general readability fixes — phrasing/structure edits only, still
subject to the Step 2g established-science gate wherever a sentence's
*content* (not just its wording) changes:
- No sentence over 30 words — split any that exceed it.
- No three consecutive sentences starting with the same word — vary
  sentence openers.
- Remove filler phrases ("it is worth noting", "it should be mentioned",
  "it is important to understand") — say the thing directly instead.
- Every section should close with a payoff sentence or a forward transition
  — if a section currently ends abruptly right after a bullet list or table
  with no closing sentence, add one.
- This is a lower-priority polish pass — don't rewrite a section end-to-end
  for style alone; fix specific violations where they clearly exist.

### 2j — Self-review pass (mandatory before writing anything for this post)
Before using `Edit` on the file, re-check:
1. No sentence added anywhere in this pass states a mechanism, property, or
   performance claim that isn't verifiable from established science — if in
   doubt, cut it.
2. `BlogPosting.headline`/`description` still match the `<h1>`/`description`
   prop exactly.
3. `FAQPage.mainEntity` still mirrors the on-page FAQ exactly, same count,
   same order.
4. No link's `target` attribute was added, removed, or changed anywhere in
   this pass.
5. No image `src`, dimensions, or crop was touched — only `alt` text and
   missing `width`/`height`/`loading` attributes.
6. Nothing outside `src/pages/<slug>.astro` (and, if triggered, the matching
   entry in `src/pages/blog/index.astro`) was modified for this post.
7. Any list touched in Step 2f uses the right type (bulleted vs numbered),
   bolds only the lead term, and has no 2-item lists; any new table holds
   only data that was already present or added under the Step 2g gate.
8. The schema `Person.name` matches the visible byline and blog-index
   `author` field, exactly one `<h1>` exists, `canonical` ends with a
   trailing slash, and `BlogPosting.wordCount` reflects the current actual
   word count.
9. Any category rename made in Step 2a was to the majority spelling used
   elsewhere in `allPosts` (never an invented name, never a move into a
   currently-dead category) and is called out in the Step 6 report.
10. Every internal link target and every newly-added external link was
    confirmed to actually resolve (Steps 2b/2c) — nothing points at a 404.
11. In-body internal links reach 6–8 and external authority links reach 4
    (or the report explicitly notes why the topic can't genuinely support
    that many) — and none of them were forced into an unrelated sentence
    just to hit the count.

Fix anything the self-review catches before moving to Step 3 for this post.

---

## Step 3 — Write edits

Use `Edit` (never `Write`) on `src/pages/<slug>.astro` so only the changed
lines are touched. If the on-page `<h1>`/title or `description` actually
changed during this pass, also `Edit` the matching entry in
`src/pages/blog/index.astro` (its `title`/`description`) so the blog index
card doesn't drift from the post — leave that entry untouched otherwise.

---

## Step 4 — Build verification

After all posts in the batch have been edited, run `npm run build` **before**
touching the tracker — a post is only considered "enhanced" if its changes
actually build cleanly. (Note: `npm run build` also runs
`submit-indexnow.js` per `package.json` — if that step fails for reasons
unrelated to the edited files, e.g. a missing IndexNow key in the local
environment, judge the Astro build output on its own merits rather than
treating an unrelated IndexNow failure as a reason to revert a post.)

- If the build fails, read the error output to identify which edited file(s)
  caused it, fix the specific issue, and re-run the build. Repeat until clean.
- If a specific post's edits still can't be made to build cleanly after a
  reasonable fix attempt, revert that post's edits back to its
  pre-enhancement content, **exclude it from Step 5's tracker update**, and
  report it in Step 6 as "skipped — build error, needs manual review." A
  broken post must never be silently marked as enhanced.
- Do not proceed to Step 5 until the build is clean for every post that will
  be marked enhanced.

---

## Step 5 — Update tracker

For each post that built cleanly in Step 4, update
`Blogskill/blogupdate-state.json`:
```json
"enhanced": {
  "<slug>": { "pass": <cycle>, "last_enhanced": "<YYYY-MM-DD>" }
}
```
Write the file with `Edit` (or `Write` if the file was just created in
Step 1). Posts skipped in Step 4 are left out of this update so they're
picked up again on a future run rather than being marked done.

---

## Step 6 — Output summary to user

For each post that built cleanly, print a compact change list, e.g.:
```
✅ <title> (/<slug>/)
   • Added FAQPage schema (was missing) — mirrored 6 on-page FAQs
   • Fixed schema Person.name: "Absar Khan" → "Global Aerosols Team" (matches byline)
   • Fixed canonical: added trailing slash
   • Internal links: 3 → 7 in-body (added 4 from same-category topic cluster) + footer 2 topic-related/6 cornerstone
   • External authority links: 2 → 4 (added NFPA 30B, OSHA HazCom)
   • Expanded "Corrosion Behavior and Internal Coatings" section (was bullets-only, added opening paragraph) — created room for 2 of the new links above
   • Enriched keywords: added "X", "Y", "Z" naturally in body + alt text
   • Flagged: hero image still on assets.zyrosite.com — migration candidate
   • dateModified → 2026-07-29 (added visible "Updated:" label)
```
For any post skipped in Step 4, report it plainly instead:
```
⚠️ <title> (/<slug>/) — SKIPPED: build error after edit, reverted, needs manual review
```
Then a batch footer:
```
Cycle 1 · 12/51 enhanced this cycle · build verified clean
Review with `git diff` before committing.
```

Never commit or push — the user reviews and commits separately.

---

## What this skill never does

- Never touches any file under `Blog/{slug}/` or re-uploads to Cloudflare R2.
- Never writes a brand-new post (that's `Blogskill/BlogSkill.md`).
- Never regenerates, re-uploads, or changes the `src` of any image.
- Never touches link `target` attributes or `rel` attributes — no adding,
  removing, or normalizing `target="_top"`, `target="_blank"`, or
  `rel="noopener noreferrer"`. Link-attribute mechanics are out of scope.
- Never states a technical claim that isn't grounded in established science —
  no speculation, no hedged speculation, no padding for word count.
- Never reveals exact formulation dosages, percentages, or proprietary ratios.
- Never applies literal or moderate keyword stuffing — enrichment is natural
  density + semantic variants only.
- Never forces an internal or external link into an unrelated sentence just
  to hit the 6–8 / 4 link targets — genuine topical relevance always outranks
  the count, and a post that can't genuinely support the target says so in
  the report instead.
- Never processes more or fewer than the oldest 5 not-yet-enhanced posts in
  a single run (fewer only immediately after a cycle rollover).
- Never marks a post as enhanced in the tracker if its edits didn't pass
  `npm run build` — a skipped/reverted post stays eligible for a future run.
- Never invents a category name or moves a post into a currently-dead
  category — only fixes mechanical spelling/pluralization drift of the same
  category, and always reports the change.
- Never edits `Blogskill/BlogSkill.md`, `Blogskill/state.json`, or
  `Blogskill/topics.json` — those belong to the creation pipeline.
- Never commits or pushes changes.
