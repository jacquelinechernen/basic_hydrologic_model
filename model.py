import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data
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
c = -1  # Unitless runoff coefficient
S_max = 200.0  # mm, maximum soil water storage
k = 0.1  # d^-1, baseflow coefficient
A = 38.77 * 1e6  # m², watershed area (converted from km²)
initial_storage = 50.0  # mm, initial soil water storage
delta_t = 1  # day, time step

print(f"Initial storage exceeds max soil water storage! {initial_storage:.2f} > {S_max:.2f}")

# Initialize variables
storage = initial_storage
storage_series = []  # To store storage values
streamflow_series = []  # To store streamflow values
overflow_series = []  # To track overflow
evapotranspiration_series = []  # To track ET
runoff_series = []  # To track runoff
baseflow_series = []  # To track baseflow

# Time loop through dataset
for i, row in data.iterrows():
    P = row["Precipitation_mm_per_d"]
    PET = row["PET_mm_per_d"]
    
    # Step 1: Precipitation and potential evapotranspiration adjustment
    P_effective = P  
    PET_effective = PET  

    # Step 2: Runoff and Infiltration
    R = c * P_effective  # Runoff (mm/day)
    I = (1 - c) * P_effective  # Infiltration (mm/day)
    
    # Update storage with infiltration
    storage += I * delta_t

    # Step 3: Actual Evapotranspiration (AET)
    AET = (storage / S_max) * PET_effective  # ET proportional to storage availability
    AET = min(AET * delta_t, storage)  # Ensure ET does not exceed available storage
    storage -= AET  # Update storage after ET

    # Step 4: Baseflow calculation
    B = k * storage * delta_t  # Baseflow proportional to storage
    storage -= B * delta_t  # Update storage after baseflow

   # Step 5: Overflow calculation (saturation excess runoff)
    if storage > S_max:
        O = (storage - S_max) / delta_t  # Calculate overflow as excess water
        storage = S_max  # Cap storage at maximum capacity
    else:
        O = 0  # No overflow if within capacity

    # Step 6: Total Streamflow calculation
    Q = (R + B + O) * delta_t
    
    # Convert from mm/day to m³/s
    Q_cms = Q * (A / 1000) / (86400 * delta_t)

    # Store results
    storage_series.append(storage)
    streamflow_series.append(Q_cms)
    overflow_series.append(O)
    evapotranspiration_series.append(AET)
    runoff_series.append(R)
    baseflow_series.append(B)

# Add results to the dataframe
data["Storage_mm"] = storage_series
data["Streamflow_m3_per_s"] = streamflow_series
data["Overflow_mm"] = overflow_series
data["Evapotranspiration_mm"] = evapotranspiration_series
data["Runoff_mm"] = runoff_series
data["Baseflow_mm"] = baseflow_series

# Perform mass balance check
total_precipitation = data["Precipitation_mm_per_d"].sum() * A / 1000  # Convert to m³
total_evapotranspiration = sum(evapotranspiration_series) * A / 1000  # Total ET in m³
total_runoff = sum(streamflow_series) * 86400  # Convert to m³
total_storage_change = (storage_series[-1] - initial_storage) * A / 1000  # Storage change in m³

# mass balance calculations
LHS = -1 * ((storage_series[-1] - initial_storage) * A / 1000 ) # Convert storage change to m³
RHS = -1 * (total_precipitation - (total_evapotranspiration + total_runoff))

mass_balance = LHS - RHS

print(f"Mass balance check: {mass_balance:.2f}")
print(f"Left hand side: {LHS:.2f} m³")
print(f"Right hand side: {RHS:.2f} m³")

# # Report streamflow on day 100
# day_100_streamflow = data.loc[data["Julian_day"] == 100, "Streamflow_m3_per_s"].values[0]
# print(f"Streamflow on day 100: {day_100_streamflow:.2f} m³/s (average rate over the timestep)")

# # Report soil water storage at the start of day 100
# day_100_storage = data.loc[data["Julian_day"] == 100, "Storage_mm"].values[0]
# print(f"Soil water storage at the start of day 100: {day_100_storage:.2f} mm")

# # Calculate total runoff and overflow over the entire period
# total_runoff_mm = sum(runoff_series)  # Total runoff in mm
# total_overflow_mm = sum(overflow_series)  # Total overflow in mm

# # Print results
# print(f"Total simulated runoff: {total_runoff_mm:.2f} mm")
# print(f"Total simulated overflow: {total_overflow_mm:.2f} mm")

# # Compare runoff and overflow
# if total_runoff_mm > total_overflow_mm:
#     print("Total runoff is greater than total overflow.")
# elif total_runoff_mm < total_overflow_mm:
#     print("Total overflow is greater than total runoff.")
# else:
#     print("Total runoff and total overflow are equal.")

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
plt.xlabel("Julian Day")
plt.ylabel("Streamflow (m³/s)")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()
