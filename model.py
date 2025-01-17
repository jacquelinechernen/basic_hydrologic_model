import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# path to csv input file
csv_file = '/content/Storage_Calculation_Results.csv'

# Read the data from the CSV file
df = pd.read_csv(csv_file)

# Initialize storage
storage = 100.0  # Initial water storage
storage_time_series = []

# Perform calculations using numpy for efficiency
precipitation = df["Precipitation"].values
evapotranspiration = df["Evapotranspiration"].values
runoff = df["Runoff"].values

# Calculate storage for each day
for p, e, r in zip(precipitation, evapotranspiration, runoff):
    delta_storage = p - e - r
    storage += delta_storage
    storage = max(storage, 0)  # Ensure storage doesn't go negative
    storage_time_series.append(storage)

# Add the storage results to the DataFrame
df["Storage"] = storage_time_series

# Plot the storage time series as a red line
plt.figure(figsize=(8, 6))
plt.plot(df["Timestep"], df["Storage"], color='red', marker='o', linestyle='-', label='Storage')
plt.title('Water Storage Over Time')
plt.xlabel('Timestep')
plt.ylabel('Storage (mm)')
plt.xticks(df["Timestep"])
#plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()