
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, BartForConditionalGeneration
import pickle
model_sim = None
tokenizer = None  
model_sum = None      
def load_model_similarty():
    global model_sim
    model_sim = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print("Model sim yüklendi:", model_sim)
    
def load_model_sum():
    global model_sum
    model_sum = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
    with open('model.pkl', 'rb') as file:
        model_sum = pickle.load(file)
    
def load_tokenizer_sum():
    global tokenizer
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
    with open('tokenizer.pkl', 'rb') as file:
        tokenizer = pickle.load(file)
        
