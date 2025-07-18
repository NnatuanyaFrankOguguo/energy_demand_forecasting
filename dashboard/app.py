
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
st.set_page_config(page_title="Energy Demand Forecasting Dashboard", layout="wide")
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from loggerInfo import get_logger
from datetime import datetime, timedelta
from quality.check_missing import check_missing_values
from quality.check_outliers import check_temperature_outliers, check_energy_outliers
from quality.check_freshness import check_data_freshness
from sklearn.linear_model import LinearRegression
import numpy as np


logger = get_logger("dashboard")

# Load historical data
@st.cache_data(ttl=3600)
def load_data():
    try:
        files = [f for f in os.listdir("data/processed") if f.endswith('.csv')]
        if not files:
            logger.error("No historical data files found.")
            return pd.DataFrame()
        
        latest_file = max(files, key=lambda x: os.path.getctime(os.path.join("data/processed", x)))
        path = os.path.join("data/processed", latest_file)
        df = pd.read_csv(path)
        df["avg_temp"] = (df["TMAX"] + df["TMIN"]) / 2
        df["day_of_week"] = pd.to_datetime(df["date"]).dt.day_name()
        logger.info(f"Loaded historical data from {latest_file}.")
        
        return df
    
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return pd.DataFrame()
    
# Run quality checks
def run_quality_checks(df):
    missing_summary = check_missing_values(df)
    temp_outliers = check_temperature_outliers(df)
    energy_outliers = check_energy_outliers(df)
    data_freshness = check_data_freshness(df)
    
    return missing_summary, temp_outliers, energy_outliers, data_freshness


# Load historical data
df = load_data()
cities = df["city"].unique().tolist()

# Sidebar Filters
st.sidebar.header("Filters Options")
selected_city = st.sidebar.multiselect("Select Cities", cities, default=cities)

# selected_data_type = st.sidebar.selectbox("Select Data Type", options=["All", "Temperature", "Energy"]) if not df.empty else "All"
selected_date_range = st.sidebar.slider("Select Date Range", df["date"].min(), df["date"].max(), (df["date"].min(), df["date"].max())) if not df.empty else (None, None)

df = df[(df["date"] >= pd.to_datetime(selected_date_range[0])) & (df["date"] <= pd.to_datetime(selected_date_range[1]))] if selected_date_range else df
df = df[df["city"].isin(selected_city)] if selected_city else df

# Streamlit app
st.title("Energy Demand Forecasting Quality Dashboard")
st.markdown(f"Last updated: **{df['date'].max().strftime('%Y-%m-%d')}**")
    
# Display Data
if not df.empty:
    st.header("Data Quality Checks")
    missing_summary, temp_outliers, energy_outliers, data_freshness = run_quality_checks(df)
    st.subheader("Missing Values Summary")
    st.write(missing_summary)
    st.subheader("Temperature Outliers")
    st.write(temp_outliers)
    st.subheader("Energy Outliers")
    st.write(energy_outliers)
    st.subheader("Data Freshness")
    st.write(data_freshness)
    

def display_geographical_overview(df):    
    # Visualization 1 - Geographical Overview
    st.subheader("Geographical Overview")
    
    # Dummy coordinates (replace with accurate ones if needed)
    city_coords = {
        "New York": [40.7128, -74.0060],
        "Chicago": [41.8781, -87.6298],
        "Houston": [29.7604, -95.3698],
        "Phoenix": [33.4484, -112.0740],
        "Seattle": [47.6062, -122.3321]
    }
    
    if df.empty:
        st.warning("No data available for geographical overview.")
        return
    st.caption(f"Data from {df['date'].min()} to {df['date'].max()}")
    
    latest_df = df[df["date"] == df["date"].max()]
    
    latest_df["latitude"] = latest_df["city"].map(lambda x: city_coords.get(x, [0, 0])[0])
    latest_df["longitude"] = latest_df["city"].map(lambda x: city_coords.get(x, [0, 0])[1])
    
    # calculate % change from previous day
    prev_day = df["date"].max() - timedelta(days=1)
    
    prev_day_df = df[df["date"] == prev_day][["city", "energy_consumption"]]
    
    latest_df = latest_df.merge(prev_day_df, on="city", how="left", suffixes=("", "_prev_day"))
    
    latest_df["pct_change"] = ((latest_df["energy_consumption"] - latest_df["energy_consumption_prev_day"]) / latest_df["energy_consumption_prev_day"]) * 100
    
    fig_map = px.scatter_mapbox(
        latest_df,
        lat="latitude",
        lon="longitude",
        size="energy_consumption",
        color="energy_consumption",
        hover_name="city",
        hover_data={"lat": False, "lon": False, "avg_temp": True, "energy_consumption": True, "pct_change": True},
        color_continuous_scale=["green", "yellow", "red"],
        size_max=15,
        zoom=3,
        height=600
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)

# Visulation 2 Time serires analysis

def time_series_analysis(df):
    st.header("📊 Time Series: Temperature and Energy")
    selected_city = st.selectbox("Select City for Time Series", ["All Cities"] + cities )
    
    selected_city = st.selectbox("Select City for Time Series", ["All Cities"] + cities)
    plot_df = df if selected_city == "All Cities" else df[df["city"] == selected_city]
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["avg_temp"], name="Avg Temp (°F)", yaxis="y1", mode="lines+markers", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=df["date"], y=df["energy_consumption"], name="Energy Conm (MWh)", yaxis="y2", mode="lines+markers", line=dict(color="orange")))
    
    # Highlight Weekends
    for date in pd.to_datetime(df["date"]):
        if date.weekday() >= 5:
            fig.add_vrect(
                x0=date - pd.Timedelta(days=1),
                x1=date + pd.Timedelta(days=1),
                fillcolor="lightgray",
                opacity=0.5,
                layer="below",
                line_width=0,
            )
        
    fig.update_layout(
        title=f"Temperature and Energy Consumption in {selected_city} ({df['date'].min()} to {df['date'].max()})",
        xaxis_title="Date",
        yaxis=dict(title="Temperature (°F)", side="left", overlaying="y2"),
        yaxis2=dict(title="Energy Consumption (MWh)", side="right", overlaying="y", anchor="x"),
        legend=dict(x=0, y=1.1, orientation="h"),
        template="plotly_white",
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)
        
        
# Visulation 3 correlation analysis
def correlation_analysis(df):
    st.header("🔍 Correlation Analysis: Temperature vs Energy")
    
    scatter_fig = px.scatter(
        df,
        x="avg_temp",
        y="energy_consumption",
        color="city",
        hover_name="city",
        trendline="ols",
        hover_data=["date"],
    )
    
    scatter_fig.update_layout(
        title="Temperature vs Energy Consumption Correlation",
        xaxis_title="Average Temperature (°F)",
        yaxis_title="Energy Consumption (MWh)",
        template="plotly_white",
        height=600
    )
    
    st.plotly_chart(scatter_fig, use_container_width=True)
    
# Visulation 4 Regression Analysis
def regression_analysis(df):
    st.header("🔍 Regression Analysis: Temperature vs Energy")
    
    scatter_fig = px.scatter(
        df,
        x="avg_temp",
        y="energy_consumption",
        color="city",
        hover_name="city",
        trendline="ols",
        hovar_data=["date"],
    )
    
    scatter_fig.update_layout(
        title="Temperature vs Energy Consumption Correlation",
        xaxis_title="Average Temperature (°F)",
        yaxis_title="Energy Consumption (MWh)",
        template="plotly_white",
        height=600
    )
    st.plotly_chart(scatter_fig, use_container_width=True)
    # Linear Regression Model
    X = df[["avg_temp"]].values.reshape(-1, 1)
    y = df["energy_consumption"].values.reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    r2 = model.score(X, y)
    
    st.write(f"R-squared: {r2}")
    st.write("Linear Regression Coefficients:")
    st.write(f"Intercept: {model.intercept_[0]:.2f}, Slope: {model.coef_[0][0]:.2f}")
    
# visulization 5 - Daily Energy Consumption
def daily_energy_consumption(df):
    st.header("📊 Daily Energy Consumption")
    fig = px.line(df, x="date", y="energy_consumption", color="city", title="Daily Energy Consumption")
    fig.update_layout(template="plotly_white", height=600)
    st.plotly_chart(fig, use_container_width=True)

# visualization 6 - Daily Average Temperature
def daily_avg_temperature(df):    
    st.header("📊 Daily Average Temperature")
    fig = px.line(df, x="date", y="avg_temp", color="city", title="Daily Average Temperature")
    fig.update_layout(template="plotly_white", height=600)
    st.plotly_chart(fig, use_container_width=True)
    
def temp_bin(temp):
    if temp < 32:
        return "Freezing (<50°F)"
    elif 32 <= temp < 50:
        return "Cold (32-50°F)"
    elif 50 <= temp < 70:
        return "Mild (50-70°F)"
    elif 70 <= temp < 85:
        return "Warm (70-85°F)"
    else:
        return "Hot(>85°F)"

#visualization 7 - Usage patterns Heatmap
def usage_patterns_heatmap(df):
    st.header("📊 Usage Patterns Heatmap")
    
    heatmap_city = st.selectbox("Select City for Heatmap", cities)
    heatmap_df = df[df["city"] == heatmap_city].copy()
        
    heatmap_df["temp_range"] = heatmap_df["avg_temp"].apply(temp_bin)
    pivot = heatmap_df.groupby(["temp_range", "day_of_week"])["energy_consumption"].mean().unstack().fillna(0)
    pivot = pivot.reindex(["Freezing (<50°F)", "Cold (32-50°F)", "Mild (50-70°F)", "Warm (70-85°F)", "Hot(>85°F)"]) # # Reorder rows for better visualization
    pivot = pivot.reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], axis=1)  # Reorder columns for better visualization
    
    fig_heatmap = px.imshow(
        pivot,
        text_auto=".1f",
        color_continuous_scale="RdBu_r",
        labels=dict(x="Day of Week", y="Temperature Range", color="Avg Energy"),
        title=f"Average Energy Consumption by Temperature Range and Day of Week in {heatmap_city}",
        height=600   
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    

def main():
    # Main Dashboard Layout
    st.sidebar.title("Dashboard Navigation")

    if st.sidebar.checkbox("Data Quality Checks"):
        if not df.empty:
            st.header("Data Quality Checks")
            missing_summary, temp_outliers, energy_outliers, data_freshness = run_quality_checks(df)
            st.subheader("Missing Values Summary")
            st.write(missing_summary)
            st.subheader("Temperature Outliers")
            st.write(temp_outliers)
            st.subheader("Energy Outliers")
            st.write(energy_outliers)
            st.subheader("Data Freshness")
            st.write(data_freshness)
        else:
            st.warning("No data available for quality checks.")

    if st.sidebar.checkbox("Visualizations"):
        display_geographical_overview(df)
        time_series_analysis(df)
        correlation_analysis(df)
        regression_analysis(df)
        daily_energy_consumption(df)
        daily_avg_temperature(df)
        usage_patterns_heatmap(df)
        
if __name__ == "__main__":
    main()
    
    
        
    
    

    
