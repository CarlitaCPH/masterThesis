import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams


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

# Set the font to Arial & 12 for plot
rcParams['font.family'] = 'Arial'
rcParams['font.size'] = 18

# Group the data by purchaser and calculate the average price per ton in EUR
average_price_by_buyer = data_subset_cleaned.groupby('purchaser_name')['price_per_ton_EUR'].mean()

# Group the data by purchaser and count the number of transactions for each buyer
transaction_count_by_buyer = data_subset_cleaned.groupby('purchaser_name').size()

# Sort the buyers by average price per ton
average_price_by_buyer_sorted = average_price_by_buyer.sort_values(ascending=False)

# Display the results
print("Average Price per Ton of BCR for Each Buyer (EUR/ton):")
print(average_price_by_buyer_sorted)

# Plot the average price per ton for each buyer
fig, ax = plt.subplots(figsize=(20, 8), dpi=300)
average_price_by_buyer_sorted.plot(kind='bar', color='skyblue')
plt.xlabel('Purchaser')
plt.ylabel('Average Price per Ton of BCR (EUR/ton)')
plt.title('Average Price per Ton of BCR by Buyer and Amount of Purchases')
plt.xticks(rotation=90, ha='right')
plt.grid(True)
plt.tight_layout()

# Rotate x-axis labels by 45 degrees
plt.xticks(rotation=45, ha='right', rotation_mode="anchor")

# Display grid and adjust layout
ax.grid(True)
plt.tight_layout()

# Annotate the bar plot with the number of transactions for each buyer
for i, purchaser in enumerate(average_price_by_buyer_sorted.index):
    # Place the annotation (transaction count) above each bar
    ax.text(i, average_price_by_buyer_sorted.iloc[i] + 2, 
            f'{transaction_count_by_buyer[purchaser]}', 
            ha='center', va='bottom', fontsize=16)

# Show the plot
path_name = 'Thesis files/python_folder/buyer_comparison'
plt.savefig(path_name, bbox_inches="tight")


# Analyze the distribution of prices by buyer
price_difference_by_buyer = data_subset_cleaned.groupby('purchaser_name')['price_per_ton_EUR'].std()

# Remove any remaining NaN values from the result, if only one transaction they will have NaN for standard deviation 
price_difference_by_buyer = price_difference_by_buyer.dropna()

# Display the price variability by buyer
print("\nPrice Variability (Standard Deviation) by Buyer:")
print(price_difference_by_buyer)

# You can also examine the price differences by looking for large standard deviations
high_variability_buyers = price_difference_by_buyer[price_difference_by_buyer > price_difference_by_buyer.quantile(0.75)]
print("\nBuyers with High Price Variability:")
print(high_variability_buyers)
