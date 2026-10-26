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
4. Run `python3 check_posts.py` — it must pass before committing.

---

## Site header

The header is shared with the cards site and written into every page by `inject_header.py`, between `<!-- site-header-head-start/end -->` (in `<head>`) and `<!-- site-header-start/end -->` (in `<body>`) markers. Never hand-edit between the markers.

- **Files:** `site-header.css` (styles), `site-header.js` (dropdown, mobile menu, glass-to-solid on scroll), `site-header-nav.jsonc` (menu data: every link, the logos, and the cards site address `cardsSiteBase`).
- **After any change** to the menu data, `site-header.css`, `site-header.js` or `blog-post-template.css`, run `python3 inject_header.py`. It rewrites the header on every page with the markers and refreshes the `?v=` version tags so browsers load the change.
- **CARDS menu:** switched off for now. To show it, change `"enabled": false` to `"enabled": true` on the Cards entry in `site-header-nav.jsonc` (a comment marks the line), then run `inject_header.py`.
- **Glass or solid bar, per page:**
  - Glass (over a hero photo): `<body class="site-header-glass">` and `data-site-header-hero` on the hero element. The hero extends up behind the bar; the page's own CSS sets `--site-header-hero-pad` (and `--site-header-hero-min` if the hero has a min-height) next to the hero's own values, so its content stays in place.
  - Solid (no photo behind the header): no body class.
- **Option C** (darker near-black maroon solid bar plus a soft drop shadow) is set for posts in `blog-post-template.css` and for Points Handbook in `points-handbook.css`.
- **Still on the old header** (not converted yet): `landing-pages/`, `AprilDeal/`, `backend/`, `yvr-manila/`, `flying-with-your-dog.html`, the top-level post-style pages (`newsletter-april-9-2026.html`, `newsletter-april-13-2026.html`, `scotiabank-fx-fees.html`, `westjet-triangle-rewards.html`, `blog-post.html`), and `blog-accordion.html` (no header at all). The old `.top-nav` CSS stays in the per-page CSS files for them.

---

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
