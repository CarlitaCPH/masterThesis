import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

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

# Create the subset with the specified columns and filter for Biochar Carbon Removal (BCR)
data_subset = data[columns_to_keep].copy()[data['method'] == 'Biochar Carbon Removal (BCR)']

# Calculate price per ton
data_subset['price_per_ton_USD'] = data_subset['price_usd'] / data_subset['tons_purchased']
data_subset['price_per_ton_USD'] = data_subset['price_per_ton_USD'].round(2)

# Convert `announcement_date` to a datetime format and calculate days since the first date
data_subset['announcement_date'] = pd.to_datetime(data_subset['announcement_date'])
data_subset['days_since_start'] = (data_subset['announcement_date'] - data_subset['announcement_date'].min()).dt.days

# Drop rows with NaN values in `price_per_ton_USD`
data_subset_cleaned = data_subset.dropna(subset=['price_per_ton_USD'])

# Remove rows where `price_per_ton_USD` is infinite
data_subset_cleaned = data_subset_cleaned[~np.isinf(data_subset_cleaned['price_per_ton_USD'])]

# Group by `announcement_date` and calculate the mean of `price_per_ton_USD`
merged_data_mean = data_subset_cleaned.groupby('announcement_date').agg({
    'tons_purchased': 'sum',
    'price_usd': 'sum',
    'tons_delivered': 'sum',
    'price_per_ton_USD': 'mean',         # Take the mean of price per ton
    'status': 'first',
    'method': 'first',
    'marketplace_name': lambda x: ', '.join(x.dropna().astype(str).unique()),  # Concatenate unique marketplace names, ignoring NaN
    'purchaser_name': lambda x: ', '.join(x.unique()),
    'supplier_name': lambda x: ', '.join(x.unique()),
    'days_since_start': 'first'          # Take days since start as it’s the same per date
}).reset_index()


#round to two decimals
merged_data_mean['price_per_ton_USD'] = merged_data_mean['price_per_ton_USD'].round(2)

print("Merged data with mean of price_per_ton_USD:")
print(merged_data_mean)
print(merged_data_mean['price_per_ton_USD'])

#statistics: compare overall transactions in BCR, how many with price, how many after merged
# Calculate the statistics
stats_data = {
    "Dataset": ["Data", "Data Subset", "Data Subset Cleaned", "Merged Data Mean"],
    "Transactions": [len(data), len(data_subset), len(data_subset_cleaned), len(merged_data_mean)],
    "Description": [
        "Total transactions in dataset",
        "Filtered for Biochar Carbon Removal (BCR)",
        "Cleaned BCR with valid price per ton",
        "Grouped BCR data with mean price per ton"
    ]
}

# Create a DataFrame with the statistics
stats_df = pd.DataFrame(stats_data)

# Calculate the 'Percentage' column (4 values)
stats_df['Percentage'] = [
    len(data) / len(data),                            # data/data
    len(data_subset) / len(data),                     # data_subset/data
    len(data_subset_cleaned) / len(data_subset),      # data_subset_cleaned/data_subset
    len(merged_data_mean) / len(data_subset_cleaned), # merged_data_mean/data_subset_cleaned
]

# Calculate the 'BCR Percentage' column (4 values)
stats_df['BCR Percentage'] = [
    len(data) / len(data),                        # data/data
    len(data_subset) / len(data_subset),          # data_subset/data_subset
    len(data_subset_cleaned) / len(data_subset),  # data_subset_cleaned/data_subset
    len(merged_data_mean) / len(data_subset),     # merged_data_mean/data_subset
]


# Define the feature (X) and target (y)
X = data_subset_cleaned[['days_since_start']]  # Time feature
y = data_subset_cleaned['price_per_ton_USD']  # Target variable

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a linear regression model
model = LinearRegression()

# Fit the model
model.fit(X_train, y_train)

# Predict on test data
y_pred = model.predict(X_test)

# Calculate and print evaluation metrics
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'Mean Squared Error: {mse:.2f}')
print(f'R-squared: {r2:.2f}')

#stats regression
stats_reg_data = {
    "Metric": ["Mean Squared Error", "R-squared"],
    "Value": [mse, r2]
}

# Create a DataFrame for the stats
stats_reg_df = pd.DataFrame(stats_reg_data)


# Export the data_subset to an Excel file
output_filename = 'carla_cdr_linearRegression_stats.xlsx'
# Export the data_subset to separate sheets in the same Excel file
with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
    merged_data_mean.to_excel(writer, sheet_name='Data Subset', index=False)
    stats_df.to_excel(writer, sheet_name='Transaction Stats', index=False)
    stats_reg_df.to_excel(writer, sheet_name='stats_reg', index=False)

print(f"Data subset has been successfully exported to '{output_filename}'.")

# Print the current working directory
print("the file can be found here:", os.getcwd())
