# Setup & Working Conventions

See [`README.md`](./README.md) for what this project is and how it's organized. This doc covers getting your environment running and how we work together day to day.

## Getting your own GCP project + project ID

Each teammate needs their own Google Cloud project on the BigQuery free tier (no shared account, no invite needed):

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and sign in with your **PSU or personal Google account**.
2. Create a new project: click the project dropdown at the top → **New Project** → give it any name → **Create**. (The free tier gives you 1 TB of BigQuery query processing per month with no credit card required to *query* public datasets.)
3. Find your **project ID** (not the project *name* — they can differ): either read it off the project dropdown/picker right after creating it, or go to **IAM & Admin → Settings**, where it's listed as "Project ID". It looks something like `my-project-123456`.
4. Keep that project ID handy — you'll use it below to set up your local `.env`.

## Running the notebooks locally

We run these notebooks locally with [`uv`](https://docs.astral.sh/uv/) + Jupyter — no shared GCP project needed. Jupyter itself is a project dependency (`uv sync` installs it for you); the one thing you need to install separately is the `gcloud` CLI.

1. **Install `uv`** if you don't have it:

   ```
   # macOS / Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   (or see the [uv install docs](https://docs.astral.sh/uv/getting-started/installation/) for other options, e.g. `brew install uv` / `pipx install uv`.)

2. **Install the `gcloud` CLI** (needed to authenticate to your GCP project):

   ```
   # macOS (Homebrew)
   brew install --cask google-cloud-sdk

   # Linux
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL   # restart your shell so `gcloud` is on PATH

   # Windows
   # download and run the installer: https://cloud.google.com/sdk/docs/install
   ```

   Then verify it installed: `gcloud --version`.

3. **Clone this repo** and `cd` into it.
4. **Set up your `.env`** with your own project ID from above:

   ```
   cp .env.example .env
   ```

   Then open `.env` and set it:

   ```
   GOOGLE_CLOUD_PROJECT=my-project-123456
   ```

   `.env` is git-ignored — it's yours only, never commit it or push it anywhere. `.env.example` is the only one that belongs in the repo.
5. **Authenticate with GCP** once per machine:

   ```
   gcloud auth application-default login
   ```

   This opens a browser window — sign in with the same Google account that owns your GCP project.
6. **Install dependencies:**

   ```
   uv sync
   ```

7. **Enable notebook-aware git diffs/merges** (one-time, per machine — see [Merging](#merging-integrate_datasetsipynb) below for why):

   ```
   uv run nbdime config-git --enable
   ```

8. **Launch Jupyter:**

   ```
   uv run jupyter lab
   ```

9. Open whichever notebook you're working on (see the [Notebooks table](./README.md#notebooks) in the README) and run its setup cell. It loads `GOOGLE_CLOUD_PROJECT` from `.env` automatically via `python-dotenv`, and fails with a clear error if it's missing — no code changes needed per person.

## Querying the public datasets

These datasets are public — you don't need to copy any data, just query them directly and BigQuery bills/quotas against your own project:

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

BigQuery's free tier gives **1 TB of query processing per month, per project** — since everyone now has their own project, this is no longer a shared pool, but it's still worth being careful (and it's a good habit before we run anything at scale later):

- **Always add a `LIMIT`** while exploring/testing a query.
- Prefer querying partitioned/date-scoped tables (e.g. a single `githubarchive.day` table) instead of scanning full history.
- Use **"Estimate"**/dry-run before running a big query — you can check bytes processed before executing:

  ```python
  job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
  client.query(query, job_config=job_config)
  ```

## Working on the notebooks together

- **Stick to your notebook.** Splitting by data source means conflicts should be rare, but two people editing `notebooks/pypi.ipynb` at the same time will still conflict with each other.
- **Clear all cell outputs before committing** (`Kernel → Restart Kernel and Clear All Outputs` in Jupyter, or the "clear outputs" toolbar button) so diffs stay clean and don't balloon with query result dumps or plot images.
- Never hardcode secrets, API keys, or service-account JSON in any notebook.
- Shared setup logic (GCP auth, `.env` loading) belongs in `src/decay_before_archival/bq_client.py`, not copy-pasted into a notebook — if you need to change how auth works, change it there so every notebook picks it up.

## Getting work back into GitHub

Standard git workflow:

1. `git pull` before you start working, so you're not stacking changes on a stale copy.
2. Make your changes, clear notebook outputs, then `git add` / `git commit` / `git push` (to a branch + PR if we're using those, or `main` if not).
3. If you and someone else need to touch the same notebook (or `bq_client.py`) at the same time, coordinate in the group chat first — notebook merge conflicts are painful to resolve by hand.

## Merging: `integrate_datasets.ipynb`

The per-source notebooks stay one-owner-at-a-time by design, but `notebooks/integrate_datasets.ipynb` is where everyone's work comes together — so it's the one file more than one of us is likely to touch. Two things make that manageable:

- **We use `nbdime` for notebook diffs/merges instead of raw git.** `uv sync` installs it and `uv run nbdime config-git --enable` (step 7 above) wires it into git for this repo, so `git diff` on any `.ipynb` shows a readable per-cell diff instead of a JSON blob, and a real conflict in `integrate_datasets.ipynb` becomes something `git mergetool` can actually resolve cell-by-cell (via `nbdime mergetool`) instead of an unreadable mess. Everyone needs to run the `config-git --enable` step once, since it writes to your local git config and isn't something cloning the repo picks up automatically.
- **Still prefer a single owner per merge session.** `integrate_datasets.ipynb` is currently a placeholder (join-key table + TODO cells) until each source notebook has settled on what it exports. Once we're actually merging, whoever's driving that session should say so in the group chat, push when done, and `git pull` before the next person picks it up — `nbdime` makes conflicts survivable, not free.
