from qdrant_client import models, QdrantClient
from tqdm import tqdm

class QdrantVDB:
    def __init__(self, vector_dim=768, batch_size=512, url=None):
        self.batch_size = batch_size
        self.vector_dim = vector_dim
        self.client = QdrantClient(url=url if url else "http://localhost:6333", prefer_grpc=True)
    
    def create_or_set_collection(self, collection_name):
        self.collection_name = collection_name
        if not self.client.collection_exists(collection_name=self.collection_name):

            self.client.create_collection(collection_name=self.collection_name,
                                        vectors_config=models.VectorParams(size=self.vector_dim, distance=models.Distance.DOT, on_disk=True),
                                        optimizers_config=models.OptimizersConfigDiff(default_segment_number=5, indexing_threshold=0)
                                        )
            
    def batch_iterate(self, lst, batch_size):
        for i in range(0, len(lst), batch_size):
            yield lst[i : i + batch_size]
    
    def ingest_data(self, embeddata, source):
    
        for batch_context, batch_embeddings in tqdm(zip(self.batch_iterate(embeddata.contexts, self.batch_size), 
                                                        self.batch_iterate(embeddata.embeddings, self.batch_size)), 
                                                    total=len(embeddata.contexts)//self.batch_size, 
                                                    desc="Ingesting in batches"):
        
            self.client.upload_collection(collection_name=self.collection_name,
                                        vectors=batch_embeddings,
                                        payload=[{"context": context, "source": source} for context in batch_context])

        self.client.update_collection(collection_name=self.collection_name,
                                    optimizer_config=models.OptimizersConfigDiff(indexing_threshold=20000)
                                    )
