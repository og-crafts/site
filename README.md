# ogcrafts.cloud

The OGCrafts home site: a static site built by `build.py` (Python 3, no dependencies) into `dist/`.

- `apps.json`: the crafts, in display order. Add an entry here (and a `DETAILS` entry in `build.py` for a detail page, plus its images under `src/assets/apps/<id>/`) to add a craft.
- `src/site.css`: styles. The two `:root` token blocks are checked for WCAG AA contrast by the build.
- `python3 build.py --strict` builds and fails on a broken link, missing alt text, duplicate ids, a page without exactly one h1, a third-party resource or low contrast.
- Preview: `python3 build.py && python3 -m http.server -d dist 8000`.
- Deploys with GitHub Pages from `.github/workflows/pages.yml` on every push to `main`. Custom domain `ogcrafts.cloud` (the build writes `CNAME`).
