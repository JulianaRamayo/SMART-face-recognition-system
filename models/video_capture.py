import cv2
import os

# Initialize video capture from the default webcam (device index 0)
video = cv2.VideoCapture(0)

if not video.isOpened():
    print("Error: Could not open video stream.")
    exit()

print("Press 'q' to exit the video feed.")

while True:
    ret, frame = video.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Display the resulting frame
    cv2.imshow("Video Feed", frame)

    # Wait for 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting video feed.")
        break

# Release the video capture object and close display window
video.release()
cv2.destroyAllWindows()
