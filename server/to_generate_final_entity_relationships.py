from __future__ import annotations
import spacy
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
from spacy.tokens import Doc
from typing import List
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report



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

rel_ext = spacy.load('en_core_web_sm', disable=['ner', 'lemmatizer', 'attribute_rules', 'tagger'])
rel_ext.add_pipe("rebel", config={
    'device':DEVICE, # Number of the GPU, -1 if want to use CPU
    'model_name':'Babelscape/rebel-large'} # Model used, will default to 'Babelscape/rebel-large' if not given
    )