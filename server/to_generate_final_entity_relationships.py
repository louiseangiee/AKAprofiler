from __future__ import annotations
import spacy
import pandas as pd
<<<<<<< Updated upstream
from transformers import BertTokenizer, BertForSequenceClassification
from spacy.tokens import Doc
from typing import List
=======
from transformers import BertTokenizer, BertForSequenceClassification, AdamW
>>>>>>> Stashed changes
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report



<<<<<<< Updated upstream
def call_wiki_api(item):
  try:
    url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={item}&language=en&format=json"
    data = requests.get(url).json()
    # Return the first id (Could upgrade this in the future)
    return data['search'][0]['id']
  except:
    return 'id-less'
  
def set_annotations(self, doc: Doc, triplets: List[dict]):
  for triplet in triplets:

      # Remove self-loops (relationships that start and end at the entity)
      if triplet['head'] == triplet['tail']:
          continue
=======
# Load your CSV data (make sure your file has 'Entity1', 'Entity2', and 'Relation' columns)
csv_file = "./server/Dataset/entity_pairs_relationship_fortraining.csv"
data = pd.read_csv(csv_file)

# Debug: Print column names
print("Columns in CSV:", data.columns)

# Ensure "Relation" column exists
data.columns = data.columns.str.strip()  # Remove spaces
if 'Relation' not in data.columns:
    print("Warning: 'Relation' column not found! Adding a default value.")
    data['Relation'] = "No Relation"  # Default value

# Function to create sentences with [E1] and [E2] tags
def create_sentence(row):
    return f"[CLS] [E1] {row['Entity1']} [/E1] is the {row['Relation']} of [E2] {row['Entity2']} [/E2]. [SEP]"
>>>>>>> Stashed changes

      # Use regex to search for entities
      head_span = re.search(triplet["head"], doc.text)
      tail_span = re.search(triplet["tail"], doc.text)

      # Skip the relation if both head and tail entities are not present in the text
      # Sometimes the Rebel model hallucinates some entities
      if not head_span or not tail_span:
        continue

      index = hashlib.sha1("".join([triplet['head'], triplet['tail'], triplet['type']]).encode('utf-8')).hexdigest()
      if index not in doc._.rel:
          # Get wiki ids and store results
          doc._.rel[index] = {"relation": triplet["type"], "head_span": {'text': triplet['head'], 'id': self.get_wiki_id(triplet['head'])}, "tail_span": {'text': triplet['tail'], 'id': self.get_wiki_id(triplet['tail'])}}  

# Define rel extraction model

rel_ext = spacy.load('en_core_web_sm', disable=['ner', 'lemmatizer', 'attribute_rules', 'tagger'])
rel_ext.add_pipe("rebel", config={
    'device':DEVICE, # Number of the GPU, -1 if want to use CPU
    'model_name':'Babelscape/rebel-large'} # Model used, will default to 'Babelscape/rebel-large' if not given
    )
# Define rel extraction model

<<<<<<< Updated upstream
rel_ext = spacy.load('en_core_web_sm', disable=['ner', 'lemmatizer', 'attribute_rules', 'tagger'])
rel_ext.add_pipe("rebel", config={
    'device':DEVICE, # Number of the GPU, -1 if want to use CPU
    'model_name':'Babelscape/rebel-large'} # Model used, will default to 'Babelscape/rebel-large' if not given
    )
=======
# Create datasets and dataloaders
train_dataset = RelationDataset(train_data, tokenizer)
val_dataset = RelationDataset(val_data, tokenizer)

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=16)

# Initialize BERT model for sequence classification (3 classes in this case, modify as needed)
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=3)

# Define optimizer
optimizer = AdamW(model.parameters(), lr=1e-5)

# Move model to the GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Training loop
for epoch in range(3):  # Train for 3 epochs
    model.train()
    total_loss = 0
    for batch in train_loader:
        optimizer.zero_grad()
        
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        total_loss += loss.item()
        
        loss.backward()
        optimizer.step()
    
    avg_train_loss = total_loss / len(train_loader)
    print(f"Epoch {epoch + 1}, Train Loss: {avg_train_loss}")

# Evaluation
model.eval()
predictions, true_labels = [], []

for batch in val_loader:
    input_ids = batch['input_ids'].to(device)
    attention_mask = batch['attention_mask'].to(device)
    labels = batch['labels'].to(device)
    
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
    
    predicted_class = torch.argmax(logits, dim=1).cpu().numpy()
    predictions.extend(predicted_class)
    true_labels.extend(labels.cpu().numpy())

accuracy = accuracy_score(true_labels, predictions)
print(f"Validation Accuracy: {accuracy}")

# Function to predict relationships between new entity pairs
def predict_relationship(entity1, entity2):
    sentence = f"[CLS] [E1] {entity1} [/E1] and [E2] {entity2} [/E2]. [SEP]"
    inputs = tokenizer(sentence, return_tensors="pt", padding="max_length", max_length=128, truncation=True)
    
    inputs = {key: value.to(device) for key, value in inputs.items()}  # Move to GPU if available
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class = torch.argmax(logits, dim=1).item()
    
    relation_labels = {0: "No Relation", 1: "Founder_of", 2: "CEO_of"}  # Modify if needed
    return relation_labels.get(predicted_class, "Unknown")


# Example prediction for a single pair of entities
entity1 = "Apple"
entity2 = "Steve Jobs"
predicted_relation = predict_relationship(entity1, entity2)
print(f"Predicted Relationship: {predicted_relation}")

# Save predictions to CSV
data['Predicted_Relation'] = data.apply(lambda row: predict_relationship(row['Entity1'], row['Entity2']), axis=1)
data.to_csv("./server/Dataset/final_entity_relationships.csv", index=False)
>>>>>>> Stashed changes
