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
from PyPDF2 import PdfReader
from spacy.tokenizer import Tokenizer
from spacy.util import compile_infix_regex
import matplotlib.pyplot as plt
import seaborn as sns
from testModelPrediction import predict_relationship_from_entities



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

def extract_entities_from_text(output_folder):
    # Check if output folder exists
    if not os.path.exists(output_folder) or not os.path.isdir(output_folder):
        print(f"Invalid folder path: {output_folder}")
        return []  # Return an empty list if the folder is invalid

    # Load SpaCy model and configure tokenizer
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
                    clean_entity = ent.text.strip().replace("\n", " ")  # Clean entity text
                    entity_count[clean_entity]["count"] += 1
                    entity_count[clean_entity]["pages"].add(page_num)

            # Store entity data
            for entity_text, data in entity_count.items():
                entity_data.append({
                    "file_name": filename,
                    "entity": entity_text,
                    "label": nlp(entity_text).ents[0].label_ if nlp(entity_text).ents else "UNKNOWN",
                    "frequency": data["count"],
                    "pagesFound": sorted(data["pages"]),
                    "relationships": []  # Placeholder for relationships
                })

    if not entity_data:
        print("No entities were extracted.")
        return []  # Return an empty list if no entities were found

    # Convert entity data to DataFrame
    df = pd.DataFrame(entity_data)

    # Clean and preprocess the extracted entity data
    df = df[df['entity'].str.strip() != '']
    df['entity'] = df['entity'].str.replace(r'\n', ' ', regex=True).str.strip()
    df['entity'] = df['entity'].apply(lambda x: ''.join(e for e in x if e.isalnum() or e.isspace()))
    df['entity'] = df['entity'].str.lower()
    df['label'] = df['label'].str.upper()

    # Remove duplicates (this should now work without any list issues)
    df = df.drop_duplicates(subset=['file_name', 'entity', 'label'])

    # Process and filter people entities
    grouped = df.groupby('file_name')
    entity_pairs = []

    # Generate entity pairs for each file
    for file_name, group in grouped:
        person_entities = group[group['label'] == 'PERSON']
        
        # Create all unique combinations of entity pairs where one is 'PERSON'
        for entity1, entity2 in combinations(person_entities['entity'], 2):
            entity_pairs.append({'file_name': file_name, 'entity1': entity1, 'entity2': entity2})

    # Convert the list to a DataFrame
    pairs_df = pd.DataFrame(entity_pairs)

    # Save the entity pairs to a new CSV file
    pairs_df.to_csv('entity_pairs.csv', index=False)
    print("Entity pairs generated and saved to entity_pairs.csv!")

    # Determine relationships and update entity data
    # Separate the relationships to prevent issues with unhashable types
    relationships = []

    for index, row in pairs_df.iterrows():
        relationship = predict_relationship_from_entities(row['entity1'], row['entity2'])
        relationships.append({
            "file_name": row['file_name'],
            "entity1": row['entity1'],
            "entity2": row['entity2'],
            "relationship": relationship
        })

    # Now update the entity data with relationships
    for entity in entity_data:
        for rel in relationships:
            if entity['file_name'] == rel['file_name'] and entity['entity'] in [rel['entity1'], rel['entity2']]:
                entity['relationships'].append({
                    "entity1": rel['entity1'],
                    "entity2": rel['entity2'],
                    "relationship": rel['relationship']
                })

    # Return the entity data
    return entity_data



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
