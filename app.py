import pandas as pd
from sodapy import Socrata

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 100)
pd.set_option("display.width", 1000)

APP_TOKEN = "DjO84VZPdzu9XsGU9WNTUb98F"
#Setting a longer timeout than the default makes the request more reliable
TIMEOUT_TIME = 120

client  = Socrata("data.cityofnewyork.us", APP_TOKEN, timeout=TIMEOUT_TIME)

DATASET_ID = "erm2-nwe9"
#The limit to the number of records I ask for
LIMIT = 10000 #1 million is a limit that seems to run reliably but is still a large number of records

#First I want to get data for a 4 year period. I wll do it in chunks of one year to avoid timeouts but this can still take a while.
#Be Patient!
#To control the number of records, I only want complaints to the NYPD in Manhattan.
all_results = []
for year in range(2020, 2021):
    start = f"{year}-01-01"
    end = f"{year}-12-31"
    print(f"Fetching data from {DATASET_ID} with limit {LIMIT} for {year}...")
    results = client.get(DATASET_ID, 
                         limit=LIMIT,
                         where=f"agency = 'NYPD' AND borough = 'MANHATTAN' AND created_date BETWEEN '{start}' AND '{end}'"
                         )
    all_results.extend(results)
    print(f"Found {len(results)} records for {year}")

#Now I convert the results to a dataframe
results_df = pd.DataFrame.from_records(all_results)

#I next want to check column names and data types
print(results_df.dtypes)

#Next I want to convert the date columns to datetimes for use in plots and later analysis
results_df["created_date"] = pd.to_datetime(results_df["created_date"])
results_df["closed_date"] = pd.to_datetime(results_df["closed_date"])

#Though it seems unlikely that I will use these, lets convert the numeric columns to numbers
results_df['latitude'] = pd.to_numeric(results_df['latitude'], errors='coerce')
results_df['longitude'] = pd.to_numeric(results_df['longitude'], errors='coerce')
results_df['x_coordinate_state_plane'] = pd.to_numeric(results_df['x_coordinate_state_plane'], errors='coerce')
results_df['y_coordinate_state_plane'] = pd.to_numeric(results_df['y_coordinate_state_plane'], errors='coerce')

#Check the data types again
print("Data types after conversion:")
print(results_df.dtypes)

#Okay new lets clean up some more. Check for Nan values in each column.
print("Nan values in each column:")
print(results_df.isna().sum())

#I am most interested in the NYPD complaints and in what borough they occured.
columns = ["created_date", "complaint_type", "descriptor", "borough", "agency", "location_type"]

#It looks like the location_type column has a lot of Nan values but not so many that I will drop it. 
#I will keep it for now and replace the Nan values with "Unknown" for visualization purposes later.
results_df["location_type"] = results_df["location_type"].fillna("Unknown")

#Now I want to drop rows with missing critical information. It may not make a big difference but it seems like a good idea to do.
rows_before = len(results_df)
print(f"Rows before dropping: {rows_before}")

#Drop rows missing critical information
results_df.dropna(subset=['created_date', 'borough', 'complaint_type'], inplace=True)

# Number of rows after dropping
rows_after = len(results_df)
print(f"Rows after dropping: {rows_after}")

# Number of rows dropped
print(f"Rows dropped: {rows_before - rows_after}")

#Take a look at the first few rows of the dataframe
print("First few rows of the dataframe:")
head_size = 50
print(results_df[columns].head(head_size))