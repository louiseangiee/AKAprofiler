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
from Data import extract_text_from_directory, extract_entities_from_text


# Load environment variables
load_dotenv()

app = Flask(__name__)

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


db = client["aka_datathon"]
files_collection = db["PDFFiles_table"]
entities_collection = db["Entities_table"]
entities_summary_collection = db["Entity_summaries"]

# NLP Model
nlp = spacy.load("en_core_web_sm")

UPLOAD_FOLDER = "./uploads"
OUTPUT_FOLDER = "./output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER


# API Endpoint: Upload PDF
@app.route("/uploadPDF", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Extract text from PDF to get the number of pages
    doc = fitz.open(file_path)
    num_pages = doc.page_count

    # Save file info in MongoDB
    file_id = str(uuid.uuid4())
    file_entry = {
        "_id": file_id,
        "filename": filename,
        "filepath": file_path,
        "upload_time": datetime.now(),
        "pages": num_pages  # Placeholder for number of pages
    }
    files_collection.insert_one(file_entry)

    return jsonify({
        "message": "File uploaded successfully",
        "file_id": file_id,
        "filename": filename,
        "pages": num_pages,

    })

@app.route("/process_all_files", methods=["POST"])
def process_all_files():
    files = files_collection.find({"status": "uploaded"})
    processed_files = []
    
    for file_entry in files:
        file_id = file_entry["_id"]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_entry["filename"])
        output_folder = app.config['OUTPUT_FOLDER']
        
        # Extract text from PDF
        extract_text_from_directory(app.config['UPLOAD_FOLDER'], output_folder)
        
        # Extract entities
        entities = extract_entities_from_text(output_folder)
        
        # Save extracted entities in MongoDB as individual entries
        for entity in entities:
            entity_entry = {
                "_id": str(uuid.uuid4()),
                "file_id": file_id,
                "file_name": entity["file_name"],
                "entity": entity["entity"],
                "label": entity["label"]
            }
            entities_collection.insert_one(entity_entry)
        
        # Update file status to 'processed'
        files_collection.update_one(
            {"_id": file_id},
            {"$set": {"status": "processed", "processed_pages": 10}}
        )
        
        processed_files.append(file_id)
    
    return jsonify({
        "message": "All uploaded files processed successfully",
        "processed_files": processed_files
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

# API Endpoint: search for specific entities across all files
@app.route("/api/entities/search", methods=["GET"])
def search_entities():
    """Search for specific entities in the database based on a query term."""
    query = request.args.get("query", "").strip()

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    # Case-insensitive search for entities containing the query
    results = list(entities_collection.find(
        {"entity_text": {"$regex": query, "$options": "i"}},  # Case-insensitive regex search
        {"_id": 0, "file_id": 1, "filename": 1, "entity_text": 1, "label": 1, "frequency": 1}
    ))

    return jsonify({"query": query, "results": results})



if __name__ == "__main__":
    app.run(debug=True)
