Here’s a comprehensive README for the **SMART Face Recognition Attendance System** project. It follows best practices and includes sections on project description, setup, usage, and project organization.

---

# SMART Face Recognition System

SMART (Student Management and Attendance Recognition Technology) is an advanced face recognition system that automates student attendance tracking. Leveraging real-time face detection and user management, SMART enables secure and accurate attendance logging, with comprehensive reporting options.

This project uses Next.js for the frontend and Flask for the backend, integrating AWS Rekognition for face recognition and MongoDB for data storage.

## Table of Contents
1. [Project Description](#project-description)
2. [Features](#features)
3. [Getting Started](#getting-started)
4. [Project Structure](#project-structure)
5. [API Endpoints](#api-endpoints)
6. [Deployment](#deployment)

## Project Description

The SMART Face Recognition System simplifies attendance management by:
- Detecting and identifying students' faces in real-time
- Automating attendance logging
- Providing detailed reports for monitoring attendance trends

### Features
- **Real-Time Face Recognition**: Identify registered users based on face images.
- **Attendance Tracking**: Log attendance records with precise timestamps.
- **Comprehensive Reports**: Export attendance data over specified time periods.
- **User Management**: Register new users, view users, delete users, and manage attendance history.

---

## Getting Started

### Prerequisites
1. **Node.js and npm** - Install [Node.js](https://nodejs.org/) for the frontend.
2. **Python 3.x** - Install [Python](https://www.python.org/) for the backend.
3. **MongoDB** - Set up MongoDB for storing user data and attendance logs.
4. **AWS Rekognition** - Set up AWS Rekognition for face recognition.

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd SMART-face-recognition-system
   ```

2. **Frontend (Next.js)**:
   - Install dependencies:
     ```bash
     npm install
     ```
   - Start the development server:
     ```bash
     npm run dev
     ```
   - Open [http://localhost:3000](http://localhost:3000) to view in the browser.

3. **Backend (Flask)**:
   - Set up a virtual environment:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate  # On Windows, use .venv\Scripts\activate
     ```
   - Install backend dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Run the Flask server:
     ```bash
     flask run
     ```

---

## Project Structure

Here is an overview of the main directories and files in this project:

```plaintext
SMART-face-recognition-system/
├── app/                   # Frontend pages and global styles
│   ├── favicon.ico
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── components/ui          # Reusable UI components
│   ├── button.tsx
│   ├── calendar.tsx
│   ├── card.tsx
│   ├── dialog.tsx
│   ├── input.tsx
│   └── tabs.tsx
├── migrations/            # Database migration scripts (Alembic)
│   ├── README.md
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 689b5bc61b9d_initial_migration.py
├── public/                # Static assets for the frontend
│   ├── next.svg
│   └── vercel.svg
├── .gitattributes
├── .gitignore
├── Procfile
├── README.md              # Project documentation
├── app.py                 # Flask application file
├── components.json
├── next-env.d.ts
├── next.config.js         # Next.js configuration
├── package-lock.json
├── package.json           # Frontend dependencies
├── postcss.config.js
├── tailwind.config.js     # Tailwind CSS configuration
├── tailwind.config.ts
└── tsconfig.json          # TypeScript configuration
```

---

## API Endpoints

The backend provides the following endpoints:

### User Registration
- **Endpoint**: `/register`
- **Method**: `POST`
- **Description**: Registers a new user with face images.

### Face Recognition
- **Endpoint**: `/predict`
- **Method**: `POST`
- **Description**: Identifies a user based on a face image.

### Log Attendance
- **Endpoint**: `/attendance`
- **Method**: `POST`
- **Description**: Logs attendance for a recognized user.

### Attendance Report
- **Endpoint**: `/attendance_report`
- **Method**: `GET`
- **Description**: Generates a report of attendance over a date range.

### User Management
- **List Users**: `/list_users` - Retrieves a list of registered users.
- **Delete User**: `/delete_user` - Deletes a user and their associated attendance records.

---

## Deployment

The recommended deployment platform for the frontend is **Vercel**. For more details, see the [Next.js deployment documentation](https://nextjs.org/docs/deployment).

For deploying the backend, a server or cloud service such as AWS or Heroku is recommended.

----
