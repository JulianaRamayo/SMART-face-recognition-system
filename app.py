#Fixed the error where double click was needed to use the buttons.
import streamlit as st
import pandas as pd
import time
import cv2
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
def save_image(image, name):
    os.makedirs("Attendance/Photos", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Attendance/Photos/{name}_{timestamp}.jpg"
    cv2.imwrite(filename, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    return filename

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'camera_on' not in st.session_state:
    st.session_state.camera_on = False
if 'captured_image' not in st.session_state:
    st.session_state.captured_image = None

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
            st.rerun()  # Add this line to re-run the script
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
        
        # Camera controls
        start_camera = st.button("Start Camera")
        stop_camera = st.button("Stop Camera")
        
        # Update camera state based on button clicks
        if start_camera:
            st.session_state.camera_on = True
        if stop_camera:
            st.session_state.camera_on = False
            st.session_state.captured_image = None
        
        # Display camera feed if camera is on
        if st.session_state.camera_on:
            camera_placeholder = st.empty()
            try:
                camera = cv2.VideoCapture(0)
                
                if not camera.isOpened():
                    st.error("Failed to open camera.")
                else:
                    frame_placeholder = camera_placeholder.empty()
                    take_photo = st.button("Take Photo")
                    
                    while st.session_state.camera_on:
                        ret, frame = camera.read()
                        if ret:
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            frame_placeholder.image(frame_rgb, channels="RGB")
                            
                            if take_photo:
                                st.session_state.captured_image = frame_rgb.copy()
                                saved_file = save_image(st.session_state.captured_image, "attendance")
                                st.success(f"Photo captured and saved as {saved_file}")
                                break
                        else:
                            st.error("Failed to capture frame from camera.")
                            break
                    
                    camera.release()
            
            except Exception as e:
                st.error(f"Error accessing camera: {str(e)}")
        
        # Display captured image
        if st.session_state.captured_image is not None:
            st.subheader("Captured Photo:")
            st.image(st.session_state.captured_image, channels="RGB")
    
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
        st.session_state.camera_on = False
        st.session_state.captured_image = None
        st.rerun()  # Re-run the script to update the interface

