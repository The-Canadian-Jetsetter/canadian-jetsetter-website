#!/usr/bin/env python3
"""
check_posts.py — sanity-check posts.json against the posts/ folder.
Run BEFORE committing any blog change. posts.json is the single source of
truth; inject_posts.py regenerates blog.html and index.html from it.
Catches: (1) a posts/ file with no entry (invisible on site), (2) an entry
whose file is missing, (3) off-site or missing featured images, (4) bad dates.
Exits non-zero on any problem.
"""
import json, os, re, sys

d = json.load(open("posts.json", encoding="utf-8"))
entries = {p.get("slug"): p for p in d}
files = {f[:-5] for f in os.listdir("posts") if f.endswith(".html")}
problems = []

for slug in sorted(files - set(entries)):
    problems.append(f"NOT LISTED : posts/{slug}.html has no posts.json entry (invisible on site)")
for slug in sorted(set(entries) - files):
    if slug:
        problems.append(f"NO FILE    : posts.json entry '{slug}' has no posts/{slug}.html")
for p in d:
    slug = p.get("slug", "(no slug)")
    if not p.get("slug"):
        problems.append(f"NO SLUG    : entry '{p.get('title','?')[:40]}' is missing a slug")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(p.get("date", ""))):
        problems.append(f"BAD DATE   : {slug} date is '{p.get('date')}' (expected YYYY-MM-DD)")
    fi = str(p.get("featured_image", ""))
    if fi.startswith("http"):
        problems.append(f"EXTERNAL IMG: {slug} featured_image points off-site ({fi[:50]})")
    elif fi and not os.path.exists(fi):
        problems.append(f"MISSING IMG: {slug} featured_image not found: {fi}")
    elif not fi:
        problems.append(f"NO IMAGE   : {slug} has no featured_image")

if problems:
    print(f"{len(problems)} problem(s) found:\n")
    for x in problems: print("  " + x)
    print("\nFix these (usually: add the post to posts.json, then run inject_posts.py) before committing.")
    sys.exit(1)
print(f"OK - posts.json clean: {len(d)} entries, all with files, local images, valid dates.")
sys.exit(0)
