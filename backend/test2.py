from models.mongo_db import get_files_collection
import asyncio

file_collection = get_files_collection()

async def get_files_list():
    file_list = await file_collection.find().to_list()
    print(file_list)
        
asyncio.run(get_files_list())