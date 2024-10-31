import cv2
def detect_frontal_faces(frame, face_cascade):
    """
    Detects frontal faces in a given frame.

    Args:
        frame (numpy.ndarray): The input color image.
        face_cascade (cv2.CascadeClassifier): The load Haar Cascade classifier.

    Returns:
        list of tuples: A list containing the coordinates of detected face (x, y, w, h).
    """
    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    faces = face_cascade.detectMultiScale(
        gray_frame,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(30, 30),
    )

    return faces