from qdrant_client import models
from rag_modules.vector_db import QdrantVDB
from rag_modules.embed_data import EmbedData
import time
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

class Retriever:
    """
    Retriever class that performs vector-based search using Qdrant.
    
    Attributes:
        vector_db (QdrantVDB): The Qdrant vector database client.
        embeddata (EmbedData): The embedding model used for generating query embeddings.
    """
    def __init__(self, vector_db: QdrantVDB, embeddata: EmbedData):
        """
        Initializes the Retriever with a vector database and an embedding model.
        
        Args:
            vector_db (QdrantVDB): Instance of the Qdrant vector database.
            embeddata (EmbedData): Instance of the embedding model.
        """
        self.vector_db = vector_db
        self.embeddata = embeddata
        logger.info("Retriever initialized with Qdrant vector database and embedding model.")
        
    def search(self, query: str, top_k: int=10):
        """
        Searches for the most relevant vectors in the Qdrant database based on the query.
        
        Args:
            query (str): The query text to be searched.
            top_k (int, optional): The number of top results to retrieve. Defaults to 10.
        
        Returns:
            List[dict]: A list of retrieved results with context and source payloads.
        """
        logger.info(f"Performing search for query: {query}")
        
        # Generate embedding for the query
        query_embedding = self.embeddata.embed_model.get_query_embedding(query)
        logger.info("Query embedding generated successfully.")
        
        # Start timer to measure search execution time
        start_time = time.time()
        
        try:
            result = self.vector_db.client.query_points(
                collection_name=self.vector_db.collection_name,
                
                query=query_embedding,
                
                search_params=models.SearchParams(
                    quantization=models.QuantizationSearchParams(
                        ignore=True,
                        rescore=True,
                        oversampling=2.0,
                    )
                ),
                limit=top_k,
                timeout=1000,
                with_payload=['context', 'source']
            )
            
            # Measure execution time
            elapsed_time = time.time() - start_time
            logger.info(f"Search executed successfully in {elapsed_time:.4f} seconds.")
            
            return result
        except Exception as e:
            logger.error(f"Error occurred during search: {e}")
            return None