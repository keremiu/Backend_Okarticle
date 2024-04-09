import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

    
def calculate_similarity(model_sim,sentences):
    embeddings = model_sim.encode(sentences)
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return similarity

# Bu classa gerek kalmamış olabilir