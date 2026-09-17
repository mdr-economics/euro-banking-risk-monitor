import io
import requests
import pandas as pd

BASE_URL = "https://data-api.ecb.europa.eu/service/data"

def fetch_series(dataflow, key, start_period):
    "DOWNLOAD A ECB SERIES FROM THE ECB API AND RETURN IT AS A PANDAS DATAFRAME"
    url = f"{BASE_URL}/{dataflow}/{key}"
    params = {"startPeriod": start_period, "format": "csvdata"}
   
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    df = pd.read_csv(io.StringIO(response.text))
    df = df[["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]].copy()
    df["TIME_PERIOD"] = pd.to_datetime(df["TIME_PERIOD"])
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"])
    df = df.sort_values(["REF_AREA", "TIME_PERIOD"]).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = fetch_series("MIR", "M.ES+U2+DE+FR+IT.B.A2A.A.R.A.2240.EUR.N", "2003-01")
    print(df.head())
    print(df.tail())
    print(df["REF_AREA"].value_counts())
    print(df.dtypes)
    print(df.shape)