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
    exit()
except pd.errors.EmptyDataError:
    print("Error: The file is empty.")
    exit()
except pd.errors.ParserError:
    print("Error: There was an issue parsing the file.")
    exit()

# List of columns to include in the subset
columns_to_keep = [
    "purchaser_name", "supplier_name", "marketplace_name", "status", 
    "method", "tons_purchased", "price_usd", "announcement_date", "delivery_date", "tons_delivered"
]

# Filter for Biochar Carbon Removal (BCR)
data_subset = data[columns_to_keep].copy()[data['method'] == 'Biochar Carbon Removal (BCR)']

# Ensure 'announcement_date' is in datetime format
data_subset['announcement_date'] = pd.to_datetime(data_subset['announcement_date'], errors='coerce')

# Create a new column 'announcement_year'
data_subset['announcement_year'] = data_subset['announcement_date'].dt.year

# Drop rows where tons_purchased is missing
data_subset_cleaned = data_subset.dropna(subset=['tons_purchased'])

# Summarize the total BCR tons purchased per year
bcr_volume_stats = data_subset_cleaned.groupby('announcement_year').agg(
    TotalTonsPurchased=('tons_purchased', 'sum'),
    AverageTonsPurchased=('tons_purchased', 'mean'),
    MedianTonsPurchased=('tons_purchased', 'median'),
    MinTonsPurchased=('tons_purchased', 'min'),
    MaxTonsPurchased=('tons_purchased', 'max'),
    TransactionCount=('tons_purchased', 'count')
).reset_index()

# Compute the overall sum of tons purchased across all years
total_tons_purchased = data_subset_cleaned['tons_purchased'].sum()

overall_summary = pd.DataFrame({
    "Year": ["Overall"],
    "TotalTonsPurchased": [total_tons_purchased],
    "AverageTonsPurchased": [None],
    "MedianTonsPurchased": [None],
    "MinTonsPurchased": [None],
    "MaxTonsPurchased": [None],
    "TransactionCount": [None]
})

# Append the overall summary to the statistics dataframe
bcr_volume_stats = pd.concat([bcr_volume_stats, overall_summary], ignore_index=True)

# Round the statistics to two decimal places
bcr_volume_stats = bcr_volume_stats.round(2)

# Rename columns before exporting
bcr_volume_stats.rename(columns={
    'TotalTonsPurchased': 'Total Tons Purchased',
    'AverageTonsPurchased': 'Average Tons Purchased',
    'MedianTonsPurchased': 'Median Tons Purchased',
    'MinTonsPurchased': 'Min Tons Purchased',
    'MaxTonsPurchased': 'Max Tons Purchased',
    'TransactionCount': 'Transaction Count'
}, inplace=True)

# Print the summarized statistics
print(bcr_volume_stats)

# Export the statistics to an Excel file
output_filename = 'bcr_volume_analysis.xlsx'
with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
    bcr_volume_stats.to_excel(writer, sheet_name='BCR Volume Stats', index=False)

print(f"BCR volume statistics have been successfully exported to '{output_filename}'.")

