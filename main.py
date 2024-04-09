from fastapi import FastAPI, UploadFile, File, Form
from typing import List,Optional
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from Modules.similarity import  calculate_similarity
from config.file import extract_text, extract_text_from_bytes
from config.MyDB import insert_pdf, list_pdfs,calculate_similarity_with_db,calculate_similarity_for_all_pdfs
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

@app.get("/")
async def read_root():
    return {"Hello": "World"}

    #"List[UploadFile] = File(...),
# Global bir PDF listesi tanımlayın
global_pdfs = []
global_index = 0  # Seçili makale için global index

PDF_SAVE_FOLDER = "saved_pdfs"
os.makedirs(PDF_SAVE_FOLDER, exist_ok=True)

@app.post("/upload/")
async def upload_pdfs(files: List[UploadFile] = File(...),index: str = Form(...)):
    global global_pdfs, global_index
    global_index = int(index)
    unique_pdfs = []
    global_pdfs.clear()
    for file in files:
        pdf_file_path = os.path.join(PDF_SAVE_FOLDER, file.filename)
        contents = await file.read()
        with open(pdf_file_path, 'wb') as f:
            f.write(contents)
        tree = get_tree_from_article_pdf(pdf_file_path)
        text = tree.get_article_tree_as_string()
        pdf_name = tree.root.data 
        is_similar_to_db = await calculate_similarity_with_db(text,model_sim)
        is_similar_to_uploaded = any(calculate_similarity(model_sim,[text, existing_text]) > 0.95 for existing_text in unique_pdfs)
        if not is_similar_to_uploaded and not is_similar_to_db:
            await insert_pdf(pdf_name,text,model_sim)
        global_pdfs.append({"name": pdf_name, "text": text, "path": pdf_file_path})  # PDF dosya yolu burada ekleniyor
    return pdf_name 

@app.get("/RecommendArticle/")
async def process_RecommendArticle():
    global global_pdfs, global_index
    target_pdf = global_pdfs[global_index]
    top5 = await calculate_similarity_for_all_pdfs(target_pdf,model_sim)
    return top5

@app.get("/CalSim/")
async def process_calSim():
    global global_pdfs, global_index
    if not global_pdfs or len(global_pdfs) <= 1:
        return {"Not enough PDFs to calculate similarity."}

    target_pdf = global_pdfs[global_index]
    target_text = target_pdf["text"]

    similarities = []
    for idx, pdf in enumerate(global_pdfs):
        if idx == global_index:
            continue  
        other_text = pdf["text"]
        similarity = calculate_similarity(model_sim, [target_text, other_text])
        similarities.append(similarity)

    if not similarities:
        return {"error": "No similarities calculated."}

    average_similarity = sum(similarities) / len(similarities)
    return str(average_similarity)

@app.post("/FindContext/")
async def process_Contex(string: str = Form(...) ):
    global global_pdfs, global_index
    target_pdf = global_pdfs[global_index]
    pdf_file_path = target_pdf['path']
    tree = get_tree_from_article_pdf(pdf_file_path)
    return tree.get_context(string,5,model_sim)


@app.post("/summarize/")
async def process_pdfs(files: List[UploadFile] = File(...), index: str = Form(...), ratio: str = Form(...)):
    global global_pdfs, global_index
    global_index = int(index)
    global_pdfs.clear()
    
    if len(files) > 1:
        temp_pdfs = []  # İşlenen PDF'leri geçici olarak saklamak için
        base_file = files[global_index]  # Index ile belirlenen dosyayı al
        base_pdf_path = os.path.join(PDF_SAVE_FOLDER, base_file.filename)
        base_contents = await base_file.read()
        with open(base_pdf_path, 'wb') as f:
            f.write(base_contents)
        base_tree = get_tree_from_article_pdf(base_pdf_path)
        base_text = base_tree.get_article_tree_as_string()
        base_pdf_name = base_tree.root.data
        temp_pdfs.append({"name": base_pdf_name, "text": base_text, "path": base_pdf_path})
        is_similar_to_db = await calculate_similarity_with_db(base_text,model_sim)
        if not is_similar_to_db:
                await insert_pdf(base_pdf_name,base_text,model_sim)
        # Diğer tüm PDF'leri sırayla base_tree'ye merge et
        for i, file in enumerate(files):
            if i != global_index:  # Base dosya dışındaki dosyaları işle
                pdf_path = os.path.join(PDF_SAVE_FOLDER, file.filename)
                contents = await file.read()
                with open(pdf_path, 'wb') as f:
                    f.write(contents)
                tree = get_tree_from_article_pdf(pdf_path)
                # Merge işlemi
                base_tree = base_tree.merge_trees(tree,model_sim, float(ratio), True)
                # İşlenen PDF'i temp_pdfs'e ekle
                text = tree.get_article_tree_as_string()
                pdf_name = tree.root.data
                is_similar_to_db = await calculate_similarity_with_db(text,model_sim)
                if not is_similar_to_db:
                    await insert_pdf(pdf_name,text,model_sim)
                temp_pdfs.append({"name": pdf_name, "text": text, "path": pdf_path})

        # İşlem tamamlandıktan sonra, temp_pdfs'i global_pdfs'e aktar
        global_pdfs = temp_pdfs.copy()

        # Birleştirilmiş ağacı özetle ve sonucu dön
        summary = base_tree.summarize_parts(float(ratio), tokenizer, model_sum)
        return summary
    else:
        # Tek dosya için özetleme işlemi
        file = files[0]  # Tek dosyayı işle
        pdf_file_path = os.path.join(PDF_SAVE_FOLDER, file.filename)
        contents = await file.read()
        with open(pdf_file_path, 'wb') as f:
            f.write(contents)
        tree = get_tree_from_article_pdf(pdf_file_path)
        text = tree.get_article_tree_as_string()
        pdf_name = tree.root.data
        global_pdfs.append({"name": pdf_name, "text": text, "path": pdf_file_path})
        is_similar_to_db = await calculate_similarity_with_db(text,model_sim)
        if not is_similar_to_db:
             await insert_pdf(pdf_name,text,model_sim)
        return tree.summarize_parts(float(ratio), tokenizer, model_sum)





@app.on_event("startup")
async def startup_event():
    load_model_similarty()
    load_model_sum()
    load_tokenizer_sum()
    
def load_model_similarty():
    global model_sim
    model_sim = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2') 
    
def load_model_sum():
    global model_sum
    #model_sum = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
    with open('model.pkl', 'rb') as file:
        model_sum = pickle.load(file)
    
def load_tokenizer_sum():
    global tokenizer
    #tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
    with open('tokenizer.pkl', 'rb') as file:
        tokenizer = pickle.load(file)

     
if __name__ == '__main__':
    uvicorn.run(app, host="10.3.134.104", port=8000)
