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
