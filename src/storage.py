import sqlite3
from pathlib import Path

DB_PATH = Path("data/db/ecb.sqlite")

def get_connection():
    "GET A CONNECTION TO THE SQLITE DATABASE"
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_table(conn):
    "CREATE THE TABLE FOR ECB DATA"
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ecb_data (
            ref_area TEXT,
            time_period TEXT,
            obs_value REAL,
            PRIMARY KEY (ref_area, time_period)
        )
        """
    )
    conn.commit()


def upsert_data(conn, df):
    "UPSERT DATA INTO THE ECB DATA TABLE"
    rows = df[["REF_AREA","TIME_PERIOD", "OBS_VALUE"]].copy()
    rows["TIME_PERIOD"] = rows["TIME_PERIOD"].dt.strftime("%Y-%m-%d")

    conn.executemany(
        """
        INSERT INTO ecb_data (ref_area, time_period, obs_value)
        VALUES (?, ?, ?)
        ON CONFLICT(ref_area, time_period) DO UPDATE SET
            obs_value=excluded.obs_value
        """,
        rows.itertuples(index=False, name=None),
    )
    conn.commit()

if __name__ == "__main__":
    from ecb_client import fetch_series

    # Fetch data from ECB API
    df = fetch_series("MIR", "M.ES+U2+DE+FR+IT.B.A2A.A.R.A.2240.EUR.N", "2003-01")

    # Store data in SQLite database
    conn = get_connection()
    create_table(conn)
    upsert_data(conn, df)

    count = conn.execute("SELECT COUNT(*) FROM ecb_data").fetchone()[0]
    print(f"inserted - updated {count} rows in the database.")

    conn.close()