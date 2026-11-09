# Portfolio Templates

Single-file HTML portfolios. Open one in the browser, or download a zip, replace the sample copy, and upload the folder.

The gallery is published from this repository’s `main` branch, folder `/`.

https://ccavins.github.io/Portfolio_Templates/

## Templates

| Template | For | Shape |
| --- | --- | --- |
| Aurora | Producers and technical program managers | Dark sidebar, glass panels, particle field |
| Editorial | Strategists and writers | Paper magazine page |
| Signal | Software engineers | Project index with a note that updates |
| Atelier | Art directors and studios | Large type, color that shifts with the work |
| Monograph | Architects and researchers | Sticky cover beside a project list |
| Bento | A personal home page | Tile grid: now, work, contact |
| Vita | A job search | One-page résumé that prints |
| Plate | Photographers | Contact sheet; swap the frames for images |
| Proof | Product designers | Case studies that lead with the outcome |

Names, jobs, and projects in the templates are fictional.

## Edit and deploy

1. On the gallery, choose **Download zip**, or take everything in [downloads/all-templates.zip](downloads/all-templates.zip).
2. Unzip it. You get a folder with `index.html` and `README.txt`.
3. In `index.html`, replace every value marked `data-field` (name, role, projects, email, links).
4. Open `index.html` in a browser to preview. Fonts load from Google Fonts.
5. Upload that folder to any static host. On GitHub Pages, use branch `main` and folder `/`. The entry file is `index.html`.

The zip has already removed the “All templates” bar. If you copy a file from `templates/` instead, delete that link before you publish.

Plate is the one template that expects your own images. A note at the top of its HTML shows how to point a frame at a photo in a `photos/` folder.

## Rebuild the zips

After you change a template, regenerate the downloads:

```bash
python3 scripts/build_downloads.py
```

That writes one zip per template plus `downloads/all-templates.zip`. Each archive is a folder ready to upload.
