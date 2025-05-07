import streamlit as st
import pandas as pd
import altair as alt

st.title("Sales and Profitability Analysis")
st.markdown("This app helps in analyzing SKU-level performance with focus on pricing and profitability.")

# Step 1: Upload Excel file
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    try:
        # Load Excel file
        excel_data = pd.ExcelFile(uploaded_file)
        sheet_names = excel_data.sheet_names
        selected_sheet = st.selectbox("Select the sheet to analyze", sheet_names)
        data = excel_data.parse(selected_sheet)

        # Display the raw data
        st.subheader("Raw Data Preview")
        st.write(data.head())

        # Data Cleaning and Calculation
        data = data.dropna(subset=['Actual @AOPNet Trade Sales', 'Actual @AOPQuantity sold'])
        data = data[data['Actual @AOPQuantity sold'] > 0]
        data['Period'] = data['Period'].astype(str).str.zfill(2)
        data['Date'] = pd.to_datetime(data['Year'].astype(str) + '-' + data['Period'] + '-01')
        data['Average Price'] = data['Actual @AOPNet Trade Sales'] / data['Actual @AOPQuantity sold']
        data['Gross Margin (%)'] = (data['Actual @AOPStandard Gross Profit'] / data['Actual @AOPNet Trade Sales']) * 100

        # Display processed data
        st.subheader("Processed Data with Key Metrics")
        st.write(data.head())

        # Data Exploration
        subcategory = st.selectbox("Select Product Sub Group", data['Product Sub Group'].unique())
        filtered_data = data[data['Product Sub Group'] == subcategory]

        # Time Series Plot
        st.subheader("Time-Series Trends for Selected Sub Group")
        chart = alt.Chart(filtered_data).mark_line(point=True).encode(x='Date', y=alt.Y('Average Price', title='Average Price'), color=alt.value('blue')).properties(title=f'Average Price Trend for {subcategory}')
st.altair_chart(chart, use_container_width=True)

chart_gm = alt.Chart(filtered_data).mark_line(point=True).encode(x='Date', y=alt.Y('Gross Margin (%)', title='Gross Margin (%)'), color=alt.value('red')).properties(title=f'Gross Margin Trend for {subcategory}')
st.altair_chart(chart_gm, use_container_width=True)

        # Top and Bottom SKUs
        st.subheader("Top and Bottom SKUs by Gross Margin")
        top_skus = filtered_data.nlargest(5, 'Gross Margin (%)')
        bottom_skus = filtered_data.nsmallest(5, 'Gross Margin (%)')
        st.write("Top 5 SKUs:")
        st.write(top_skus[['Material', 'Description', 'Average Price', 'Gross Margin (%)']])
        st.write("Bottom 5 SKUs:")
        st.write(bottom_skus[['Material', 'Description', 'Average Price', 'Gross Margin (%)']])

    except Exception as e:
        st.error(f"Error processing file: {e}")
