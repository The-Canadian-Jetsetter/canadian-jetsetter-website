#!/usr/bin/env python3
"""
inject_header.py — write the shared site header into pages, from site-header-nav.jsonc.

Each page needs two pairs of marker comments; everything between them is replaced:

    <head>
      ...
      <!-- site-header-head-start --><!-- site-header-head-end -->
    </head>
    <body>                      (add class="site-header-glass" for the glass bar over a hero photo)
      <!-- site-header-start --><!-- site-header-end -->

The head block loads the fonts, site-header.css and site-header.js (with a ?v= version taken from
their contents, so browsers pick up changes). The body block is the header itself.

Posts and templates also get their blog-post-template.css link's ?v= version refreshed the same way
(it holds the posts' header styling, Option C).

Re-running is idempotent; files are only written when something changed.

Usage:
    python3 inject_header.py                  every .html file in the site that has the markers
    python3 inject_header.py index.html ...   just these files (each must have the markers)
"""

import hashlib
import html as htmlmod
import json
import os
import re
import sys
from urllib.parse import quote

NAV_DATA = "site-header-nav.jsonc"
CSS_FILE = "site-header.css"
JS_FILE  = "site-header.js"
POST_CSS = "blog-post-template.css"

HEAD_START, HEAD_END = "<!-- site-header-head-start -->", "<!-- site-header-head-end -->"
BODY_START, BODY_END = "<!-- site-header-start -->", "<!-- site-header-end -->"

FONTS_HREF = "https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;700&family=Young+Serif&display=swap"

CHEVRON = ('<svg class="site-header__chevron" viewBox="0 0 24 24" width="14" height="14" '
           'aria-hidden="true"><path d="M6 9l6 6 6-6" /></svg>')

SKIP_DIRS = {"node_modules", "backend"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def esc(s):
    return htmlmod.escape(str(s), quote=True)


def url(s):
    """Escape a URL for an attribute, encoding spaces (as in 'TCJ Website Assets')."""
    return esc(quote(s, safe="/:?&=#%+@,;~"))


def card_name(name):
    """Card name with ® / ™ / * as small superscripts, as on the cards site."""
    return re.sub(r"([®™*])", r'<span class="site-header__reg">\1</span>', esc(name))


def version(path):
    with open(path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


def load_nav():
    """The menu data: JSON with whole-line // comments."""
    with open(NAV_DATA, "r", encoding="utf-8") as f:
        lines = [l for l in f if not l.lstrip().startswith("//")]
    nav = json.loads("".join(lines))
    # Hidden entries (e.g. Cards while "enabled" is false) are left out of the page entirely
    nav["items"] = [i for i in nav["items"] if i.get("enabled", True)]
    return nav


# ── Blocks ────────────────────────────────────────────────────────────────────

def head_block():
    return [
        '<link rel="preconnect" href="https://fonts.googleapis.com" />',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />',
        f'<link href="{esc(FONTS_HREF)}" rel="stylesheet" />',
        f'<link rel="stylesheet" href="/{CSS_FILE}?v={version(CSS_FILE)}" />',
        f'<script src="/{JS_FILE}?v={version(JS_FILE)}" defer></script>',
    ]


def cards_href(nav, path):
    return url(nav["cardsSiteBase"].rstrip("/") + path)


def desktop_item(nav, item):
    if item["kind"] == "link":
        return [f'<li><a class="site-header__top-link" href="{url(item["href"])}">{esc(item["label"])}</a></li>']

    pid = esc(item["id"])
    out = [
        '<li>',
        f'  <button type="button" class="site-header__top-link" aria-expanded="false" '
        f'aria-controls="site-header-panel-{pid}" data-panel-toggle="{pid}">{esc(item["label"])}{CHEVRON}</button>',
        '  <!-- Full-width panel under the bar, right after its button so keyboard users reach its links next -->',
        f'  <div class="site-header__panel" id="site-header-panel-{pid}" data-panel="{pid}">',
        '    <div class="site-header__panel-inner">',
        '      <div class="site-header__wrap">',
    ]
    if item["kind"] == "dropdown":
        out.append('        <ul class="site-header__panel-links">')
        out += [f'          <li><a href="{url(l["href"])}">{esc(l["label"])}</a></li>' for l in item["items"]]
        out.append('        </ul>')
    else:  # cards
        out += ['        <div class="site-header__panel-cards">',
                '          <ul class="site-header__card-links">']
        for c in item["cards"]:
            out.append(
                f'            <li><a href="{cards_href(nav, c["href"])}">'
                f'<img src="{cards_href(nav, c["image"])}" alt="" width="{c["width"]}" height="{c["height"]}" loading="lazy" />'
                f'<span>{card_name(c["name"])}</span></a></li>')
        out.append('          </ul>')
        all_cards = item.get("allCards", {})
        if all_cards.get("show"):
            out.append(f'          <a class="site-header__all-cards" href="{cards_href(nav, all_cards["href"])}">'
                       f'{esc(all_cards["label"])}<span class="site-header__arrow" aria-hidden="true">→</span></a>')
        out.append('        </div>')
    out += ['      </div>', '    </div>', '  </div>', '</li>']
    return out


def drawer_item(nav, item):
    if item["kind"] == "link":
        return [f'<li><a class="site-header__drawer-link" href="{url(item["href"])}">{esc(item["label"])}</a></li>']

    sid = f'site-header-sub-{esc(item["id"])}'
    out = [
        '<li>',
        f'  <button type="button" class="site-header__drawer-link" aria-expanded="false" aria-controls="{sid}" '
        f'data-sub-toggle>{esc(item["label"])}{CHEVRON}</button>',
        f'  <ul class="site-header__drawer-sub" id="{sid}" hidden>',
    ]
    if item["kind"] == "dropdown":
        out += [f'    <li><a href="{url(l["href"])}">{esc(l["label"])}</a></li>' for l in item["items"]]
    else:  # cards
        for c in item["cards"]:
            out.append(
                f'    <li><a class="site-header__sub-card" href="{cards_href(nav, c["href"])}">'
                f'<img src="{cards_href(nav, c["image"])}" alt="" width="{c["width"]}" height="{c["height"]}" loading="lazy" />'
                f'<span>{card_name(c["name"])}</span></a></li>')
        all_cards = item.get("allCards", {})
        if all_cards.get("show"):
            out.append(f'    <li><a href="{cards_href(nav, all_cards["href"])}"><span>{esc(all_cards["label"])} '
                       f'<span class="site-header__arrow" aria-hidden="true">→</span></span></a></li>')
    out += ['  </ul>', '</li>']
    return out


def indent(lines, n):
    return ["  " * n + l for l in lines]


def body_block(nav):
    logo = nav["logo"]
    img = lambda src: (f'<img class="site-header__logo" src="{url(src)}" alt="{esc(logo["alt"])}" '
                       f'width="{logo["width"]}" height="{logo["height"]}" />')
    out = [
        '<header class="site-header" data-site-header>',
        '  <div class="site-header__bar">',
        '    <div class="site-header__wrap site-header__bar-inner">',
        f'      <a href="{url(logo["href"])}" class="site-header__brand">{img(logo["src"])}</a>',
        '',
        '      <!-- Desktop menu -->',
        '      <nav class="site-header__desktop" aria-label="Main">',
        '        <ul class="site-header__top">',
    ]
    for item in nav["items"]:
        out += indent(desktop_item(nav, item), 5)
    out += [
        '        </ul>',
        '      </nav>',
        '',
        '      <!-- Mobile menu button -->',
        '      <button type="button" class="site-header__menu-button" aria-expanded="false" '
        'aria-controls="site-header-drawer" data-drawer-open>',
        '        <svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" /></svg>',
        '        <span class="site-header__vh">Menu</span>',
        '      </button>',
        '    </div>',
        '  </div>',
        '',
        '  <!-- Mobile drawer -->',
        '  <div class="site-header__scrim" data-drawer-scrim></div>',
        '  <div class="site-header__drawer" id="site-header-drawer" role="dialog" aria-modal="true" aria-label="Menu" data-drawer>',
        '    <div class="site-header__drawer-head">',
        f'      <span class="site-header__brand">{img(logo["panelSrc"])}</span>',
        '      <button type="button" class="site-header__drawer-close" data-drawer-close>',
        '        <svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" /></svg>',
        '        <span class="site-header__vh">Close menu</span>',
        '      </button>',
        '    </div>',
        '    <nav aria-label="Main">',
        '      <ul class="site-header__drawer-list">',
    ]
    for item in nav["items"]:
        out += indent(drawer_item(nav, item), 4)
    out += [
        '      </ul>',
        '    </nav>',
        '  </div>',
        '</header>',
    ]
    return out


# ── Injection ─────────────────────────────────────────────────────────────────

def replace_between(html, start, end, lines):
    """Replace what's between the markers, indenting the block to match the start marker."""
    m = re.search(r"^([ \t]*)" + re.escape(start) + r".*?" + re.escape(end), html, re.S | re.M)
    if not m:
        return None
    pad = m.group(1)
    block = "\n".join(pad + l if l else "" for l in lines)
    return html[:m.start()] + f"{pad}{start}\n{block}\n{pad}{end}" + html[m.end():]


def inject(path, head, body):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    new = replace_between(html, HEAD_START, HEAD_END, head)
    new = new and replace_between(new, BODY_START, BODY_END, body)
    if new is None:
        return "missing markers"
    new = re.sub(r'(href="(?:\.\./)?' + re.escape(POST_CSS) + r')(?:\?v=[0-9a-f]+)?"',
                 rf'\1?v={version(POST_CSS)}"', new)
    if new == html:
        return "unchanged"
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)
    return "updated"


def pages_with_markers():
    found = []
    for d, dirs, files in os.walk("."):
        dirs[:] = sorted(x for x in dirs if not x.startswith(".") and x not in SKIP_DIRS)
        for name in sorted(files):
            if name.endswith(".html"):
                path = os.path.normpath(os.path.join(d, name))
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    if BODY_START in f.read():
                        found.append(path)
    return found


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    given = [os.path.abspath(p) for p in sys.argv[1:]]
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    nav = load_nav()
    head, body = head_block(), body_block(nav)

    paths = [os.path.relpath(p) for p in given] or pages_with_markers()
    failed = False
    for path in paths:
        result = inject(path, head, body)
        failed |= result == "missing markers"
        print(f"  {result:<16} {path}")

    print(f"\n{len(paths)} page(s) checked.")
    if failed:
        sys.exit("Some pages are missing the site-header markers (see above).")


if __name__ == "__main__":
    main()
