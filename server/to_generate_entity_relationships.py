# use bert
# pip install transformers torch
# python3 -m pip install transformers torch
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
import torch

# Load pre-trained BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=3)  # Assume 3 relationship classes

# Read CSV file
csv_file = "/Dataset/extracted_entities_cleaned_v2.csv"
data = pd.read_csv(csv_file)

# Example sentence with marked entities
sentence = "[CLS] [E1] Elon Musk [/E1] is the CEO of [E2] Tesla [/E2]. [SEP]"

# Tokenize the sentence
inputs = tokenizer(sentence, return_tensors="pt")

# Model prediction
with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=1).item()

# Define relation labels (for demonstration purposes)
relation_labels = {0: "No Relation", 1: "Founder_of", 2: "CEO_of"}

# Print the predicted relationship
print(f"Predicted Relationship: {relation_labels[predicted_class]}")
