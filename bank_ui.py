
import streamlit as st
from supabase import create_client, Client

# ============================================================
# SUPABASE CONFIGURATION
# ============================================================

SUPABASE_URL = "https://lnlqplkchjobbkbcbfaq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxubHFwbGtjaGpvYmJrYmNiZmFxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNDEwMTQsImV4cCI6MjA4MTYxNzAxNH0.YiViz0eQfPNEVK-ZtLt0rjtgqCYkp5fsZVfMFTptm8s"

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Streamlit page setup
st.set_page_config(page_title="Bank System", layout="centered")
st.title("🏦 Simple Bank Application")

# ============================================================
# AUTHENTICATION FUNCTIONS
# ============================================================

def signup_user(email, password):
    """
    Registers a new user in Supabase Auth.

    - Password is hashed by Supabase
    - Stored in auth.users table
    """
    return supabase.auth.sign_up({
        "email": email,
        "password": password
    })


def login_user(email, password):
    """
    Logs in an existing user.

    - Supabase validates credentials
    - JWT token is stored internally
    """
    return supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })


def logout_user():
    """
    Logs out current user.

    - JWT token is removed
    """
    supabase.auth.sign_out()


def get_logged_in_user():
    """
    Returns current logged-in user if JWT exists.
    """
    return supabase.auth.get_user()

# ============================================================
# SIDEBAR MENU
# ============================================================

menu = ["Signup", "Login", "Dashboard", "Logout"]
choice = st.sidebar.selectbox("Menu", menu)

# ============================================================
# SIGNUP PAGE
# ============================================================

if choice == "Signup":
    st.subheader("Create Account")

    # Form clears automatically after submit
    with st.form("signup_form", clear_on_submit=True):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Signup")

    if submit:
        result = signup_user(email, password)

        if result.user:
            st.success("Signup successful. Please login.")
        else:
            st.error("Signup failed")

# ============================================================
# LOGIN PAGE
# ============================================================

elif choice == "Login":
    st.subheader("Login")

    with st.form("login_form", clear_on_submit=True):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        result = login_user(email, password)

        if result.user:
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

# ============================================================
# DASHBOARD
# ============================================================

elif choice == "Dashboard":

    user_response = get_logged_in_user()

    if not user_response or not user_response.user:
        st.warning("Please login first")
    else:
        user_id = user_response.user.id

        # Fetch bank account linked to logged-in user
        account = supabase.table("bank_accounts") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()

        # ----------------------------------------------------
        # CREATE BANK ACCOUNT (ONLY ONCE)
        # ----------------------------------------------------
        if not account.data:
            st.info("No bank account found")

            with st.form("create_account_form", clear_on_submit=True):
                name = st.text_input("Name")
                age = st.number_input("Age", min_value=18)
                acc_no = st.number_input("Account Number", step=1)
                submit = st.form_submit_button("Create Account")

            if submit:
                supabase.table("bank_accounts").insert({
                    "user_id": user_id,
                    "name": name,
                    "age": age,
                    "account_number": int(acc_no),
                    "balance": 500
                }).execute()

                st.success("Bank account created")

        # ----------------------------------------------------
        # BANK OPERATIONS
        # ----------------------------------------------------
        else:
            acc = account.data[0]

            st.success(f"Welcome {acc['name']}")
            st.metric("Current Balance", f"₹ {acc['balance']}")

            with st.form("transaction_form", clear_on_submit=True):
                amount = st.number_input(
                    "Amount",
                    min_value=1,
                    help="Enter amount to deposit or withdraw"
                )

                deposit = st.form_submit_button("Deposit")
                withdraw = st.form_submit_button("Withdraw")

            # Deposit logic
            if deposit:
                new_balance = acc["balance"] + amount

                supabase.table("bank_accounts") \
                    .update({"balance": new_balance}) \
                    .eq("id", acc["id"]) \
                    .execute()

                st.success("Amount deposited")

            # Withdraw logic
            if withdraw:
                if amount > acc["balance"]:
                    st.error("Insufficient balance")
                else:
                    new_balance = acc["balance"] - amount

                    supabase.table("bank_accounts") \
                        .update({"balance": new_balance}) \
                        .eq("id", acc["id"]) \
                        .execute()

                    st.success("Amount withdrawn")

# ============================================================
# LOGOUT
# ============================================================

elif choice == "Logout":
    logout_user()
    st.success("Logged out successfully")
