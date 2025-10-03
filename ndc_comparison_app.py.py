import pandas as pd
import streamlit as st
import re

# --- Helper: clean NDC ---
def clean_ndc(ndc):
    if pd.isna(ndc):
        return None
    ndc = str(ndc)
    ndc = re.sub(r'\D', '', ndc)   # remove non-numeric
    if len(ndc) > 10:
        ndc = ndc[-10:]            # keep last 10 digits if longer
    return ndc.zfill(10)

# --- Comparison function ---
def compare_ndc_files(dispense_file, purchase_file):
    # Load CSVs
    dispense_df = pd.read_csv(dispense_file)
    purchase_df = pd.read_csv(purchase_file)

    # Clean columns
    dispense_df.columns = dispense_df.columns.str.strip()
    purchase_df.columns = purchase_df.columns.str.strip()

    # Clean NDCs
    dispense_df["NDC"] = dispense_df["NDC"].apply(clean_ndc)
    purchase_df["NDC"] = purchase_df["NDC"].apply(clean_ndc)

    # Rename
    dispense_df.rename(columns={"Rx Quantity Filled": "Dispensed_Qty", "Drug Name": "Drug_Name"}, inplace=True)
    purchase_df.rename(columns={"TOTAL": "Purchased_Qty", "Product Description": "Product_Description"}, inplace=True)

    # Merge
    comparison_df = pd.merge(dispense_df, purchase_df, on="NDC", how="outer")

    # Difference
    comparison_df["Difference"] = comparison_df["Purchased_Qty"].fillna(0) - comparison_df["Dispensed_Qty"].fillna(0)

    return comparison_df

# --- Streamlit UI ---
st.title("💊 NDC Comparison Tool")
st.write("Upload your **Dispense Report** and **Purchase Report** to compare quantities.")

dispense_file = st.file_uploader("Upload Dispense Report (CSV)", type=["csv"])
purchase_file = st.file_uploader("Upload Purchase Report (CSV)", type=["csv"])

if dispense_file and purchase_file:
    comparison_df = compare_ndc_files(dispense_file, purchase_file)

    st.success("✅ Comparison Completed!")
    st.dataframe(comparison_df.head(20))

    # Download Excel
    output_file = "NDC_Comparison_Report.xlsx"
    comparison_df.to_excel(output_file, index=False)
    with open(output_file, "rb") as f:
        st.download_button("⬇️ Download Full Report", f, file_name=output_file)
