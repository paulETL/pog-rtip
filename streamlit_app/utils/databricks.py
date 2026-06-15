"""
utils/databricks.py
Databricks connection helpers — query runner + table-existence guard.
"""
from databricks import sql
import pandas as pd
import streamlit as st


def _connect():
    return sql.connect(
        server_hostname=st.secrets["DATABRICKS_HOST"],
        http_path=st.secrets["DATABRICKS_HTTP_PATH"],
        access_token=st.secrets["DATABRICKS_TOKEN"],
    )


# SHORT CACHE ONLY FOR STREAMING EFFECT
@st.cache_data(ttl=5)     # NOT 60
def run_query(query: str):

    conn = _connect()

    try:
        cursor = conn.cursor()

        cursor.execute(query)

        rows = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]

        df = pd.DataFrame(rows, columns=columns)

        cursor.close()

        return df

    finally:
        conn.close()

# ── Convenience table loaders ────────────────────────────────────────────────
GOLD   = "workspace.pog_rtip_bronze_pog_rtip_gold"
SILVER = "workspace.pog_rtip_bronze_pog_rtip_silver"


def gold(table: str, where: str = "", limit: int = 0) -> pd.DataFrame:
    q = f"SELECT * FROM {GOLD}.{table}"
    if where:
        q += f" WHERE {where}"
    if limit:
        q += f" LIMIT {limit}"
    return run_query(q)


def silver(table: str, where: str = "", limit: int = 0) -> pd.DataFrame:
    q = f"SELECT * FROM {SILVER}.{table}"
    if where:
        q += f" WHERE {where}"
    if limit:
        q += f" LIMIT {limit}"
    return run_query(q)
