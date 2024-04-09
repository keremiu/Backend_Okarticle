import motor.motor_asyncio
from bson.objectid import ObjectId
#client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://kerem:ztwk3iTKlL8RuQyE@cluster0.0pubafo.mongodb.net/')

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://kerem:ztwk3iTKlL8RuQyE@cluster0.0pubafo.mongodb.net/')

db = client.pdf_database  
pdf_collection = db.pdfs  
from sklearn.metrics.pairwise import cosine_similarity
async def insert_pdf(pdf_name, pdf_text, model_sim):
    pdf_vector = model_sim.encode([pdf_text])[0].tolist()
    pdf_data = {"name": pdf_name, "text": pdf_text, "vector": pdf_vector}
    result = await pdf_collection.insert_one(pdf_data)
    return str(result.inserted_id)

async def calculate_similarity_with_db(new_pdf_text,model_sim):
    print("ModeL SİM DATABASE:", model_sim)
    new_pdf_vector = model_sim.encode([new_pdf_text])[0]
    async for pdf in pdf_collection.find({}):
        existing_pdf_vector = pdf["vector"]
        similarity = cosine_similarity([new_pdf_vector], [existing_pdf_vector])[0][0]
        if similarity > 0.95:
            return True
    return False

async def calculate_similarity_for_all_pdfs(pdf_text, model_sim):
    input_pdf_vector = model_sim.encode([pdf_text])[0]
    similarities = []
    async for pdf in pdf_collection.find():
        similarity = cosine_similarity([input_pdf_vector], [pdf["vector"]])[0][0]
        similarities.append((pdf["name"], similarity))
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_5_similar_pdfs = [name for name, _ in similarities[:5]]
    return top_5_similar_pdfs

async def delete_all_pdfs():
    result = await pdf_collection.delete_many({})
    return result.deleted_count

async def get_pdf_vector(pdf_id):
    document = await pdf_collection.find_one({"_id": ObjectId(pdf_id)}, {"vector": 1})
    return document.get("vector", [])

async def get_pdf(pdf_id):
    document = await pdf_collection.find_one({"_id": ObjectId(pdf_id)})
    return document

async def update_pdf(pdf_id, update_data):
    result = await pdf_collection.update_one({"_id": ObjectId(pdf_id)}, {"$set": update_data})
    return result.modified_count

async def get_pdf_name(pdf_id):
    document = await pdf_collection.find_one({"_id": ObjectId(pdf_id)}, {"name": 1})
    return document.get("name", "PDF Not Found")

async def delete_pdf(pdf_id):
    result = await pdf_collection.delete_one({"_id": ObjectId(pdf_id)})
    return result.deleted_count

async def list_pdf_names():
    names = []
    async for pdf in pdf_collection.find({}, {'name': 1}):  # Projection to return only the name field
        names.append(pdf['name'])
    return names

async def list_pdfs():
    pdfs = []
    async for pdf in pdf_collection.find():
        pdfs.append(pdf)
    return pdfs
