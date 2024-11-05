from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_pymongo import PyMongo
import boto3
import os
import datetime
from dotenv import load_dotenv
import csv
import io

# Load environment variables from .env file (only in development)
if os.getenv('FLASK_ENV') == 'development':
    load_dotenv()

app = Flask(__name__)

# Configure CORS
CORS(app, resources={r"/*": {"origins": "*"}})  # For production, replace "*" with your frontend URL

# Configure MongoDB URI
app.config["MONGO_URI"] = os.getenv('MONGO_URI')
mongo = PyMongo(app)

# Initialize Rekognition client with environment variables
rekognition = boto3.client(
    'rekognition',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

# Collection ID
COLLECTION_ID = 'my_face_collection'

# Create the collection if it doesn't exist
def create_collection():
    try:
        existing_collections = rekognition.list_collections()['CollectionIds']
        if COLLECTION_ID not in existing_collections:
            rekognition.create_collection(CollectionId=COLLECTION_ID)
            print(f"Created collection {COLLECTION_ID}")
        else:
            print(f"Collection {COLLECTION_ID} already exists")
    except Exception as e:
        print(f"Error creating collection: {e}")

create_collection()

# API Endpoints

@app.route('/register', methods=['POST'])
def register():
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    if 'images' not in request.files:
        return jsonify({'error': 'No images provided'}), 400

    # Check if user already exists
    existing_user = mongo.db.users.find_one({'user_id': user_id})
    if existing_user:
        return jsonify({'error': 'User ID already exists'}), 400

    images = request.files.getlist('images')

    face_ids = []
    for image in images:
        image_bytes = image.read()
        # Index the face
        try:
            response = rekognition.index_faces(
                CollectionId=COLLECTION_ID,
                Image={'Bytes': image_bytes},
                ExternalImageId=user_id,  # Associate the face with the user_id
                DetectionAttributes=['DEFAULT'],
                MaxFaces=1,  # Assume one face per image
                QualityFilter='AUTO'
            )
        except Exception as e:
            return jsonify({'error': f"AWS Rekognition error: {str(e)}"}), 500

        face_records = response.get('FaceRecords', [])
        if face_records:
            for faceRecord in face_records:
                face_id = faceRecord['Face']['FaceId']
                face_ids.append(face_id)
        else:
            return jsonify({'error': 'No face detected in one of the images'}), 400

    # Add user to the database
    mongo.db.users.insert_one({
        'user_id': user_id,
        'created_at': datetime.datetime.utcnow()
    })

    return jsonify({'message': 'User registered successfully', 'face_ids': face_ids}), 200

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image = request.files['image']
    image_bytes = image.read()

    # Search for matching faces
    try:
        response = rekognition.search_faces_by_image(
            CollectionId=COLLECTION_ID,
            Image={'Bytes': image_bytes},
            MaxFaces=1,
            FaceMatchThreshold=80
        )
    except Exception as e:
        return jsonify({'error': f"AWS Rekognition error: {str(e)}"}), 500

    face_matches = response.get('FaceMatches', [])
    if face_matches:
        best_match = face_matches[0]
        user_id = best_match['Face']['ExternalImageId']
        similarity = best_match['Similarity']
        return jsonify({'user_id': user_id, 'similarity': similarity}), 200
    else:
        return jsonify({'message': 'No matching faces found'}), 404

@app.route('/attendance', methods=['POST'])
def attendance():
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    # Check if user exists
    user = mongo.db.users.find_one({'user_id': user_id})
    if not user:
        return jsonify({'error': 'User does not exist'}), 400

    timestamp = datetime.datetime.utcnow()
    attendance_record = {
        'user_id': user_id,
        'timestamp': timestamp
    }
    result = mongo.db.attendance.insert_one(attendance_record)
    attendance_record['_id'] = str(result.inserted_id)

    return jsonify({'message': 'Attendance logged', 'attendance_record': attendance_record}), 200

@app.route('/attendance_report', methods=['GET'])
def attendance_report():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if not start_date_str or not end_date_str:
        return jsonify({'error': 'start_date and end_date are required in YYYY-MM-DD format'}), 400

    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d') + datetime.timedelta(days=1)
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    # Query attendance records
    records_cursor = mongo.db.attendance.find({
        'timestamp': {'$gte': start_date, '$lt': end_date}
    })

    records = list(records_cursor)

    if not records:
        return jsonify({'message': 'No attendance records found for the specified period'}), 404

    # Create CSV
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'User ID', 'Timestamp'])
    for record in records:
        cw.writerow([str(record['_id']), record['user_id'], record['timestamp'].isoformat()])

    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)

    filename = f"attendance_report_{start_date_str}_to_{end_date_str}.csv"

    return send_file(output,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=filename)

@app.route('/list_users', methods=['GET'])
def list_users():
    users_cursor = mongo.db.users.find()
    users_list = [{'user_id': user['user_id'], 'created_at': user['created_at'].isoformat()} for user in users_cursor]
    return jsonify({'users': users_list}), 200

@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({'error': 'user_id is required in the JSON payload'}), 400

    user_id = data['user_id']
    user = mongo.db.users.find_one({'user_id': user_id})
    if not user:
        return jsonify({'error': 'User does not exist'}), 404

    # Delete user
    mongo.db.users.delete_one({'user_id': user_id})

    # Delete associated attendance records
    mongo.db.attendance.delete_many({'user_id': user_id})

    # Remove faces from Rekognition
    try:
        # List all faces in the collection
        paginator = rekognition.get_paginator('list_faces')
        face_ids_to_delete = []
        for page in paginator.paginate(CollectionId=COLLECTION_ID, MaxResults=1000):
            for face in page['Faces']:
                if face.get('ExternalImageId') == user_id:
                    face_ids_to_delete.append(face.get('FaceId'))

        # Delete faces
        if face_ids_to_delete:
            rekognition.delete_faces(
                CollectionId=COLLECTION_ID,
                FaceIds=face_ids_to_delete
            )
    except Exception as e:
        return jsonify({'error': f'User deleted, but failed to remove faces: {str(e)}'}), 500

    return jsonify({'message': 'User and associated records deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
