
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

st.set_page_config(
    page_title="Data Cleaning & Reporting Automation",
    layout="wide"
)

st.title("Data Cleaning & Reporting Automation")
st.write("Automatically clean datasets, analyze data quality and generate reports.")

uploaded_file = st.file_uploader(
    "Upload your CSV or Excel dataset",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    original_df = df.copy()

    st.sidebar.header("Cleaning Options")

    remove_duplicates = st.sidebar.checkbox(
        "Remove duplicate rows",
        value=True
    )

    standardize_columns = st.sidebar.checkbox(
        "Standardize column names",
        value=True
    )

    missing_method = st.sidebar.selectbox(
        "Handle missing values",
        ["Mean / Mode", "Median / Mode", "Drop Missing Rows"]
    )

    cleaned_df = df.copy()

    if standardize_columns:
        cleaned_df.columns = (
            cleaned_df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_", regex=False)
            .str.replace(r"[^a-zA-Z0-9_]", "", regex=True)
        )

    duplicate_count = cleaned_df.duplicated().sum()

    if remove_duplicates:
        cleaned_df = cleaned_df.drop_duplicates()

    missing_before = cleaned_df.isnull().sum().sum()

    if missing_method == "Drop Missing Rows":
        cleaned_df = cleaned_df.dropna()

    else:
        for column in cleaned_df.columns:

            if cleaned_df[column].isnull().sum() > 0:

                if pd.api.types.is_numeric_dtype(cleaned_df[column]):

                    if missing_method == "Mean / Mode":
                        fill_value = cleaned_df[column].mean()
                    else:
                        fill_value = cleaned_df[column].median()

                    cleaned_df[column] = cleaned_df[column].fillna(fill_value)

                else:

                    mode_values = cleaned_df[column].mode()

                    if len(mode_values) > 0:
                        cleaned_df[column] = cleaned_df[column].fillna(
                            mode_values[0]
                        )

                    else:
                        cleaned_df[column] = cleaned_df[column].fillna(
                            "Unknown"
                        )

    missing_after = cleaned_df.isnull().sum().sum()

    st.success("Data cleaning completed successfully!")

    st.header("1. Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Original Rows", len(original_df))
    col2.metric("Cleaned Rows", len(cleaned_df))
    col3.metric("Duplicates Found", int(duplicate_count))
    col4.metric("Missing Values Removed / Filled", int(missing_before))

    st.subheader("Original Dataset")
    st.dataframe(original_df.head(10), width="stretch")

    st.subheader("Cleaned Dataset")
    st.dataframe(cleaned_df.head(10), width="stretch")

    st.header("2. Data Quality Analysis")

    quality_data = pd.DataFrame({
        "Column": original_df.columns,
        "Data Type": original_df.dtypes.astype(str).values,
        "Missing Values": original_df.isnull().sum().values,
        "Missing Percentage": (
            original_df.isnull().mean().values * 100
        ).round(2)
    })

    st.dataframe(quality_data, width="stretch")

    col1, col2 = st.columns(2)

    with col1:
        missing_chart = px.bar(
            quality_data,
            x="Column",
            y="Missing Values",
            title="Missing Values by Column"
        )
        st.plotly_chart(missing_chart, width="stretch")

    with col2:
        duplicate_chart = px.pie(
            names=["Unique Rows", "Duplicate Rows"],
            values=[
                len(original_df) - duplicate_count,
                duplicate_count
            ],
            title="Duplicate Data Analysis"
        )
        st.plotly_chart(duplicate_chart, width="stretch")

    st.header("3. Statistical Summary")

    st.dataframe(
        cleaned_df.describe(include="all").transpose(),
        width="stretch"
    )

    st.header("4. Data Visualization")

    numeric_columns = cleaned_df.select_dtypes(
        include=np.number
    ).columns.tolist()

    categorical_columns = cleaned_df.select_dtypes(
        exclude=np.number
    ).columns.tolist()

    if numeric_columns:

        selected_column = st.selectbox(
            "Select a numerical column",
            numeric_columns
        )

        histogram = px.histogram(
            cleaned_df,
            x=selected_column,
            title=f"Distribution of {selected_column}"
        )

        st.plotly_chart(histogram, width="stretch")

    if categorical_columns:

        selected_category = st.selectbox(
            "Select a categorical column",
            categorical_columns
        )

        category_counts = (
            cleaned_df[selected_category]
            .astype(str)
            .value_counts()
            .head(15)
            .reset_index()
        )

        category_counts.columns = ["Category", "Count"]

        category_chart = px.bar(
            category_counts,
            x="Category",
            y="Count",
            title=f"Top Categories in {selected_category}"
        )

        st.plotly_chart(category_chart, width="stretch")

    st.header("5. Cleaning Summary")

    summary = f"""
DATA CLEANING & REPORTING AUTOMATION

Original Dataset Rows: {len(original_df)}
Original Dataset Columns: {len(original_df.columns)}

Duplicate Rows Detected: {int(duplicate_count)}

Missing Values Before Cleaning: {int(missing_before)}
Missing Values After Cleaning: {int(missing_after)}

Rows After Cleaning: {len(cleaned_df)}
Columns After Cleaning: {len(cleaned_df.columns)}

Missing Value Method: {missing_method}
Duplicate Removal Enabled: {remove_duplicates}
Column Standardization Enabled: {standardize_columns}

Cleaning Status: Completed
"""

    st.text_area(
        "Automated Cleaning Report",
        summary,
        height=250
    )

    st.header("6. Download Your Results")

    csv_data = cleaned_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Cleaned Dataset (CSV)",
        data=csv_data,
        file_name="cleaned_dataset.csv",
        mime="text/csv"
    )

    excel_buffer = BytesIO()

    cleaned_df.to_excel(
        excel_buffer,
        index=False,
        engine="openpyxl"
    )

    st.download_button(
        "Download Cleaned Dataset (Excel)",
        data=excel_buffer.getvalue(),
        file_name="cleaned_dataset.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.download_button(
        "Download Cleaning Report",
        data=summary,
        file_name="data_cleaning_report.txt",
        mime="text/plain"
    )

    st.success("Your automated cleaning and reporting workflow is complete!")

else:

    st.info("Upload a CSV or Excel dataset to get started.")

    st.markdown("""
    ### Features

    - Automatic missing value detection
    - Duplicate row removal
    - Column name standardization
    - Data quality analysis
    - Statistical summary
    - Interactive visualizations
    - Cleaned CSV and Excel downloads
    - Automated cleaning report
    """)
