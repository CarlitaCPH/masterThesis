import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA

# Preparation dataset
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

# Remove rows where 'price_per_ton_EUR' is infinite
data_subset_cleaned = data_subset_cleaned[~np.isinf(data_subset_cleaned['price_per_ton_USD'])]

# Define the conversion rate from USD to EUR
conversion_rate = 1.0718

# Convert 'price_per_ton_USD' to EUR and add a new column 'price_per_ton_EUR'
data_subset_cleaned['price_per_ton_EUR'] = data_subset_cleaned['price_per_ton_USD'] / conversion_rate

# Set 'announcement_date' as the index for time series analysis
# Aggregation: Median price for duplicate timestamps
aggregated_data = data_subset_cleaned.groupby('announcement_date', as_index=True).agg({
    'price_per_ton_EUR': 'median'  # median price per timestamp
}).dropna()

# Test for stationarity
# Run ADF Test on aggregated data
result = adfuller(aggregated_data['price_per_ton_EUR'])

# Extract values
adf_statistic = result[0]
p_value = result[1]
num_lags = result[2]
num_obs = result[3]
critical_values = result[4]

# Print results in a structured way
print("Augmented Dickey-Fuller Test Results:")
print(f"ADF Statistic: {adf_statistic:.4f}")
print(f"p-value: {p_value:.4f}")
print(f"Number of Lags Used: {num_lags}")
print(f"Number of Observations Used: {num_obs}")

print("Critical Values for Different Confidence Levels:")
for key, value in critical_values.items():
    print(f"   {key}: {value:.4f}")

# Interpret the p-value
if result[1] < 0.05:
    print("The series is stationary (Reject H0).")
else:
    print("The series is non-stationary (Fail to reject H0).")


# Prediction of future values
# Ensure the index is a DateTime index
#aggregated_data = aggregated_data.asfreq('D')  # 'D' for daily data
#print(aggregated_data.index.freq)

# Step 1: Visualize the time series
plt.figure(figsize=(12, 6))
plt.plot(aggregated_data.index, aggregated_data['price_per_ton_EUR'], marker='o', linestyle='-')
plt.xlabel("Announcement Date")
plt.ylabel("Price per Ton (EUR)")
plt.title("Time Series of Price per Ton (EUR)")
plt.grid(True)
plt.show()

# Step 2: Plot ACF and PACF to identify ARIMA parameters
fig, ax = plt.subplots(1, 2, figsize=(12, 6))

plot_acf(aggregated_data['price_per_ton_EUR'], ax=ax[0], lags=30)
ax[0].set_title("Autocorrelation Function (ACF)")

plot_pacf(aggregated_data['price_per_ton_EUR'], ax=ax[1], lags=30)
ax[1].set_title("Partial Autocorrelation Function (PACF)")

plt.show()

# Step 3: Fit the ARIMA model
# Select ARIMA parameters based on ACF and PACF plots
p, d, q = 1, 0, 1  # Adjust these values if needed

model = ARIMA(aggregated_data['price_per_ton_EUR'], order=(p, d, q))
model_fit = model.fit()

# Step 4: Print model summary
print(model_fit.summary())

# Step 5: Forecast future values
forecast_steps = 12  # Forecast for 12 future periods
forecast = model_fit.forecast(steps=forecast_steps)

# Step 6: Plot the forecast
plt.figure(figsize=(12, 6))
plt.plot(aggregated_data.index, aggregated_data['price_per_ton_EUR'], label='Actual Data', marker='o')
plt.plot(pd.date_range(start=aggregated_data.index[-1], periods=forecast_steps+1, freq='D')[1:], 
         forecast, label='Forecast', color='red', linestyle='dashed', marker='o')

plt.xlabel("Time")
plt.ylabel("Price per Ton (EUR)")
plt.title("ARIMA Forecast of Price per Ton (EUR)")
plt.legend()
plt.grid(True)
plt.show()
plt.close()
