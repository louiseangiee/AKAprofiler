from __future__ import annotations
import spacy
import pandas as pd
import requests
import torch
import re
import hashlib
from typing import List
from spacy.tokens import Doc
from spacy.language import Language
from transformers import pipeline
from datasets import Dataset
from torch.utils.data import DataLoader
from transformers import Trainer, TrainingArguments
from sklearn.metrics import accuracy_score
from typing import List

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

def set_annotations(doc: Doc, triplets: List[dict]):
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
    text = doc.text
    results = rebel_pipeline(text, max_length=512, truncation=True)
    
    extracted_relations = {}
    
    for result in results:
        extracted_relations[hashlib.sha1(result["generated_text"].encode()).hexdigest()] = result["generated_text"]
    
    doc._.rel = extracted_relations  # Store relations in spaCy doc
    return doc

# Add the custom component to spaCy
nlp.add_pipe("rebel", last=True)

def load_csv(file_path):
    """Loads entity pairs from a CSV file."""
    df = pd.read_csv(file_path)
    print(f"Original columns: {df.columns.tolist()}")  # Debugging check
    df = df.iloc[:, :4]  # Ensure we only have the correct 4 columns
    df.columns = ["File Name", "Entity1", "Entity2", "Relationship"]
    return df

def extract_relationships(df):
    """Uses Rebel to extract relationships for given entity pairs."""
    for index, row in df.iterrows():
        entity1, entity2, relationship = row["Entity1"], row["Entity2"], row["Relationship"]
        if relationship == "Unknown":
            wiki_id1 = call_wiki_api(entity1)
            wiki_id2 = call_wiki_api(entity2)
            
            query_text = f"{entity1} and {entity2} relationship"
            doc = nlp(query_text)
            
            if doc._.rel:
                print(f"Found relation: {list(doc._.rel.values())[0]}")
                df.at[index, "Relationship"] = list(doc._.rel.values())[0]  # Update dataframe
    return df

# Load data and process relationships
df = load_csv("./server/Dataset/entity_pairs_relationship_fortraining2.csv")
df = extract_relationships(df)
print(df.head())

# Save updated data
df.to_csv("./server/Dataset/updated_relationships.csv", index=False)
