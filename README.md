# Rehabus Lens & Link

An interactive GIS web application for Rehabus mobility analysis, combining multi-source spatial data, POIs, road-network information, demand patterns and infrastructure planning into an online interface.

## Live Demo

After enabling GitHub Pages for this repository, the site can be opened directly at:

`https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/`

## Key Features

- Interactive Mapbox-based GIS visualization
- Rehabus mobility and trajectory analysis
- POI and elderly-service spatial analysis
- Road-network and accessibility visualization
- Demand hotspot and operational analysis
- Depot / EV infrastructure candidate-site evaluation
- Multi-source spatial data integration
- Module A / B / C interactive workflows

## Deploy to GitHub Pages

1. Create a new **public** GitHub repository, for example `Rehabus-Lens-Link`.
2. Upload **all files in this folder** to the repository root.
3. Open **Settings → Pages**.
4. Under **Build and deployment**, choose **Deploy from a branch**.
5. Select the `main` branch and `/ (root)` folder, then click **Save**.
6. Wait for GitHub Pages to finish deploying.
7. Open the generated Pages URL.

The project has been prepared with relative asset/data paths so it works under a GitHub Pages project URL such as `/Rehabus-Lens-Link/`.

## Important: Mapbox

The frontend uses a client-side Mapbox public access token. Client-side Mapbox tokens are normally visible in browser code. For a public portfolio deployment, use a token restricted to your GitHub Pages domain and appropriate scopes/usage limits.

## Data Note

The repository contains a compacted version of the POI dataset used by the web application. The original local-demo package contained a large unused POI v2 file that exceeded GitHub's 100 MB individual-file limit, so it is intentionally excluded from this GitHub Pages build.

## Local Preview

Because this is a static site, it can also be previewed with any static HTTP server. For example:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000/`.
