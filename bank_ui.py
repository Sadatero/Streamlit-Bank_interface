
import streamlit as st
from supabase import create_client, Client
import random

# ==========================================
# 1. SUPABASE CONNECTION
# ==========================================
URL = "https://lnlqplkchjobbkbcbfaq.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxubHFwbGtjaGpvYmJrYmNiZmFxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNDEwMTQsImV4cCI6MjA4MTYxNzAxNH0.YiViz0eQfPNEVK-ZtLt0rjtgqCYkp5fsZVfMFTptm8s"
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Vivnovation Bank", layout="centered")

# --- FIXED SESSION LOGIC ---
if "user" not in st.session_state:
    try:
        # Safely check if a user is already logged in
        response = supabase.auth.get_user()
        if response and hasattr(response, 'user') and response.user:
            st.session_state.user = response.user
        else:
            st.session_state.user = None
    except:
        st.session_state.user = None

st.title("🏦 Vivnovation Bank System")

# ==========================================
# 2. SIDEBAR NAVIGATION
# ==========================================
if st.session_state.user:
    menu = ["Dashboard", "Logout"]
else:
    menu = ["Signup", "Login"]
choice = st.sidebar.selectbox("Menu", menu)

# ==========================================
# 3. LOGIN MODULE
# ==========================================
if choice == "Login":
    st.subheader("Customer Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                st.session_state.user = res.user
                st.success("Login Successful!")
                st.rerun()
        except Exception as e:
            st.error("Invalid Email or Password.")

# ==========================================
# 4. SIGNUP MODULE
# ==========================================
elif choice == "Signup":
    st.subheader("Create New Account")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Register"):
        try:
            supabase.auth.sign_up({"email": email, "password": password})
            st.success("Credentials saved! Now switch to Login.")
        except Exception as e:
            st.error(f"Signup failed: {e}")

# ==========================================
# 5. DASHBOARD
# ==========================================
elif choice == "Dashboard":
    if not st.session_state.user:
        st.warning("Please login first.")
    else:
        user_id = st.session_state.user.id
        # We fetch only columns we are SURE exist: name, age, balance, account_number
        res = supabase.table("bank_accounts").select("id, name, age, balance, account_number").eq("user_id", user_id).execute()
        
        if not res.data:
            st.subheader("📝 Complete Your Profile")
            with st.form("reg_form", clear_on_submit=True):
                name = st.text_input("Full Name")
                age = st.number_input("Age", min_value=1, step=1)
                balance = st.number_input("Initial Deposit", min_value=500)
                
                if st.form_submit_button("Save Details"):
                    if age < 18:
                        st.error("You must be 18+ to open an account.")
                    else:
                        auto_acc = f"VIV-{random.randint(100000, 999999)}"
                        supabase.table("bank_accounts").insert({
                            "user_id": user_id, "name": name, "age": int(age), 
                            "account_number": auto_acc, "balance": balance
                        }).execute()
                        st.success("Profile Created!")
                        st.rerun()
        else:
            user_info = res.data[0]
            st.subheader(f"Welcome, {user_info['name']}")
            st.metric("Total Balance", f"₹ {user_info['balance']}")
            st.info(f"Account No: {user_info['account_number']}")

# ==========================================
# 6. LOGOUT
# ==========================================
elif choice == "Logout":
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()
