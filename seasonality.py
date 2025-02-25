import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams

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

# Handle duplicate timestamps by grouping them
# Aggregation: Mean price per ton, Sum of tons purchased
aggregated_data = data_subset_cleaned.groupby('announcement_date').agg({
    'price_per_ton_EUR': 'mean',  
    'tons_purchased': 'sum'
}).reset_index()

# Basic Statistical Analysis
summary = aggregated_data['price_per_ton_EUR'].describe().round(2)
print("Statistical Summary of 'price_per_ton_EUR':")
print(summary)

# Calculate the mode (there may be multiple modes)
mode_value = aggregated_data['price_per_ton_EUR'].mode().round(2)
mode_str = ', '.join(map(str, mode_value.tolist()))
summary.loc['mode'] = mode_str

# Print updated summary
print("Statistical Summary of 'price_per_ton_EUR':")
print(summary)

# Set the font to Arial & 12 for plot
rcParams['font.family'] = 'Arial'
rcParams['font.size'] = 20

# Line Plot of Price Per Ton Over Time
plt.figure(figsize=(12, 12))
plt.plot(aggregated_data['announcement_date'], aggregated_data['price_per_ton_EUR'], marker='o', linestyle='-', label='Price per Ton (EUR)')
plt.xlabel('Announcement Date')
plt.ylabel('Price per Ton (EUR)')
plt.title('Price per Ton of BCR Over Time')
plt.legend()
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Save the line plot
lineplot_path = '/Users/carlasoleta/Library/CloudStorage/GoogleDrive-carla.soleta@gmail.com/My Drive/Thesis files/python_folder/price_per_ton_lineplot.png'
plt.savefig(lineplot_path)
print(f"Line plot saved to {lineplot_path}")
plt.close()  # Close the figure to prevent display issues

# Export summary statistics to Excel
output_filename = '/Users/carlasoleta/Library/CloudStorage/GoogleDrive-carla.soleta@gmail.com/My Drive/Thesis files/python_folder/Seasonality.xlsx'

# Convert summary to DataFrame for export
summary_df = summary.to_frame(name='price_per_ton_EUR_summary')

with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
    summary_df.to_excel(writer, sheet_name='Statistical summary')
    print(f"Statistical summary saved to {output_filename}")


import matplotlib.pyplot as plt
import seaborn as sns

# Extract Year and Month
aggregated_data['year'] = aggregated_data['announcement_date'].dt.year
aggregated_data['month'] = aggregated_data['announcement_date'].dt.month

# Group by Year and Month, then calculate average price per ton
monthly_avg_by_year = aggregated_data.groupby(['year', 'month'])['price_per_ton_EUR'].mean().reset_index()

# Pivot table for visualization
seasonality_pivot = monthly_avg_by_year.pivot(index='month', columns='year', values='price_per_ton_EUR')

# Plot seasonality trends by year
plt.figure(figsize=(12, 6))
sns.lineplot(data=seasonality_pivot, marker="o")

# Customize the plot
plt.xlabel('Month')
plt.ylabel('Average Price per Ton (EUR)')
plt.title('Monthly Seasonality of Price per Ton of BCR (Separated by Year)')
plt.xticks(ticks=range(1, 13), labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
plt.legend(title="Year", loc="upper right")
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Save the figure
seasonality_plot_path = '/Users/carlasoleta/Library/CloudStorage/GoogleDrive-carla.soleta@gmail.com/My Drive/Thesis files/python_folder/monthly_seasonality_by_year.png'
plt.savefig(seasonality_plot_path)

# Show the plot
plt.show()
plt.close()  # Close the figure to prevent display issues

print(f"Seasonality trends by year plot saved to {seasonality_plot_path}")
