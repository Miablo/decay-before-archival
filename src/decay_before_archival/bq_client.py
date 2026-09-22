"""Shared BigQuery client setup for all analysis notebooks.

Usage, in any notebook:

    from bq_client import get_client
    client = get_client()
"""

import os

from dotenv import load_dotenv
from google.cloud import bigquery


def get_client():
    load_dotenv()  # loads GOOGLE_CLOUD_PROJECT from a local .env (see .env.example)

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise RuntimeError(
            "GOOGLE_CLOUD_PROJECT is not set. Copy .env.example to .env and fill in "
            "your own GCP project id (a free-tier project works fine)."
        )

    return bigquery.Client(project=project_id)
