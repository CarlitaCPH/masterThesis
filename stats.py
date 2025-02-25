import pandas as pd
import numpy as np
import os

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



# Filter for Biochar Carbon Removal (BCR)
# Create the subset with the specified columns and filter for Biochar Carbon Removal (BCR)
data_subset = data[columns_to_keep].copy()[data['method'] == 'Biochar Carbon Removal (BCR)']

# Ensure 'announcement_date' is in datetime format
data_subset['announcement_date'] = pd.to_datetime(data_subset['announcement_date'], errors='coerce')

# Create a new column 'announcement_year' with the year extracted from 'announcement_date'
data_subset['announcement_year'] = data_subset['announcement_date'].dt.year

# Add a new column 'price_per_ton_USD'
data_subset['price_per_ton_USD'] = data_subset['price_usd'] / data_subset['tons_purchased']

#drop rows without price
data_subset_cleaned = data_subset.dropna(subset=['price_per_ton_USD'])

# change rows where 'price_per_ton_USD' is infinite
data_subset_cleaned = data_subset_cleaned[~np.isinf(data_subset_cleaned['price_per_ton_USD'])]

# Define the conversion rate from USD to EUR
conversion_rate = 1.0718

#convert to EUR
# Add a new column 'price_per_ton_EUR'
data_subset_cleaned['price_per_ton_EUR'] = data_subset_cleaned['price_per_ton_USD'] / conversion_rate

# Show the min, max, average, mode, and median prices for each year, including data points per year
# Group by 'announcement_year' and calculate the required statistics
stats = data_subset_cleaned.groupby('announcement_year').agg(
    min_price_EUR=('price_per_ton_EUR', 'min'),
    max_price_EUR=('price_per_ton_EUR', 'max'),
    avg_price_EUR=('price_per_ton_EUR', 'mean'),
    median_price_EUR=('price_per_ton_EUR', 'median'),  # Get median
    mode_price_EUR=('price_per_ton_EUR', lambda x: x.mode()[0] if not x.mode().empty else None),  # Get mode
    count=('price_per_ton_EUR', 'count'),  # Count of non-null price_usd entries
).reset_index()

# Compute total_entries from data_subset (before filtering out missing price values)
total_entries = data_subset.groupby('announcement_year').size().reset_index(name='total_entries')

# Merge the total_entries into stats
stats = stats.merge(total_entries, on='announcement_year', how='left')

# Round the statistics to one decimal place
stats[['min_price_EUR', 'max_price_EUR', 'avg_price_EUR', 'median_price_EUR', 'mode_price_EUR']] = \
    stats[['min_price_EUR', 'max_price_EUR', 'avg_price_EUR', 'median_price_EUR', 'mode_price_EUR']].round(1)

# Rename columns to the specified headers
stats.rename(columns={
    'announcement_year' : 'Year',
    'min_price_EUR': 'Min (€)/ton CDR',
    'max_price_EUR': 'Max (€)/ton CDR',
    'avg_price_EUR': 'Average (€)/ton CDR',
    'median_price_EUR': 'Median (€)/ton CDR',
    'mode_price_EUR': 'Mode (€)/ton CDR',
    'count': 'Transactions with price tag per year',
    'total_entries': 'Total transactions per year',
    'transaction_price_public': 'Share of public prices'
}, inplace=True)

print(stats)

#show the min, max, average, mode prices for total dataset (2021-2024)
stats_total = pd.DataFrame({
    'min_price_EUR': [data_subset_cleaned['price_per_ton_EUR'].min()],
    'max_price_EUR': [data_subset_cleaned['price_per_ton_EUR'].max()],
    'avg_price_EUR': [data_subset_cleaned['price_per_ton_EUR'].mean()],
    'median_price_EUR': [data_subset_cleaned['price_per_ton_EUR'].median()],
    'mode_price_EUR': [data_subset_cleaned['price_per_ton_EUR'].mode()[0] if not data_subset_cleaned['price_per_ton_EUR'].mode().empty else None],
    'count': [data_subset_cleaned['price_per_ton_EUR'].count()],  # Count of non-null entries
    'total_entries': [data_subset.shape[0]]  # Total number of entries in the dataset
})

# Round the statistics to one decimal place
stats_total[['min_price_EUR', 'max_price_EUR', 'avg_price_EUR', 'median_price_EUR', 'mode_price_EUR']] = stats_total[['min_price_EUR', 'max_price_EUR', 'avg_price_EUR', 'median_price_EUR', 'mode_price_EUR']].round(1)

# Rename columns to the specified headers
stats_total.rename(columns={
    'announcement_year' : 'Year',
    'min_price_EUR': 'Min (€)/ton CDR',
    'max_price_EUR': 'Max (€)/ton CDR',
    'avg_price_EUR': 'Average (€)/ton CDR',
    'median_price_EUR': 'Median (€)/ton CDR',
    'mode_price_EUR': 'Mode (€)/ton CDR',
    'count': 'Transactions with price tag per year',
    'total_entries': 'Total transactions per year',
    'transaction_price_public': 'Share of public prices'
}, inplace=True)


print(stats_total)

# Export the data_subset to an Excel file
output_filename = 'carla_cdr_data_.xlsx'

# Export the data_subset and stats to separate sheets in the same Excel file

with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
    data_subset_cleaned.to_excel(writer, sheet_name='Data Subset', index=False)
    stats.to_excel(writer, sheet_name='Statistics per year', index=False)
    stats_total.to_excel(writer, sheet_name='Stats total', index=False)

print(f"Data subset and statistics have been successfully exported to '{output_filename}'.")

# Print the current working directory
print("the file can be found here:", os.getcwd())


print(data_subset_cleaned[data_subset_cleaned['announcement_year'] == 2023]['price_per_ton_EUR'])


