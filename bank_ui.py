
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

# --- REFRESH LOGIC ---
# We check if Supabase ALREADY has a user session active.
# This prevents the "Invalid/Wait" feeling during transitions.
if "user" not in st.session_state:
    current_session = supabase.auth.get_user()
    if current_session.user:
        st.session_state.user = current_session.user
    else:
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
# 3. LOGIN MODULE (FIXED)
# ==========================================
if choice == "Login":
    st.subheader("Customer Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        try:
            # Step 1: Attempt authentication
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            
            if res.user:
                # Step 2: Save user to state
                st.session_state.user = res.user
                st.success("Login Successful! Redirecting...")
                
                # Step 3: CRITICAL FIX - We force a rerun here.
                # This makes the app immediately see the new session and switch to Dashboard.
                st.rerun() 
        except Exception as e:
            # We only show "Invalid" if Supabase actually returns an error.
            st.error("Invalid Email or Password. Please try again.")

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
            st.success("Credentials saved! You can now switch to the Login page.")
        except Exception as e:
            st.error(f"Signup failed: {e}")

# ==========================================
# 5. DASHBOARD (The Personal Interface)
# ==========================================
elif choice == "Dashboard":
    if not st.session_state.user:
        st.warning("Please login first.")
    else:
        user_id = st.session_state.user.id
        
        # Check if profile exists
        res = supabase.table("bank_accounts").select("*").eq("user_id", user_id).execute()
        
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
                        st.success("Saved! Refreshing...")
                        st.rerun()
        else:
            # --- DISPLAY DASHBOARD ---
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
