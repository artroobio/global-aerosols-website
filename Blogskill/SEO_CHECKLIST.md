# SEO CHECKLIST — Global Aerosols Blog
# Integrated into BlogSkill.md — verified on every article before output

## 1. TITLE & META
- [ ] Title is 44–59 characters (NO "| Global Aerosols" suffix — the Astro Layout appends it automatically)
- [ ] Title contains primary keyword
- [ ] Meta description is 140–160 characters
- [ ] Meta description contains primary keyword + a benefit/hook
- [ ] Canonical tag present and correct (globalaerosols.com/{slug})
- [ ] Open Graph tags: og:title, og:description, og:image, og:url, og:site_name

## 2. HEADINGS STRUCTURE
- [ ] One H1 only — contains primary keyword
- [ ] H2s contain supporting keywords naturally
- [ ] H3s used for sub-sections, not keyword stuffing
- [ ] Logical hierarchy: H1 > H2 > H3 only

## 3. KEYWORD USAGE
- [ ] Primary keyword in first 100 words
- [ ] Primary keyword density: 1–2% (not stuffed)
- [ ] Supporting keywords distributed across H2s and body
- [ ] LSI/semantic keywords used naturally in body text
- [ ] No keyword cannibalization with existing posts

## 4. CONTENT QUALITY (E-E-A-T)
- [ ] Minimum 2000 words (2500–3000 target for competitive/pillar topics)
- [ ] Author bio with aerosol credentials present
- [ ] Every section starts with 3–4 line explanatory paragraph
- [ ] Bullet points only after paragraphs — never as main content
- [ ] No speculation — only verified technical facts from established aerosol science
- [ ] NO exact percentages, ingredient ratios, or proprietary formulation dosages revealed
- [ ] Tables used wherever comparison data exists (propellant types, valve specs, standards, etc.)
- [ ] FAQ section with minimum 6 questions (FAQ Schema added)
- [ ] CTA present and links to /contact

## 5. INTERNAL LINKS
- [ ] Minimum 3–4 contextual internal links woven into BODY text (not just footer)
- [ ] At least 1 in-body link to the relevant category/landing page:
      • Aerosol Technology → /aerosol-technology-and-formulations
      • Propellants & Valves → /aerosols
      • Industrial Aerosols → /industrial
      • Personal Care Aerosols → /cosmetics-and-personal-care-aerosols-guide
      • Regulatory & Safety → /aerosol-can-safety-explained
- [ ] Internal links use descriptive anchor text (not "click here")
- [ ] All internal links use target="_top"
- [ ] Related Articles footer block = 8 links: 2 topic-related + 6 cornerstone defaults
- [ ] All 6 cornerstone defaults present in EVERY blog:
      • Aerosol Manufacturing 101 → /aerosol-manufacturing-101-guide
      • How Aerosol Cans Work → /how-aerosol-cans-work
      • Aerosol Propellants Explained → /aerosol-propellants-explained-lpg-vs-dme-vs-hfc-vs-n2-vs-co2
      • Aerosol Chemistry 101 → /aerosol-chemistry-101
      • From Lab to Factory → /from-lab-to-commercial-launch
      • Choosing the Right Aerosol Consultant → /choosing-the-right-product-consultant

## 6. EXTERNAL LINKS
- [ ] Minimum 3 external authority links woven into body prose (NOT a list at the end)
- [ ] All sources drawn from the Section H library in BlogSkill.md — no invented URLs
- [ ] At least 1 link to the primary standard/regulation governing the topic:
      • Technology/Engineering → ASTM (astm.org) or ISO (iso.org) test standard
      • Propellants/Valves → EPA SNAP (epa.gov/snap), UNEP Ozone (ozone.unep.org), NFPA (nfpa.org)
      • Industrial Aerosols → ASTM, OSHA (osha.gov), IPC (ipc.org) for electronics
      • Personal Care → FDA (fda.gov/cosmetics), EU Cosmetics Reg (eur-lex.europa.eu), ECHA (echa.europa.eu)
      • Regulatory & Safety → Primary regulation text: DOT 49 CFR (ecfr.gov), NFPA 30B, EU Directive (eur-lex.europa.eu), CARB (arb.ca.gov), BIS (bis.gov.in)
- [ ] At least 1 link to a technical database for any physical/chemical property claim:
      • PubChem (pubchem.ncbi.nlm.nih.gov) — vapor pressure, boiling point, GHS class, LD50
      • NIST WebBook (webbook.nist.gov) — thermodynamic/pressure-temperature data
      • PubMed (pubmed.ncbi.nlm.nih.gov) — peer-reviewed research, inhalation studies
- [ ] Industry association where relevant: BAMA (bama.co.uk), FEA (aerosol.org), CSPA (cspa.org), IATA (iata.org)
- [ ] Wikipedia only for well-established chemistry/physics definitions — never for regulatory or safety claims
- [ ] All external links use target="_blank" rel="noopener noreferrer"
- [ ] Each link placed at the exact point in the prose where the claim is made

## 7. IMAGES
- [ ] Minimum 3 images per article
- [ ] Hero image: loading="eager", srcset and sizes present
- [ ] All other images: loading="lazy"
- [ ] All images have src, alt, width, height
- [ ] Naming convention: {slug}-{descriptor}-globalaerosols.webp
- [ ] All images have descriptive alt text with keyword, ending "— Global Aerosols"
- [ ] Images uploaded to Cloudflare R2 bucket: global-aerosols-website
- [ ] CDN URLs use cdn.globalaerosols.com/images/{slug}/

## 8. SCHEMA MARKUP
- [ ] Organization schema (name: "Global Aerosols", url: globalaerosols.com)
- [ ] WebSite + SearchAction schema
- [ ] Person/Author schema (Absar Khan, affiliation: Global Aerosols)
- [ ] BlogPosting schema (with wordCount, keywords, articleSection, datePublished, dateModified)
- [ ] BreadcrumbList schema (3 levels: Home → Blog → Post)
- [ ] FAQPage schema — Q&As mirror article body exactly

## 9. TECHNICAL
- [ ] Two-column layout on desktop, single-column on mobile
- [ ] Sticky TOC sidebar (desktop)
- [ ] max-width 1140px container
- [ ] Font loads from Google Fonts CDN (Playfair Display + Source Serif 4)
- [ ] No render-blocking scripts
- [ ] Responsive images with srcset
- [ ] Page loads clean (no broken links, no broken CDN URLs)

## 10. BRANDING
- [ ] Post author: "By Global Aerosols Team" in hero meta row
- [ ] About the Author: Absar Khan aerosol-specific bio at bottom
- [ ] LinkedIn link correct and opens in new tab
- [ ] Contact CTA: "Need Expert Aerosol Consulting?" links to https://www.globalaerosols.com/contact
- [ ] All 6 cornerstone default links in Related Articles footer block
