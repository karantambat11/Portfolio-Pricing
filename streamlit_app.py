import streamlit as st
import pandas as pd

st.title("Data Restructuring for Subcategories")
st.markdown("Upload your Excel file to organize data by subcategories, correctly grouped by Year, Month, and SKU.")

# Step 1: Upload Excel file
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    try:
        # Load Excel file
        excel_data = pd.ExcelFile(uploaded_file)
        sheet_names = excel_data.sheet_names
        selected_sheet = st.selectbox("Select the sheet to analyze", sheet_names)
        data = excel_data.parse(selected_sheet)

        # Standardize column names
        data.columns = data.columns.map(str).str.strip()

        # Extract unique subcategories
        subcategories = data['Product Sub Group'].unique()
        st.write("Unique Subcategories:", subcategories)

        # Dictionary to store aggregated data per subcategory
        aggregated_data = {}

        for subcategory in subcategories:
            subcategory_data = data[data['Product Sub Group'] == subcategory]
            # Group and aggregate by Year, Month, SKU
            grouped = subcategory_data.groupby(['Year', 'Period', 'Material']).agg({
                'Actual @AOPNet Trade Sales': 'sum',
                'Actual @AOPStandard Gross Profit': 'sum',
                'Actual @AOPQuantity sold': 'sum',
                'Actual @AOPNet Weight': 'sum'
            }).reset_index()
            # Rename 'Period' to 'Month'
            grouped = grouped.rename(columns={'Period': 'Month'})
            # Sort by Year, Month, SKU
            grouped = grouped.sort_values(by=['Year', 'Month', 'Material'])
            # Save to dictionary
            aggregated_data[subcategory] = grouped

        # Display the first few rows of each subcategory
        st.subheader("Aggregated Data Preview")
        for subcategory, df in aggregated_data.items():
            st.write(f"Subcategory: {subcategory}")
            st.write(df.head())

        st.success("Data restructuring completed successfully!")

    except Exception as e:
        st.error(f"Error processing file: {e}")
