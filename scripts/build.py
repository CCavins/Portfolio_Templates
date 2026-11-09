#!/usr/bin/env python3
"""Build the gallery page and the downloadable zips from templates/catalog.json.

    python3 scripts/build.py

What it does:

1. Validates every template against the catalog: the <html> tag carries
   data-theme, every catalog theme id exists in the stylesheet, and the
   gallery bar is present so it can be removed.
2. Rewrites the card grid in index.html (between the cards:start and
   cards:end markers) and the counts in the header and hero.
3. Writes downloads/<slug>-<theme>.zip for every design and theme, each with
   index.html set to that theme and a README.txt written for that template.
   downloads/<slug>.zip is the default theme, and downloads/all-templates.zip
   holds the default theme of every design.
"""

import html as html_lib
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
CATALOG = TEMPLATES / "catalog.json"
INDEX = ROOT / "index.html"
OUT = ROOT / "downloads"

CARDS_START = "<!-- cards:start -->"
CARDS_END = "<!-- cards:end -->"
STATS_START = "<!-- stats:start -->"
STATS_END = "<!-- stats:end -->"


# --------------------------------------------------------------------------- #
# Catalog
# --------------------------------------------------------------------------- #


def load_catalog() -> dict:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    seen = set()
    for entry in data["templates"]:
        for key in ("slug", "name", "category", "for", "description", "tags", "themes", "sections"):
            if key not in entry:
                raise SystemExit(f"{entry.get('slug', '?')}: catalog entry is missing '{key}'")
        if entry["slug"] in seen:
            raise SystemExit(f"duplicate slug in catalog: {entry['slug']}")
        seen.add(entry["slug"])
        if not entry["themes"]:
            raise SystemExit(f"{entry['slug']}: needs at least one theme")
        if entry["category"] not in data["categories"]:
            raise SystemExit(f"{entry['slug']}: unknown category {entry['category']!r}")
        entry.setdefault("notes", [])
    return data


def slugify(text: str) -> str:
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")


# --------------------------------------------------------------------------- #
# Template preparation
# --------------------------------------------------------------------------- #

HTML_TAG = re.compile(r"<html\b[^>]*>")
THEME_ATTR = re.compile(r'(\bdata-theme=")[^"]*(")')
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def without_comments(source: str) -> str:
    """The HOW TO EDIT comments mention markup; strip them before checking for real tags."""
    return COMMENT.sub("", source)


def validate(entry: dict, source: str) -> None:
    slug = entry["slug"]
    tag = HTML_TAG.search(source)
    if not tag or 'data-theme="' not in tag.group(0):
        raise SystemExit(f"{slug}: <html> tag needs a data-theme attribute")
    for theme in entry["themes"]:
        selector = f'[data-theme="{theme["id"]}"]'
        if selector not in source:
            raise SystemExit(f"{slug}: stylesheet has no {selector} block")
    if 'class="template-gallery"' not in without_comments(source):
        raise SystemExit(f"{slug}: missing the .template-gallery link")
    if "--gallery-bar: 34px;" not in source:
        raise SystemExit(f"{slug}: missing --gallery-bar: 34px; in :root")
    if "HOW TO EDIT" not in source:
        raise SystemExit(f"{slug}: missing the HOW TO EDIT comment")


def set_theme(source: str, theme_id: str) -> str:
    tag = HTML_TAG.search(source)
    new_tag = THEME_ATTR.sub(lambda m: f'{m.group(1)}{theme_id}{m.group(2)}', tag.group(0), count=1)
    return source[: tag.start()] + new_tag + source[tag.end():]


def ready(source: str, theme_id: str) -> str:
    """Return a copy of the template ready to publish: themed, gallery bar removed."""
    out = set_theme(source, theme_id)
    # The real link always has an href; the HOW TO EDIT comment mentions the tag without one.
    out = re.sub(
        r'\s*<a class="template-gallery" href="[^"]*">[^<]*</a>\s*',
        "\n",
        out,
        count=1,
    )
    out = out.replace("--gallery-bar: 34px;", "--gallery-bar: 0px;", 1)
    if 'class="template-gallery"' in without_comments(out):
        raise SystemExit("Gallery link still present after cleanup")
    if "--gallery-bar: 34px" in out:
        raise SystemExit("Gallery bar offset still present after cleanup")
    return out


def readme(entry: dict, theme: dict) -> str:
    others = [t for t in entry["themes"] if t["id"] != theme["id"]]
    other_text = ", ".join(f'"{t["id"]}" ({t["label"]})' for t in others) or "no other themes"
    notes = ""
    if entry["notes"]:
        notes = "NOTES FOR THIS TEMPLATE\n" + "".join(f"- {n}\n" for n in entry["notes"]) + "\n"
    sections = ", ".join(entry["sections"])
    return f"""{entry['name']} — {theme['label']} theme
A single-file portfolio for {entry['for'].lower()}.

WHAT IS IN THIS FOLDER
  index.html   the whole site: HTML, CSS, and a little JavaScript in one file
  README.txt   this file

EDIT THE TEXT
1. Open index.html in any plain-text editor (VS Code, Sublime, Notepad, TextEdit in plain-text mode).
2. The top of the file has a HOW TO EDIT comment that walks through the page.
3. Replace every value marked data-field="...": your name, role, projects, email, and links.
   Sample names, companies, and projects are fictional.
4. Sections in this template: {sections}.
   Each repeating block (a project, a job, a quote) is wrapped in a comment that says how to copy it.
5. Update the <title> and the two meta descriptions near the top; search engines and link previews read them.

COLOR THEMES
This copy is set to the "{theme['id']}" theme. The same file also contains: {other_text}.
To switch, change data-theme="{theme['id']}" on the <html> tag at the top of index.html.
Every color lives in the :root and [data-theme] blocks at the start of the <style> tag, so you can
also edit a theme or add your own.

{notes}PREVIEW
Double-click index.html to open it in a browser. Fonts load from Google Fonts, so the first look
needs a network connection. You can also preview another theme without editing by opening
index.html?theme={others[0]['id'] if others else theme['id']} in the browser.

PUBLISH
Upload this folder to any static host. The entry file is index.html.
- GitHub Pages: create a repository, upload the files, then Settings > Pages > branch main, folder /.
- Netlify or Cloudflare Pages: drag the folder onto the dashboard.
"""


# --------------------------------------------------------------------------- #
# Gallery cards
# --------------------------------------------------------------------------- #


def card(entry: dict, theme: dict, number: int) -> str:
    slug = entry["slug"]
    e = html_lib.escape
    view = f"templates/{slug}/index.html?theme={theme['id']}"
    preview = f"templates/{slug}/index.html?preview=1&amp;theme={theme['id']}"
    zip_name = f"{slug}-{theme['id']}.zip"
    label = f"{entry['name']}, {theme['label']} theme"
    tags = "".join(f"<li>{e(t)}</li>" for t in [theme["mode"].title(), *entry["tags"]])
    return f"""      <article class="card" data-category="{slugify(entry['category'])}" data-mode="{theme['mode']}" data-slug="{slug}">
        <div class="preview">
          <iframe data-preview src="{preview}" title="Preview of {e(label)}" loading="lazy" tabindex="-1"></iframe>
          <a class="preview-hit" href="{view}" aria-label="View {e(label)}"></a>
        </div>
        <div class="card-body">
          <div class="card-top">
            <h3>{e(entry['name'])} <span class="variant">{e(theme['label'])}</span></h3>
            <span class="num">{number:02d}</span>
          </div>
          <p class="for">For {e(entry['for'].lower())}.</p>
          <p>{e(entry['description'])}</p>
          <ul class="tags">{tags}</ul>
          <div class="actions">
            <a class="open" href="{view}">View template</a>
            <a class="download" href="downloads/{zip_name}" download="{zip_name}">Download zip</a>
          </div>
        </div>
      </article>
"""


def render_cards(data: dict) -> str:
    numbers = {entry["slug"]: i + 1 for i, entry in enumerate(data["templates"])}
    parts = []
    for category in data["categories"]:
        entries = [t for t in data["templates"] if t["category"] == category]
        if not entries:
            continue
        cat_id = slugify(category)
        designs = len(entries)
        variants = sum(len(t["themes"]) for t in entries)
        parts.append(f"""    <section class="group" data-category="{cat_id}" aria-labelledby="group-{cat_id}">
      <h2 class="group-title" id="group-{cat_id}">{html_lib.escape(category)} <span>{designs} design{'s' if designs != 1 else ''} · {variants} themes</span></h2>
      <div class="grid">
""")
        for entry in entries:
            for theme in entry["themes"]:
                parts.append(card(entry, theme, numbers[entry["slug"]]))
        parts.append("      </div>\n    </section>\n")
    return "".join(parts)


def replace_between(source: str, start: str, end: str, body: str, what: str) -> str:
    a = source.find(start)
    b = source.find(end)
    if a == -1 or b == -1 or b < a:
        raise SystemExit(f"index.html is missing the {what} markers")
    return source[: a + len(start)] + "\n" + body + source[b:]


def update_index(data: dict) -> None:
    source = INDEX.read_text(encoding="utf-8")
    designs = len(data["templates"])
    themes = sum(len(t["themes"]) for t in data["templates"])
    stats = f"{designs} designs · {themes} color themes"
    source = replace_between(source, CARDS_START, CARDS_END, render_cards(data), "cards")
    source = re.sub(
        re.escape(STATS_START) + r".*?" + re.escape(STATS_END),
        f"{STATS_START}{stats}{STATS_END}",
        source,
        flags=re.DOTALL,
    )
    INDEX.write_text(source, encoding="utf-8")
    print(f"updated index.html ({stats})")


# --------------------------------------------------------------------------- #
# Zips
# --------------------------------------------------------------------------- #


def write_zip(path: Path, folder: str, page: str, note: str) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"{folder}/index.html", page)
        archive.writestr(f"{folder}/README.txt", note)


def build_zips(data: dict) -> None:
    OUT.mkdir(exist_ok=True)
    produced = set()
    defaults = []
    for entry in data["templates"]:
        slug = entry["slug"]
        source_path = TEMPLATES / slug / "index.html"
        if not source_path.is_file():
            raise SystemExit(f"{slug}: templates/{slug}/index.html does not exist")
        source = source_path.read_text(encoding="utf-8")
        validate(entry, source)
        for i, theme in enumerate(entry["themes"]):
            page = ready(source, theme["id"])
            note = readme(entry, theme)
            name = f"{slug}-{theme['id']}.zip"
            write_zip(OUT / name, slug, page, note)
            produced.add(name)
            if i == 0:
                write_zip(OUT / f"{slug}.zip", slug, page, note)
                produced.add(f"{slug}.zip")
                defaults.append((slug, page, note))
        print(f"wrote downloads/{slug}*.zip ({len(entry['themes'])} themes)")

    all_path = OUT / "all-templates.zip"
    with zipfile.ZipFile(all_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for slug, page, note in defaults:
            archive.writestr(f"{slug}/index.html", page)
            archive.writestr(f"{slug}/README.txt", note)
    produced.add(all_path.name)
    print(f"wrote downloads/all-templates.zip ({len(defaults)} templates)")

    for stale in OUT.glob("*.zip"):
        if stale.name not in produced:
            stale.unlink()
            print(f"removed stale downloads/{stale.name}")


def main() -> None:
    data = load_catalog()
    for folder in sorted(p for p in TEMPLATES.iterdir() if p.is_dir()):
        if folder.name not in {t["slug"] for t in data["templates"]}:
            print(f"warning: templates/{folder.name} is not in catalog.json and will be skipped", file=sys.stderr)
    build_zips(data)
    update_index(data)


if __name__ == "__main__":
    main()
