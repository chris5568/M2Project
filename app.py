import streamlit as st
import duckdb
import pandas as pd

# Set up the dashboard page styling
st.set_page_config(page_title="Olist Customer Insights", page_icon="📊", layout="wide")

st.title("📊 Olist Customers Dashboard")
st.markdown("An interactive visualization of the Olist e-commerce customer dataset using DuckDB and Pandas.")

# --- STEP 1: Data Loading (Cached for performance) ---
@st.cache_data
def load_customer_data():
    # Connect to your persistent database file
    con = duckdb.connect(database='Module2projectdb.duckdb')
    
    # Fetch the required columns for analysis
    query = "SELECT customer_id, customer_unique_id, customer_state, customer_city FROM customers_dataset"
    df = con.execute(query).df()
    
    con.close()
    return df

# Display a clean loading message while data fetches
with st.spinner("Fetching data from Module2projectdb.duckdb..."):
    df = load_customer_data()


# --- STEP 2: KPI Metrics Section ---
st.subheader("Key Performance Indicators")
col1, col2, col3 = st.columns(3)

total_rows = len(df)
# Unique calculation using your variable logic
unique_customers = df['customer_unique_id'].nunique()
repeat_customers = total_rows - unique_customers

with col1:
    st.metric(label="Total Orders/Rows", value=f"{total_rows:,}")
with col2:
    st.metric(label="Unique Customers", value=f"{unique_customers:,}")
with col3:
    st.metric(label="Repeat Orders/Customers", value=f"{repeat_customers:,}", delta="- Accounts for loyalty")


# --- STEP 3: Visualizations ---
st.write("---")
st.subheader("Geographic Distribution of Unique Customers")

# Aggregate unique customers by state for plotting
state_data = df.groupby('customer_state')['customer_unique_id'].nunique().reset_index()
state_data.columns = ['State', 'Unique Customers Count']
state_data = state_data.sort_values(by='Unique Customers Count', ascending=False)

# Split screen into interactive Dataframe view and a visual chart
view_col1, view_col2 = st.columns([1, 2])

with view_col1:
    st.write("### Raw State Breakdown")
    st.dataframe(state_data, use_container_width=True, hide_index=True)

with view_col2:
    st.write("### Visual Chart (Top States)")
    # Render an interactive native bar chart
    st.bar_chart(
        data=state_data, 
        x='State', 
        y='Unique Customers Count', 
        color="#29b5e8", 
        use_container_width=True
    )


# --- STEP 4: Data Explorer ---
st.write("---")
with st.expander("🔍 View Raw Sample Dataset"):
    st.write("Showing the first 100 entries:")
    st.dataframe(df.head(100), use_container_width=True)