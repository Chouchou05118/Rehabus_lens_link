# Deployment notes

## What was changed from the local demo

- Removed the bundled portable Node.js runtime and local Windows launcher/server files.
- Removed `poi_cleaned_v2.json` because it is not referenced by the built frontend and is larger than GitHub's 100 MB individual-file limit.
- Compacted the referenced `poi_cleaned_v1.json` to fields used by the built frontend: `id`, `name`, `category`, `subcategory`, `lng`, `lat`, `raw_name`, `raw_major`, `raw_minor`.
- Converted root-absolute `/assets/...` and `/data...` references to relative paths so the site works under a GitHub Pages project path.
- Added `.nojekyll` so GitHub Pages serves the static assets without Jekyll processing.
