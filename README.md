# Portfolio Templates

Single-file HTML portfolios. Open one in the browser, or download a zip, replace the sample copy, and upload the folder.

19 designs, each with two color themes, for 38 downloadable variants. No build step, no framework; fonts load from Google Fonts.

The gallery is published from this repository’s `main` branch, folder `/`.

https://ccavins.github.io/Portfolio_Templates/

## Templates

| # | Template | For | Shape | Themes |
| --- | --- | --- | --- | --- |
| 01 | Aurora | Producers and technical program managers | Dark sidebar, glass panels, particle field | Ocean (dark), Ember (dark) |
| 02 | Editorial | Strategists and writers | Paper magazine page | Paper (light), Night (dark) |
| 03 | Signal | Software engineers | Project index with a note that updates | Acid (dark), Paper (light) |
| 04 | Atelier | Art directors and studios | Large type, color that shifts with the work | Paper (light), Concrete (dark) |
| 05 | Monograph | Architects and researchers | Sticky cover beside a project list | Forest (light), Oxblood (dark) |
| 06 | Bento | A personal home page | Tile grid: now, work, contact | Stone (light), Midnight (dark) |
| 07 | Vita | A job search | One-page résumé that prints | Classic (light), Navy (dark) |
| 08 | Plate | Photographers | Contact sheet with a lightbox; swap the frames for images | Darkroom (dark), Gallery (light) |
| 09 | Proof | Product designers | Case studies that lead with the outcome | Paper (light), Slate (dark) |
| 10 | Ledger | Freelancers and consultants | Services with prices, process steps, testimonials, a booking link | Linen (light), Graphite (dark) |
| 11 | Thesis | Academics and researchers | Publications by year, teaching, talks, CV link | Ivory (light), Oxford (dark) |
| 12 | Reel | Directors, editors, motion designers | Showreel first, then filmography, credits, stills | Cinema (dark), Daylight (light) |
| 13 | Marquee | Bands and musicians | Listen links, tour dates, releases, press | Neon (dark), Vinyl (light) |
| 14 | Folio | Illustrators and visual artists | Masonry wall of work with a lightbox | Cream (light), Charcoal (dark) |
| 15 | Dispatch | Journalists | Clippings grouped by beat, newsletter signup | Newsprint (light), Broadsheet (dark) |
| 16 | Cohort | Teachers, coaches, workshop leaders | Offers, upcoming sessions, quotes, FAQ | Sage (light), Plum (dark) |
| 17 | Primer | Students and first portfolios | Three projects with “what I did / what I learned” | Sky (light), Dusk (dark) |
| 18 | Collective | Small studios and agencies | Numbered services, clients, team, approach | Bone (light), Carbon (dark) |
| 19 | Pixel | Indie game developers | Project cards with screenshots, tags, store links, dev log | Arcade (dark), Mono (light) |

Names, jobs, and projects in the templates are fictional.

## Edit and deploy

1. On the gallery, filter by category or light/dark, then choose **Download zip** under the variant you want. [downloads/all-templates.zip](downloads/all-templates.zip) has every design in its default theme.
2. Unzip it. You get a folder with `index.html` and `README.txt`.
3. In `index.html`, read the numbered **HOW TO EDIT** comment at the top, then replace every value marked `data-field` (name, role, projects, email, links). Sections that repeat are wrapped in `<!-- ===== SECTION ... ===== -->` comments; copy one block to add another project, date, or publication.
4. Open `index.html` in a browser to preview. Fonts load from Google Fonts.
5. Upload that folder to any static host. On GitHub Pages, use branch `main` and folder `/`. The entry file is `index.html`.

The zip has already removed the “All templates” bar. If you copy a file from `templates/` instead, delete that link before you publish.

Plate and Folio expect your own images. Notes at the top of their HTML show how to point a frame at a photo in a `photos/` or `art/` folder next to `index.html`. Reel expects a YouTube or Vimeo embed in place of the showreel placeholder; the exact snippet is in its head comment.

## Themes

Every template carries all of its color themes in the same file. The active one is set on the root element:

```html
<html lang="en" data-theme="ocean">
```

Change that value to any theme id from the table above (lowercase) to switch. Each theme is a block of CSS variables under the `THEMES` comment in the stylesheet; copy one, rename it, and change the colors to make your own. The downloaded zip is already set to the theme you picked in the gallery.

While previewing inside this repository you can also append `?theme=<id>` to a template URL to try another theme without editing the file.

## Rebuild the gallery and zips

`templates/catalog.json` is the source of truth for names, categories, descriptions, tags, and themes. After you change a template or the catalog, run:

```bash
python3 scripts/build.py
```

The script validates every template (theme attribute, one CSS block per theme, gallery bar, how-to-edit comment), regenerates the cards and counts in `index.html` between the `cards:start`/`cards:end` and `stats:start`/`stats:end` markers, and writes one zip per theme variant to `downloads/` (`<slug>-<theme>.zip`), plus `<slug>.zip` for each default theme and `downloads/all-templates.zip`. Each archive is a folder with `index.html` and a generated `README.txt`, ready to upload.

### Adding a template

1. Create `templates/<slug>/index.html` following an existing template: a `HOW TO EDIT` comment, `data-theme` on `<html>`, a `:root, [data-theme="default"]` block plus one `[data-theme="..."]` block per extra theme, the `.template-gallery` link, and `data-field` on editable copy.
2. Add an entry to `templates/catalog.json` with its slug, category, description, tags, and themes (`id`, `label`, `mode`).
3. Run `python3 scripts/build.py` and open `index.html`.
