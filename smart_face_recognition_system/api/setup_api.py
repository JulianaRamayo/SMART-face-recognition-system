import cv2
import pickle
import numpy as np
import os
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from datetime import datetime
import shutil
from typing import List
from collections import Counter
import uvicorn
from io import BytesIO

app = FastAPI()

# Ensure the necessary directories exist
if not os.path.exists('data'):
    os.makedirs('data')
if not os.path.exists('Attendance'):
    os.makedirs('Attendance')
if not os.path.exists('temp'):
    os.makedirs('temp')


# Load the face recognizer model and data
def load_model():
    global recognizer, label_ids, id_to_name
    # Load the face data and labels
    with open('data/faces_data.pkl', 'rb') as f:
        faces_data = pickle.load(f)
    with open('data/labels.pkl', 'rb') as f:
        labels = pickle.load(f)
    with open('data/label_ids.pkl', 'rb') as f:
        label_ids = pickle.load(f)
    # Invert the label_ids dictionary to map IDs to names
    id_to_name = {v: k for k, v in label_ids.items()}
    # Initialize the LBPH face recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces_data, np.array(labels))
    print("Model loaded successfully.")

# Load the model at startup
load_model()

# Load face detectors
frontal_face_cascade = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
profile_face_cascade = cv2.CascadeClassifier('data/haarcascade_profileface.xml')

def detect_faces(gray_frame):
    faces = []
    # Detect frontal faces
    frontal_faces = frontal_face_cascade.detectMultiScale(gray_frame, 1.3, 5)
    for (x, y, w, h) in frontal_faces:
        faces.append((x, y, w, h, 'frontal'))
    # Detect profile faces (left side)
    profile_faces_left = profile_face_cascade.detectMultiScale(gray_frame, 1.3, 5)
    for (x, y, w, h) in profile_faces_left:
        faces.append((x, y, w, h, 'profile_left'))
    # Detect profile faces (right side by flipping the frame)
    flipped_frame = cv2.flip(gray_frame, 1)
    profile_faces_right = profile_face_cascade.detectMultiScale(flipped_frame, 1.3, 5)
    for (x, y, w, h) in profile_faces_right:
        x = gray_frame.shape[1] - x - w  # Adjust x-coordinate after flipping
        faces.append((x, y, w, h, 'profile_right'))
    return faces


@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    # Read the uploaded image file
    image_bytes = await image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detect_faces(gray)

    if len(faces) == 0:
        return JSONResponse(content={"message": "No face detected."}, status_code=400)

    # Assume the first face detected
    (x, y, w, h, face_type) = faces[0]
    face_img = gray[y:y+h, x:x+w]
    # If it's a profile face, flip the image to face forward
    if face_type == 'profile_left':
        face_img = cv2.flip(face_img, 1)
    resized_img = cv2.resize(face_img, (200, 200))
    label_id, confidence = recognizer.predict(resized_img)
    name = id_to_name.get(label_id, "Unknown")

    return {"name": name, "confidence": float(confidence)}
