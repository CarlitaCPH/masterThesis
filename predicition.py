import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

#check under view command pallete, interpretor, version it runs on in case libraries dont work

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

# Create the subset with the specified columns
# Create the subset with the specified columns and filter for Biochar Carbon Removal (BCR)
data_subset = data[columns_to_keep].copy()[data['method'] == 'Biochar Carbon Removal (BCR)']

# Add a new column 'price_per_ton_USD'
data_subset['price_per_ton_USD'] = data_subset['price_usd'] / data_subset['tons_purchased']
#round to two decimals
data_subset['price_per_ton_USD'] = data_subset['price_per_ton_USD'].round(2)

# Convert `announcement_date` to a numerical format (e.g., days since the first date)
data_subset['announcement_date'] = pd.to_datetime(data_subset['announcement_date'])
data_subset['days_since_start'] = (data_subset['announcement_date'] - data_subset['announcement_date'].min()).dt.days

# Inspect the data to ensure it's loaded correctly
print(data_subset.head())


data_subset_cleaned = data_subset.dropna(subset=['price_per_ton_USD'])
# print cleaned data set
print(data_subset_cleaned)

# change rows where 'price_per_ton_USD' is infinite
data_subset_cleaned = data_subset_cleaned[~np.isinf(data_subset_cleaned['price_per_ton_USD'])]

# Display the cleaned DataFrame
print(data_subset_cleaned)


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


""" 
# Export the data_subset to an Excel file
output_filename = 'carla_cdr_prediction.xlsx'
# Export the data_subset to separate sheets in the same Excel file
with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
    data_subset.to_excel(writer, sheet_name='Data Subset', index=False)

print(f"Data subset and statistics have been successfully exported to '{output_filename}'.")

# Print the current working directory
print("the file can be found here:", os.getcwd())

"""