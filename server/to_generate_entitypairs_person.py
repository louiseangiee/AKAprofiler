import pandas as pd
from itertools import combinations

# Load the extracted entities CSV
entities_df = pd.read_csv('server/Dataset/extracted_entities_cleaned_v2.csv')

# Group entities by file name
grouped = entities_df.groupby('File Name')

# List to store the entity pairs
entity_pairs = []

# Generate entity pairs for each file
for file_name, group in grouped:
    # Filter out entities with the label 'PERSON'
    person_entities = group[group['Label'] == 'PERSON']
    
    # Create all unique combinations of entity pairs where one is 'PERSON'
    for entity1, entity2 in combinations(person_entities['Entity'], 2):
        entity_pairs.append({'File Name': file_name, 'Entity1': entity1, 'Entity2': entity2})

# Convert the list to a DataFrame
pairs_df = pd.DataFrame(entity_pairs)

# Save the entity pairs to a new CSV file
pairs_df.to_csv('entity_pairs.csv', index=False)

print("Entity pairs generated and saved to entity_pairs.csv!")
