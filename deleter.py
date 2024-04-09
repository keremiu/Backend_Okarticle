import asyncio
import motor.motor_asyncio
from bson.objectid import ObjectId

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://kerem:ztwk3iTKlL8RuQyE@cluster0.0pubafo.mongodb.net/')
db = client.pdf_database
pdf_collection = db.pdfs

async def delete_all_pdfs():
    result = await pdf_collection.delete_many({})
    return result.deleted_count
async def list_pdfs():
    pdfs = []
    async for pdf in pdf_collection.find():
        pdfs.append(pdf)
    return pdfs
async def list_pdf_names():
    names = []
    async for pdf in pdf_collection.find({}, {'name': 1}):  # Projection to return only the name field
        names.append(pdf['name'])
    return names
async def main():
    pdfs = await list_pdf_names()
    print(f"Silinen PDF belge sayısı: {pdfs}")

if __name__ == "__main__":
    asyncio.run(main())
