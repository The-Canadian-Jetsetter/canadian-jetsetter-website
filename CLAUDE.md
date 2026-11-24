# CLAUDE.md — The Canadian Jetsetter Website

This file is read automatically by Claude Code on every session start. It contains everything you need to work on this project correctly.

---

## Project

Rebuilding the website for **The Canadian Jetsetter** — a Canadian flight deals and points newsletter. Plain HTML/CSS/JS, no framework.

- **Live site:** https://thecanadianjetsetter.com
- **GitHub:** https://github.com/The-Canadian-Jetsetter/canadian-jetsetter-website
- **Hosting:** Cloudflare Pages

---

## File Structure

```
/
├── index.html                  Homepage
├── economy.html                Jetsetter Economy page (DESIGN REFERENCE)
├── jetsetter-premium.html      Jetsetter Premium page
├── jetsetter-free.html         Jetsetter Free page
├── golden-visa.html            Golden Visa page
├── golden-visa.css             Golden Visa styles
├── contact.html                Contact page
├── contact.css                 Contact styles
├── links.html                  Link-in-bio page
├── blog.html                   Blog listing page
├── posts/                      Individual blog post HTML files
├── posts.json                  Blog metadata
├── inject_posts.py             Blog injection script
├── TCJ Website Assets/
│   ├── logos/
│   │   ├── site-header-logo-white.png      (header bar logo)
│   │   └── site-header-logo-charcoal.png   (mobile menu panel logo)
│   └── [other images]
```

---

## Design Reference

**`economy.html` is the master design reference.** Before creating or significantly editing any page, read `economy.html` to ensure consistency.

### Colors
- Dark red: `#761915`
- Cream: `#F6F2E7`
- Black (footer): `#000000`

### Header
See **Site header** below. The header (desktop and mobile menu) comes from `site-header-nav.jsonc` and `site-header.css`; it switches to the mobile menu below 900px.

### Hero Sections
- Slim banner style
- Small uppercase label + large uppercase headline
- Background image with dark gradient overlay

### Footer
Always copy footer exactly from `economy.html`.

### Social Stats Bar
`TikTok: 100K+ Followers  |  Instagram: 120K+ Followers  |  Newsletter: 37K+ Subscribers`

---

## Key Rules

1. **Always read `economy.html` before creating or significantly editing a page** — it's the design source of truth
2. **Mobile responsive** — use media query breakpoint at 768px (the site header uses its own 900px breakpoint; see Site header)
3. **Use `!important`** when overriding styles that aren't responding
4. **When asked to apply changes across all pages**, apply to: `index.html`, `economy.html`, `jetsetter-premium.html`, `jetsetter-free.html`, `golden-visa.html`, `blog.html`, `contact.html`, `links.html`
5. **New pages** get their own `.css` file (e.g. `golden-visa.html` + `golden-visa.css`)
6. **Show before/after values** whenever changing CSS — makes it easy to review and revert

---

## Blog Publishing — Source of Truth

**`posts.json` is the single source of truth for the blog listing.** `blog.html`'s `POSTS_DATA` and the "Latest From The Blog" cards in `index.html` are GENERATED from it by `inject_posts.py`. NEVER hand-edit `POSTS_DATA` in `blog.html` or the homepage cards directly — any such edit is wiped the next time `inject_posts.py` runs, which is how posts have silently disappeared before.

Adding or changing a post, in order:
1. Put the post HTML in `posts/` (the filename becomes the `slug`).
2. Add/edit its entry in `posts.json`. Every entry needs: `slug` (= filename without `.html`), `date` as `YYYY-MM-DD`, `excerpt`, a LOCAL `featured_image` (`blog-images/…`, never an off-site URL), and `categories`/`tags`.
3. Run `python3 inject_posts.py` to regenerate `blog.html` and `index.html`.
4. Run `python3 check_posts.py` — it must pass before committing. It also checks that every page, posts included, has the current site header (see Site header).

---

## Site header

**Every page has the same header, CARDS included, and it is never copied by hand.** The single source is `site-header-nav.jsonc` (menu data) plus `site-header.css` / `site-header.js`. `inject_header.py` writes the header into every page between `<!-- site-header-head-start/end -->` (in `<head>`) and `<!-- site-header-start/end -->` (in `<body>`) markers. Never hand-edit between the markers; edit the menu data and re-run the script.

```bash
python3 inject_header.py            # write the current header into every page that has the markers, and refresh every page's CSS/JS ?v= versions
python3 inject_header.py --check    # report pages with no header, an out-of-date one, or out-of-date CSS/JS versions (changes nothing)
```

`check_posts.py` runs the same check, so a page or post with a missing or stale header fails it before commit.

- **Files:** `site-header.css` (styles), `site-header.js` (dropdown, mobile menu, glass-to-solid on scroll), `site-header-nav.jsonc` (menu data: every link, the logos, and the CARDS dropdown's cards).
- **After any change** to the menu data, `site-header.css`, `site-header.js` or any other CSS/JS file, run `python3 inject_header.py`. It rewrites the header on every page with the markers and refreshes the `?v=` version tags so browsers load the change (see Caching and cache-busting).
- **CARDS menu:** on, grouped like the cards site's menu: "All cards" on the left, then an "American Express" group (7 cards) and a "Scotiabank" group (5 cards); on mobile, "All cards →" then each group under a small heading. The card pages and their images are served on the live domain at `/cards/…` by the cards site's Cloudflare Worker route; the menu uses full `https://thecanadianjetsetter.com/cards/…` URLs (set by `cardsBase` on the Cards entry), so they also work in a local preview. To hide the menu, set `"enabled": false` on the Cards entry in `site-header-nav.jsonc`, then run `inject_header.py`.
- **Keep the card menu markup's shape:** the cards site's `npm run sync-header` copies this header and reads the CARDS lists, so keep the exact opening tags `<ul class="site-header__card-links">` and `<ul class="site-header__drawer-sub" id="site-header-sub-cards" hidden>`, each card item on one line, and the group lists as `<ol>` (a nested `</ul>` would cut its list short).
- **Glass or solid bar, per page:**
  - Glass (over a hero photo): `<body class="site-header-glass">` and `data-site-header-hero` on the hero element. The hero extends up behind the bar; the page's own CSS sets `--site-header-hero-pad` (and `--site-header-hero-min` if the hero has a min-height) next to the hero's own values, so its content stays in place.
  - Solid (no photo behind the header): no body class.
- **Option C** (darker near-black maroon solid bar plus a soft drop shadow) is set for posts in `blog-post-template.css` and for Points Handbook in `points-handbook.css`.
- **New pages and posts:** copy the two marker pairs from any page (or start from `blog-post-template.html` / `_templates/newsletter-post-template.html`, which already contain the full header), then run `python3 inject_header.py`. `convert_wp_to_html.py` builds posts from `blog-post-template.html`, so they get the header too. `inject_posts.py` only regenerates the blog listing and doesn't touch headers.
- **Pages without a header:** `blog-accordion.html` (a transparent embed widget) and `links.html` (the link-in-bio page, which starts with a black subscribe bar); both are listed in `NO_HEADER` in `inject_header.py`. `backend/` is the separate checkout Worker (excluded by `.assetsignore`) and is skipped.
- **Active-page highlighting:** none. The header doesn't mark the current page; the underline only shows on the dropdown that's open.
- The old `.top-nav` header markup and its JS were removed from every page (landing pages, `AprilDeal/`, `yvr-manila/`, the top-level post-style pages). The old `.top-nav` CSS still sits unused in the per-page CSS files.

---

## Cards (CARDS menu and the All cards page)

**After card changes, build travel-cards-site, then run sync_cards.py here.**

```bash
cd ~/travel-cards-site && npm run build      # writes dist/cards/cards.json (public cards only)
cd -  && python3 sync_cards.py               # updates the menu data and /cards/, then runs inject_header.py
python3 sync_cards.py --check                # exit 1 if either is out of date with cards.json (changes nothing)
```

- **Source:** the cards site (`~/travel-cards-site`, `CARDS_SITE_DIR` to override) is the single source for which cards are public, their full official names, images, groups and order. Its build exports them to `dist/cards/cards.json`; if that file is missing, `sync_cards.py` runs `npm run build` there first. Nothing else in the cards site is touched.
- **Generated, never hand-edited:** the Cards entry's `"groups"` in `site-header-nav.jsonc` (between `// cards-sync-start/end`) and the grid in `cards/index.html` (between `<!-- cards-grid-start/end -->`).
- **No hidden or test cards:** only cards in `cards.json` are listed, and the script refuses slugs like `example`/`test`/`demo`.
- **All cards page:** one group per bank under a white heading in a dark pill (AA contrast over the photo). Desktop has up to 4 tiles per row, the same size in every group; the script balances each group's rows (`--per-row`: 7 cards → 4 + 3, 5 → 3 + 2). Styles in `all-cards.css`.

---

## Caching and cache-busting

Returning visitors' browsers keep CSS and JS, so **every local CSS and JS link on every page carries a version**: `href="/all-cards.css?v=ae70a534"`, `src="/site-header.js?v=18effb22"`. The version is a short hash of the file's contents, written by `inject_header.py` (the same script that writes the header).

- **To bump it:** after changing any `.css` or `.js` file, run `python3 inject_header.py`. Every page that uses the changed file gets its new version; files you didn't change keep theirs (and stay cached). There's no number to edit by hand.
- **New pages:** link CSS/JS normally (`<link rel="stylesheet" href="my-page.css" />`), then run `inject_header.py`; it adds the `?v=`.
- **Check:** `python3 inject_header.py --check` (also run by `check_posts.py`) fails if any page has an out-of-date version, so a forgotten bump is caught before commit.
- **`_headers`** (Cloudflare) lets browsers keep `*.css` and `*.js` for a year (`public, max-age=31536000, immutable`). That's safe only because every link is versioned: always run `inject_header.py` after editing CSS/JS, or visitors keep the old file.
- **HTML** keeps Cloudflare's default, `public, max-age=0, must-revalidate` (browsers re-check it on every visit), so new `?v=` links reach visitors straight away. Don't add a `/*` rule to `_headers`: Cloudflare merges the headers of every matching rule, which would clash with the CSS/JS rules.
- Off-site links (fonts, Instagram) and `backend/` (the separate checkout Worker) aren't versioned.

## Git

```bash
# Push changes
git add .
git commit -m "Description"
git push origin main

# Sync to latest
git fetch origin
git reset --hard origin/main
```

---

## External Links

- Credit card tool: **TBD — old Milesopedia link no longer active, new link coming soon**
- YouTube: `https://www.youtube.com/@TheCanadianJetsetter`
- Social handles: `@thecanadianjetsetter`
- Contact email: `thecanadianjetsetter@gmail.com`
