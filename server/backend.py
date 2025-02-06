from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import fitz  
import spacy
import uuid
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from Functions import extract_text_from_directory, extract_entities_from_text
import shutil
from flask_cors import CORS


# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # <--- This allows cross-origin requests for all routes

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

UPLOAD_FOLDER = "./LocalDB/uploads"
OUTPUT_FOLDER = "./LocalDB/output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER


def cleanup_folders(folders):
    """Deletes all files in the specified folders"""
    for folder in folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # Delete file
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # Delete folder
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")



# API Endpoint: Upload PDF
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist("file")
    if not files:
        return jsonify({"error": "No selected files"}), 400

    uploaded_files_info = []

    for file in files:
        if file.filename == "":
            continue

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
            "pages": num_pages
        }
        files_collection.insert_one(file_entry)

        uploaded_files_info.append({
            "file_id": file_id,
            "filename": filename,
            "pages": num_pages
        })

    # Extract entities from uploaded files
    extract_text_from_directory(app.config['UPLOAD_FOLDER'], OUTPUT_FOLDER)

    # Extract entities
    entities = extract_entities_from_text(OUTPUT_FOLDER)
    print(entities)

    # Save extracted entities in MongoDB
    for entity in entities:
        entity_entry = {
            "_id": str(uuid.uuid4()),
            "file_id": file_id,
            "file_name": entity["file_name"],
            "entity": entity["entity"],
            "label": entity["label"],
            "frequency": entity["frequency"],  # Number of times the entity is mentioned
            "pagesFoundIn": entity["pagesFound"],  # Pages where the entity is mentioned
            "relationships": entity["relationships"]  # Placeholder for relationships
        }
        entities_collection.insert_one(entity_entry)

    

    return jsonify({
        "message": "Files uploaded successfully",
        "files": uploaded_files_info
    })



# API Endpoint: Get Extracted Entities by file_id
@app.route("/entities/file/<file_id>", methods=["GET"])
def get_entities_by_file_id(file_id):
    entities = list(entities_collection.find({"file_id": file_id}, {"_id": 0}))
    return jsonify({"file_id": file_id, "entities": entities}
                   )

# API Endpoint: Get all people entities
@app.route("/entities/people", methods=["GET"])
def get_people_entities():
    people_entities = list(entities_collection.find({"label": "PERSON"}, {"_id": 0}))
    return jsonify({"people_entities": people_entities})

@app.route("/entities/name/<entity_name>", methods=["GET"])
def get_entities_by_entity_name(entity_name):
    if not entity_name:
        return jsonify({"error": "Entity name is required"}), 400

    try:
        entities = list(entities_collection.find(
            {"entity": {"$regex": f"^{entity_name}$", "$options": "i"}},  # Case-insensitive search
            {"_id": 0}
        ))

        if not entities:
            return jsonify({"message": f"No entities found for '{entity_name}'"}), 404

        return jsonify({"entity_name": entity_name, "entities": entities})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# API Endpoint: List Uploaded Files
@app.route("/files", methods=["GET"])
def list_files():
    files = list(files_collection.find({}, {"_id": 0, "text": 0}))
    return jsonify({"files": files})

# API Endpoint: Get file by File_name
@app.route("/files/<file_name>", methods=["GET"])
def get_file_by_file_name(file_name):
    file = files_collection.find_one({"filename": file_name}, {"_id": 0, "text": 0})
    if file:
        return jsonify({"file": file})
    else:
        return jsonify({"error": "File not found"}), 404


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

# Get all relationships (new)
@app.route("/relationships", methods=["GET"])
def get_all_relationships():
    # Fetch all relationships from the relationships collection
    relationships = list(entities_collection.find({}, {"_id": 0}))  
    return jsonify({"relationships": relationships})


# Get relationships if its in entity 1 or 2 (new) 
@app.route("/relationships/entity/<entity_name>", methods=["GET"])
def get_relationships_by_entity(entity_name):
    if not entity_name:
        return jsonify({"error": "Entity name is required"}), 400

    try:
        # Find relationships where the entity appears in either 'entity_1' or 'entity_2'
        relationships = list(entities_collection.find(
            {
                "$or": [
                    {"entity_1": {"$regex": f"^{entity_name}$", "$options": "i"}},  # Case-insensitive search for entity_1
                    {"entity_2": {"$regex": f"^{entity_name}$", "$options": "i"}}   # Case-insensitive search for entity_2
                ]
            },
            {"_id": 0}  # Exclude the _id field in the response
        ))

        if not relationships:
            return jsonify({"message": f"No relationships found for entity '{entity_name}'"}), 404

        return jsonify({"entity_name": entity_name, "relationships": relationships})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)
