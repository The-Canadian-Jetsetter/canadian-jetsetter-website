#!/usr/bin/env python3
"""
sync_cards.py — bring the CARDS menu and the All cards page (/cards/) in line with the cards site.

The cards site (~/travel-cards-site) is the single source for which cards exist, their full official
names, images, groups and order. Its build exports the PUBLIC cards (hidden and test cards are never in it)
to dist/cards/cards.json. This script reads that file and writes:

  site-header-nav.jsonc   the Cards entry's "groups" (between // cards-sync-start / // cards-sync-end)
  cards/index.html        the All cards grid (between <!-- cards-grid-start --> / <!-- cards-grid-end -->)

then runs inject_header.py, which writes the menu into every page and refreshes the ?v= versions.

After card changes:  build travel-cards-site (npm run build there), then run  python3 sync_cards.py  here.

Usage:
    python3 sync_cards.py           write both files (only if changed), then run inject_header.py
    python3 sync_cards.py --check   exit 1 if either file is out of date with cards.json (changes nothing)

CARDS_SITE_DIR overrides the cards site's folder (default ~/travel-cards-site). If dist/cards/cards.json is
missing, the script runs `npm run build` there first (writing only into the cards site's own dist/).
"""

import html as htmlmod
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CARDS_SITE = os.path.expanduser(os.environ.get("CARDS_SITE_DIR", "~/travel-cards-site"))
CARDS_JSON = os.path.join(CARDS_SITE, "dist", "cards", "cards.json")

NAV_DATA = os.path.join(HERE, "site-header-nav.jsonc")
PAGE = os.path.join(HERE, "cards", "index.html")

NAV_START, NAV_END = "// cards-sync-start", "// cards-sync-end"
PAGE_START, PAGE_END = "<!-- cards-grid-start -->", "<!-- cards-grid-end -->"

BASE = "https://thecanadianjetsetter.com"
# Desktop All cards grid: at most this many tiles per row; each group's rows are balanced (7 -> 4 + 3, 5 -> 3 + 2)
MAX_PER_ROW = 4
# The first desktop row loads straight away; the rest lazily
EAGER_IMAGES = MAX_PER_ROW
# Never list these, even if they somehow reach cards.json
BLOCKED_SLUG = re.compile(r"(^|-)(example|test|sample|demo|draft|hidden)(-|$)")


def fail(msg):
    sys.exit(f"sync_cards: {msg}")


def esc(s):
    return htmlmod.escape(str(s), quote=True)


# ── Card data ─────────────────────────────────────────────────────────────────

def load_cards():
    """The cards site's public cards, as [{heading, cards: [...]}] in menu order. Checks every entry."""
    if not os.path.exists(CARDS_JSON):
        if not os.path.isdir(CARDS_SITE):
            fail(f"can't find the cards site at {CARDS_SITE} (set CARDS_SITE_DIR)")
        print(f"{CARDS_JSON} is missing: running npm run build in {CARDS_SITE} ...")
        subprocess.run(["npm", "run", "build"], cwd=CARDS_SITE, check=True)
        if not os.path.exists(CARDS_JSON):
            fail(f"the cards site's build didn't write {CARDS_JSON}")

    with open(CARDS_JSON, encoding="utf-8") as f:
        data = json.load(f)

    group_order = {g["name"]: g["order"] for g in data.get("groups", [])}
    groups = {}
    seen = set()
    for c in data.get("cards", []):
        slug = c.get("slug", "")
        where = f"card {slug or '?'} in {CARDS_JSON}"
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
            fail(f"{where}: bad slug")
        if BLOCKED_SLUG.search(slug):
            fail(f"{where}: looks like a test or hidden card; it must not be public")
        if slug in seen:
            fail(f"{where}: listed twice")
        seen.add(slug)
        for k in ("name", "url", "image", "imageWidth", "imageHeight", "group", "order"):
            if c.get(k) in (None, ""):
                fail(f"{where}: no {k}")
        if c["url"] != f"{BASE}/cards/{slug}/":
            fail(f"{where}: url should be {BASE}/cards/{slug}/")
        if not c["image"].startswith(f"{BASE}/cards/images/"):
            fail(f"{where}: image should be under {BASE}/cards/images/")
        g = c["group"]
        groups.setdefault(g, []).append(c)

    if not groups:
        fail(f"no cards in {CARDS_JSON}")

    # Groups by their order (cards.json "groups", else the cards' groupOrder); cards by "order" within a group
    def g_rank(name):
        return group_order.get(name, groups[name][0].get("groupOrder", math.inf))

    return [{"heading": name, "cards": sorted(groups[name], key=lambda c: c["order"])}
            for name in sorted(groups, key=g_rank)]


def path_of(full_url):
    """https://thecanadianjetsetter.com/cards/x/ -> /cards/x/ (the menu data adds its cardsBase back)."""
    return full_url[len(BASE):]


# ── Menu data (site-header-nav.jsonc) ─────────────────────────────────────────

def nav_lines(groups):
    out = ['"groups": [']
    for gi, g in enumerate(groups):
        out.append(f'  {{ "heading": {json.dumps(g["heading"], ensure_ascii=False)}, "cards": [')
        for ci, c in enumerate(g["cards"]):
            entry = json.dumps({"name": c["name"], "href": path_of(c["url"]), "image": path_of(c["image"]),
                                "width": c["imageWidth"], "height": c["imageHeight"]}, ensure_ascii=False)
            out.append(f'    {entry}{"," if ci < len(g["cards"]) - 1 else ""}')
        out.append(f'  ] }}{"," if gi < len(groups) - 1 else ""}')
    out.append('],')
    return out


# ── All cards page (cards/index.html) ─────────────────────────────────────────

def card_name(name):
    """® / ™ / * as small superscripts (styled by .card-name sup in all-cards.css)."""
    return re.sub(r"([®™*])", r"<sup>\1</sup>", esc(name))


def page_lines(groups):
    out = []
    n = 0
    for g in groups:
        gid = "group-" + re.sub(r"[^a-z0-9]+", "-", g["heading"].lower()).strip("-")
        count = len(g["cards"])
        per_row = math.ceil(count / math.ceil(count / MAX_PER_ROW))  # balanced rows on desktop
        out += [f'<div class="card-group" role="group" aria-labelledby="{gid}">',
                f'  <h2 class="card-group-heading" id="{gid}"><span>{esc(g["heading"])}</span></h2>',
                f'  <ul class="card-grid" style="--per-row: {per_row}">']
        for c in g["cards"]:
            lazy = "" if n < EAGER_IMAGES else ' loading="lazy"'
            n += 1
            out += ['    <li>',
                    f'      <a class="card-tile" href="{esc(c["url"])}">',
                    f'        <img src="{esc(c["image"])}" alt="" width="{c["imageWidth"]}" height="{c["imageHeight"]}"{lazy} />',
                    f'        <span class="card-box"><span class="card-name">{card_name(c["name"])}</span></span>',
                    '      </a>',
                    '    </li>']
        out += ['  </ul>', '</div>']
    return out


# ── Writing ───────────────────────────────────────────────────────────────────

def replace_between(text, start, end, lines, path):
    """Replace the lines between the start and end markers, indented like the start marker."""
    m = re.search(r"^([ \t]*)" + re.escape(start) + r"[^\n]*\n(.*?)^[ \t]*" + re.escape(end), text, re.S | re.M)
    if not m:
        fail(f"no {start} … {end} markers in {path}")
    pad = m.group(1)
    body = "".join(pad + l + "\n" for l in lines)
    return text[:m.start(2)] + body + text[m.end(2):]


def main():
    check = sys.argv[1:] == ["--check"]
    if sys.argv[1:] and not check:
        fail("usage: python3 sync_cards.py [--check]")

    groups = load_cards()
    targets = [(NAV_DATA, NAV_START, NAV_END, nav_lines(groups)),
               (PAGE, PAGE_START, PAGE_END, page_lines(groups))]
    stale = 0
    for path, start, end, lines in targets:
        with open(path, encoding="utf-8") as f:
            old = f.read()
        new = replace_between(old, start, end, lines, path)
        rel = os.path.relpath(path, HERE)
        if new == old:
            print(f"  unchanged    {rel}")
            continue
        stale += 1
        if check:
            print(f"  OUT OF DATE  {rel}")
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            print(f"  updated      {rel}")

    total = sum(len(g["cards"]) for g in groups)
    summary = ", ".join(f'{g["heading"]} {len(g["cards"])}' for g in groups)
    if check:
        if stale:
            sys.exit(f"\n{stale} file(s) out of date with {CARDS_JSON}: run python3 sync_cards.py")
        print(f"\nOK - the CARDS menu and All cards page match the cards site ({total} cards: {summary}).")
        return

    print(f"\n{total} cards ({summary}). Running inject_header.py ...\n")
    subprocess.run([sys.executable, os.path.join(HERE, "inject_header.py")], cwd=HERE, check=True)


if __name__ == "__main__":
    main()
