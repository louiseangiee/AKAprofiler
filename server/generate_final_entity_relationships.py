from __future__ import annotations
import spacy
import pandas as pd
import requests
import torch
import re
import hashlib
from typing import List
from spacy.tokens import Doc
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datasets import Dataset
from torch.utils.data import DataLoader
from transformers import Trainer, TrainingArguments
from sklearn.metrics import accuracy_score

# Define DEVICE variable
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def call_wiki_api(item):
    """Fetches Wikidata ID for an entity."""
    try:
        url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={item}&language=en&format=json"
        data = requests.get(url).json()
        return data['search'][0]['id']
    except:
        return 'id-less'

def set_annotations(doc: Doc, triplets: List[dict]):
    """Sets relationships in SpaCy's Doc object."""
    for triplet in triplets:
        if triplet['head'] == triplet['tail']:
            continue
        head_span = re.search(re.escape(triplet["head"]), doc.text)
        tail_span = re.search(re.escape(triplet["tail"]), doc.text)
        if not head_span or not tail_span:
            continue
        index = hashlib.sha1("".join([triplet['head'], triplet['tail'], triplet['type']]).encode('utf-8')).hexdigest()
        if index not in doc._.rel:
            doc._.rel[index] = {
                "relation": triplet["type"],
                "head_span": {'text': triplet['head'], 'id': call_wiki_api(triplet['head'])},
                "tail_span": {'text': triplet['tail'], 'id': call_wiki_api(triplet['tail'])}
            }

# Load relation extraction model
nlp = spacy.load('en_core_web_sm', disable=['ner', 'lemmatizer', 'attribute_rules', 'tagger'])

# Load CSV File
def load_csv(file_path):
    """Loads entity pairs from a CSV file."""
    df = pd.read_csv(file_path)
    print(f"Original columns: {df.columns.tolist()}")  # Check the column names

    # If there are more than 3 columns, only keep the first 3 columns
    df = df.iloc[:, :3]
    df.columns = ["File Name", "Entity1", "Entity2"]
    return df

def extract_relationships(entity1, entity2, text):
    """Extracts relationships between entity pairs using regex matching."""
    pattern = re.escape(entity1) + r".*?" + re.escape(entity2)
    if re.search(pattern, text, re.IGNORECASE):
        return "RELATED"
    return "UNKNOWN"

# Assume we have document text stored
sample_text = "Shinzo Abe met with George W. Bush in Washington to discuss economic policies."

def add_relationships_to_csv(df, text):
    """Adds extracted relationships to the dataframe."""
    df["Relationship"] = df.apply(lambda row: extract_relationships(row["Entity1"], row["Entity2"], text), axis=1)
    return df

# Load data and extract relationships
df = load_csv("./server/Dataset/entity_pairs_relationship_fortraining.csv")
df = add_relationships_to_csv(df, sample_text)
print(df.head())

# Convert DataFrame to Hugging Face Dataset
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def preprocess_data(examples):
    inputs = [f"{e1} [SEP] {e2}" for e1, e2 in zip(examples["Entity1"], examples["Entity2"])]
    # Apply padding and truncation explicitly
    return tokenizer(inputs, padding=True, truncation=True, max_length=128)

train_data = Dataset.from_pandas(df)
train_data = train_data.map(preprocess_data, batched=True)
train_data = train_data.remove_columns(["File Name", "Entity1", "Entity2"])

# Ensure that labels are integers
train_data = train_data.rename_column("Relationship", "labels")
train_data = train_data.map(lambda x: {"labels": [1 if label == "RELATED" else 0 for label in x["labels"]]}, batched=True)

# Split the dataset into training and evaluation sets (90% train, 10% eval)
train_data = train_data.train_test_split(test_size=0.1)

# Train model
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
training_args = TrainingArguments(
    output_dir="./bert_finetuned",
    evaluation_strategy="epoch",  # Set evaluation strategy to epoch
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_data['train'],  # Train dataset
    eval_dataset=train_data['test'],   # Evaluation dataset
    tokenizer=tokenizer
)

trainer.train()

# Evaluate Model and Extract Logits
predictions = trainer.predict(train_data['test'])  # Use the evaluation dataset

# Extract logits and probabilities
logits = predictions.predictions
probabilities = torch.softmax(torch.tensor(logits), dim=-1)

# Get the predicted labels
pred_labels = logits.argmax(-1)

# Print logits and probabilities for debugging
print(f"Logits: {logits}")
print(f"Probabilities: {probabilities}")

# Optionally, apply threshold
threshold = 0.7
pred_labels_thresholded = (probabilities[:, 1] > threshold).long()

# Compute Accuracy
accuracy = accuracy_score(train_data['test']["labels"], pred_labels_thresholded)
print(f"Model Accuracy: {accuracy:.4f}")

# Optionally print some predictions to verify
for i in range(10):  # Print the first 10 predictions
    print(f"Text: {train_data['test'][i]}")
    print(f"Predicted Label: {pred_labels[i]}, Probability: {probabilities[i]}")
