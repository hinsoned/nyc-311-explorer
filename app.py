import pandas as pd
from sodapy import Socrata
import matplotlib.pyplot as plt
import seaborn as sns
import platform
import subprocess
import os
from datetime import datetime

#NYC-311 data Project: Phase 2
#Author: Edward Hinson
#Description: This script is used to explore the NYC-311 data. It is used to get a sense of the data and to prepare it for analysis.

#function to prompt user
def prompt_user():
    print("Enter a borough, a start year, and an end year to get data for that borough between those years.")

    while True:
        start_year = int(input("Enter the start year (2015-2024): "))
        if start_year >= 2015 and start_year < 2025:
            break
        else:
            print("Invalid year. Please enter a year between 2015 and 2024.")

    while True:
        end_year = int(input("Enter the end year (2015-2024): "))
        if start_year > end_year:
            print("End year must be greater than or equal to start year.")
        elif end_year >= 2015 and end_year < 2025:
            break
        else:
            print("Invalid year. Please enter a year between 2015 and 2024.")

    while True:
        borough = input("Enter the borough (Bronx, Brooklyn, Manhattan, Queens, Staten Island): ")
        if borough.lower() in ["bronx", "brooklyn", "manhattan", "queens", "staten island"]:
            borough = borough.upper()
            break
        else:
            print("Invalid borough. Please enter a borough.")
    return borough, start_year, end_year

#function to get results from the API
def get_results(client, DATASET_ID, LIMIT, borough, start_year, end_year):
    all_results = []
    #Adding 1 to the end year to include the year in the range
    for year in range(start_year, end_year + 1):
        start = f"{year}-01-01"
        end = f"{year}-12-31"
        print(f"Fetching data from {DATASET_ID} with limit {LIMIT} for {borough} in {year}...")
        results = client.get(DATASET_ID, 
                            limit=LIMIT,
                            where=f"agency = 'NYPD' AND borough = '{borough}' AND created_date BETWEEN '{start}' AND '{end}'"
                            )
        all_results.extend(results)
        print(f"Found {len(results)} records for {year}")

    #total number of records
    total_records = len(all_results)
    print(f"Total number of records: {total_records}")

    return all_results, total_records

def open_image(path):
    system = platform.system()#This gets the operating system
    if system == "Darwin":  # macOS
        subprocess.call(["open", path])#This opens the image on macOS
    elif system == "Windows":
        os.startfile(path)#This opens the image on Windows
    else:  # Linux
        subprocess.call(["xdg-open", path])#This opens the image on Linux

#Line for monthly complaint totals
def plot_monthly_complaints(results_df, borough, start_year, end_year, export_folder):
    monthly_counts = results_df.groupby(["year", "month"]).size()
    monthly_counts.plot(kind="line", marker="o", figsize=(12,6))
    plt.title(f"{borough} NYPD 311 Complaints per Month ({start_year}-{end_year})")
    plt.xlabel("Year, Month")
    plt.ylabel("Number of Complaints")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{export_folder}/{borough}_monthly_complaints.png")
    open_image(f"{export_folder}/{borough}_monthly_complaints.png")
    plt.close()

def plot_top_complaint_types(results_df, borough, start_year, end_year, total_records, export_folder):
    top_complaints = results_df["complaint_type"].value_counts().head(10)
    plt.figure(figsize=(10,6))
    sns.barplot(x=top_complaints.index, y=top_complaints.values, palette="pastel", hue=top_complaints.index)
    plt.title(f"Top 10 Complaint Types in {borough} ({start_year}-{end_year}) with {total_records} total complaints")
    plt.xlabel("Complaint Type")
    plt.ylabel("Number of Complaints")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(f"{export_folder}/{borough}_top_complaint_types.png")
    open_image(f"{export_folder}/{borough}_top_complaint_types.png")
    plt.close()

#Heatmap for seasonality of complaints
def plot_seasonality_heatmap(results_df, borough, start_year, end_year, export_folder):
    pivot = results_df.pivot_table(index="year", columns="month", values="unique_key", aggfunc="count")
    plt.figure(figsize=(12,6))
    sns.heatmap(pivot, cmap="YlOrRd", annot=True, fmt="d")
    plt.title(f"Complaint Seasonality Heatmap in {borough} ({start_year}-{end_year})")
    plt.xlabel("Month")
    plt.ylabel("Year")
    plt.tight_layout()
    plt.savefig(f"{export_folder}/{borough}_seasonality_heatmap.png")
    open_image(f"{export_folder}/{borough}_seasonality_heatmap.png")
    plt.close()

#function to remove unnecessary columns
def remove_unnecessary_columns(results_df):
    #I do not need all of these columns. I know the agency is the NYPD and the borough is Manhattan. I also do not need the bbl and the agency_name column
    #has bad information according to the documentation. Exact location is not needed for my analysis.
    #Columns to keep:
    keep_columns = [
        "unique_key", 
        "created_date", 
        "closed_date", 
        "complaint_type", 
        "descriptor", 
        "incident_zip", 
        "status", 
        "resolution_description", 
        "community_board", 
        "open_data_channel_type", 
        "park_facility_name", 
        "park_borough", 
        "location", 
        "location_type"]

    drop_columns = []
    for col in results_df.columns:
        if col not in keep_columns:
            drop_columns.append(col)
    results_df.drop(columns=drop_columns, inplace=True)

    print("Dropped columns:")
    for col in drop_columns:
        print(f"- {col}")

    return results_df

#function to drop bad rows
def drop_bad_rows(results_df):
    #Now I want to drop rows with missing critical information. It may not make a big difference but it seems like a good idea to do.
    print("Dropping rows with missing critical information...")
    rows_before = len(results_df)
    print(f"Rows before dropping: {rows_before}")

    #Drop rows missing critical information
    results_df.dropna(subset=['created_date', 'complaint_type'], inplace=True)

    # Number of rows after dropping
    rows_after = len(results_df)
    print(f"Rows after dropping: {rows_after}")

    # Number of rows dropped
    print(f"Rows dropped: {rows_before - rows_after}")

    return results_df

def main():
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", 100)
    pd.set_option("display.width", 1000)

    APP_TOKEN = "DjO84VZPdzu9XsGU9WNTUb98F"
    #Setting a longer timeout than the default makes the request more reliable
    TIMEOUT_TIME = 120

    client  = Socrata("data.cityofnewyork.us", APP_TOKEN, timeout=TIMEOUT_TIME)

    DATASET_ID = "erm2-nwe9"
    #The limit to the number of records I ask for
    LIMIT = 1000000 #1 million is a limit that seems to run reliably but is still a large number of records

    #Prompt user for borough, start year, and end year
    borough, start_year, end_year = prompt_user()

    #First I want to get data for a 4 year period. I wll do it in chunks of one year to avoid timeouts but this can still take a while.
    #Be Patient!
    #To control the number of records, I only want complaints to the NYPD in Manhattan.
    print("Be Patient! This may take a while...")
    print(f"Fetching data from {DATASET_ID} for {borough} between {start_year} and {end_year}...")

    all_results, total_records = get_results(client, DATASET_ID, LIMIT, borough, start_year, end_year)

    #Now I convert the results to a dataframe
    results_df = pd.DataFrame.from_records(all_results)

    #I next want to check column names and data types
    print(results_df.dtypes)

    #remove unnecessary columns
    results_df = remove_unnecessary_columns(results_df)

    #Print to see the data types again
    print(results_df.dtypes)

    #Next I want to convert the date columns to datetimes for use in plots and later analysis
    results_df["created_date"] = pd.to_datetime(results_df["created_date"])
    results_df["closed_date"] = pd.to_datetime(results_df["closed_date"])

    #Check the data types again
    print("Data types after conversion:")
    print(results_df.dtypes)

    #Okay now lets clean up some more. Check for Nan values in each column.
    print("Nan values in each column:")
    print(results_df.isna().sum())

    #It looks like the location_type column has a lot of Nan values but not so many that I will drop it. 
    #I will keep it for now and replace the Nan values with "Unknown" for visualization purposes later.
    results_df["location_type"] = results_df["location_type"].fillna("Unknown")

    #drop bad rows
    results_df = drop_bad_rows(results_df)

    #I am most interested in the NYPD complaints and in what borough they occured.
    columns = ["created_date", "complaint_type", "descriptor", "status", "location_type", "open_data_channel_type"]

    #Take a look at the first few rows of the dataframe
    print("First few rows of the dataframe:")
    head_size = 25
    print(results_df[columns].head(head_size))

    #I want to add some additional columns to the dataframe for analysis. I want to know the year, month, and day of the week of the complaint.
    results_df["year"] = results_df["created_date"].dt.year
    results_df["month"] = results_df["created_date"].dt.month
    results_df["day_of_week"] = results_df["created_date"].dt.day_name()

    #print("--Value counts for key columns--")
    #print(results_df['complaint_type'].value_counts().head(10))
    #print(results_df['descriptor'].value_counts().head(10))
    #print(results_df['status'].value_counts().head(10))
    #print(results_df['location_type'].value_counts().head(10))
    #print(results_df['open_data_channel_type'].value_counts())
    #print(results_df['month'].value_counts())
    #print(results_df['day_of_week'].value_counts())

    print("Data types after adding new columns:")
    print(results_df.dtypes)

    #Timestamp to differentiate between export folders
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    #Create an export folder for the plots
    export_folder = f"{borough}_{start_year}_{end_year}_{timestamp}"
    os.makedirs(export_folder, exist_ok=True)

    #A CSV file for the dataframe
    results_df.to_csv(f"{export_folder}/nyc_311_data_{timestamp}.csv", index=False)

    #Plots
    plot_monthly_complaints(results_df, borough, start_year, end_year, export_folder)
    plot_top_complaint_types(results_df, borough, start_year, end_year, total_records, export_folder)
    plot_seasonality_heatmap(results_df, borough, start_year, end_year, export_folder)

    #Print some summary statistics
    print(f"""Between {start_year} and {end_year} there were {len(results_df)} complaints. 
    The day of the week with the most complaints was {results_df['day_of_week'].value_counts().idxmax()} 
    while the month with the most complaints was {results_df['month'].value_counts().idxmax()}. 
    The three most common complaint types were {results_df['complaint_type'].value_counts().head(3).index.tolist()}.""")

if __name__ == "__main__":
    main()