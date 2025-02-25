import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams


# Set the font to Arial & 18 for plot
rcParams['font.family'] = 'Arial'
rcParams['font.size'] = 18

# Define the filename
filename = 'Thesis files/CDR_data_Oct_17_2024.csv'

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

# Identify the three most common marketplaces
top_marketplaces = data_subset_cleaned['marketplace_name'].value_counts().nlargest(5).index

# Filter the data to only include rows with the top three marketplaces
data_top_marketplaces = data_subset_cleaned[data_subset_cleaned['marketplace_name'].isin(top_marketplaces)]

# Create the scatter plot for the top three marketplaces
plt.figure(figsize=(12, 8), dpi=300)

# Plot 1: overview most common marketplaces with price
# Use groupby to separate the data by marketplace, then plot each group
for marketplace, group in data_top_marketplaces.groupby('marketplace_name'):
    plt.scatter(group['announcement_date'], group['price_per_ton_EUR'], label=marketplace, s=50)

# Customize the plot
plt.xlabel('Announcement Date')
plt.ylabel('Price per Ton (EUR/ton CDR)')
plt.title('Transactions Over Time by Marketplace (Top 5)')
plt.legend(title='Marketplace')
plt.xticks(rotation=45)
plt.grid(True)

# Add the note to the plot
plt.figtext(0.5, -0.1, "Top 5 by amount of transactions that published a price", 
            ha="center", fontsize=10, style="italic")

# Save the plot
path_name = 'Thesis files/python_folder/marketplace_comparison'
plt.savefig(path_name, bbox_inches="tight")
print("Plot saved successfully as marketplace_comparison.png.")
plt.close()  # Close the figure to prevent it from displaying in interactive environments

# Stats: Puro
""" 
# Filter the transactions where the price per ton is over 200€ by puro.earth
transactions_over_200_puro = data_subset_cleaned[(data_subset_cleaned['price_per_ton_EUR'] > 200) & (data_subset_cleaned['marketplace_name'] == 'Puro')]
count_over_200 = len(transactions_over_200_puro)
transaction_puro = len(data_subset_cleaned['marketplace_name'] == 'Puro')
"""
# Group by marketplace and count the total number of transactions for each marketplace
total_transactions_by_marketplace = data_subset_cleaned.groupby('marketplace_name').size()

# Filter the data for transactions with price > 200€/ton
transactions_over_200_by_marketplace = data_subset_cleaned[data_subset_cleaned['price_per_ton_EUR'] > 200]

# Group by marketplace and count the transactions with price > 200€/ton for each marketplace
transactions_over_200_by_marketplace_count = transactions_over_200_by_marketplace.groupby('marketplace_name').size()

# Combine the results into a single DataFrame for easy comparison
result_stats = pd.DataFrame({
    'Total Transactions': total_transactions_by_marketplace,
    'Transactions > 200€/ton': transactions_over_200_by_marketplace_count
}).fillna(0)  # Fill NaN with 0 for marketplaces with no transactions > 200€/ton

# Calculate the share (percentage) of transactions over 200€/ton for each marketplace
result_stats['Share of Transactions > 200€/ton'] = result_stats['Transactions > 200€/ton'] / result_stats['Total Transactions']
print(result_stats)
# Export the data_subset to an Excel file
output_filename = 'marketplace_comparison_stats.xlsx'

# Export the data_subset and stats to separate sheets in the same Excel file

with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
    result_stats.to_excel(writer, sheet_name='Stats', index=False)

print(f"Data subset and statistics have been successfully exported to '{output_filename}'.")


# Plot 2: 
# Outliers and marketplaces
# Ensure 'marketplace_name' has no NaN values (fixes missing transactions)
data_subset_cleaned['marketplace_name'] = data_subset_cleaned['marketplace_name'].fillna('No Marketplace')
# Define outliers
# Calculate Q1 (25th percentile) and Q3 (75th percentile)
# Ensure the column is numeric (in case of incorrect format)

Q1 = np.percentile(data_subset_cleaned['price_per_ton_EUR'], 25)
Q3 = np.percentile(data_subset_cleaned['price_per_ton_EUR'], 75)

# Calculate IQR
IQR = Q3 - Q1

# Define outlier bounds
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Identify all outliers (both lower and upper)
outliers = data_subset_cleaned[(data_subset_cleaned['price_per_ton_EUR'] < lower_bound) | 
                               (data_subset_cleaned['price_per_ton_EUR'] > upper_bound)]

# Count total number of outliers
outlier_count = outliers.shape[0]

# Get transaction values of all outliers
outlier_values = outliers[['price_per_ton_EUR', 'marketplace_name']]  # Include marketplace_name for context

# Find the smallest outlier above the upper bound
outliers_upper = outliers[outliers['price_per_ton_EUR'] > upper_bound]
if not outliers_upper.empty:
    smallest_upper_outlier = outliers_upper['price_per_ton_EUR'].min()
else:
    smallest_upper_outlier = upper_bound  # Fallback if no upper outliers exist

# Filter dataset using the smallest upper outlier as the threshold
data_filtered = data_subset_cleaned[data_subset_cleaned['price_per_ton_EUR'] > smallest_upper_outlier]

# Print results
print(f"Total number of outliers in 'price_per_ton_EUR': {outlier_count}")
print("\nTransaction values of all outliers:")
print(outlier_values)



# Create the scatter plot for marketplaces with prices above the threshold
plt.figure(figsize=(12, 8), dpi=300)  # Larger figure

# Use groupby to separate the data by marketplace, then plot each group
for marketplace, group in data_filtered.groupby('marketplace_name'):
    plt.scatter(group['announcement_date'], group['price_per_ton_EUR'], label=marketplace, s=70)  # Smaller markers

# Customize the plot
plt.xlabel('Announcement Date', fontsize=20)
plt.ylabel('Price per Ton (€/ton CDR)', fontsize=20)
plt.title(f'Transactions Over 305 €/ton Over Time by Marketplace', fontsize=20)

# Adjust x-axis labels
plt.xticks(rotation=60, fontsize=20)  # Rotated for readability

# Adjust y-axis limits
plt.ylim(bottom=0, top=max(data_filtered['price_per_ton_EUR']) + 50)  # Adds some space at the top

# Move legend outside the plot for better readability
plt.legend(title=f'Above 305 €/ton BCR by Marketplace', fontsize=12, title_fontsize=13, loc='upper left', bbox_to_anchor=(1, 1))

# Add grid for readability
plt.grid(True, linestyle='--', alpha=0.6)

# Save the plot
plot_path = 'Thesis files/python_folder/above_threshold_marketplace_improved.png'
plt.savefig(plot_path, bbox_inches="tight")

# Print success message
print(f"Plot saved successfully as {plot_path}.")
