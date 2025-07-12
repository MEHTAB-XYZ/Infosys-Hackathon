**EV Charging Demand Forecast Dashboard**
Overview
This project is a Streamlit-powered dashboard for simulating, forecasting, and analyzing electric vehicle (EV) charging demand across major stations in Delhi, India. It helps city planners and operators identify overloaded stations, plan infrastructure upgrades, and spot locations suitable for solar-powered charging.

Features
Synthetic Data Simulation:
Generates realistic hourly EV charging data for 10 Delhi stations over 7 days, with congestion and session time modeling.

Forecasting:
Uses Facebook Prophet to predict hourly demand for each station and vehicle type.

Overload Detection:
Compares forecasted demand against station capacity, flags overloads, and recommends additional ports.

Solar Suitability Analysis:
Identifies top stations for solar-powered charging based on daytime demand.

What-If Simulator:
Lets users interactively adjust station, vehicle type, number of ports, demand multiplier, and session time to see impact on overload risk and recommendations.

Interactive Visualizations:
Includes demand charts, station maps, and summary tables.

File Structure
ev_streamlit_app.py
Main Streamlit dashboard app.

simulate_ev_data.py
Generates synthetic EV charging data.

ev_forecast_analysis.py
Batch forecasting and peak analysis script.



Use the sidebar to select station, vehicle type, and date.
Explore overload suggestions, solar suitability, and run What-If simulations at the bottom of the page.
See which stations are at risk of exceeding capacity and get recommendations for adding more ports.

Solar Suitability:
Find stations with highest daytime demand for solar panel installation.

What-If Simulator:
Test scenarios by changing ports, demand, and session time to see how overload risk changes.

**EV Station Recommender**
A visually appealing Streamlit app to recommend the best EV charging stations in Delhi for cars and scooters. The app simulates real-time station data, calculates ETA based on queue and traffic, and displays recommendations in a modern, user-friendly interface.

Features
10 Fixed Delhi Stations: Connaught Place, Saket, Dwarka, Karol Bagh, Lajpat Nagar, Rajouri Garden, Vasant Kunj, Preet Vihar, Rohini, Nehru Place.
Realistic Simulation: Randomized ports, queue, session times, and traffic speed for each station.
Smart ETA Calculation: Combines queue time and travel time for accurate recommendations.
Beautiful UI: Dark mode, colored cards, badges, and two-column layout for easy comparison.
Vehicle Type Selection: Choose car or scooter to see relevant details.
Admin Panel Button: Quick access to a separate admin Streamlit app.

