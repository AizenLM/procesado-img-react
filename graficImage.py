from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import numpy as np
import cv2  # Usado para manipular imágenes
import os
import matplotlib.pyplot as plt
from PIL import Image
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import time