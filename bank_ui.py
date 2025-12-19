import streamlit as st
from supabase import create_client, Client
import random
import time

# ==========================================
# 1. SUPABASE CONFIGURATION
# ==========================================
# Link to your specific project in the Supabase Cloud
URL = "https://lnlqplkchjobbkbcbfaq.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxubHFwbGtjaGpvYmJrYmNiZmFxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNDEwMTQsImV4cCI6MjA4MTYxNzAxNH0.YiViz0eQfPNEVK-ZtLt0rjtgqCYkp5fsZVfMFTptm8s"

# Creating the 'bridge' between Python and your Database
supabase: Client = create_client(URL, KEY)

# Page configuration for a professional look
st.set_page_config(page_title="Vivnovation Bank", layout="centered")

# --- SAFE SESSION LOGIC ---
# This ensures that even if the page refreshes, we check if the user is still logged in.
if "user" not in st.session_state:
    try:
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
# If user is logged in, show Dashboard/Logout. If not, show Signup/Login.
if st.session_state.user:
    menu = ["Dashboard", "Logout"]
else:
    menu = ["Signup", "Login"]
choice = st.sidebar.selectbox("Menu Navigation", menu)

# ==========================================
# 3. LOGIN MODULE (WITH BALLOONS)
# ==========================================
if choice == "Login":
    st.subheader("Customer Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Secure Login"):
        try:
            # Check credentials against Supabase Auth
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                st.session_state.user = res.user
                
                # Visual Feedback for Successful UX
                st.balloons() 
                st.success("Login Successful! Welcome back.")
                
                # Wait 1 second so the user sees the animation
                time.sleep(1) 
                st.rerun()
        except Exception as e:
            st.error("Invalid Email or Password. Please try again.")

# ==========================================
# 4. SIGNUP MODULE
# ==========================================
elif choice == "Signup":
    st.subheader("Create New Bank Account")
    email = st.text_input("Email")
    password = st.text_input("Password (Min 6 Characters)", type="password")
    
    if st.button("Register Credentials"):
        try:
            # Registers user in the Auth table
            supabase.auth.sign_up({"email": email, "password": password})
            st.success("Credentials saved! Now switch to the Login page.")
        except Exception as e:
            st.error(f"Signup failed: {e}")

# ==========================================
# 5. DASHBOARD (CORE BANKING LOGIC)
# ==========================================
elif choice == "Dashboard":
    if not st.session_state.user:
        st.warning("Please login first to access your dashboard.")
    else:
        user_id = st.session_state.user.id
        
        # Query our custom table to find this user's bank data
        res = supabase.table("bank_accounts").select("*").eq("user_id", user_id).execute()
        
        # --- CASE A: PROFILE NEEDS SETUP ---
        if not res.data:
            st.subheader("📝 Complete Your Bank Profile")
            with st.form("reg_form", clear_on_submit=True):
                name = st.text_input("Full Name")
                age = st.number_input("Age", min_value=1, step=1)
                balance = st.number_input("Initial Deposit (Min ₹500)", min_value=500)
                
                if st.form_submit_button("Save Profile"):
                    # Business Logic: Age Validation
                    if age < 18:
                        st.error("Error: You must be 18+ to open a Vivnovation bank account.")
                    elif name == "":
                        st.warning("Please enter your legal name.")
                    else:
                        # Logic: Automatically generate a unique account number
                        auto_acc = f"VIV-{random.randint(100000, 999999)}"
                        
                        # Save the bank details linked to the Auth User ID
                        supabase.table("bank_accounts").insert({
                            "user_id": user_id, 
                            "name": name, 
                            "age": int(age), 
                            "account_number": auto_acc, 
                            "balance": balance
                        }).execute()
                        
                        st.snow()
                        st.success(f"Profile Created! Account No: {auto_acc}")
                        time.sleep(1.5)
                        st.rerun()
        
        # --- CASE B: ACTIVE DASHBOARD ---
        else:
            user_info = res.data[0]
            st.subheader(f"Welcome, {user_info['name']}")
            
            # Row 1: Display Metrics and Account Info
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Balance", f"₹ {user_info['balance']}")
            with col2:
                st.info(f"**Account No:** {user_info['account_number']}")
                st.info(f"**Status:** Verified Member")

            st.divider()

            # Row 2: Transactions (Deposit/Withdraw)
            st.subheader("💸 Transactions")
            with st.form("transaction_form", clear_on_submit=True):
                amount = st.number_input("Transaction Amount (₹)", min_value=1, step=1)
                t_col1, t_col2 = st.columns(2)
                
                # DEPOSIT LOGIC
                if t_col1.form_submit_button("Deposit"):
                    new_bal = user_info['balance'] + amount
                    supabase.table("bank_accounts").update({"balance": new_bal}).eq("user_id", user_id).execute()
                    st.success(f"Successfully deposited ₹{amount}")
                    time.sleep(1)
                    st.rerun()
                
                # WITHDRAW LOGIC
                if t_col2.form_submit_button("Withdraw"):
                    if amount > user_info['balance']:
                        st.error("Transaction Declined: Insufficient Funds.")
                    else:
                        new_bal = user_info['balance'] - amount
                        supabase.table("bank_accounts").update({"balance": new_bal}).eq("user_id", user_id).execute()
                        st.success(f"Successfully withdrew ₹{amount}")
                        time.sleep(1)
                        st.rerun()

# ==========================================
# 6. LOGOUT
# ==========================================
elif choice == "Logout":
    # Ends the session on the cloud and wipes local session state
    supabase.auth.sign_out()
    st.session_state.user = None
    st.info("You have been securely logged out.")
    time.sleep(1)
    st.rerun()
