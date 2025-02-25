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

# Group the data by supplier and calculate the average price per ton in EUR
average_price_by_supplier = data_subset_cleaned.groupby('supplier_name')['price_per_ton_EUR'].mean()

# Group the data by supplier and count the number of transactions for each supplier
transaction_count_by_supplier = data_subset_cleaned.groupby('supplier_name').size()

# Sort the suppliers by average price per ton
average_price_by_supplier_sorted = average_price_by_supplier.sort_values(ascending=False)

# Display the results
print("Average Price per Ton for Each Supplier (EUR/ton):")
print(average_price_by_supplier_sorted)

# Plot the average price per ton for each supplier and get the axis object
fig, ax = plt.subplots(figsize=(20, 8), dpi=300)  # Increase the figure width for readability
average_price_by_supplier_sorted.plot(kind='bar', color='lightgreen', ax=ax)
ax.set_xlabel('Supplier')
ax.set_ylabel('Average Price per Ton BCR (EUR/ton)')
ax.set_title('Average Price per Ton of BCR by Supplier')

# Rotate x-axis labels by 45 degrees and adjust alignment to prevent overlap
plt.xticks(rotation=45, ha='right', rotation_mode="anchor")

# Display grid and adjust layout
ax.grid(True)
plt.tight_layout()

# Annotate the bar plot with the number of transactions for each supplier
for i, supplier in enumerate(average_price_by_supplier_sorted.index):
    # Place the annotation (transaction count) above each bar
    ax.text(i, average_price_by_supplier_sorted.iloc[i] + 2, 
            f'{transaction_count_by_supplier[supplier]}', 
            ha='center', va='bottom', fontsize=16)

# Show the plot
path_name = 'Thesis files/python_folder/supplier_comparison'
plt.savefig(path_name, bbox_inches="tight")
plt.show()

# Analyze the distribution of prices by supplier
price_difference_by_supplier = data_subset_cleaned.groupby('supplier_name')['price_per_ton_EUR'].std()

# Display the price variability by supplier
print("\nPrice Variability (Standard Deviation) by Supplier:")
print(price_difference_by_supplier)

# Examine the price differences by looking for large standard deviations
high_variability_suppliers = price_difference_by_supplier[price_difference_by_supplier > price_difference_by_supplier.quantile(0.75)]
print("\nSuppliers with High Price Variability:")
print(high_variability_suppliers)
