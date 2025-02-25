import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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
data_subset = data[columns_to_keep].copy()[data['method'] == 'Biochar Carbon Removal (BCR)']

# Ensure 'announcement_date' is in datetime format
data_subset['announcement_date'] = pd.to_datetime(data_subset['announcement_date'], errors='coerce')

# Add a new column 'price_per_ton_USD'
data_subset['price_per_ton_USD'] = data_subset['price_usd'] / data_subset['tons_purchased']

# Drop rows without price
data_subset_cleaned = data_subset.dropna(subset=['price_per_ton_USD'])

# Remove rows where 'price_per_ton_USD' is infinite
data_subset_cleaned = data_subset_cleaned[~np.isinf(data_subset_cleaned['price_per_ton_USD'])]

# Define the conversion rate from USD to EUR
conversion_rate = 1.0718

# Convert 'price_per_ton_USD' to EUR and add a new column 'price_per_ton_EUR'
data_subset_cleaned['price_per_ton_EUR'] = data_subset_cleaned['price_per_ton_USD'] / conversion_rate


# Basic Statistical Analysis with two decimal places
summary = data_subset_cleaned['price_per_ton_EUR'].describe().round(2)
print("Statistical Summary of 'price_per_ton_EUR':")
print(data_subset_cleaned['price_per_ton_EUR'].describe().round(2))

# Calculate the mode (there may be multiple modes)
mode_value = data_subset_cleaned['price_per_ton_EUR'].mode().round(2)

# Convert mode to a single value if there's only one, otherwise keep all
mode_str = ', '.join(map(str, mode_value.tolist()))

# Add mode to summary
summary.loc['mode'] = mode_str

# Print the updated summary
print("Statistical Summary of 'price_per_ton_EUR':")
print(summary)

# Set the font to Arial & 12 for plot
rcParams['font.family'] = 'Arial'
rcParams['font.size'] = 20

# Histogram of 'price_per_ton_EUR'
plt.figure(figsize=(10, 6))
sns.histplot(data_subset_cleaned['price_per_ton_EUR'], bins=30, kde=True)
plt.title('Distribution of Price per Ton of BCR (EUR)')
plt.xlabel('Price per Ton (EUR/ton BCR)')
plt.ylabel('Frequency')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Save the histogram
histogram_path = 'Thesis files/python_folder/price_per_ton_histogram.png'
plt.savefig(histogram_path)
print(f"Histogram saved to {histogram_path}")
plt.close()  # Close the figure to prevent it from displaying in interactive environments


# Boxplot to check for outliers
plt.figure(figsize=(10, 6))
sns.boxplot(x=data_subset_cleaned['price_per_ton_EUR'])
plt.title('Boxplot of Price per Ton of BCR (EUR/ton BCR)')
plt.xlabel('Price per Ton (EUR/ton BCR)')

# Save the boxplot
boxplot_path = 'Thesis files/python_folder/price_per_ton_boxplot.png'
plt.savefig(boxplot_path)
print(f"Boxplot saved to {boxplot_path}")
plt.close()

#transactions between 100-200 EUR
# Calculate total number of transactions
total_transaction_count = data_subset_cleaned.shape[0]

# Count transactions with prices between 100 and 200 EUR/ton
transaction_count = data_subset_cleaned[(data_subset_cleaned['price_per_ton_EUR'] >= 100) & (data_subset_cleaned['price_per_ton_EUR'] <= 200)].shape[0]

# Calculate the percentage of transactions in the 100-200 EUR/ton range
percentage_100_200 = (transaction_count / total_transaction_count) * 100


# Create a DataFrame for the count and percentage statistics
transaction_summary = pd.DataFrame({
    'Metric': ['Total Transactions', 'Transactions 100-200 EUR/ton', 'Percentage 100-200 EUR/ton'],
    'Value': [total_transaction_count, transaction_count, round(percentage_100_200, 2)]
})

#Prep excel
# Transform summary to DataFrame for export
summary_df = summary.to_frame(name='price_per_ton_EUR_summary')

# Export summary to Excel
output_filename = 'Thesis files/python_folder/Statistical_Summary.xlsx'

with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
    summary_df.to_excel(writer, sheet_name='Statistical summary')
    # Write the transaction count and percentage statistics to a new sheet
    transaction_summary.to_excel(writer, sheet_name='Transaction Summary', index=False)
    print(f"Statistical summary saved to {output_filename}")
