from rag_modules.embed_data import EmbedData
from rag_modules.vector_db import QdrantVDB
from rag_modules.rag_retriever import Retriever
from rag_modules.rag import RAG
from services.rag_service import bot

database = QdrantVDB()
database.create_or_set_collection("multimodal_rag_admin_collection")
embeddata = EmbedData()
retriever = Retriever(database, embeddata)
query = "what is positional encoding"
rag_bot = RAG(retriever, bot)

response = rag_bot.generate_context(query)
print(response)