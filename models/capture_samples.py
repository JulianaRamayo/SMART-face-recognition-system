import cv2
import os
from face_detection import detect_frontal_faces

# Load the Haar Cascade classifier
cascade_path = 'data/haarcascade_frontalface_default.xml'
frontal_face_cascade = cv2.CascadeClassifier(cascade_path)

# Initialize user input and sample directory
name = input("Enter your name: ").strip()
samples_dir = os.path.join('data', 'samples', name)
os.makedirs(samples_dir, exist_ok=True)

# Initialize video capture
video = cv2.VideoCapture(0)

# Parameters for sample collection
max_samples = 100
sample_count = 0
frame_count = 0

while True:
    ret, frame = video.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Detect faces in the current frame
    faces = detect_frontal_faces(frame, frontal_face_cascade)

    for (x, y, w, h) in faces:
        face_img = frame[y:y+h, x:x+w]
        resized_img = cv2.resize(face_img, (224, 224))

        if sample_count < max_samples and frame_count % 5 == 0:
            sample_filename = os.path.join(samples_dir, f"{name}_{sample_count + 1}.png")
            cv2.imwrite(sample_filename, resized_img)
            sample_count += 1
            print(f"Saved sample {sample_count}/{max_samples}: {sample_filename}")

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.putText(
        frame, f"Samples: {sample_count}/{max_samples}",
        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2
    )

    cv2.imshow("Capturing Faces", frame)
    frame_count += 1

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or sample_count >= max_samples:
        break

# Release resources
video.release()
cv2.destroyAllWindows()

print(f"Data collection complete. {sample_count} samples saved in '{samples_dir}'.")
