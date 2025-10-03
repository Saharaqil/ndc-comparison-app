import pandas as pd
import streamlit as st
import re

# --- Helper function to clean NDCs ---
def clean_ndc(ndc):
    if pd.isna(ndc):
        return None
    ndc = str(ndc)
    ndc = re.sub(r'\D', '', ndc)   # remove non-numeric chars like dashes
    if len(ndc) > 10:
        ndc = ndc[-10:]            # keep last 10 digits if longer
    return ndc.zfill(10)           # pad to 10 digits

# --- Main comparison function ---
def compare_ndc_files(dispense_file, purchase_file):
    # Load CSV files
    dispense_df = pd.read_csv(dispense_file)
    purchase_df = pd.read_csv(purchase_file)

    # Clean column names
    dispense_df.columns = dispense_df.columns.str.strip()
    purchase_df.columns = purchase_df.columns.str.strip()

    # Clean NDC values
    dispense_df["NDC"] = dispense_df["NDC"].apply(clean_ndc)
    purchase_df["NDC"] = purchase_df["NDC"].apply(clean_ndc)

    # Rename columns for clarity
    dispense_df.rename(columns={"Rx Quantity Filled": "Dispensed_Qty", 
                                "Drug Name": "Drug_Name"}, inplace=True)
    purchase_df.rename(columns={"TOTAL": "Purchased_Qty", 
                                "Product Description": "Product_Description"}, inplace=True)

    # Merge both files on NDC
    comparison_df = pd.merge(dispense_df, purchase_df, on="NDC", how="outer")

    # Add Difference column
    comparison_df["Difference"] = comparison_df["Purchased_Qty"].fillna(0) - comparison_df["Dispensed_Qty"].fillna(0)

    return comparison_df

# --- Streamlit UI ---
st.title("💊 NDC Comparison Tool")
st.write("Upload your **Dispense Report** and **Purchase Report** to compare quantities.")

# Upload files
dispense_file = st.file_uploader("Upload Dispense Report (CSV)", type=["csv"])
purchase_file = st.file_uploader("Upload Purchase Report (CSV)", type=["csv"])

if dispense_file and purchase_file:
    # Perform comparison
    comparison_df = compare_ndc_files(dispense_file, purchase_file)

    st.success("✅ Comparison Completed!")

    # Show full DataFrame (scrollable inside app)
    st.dataframe(comparison_df)

    # --- Download Full Excel Report ---
    output_file = "NDC_Comparison_Report.xlsx"
    comparison_df.to_excel(output_file, index=False)

    with open(output_file, "rb") as f:
        st.download_button(
            "⬇️ Download Full Report (Excel)",
            f,
            file_name=output_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
