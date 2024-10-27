# app.py

import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Function to verify credentials
def verify_credentials(username, password):
    # In a real application, use a secure method to store and verify credentials
    # For demonstration, using hardcoded credentials
    return username == "admin" and password == "password123"

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# If not authenticated, show login form
if not st.session_state.authenticated:
    st.title("🔒 Login to FizzBuzz Attendance App")
    
    # Create input fields for username and password
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    # Login button
    if st.button("Login"):
        if verify_credentials(username, password):
            st.session_state.authenticated = True
            st.success("Login successful!")
        else:
            st.error("Invalid username or password.")
else:
    # Set the page configuration
    st.set_page_config(page_title="FizzBuzz Attendance App", layout="wide")

    # Application Title
    st.title("🚀 FizzBuzz Attendance Dashboard")

    # Get current timestamp
    ts = time.time()

    # Format date and time from timestamp
    current_date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
    current_time = datetime.fromtimestamp(ts).strftime("%H:%M:%S")

    # Display current date and time in a sidebar
    st.sidebar.header("📅 Current Date and Time")
    st.sidebar.write(f"**Date:** {current_date}")
    st.sidebar.write(f"**Time:** {current_time}")

    # Auto-refresh the app every 2000 milliseconds (2 seconds), up to 100 times
    count = st_autorefresh(interval=2000, limit=100, key="fizzbuzzcounter")

    # Create two columns for FizzBuzz and Attendance
    col1, col2 = st.columns(2)

    # FizzBuzz Section
    with col1:
        st.header("🔢 FizzBuzz Counter")
        if count == 0:
            st.write("Count is zero")
        elif count % 3 == 0 and count % 5 == 0:
            st.write("FizzBuzz")
        elif count % 3 == 0:
            st.write("Fizz")
        elif count % 5 == 0:
            st.write("Buzz")
        else:
            st.write(f"Count: {count}")

    # Attendance Section
    with col2:
        st.header("📊 Attendance Data")
        
        # Add a date picker for selecting the date
        selected_date = st.date_input("Select Date", datetime.now())
        
        # Format the selected date to match the filename
        selected_date_str = selected_date.strftime("%d-%m-%Y")
        
        # Path to the attendance CSV file
        attendance_file = f"Attendance/Attendance_{selected_date_str}.csv"
        
        st.write(f"**Selected Date:** {selected_date_str}")
        
        # Try to read the CSV file
        try:
            df = pd.read_csv(attendance_file)
            
            # Display the DataFrame with maximum values highlighted
            st.dataframe(df.style.highlight_max(axis=0))
        except FileNotFoundError:
            st.error(f"Attendance file for {selected_date_str} not found.")
