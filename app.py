#Added the Take Attendance feature that starts and stops the camera
import streamlit as st
import pandas as pd
import time
import cv2
import numpy as np
from datetime import datetime
import os
from PIL import Image

# Function to verify credentials
def verify_credentials(username, password):
    # In a real application, use a secure method to store and verify credentials
    return username == "admin" and password == "password123"

# Function to save the captured image
def save_image(image, name):
    # Create Attendance/Photos directory if it doesn't exist
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

# If not authenticated, show login form
if not st.session_state.authenticated:
    st.title("🔒 Login to Attendance App")
    
    # Create input fields for username and password
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    # Login button
    if st.button("Login"):
        if verify_credentials(username, password):
            st.session_state.authenticated = True
            st.success("Login successful!")
            st.rerun()  # Updated here
        else:
            st.error("Invalid username or password.")
else:
    # Set the page configuration
    st.set_page_config(page_title="Attendance App", layout="wide")
    
    # Application Title
    st.title("🚀 Attendance Dashboard")
    
    # Get current timestamp
    ts = time.time()
    current_date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
    current_time = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
    
    # Display current date and time in a sidebar
    st.sidebar.header("📅 Current Date and Time")
    st.sidebar.write(f"**Date:** {current_date}")
    st.sidebar.write(f"**Time:** {current_time}")
    
    # Create two columns for Attendance and Attendance Data
    col1, col2 = st.columns(2)
    
    # Attendance Section (Camera Feed)
    with col1:
        st.header("📷 Take Attendance")
        
        # Camera control buttons
        camera_col1, camera_col2 = st.columns(2)
        with camera_col1:
            start_camera = st.button("Start Camera", key="start_cam")
        with camera_col2:
            stop_camera = st.button("Stop Camera", key="stop_cam")
        
        if start_camera:
            st.session_state.camera_on = True
        if stop_camera:
            st.session_state.camera_on = False
            st.session_state.captured_image = None
        
        if st.session_state.camera_on:
            # Create a placeholder for the camera feed
            camera_placeholder = st.empty()
            
            # Initialize camera
            try:
                camera = cv2.VideoCapture(0)
                
                # Ensure camera is opened successfully
                if not camera.isOpened():
                    st.error("Failed to open camera. Please check your camera connection.")
                else:
                    # Display camera feed
                    frame_placeholder = camera_placeholder.empty()
                    take_photo = st.button("Take Photo")
                    
                    while st.session_state.camera_on:
                        ret, frame = camera.read()
                        if ret:
                            # Convert BGR to RGB
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            frame_placeholder.image(frame_rgb, channels="RGB")
                            
                            if take_photo:
                                st.session_state.captured_image = frame_rgb.copy()
                                # Save the captured image
                                saved_file = save_image(st.session_state.captured_image, "attendance")
                                st.success(f"Photo captured and saved as {saved_file}")
                                break
                        else:
                            st.error("Failed to capture frame from camera")
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
            st.dataframe(df)
        except FileNotFoundError:
            st.warning(f"No attendance records found for {selected_date_str}")
            
        # Add a refresh button
        if st.button("Refresh Data"):
            st.rerun()  # Updated here
            
    # Logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.camera_on = False
        st.session_state.captured_image = None
        st.rerun()  # Updated here
