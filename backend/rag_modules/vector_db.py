from qdrant_client import models, QdrantClient
from utils import is_valid_url
from tqdm import tqdm
import logging
from grpc import RpcError


# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

class QdrantVDB:
    """
    A class to manage interactions with Qdrant vector database.
    """
    def __init__(self, vector_dim=768, batch_size=512, url="http://localhost:6333"):
        """
        Initializes Qdrant vector database client.

        Args:
            vector_dim: Dimensionality of the vectors.
            batch_size: Batch size for ingestion.
            url: Qdrant server URL, defaults to localhost.
        """
        self.batch_size = batch_size
        self.vector_dim = vector_dim
        try:
            if not is_valid_url(url):
                logger.error(f"Invalid URL provided: {url}")
                raise ValueError(f"Invalid URL provided: {url}")

            self.client = QdrantClient(url=url, prefer_grpc=True)
            logger.info("QdrantVDB initialized with vector_dim=%d, batch_size=%d, url=%s", vector_dim, batch_size, url)
        except Exception as e:
            logger.error(f"Failed to initialized QdrantVDB: {e}", exc_info=True)
            raise
    
    def create_or_set_collection(self, collection_name):
        """
        Creates a new collection if it doesn't exist, or sets the current collection.
        
        Args:
            collection_name: Name of the collection.
        """
        try:
            self.collection_name = collection_name
            if not self.client.collection_exists(collection_name=self.collection_name):
                logger.info("Creating collection: %s", collection_name)
                self.client.create_collection(collection_name=self.collection_name,
                                            vectors_config=models.VectorParams(size=self.vector_dim, distance=models.Distance.DOT, on_disk=True),
                                            optimizers_config=models.OptimizersConfigDiff(default_segment_number=5, indexing_threshold=0)
                                            )
                logger.info("Collection %s created successfully", collection_name)
            else:
                logger.info("Collection %s already exists", collection_name)
        except RpcError as re:
            logger.error(f"Failed to connect to Qdrant server: %s", re.details() if hasattr(re, "details") else str(re))
            raise
        except Exception as e:
            logger.error(f"Error creating or setting collection: %s", str(e), exc_info=True)
            raise
            
    def batch_iterate(self, lst, batch_size):
        """
        Yields batches from a given list.
        
        Args:
            lst: List to be batched.
            batch_size: Size of each batch.
        """
        for i in range(0, len(lst), batch_size):
            yield lst[i : i + batch_size]
    
    def ingest_data(self, embeddata, source):
        """
        Ingests data into the Qdrant vector database in batches.
        
        Args:
            embeddata: An instance of EmbedData containing contexts and embeddings.
            source: Source identifier for the ingested data.
        """
        logger.info("Starting data ingestion for collection: %s", self.collection_name)
        try:
            for batch_context, batch_embeddings in tqdm(zip(self.batch_iterate(embeddata.contexts, self.batch_size), 
                                                            self.batch_iterate(embeddata.embeddings, self.batch_size)), 
                                                        total=len(embeddata.contexts)//self.batch_size, 
                                                        desc="Ingesting in batches"):
            
                self.client.upload_collection(collection_name=self.collection_name,
                                            vectors=batch_embeddings,
                                            payload=[{"context": context, "source": source} for context in batch_context]
                                            )
                logger.info("Ingested a batch of %d items into collection %s", len(batch_context), self.collection_name)
                
            # Update collection optimizer configuration after ingestion
            self.client.update_collection(collection_name=self.collection_name,
                                        optimizer_config=models.OptimizersConfigDiff(indexing_threshold=20000)
                                        )
            logger.info("Collection %s updated successfully with new optimizer settings", self.collection_name)
        except Exception as e:
            logger.error("Error during data ingestion: %s", str(e), exc_info=True)
            raise