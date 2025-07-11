import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import numpy as np

# Load the data
df = pd.read_csv("ev_demand_data.csv")

# Convert date and hour to datetime for Prophet
df["ds"] = pd.to_datetime(df["date"], format="%d-%m-%Y") + pd.to_timedelta(df["hour"], unit="h")

results = []
peak_info = []

for station_id, station_name in df.groupby(["station_id", "station_name"]).groups:
    for vtype in ["car", "scooter"]:
        station_df = df[(df["station_id"] == station_id) & (df["vehicle_type"] == vtype)]
        # Group by ds (hourly)
        ts = station_df.groupby("ds")["vehicles_charged"].sum().reset_index()
        ts = ts.rename(columns={"ds": "ds", "vehicles_charged": "y"})
        # Prophet forecast
        m = Prophet()
        m.fit(ts)
        future = m.make_future_dataframe(periods=72, freq='H')
        forecast = m.predict(future)
        # Plot
        plt.figure(figsize=(10,4))
        m.plot(forecast, xlabel="Time", ylabel="Vehicles Charged")
        plt.title(f"Forecast for {station_name} ({vtype})")
        plt.tight_layout()
        plt.savefig(f"forecast_{station_name}_{vtype}.png")
        plt.close()
        # Save forecast to CSV for Streamlit app
        forecast["station_name"] = station_name
        forecast["vehicle_type"] = vtype
        forecast["latitude"] = station_df["latitude"].iloc[0]
        forecast["longitude"] = station_df["longitude"].iloc[0]
        forecast.to_csv(f"forecast_{station_name}_{vtype}.csv", index=False)
        # Find peak hour in forecast
        peak_row = forecast.iloc[-72:]["yhat"].idxmax()
        peak_time = forecast.iloc[peak_row]["ds"]
        peak_value = forecast.iloc[peak_row]["yhat"]
        peak_info.append({
            "station_id": station_id,
            "station_name": station_name,
            "vehicle_type": vtype,
            "peak_hour": peak_time,
            "predicted_vehicles": peak_value
        })

# Find top 3 busiest stations (by max predicted vehicles in forecast)
busy_df = pd.DataFrame(peak_info)
top3 = busy_df.sort_values("predicted_vehicles", ascending=False).head(3)
print("Top 3 busiest stations (predicted) and their peak hour:")
print(top3[["station_name", "vehicle_type", "peak_hour", "predicted_vehicles"]])
