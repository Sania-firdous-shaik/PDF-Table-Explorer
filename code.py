import streamlit as st
import pdfplumber
import pandas as pd
import plotly.express as px

from io import BytesIO

st.set_page_config(page_title="PDF Table Extractor & Visualizer", layout="wide")
st.title("📊 PDF Table Extractor & Visualizer")

uploaded_file = st.file_uploader("Upload a PDF file with tables", type=["pdf"])

if uploaded_file:
    tables = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            extracted_tables = page.extract_tables()
            for table_num, table in enumerate(extracted_tables):
                df = pd.DataFrame(table[1:], columns=table[0])
                df.dropna(how="all", inplace=True)
                if not df.empty:
                    tables.append({
                        "page": page_num + 1,
                        "table_num": table_num + 1,
                        "data": df
                    })

    if tables:
        st.success(f"✅ Found {len(tables)} table(s) in the PDF.")
        table_choice = st.selectbox(
            "Select a table to view and analyze",
            [f"Page {t['page']} - Table {t['table_num']}" for t in tables]
        )

        selected_table = tables[
            [f"Page {t['page']} - Table {t['table_num']}" for t in tables].index(table_choice)
        ]["data"]

        st.subheader("📄 Extracted Table")
        st.dataframe(selected_table, use_container_width=True)

        st.subheader("📈 Visualize Table Data")

        if selected_table.shape[1] >= 2:
            numeric_cols = selected_table.select_dtypes(include=['float64', 'int64']).columns.tolist()
            if not numeric_cols:
                for col in selected_table.columns:
                    selected_table[col] = pd.to_numeric(
                        selected_table[col].str.replace(',', '').str.replace('$', ''),
                        errors='coerce'
                    )
                numeric_cols = selected_table.select_dtypes(include=['float64', 'int64']).columns.tolist()

            if numeric_cols:
                x_axis = st.selectbox("Select X-axis", selected_table.columns)
                y_axis = st.selectbox("Select Y-axis", numeric_cols)
                chart_type = st.radio("Chart Type", ["Bar", "Line", "Pie"], horizontal=True)

                if chart_type == "Bar":
                    fig = px.bar(selected_table, x=x_axis, y=y_axis)
                    st.plotly_chart(fig, use_container_width=True)
                elif chart_type == "Line":
                    fig = px.line(selected_table, x=x_axis, y=y_axis)
                    st.plotly_chart(fig, use_container_width=True)
                elif chart_type == "Pie":
                    fig = px.pie(selected_table, names=x_axis, values=y_axis)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ No numeric data found for visualization.")
        else:
            st.warning("⚠️ Table must have at least 2 columns for visualization.")
    else:
        st.error("❌ No tables found in the PDF.")
