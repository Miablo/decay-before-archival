# Decay Before Archival

Team project studying open source project health signals (decay leading up to archival) using public BigQuery datasets: **deps.dev**, **OpenSSF Scorecard**, **GH Archive**, and **PyPI download stats**.

## How this project is organized

1. **Shared GCP project** — one Google Cloud project all 4 teammates have access to. This is the query target for every public BigQuery dataset we use (deps.dev, Scorecard, GH Archive, PyPI). It also lets us watch our shared free-tier query quota as a group so no one accidentally burns through it.
2. **Google Colab** — our working environment for writing and running analysis code together (live co-editing, exploring a data source, sketching a plot, testing a query). Colab connects directly to the shared GCP project to run BigQuery queries.
3. **This GitHub repo** — the checkpoint / source of truth for the project, so nothing lives only in one person's Google Drive. It holds notebooks, extraction scripts, and this README.

## Getting access

- The GCP project will be created and shared by one team member (account owner). Once you're invited, accept the invite using your **PSU or personal Google account** (whichever address you gave the owner).
- You'll need the **GCP project ID** to connect from Colab — ask the project owner if you don't have it yet, and note it below once assigned:

  ```
  GCP_PROJECT_ID = "<fill-in-project-id>"
  ```

## Opening the notebook in Colab

1. Open [`OS_Project_Health_Signals.ipynb`](./OS_Project_Health_Signals.ipynb) in this repo and click the **"Open in Colab"** badge at the top of the notebook (or go directly to [Colab](https://colab.research.google.com/github/Miablo/decay-before-archival/blob/main/OS_Project_Health_Signals.ipynb)).
2. Make sure you're signed into the Google account that has access to the shared GCP project.
3. Run the auth cell — the first time you run a BigQuery cell in a fresh Colab session, it will prompt you to log in and authorize access:

   ```python
   from google.colab import auth
   auth.authenticate_user()

   from google.cloud import bigquery
   client = bigquery.Client(project="<GCP_PROJECT_ID>")
   ```

4. Replace `"<GCP_PROJECT_ID>"` with the real project ID (see above). Do **not** commit the real project ID with billing/service-account keys attached — the project ID string itself is fine to share, just never commit credentials or key files.

### Querying the public datasets

These datasets are public — you don't need to copy any data, just query them directly and BigQuery bills/quotas against our shared project:

| Data source | Example public dataset path |
|---|---|
| deps.dev | `bigquery-public-data.deps_dev_v1` |
| OpenSSF Scorecard | `openssf.scorecardcron.scorecard-v2` (via [Scorecard's BigQuery docs](https://github.com/ossf/scorecard#public-data)) |
| GH Archive | `githubarchive.day` / `githubarchive.month` / `githubarchive.year` |
| PyPI download stats | `bigquery-public-data.pypi.file_downloads` |

Example query pattern:

```python
query = """
SELECT *
FROM `bigquery-public-data.pypi.file_downloads`
LIMIT 10
"""
client.query(query).to_dataframe()
```

## Quota etiquette

BigQuery's free tier gives **1 TB of query processing per month, per billing account** — shared across all 4 of us on this project.

- **Always add a `LIMIT`** while exploring/testing a query.
- Prefer querying partitioned/date-scoped tables (e.g. a single `githubarchive.day` table) instead of scanning full history.
- Use **"Estimate"**/dry-run before running a big query — in Colab you can check bytes processed before executing:

  ```python
  job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
  client.query(query, job_config=job_config)
  ```

- If you're about to run something that scans more than a few GB, post in the group chat first.

## Working in Colab together

- Live co-edit during team sessions is fine — Colab supports multiple simultaneous editors, like a Google Doc.
- **Clear all cell outputs before saving/committing to GitHub** (`Edit → Clear all outputs` in Colab) so notebook diffs stay clean and don't balloon with query result dumps or plot images.
- Never hardcode secrets, API keys, or service-account JSON in the notebook.

## Getting work back into GitHub

1. When your working session is done, in Colab go to **File → Save a copy in GitHub**.
2. Choose this repo (`decay-before-archival`) and the `main` branch (or open a PR branch if we adopt one later).
3. **One person owns the push at the end of each session** — coordinate in the group chat so we don't end up with duplicate/conflicting commits from multiple people saving at once.

## Project documents

- [Data Collection Plan](https://pennstateoffice365-my.sharepoint.com/:x:/r/personal/mvd5044_psu_edu/Documents/Data%20Mining%202026%20Group%207/Data%20Collection%20Plan%20Template.xlsx?d=w163654a2b80f44fdba1f7f15b5354a86&csf=1&web=1&e=upZSxO) — shared SharePoint spreadsheet defining each metric we're collecting, its stratification factors, operational definition, frequency/time frame, source & location, collection method, and who collects it, plus how the data will be used and displayed.

## Repo contents

- `OS_Project_Health_Signals.ipynb` — main analysis notebook (Colab-linked).
- `readme.md` — this file.
