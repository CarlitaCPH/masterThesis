import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from matplotlib import rcParams

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

# Add a new column 'price_per_ton_USD'
data_subset['price_per_ton_USD'] = data_subset['price_usd'] / data_subset['tons_purchased']

# Drop rows without price and remove infinite values
data_subset_cleaned = data_subset.dropna(subset=['price_per_ton_USD'])
data_subset_cleaned = data_subset_cleaned[~np.isinf(data_subset_cleaned['price_per_ton_USD'])]

# Define the conversion rate from USD to EUR
conversion_rate = 1.0718

# Convert price to EUR
data_subset_cleaned['price_per_ton_EUR'] = data_subset_cleaned['price_per_ton_USD'] / conversion_rate

# Set font for plot
rcParams['font.family'] = 'Arial'
rcParams['font.size'] = 20

# Group the data by purchaser and calculate the average price per ton in EUR
average_price_by_buyer = data_subset_cleaned.groupby('purchaser_name')['price_per_ton_EUR'].mean()

# Group the data by purchaser and count the number of transactions for each buyer
transaction_count_by_buyer = data_subset_cleaned.groupby('purchaser_name').size()

# Perform Spearman correlation test
correlation, p_value = stats.spearmanr(transaction_count_by_buyer, average_price_by_buyer)

# Display correlation results
print("Spearman Correlation Test Results:")
print(f"Spearman correlation coefficient: {correlation:.4f}")
print(f"P-value: {p_value:.4f}")
if p_value < 0.05:
    print("The correlation is statistically significant.")
else:
    print("The correlation is not statistically significant.")

# Sort the buyers by average price per ton
average_price_by_buyer_sorted = average_price_by_buyer.sort_values(ascending=False)

# Plot the average price per ton for each buyer
fig, ax = plt.subplots(figsize=(20, 8), dpi=300)
average_price_by_buyer_sorted.plot(kind='bar', color='skyblue')
plt.xlabel('Purchaser')
plt.ylabel('Average Price per Ton of BCR (EUR/ton)')
plt.title('Average Price per Ton of BCR by Buyer and Amount of Purchases')
plt.xticks(rotation=90, ha='right')
plt.grid(True)
plt.tight_layout()

# Annotate the bar plot with the number of transactions for each buyer
for i, purchaser in enumerate(average_price_by_buyer_sorted.index):
    ax.text(i, average_price_by_buyer_sorted.iloc[i] + 2, 
            f'{transaction_count_by_buyer[purchaser]}', 
            ha='center', va='bottom', fontsize=16)

# Show the plot
path_name = '/Users/carlasoleta/Library/CloudStorage/GoogleDrive-carla.soleta@gmail.com/My Drive/Thesis files/python_folder/buyer_comparison'
plt.savefig(path_name, bbox_inches="tight")
plt.show()
plt.close()

# Analyze the distribution of prices by buyer
price_difference_by_buyer = data_subset_cleaned.groupby('purchaser_name')['price_per_ton_EUR'].std()

# Remove NaN values (if only one transaction, standard deviation is NaN)
price_difference_by_buyer = price_difference_by_buyer.dropna()

# Display the price variability by buyer
print("\nPrice Variability (Standard Deviation) by Buyer:")
print(price_difference_by_buyer)

# Identify buyers with high price variability
high_variability_buyers = price_difference_by_buyer[price_difference_by_buyer > price_difference_by_buyer.quantile(0.75)]
print("\nBuyers with High Price Variability:")
print(high_variability_buyers)
