import cv2
import pickle
import numpy as np
import os

# Initialize video capture from the default webcam
video = cv2.VideoCapture(0)

# Load frontal and profile face detectors
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


faces_data = []  # List to hold face images
labels = []      # List to hold labels (names converted to IDs)
i = 0

name = input("Enter Your Name: ")

# Create a unique label ID for the person
if 'label_ids.pkl' not in os.listdir('data/'):
    label_id = 0
    label_ids = {name: label_id}
else:
    with open('data/label_ids.pkl', 'rb') as f:
        label_ids = pickle.load(f)
    if name in label_ids:
        label_id = label_ids[name]
    else:
        label_id = max(label_ids.values()) + 1
        label_ids[name] = label_id

print(f"Assigned label ID {label_id} to {name}")
print("Please turn your head slowly from left to right and up and down during data collection.")

while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detect_faces(gray)
    for (x, y, w, h, face_type) in faces:
        face_img = gray[y:y+h, x:x+w]
        # If it's a profile face, flip the image to face forward
        if face_type == 'profile_left':
            face_img = cv2.flip(face_img, 1)
        elif face_type == 'profile_right':
            pass  # Right profile faces are already facing forward after flipping
        resized_img = cv2.resize(face_img, (200, 200))
        if len(faces_data) < 100 and i % 5 == 0:
            faces_data.append(resized_img)
            labels.append(label_id)
        i += 1
        cv2.putText(frame, f"Samples: {len(faces_data)}", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imshow("Capturing Faces", frame)
    key = cv2.waitKey(1)
    if key == ord('q') or len(faces_data) >= 100:
        break

video.release()
cv2.destroyAllWindows()


# Initialize existing_faces and existing_labels
existing_faces = []
existing_labels = []

# Check if data files exist and load existing data
if 'faces_data.pkl' in os.listdir('data/'):
    with open('data/faces_data.pkl', 'rb') as f:
        existing_faces = pickle.load(f)
    with open('data/labels.pkl', 'rb') as f:
        existing_labels = pickle.load(f)

# Combine existing data with new data
all_faces = existing_faces + faces_data
all_labels = existing_labels + labels

# Save the combined data
with open('data/faces_data.pkl', 'wb') as f:
    pickle.dump(all_faces, f)
with open('data/labels.pkl', 'wb') as f:
    pickle.dump(all_labels, f)

# Save or update the label IDs
with open('data/label_ids.pkl', 'wb') as f:
    pickle.dump(label_ids, f)

print(f"Data saved. Total samples: {len(all_faces)}")


# Initialize the LBPH face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(all_faces, np.array(all_labels))

# Save the trained model
recognizer.save('data/face_recognizer.yml')
print("Model trained and saved successfully.")


