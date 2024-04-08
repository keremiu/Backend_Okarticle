from fastapi import FastAPI, UploadFile, File, Form
from typing import List,Optional
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from models.similarity import  calculate_similarity
from config.file import extract_text, extract_text_from_bytes
from config.MyDB import insert_pdf, list_pdfs,calculate_similarity_with_db
#from models.load_models import load_model_similarty,load_tokenizer_sum,load_model_sum
from Modules.article_tree import ArticleTree 
from Modules.reader import get_tree_from_article_pdf
#from models.load_models import model_sum,tokenizer,model_sim
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, BartForConditionalGeneration
import tempfile
import pickle
import os
from model import User,Ratio
app = FastAPI()

model_sim = None
tokenizer = None  
model_sum = None 

# CORS için tüm kökenlere izin ver
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    
@app.post("/deneme2/")
def deneme2(user: User):
    return user

@app.get("/")
async def read_root():
    return {"Hello": "World"}

    #"List[UploadFile] = File(...),

@app.post("/pdfs/")
async def process_pdfs(files: List[UploadFile] = File(...),ratio: str = Form(...)):
    return "summarize"

@app.get("/findContext/")
async def process_findContext():
    return "findContext"

@app.get("/CalSim/")
async def process_calSim():
    global global_pdfs
    return global_pdfs

# Global bir PDF listesi tanımlayın
global_pdfs = []
PDF_SAVE_FOLDER = "saved_pdfs"
os.makedirs(PDF_SAVE_FOLDER, exist_ok=True)

@app.post("/summarize/")
async def process_pdfs(files: List[UploadFile] = File(...), ratio: str = Form(...)):
    global global_pdfs
    unique_pdfs = []
    global_pdfs.clear()
    for file in files:
        pdf_file_path = os.path.join(PDF_SAVE_FOLDER, file.filename)
        contents = await file.read()
        with open(pdf_file_path, 'wb') as f:
            f.write(contents)
        print(f"PDF dosyası kaydedildi: {pdf_file_path}")  

        tree = get_tree_from_article_pdf(pdf_file_path)
        text = tree.get_article_tree_as_string()
        #print(f"Elde edilen metin: {text}")  

        #if text is None:
          #  print("Dikkat: Elde edilen metin 'None' döndü.")
         #   continue  
        is_similar_to_db = await calculate_similarity_with_db(text,model_sim)
        is_similar_to_uploaded = any(calculate_similarity([text, existing_text]) > 0.95 for existing_text in unique_pdfs)
        if not is_similar_to_uploaded and not is_similar_to_db:
            await insert_pdf(text,model_sim)
            
        '''for filename in os.listdir(PDF_SAVE_FOLDER):
            file_path = os.path.join(PDF_SAVE_FOLDER, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)  '''   
    print("Model sum yüklendi:", model_sum)
    print("tokenizer yüklendi:", tokenizer)
    return  tree.summarize_parts(float(ratio), tokenizer, model_sum)

@app.get("/islem/")
async def process_int_array(operations: List[int] = Form(...)):
    return {"processed_operations": operations}

@app.get("/deneme/")
async def deneme():
        return "merhaba"
    
@app.post("/deneme2/")
def deneme2(user: User):
    return user


@app.on_event("startup")
async def startup_event():
    load_model_similarty()
    load_model_sum()
    load_tokenizer_sum()
    
def load_model_similarty():
    global model_sim
    model_sim = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print("Model sim yüklendi:", model_sim)  
    
def load_model_sum():
    global model_sum
    #model_sum = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
    with open('model.pkl', 'rb') as file:
        model_sum = pickle.load(file)
    print("Model sum yüklendi:", model_sum)
    
def load_tokenizer_sum():
    global tokenizer
    #tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
    with open('tokenizer.pkl', 'rb') as file:
        tokenizer = pickle.load(file)
    print("tokenizer yüklendi:", tokenizer)

     
if __name__ == '__main__':
    uvicorn.run(app, host="10.3.134.104", port=8000)
