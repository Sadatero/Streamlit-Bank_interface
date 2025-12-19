import streamlit as st
from supabase import create_client, Client

# --- CONNECT TO SUPABASE ---
URL = "https://lnlqplkchjobbkbcbfaq.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxubHFwbGtjaGpvYmJrYmNiZmFxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNDEwMTQsImV4cCI6MjA4MTYxNzAxNH0.YiViz0eQfPNEVK-ZtLt0rjtgqCYkp5fsZVfMFTptm8s"

supabase: Client = create_client(URL, KEY)

st.title("🏦 Vivnovation Bank App")

# --- APP MEMORY ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- SIDEBAR ---
if st.session_state.user:
    menu = ["Dashboard", "Logout"]
else:
    menu = ["Signup", "Login"]
choice = st.sidebar.selectbox("Menu", menu)

# --- SIGNUP ---
if choice == "Signup":
    st.subheader("New User Registration")
    email = st.text_input("Email")
    password = st.text_input("Password (min 6 chars)", type="password")
    
    if st.button("Register"):
        try:
            # This line sends the data to Supabase
            res = supabase.auth.sign_up({"email": email, "password": password})
            if res.user:
                st.success(f"Account created for {email}! Now go to Login.")
            else:
                st.error("Signup failed. Check your Supabase logs.")
        except Exception as e:
            st.error(f"Signup Error: {e}")

# --- LOGIN ---
elif choice == "Login":
    st.subheader("Login to your Bank")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        try:
            # This checks the cloud for your email/password
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.user = res.user
            st.success("Login Successful!")
            st.rerun()
        except Exception as e:
            st.error(f"Login Failed: {e}")

# --- DASHBOARD ---
elif choice == "Dashboard":
    user_id = st.session_state.user.id
    # Fetch from our table
    res = supabase.table("bank_accounts").select("*").eq("user_id", user_id).execute()
    
    if not res.data:
        st.info("Complete your profile setup")
        name = st.text_input("Full Name")
        if st.button("Create Profile"):
            # This creates your starting balance of 500
            supabase.table("bank_accounts").insert({"user_id": user_id, "name": name, "balance": 500}).execute()
            st.success("Profile Created!")
            st.rerun()
    else:
        acc = res.data[0]
        st.write(f"### Welcome, {acc['name']}")
        st.metric("Balance", f"₹ {acc['balance']}")
        # (Deposit/Withdraw buttons go here...)

elif choice == "Logout":
    st.session_state.user = None
    st.rerun()
