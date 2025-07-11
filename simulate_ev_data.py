def simulate_ev_data():
    import pandas as pd
    import numpy as np
    import random
    from datetime import datetime, timedelta
    stations = [
        {"station_id": 1, "station_name": "Connaught Place", "latitude": 28.6315, "longitude": 77.2167},
        {"station_id": 2, "station_name": "Saket", "latitude": 28.5222, "longitude": 77.2076},
        {"station_id": 3, "station_name": "Dwarka", "latitude": 28.5921, "longitude": 77.0460},
        {"station_id": 4, "station_name": "Karol Bagh", "latitude": 28.6512, "longitude": 77.1906},
        {"station_id": 5, "station_name": "Lajpat Nagar", "latitude": 28.5672, "longitude": 77.2436},
        {"station_id": 6, "station_name": "Rajouri Garden", "latitude": 28.6426, "longitude": 77.1232},
        {"station_id": 7, "station_name": "Vasant Kunj", "latitude": 28.5273, "longitude": 77.1506},
        {"station_id": 8, "station_name": "Preet Vihar", "latitude": 28.6507, "longitude": 77.3012},
        {"station_id": 9, "station_name": "Rohini", "latitude": 28.7499, "longitude": 77.0560},
        {"station_id": 10, "station_name": "Nehru Place", "latitude": 28.5483, "longitude": 77.2513},
    ]
    vehicle_types = ["car", "scooter"]
    today = datetime.now().date()
    days = 7
    rows = []
    start_date = today - timedelta(days=today.weekday() + 7)
    for day in range(days):
        date = start_date + timedelta(days=day)
        for station in stations:
            for hour in range(24):
                if 8 <= hour <= 10 or 17 <= hour <= 20:
                    vehicles_charged = np.random.poisson(10) + 5
                    traffic_congestion = "High"
                elif 7 <= hour < 8 or 10 < hour < 12 or 16 <= hour < 17 or 20 < hour < 22:
                    vehicles_charged = np.random.poisson(5) + 2
                    traffic_congestion = "Medium"
                else:
                    vehicles_charged = np.random.poisson(2)
                    traffic_congestion = "Low"
                vehicle_type = random.choices(vehicle_types, weights=[0.7, 0.3])[0]
                avg_session_minutes = round(np.random.normal(40 if vehicle_type=="car" else 25, 8), 1)
                rows.append({
                    "station_id": station["station_id"],
                    "station_name": station["station_name"],
                    "latitude": station["latitude"],
                    "longitude": station["longitude"],
                    "date": date.strftime("%d-%m-%Y"),
                    "hour": hour,
                    "vehicles_charged": max(0, vehicles_charged),
                    "vehicle_type": vehicle_type,
                    "avg_session_minutes": max(10, avg_session_minutes),
                    "traffic_congestion": traffic_congestion
                })
    df = pd.DataFrame(rows)
    return df
