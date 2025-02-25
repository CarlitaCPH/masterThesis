import pandas as pd

# Define the filename
filename = '/Users/carlasoleta/Library/CloudStorage/GoogleDrive-carla.soleta@gmail.com/My Drive/Thesis files/CDR_data_Oct_17_2024.csv'

# Read the CSV file into a pandas DataFrame
try:
    data = pd.read_csv(filename)
    print("Data loaded successfully!")
except FileNotFoundError:
    print(f"Error: The file '{filename}' was not found.")
except pd.errors.EmptyDataError:
    print("Error: The file is empty.")
except pd.errors.ParserError:
    print("Error: There was an issue parsing the file.")

# List of columns to include in the subset
columns_to_keep = [
    "purchaser_name", "supplier_name", "marketplace_name", "status", 
    "method", "tons_purchased", "price_usd", "announcement_date", "delivery_date", "tons_delivered"
]

# Create the subset with the specified columns
data_subset = data[columns_to_keep].copy()

# Add a new column 'price_per_ton_USD'
data_subset['price_per_ton_USD'] = data_subset['price_usd'] / data_subset['tons_purchased']
#round to two decimals
data_subset['price_per_ton_USD'] = data_subset['price_per_ton_USD'].round(2)

data_subset_cleaned = data_subset.dropna(subset=['price_per_ton_USD'])
# print cleaned data set
print("Cleaned data subset:")
print(data_subset_cleaned)

# Check if 'announcement_date' is already in datetime format
if pd.api.types.is_datetime64_any_dtype(data_subset_cleaned['announcement_date']):
    print("The 'announcement_date' column is already in datetime format.")
else:
    print("The 'announcement_date' column is NOT in datetime format. Converting it to datetime.")
    data_subset_cleaned['announcement_date'] = pd.to_datetime(data_subset_cleaned['announcement_date'])

# Identify duplicate timestamps in 'announcement_date'
duplicate_timestamps = data_subset_cleaned[data_subset_cleaned.duplicated('announcement_date', keep=False)]

# Display transactions with duplicate timestamps
print("Transactions with duplicate announcement dates:")
print(duplicate_timestamps) #302 rows are shown