import streamlit as st
import pandas as pd

st.title("Data Restructuring by SKU Name")
st.markdown("Upload your Excel file to organize data by SKU Name, Year, and Month.")

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

        # Extract unique SKU names
        unique_skus = data['SKU Name'].unique()
        st.write("Unique SKUs:", unique_skus)

        # Final DataFrame to store results
        final_df = pd.DataFrame(columns=[
            'SKU Name', 'Product Sub Group', 'Year', 'Month',
            'Sum of Actual @AOPNet Trade Sales', 'Sum of Actual @AOPStandard Gross Profit',
            'Sum of Actual @AOPQuantity sold', 'Sum of Actual @AOPNet Weight'
        ])

        for sku in unique_skus:
            sku_data = data[data['SKU Name'] == sku]
            product_sub_group = sku_data['Product Sub Group'].iloc[0] if not sku_data.empty else 'Unknown'
            unique_years = sku_data['Year'].unique()

            for year in unique_years:
                year_data = sku_data[sku_data['Year'] == year]
                for month in range(1, 13):  # Loop through all months
                    month_data = year_data[year_data['Period'] == month]
                    if not month_data.empty:
                        # Sum the required values
                        sum_net_sales = month_data['Actual @AOPNet Trade Sales'].sum()
                        sum_gross_profit = month_data['Actual @AOPStandard Gross Profit'].sum()
                        sum_quantity_sold = month_data['Actual @AOPQuantity sold'].sum()
                        sum_net_weight = month_data['Actual @AOPNet Weight'].sum()

                        # Append the aggregated data to the final DataFrame
                        # Create a temporary DataFrame for the current row
                        row = pd.DataFrame([{
                            'SKU Name': sku,
                            'Product Sub Group': product_sub_group,
                            'Year': year,
                            'Month': month,
                            'Sum of Actual @AOPNet Trade Sales': sum_net_sales,
                            'Sum of Actual @AOPStandard Gross Profit': sum_gross_profit,
                            'Sum of Actual @AOPQuantity sold': sum_quantity_sold,
                            'Sum of Actual @AOPNet Weight': sum_net_weight
                        }])
                        
                        # Concatenate the new row to the final DataFrame
                        final_df = pd.concat([final_df, row], ignore_index=True)


        # Display the final structured data
        st.subheader("Restructured Data by SKU Name")
        st.write(final_df.head(20))

        st.success("Data restructuring completed successfully!")

    except Exception as e:
        st.error(f"Error processing file: {e}")
