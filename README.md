# Decay Before Archival

Team project studying open source project health signals (decay leading up to archival) using public BigQuery datasets: **deps.dev**, **OpenSSF Scorecard**, **GH Archive**, and **PyPI download stats**.

See [`SETUP.md`](./SETUP.md) for environment setup, working conventions, and how we merge datasets.

## How this project is organized

1. **Your own free-tier GCP project** — each teammate creates their own personal Google Cloud project and uses its free tier as their query target for every public BigQuery dataset we use (deps.dev, Scorecard, GH Archive, PyPI). Nobody shares billing or quota — you can only burn through your own.
2. **Jupyter, run locally** — our working environment for writing and running analysis code (exploring a data source, sketching a plot, testing a query), run via `uv` on your own machine. It connects to *your* GCP project to run BigQuery queries.
3. **One notebook per data source, not one shared notebook** — `.ipynb` files merge/diff badly, so instead of everyone editing the same file, each data source gets its own notebook (see below). Pick one to work in and you won't be stepping on anyone else's changes.
4. **This GitHub repo** — the checkpoint / source of truth for the project, so nothing lives only in one person's machine. It holds notebooks, extraction scripts, and this README.

## Notebooks

All notebooks live under `notebooks/`:

| Notebook | Data source |
|---|---|
| `notebooks/deps_dev.ipynb` | deps.dev |
| `notebooks/scorecard.ipynb` | OpenSSF Scorecard |
| `notebooks/gh_archive.ipynb` | GH Archive |
| `notebooks/pypi.ipynb` | PyPI download stats |
| `notebooks/other_sources.ipynb` | OSV.dev, GitHub REST/GraphQL API, npm downloads API, CHAOSS Metrics (all still TODO — pick one if you want to start on it) |
| `notebooks/integrate_datasets.ipynb` | Combines the per-source data into one dataset once each notebook has settled on a join key — currently a placeholder, see [Merging](./SETUP.md#merging-integrate_datasetsipynb) in `SETUP.md` |

All six import a shared helper (`from decay_before_archival import get_client; client = get_client()`) so the GCP auth/`.env` logic lives in one place instead of being copy-pasted into every notebook. That helper lives at `src/decay_before_archival/bq_client.py` and is installed as an editable local package by `uv sync`, so it's importable from any notebook regardless of where it sits in `notebooks/`.

If you pick a source out of `notebooks/other_sources.ipynb` to actually explore, **create your own notebook for it** (same pattern as the others, in `notebooks/`) instead of building it out inside `other_sources.ipynb` — that file is just a holding area for unclaimed sources.

We don't track "who worked on what" with a names cell in the notebooks — that goes stale. Use `git log --author` or `git blame` on a given notebook if you need to see who touched what.

Per-source exploration in these notebooks is just the first step — we'll eventually need to integrate/merge everything into one combined dataset. While exploring your source, it's worth noting what you could join it on back to the others (project name, repo owner/name, package name, etc.), so that step isn't a rewrite later.

## Project documents

- [Data Collection Plan](https://pennstateoffice365-my.sharepoint.com/:x:/r/personal/mvd5044_psu_edu/Documents/Data%20Mining%202026%20Group%207/Data%20Collection%20Plan%20Template.xlsx?d=w163654a2b80f44fdba1f7f15b5354a86&csf=1&web=1&e=upZSxO) — shared SharePoint spreadsheet defining each metric we're collecting, its stratification factors, operational definition, frequency/time frame, source & location, collection method, and who collects it, plus how the data will be used and displayed.

## Repo contents

```
decay-before-archival/
├── notebooks/                        # all analysis notebooks (see Notebooks above)
│   ├── deps_dev.ipynb
│   ├── scorecard.ipynb
│   ├── gh_archive.ipynb
│   ├── pypi.ipynb
│   ├── other_sources.ipynb
│   └── integrate_datasets.ipynb      # merge step (see SETUP.md)
├── src/decay_before_archival/        # shared code, installed as an editable local package
│   └── bq_client.py                  # GCP auth / BigQuery client setup
├── .env                              # your own project id (git-ignored, not committed)
├── .env.example                      # template for .env
├── .gitattributes                    # tells git to use nbdime for .ipynb diffs/merges
├── pyproject.toml / uv.lock          # dependencies, managed by uv
├── README.md                         # this file
└── SETUP.md                          # environment setup + working conventions
```

Anything under `src/decay_before_archival/` is meant to be shared code imported by notebooks, not exploration itself — if you're writing SQL and looking at a dataframe, that belongs in a notebook; if you're writing a reusable helper function, it belongs in `src/`.
