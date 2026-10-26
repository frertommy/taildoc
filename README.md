# taildoc

docs.tail.trade: static single-page docs (Vercel project `taildoc`).

- Edit content in `index.html` only.
- Then run `python3 build_pages.py`: regenerates `pages/<section>.html` (one crawlable page per section, own title/description/canonical) and `sitemap.xml`.
- `vercel.json` rewrites `/<section>` to `pages/<section>.html`; add new section ids there too.
