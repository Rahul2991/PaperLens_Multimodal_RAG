from rag_modules.conversational_bot import Conversational_Bot
from rag_modules.embed_data import EmbedData
from rag_modules.vector_db import QdrantVDB

def get_vector_db():
    return QdrantVDB()

def get_embed_data_obj():
    return EmbedData()

def initialize_bot():
    system_message = "You are an expert in the field of AI Research and current AI Trends."
    bot_instance = Conversational_Bot(system_message)
    return bot_instance

bot = initialize_bot()
