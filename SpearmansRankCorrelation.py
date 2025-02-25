import pandas as pd
import numpy as np
import os
import scipy.stats as stats
import matplotlib.pyplot as plt

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

# Create the subset with the specified columns and filter for Biochar Carbon Removal (BCR)
data_subset = data[columns_to_keep].copy()[data['method'] == 'Biochar Carbon Removal (BCR)']

# Calculate price per ton
data_subset['price_per_ton_USD'] = data_subset['price_usd'] / data_subset['tons_purchased']
data_subset['price_per_ton_USD'] = data_subset['price_per_ton_USD'].round(2)

# Convert `announcement_date` to datetime and calculate days since first date
data_subset['announcement_date'] = pd.to_datetime(data_subset['announcement_date'])
data_subset['days_since_start'] = (data_subset['announcement_date'] - data_subset['announcement_date'].min()).dt.days

# Drop NaN and infinite values
data_subset_cleaned = data_subset.dropna(subset=['price_per_ton_USD'])
data_subset_cleaned = data_subset_cleaned[~np.isinf(data_subset_cleaned['price_per_ton_USD'])]

# Define variables for correlation analysis
X = data_subset_cleaned['days_since_start']  # Time as independent variable
y = data_subset_cleaned['price_per_ton_USD']  # Price per ton as dependent variable

# Perform Spearman's Rank Correlation
spearman_corr, spearman_p_value = stats.spearmanr(X, y)

# Print results
print(f"Spearman's Rank Correlation Coefficient: {spearman_corr:.3f}")
print(f"P-value: {spearman_p_value:.5f}")

# Interpretation
if spearman_p_value < 0.05:
    print("The correlation is statistically significant (p < 0.05).")
else:
    print("The correlation is not statistically significant (p >= 0.05).")

# Scatter plot with trendline
plt.scatter(X, y, alpha=0.6, label='Data Points')
plt.xlabel("Days Since Start")
plt.ylabel("Price per Ton (USD)")
plt.title("Spearman's Rank Correlation: Price vs Time")
plt.grid(True)

# Display plot
plt.legend()
plt.show()