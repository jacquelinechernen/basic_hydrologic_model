import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

csv_file = "model_data.csv"
data = pd.read_csv(csv_file)

data.columns = [
    "Julian_day",
    "Precipitation_mm_per_d",
    "Temperature_C",
    "PET_mm_per_d",
    "Observed_streamflow_m3_per_s"
]

# Model parameters
c = 0.3  # Unitless
S_max = 200.0  # mm
k = 0.1  # d^-1
A = 38.77 * 1e6  # km^2 to m^2
initial_storage = 50.0  # mm
delta_t = 1  # day

# Initialize variables
storage = initial_storage
storage_series = []  # To store storage values
streamflow_series = []  # To store streamflow values

# Iterate through each day in the dataset
for i, row in data.iterrows():
    P = row["Precipitation_mm_per_d"]
    PET = row["PET_mm_per_d"]
    
    # Step 1: Infiltration and Runoff
    I = (1 - c) * P  # Infiltration
    R = P - I  # Runoff
    
    # Step 2: Evapotranspiration
    E = PET * (storage / S_max) if storage > 0 else 0
    
    # Step 3: Baseflow
    B = k * storage
    
    # Update storage with limits
    delta_storage = I - E - B
    storage += delta_storage
    overflow = max(storage - S_max, 0)
    storage = min(max(storage, 0), S_max)
    
    # Streamflow
    Q = R + overflow + B  # Total streamflow at outlet
    
    # Append results
    storage_series.append(storage)
    streamflow_series.append(Q)

# Add results to the dataframe
data["Storage_mm"] = storage_series
data["Streamflow_m3_per_s"] = np.array(streamflow_series) * A / (1000 * 86400)  # Convert mm/day to m³/s

# Perform a mass balance check
total_precipitation = data["Precipitation_mm_per_d"].sum() * A / 1000  # Total precipitation (m³)
total_evapotranspiration = (data["PET_mm_per_d"] * data["Storage_mm"] / S_max).sum() * A / 1000  # Total ET (m³)
total_runoff = data["Streamflow_m3_per_s"].sum()  # Total streamflow (m³)
total_storage_change = (storage_series[-1] - initial_storage) * A / 1000  # Storage change (m³)
mass_balance = total_precipitation - (total_evapotranspiration + total_runoff + total_storage_change)

mass_balance, data.head()  # Display mass balance check and sample data

# Plot Storage Over Time
plt.figure(figsize=(10, 6))
plt.plot(data["Julian_day"], data["Storage_mm"], label="Storage (mm)")
plt.title("Storage Over Time")
plt.xlabel("Julian Day")
plt.ylabel("Storage (mm)")
plt.legend()
plt.grid()
plt.show()

# Plot Observed vs Simulated Streamflow
plt.figure(figsize=(12, 6))
plt.plot(
    data["Julian_day"], 
    data["Observed_streamflow_m3_per_s"], 
    label="Observed Streamflow (m³/s)", 
    color="blue", 
    linestyle="--"
)
plt.plot(
    data["Julian_day"], 
    data["Streamflow_m3_per_s"], 
    label="Simulated Streamflow (m³/s)", 
    color="orange"
)
#plt.title("Observed vs Simulated Streamflow")
plt.xlabel("Julian Day")
plt.ylabel("Streamflow (m³/s)")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()
