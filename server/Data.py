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
import pymongo
from PyPDF2 import PdfReader
from spacy.tokenizer import Tokenizer
from spacy.util import compile_infix_regex
import matplotlib.pyplot as plt
import seaborn as sns


# Insert entity data into the Entities database
def insert_entities_into_db(entity_data, entities_collection):
    """ Insert extracted entity data into the MongoDB Entities collection. """
    if entity_data:
        try:
            entities_collection.insert_many(entity_data)
            print("Entity data inserted into Entities database.")
        except pymongo.errors.PyMongoError as e:
            print(f"MongoDB Error while inserting entities: {e}")
    else:
        print("No entity data to insert.")

# Insert PDF data into the Files database
def insert_pdf_data_into_db(pdf_data, files_collection):
    """ Insert PDF data (file name and extracted text) into the MongoDB Files collection. """
    if pdf_data:
        try:
            files_collection.insert_many(pdf_data)
            print("PDF data inserted into Files database.")
        except pymongo.errors.PyMongoError as e:
            print(f"MongoDB Error while inserting PDF data: {e}")
    else:
        print("No PDF data to insert.")

# Insert entity summary into the Entity Summary database
def insert_entity_summary(entity_summary, entity_summary_collection):
    """ Insert entity summary data into the MongoDB Entity Summary collection. """
    if entity_summary:
        try:
            entity_summary_collection.insert_one(entity_summary)
            print("Entity summary inserted into Entity Summary database.")
        except pymongo.errors.PyMongoError as e:
            print(f"MongoDB Error while inserting entity summary: {e}")
    else:
        print("No entity summary data to insert.")


# Function to fetch data from an API
def fetch_data_from_api(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()  # Assuming the response is JSON
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None

# Function to upload data to MongoDB
def upload_to_mongo(data, collection):
    if data:
        collection.insert_many(data)
        print("Data uploaded to MongoDB.")
    else:
        print("No data to upload.")

# Function to extract text from a single PDF file
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from all PDFs in a directory
def extract_text_from_directory(directory_path, output_folder):
    if not os.path.exists(output_folder):  
        os.makedirs(output_folder)

    pdf_text_data = {}  # Stores extracted text per file

    for pdf_file in os.listdir(directory_path):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(directory_path, pdf_file)
            print(f"Processing: {pdf_file}")

            # Open PDF and extract text per page
            doc = fitz.open(pdf_path)
            text_per_page = {}

            for page_num in range(len(doc)):
                text = doc[page_num].get_text()
                text_per_page[page_num + 1] = text  # Store text by page number

            pdf_text_data[pdf_file] = text_per_page

            # Save full extracted text to a .txt file
            full_text = "\n".join(text_per_page.values())
            output_file = os.path.join(output_folder, f"{os.path.splitext(pdf_file)[0]}.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(full_text)
            print(f"Saved extracted text to: {output_file}")

    return pdf_text_data  # Returns extracted text by file & page



# Load spaCy NLP model with custom tokenizer
def load_spacy_model():
    """ Load spaCy model and set custom tokenizer for handling specific token delimiters. """
    nlp = spacy.load("en_core_web_sm")
    infixes = list(nlp.Defaults.infixes) + [r'k']  # Add custom infix 'k'
    infix_re = compile_infix_regex(infixes)
    nlp.tokenizer = Tokenizer(nlp.vocab, infix_finditer=infix_re.finditer)
    return nlp

# Entity Extraction
def extract_entities_from_text(output_folder):
    nlp = spacy.load("en_core_web_sm")
    infixes = list(nlp.Defaults.infixes)
    infixes.append(r'k')
    infix_re = compile_infix_regex(infixes)
    nlp.tokenizer = Tokenizer(nlp.vocab, infix_finditer=infix_re.finditer)

    entity_data = []

    # Process each text file in the output folder
    for filename in os.listdir(output_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(output_folder, filename)

            # Read file content
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()

            doc = nlp(text)
            cleaned_text = ' '.join([token.text for token in doc if token.text != 'K'])
            doc_cleaned = nlp(cleaned_text)

            # Count entity occurrences
            entity_count = defaultdict(lambda: {"count": 0, "pages": set()})

            # Simulate page numbers by splitting text into chunks
            page_size = 1000  # Approximate characters per page
            pages = [cleaned_text[i:i+page_size] for i in range(0, len(cleaned_text), page_size)]

            for page_num, page_text in enumerate(pages, start=1):
                doc_page = nlp(page_text)
                for ent in doc_page.ents:
                    entity_count[ent.text]["count"] += 1
                    entity_count[ent.text]["pages"].add(page_num)

            # Store entity data
            for entity_text, data in entity_count.items():
                entity_data.append({
                    "file_name": filename,
                    "entity": entity_text,
                    "label": nlp(entity_text).ents[0].label_ if nlp(entity_text).ents else "UNKNOWN",
                    "frequency": data["count"],
                    "pagesFound": sorted(data["pages"])
                })

    return entity_data

#find the frequency of each entity in the pdf file that they are located in

# Clean and preprocess entity data
def clean_entity_data(df):
    """ Clean and preprocess the extracted entity data. """
    df = df[df['Entity'].str.strip() != '']
    df['Entity'] = df['Entity'].str.replace(r'\n', ' ', regex=True).str.strip()
    df['Entity'] = df['Entity'].apply(lambda x: ''.join(e for e in x if e.isalnum() or e.isspace()))
    df['Entity'] = df['Entity'].str.lower()
    df['Label'] = df['Label'].str.upper()
    df = df.drop_duplicates()
    # Save to CSV
    df.to_csv("./extracted_entities_cleaned_v2.csv", index=False)
    # Print out the first few rows of the cleaned DataFrame to confirm the cleaning
    print("Cleaned Extracted Entities:")
    print(df.head())
    return df


# Visualize and analyze the entity data
def visualize_entity_data(df):
    """ Perform exploratory data analysis and visualizations on the entity data. """
    # Plot the top 20 most common entities
    top_entities = df['Entity'].value_counts().head(20)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_entities.values, y=top_entities.index, palette='viridis')
    plt.title("Top 20 Most Common Entities")
    plt.xlabel("Frequency")
    plt.ylabel("Entity")
    plt.show()

    # Plot the frequency distribution of labels
    plt.figure(figsize=(8, 6))
    sns.countplot(y='Label', data=df, palette='Set2')
    plt.title("Frequency Distribution of Labels")
    plt.xlabel("Frequency")
    plt.ylabel("Label")
    plt.show()

    # Distribution of entity lengths
    df['Entity Length'] = df['Entity'].apply(len)
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Entity Length'], kde=True, color='blue')
    plt.title("Distribution of Entity Lengths")
    plt.xlabel("Entity Length")
    plt.ylabel("Frequency")
    plt.show()

    
    # Create a new column for entity lengths
    df['Entity Length'] = df['Entity'].apply(len)

    # Plot the distribution of entity lengths
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Entity Length'], kde=True, color='blue')
    plt.title("Distribution of Entity Lengths")
    plt.xlabel("Entity Length")
    plt.ylabel("Frequency")
    plt.show()

    # Count the frequency of entity-label pairs
    entity_label_pair = df.groupby(['Entity', 'Label']).size().reset_index(name='Frequency')

    # Sort and display the top 10 entity-label pairs by frequency
    top_entity_label_pairs = entity_label_pair.sort_values('Frequency', ascending=False).head(10)
    print(top_entity_label_pairs)

    # Display the first few rows
    print(df.head())
    # Check the number of rows and columns
    print(f"Data Shape: {df.shape}")

    # Check for unique entity types and labels
    print(f"Unique Entities: {df['Entity'].nunique()}")
    print(f"Unique Labels: {df['Label'].nunique()}")

    # Check the frequency distribution of the labels
    print(df['Label'].value_counts())
