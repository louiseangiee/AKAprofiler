from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import fitz  # PyMuPDF
import spacy
import uuid
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from Data import extract_text_from_pdf, extract_entities_from_text


# Load environment variables
load_dotenv()

app = Flask(__name__)

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

db = client["pdf_processor"]
files_collection = db["files"]
entities_collection = db["entities"]

# NLP Model
nlp = spacy.load("en_core_web_sm")

UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# API Endpoint: Upload PDF
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Extract text from PDF
    text = extract_text_from_pdf(file_path)
    
    # Extract entities
    entities = extract_entities(text)
    
    # Save file info in MongoDB
    file_id = str(uuid.uuid4())
    file_entry = {
        "file_id": file_id,
        "filename": filename,
        "uploaded_at": datetime.utcnow(),
        "text": text,
    }
    files_collection.insert_one(file_entry)
    
    # Save extracted entities in MongoDB
    if entities:
        entities_collection.insert_many(
            [{"file_id": file_id, **entity} for entity in entities]
        )
    
    return jsonify({
        "message": "File uploaded and processed successfully",
        "file_id": file_id,
        "entities": entities
    })

# API Endpoint: Get Extracted Entities
@app.route("/entities/<file_id>", methods=["GET"])
def get_entities(file_id):
    entities = list(entities_collection.find({"file_id": file_id}, {"_id": 0}))
    return jsonify({"file_id": file_id, "entities": entities})

# API Endpoint: List Uploaded Files
@app.route("/files", methods=["GET"])
def list_files():
    files = list(files_collection.find({}, {"_id": 0, "text": 0}))
    return jsonify({"files": files})

if __name__ == "__main__":
    app.run(debug=True)
