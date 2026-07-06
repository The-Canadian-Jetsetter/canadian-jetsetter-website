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
│   │   └── jetsetter text logo.png   (navbar logo)
│   └── [other images]
```

---

## Design Reference

**`economy.html` is the master design reference.** Before creating or significantly editing any page, read `economy.html` to ensure consistency.

### Colors
- Dark red: `#761915`
- Cream: `#F6F2E7`
- Black (navbar/footer): `#000000`

### Navbar — Desktop
- Black background
- Logo (`TCJ Website Assets/logos/jetsetter text logo.png`) left-aligned
- Nav links centered: OFFERINGS (dropdown) / LINKS / CREDIT CARDS / BLOG / CONTACT
- Link color: `#F6F2E7`, uppercase, wide letter-spacing
- Subtle dark red bottom border
- Hover: dark red

### Navbar — Mobile (below 768px)
- Hamburger icon (three lines), right side, `#F6F2E7`
- Dropdown: black background

### Mobile Menu Structure
```
OFFERINGS (expandable)
  ├── Jetsetter Free → jetsetter-free.html
  ├── Jetsetter Economy → economy.html
  ├── Jetsetter Premium → jetsetter-premium.html
  └── Golden Visa → golden-visa.html
LINKS → links.html

BLOG → blog.html
CONTACT → contact.html
```

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
2. **Mobile responsive** — use media query breakpoint at 768px
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
