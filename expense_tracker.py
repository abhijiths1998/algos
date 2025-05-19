import streamlit as st
import pandas as pd
import plotly.express as px

# --- Basic Setup ---
st.title("Personal Finance Tracker")
st.sidebar.header("Navigation")

# --- Data Storage (Simple - In-memory for this example) ---
if 'transactions' not in st.session_state:
    st.session_state['transactions'] = pd.DataFrame({
        'Date': [],
        'Category': [],
        'Description': [],
        'Amount': [],
        'Type': []  # 'Income' or 'Expense'
    })

# --- Helper Functions ---
def add_transaction(date, category, description, amount, type):
    new_transaction = pd.DataFrame({
        'Date': [date],
        'Category': [category],
        'Description': [description],
        'Amount': [amount],
        'Type': [type]
    })
    st.session_state['transactions'] = pd.concat([st.session_state['transactions'], new_transaction], ignore_index=True)
    st.session_state['transactions']['Amount'] = pd.to_numeric(st.session_state['transactions']['Amount'], errors='coerce')
    st.session_state['transactions']['Date'] = pd.to_datetime(st.session_state['transactions']['Date'], errors='coerce')

def calculate_balances():
    income = st.session_state['transactions'][st.session_state['transactions']['Type'] == 'Income']['Amount'].sum()
    expense = st.session_state['transactions'][st.session_state['transactions']['Type'] == 'Expense']['Amount'].sum()
    balance = income - expense
    return income, expense, balance

# --- Navigation Menu ---
page = st.sidebar.radio("Go to", ("Dashboard", "Add Transaction", "View Transactions", "Budgeting", "Reports"))

# --- Dashboard Page ---
if page == "Dashboard":
    st.subheader("Overview")
    income, expense, balance = calculate_balances()
    st.metric("Current Balance", f"₹ {balance:,.2f}")
    col1, col2 = st.columns(2)
    col1.metric("Total Income", f"₹ {income:,.2f}")
    col2.metric("Total Expenses", f"₹ {expense:,.2f}")

    if not st.session_state['transactions'].empty:
        # Spending by Category Pie Chart
        expenses = st.session_state['transactions'][st.session_state['transactions']['Type'] == 'Expense']
        if not expenses.empty:
            spending_by_category = expenses.groupby('Category')['Amount'].sum().reset_index()
            fig_pie = px.pie(spending_by_category, names='Category', values='Amount', title='Spending by Category')
            st.plotly_chart(fig_pie)
        else:
            st.info("No expense data available to display spending by category.")

        # Income vs Expense Line Chart over Time
        monthly_data = st.session_state['transactions'].groupby([pd.Grouper(key='Date', freq='M'), 'Type'])['Amount'].sum().unstack(fill_value=0)
        if not monthly_data.empty:
            fig_line = px.line(monthly_data, title='Income vs Expenses Over Time')
            st.plotly_chart(fig_line)
        else:
            st.info("Not enough data to display income vs expenses over time.")
    else:
        st.info("No transaction data available. Add transactions to see insights.")

# --- Add Transaction Page ---
elif page == "Add Transaction":
    st.subheader("Add New Transaction")
    with st.form("add_transaction_form"):
        date = st.date_input("Date")
        type = st.selectbox("Type", ["Income", "Expense"])
        category = st.text_input("Category")
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.01)
        submitted = st.form_submit_button("Add Transaction")
        if submitted:
            add_transaction(date, category, description, amount, type)
            st.success("Transaction added successfully!")

# --- View Transactions Page ---
elif page == "View Transactions":
    st.subheader("View All Transactions")
    if not st.session_state['transactions'].empty:
        st.dataframe(st.session_state['transactions'])

        # Download Transactions as CSV
        st.download_button(
            label="Download as CSV",
            data=st.session_state['transactions'].to_csv(index=False).encode('utf-8'),
            file_name='transactions.csv',
            mime='text/csv',
        )
    else:
        st.info("No transactions recorded yet.")

# --- Budgeting Page ---
elif page == "Budgeting":
    st.subheader("Set Your Budgets")
    st.info("Budgeting features will be implemented here. You could have sections to set monthly budgets for different categories and track your spending against them.")
    # Placeholder for future budgeting features
    if 'budgets' not in st.session_state:
        st.session_state['budgets'] = {}

    category_options = st.session_state['transactions']['Category'].unique().tolist() + ["New Category"]
    selected_budget_category = st.selectbox("Select Category to Budget", category_options)

    if selected_budget_category == "New Category":
        new_budget_category = st.text_input("Enter new category name:")
        if new_budget_category:
            budget_amount = st.number_input(f"Set monthly budget for {new_budget_category}", min_value=0.01)
            if st.button(f"Set Budget for {new_budget_category}"):
                st.session_state['budgets'][new_budget_category] = budget_amount
                st.success(f"Budget of ₹ {budget_amount:,.2f} set for {new_budget_category}")
    elif selected_budget_category and selected_budget_category != "New Category":
        existing_budget = st.session_state['budgets'].get(selected_budget_category, 0)
        budget_amount = st.number_input(f"Set monthly budget for {selected_budget_category}", min_value=0.01, value=existing_budget)
        if st.button(f"Update Budget for {selected_budget_category}"):
            st.session_state['budgets'][selected_budget_category] = budget_amount
            st.success(f"Budget of ₹ {budget_amount:,.2f} updated for {selected_budget_category}")

    if st.session_state['budgets']:
        st.subheader("Current Budgets")
        budgets_df = pd.DataFrame(list(st.session_state['budgets'].items()), columns=['Category', 'Budget'])
        st.dataframe(budgets_df)

        # Track spending against budget (basic implementation)
        if not st.session_state['transactions'].empty:
            monthly_expenses = st.session_state['transactions'][st.session_state['transactions']['Type'] == 'Expense']
            if not monthly_expenses.empty:
                spending_vs_budget = monthly_expenses.groupby('Category')['Amount'].sum().reset_index()
                spending_vs_budget = spending_vs_budget.rename(columns={'Amount': 'Actual Spending'})
                budget_df = pd.DataFrame(list(st.session_state['budgets'].items()), columns=['Category', 'Budget'])
                merged_df = pd.merge(spending_vs_budget, budget_df, on='Category', how='left').fillna(0)
                merged_df['Remaining Budget'] = merged_df['Budget'] - merged_df['Actual Spending']
                st.subheader("Spending vs Budget (Monthly - Rough)")
                st.dataframe(merged_df)
            else:
                st.info("No expense data to track against budget.")
        else:
            st.info("Add transactions to track against your budget.")
    else:
        st.info("Set budgets for different categories to start tracking.")

# --- Reports Page ---
elif page == "Reports":
    st.subheader("Financial Reports")
    if not st.session_state['transactions'].empty:
        # Income by Category
        income_data = st.session_state['transactions'][st.session_state['transactions']['Type'] == 'Income']
        if not income_data.empty:
            income_by_category = income_data.groupby('Category')['Amount'].sum().reset_index()
            fig_income = px.bar(income_by_category, x='Category', y='Amount', title='Income by Category')
            st.plotly_chart(fig_income)
        else:
            st.info("No income data available.")

        # Expenses by Category
        expense_data = st.session_state['transactions'][st.session_state['transactions']['Type'] == 'Expense']
        if not expense_data.empty:
            expenses_by_category = expense_data.groupby('Category')['Amount'].sum().reset_index()
            fig_expense = px.bar(expenses_by_category, x='Category', y='Amount', title='Expenses by Category')
            st.plotly_chart(fig_expense)
        else:
            st.info("No expense data available.")
    else:
        st.info("No transaction data to generate reports.")
