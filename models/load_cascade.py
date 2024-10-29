import cv2

# Path to the Haar Cascade file for frontal face detection
cascade_path = "models/haarcascade_frontalface_default.xml"

# Load the Haar Cascade classifier
frontal_face_cascade = cv2.CascadeClassifier(cascade_path)

# Check if the classifier has been loaded correctly
if frontal_face_cascade.empty():
    print(f"Error: Could not load Haar Cascade file at '{cascade_path}'.")
    exit()
else:
    print("Haar Cascade classifier loaded successfully.")