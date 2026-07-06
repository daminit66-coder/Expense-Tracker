"""
Expense Tracker — Streamlit UI
--------------------------------
A polished Streamlit front-end for the PostgreSQL-backed expense tracker.

Setup:
    pip install streamlit psycopg2-binary python-dotenv pandas plotly

Create a `.env` file next to this script with:
    DB_HOST=your_host
    DB_NAME=your_db
    DB_USER=your_user
    DB_PASSWORD=your_password
    DB_PORT=5432

Run with:
    streamlit run expense_tracker_app.py

Expected table schema (adjust column names in queries below if yours differ):
    CREATE TABLE expense (
        id SERIAL PRIMARY KEY,
        Product_Name TEXT,
        category TEXT,
        price NUMERIC,
        Quantity INTEGER,
        Payment_Method TEXT,
        Buy_From TEXT,
        Purchase_Date DATE
    );
"""

import os
from datetime import date

import pandas as pd
import psycopg2
import streamlit as st
from dotenv import load_dotenv

# ----------------------------------------------------------------------------
# Page config & theming
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .main > div {padding-top: 1.5rem;}
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e6e6e6;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetricLabel"] {font-weight: 600; color: #555;}
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton>button[kind="primary"] {
        background-color: #2E7D32;
        border: none;
    }
    section[data-testid="stSidebar"] {
        border-right: 1px solid #eaeaea;
    }
    h1, h2, h3 {font-weight: 700;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Database connection (cached across reruns)
# ----------------------------------------------------------------------------
load_dotenv()

VALID_COLUMNS = [
    "Product_Name",
    "category",
    "price",
    "Quantity",
    "Payment_Method",
    "Buy_From",
    "Purchase_Date",
]


@st.cache_resource(show_spinner=False)
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
    )


def run_query(query, params=None, fetch=True):
    """Run a query and optionally return rows as a DataFrame."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(query, params)
        if fetch and cur.description:
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return pd.DataFrame(rows, columns=cols)
        conn.commit()
        return None


def fetch_all_expenses():
    return run_query("SELECT * FROM expense ORDER BY 1 DESC")


# ----------------------------------------------------------------------------
# Sidebar navigation
# ----------------------------------------------------------------------------
st.sidebar.title("💰 Expense Tracker")
st.sidebar.caption("Track, analyze, and manage your spending")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "➕ Add Expense", "📋 View Expenses", "✏️ Update", "🗑️ Delete", "📈 Insights"],
    label_visibility="collapsed",
)

st.sidebar.divider()

try:
    _conn_test = get_connection()
    st.sidebar.success("Database connected", icon="✅")
except Exception as e:  # noqa: BLE001
    st.sidebar.error(f"Connection failed: {e}", icon="🚫")
    st.stop()

# ----------------------------------------------------------------------------
# DASHBOARD
# ----------------------------------------------------------------------------
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.caption("A quick snapshot of your spending")

    df = fetch_all_expenses()

    if df.empty:
        st.info("No expenses recorded yet. Add your first one from the sidebar!")
    else:
        df.columns = [c.lower() for c in df.columns]
        df["total"] = df["price"].astype(float) * df["quantity"].astype(float)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Spend", f"₹{df['total'].sum():,.2f}")
        col2.metric("Total Purchases", f"{len(df)}")
        col3.metric("Avg. Price", f"₹{df['price'].astype(float).mean():,.2f}")
        col4.metric("Categories", f"{df['category'].nunique()}")

        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Spend by Category")
            cat_df = df.groupby("category")["total"].sum().reset_index()
            st.bar_chart(cat_df, x="category", y="total", use_container_width=True)
        with c2:
            st.subheader("Spend by Payment Method")
            pay_df = df.groupby("payment_method")["total"].sum().reset_index()
            st.bar_chart(pay_df, x="payment_method", y="total", use_container_width=True)

        st.subheader("Recent Purchases")
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------
# ADD EXPENSE
# ----------------------------------------------------------------------------
elif page == "➕ Add Expense":
    st.title("➕ Add a New Expense")

    with st.form("add_expense_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Product Name")
            category = st.text_input("Category")
            price = st.number_input("Price", min_value=0.0, step=1.0, format="%.2f")
            quantity = st.number_input("Quantity", min_value=1, step=1)
        with c2:
            payment = st.selectbox(
                "Payment Method", ["Gpay", "Cash", "Credit Card", "Debit Card", "UPI", "Other"]
            )
            buy_from = st.text_input("Buy From")
            purchase_date = st.date_input("Purchase Date", value=date.today())

        submitted = st.form_submit_button("Add Expense", type="primary", use_container_width=True)

        if submitted:
            if not name or not category or not buy_from:
                st.warning("Please fill in Product Name, Category, and Buy From.")
            else:
                query = """
                    INSERT INTO expense
                    (Product_Name, category, price, Quantity, Payment_Method, Buy_From, Purchase_Date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    name,
                    category,
                    price,
                    int(quantity),
                    payment,
                    buy_from,
                    purchase_date.strftime("%Y-%m-%d"),
                )
                try:
                    run_query(query, values, fetch=False)
                    st.success(f"'{name}' added successfully!", icon="✅")
                except Exception as e:  # noqa: BLE001
                    get_connection().rollback()
                    st.error(f"Error adding expense: {e}")

# ----------------------------------------------------------------------------
# VIEW EXPENSES
# ----------------------------------------------------------------------------
elif page == "📋 View Expenses":
    st.title("📋 View Expenses")

    tab1, tab2, tab3 = st.tabs(["All Entries", "Search by Product", "Single Column"])

    with tab1:
        df = fetch_all_expenses()
        st.write(f"**{len(df)}** total entries")
        st.dataframe(df, use_container_width=True, hide_index=True)
        if not df.empty:
            st.download_button(
                "⬇️ Download as CSV",
                df.to_csv(index=False).encode("utf-8"),
                "expenses.csv",
                "text/csv",
            )

    with tab2:
        search_name = st.text_input("Enter Product Name to search")
        if st.button("Search", key="search_btn"):
            if search_name:
                df = run_query(
                    "SELECT * FROM expense WHERE Product_Name ILIKE %s",
                    (f"%{search_name}%",),
                )
                if df.empty:
                    st.info("No matching products found.")
                else:
                    st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning("Please enter a product name.")

    with tab3:
        col_choice = st.selectbox("Choose a column to view", VALID_COLUMNS)
        if st.button("Show Column", key="col_btn"):
            df = run_query(f"SELECT {col_choice} FROM expense")
            st.dataframe(df, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------
# UPDATE EXPENSE
# ----------------------------------------------------------------------------
elif page == "✏️ Update":
    st.title("✏️ Update an Expense")

    df = fetch_all_expenses()
    df.columns = [c.lower() for c in df.columns] if not df.empty else df.columns

    if df.empty:
        st.info("No expenses to update yet.")
    else:
        product_names = sorted(df["product_name"].dropna().unique().tolist())
        selected_product = st.selectbox("Select Product Name to update", product_names)

        matching_rows = df[df["product_name"] == selected_product]
        st.dataframe(matching_rows, use_container_width=True, hide_index=True)

        with st.form("update_form"):
            field_to_update = st.selectbox("Field to update", VALID_COLUMNS)
            new_value = st.text_input("New value")
            submitted = st.form_submit_button("Update", type="primary")

            if submitted:
                if not new_value:
                    st.warning("Please enter a new value.")
                else:
                    query = f"UPDATE expense SET {field_to_update} = %s WHERE Product_Name = %s"
                    try:
                        run_query(query, (new_value, selected_product), fetch=False)
                        st.success("Updated successfully!", icon="✅")
                        st.rerun()
                    except Exception as e:  # noqa: BLE001
                        get_connection().rollback()
                        st.error(f"Error updating: {e}")

# ----------------------------------------------------------------------------
# DELETE EXPENSE
# ----------------------------------------------------------------------------
elif page == "🗑️ Delete":
    st.title("🗑️ Delete Expenses")

    tab1, tab2 = st.tabs(["Delete One Product", "Delete All"])

    with tab1:
        df = fetch_all_expenses()
        if df.empty:
            st.info("No expenses to delete.")
        else:
            df.columns = [c.lower() for c in df.columns]
            product_names = sorted(df["product_name"].dropna().unique().tolist())
            product_to_delete = st.selectbox("Select Product Name to delete", product_names)

            st.dataframe(df[df["product_name"] == product_to_delete], use_container_width=True, hide_index=True)

            if st.button("Delete This Product", type="primary"):
                try:
                    run_query("DELETE FROM expense WHERE Product_Name = %s", (product_to_delete,), fetch=False)
                    st.success(f"Deleted '{product_to_delete}' successfully!", icon="✅")
                    st.rerun()
                except Exception as e:  # noqa: BLE001
                    get_connection().rollback()
                    st.error(f"Error deleting: {e}")

    with tab2:
        st.warning("This will permanently delete **all** expense records.")
        confirm = st.checkbox("I understand this action cannot be undone")
        if st.button("Delete All Entries", disabled=not confirm):
            try:
                run_query("TRUNCATE TABLE expense RESTART IDENTITY", fetch=False)
                st.success("All entries deleted successfully!", icon="✅")
                st.rerun()
            except Exception as e:  # noqa: BLE001
                get_connection().rollback()
                st.error(f"Error deleting all entries: {e}")

# ----------------------------------------------------------------------------
# INSIGHTS ("more" from original CLI)
# ----------------------------------------------------------------------------
elif page == "📈 Insights":
    st.title("📈 Insights & Analytics")

    df = fetch_all_expenses()

    if df.empty:
        st.info("No data available yet.")
    else:
        df.columns = [c.lower() for c in df.columns]
        df["price"] = df["price"].astype(float)
        df["quantity"] = df["quantity"].astype(float)
        df["total"] = df["price"] * df["quantity"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Maximum Price", f"₹{df['price'].max():,.2f}")
        c2.metric("Minimum Price", f"₹{df['price'].min():,.2f}")
        c3.metric("Average Price", f"₹{df['price'].mean():,.2f}")
        c4.metric("Total Spend", f"₹{df['total'].sum():,.2f}")

        st.divider()

        st.subheader("Category-wise Total Spending")
        cat_spend = df.groupby("category")["total"].sum().sort_values(ascending=False).reset_index()
        st.bar_chart(cat_spend, x="category", y="total", use_container_width=True)
        st.dataframe(cat_spend, use_container_width=True, hide_index=True)

        st.subheader("Top 5 Most Expensive Purchases")
        top5 = df.sort_values("price", ascending=False).head(5)
        st.dataframe(top5, use_container_width=True, hide_index=True)

        c5, c6 = st.columns(2)
        with c5:
            st.subheader("Sorted — Ascending Price")
            st.dataframe(df.sort_values("price"), use_container_width=True, hide_index=True, height=300)
        with c6:
            st.subheader("Sorted — Descending Price")
            st.dataframe(df.sort_values("price", ascending=False), use_container_width=True, hide_index=True, height=300)

        st.metric("Total Number of Expenses", len(df))