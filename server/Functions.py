# Module imports
from collections import defaultdict
from spacy.util import compile_infix_regex
from itertools import combinations
import os
import requests
import fitz  # PyMuPDF
import spacy
import pandas as pd
import pymongo
import matplotlib.pyplot as plt
import seaborn as sns
import pdfplumber
import re
import spacy
import pandas as pd
import requests
import torch
import re
import hashlib
from typing import List, Dict
from spacy.tokens import Doc
from spacy.language import Language
from transformers import pipeline
from datasets import Dataset
from torch.utils.data import DataLoader
from transformers import Trainer, TrainingArguments
from sklearn.metrics import accuracy_score

# Helper functions
# 1. Helper Function to extract text from a single PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"  # Preserve line breaks
    return text

# 2. Helper Function to clean up extracted text
def clean_extracted_text(text):
    # Remove unwanted "K" characters (use a regex to remove K's in inappropriate places)
    cleaned_text = re.sub(r'K+', ' ', text)  # Replace multiple 'K's with a single space
    # Normalize spaces (e.g., remove extra spaces)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Replace multiple spaces with a single space
    # Remove spaces around punctuation (if necessary)
    cleaned_text = re.sub(r'\s([?.!,:;])', r'\1', cleaned_text)  # Remove space before punctuation
    # Clean up leading and trailing spaces
    cleaned_text = cleaned_text.strip()
    # Fix common misspellings and spacing errors
    cleaned_text = re.sub(r'\bosovo\b', 'Kosovo', cleaned_text)  # Fix "osovo" -> "Kosovo"
    return cleaned_text

# 3. Helper Function to filter out unwanted entities using regex
def is_valid_entity(entity_text, label):
    # Remove unwanted entities based on patterns
    if re.search(r'\d+[A-Za-z]+|\d+[A-Za-z]*\d+', entity_text):  # Match entities with digits and letters (e.g., 14KJanuaryK2005)
        return False
    if re.search(r'[^A-Za-z0-9\s]+', entity_text):  # Match entities with unusual symbols (e.g., "K   K REFERENCE")
        return False
    if label not in ["PERSON", "ORG"]:  # Exclude all labels except PERSON and ORG
        return False
    if len(entity_text.split()) > 1 and re.search(r'[^\w\s]', entity_text):  # e.g., special characters like '@' or '/'
        return False
    if re.search(r'K.*K', entity_text):  # Match entities containing multiple "K"s
        return False
    if len(entity_text.split()) == 1 and not entity_text.isalpha():  # single-word entities that are not purely alphabetic
        return False
    if len(entity_text) > 2 and entity_text.isalpha() and entity_text.lower() == entity_text:  # Remove single, concatenated long words
        return False
    if re.search(r'(?=.*[a-z])(?=.*[A-Z])', entity_text) and len(entity_text.split()) == 1:  # Exclude mixed case long words without spaces
        return False
    return True

# Main functions
# 1. Main Function to extract text from all PDFs in a directory
def extract_text_from_directory(directory_path, output_folder):
    if not os.path.exists(output_folder):  # Create output folder if it doesn't exist
        os.makedirs(output_folder)
    pdf_files = [f for f in os.listdir(directory_path) if f.endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found in the directory.")
        return
    for pdf_file in pdf_files:
        pdf_path = os.path.join(directory_path, pdf_file)
        print(f"Processing: {pdf_file}")
        # Extract and clean the text
        text = extract_text_from_pdf(pdf_path)
        cleaned_text = clean_extracted_text(text)
        # Save the cleaned text to a .txt file
        output_file = os.path.join(output_folder, f"{os.path.splitext(pdf_file)[0]}.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(cleaned_text)
        print(f"Saved cleaned text to: {output_file}")

# 2. Main Function to extract entities 
def extract_entities_from_text_files(folder_path, output_csv_path):
    nlp = spacy.load("en_core_web_sm")
    entity_data = []
    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            # Read the content of the file
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
            # Process the text with spaCy NLP model
            doc = nlp(text)
            # Extract and store entities for the current file
            for ent in doc.ents:
                entity_text = ent.text.replace('\n', ' ').strip()
                entity_text = entity_text.title()  # Normalize capitalisation
                if ent.label_ == "PERSON":
                    words = entity_text.split()
                    if len(words) > 2:
                        entity_text = " ".join(words[:2])
                if is_valid_entity(entity_text, ent.label_):
                    entity_data.append({
                        "File Name": filename,
                        "Entity": entity_text,
                        "Label": ent.label_,
                        "Frequency": 1,  # Placeholder for frequency
                        "Pages Found": [],  # Placeholder for pages found
                        "Relationships": []  # Placeholder for relationships
                    })
    # Create a DataFrame to organize the extracted data
    df = pd.DataFrame(entity_data)
    df = df.drop_duplicates(subset=["File Name", "Entity", "Label"])
    df.to_csv(output_csv_path, index=False)
    print(f"Entities extracted and saved to {output_csv_path}")
    return df.to_dict(orient='records')

# Main function 3 to extract entity pairs
def extract_entity_pairs_from_text_files(folder_path, output_csv_path):
    nlp = spacy.load("en_core_web_sm")
    print(folder_path)
    entity_pairs_data = []
    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            print(file_path)
            # Read the content of the file
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
            # Process the text with spaCy NLP model
            doc = nlp(text)
            unique_entities = set()
            for ent in doc.ents:
                entity_text = ent.text.replace('\n', ' ').strip()
                entity_text = entity_text.title()
                if ent.label_ == "PERSON":
                    words = entity_text.split()
                    if len(words) > 2:
                        entity_text = " ".join(words[:2])
                    if is_valid_entity(entity_text, ent.label_) and entity_text not in unique_entities:
                        unique_entities.add((entity_text, ent.label_))
            # Generate entity pairs
            entity_pairs = list(combinations(unique_entities, 2))
            # Add entity pairs to the list
            for entity1, entity2 in entity_pairs:
                entity_pairs_data.append({
                    "Entity 1": entity1[0],
                    "Type 1": entity1[1],
                    "Entity 2": entity2[0],
                    "Type 2": entity2[1],
                    "Relationship": "Unknown"
                })
    df_pairs = pd.DataFrame(entity_pairs_data)
    df_pairs.to_csv(output_csv_path, index=False)
    print(f"Entity pairs extracted and saved to {output_csv_path}")

# Main function 4 to predict relationships between entities
def predict_relationships_from_entity_pairs(entity_pairs_csv, output_csv_path):
    """Predict relationships from entity pairs using the REBEL model and save results to a CSV."""
    # Define DEVICE variable
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Load Rebel model from Hugging Face
    rebel_pipeline = pipeline("text2text-generation", model="Babelscape/rebel-large", device=0 if torch.cuda.is_available() else -1)
    # Register custom spaCy extension
    if not Doc.has_extension("rel"):
        Doc.set_extension("rel", default={})

    def call_wiki_api(item):
        """Fetches Wikidata ID for an entity."""
        try:
            url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={item}&language=en&format=json"
            data = requests.get(url).json()
            return data['search'][0]['id']
        except:
            return 'id-less'

    def set_annotations(doc: Doc, triplets: List[Dict]):
        """Annotates document with extracted relationships."""
        for triplet in triplets:
            if triplet['head'] == triplet['tail']:
                continue  # Remove self-loops
            head_span = re.search(triplet["head"], doc.text)
            tail_span = re.search(triplet["tail"], doc.text)
            if not head_span or not tail_span:
                continue
            index = hashlib.sha1("".join([triplet['head'], triplet['tail'], triplet['type']]).encode('utf-8')).hexdigest()
            if index not in doc._.rel:
                doc._.rel[index] = {
                    "relation": triplet["type"],
                    "head_span": {'text': triplet['head'], 'id': call_wiki_api(triplet['head'])},
                    "tail_span": {'text': triplet['tail'], 'id': call_wiki_api(triplet['tail'])}
                }

    # Load spaCy model
    nlp = spacy.load('en_core_web_sm', disable=['ner', 'lemmatizer', 'attribute_rules', 'tagger'])

    @Language.component("rebel")
    def rebel_component(doc):
        """Custom spaCy component for relation extraction."""
        text = doc.text
        results = rebel_pipeline(text, max_length=512, truncation=True)
        extracted_relations = {}

        for result in results:
            relation_phrase = result["generated_text"].strip()
            match = re.match(r'^(.+?) (?:is|are) (.+?) (.+)$', relation_phrase)
            if match:
                head, tail, relation = match.groups()
                extracted_relations[hashlib.sha1(relation.encode()).hexdigest()] = {
                    "head": head.strip(),
                    "tail": tail.strip(),
                    "type": relation.strip()
                }
            else:
                match = re.match(r'^(.+?) (.+) (.+?)$', relation_phrase)
                if match:
                    head, relation, tail = match.groups()
                    extracted_relations[hashlib.sha1(relation.encode()).hexdigest()] = {
                        "head": head.strip(),
                        "tail": tail.strip(),
                        "type": relation.strip()
                    }

        doc._.rel = extracted_relations
        return doc

    # Add the custom component to spaCy
    nlp.add_pipe("rebel", last=True)

    def load_csv(file_path):
        """Loads entity pairs from a CSV file."""
        df = pd.read_csv(file_path)
        print(f"Original columns: {df.columns.tolist()}")  # Debugging check
        # Ensure we only have the correct 5 columns
        df = df.iloc[:, :5]
        df.columns = ["Entity 1", "Type 1", "Entity 2", "Type 2", "Relationship"]
        return df

    def extract_relationships(df):
        """Uses Rebel to extract relationships for given entity pairs."""
        for index, row in df.iterrows():
            entity1, entity2, relationship = row["Entity 1"], row["Entity 2"], row["Relationship"]
            # Only process rows where the relationship is "Unknown"
            if relationship == "Unknown":
                wiki_id1 = call_wiki_api(entity1)
                wiki_id2 = call_wiki_api(entity2)
                query_text = f"{entity1} and {entity2} relationship"
                doc = nlp(query_text)
                if doc._.rel:
                    extracted_relation = list(doc._.rel.values())[0]["type"]
                    print(f"Found relation: {extracted_relation}")
                    df.at[index, "Relationship"] = extracted_relation  # Update dataframe
        return df

    # Load data and process relationships
    df = load_csv(entity_pairs_csv)
    df = extract_relationships(df)
    print(df.head())
    # Save updated data
    df.to_csv(output_csv_path, index=False)
    print(f"Updated relationships saved to {output_csv_path}")