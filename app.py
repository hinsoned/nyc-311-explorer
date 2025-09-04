import pandas as pd
from sodapy import Socrata

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 100)
pd.set_option("display.width", 1000)

APP_TOKEN = "DjO84VZPdzu9XsGU9WNTUb98F"

client  = Socrata("data.cityofnewyork.us", APP_TOKEN, timeout=120)

DATASET_ID = "erm2-nwe9"
LIMIT = 5000

print(f"Fetching data from {DATASET_ID} with limit {LIMIT}...")
results = client.get(DATASET_ID, 
                     limit=LIMIT,
                     where="agency = 'NYPD'"
                     )
print(f"Found {len(results)} records")

results_df = pd.DataFrame.from_records(results)

#Print the column names first to know what we are working with
print(results_df.columns)

columns = ["created_date", "complaint_type", "borough", "agency"]

head_size = 100

print(results_df[columns].head(head_size))