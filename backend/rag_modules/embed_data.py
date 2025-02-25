from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from tqdm import tqdm
from typing import List
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

class EmbedData:
    """
    A class for generating text embeddings using a Hugging Face model.
    
    Attributes:
        embed_model_name (str): Name of the Hugging Face embedding model.
        batch_size (int): Number of contexts to process per batch.
        embed_model (HuggingFaceEmbedding): Loaded embedding model instance.
        embeddings (list): List of generated embeddings.
    """
    def __init__(self, embed_model_name: str = "nomic-ai/nomic-embed-text-v1.5", batch_size: int = 32):
        """
        Initializes the EmbedData class with the given model name and batch size.
        
        Args:
            embed_model_name (str): Name of the Hugging Face embedding model.
            batch_size (int): Number of contexts to process in a single batch.
        """
        self.embed_model_name = embed_model_name
        try:
            self.embed_model = self._load_embed_model()
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise
        self.batch_size = batch_size
        self.embeddings = []
        
    def _load_embed_model(self):
        """
        Loads the specified Hugging Face embedding model.
        
        Returns:
            HuggingFaceEmbedding: An instance of the embedding model.
        """
        logger.info(f"Loading embedding model: {self.embed_model_name}")
        embed_model = HuggingFaceEmbedding(model_name=self.embed_model_name, trust_remote_code=True)
        logger.info("Model loaded successfully.")
        return embed_model
    
    def generate_embedding(self, context: List[str]):
        """
        Generates embeddings for a given list of text contexts.
        
        Args:
            context (List[str]): A list of text inputs to embed.
        
        Returns:
            list: A list of generated embeddings.
        """
        logger.info(f"Generating embeddings for {len(context)} texts.")
        return self.embed_model.get_text_embedding_batch(context)
    
    def batch_iterate(self, lst: List, batch_size: int):
        """
        Yields batches of data from the given list.
        
        Args:
            lst (list): List of data to batch.
            batch_size (int): Size of each batch.
        
        Yields:
            list: A batch of data.
        """
        for i in range(0, len(lst), batch_size):
            yield lst[i : i + batch_size]
        
    def embed(self, contexts: List[str]):
        """
        Processes a list of text contexts in batches and generates embeddings.
        
        Args:
            contexts (list of str): A list of text inputs to be embedded.
        """
        try:
            self.contexts = contexts
            logger.info(f"Starting embedding process for {len(contexts)} texts.")
            
            for batch_context in tqdm(self.batch_iterate(contexts, self.batch_size), total=len(contexts)//self.batch_size, desc="Embedding data in batches"):
                batch_embeddings = self.generate_embedding(batch_context)
                self.embeddings.extend(batch_embeddings)
            
            logger.info("Embedding process completed.")
        except Exception as e:
            logger.error("Error during embedding: %s", str(e))
            raise