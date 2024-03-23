import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sentence_transformers import SentenceTransformer
model = None
        
def load_model_similarty():
    global model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
def calculate_similarity(sentences):
    embeddings = model.encode(sentences)
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return similarity
