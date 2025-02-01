import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Function to find the latest checkpoint directory
def get_latest_checkpoint(checkpoint_dir):
    """Finds the latest checkpoint in the given directory."""
    checkpoints = [d for d in os.listdir(checkpoint_dir) if os.path.isdir(os.path.join(checkpoint_dir, d))]
    if not checkpoints:
        raise ValueError("No checkpoints found in the directory.")
    
    # Sort the directories by their modification time, get the latest one
    checkpoints.sort(key=lambda x: os.path.getmtime(os.path.join(checkpoint_dir, x)), reverse=True)
    
    return os.path.join(checkpoint_dir, checkpoints[0])

# Load the tokenizer and the latest checkpoint model
checkpoint_dir = "./bert_finetuned"
latest_checkpoint = get_latest_checkpoint(checkpoint_dir)

model = AutoModelForSequenceClassification.from_pretrained(latest_checkpoint)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Set the device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def predict_relationship_from_entities(entity1: str, entity2: str) -> str:
    """Predicts the relationship between two entities using a fine-tuned BERT model."""
    # Format the input text
    input_text = f"{entity1} [SEP] {entity2}"
    
    # Tokenize the input
    inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    
    # Move the inputs to the appropriate device (GPU or CPU)
    inputs = {key: value.to(device) for key, value in inputs.items()}
    
    # Get model predictions
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Get the predicted label (0 for 'UNKNOWN', 1 for 'RELATED')
    predicted_label = torch.argmax(outputs.logits, dim=-1).item()
    
    # Map the numeric label to the relationship
    relationship = "RELATED" if predicted_label == 1 else "UNKNOWN"
    
    return relationship
