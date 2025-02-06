from qdrant_client import models
from rag_modules.vector_db import QdrantVDB
from rag_modules.embed_data import EmbedData
import time

class Retriever:
    def __init__(self, vector_db: QdrantVDB, embeddata: EmbedData):
        self.vector_db = vector_db
        self.embeddata = embeddata
        
    def search(self, query, top_k=10):
        query_embedding = self.embeddata.embed_model.get_query_embedding(query)
            
        # Start the timer
        start_time = time.time()
        
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
        
        # End the timer
        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"Execution time for the search: {elapsed_time:.4f} seconds")

        return result