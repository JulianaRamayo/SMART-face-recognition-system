#Take Photo button works and it saves the image in a folder as evidence
import streamlit as st
import pandas as pd
import time
import numpy as np
from datetime import datetime
import os
from PIL import Image

# Set page configuration (must be the first Streamlit command)
st.set_page_config(page_title="Attendance App", layout="wide")

# Function to verify credentials
def verify_credentials(username, password):
    return username == "admin" and password == "password123"

# Function to save the captured image
def save_image(image_data, name):
    os.makedirs("Attendance/Photos", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Attendance/Photos/{name}_{timestamp}.jpg"
    image = Image.open(image_data)
    image.save(filename)
    return filename

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Login Form
if not st.session_state.authenticated:
    st.title("🔒 Login to Attendance App")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    # Login button
    if st.button("Login"):
        if verify_credentials(username, password):
            st.session_state.authenticated = True
            st.success("Login successful!")
            st.rerun()  # Re-run the script to update the interface
        else:
            st.error("Invalid username or password.")

# Main Application Content (only after login)
if st.session_state.authenticated:
    # Show a success message once logged in
    st.success("Login successful!")
    
    # Title for the main dashboard
    st.title("🚀 Attendance Dashboard")
    
    # Display current date and time in sidebar
    current_date = datetime.now().strftime("%d-%m-%Y")
    current_time = datetime.now().strftime("%H:%M:%S")
    st.sidebar.header("📅 Current Date and Time")
    st.sidebar.write(f"**Date:** {current_date}")
    st.sidebar.write(f"**Time:** {current_time}")
    
    # Attendance and Camera Controls
    col1, col2 = st.columns(2)
    with col1:
        st.header("📷 Take Attendance")
        
        # Use st.camera_input to capture a photo
        img_file_buffer = st.camera_input("Take a picture")
        
        if img_file_buffer is not None:
            # To read image file buffer as a PIL Image:
            image = Image.open(img_file_buffer)
            # Optionally, convert the image to OpenCV format:
            # image = np.array(image)
            # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Save the image
            saved_file = save_image(img_file_buffer, "attendance")
            st.success(f"Photo captured and saved as {saved_file}")
            
            # Display the captured image
            st.subheader("Captured Photo:")
            st.image(image, caption='Captured Image', use_column_width=True)
    
    # Attendance Data Section
    with col2:
        st.header("📊 Attendance Data")
        
        selected_date = st.date_input("Select Date", datetime.now())
        selected_date_str = selected_date.strftime("%d-%m-%Y")
        attendance_file = f"Attendance/Attendance_{selected_date_str}.csv"
        st.write(f"**Selected Date:** {selected_date_str}")
        
        try:
            df = pd.read_csv(attendance_file)
            st.dataframe(df)
        except FileNotFoundError:
            st.warning(f"No attendance records found for {selected_date_str}")
            
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()  # Re-run the script to update the interface
