import pandas as pd
import plotly.express as px
import streamlit as st

# --- 1. Streamlit Page Configuration ---
st.set_page_config(
    page_title="Olist Logistics & Financial Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📦 Olist E-Commerce Performance Dashboard")
st.markdown(
    "Analyzing **Delivery Timings**, **Freight Charges**, and **Customer Payments** by State (2016 - 2018)."
)


# --- 2. Data Loading & Pipeline ---
@st.cache_data
def load_and_process_data():
    # Use absolute or relative paths to your files
    base_path = "/home/moswal/m2/M2Project/"
    df_orders = pd.read_csv(f"{base_path}olist_orders_dataset.csv")
    df_customers = pd.read_csv(f"{base_path}olist_customers_dataset.csv")
    df_items = pd.read_csv(f"{base_path}olist_order_items_dataset.csv")
    df_payments = pd.read_csv(f"{base_path}olist_order_payments_dataset.csv")

    # Timestamps & Delivery calculation
    df_orders["order_purchase_timestamp"] = pd.to_datetime(
        df_orders["order_purchase_timestamp"]
    )
    df_orders["order_delivered_customer_date"] = pd.to_datetime(
        df_orders["order_delivered_customer_date"]
    )
    df_orders["delivery_timing_days"] = (
        df_orders["order_delivered_customer_date"]
        - df_orders["order_purchase_timestamp"]
    ).dt.days

    # Year extraction & filtering
    df_orders["year"] = df_orders["order_purchase_timestamp"].dt.year
    df_orders = df_orders[df_orders["year"].isin([2016, 2017, 2018])]

    # Order level grouping
    df_order_freight = (
        df_items.groupby("order_id")["freight_value"].sum().reset_index()
    )
    df_order_payments = (
        df_payments.groupby("order_id")["payment_value"].sum().reset_index()
    )

    # Merges
    df_merged = df_orders.merge(df_customers, on="customer_id", how="inner")
    df_merged = df_merged.merge(df_order_freight, on="order_id", how="left")
    df_merged = df_merged.merge(df_order_payments, on="order_id", how="left")

    # Final Aggregation
    report = (
        df_merged.groupby(["customer_state", "year"])
        .agg(
            avg_delivery_timing_days=("delivery_timing_days", "mean"),
            total_freight_charges=("freight_value", "sum"),
            avg_freight_per_order=("freight_value", "mean"),
            total_customer_paid=("payment_value", "sum"),
            avg_customer_paid_per_order=("payment_value", "mean"),
            total_orders=("order_id", "count"),
        )
        .reset_index()
    )

    # Cleaning up numerical columns
    for col in report.columns:
        if report[col].dtype == "float64":
            report[col] = report[col].round(2)

    return report


# Load the data safely using Streamlit's caching
try:
    final_report = load_and_process_data()
except Exception as e:
    st.error(f"Error loading Olist dataset files: {e}")
    st.stop()

# --- 3. Sidebar Filters ---
st.sidebar.header("🎛️ Filter Options")

# Year multi-select filter
available_years = sorted(final_report["year"].unique())
selected_years = st.sidebar.multiselect(
    "Select Years", options=available_years, default=available_years
)

# State multi-select filter
available_states = sorted(final_report["customer_state"].unique())
selected_states = st.sidebar.multiselect(
    "Select States", options=available_states, default=["SP", "RJ", "MG", "BA", "RS"]
)

# Filtering dataset based on selection
df_filtered = final_report[
    (final_report["year"].isin(selected_years))
    & (final_report["customer_state"].isin(selected_states))
]

if df_filtered.empty:
    st.warning("No data matches your selection criteria. Please adjust your filters.")
    st.stop()

# --- 4. Main Dashboard KPIs ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="Total Orders in Selection",
        value=f"{int(df_filtered['total_orders'].sum()):,}",
    )
with col2:
    st.metric(
        label="Total Freight Charges",
        value=f"${df_filtered['total_freight_charges'].sum():,.2f}",
    )
with col3:
    st.metric(
        label="Total Revenue (Customer Paid)",
        value=f"${df_filtered['total_customer_paid'].sum():,.2f}",
    )

st.write("---")

# --- 5. Data Visualizations ---
tab1, tab2, tab3 = st.tabs(
    ["🚚 Delivery Timings", "💰 Freight vs Payments", "📊 Raw Summary Data"]
)

with tab1:
    st.subheader("Average Delivery Days by State and Year")
    # Grouped bar chart tracking delivery times across years
    fig_delivery = px.bar(
        df_filtered,
        x="customer_state",
        y="avg_delivery_timing_days",
        color="year",
        barmode="group",
        labels={
            "customer_state": "Customer State",
            "avg_delivery_timing_days": "Avg Delivery Time (Days)",
            "year": "Year",
        },
        title="Delivery Speed Breakdown",
        color_continuous_scale=px.colors.sequential.Viridis,
    )
    fig_delivery.update_layout(xaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_delivery, use_container_width=True)

with tab2:
    st.subheader("Financial Breakdown: Freight Costs vs Total Payment Received")
    # Scatter plot checking if higher freight correlates to higher user out-of-pocket costs
    fig_financial = px.scatter(
        df_filtered,
        x="avg_freight_per_order",
        y="avg_customer_paid_per_order",
        size="total_orders",
        color="customer_state",
        hover_name="year",
        labels={
            "avg_freight_per_order": "Average Freight per Order ($)",
            "avg_customer_paid_per_order": "Average Paid per Order ($)",
            "customer_state": "State",
        },
        title="Order Economics by State (Size = Order Volume)",
    )
    st.plotly_chart(fig_financial, use_container_width=True)

with tab3:
    st.subheader("Processed Matrix Slice")
    # Streamlit interactive data frame display
    st.dataframe(df_filtered, use_container_width=True)