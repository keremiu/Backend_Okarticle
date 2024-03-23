import motor.motor_asyncio
from bson.objectid import ObjectId

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://kerem:ztwk3iTKlL8RuQyE@cluster0.0pubafo.mongodb.net/')
db = client.pdf_database  
pdf_collection = db.pdfs  

async def insert_pdf(pdf_data):
    result = await pdf_collection.insert_one(pdf_data)
    return str(result.inserted_id)

async def get_pdf(pdf_id):
    document = await pdf_collection.find_one({"_id": ObjectId(pdf_id)})
    return document

async def update_pdf(pdf_id, update_data):
    result = await pdf_collection.update_one({"_id": ObjectId(pdf_id)}, {"$set": update_data})
    return result.modified_count

async def delete_pdf(pdf_id):
    result = await pdf_collection.delete_one({"_id": ObjectId(pdf_id)})
    return result.deleted_count

async def list_pdfs():
    pdfs = []
    async for pdf in pdf_collection.find():
        pdfs.append(pdf)
    return pdfs
