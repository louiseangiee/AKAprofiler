from bson import ObjectId
from nanoid import generate
from flask import Flask, request, jsonify
import pandas as pd
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import fitz  # PyMuPDF
import spacy
import uuid
from datetime import datetime
from Functions import extract_entity_pairs_from_text_files, extract_text_from_directory, extract_entities_from_text_files, predict_relationships_from_entity_pairs
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
files_collection = db["PDFFiles"]
entities_collection = db["Entities"]
relationship_collection = db["Relationships"]

# NLP Model
nlp = spacy.load("en_core_web_sm")

# Define a base directory for storage
BASE_DIR = os.path.abspath("./LocalDB")

# Define folder paths
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER_TXT = os.path.join(BASE_DIR, "output_txt")

# Define file paths
OUTPUT_FOLDER_CSV_ENTITIES = os.path.join(BASE_DIR, "entity.csv")
OUTPUT_FOLDER_CSV_ENTITIES_PAIR = os.path.join(BASE_DIR, "entitypairs.csv")
OUTPUT_FOLDER_CSV_COMPLETE = os.path.join(BASE_DIR, "entitypairsComplete.csv")

# Ensure necessary folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER_TXT, exist_ok=True)

# Configure Flask app paths
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER_TXT"] = OUTPUT_FOLDER_TXT

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
        with fitz.open(file_path) as doc:
            num_pages = len(doc)
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
    # # Extract entities from uploaded files (ACTUAL - UNCOMMENT LATER)
    # extract_text_from_directory(app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER_TXT'])
    # # Extract entities
    # print(app.config['OUTPUT_FOLDER_TXT'])
    # print(OUTPUT_FOLDER_CSV_ENTITIES)
    # entities = extract_entities_from_text_files(app.config['OUTPUT_FOLDER_TXT'], OUTPUT_FOLDER_CSV_ENTITIES)
    # extract_entity_pairs_from_text_files(app.config['OUTPUT_FOLDER_TXT'], OUTPUT_FOLDER_CSV_ENTITIES_PAIR)
    # relationships = predict_relationships_from_entity_pairs(OUTPUT_FOLDER_CSV_ENTITIES_PAIR, OUTPUT_FOLDER_CSV_COMPLETE)
    
   #Use Preloaded CSV files (test)
    entities = pd.read_csv(OUTPUT_FOLDER_CSV_ENTITIES)
    relationships = pd.read_csv(OUTPUT_FOLDER_CSV_COMPLETE)

    entities.head()
    relationships.head()


     # Save extracted entities in MongoDB
    # Convert DataFrames to lists of dictionaries for easier processing
    entities_list = entities.to_dict(orient="records")
    relationships_list = relationships.to_dict(orient="records")

    # Process entities and relationships
    for entity in entities_list:
        # Create a list to store relationship IDs for this entity
        relationship_ids = []

        # Iterate through all relationships to find those related to this entity
        for relation in relationships_list:
            # Check if the current entity is involved in the relationship (as Entity 1 or Entity 2)
            if entity["Entity"] == relation["Entity 1"] or entity["Entity"] == relation["Entity 2"]:
                # Generate a unique ID for the relationship
                full_uuid = str(uuid.uuid4())
                relationship_id = generate(size=8)  # Generate an 8-character ID  
                relationship_ids.append(relationship_id)

                # Insert the relationship entry into the relationship_collection
                relationship_entry = {
                    "_id": relationship_id,
                    "entity_1_name": relation["Entity 1"],
                    "entity_1_type": relation["Type 1"],
                    "entity_2_name": relation["Entity 2"],
                    "entity_2_type": relation["Type 2"],
                    "relationship": relation["Relationship"]
                }
                relationship_collection.insert_one(relationship_entry)

        # Create the entity_entry with the relationships array
        entity_entry = {
            "_id": str(uuid.uuid4()),
            "file_id": file_id,
            "file_name": entity["File Name"],
            "entity": entity["Entity"],
            "label": entity["Label"],
            "frequency": 0,  # You can calculate frequency later if needed
            "relationships": relationship_ids  # Array of relationship IDs
        }

        # Insert the entity_entry into the entities_collection
        entities_collection.insert_one(entity_entry)
    
    return jsonify({
        "message": "Files uploaded successfully",
        "files": uploaded_files_info
    })

# API Endpoint: Get Extracted Entities by file_id
@app.route("/entities/file/<file_id>", methods=["GET"])
def get_entities_by_file_id(file_id):
    entities = list(entities_collection.find({"file_id": file_id}, {"_id": 0}))
    return jsonify({"file_id": file_id, "entities": entities})

# API Endpoint: Get all people entities
@app.route("/entities/people", methods=["GET"])
def get_people_entities():
    people_entities = list(entities_collection.find({"label": "PERSON"}, {"_id": 0}))
    return jsonify({"people_entities": people_entities})

@app.route("/entities", methods=["GET"])
def get_entities():
    entities = list(entities_collection.find({}, {"_id": 0}))
    return jsonify({"entities": entities})

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
    relationships = list(relationship_collection.find({}, {"_id": 0}))  
    return jsonify({"relationships": relationships})

# Get relationships by relationship ID (new)
@app.route("/relationships/<relationship_id>", methods=["GET"])
def get_relationship_by_id(relationship_id):
    if not relationship_id:
        return jsonify({"error": "Relationship ID is required"}), 400
    try:
        # Find the relationship by its _id
        relationship = relationship_collection.find_one(
            {"_id": relationship_id},
            {"_id": 0}  # Exclude the _id field in the response
        )

        if not relationship:
            return jsonify({"message": f"No relationship found with ID '{relationship_id}'"}), 404
        return jsonify({"relationship": relationship})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get relationships if its in entity 1 or 2 (new) 
@app.route("/relationships/entity/<entity_name>", methods=["GET"])
def get_relationships_by_entity(entity_name):
    if not entity_name:
        return jsonify({"error": "Entity name is required"}), 400
    try:
        # Find relationships where the entity appears in either 'entity_1' or 'entity_2'
        relationships = list(relationship_collection.find(
            {
                "$or": [
                    {"entity_1_name": {"$regex": f"^{entity_name}$", "$options": "i"}},  # Case-insensitive search for entity_1
                    {"entity_2_name": {"$regex": f"^{entity_name}$", "$options": "i"}}   # Case-insensitive search for entity_2
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