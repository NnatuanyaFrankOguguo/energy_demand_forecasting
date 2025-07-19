
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure the loggerInfo module is accessible
from common.loggerInfo import get_logger
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from quality.check_missing import check_missing_values
from quality.check_outliers import check_temperature_outliers, check_energy_outliers
from quality.check_freshness import check_data_freshness
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
df["date"] = pd.to_datetime(df["date"])

# Sidebar Filters
st.sidebar.header("Filters Options")
selected_city = st.sidebar.multiselect("Select Cities", cities, default=cities)

# selected_data_type = st.sidebar.selectbox("Select Data Type", options=["All", "Temperature", "Energy"]) if not df.empty else "All"
if not df.empty:
    min_date = df["date"].min().to_pydatetime()
    max_date = df["date"].max().to_pydatetime()

    # Default value is latest 30 days
    default_start = max_date - pd.Timedelta(days=30)

    selected_date_range = st.sidebar.slider(
        "Select Date Range (30-60 Days)", 
        min_value=min_date,
        max_value=max_date,
        value=(default_start, max_date)
    )
else:
    selected_date_range = (None, None)

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
    # If negative energy values are invalid for your map, filter them out:
    latest_df["bubble_size"] = latest_df["energy_consumption"].abs()
    
    fig_map = px.scatter_map(
        latest_df,
        lat="latitude",
        lon="longitude",
        size="bubble_size",
        color="energy_consumption",
        hover_name="city",
        hover_data={
            "latitude": False,
            "longitude": False,
            "avg_temp": True,
            "energy_consumption": True,
            "pct_change": True
        },
        color_continuous_scale=["green", "yellow", "red"],
        size_max=15,
        zoom=3,
        height=600,
        width=1200   # 👈 add this line
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map,  key="geographical_overview_map")

# Visulation 2 Time serires analysis

def time_series_analysis(df):
    st.header("📊 Time Series: Temperature and Energy")
    
    selected_city = st.selectbox(
        "Select City for Time Series",
        ["All Cities"] + cities,
        key="time_series_city_select"
    )
    plot_df = df if selected_city == "All Cities" else df[df["city"] == selected_city]
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot_df["date"], y=plot_df["avg_temp"], name="Avg Temp (°F)", yaxis="y1", mode="lines+markers", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=plot_df["date"], y=plot_df["energy_consumption"], name="Energy Conm (MWh)", yaxis="y2", mode="lines+markers", line=dict(color="orange")))
    
    # Highlight Weekends
    for date in pd.to_datetime(plot_df["date"]):
        if date.weekday() >= 5:
            fig.add_vrect(
                x0=date - pd.Timedelta(days=1),
                x1=date + pd.Timedelta(days=1),
                fillcolor="yellow",
                opacity=0.3,
                layer="below",
                line_width=0,
            )
        
    fig.update_layout(
        title=f"Temperature and Energy Consumption in {selected_city} ({plot_df['date'].min()} to {plot_df['date'].max()})",
        xaxis_title="Date",
        yaxis=dict(title="Temperature (°F)", side="left", overlaying="y2"),
        yaxis2=dict(title="Energy Consumption (MWh)", side="right", overlaying="y", anchor="x"),
        legend=dict(x=0, y=1.1, orientation="h"),
        template="plotly_white",
        height=600,
        width=1200  # 👈 add this line
    )
    print(plot_df["avg_temp"].describe())
    st.plotly_chart(fig,  key="time_series_chart")
        
        
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
        height=600,
        width=1200  # 👈 add this line
    )
    
    st.plotly_chart(scatter_fig, key="correlation_chart")
    
# Visulation 4 Regression Analysis
def regression_analysis(df):
    import numpy as np
    from sklearn.linear_model import LinearRegression
    import plotly.express as px
    import streamlit as st

    # Validate and clean data
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=["avg_temp", "energy_consumption"])

    # Prepare features and target
    X = df[["avg_temp"]]
    y = df["energy_consumption"]

    # Fit linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict energy consumption
    df["predicted_energy"] = model.predict(X)

    # Rename columns for visualization if needed
    df = df.rename(columns={
        "avg_temp": "Temperature",
        "energy_consumption": "Energy Consumption"
    })

    # Create scatter plot with regression line
    scatter_fig = px.scatter(
        df,
        x="Temperature",
        y="Energy Consumption",
        title="Temperature vs Energy Consumption with Regression Line",
        hover_data=["date"]
    )

    scatter_fig.add_traces(px.line(
        df.sort_values(by="Temperature"),
        x="Temperature",
        y="predicted_energy"
    ).data)

    # Display plot in Streamlit
    st.plotly_chart(scatter_fig, use_container_width=True, key="regression_scatter")
    
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
    
# Helper function to categorize temperatures into bins
def temp_bin(temp):
    if temp < 32:
        return "Freezing (<32°F)"
    elif 32 <= temp < 50:
        return "Cold (32–50°F)"
    elif 50 <= temp < 70:
        return "Mild (50–70°F)"
    elif 70 <= temp < 85:
        return "Warm (70–85°F)"
    else:
        return "Hot (>85°F)"

# Visualization 7 - Usage Patterns Heatmap
def usage_patterns_heatmap(df):
    st.header("📊 Usage Patterns Heatmap")

    # Ensure cities list is derived from the data
    cities = sorted(df["city"].dropna().unique())
    selected_city = st.selectbox("Select a City", cities)

    # Filter the dataframe for the selected city
    city_df = df[df["city"] == selected_city].copy()

    # Categorize temperatures
    city_df["temp_range"] = city_df["avg_temp"].apply(temp_bin)

    # Create a pivot table: average energy consumption by temp range and day of week
    pivot_table = (
        city_df.groupby(["temp_range", "day_of_week"])["energy_consumption"]
        .mean()
        .unstack()
        .fillna(0)
    )

    # Ensure logical order of temperature bins and days of the week
    temp_order = ["Freezing (<32°F)", "Cold (32–50°F)", "Mild (50–70°F)", "Warm (70–85°F)", "Hot (>85°F)"]
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot_table = pivot_table.reindex(temp_order)
    pivot_table = pivot_table.reindex(columns=day_order)

    # Plot heatmap
    fig = px.imshow(
        pivot_table,
        text_auto=".1f",
        color_continuous_scale="RdBu_r",
        labels={"x": "Day of Week", "y": "Temperature Range", "color": "Avg Energy (kWh)"},
        title=f"Average Energy Consumption in {selected_city} by Temperature and Day of Week",
        height=600
    )

    # Display heatmap in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    

def main():
    # Main Dashboard Layout
    st.sidebar.title("Dashboard Navigation")

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
    
    
        
    
    

    
