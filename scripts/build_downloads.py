#!/usr/bin/env python3
"""Build zip files that are ready to edit and deploy.

Each zip is one template folder: index.html with the gallery bar removed,
plus a short README. Run this after changing a template:

    python3 scripts/build_downloads.py
"""

import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
OUT = ROOT / "downloads"

NOTE = """\
This folder is ready to edit and deploy.

1. Open index.html in any text editor.
2. Replace every value marked data-field: your name, role, projects, email, and links.
   Sample names and projects are fictional.
3. Preview by opening index.html in a browser. Fonts load from Google Fonts, so you need a network connection for the first look.
4. Upload this folder to GitHub Pages (branch main, folder /), Netlify, Cloudflare Pages, or any static host.
   The entry file is index.html.

Photography template only: replace a frame's background with your own image, for example
style="background-image: url('photos/coast.jpg')", and put the image in a photos folder next to index.html.
"""


def ready(html: str) -> str:
    html = re.sub(
        r'\s*<a class="template-gallery"[^>]*>.*?</a>\s*',
        "\n",
        html,
        count=1,
        flags=re.DOTALL,
    )
    html = html.replace("--gallery-bar: 34px;", "--gallery-bar: 0px;", 1)
    if 'class="template-gallery"' in html:
        raise SystemExit("Gallery link still present after cleanup")
    if "--gallery-bar: 34px" in html:
        raise SystemExit("Gallery bar offset still present after cleanup")
    return html


def main() -> None:
    folders = sorted(path for path in TEMPLATES.iterdir() if (path / "index.html").is_file())
    if not folders:
        raise SystemExit(f"No templates found in {TEMPLATES}")
    OUT.mkdir(exist_ok=True)
    built = []
    for folder in folders:
        html = ready((folder / "index.html").read_text(encoding="utf-8"))
        zip_path = OUT / f"{folder.name}.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(f"{folder.name}/index.html", html)
            archive.writestr(f"{folder.name}/README.txt", NOTE)
        built.append(folder.name)
        print(f"wrote {zip_path.relative_to(ROOT)}")

    all_path = OUT / "all-templates.zip"
    with zipfile.ZipFile(all_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in built:
            with zipfile.ZipFile(OUT / f"{name}.zip") as one:
                for info in one.infolist():
                    archive.writestr(info.filename, one.read(info.filename))
    print(f"wrote {all_path.relative_to(ROOT)} ({len(built)} templates)")


if __name__ == "__main__":
    main()
