from rag_modules.document_extract import extract_pdf_data
from rag_modules.embed_data import EmbedData
from rag_modules.vector_db import QdrantVDB
from services.rag_service import rag_bot

file_path = 'attention.pdf'

embed_data = EmbedData()
vector_db = QdrantVDB()

extracted_data = extract_pdf_data(file_path=file_path, bot=rag_bot)
if extracted_data:
    texts, image_summaries, table_summaries = extracted_data
    embed_data.embed(texts + image_summaries + table_summaries)
else:
    raise Exception("Failed to fetch extract data.")

collection_name = 'multimodal_rag_user_collection'
vector_db.create_collection(collection_name)
vector_db.ingest_data(embed_data, source=file_path)