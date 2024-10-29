import cv2
import pickle
import numpy as np
import os

# Initialize video capture from the default webcam
video = cv2.VideoCapture(0)

# Load frontal and profile face detectors
frontal_face_cascade = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
profile_face_cascade = cv2.CascadeClassifier('data/haarcascade_profileface.xml')
