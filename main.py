from fastapi import FastAPI
from fastapi import FastAPI, UploadFile, File, Form
from typing import List,Optional
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from models.similarity import load_model_similarty, calculate_similarity
from config.file import extract_text, extract_text_from_bytes
from config.MyDB import insert_pdf, list_pdfs
import tempfile
import os
app = FastAPI()

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
# Global olarak tanımlanan yüklenen dosyalar listesi
global_uploaded_files = []

@app.post("/pdfs/")
async def process_pdfs(files: List[UploadFile] = File(...), string: Optional[str] = Form(None)):
    global global_uploaded_files  # Global değişkeni kullanmak için belirt
    response = {"added": [], "not_added": []}
    existing_pdfs = await list_pdfs()  # Veritabanındaki PDF'leri listele

    # Bu işlem için yüklenen dosyaları geçici bir listeye sakla
    temp_uploaded_files = []

    for file in files:
        contents = await file.read()  # PDF dosyasını oku
        text = extract_text_from_bytes(contents)
        is_similar = False  # Benzer bir PDF olup olmadığını kontrol etmek için flag

        for pdf in existing_pdfs:
            similarity = calculate_similarity([text, pdf["text"]])
            if similarity > 0.95:
                is_similar = True
                response["not_added"].append(file.filename)
                break

        if not is_similar:
            await insert_pdf({"text": text})  # PDF'i veritabanına ekle
            response["added"].append(file.filename)
            temp_uploaded_files.append(file.filename)  # Geçici listeye ekle

    # Global listeyi güncelle
    global_uploaded_files = temp_uploaded_files

    return response

    return response
def extract_text_from_bytes(contents):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(contents)
        temp_path = temp_file.name

    text = extract_text(temp_path)
    os.remove(temp_path)  # Geçici dosyayı sil
    return text

@app.get("/islem/")
async def process_int_array(operations: List[int] = Form(...)):
    return {"processed_operations": operations}


@app.on_event("startup")
async def startup_event():
    load_model_similarty()
    
if __name__ == '__main__':
    uvicorn.run(app, host="10.3.134.104", port=3000)
