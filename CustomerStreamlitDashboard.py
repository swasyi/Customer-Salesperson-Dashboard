# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from io import BytesIO
#
# # ---------------- Page Config ----------------
# st.set_page_config(page_title="Customer Dashboard", layout="wide")
# st.title("📊 Customer & Salesperson Dashboard")
#
# # ---------------- Upload File ----------------
# uploaded_file = st.file_uploader("📂 Upload your Customer Excel file", type=["xlsx"])
#
# if uploaded_file:
#     # Load data
#     df = pd.read_excel(uploaded_file)
#     df_clean = df.dropna(subset=["Customer_Name", "Sales_person"])
#
#     st.subheader("🔎 Data Preview")
#     st.dataframe(df.head())
#
#     # ---------------- Search & Filter Feature ----------------
#     st.subheader("🔍 Search & Filter Customers")
#     search_name = st.text_input("Enter customer name")
#
#     top_n_option = st.selectbox("Show Top / Least N Customers by Salesperson Count",
#                                 ["Top 10", "Top 5", "Top 20", "Least 5", "Least 10"], index=0)
#
#     n = int(top_n_option.split()[1])
#     if "Least" in top_n_option:
#         top_customers = df_clean["Sales_person"].value_counts().tail(n)
#     else:
#         top_customers = df_clean["Sales_person"].value_counts().head(n)
#
#     if search_name:
#         result = df[df["Customer_Name"].str.contains(search_name, case=False, na=False)]
#         if result.empty:
#             st.warning("❌ No customer found")
#         else:
#             st.success(f"✅ Found {len(result)} result(s)")
#             st.dataframe(result[["Customer_Name", "Sales_person", "State"]])
#
#     # ---------------- Analysis ----------------
#     st.subheader("📈 Analysis")
#     salesperson_counts = df_clean["Sales_person"].value_counts()
#     state_counts = df["State"].value_counts().head(10)
#     unassigned_customers = df[df["Sales_person"].isna()]["Customer_Name"]
#
#     col1, col2 = st.columns(2)
#
#     # ---------------- Bar Chart: Customers per Salesperson ----------------
#     with col1:
#         st.markdown("### Customers per Salesperson")
#         fig, ax = plt.subplots(figsize=(6, 4))  # smaller figure
#         sns.barplot(x=salesperson_counts.index, y=salesperson_counts.values, ax=ax, palette="viridis")
#         plt.xticks(rotation=45, ha="right")
#
#         # Display exact values on top of bars
#         for i, v in enumerate(salesperson_counts.values):
#             ax.text(i, v + 0.5, str(v), ha='center', fontsize=9)
#         st.pyplot(fig)
#
#     # ---------------- Pie Chart: Customer Share ----------------
#     with col2:
#         st.markdown("### Customer Share by Salesperson")
#         fig, ax = plt.subplots(figsize=(4, 4))  # smaller figure
#         ax.pie(salesperson_counts, labels=salesperson_counts.index, autopct="%1.1f%%",
#                startangle=140, textprops={'fontsize': 9})
#         ax.axis('equal')  # equal aspect ratio ensures pie is circle
#         st.pyplot(fig)
#
#     # ---------------- Top 5 Salespeople ----------------
#     st.markdown("### 🏆 Top 5 Salespeople")
#     top_5 = salesperson_counts.head(5)
#     fig, ax = plt.subplots(figsize=(5, 3))
#     sns.barplot(x=top_5.index, y=top_5.values, palette="plasma", ax=ax)
#     for i, v in enumerate(top_5.values):
#         ax.text(i, v + 0.5, str(v), ha='center', fontsize=9)
#     st.pyplot(fig)
#
#     # ---------------- State-wise Distribution ----------------
#     st.markdown("### 🌍 Top 10 States by Customers")
#     fig, ax = plt.subplots(figsize=(8, 4))
#     sns.barplot(x=state_counts.index, y=state_counts.values, palette="cubehelix", ax=ax)
#     plt.xticks(rotation=45, ha="right")
#     for i, v in enumerate(state_counts.values):
#         ax.text(i, v + 0.5, str(v), ha='center', fontsize=9)
#     st.pyplot(fig)
#
#     # ---------------- Unassigned Customers ----------------
#     if not unassigned_customers.empty:
#         st.markdown("### ⚠️ Customers without Salesperson Assigned")
#         st.write(f"Total: {len(unassigned_customers)}")
#         st.dataframe(unassigned_customers)
#
#     # ---------------- Download Button ----------------
#     st.subheader("💾 Download Cleaned Data")
#     to_download = BytesIO()
#     df_clean.to_excel(to_download, index=False, sheet_name="Customers")
#     to_download.seek(0)
#
#     st.download_button(
#         label="⬇️ Download Excel",
#         data=to_download,
#         file_name="cleaned_customer_data.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )




import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
from io import BytesIO

# ---------------- Page Config ----------------
st.set_page_config(page_title="Customer Dashboard", layout="wide")
st.title("📊Customer & Salesperson Dashboard")

# ---------------- File Upload ----------------
uploaded_file = st.file_uploader("📂 Upload your Customer Excel file", type=["xlsx"])

if uploaded_file:
    # Load data
    df = pd.read_excel(uploaded_file)
    df_clean = df.dropna(subset=["Customer_Name", "Sales_person"])

    # ---------------- KPI Metrics ----------------
    unassigned_customers = df[df["Sales_person"].isna()]["Customer_Name"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", df_clean["Customer_Name"].nunique())
    col2.metric("Total Salespersons", df_clean["Sales_person"].nunique())
    col3.metric("Unassigned Customers", len(unassigned_customers))
    top_state = df["State"].value_counts().idxmax() if "State" in df.columns else "N/A"
    col4.metric("Top State", top_state)

    # ---------------- Tabs ----------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📋 Data", "📈 Charts", "⚠️ Unassigned", "💾 Download", "🗺️ Map"]
    )

    # ---------------- Tab 1: Data & Filters ----------------
    with tab1:
        st.subheader("🔍 Search & Filter Customers")
        salespersons = df_clean["Sales_person"].unique().tolist()
        states = df_clean["State"].dropna().unique().tolist() if "State" in df_clean.columns else []

        selected_salespersons = st.multiselect("Select Salesperson(s)", options=salespersons, default=salespersons)
        selected_states = st.multiselect("Select State(s)", options=states, default=states)
        search_name = st.text_input("Search Customer Name")

        filtered_df = df_clean[
            df_clean["Sales_person"].isin(selected_salespersons) &
            (df_clean["State"].isin(selected_states) if states else True)
        ]

        if search_name:
            filtered_df = filtered_df[filtered_df["Customer_Name"].str.contains(search_name, case=False, na=False)]

        st.dataframe(filtered_df)

    # ---------------- Tab 2: Charts ----------------
    with tab2:
        st.subheader("📊 Data Visualizations")

        # Salesperson counts
        salesperson_counts = filtered_df["Sales_person"].value_counts().reset_index()
        salesperson_counts.columns = ["Sales_person", "count"]

        # State counts
        if "State" in filtered_df.columns:
            state_counts = filtered_df["State"].value_counts().reset_index().head(10)
            state_counts.columns = ["State", "count"]
        else:
            state_counts = pd.DataFrame(columns=["State", "count"])

        # Customers per Salesperson
        fig_bar = px.bar(
            salesperson_counts,
            x="Sales_person",
            y="count",
            text="count",
            title="Customers per Salesperson",
            color="Sales_person"
        )
        fig_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_bar, use_container_width=True)

        # Pie Chart
        fig_pie = px.pie(
            salesperson_counts,
            values="count",
            names="Sales_person",
            hole=0.3,
            title="Customer Share by Salesperson"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # Top 5 Salespersons
        top_sales = salesperson_counts.head(5)
        fig_top = px.bar(
            top_sales,
            x="Sales_person",
            y="count",
            color="Sales_person",
            text="count",
            title="Top 5 Salespersons"
        )
        fig_top.update_traces(textposition="outside")
        st.plotly_chart(fig_top, use_container_width=True)

        # Top 10 States
        if not state_counts.empty:
            fig_state = px.bar(
                state_counts,
                x="State",
                y="count",
                text="count",
                title="Top 10 States by Customers",
                color="State"
            )
            fig_state.update_traces(textposition="outside")
            st.plotly_chart(fig_state, use_container_width=True)

        # AI-style insights
        if not salesperson_counts.empty:
            st.write(f"🏆 Top Salesperson: **{salesperson_counts.iloc[0]['Sales_person']}** with {salesperson_counts.iloc[0]['count']} customers.")
        if not state_counts.empty:
            st.write(f"🌍 Top State: **{state_counts.iloc[0]['State']}** with {state_counts.iloc[0]['count']} customers.")

    # ---------------- Tab 3: Unassigned Customers ----------------
    with tab3:
        st.subheader("⚠️ Customers without Salesperson")
        if not unassigned_customers.empty:
            st.write(f"Total: {len(unassigned_customers)}")
            st.dataframe(unassigned_customers)
        else:
            st.success("All customers are assigned!")

    # ---------------- Tab 4: Download ----------------
    with tab4:
        st.subheader("💾 Download Cleaned Data")
        to_download = BytesIO()
        df_clean.to_excel(to_download, index=False, sheet_name="Customers")
        to_download.seek(0)

        st.download_button(
            label="⬇️ Download Excel",
            data=to_download,
            file_name="cleaned_customer_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        csv_data = df_clean.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name="cleaned_customer_data.csv",
            mime="text/csv"
        )

    # ---------------- Tab 5: Map ----------------
    with tab5:
        st.subheader("🗺️ Customer Distribution Map")

        # Dummy coordinates (can be replaced with real lat/lon mapping)
        state_coords = {
            "Maharashtra": [19.7515, 75.7139],
            "Delhi": [28.7041, 77.1025],
            "Karnataka": [15.3173, 75.7139],
            "Gujarat": [22.2587, 71.1924],
            "Tamil Nadu": [11.1271, 78.6569],
            "Uttar Pradesh": [26.8467, 80.9462],
            "West Bengal": [22.9868, 87.8550],
            "Madhya Pradesh": [23.4733, 77.9470],
            "Rajasthan": [27.0238, 74.2179],
            "Andhra Pradesh": [15.9129, 79.7400],
        }

        if "State" in df_clean.columns:
            df_map = df_clean.groupby("State")["Customer_Name"].count().reset_index()
            df_map.columns = ["State", "Customer_Count"]
            df_map["lat"] = df_map["State"].map(lambda x: state_coords.get(x, [0, 0])[0])
            df_map["lon"] = df_map["State"].map(lambda x: state_coords.get(x, [0, 0])[1])

            map_layer = pdk.Layer(
                "ScatterplotLayer",
                data=df_map,
                get_position='[lon, lat]',
                get_fill_color='[255, 0, 0, 160]',
                get_radius="Customer_Count*5000",
                pickable=True,
                auto_highlight=True
            )

            view_state = pdk.ViewState(latitude=20, longitude=78, zoom=4, pitch=0)
            st.pydeck_chart(pdk.Deck(layers=[map_layer], initial_view_state=view_state,
                                     tooltip={"text": "{State}\nCustomers: {Customer_Count}"}))
        else:
            st.warning("No 'State' column found in the data.")
