# Station capacity dictionary (car/scooter 20-30)
station_capacity = {
    "Connaught Place": {"car": 30, "scooter": 28},
    "Nehru Place": {"car": 28, "scooter": 26},
    "Rajouri Garden": {"car": 27, "scooter": 25},
    "Saket": {"car": 29, "scooter": 27},
    "Dwarka": {"car": 25, "scooter": 23},
    "Karol Bagh": {"car": 26, "scooter": 24},
    "Lajpat Nagar": {"car": 30, "scooter": 29},
    "Vasant Kunj": {"car": 24, "scooter": 21},
    "Preet Vihar": {"car": 22, "scooter": 20},
    "Rohini": {"car": 20, "scooter": 20},
}

# Function to get overloaded stations
def get_overloaded_stations(forecast_df, capacity_dict):
    peak_df = (
        forecast_df.groupby(['station_id', 'station_name', 'vehicle_type'], as_index=False)
        .agg({'yhat': 'max'})
        .rename(columns={'yhat': 'forecasted_peak'})
    )
    peak_df['capacity'] = peak_df.apply(
        lambda row: capacity_dict.get(row['station_name'], {}).get(row['vehicle_type'], np.nan),
        axis=1
    )
    peak_df['overload_pct'] = peak_df['forecasted_peak'] / peak_df['capacity']
    peak_df['unmet_demand'] = peak_df['forecasted_peak'] - peak_df['capacity']
    overloaded = peak_df[peak_df['overload_pct'] > 0.9]
    message = ""
    # Always show 3 stations: overloaded first, then next busiest
    if overloaded.empty:
        busiest = peak_df.sort_values('forecasted_peak', ascending=False).head(3)
        busiest['recommendation'] = 'Monitor usage'
        result = busiest
        message = "No station exceeds 90% of its capacity. Showing top 3 busiest stations."
    else:
        overloaded = overloaded.copy()
        overloaded['recommendation'] = overloaded['unmet_demand'].apply(
            lambda x: f"Add {int(np.ceil(x/5))} more ports" if x > 0 else "Monitor usage"
        )
        # Get next busiest stations not overloaded
        not_overloaded = peak_df[~peak_df.index.isin(overloaded.index)]
        next_busiest = not_overloaded.sort_values('forecasted_peak', ascending=False).head(2)
        next_busiest['recommendation'] = 'Monitor usage'
        result = pd.concat([overloaded, next_busiest]).sort_values('forecasted_peak', ascending=False).head(3)
        if (overloaded['forecasted_peak'] > overloaded['capacity']).any():
            message = "Some stations exceed their maximum capacity! Immediate action required."
        else:
            message = "Some stations are above 90% capacity. Consider adding more ports."
    return result[['station_id', 'vehicle_type', 'forecasted_peak', 'capacity', 'unmet_demand', 'recommendation']], message
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from prophet import Prophet

st.title("EV Charging Demand Forecast Dashboard")


# Simulate and load data in-memory
@st.cache_data
def load_ev_data():
    from simulate_ev_data import simulate_ev_data
    return simulate_ev_data()


df = load_ev_data()

# Sidebar filters (use raw data for station/type selection)
station = st.sidebar.selectbox("Select Station", df["station_name"].unique())
vehicle_type = st.sidebar.selectbox("Select Vehicle Type", df["vehicle_type"].unique())
# Get available dates for selected station/type
available_dates = pd.to_datetime(df[(df["station_name"] == station) & (df["vehicle_type"] == vehicle_type)]["date"], format="%d-%m-%Y").dt.date.unique()
date = st.sidebar.date_input("Select Date", value=min(available_dates) if len(available_dates) > 0 else None, min_value=min(available_dates) if len(available_dates) > 0 else None, max_value=max(available_dates) if len(available_dates) > 0 else None)

# Filter for previous 7 days
selected_date = pd.to_datetime(date)
train_start = selected_date - pd.Timedelta(days=7)
train_end = selected_date - pd.Timedelta(days=1)
train_mask = (pd.to_datetime(df["date"], format="%d-%m-%Y") >= train_start) & (pd.to_datetime(df["date"], format="%d-%m-%Y") <= train_end)
station_mask = (df["station_name"] == station) & (df["vehicle_type"] == vehicle_type)
train_df = df[train_mask & station_mask]

if train_df.empty:
    st.warning("Not enough historical data for selected station/type/date.")
else:
    # Prepare time series for Prophet
    ts = train_df.groupby(["date", "hour", "latitude", "longitude"])["vehicles_charged"].sum().reset_index()
    ts["ds"] = pd.to_datetime(ts["date"], format="%d-%m-%Y") + pd.to_timedelta(ts["hour"], unit="h")
    ts = ts.rename(columns={"ds": "ds", "vehicles_charged": "y"})
    m = Prophet()
    m.fit(ts[["ds", "y"]])
    # Forecast for selected date (24 hours)
    forecast_hours = pd.date_range(selected_date, selected_date + pd.Timedelta(hours=23), freq="H")
    future = pd.DataFrame({"ds": forecast_hours})
    forecast = m.predict(future)
    forecast["station_name"] = station
    forecast["vehicle_type"] = vehicle_type
    forecast["latitude"] = ts["latitude"].iloc[0] if len(ts) > 0 else None
    forecast["longitude"] = ts["longitude"].iloc[0] if len(ts) > 0 else None

    # Build a full forecast_df for all stations/types for overload analysis
    all_forecast_rows = []
    for s in df["station_name"].unique():
        for vtype in ["car", "scooter"]:
            mask = (df["station_name"] == s) & (df["vehicle_type"] == vtype)
            train = df[train_mask & mask]
            if not train.empty:
                ts = train.groupby(["date", "hour", "latitude", "longitude"])["vehicles_charged"].sum().reset_index()
                ts["ds"] = pd.to_datetime(ts["date"], format="%d-%m-%Y") + pd.to_timedelta(ts["hour"], unit="h")
                ts = ts.rename(columns={"ds": "ds", "vehicles_charged": "y"})
                m = Prophet()
                m.fit(ts[["ds", "y"]])
                future = pd.DataFrame({"ds": forecast_hours})
                f = m.predict(future)
                for _, row in f.iterrows():
                    all_forecast_rows.append({
                        "station_id": df[df["station_name"] == s]["station_id"].iloc[0],
                        "station_name": s,
                        "vehicle_type": vtype,
                        "ds": row["ds"],
                        "yhat": row["yhat"]
                    })
    forecast_df = pd.DataFrame(all_forecast_rows)

    st.subheader("🔺 Overload or High-Usage Station Suggestions (Car)")
    car_df = forecast_df[forecast_df["vehicle_type"] == "car"]
    car_suggestions, car_message = get_overloaded_stations(car_df, station_capacity)
    st.dataframe(car_suggestions)
    st.info(car_message)

    st.subheader("🔺 Overload or High-Usage Station Suggestions (Scooter)")
    scooter_df = forecast_df[forecast_df["vehicle_type"] == "scooter"]
    scooter_suggestions, scooter_message = get_overloaded_stations(scooter_df, station_capacity)
    st.dataframe(scooter_suggestions)
    st.info(scooter_message)
    st.subheader(f"Forecasted Demand for {station} ({vehicle_type}) on {date}")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(forecast["ds"], forecast["yhat"], marker='o', color='tab:blue', label='Predicted Demand')
    if "yhat_lower" in forecast.columns and "yhat_upper" in forecast.columns:
        ax.fill_between(forecast["ds"], forecast["yhat_lower"], forecast["yhat_upper"], color='tab:blue', alpha=0.2, label='Prediction Interval')
    ax.set_xlabel("Time")
    ax.set_ylabel("Predicted Vehicles Charged")
    ax.set_title(f"Predicted EV Charging Demand for {station} ({vehicle_type})")
    ax.legend()
    st.pyplot(fig)

    # Map: show all stations. Selected station shows forecast, others show historical max for selected type
    map_df = df[df["vehicle_type"] == vehicle_type].groupby(["station_name", "latitude", "longitude"])["vehicles_charged"].max().reset_index()
    # Add forecasted demand for selected station
    map_df["forecasted_demand"] = map_df["yhat"] if "yhat" in map_df.columns else map_df["vehicles_charged"]
    selected_max = forecast["yhat"].max()
    map_df.loc[map_df["station_name"] == station, "forecasted_demand"] = selected_max
    fig_map = px.scatter_mapbox(map_df, lat="latitude", lon="longitude", color="forecasted_demand",
                               hover_name="station_name", size="forecasted_demand",
                               color_continuous_scale="Viridis", zoom=10, height=400)
    fig_map.update_layout(mapbox_style="open-street-map")
    st.subheader("Station Map (All stations, marker color = forecasted or historical demand)")
    st.plotly_chart(fig_map)

    # Top 5 stations by predicted usage (for selected date/type)
    # For demo, use all stations for selected type and date
    top_df = []
    for s in df["station_name"].unique():
        mask = (df["station_name"] == s) & (df["vehicle_type"] == vehicle_type)
        train = df[train_mask & mask]
        if not train.empty:
            ts = train.groupby(["date", "hour", "latitude", "longitude"])["vehicles_charged"].sum().reset_index()
            ts["ds"] = pd.to_datetime(ts["date"], format="%d-%m-%Y") + pd.to_timedelta(ts["hour"], unit="h")
            ts = ts.rename(columns={"ds": "ds", "vehicles_charged": "y"})
            m = Prophet()
            m.fit(ts[["ds", "y"]])
            future = pd.DataFrame({"ds": forecast_hours})
            f = m.predict(future)
            top_df.append({"station_name": s, "yhat": f["yhat"].max()})
    top5 = pd.DataFrame(top_df).sort_values("yhat", ascending=False).head(5)
    st.subheader("Top 5 Stations by Predicted Usage")
    st.table(top5[["station_name", "yhat"]])
