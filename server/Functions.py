# Module imports
# pip install PyPDF2
# pip install pytesseract
# pip install pdfminer.six
from collections import defaultdict
import os
import requests
import fitz
import spacy
import pandas as pd
from itertools import combinations
import pymongo
from spacy.util import compile_infix_regex
import matplotlib.pyplot as plt
import seaborn as sns
from testModelPrediction import predict_relationship_from_entities
import pdfplumber
import re

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
            with open(file_path, "r") as file:
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
                    entity_data.append([filename, entity_text, ent.label_])

    # Create a DataFrame to organize the extracted data
    df = pd.DataFrame(entity_data, columns=["File Name", "Entity", "Label"])
    df = df.drop_duplicates()
    df.to_csv(output_csv_path, index=False)
    print(f"Entities extracted and saved to {output_csv_path}")


# Main function 3 to extract entity pairs
def extract_entity_pairs_from_text_files(folder_path, output_csv_path):
    nlp = spacy.load("en_core_web_sm")
    entity_pairs_data = []

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)

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
                    unique_entities.add(entity_text)

            # Generate entity pairs
            entity_pairs = list(itertools.combinations(unique_entities, 2))

            # Add entity pairs to the list
            for entity1, entity2 in entity_pairs:
                entity_pairs_data.append([filename, entity1, entity2, "Unknown"])

    df_pairs = pd.DataFrame(entity_pairs_data, columns=["File Name", "Entity 1", "Entity 2", "Relationship"])
    df_pairs.to_csv(output_csv_path, index=False)
    print(f"Entity pairs extracted and saved to {output_csv_path}")



# # Old Function to extract text from all PDFs in a directory
# def extract_text_from_directory(directory_path, output_folder):
#     if not os.path.exists(output_folder):  
#         os.makedirs(output_folder)

#     pdf_text_data = {}  # Stores extracted text per file

#     for pdf_file in os.listdir(directory_path):
#         if pdf_file.endswith(".pdf"):
#             pdf_path = os.path.join(directory_path, pdf_file)
#             print(f"Processing: {pdf_file}")

#             # Open PDF and extract text per page
#             doc = fitz.open(pdf_path)
#             text_per_page = {}

#             for page_num in range(len(doc)):
#                 text = doc[page_num].get_text()
#                 text_per_page[page_num + 1] = text  # Store text by page number

#             pdf_text_data[pdf_file] = text_per_page

#             # Save full extracted text to a .txt file
#             full_text = "\n".join(text_per_page.values())
#             output_file = os.path.join(output_folder, f"{os.path.splitext(pdf_file)[0]}.txt")
#             with open(output_file, "w", encoding="utf-8") as f:
#                 f.write(full_text)
#             print(f"Saved extracted text to: {output_file}")

#     return pdf_text_data  # Returns extracted text by file & page

# Old function to extract entities

# def extract_entities_from_text(output_folder):
#     # Check if output folder exists
#     if not os.path.exists(output_folder) or not os.path.isdir(output_folder):
#         print(f"Invalid folder path: {output_folder}")
#         return []  # Return an empty list if the folder is invalid

#     # Load SpaCy model and configure tokenizer
#     nlp = spacy.load("en_core_web_sm")
#     infixes = list(nlp.Defaults.infixes)
#     infixes.append(r'k')
#     infix_re = compile_infix_regex(infixes)
#     nlp.tokenizer = Tokenizer(nlp.vocab, infix_finditer=infix_re.finditer)

#     entity_data = []

#     # Process each text file in the output folder
#     for filename in os.listdir(output_folder):
#         if filename.endswith(".txt"):
#             file_path = os.path.join(output_folder, filename)

#             # Read file content
#             with open(file_path, "r", encoding="utf-8") as file:
#                 text = file.read()

#             doc = nlp(text)
#             cleaned_text = ' '.join([token.text for token in doc if token.text != 'K'])
#             doc_cleaned = nlp(cleaned_text)

#             # Count entity occurrences
#             entity_count = defaultdict(lambda: {"count": 0, "pages": set()})

#             # Simulate page numbers by splitting text into chunks
#             page_size = 1000  # Approximate characters per page
#             pages = [cleaned_text[i:i+page_size] for i in range(0, len(cleaned_text), page_size)]

#             for page_num, page_text in enumerate(pages, start=1):
#                 doc_page = nlp(page_text)
#                 for ent in doc_page.ents:
#                     clean_entity = ent.text.strip().replace("\n", " ")  # Clean entity text
#                     entity_count[clean_entity]["count"] += 1
#                     entity_count[clean_entity]["pages"].add(page_num)

#             # Store entity data
#             for entity_text, data in entity_count.items():
#                 entity_data.append({
#                     "file_name": filename,
#                     "entity": entity_text,
#                     "label": nlp(entity_text).ents[0].label_ if nlp(entity_text).ents else "UNKNOWN",
#                     "frequency": data["count"],
#                     "pagesFound": sorted(data["pages"]),
#                     "relationships": []  # Placeholder for relationships
#                 })

#     if not entity_data:
#         print("No entities were extracted.")
#         return []  # Return an empty list if no entities were found

#     # Convert entity data to DataFrame
#     df = pd.DataFrame(entity_data)

#     # Clean and preprocess the extracted entity data
#     df = df[df['entity'].str.strip() != '']
#     df['entity'] = df['entity'].str.replace(r'\n', ' ', regex=True).str.strip()
#     df['entity'] = df['entity'].apply(lambda x: ''.join(e for e in x if e.isalnum() or e.isspace()))
#     df['entity'] = df['entity'].str.lower()
#     df['label'] = df['label'].str.upper()

#     # Remove duplicates (this should now work without any list issues)
#     df = df.drop_duplicates(subset=['file_name', 'entity', 'label'])

#     # Process and filter people entities
#     grouped = df.groupby('file_name')
#     entity_pairs = []

#     # Generate entity pairs for each file
#     for file_name, group in grouped:
#         person_entities = group[group['label'] == 'PERSON']
        
#         # Create all unique combinations of entity pairs where one is 'PERSON'
#         for entity1, entity2 in combinations(person_entities['entity'], 2):
#             entity_pairs.append({'file_name': file_name, 'entity1': entity1, 'entity2': entity2})

#     # Convert the list to a DataFrame
#     pairs_df = pd.DataFrame(entity_pairs)

#     # Save the entity pairs to a new CSV file
#     pairs_df.to_csv('entity_pairs.csv', index=False)
#     print("Entity pairs generated and saved to entity_pairs.csv!")

#     # Determine relationships and update entity data
#     # Separate the relationships to prevent issues with unhashable types
#     relationships = []

#     for index, row in pairs_df.iterrows():
#         relationship = predict_relationship_from_entities(row['entity1'], row['entity2'])
#         relationships.append({
#             "file_name": row['file_name'],
#             "entity1": row['entity1'],
#             "entity2": row['entity2'],
#             "relationship": relationship
#         })

#     # Now update the entity data with relationships
#     for entity in entity_data:
#         for rel in relationships:
#             if entity['file_name'] == rel['file_name'] and entity['entity'] in [rel['entity1'], rel['entity2']]:
#                 entity['relationships'].append({
#                     "entity1": rel['entity1'],
#                     "entity2": rel['entity2'],
#                     "relationship": rel['relationship']
#                 })

#     # Return the entity data
#     return entity_data

