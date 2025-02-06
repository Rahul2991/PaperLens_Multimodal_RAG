from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from tqdm import tqdm

class EmbedData:
    def __init__(self, embed_model_name="nomic-ai/nomic-embed-text-v1.5", batch_size=32):
        self.embed_model_name = embed_model_name
        self.embed_model = self._load_embed_model()
        self.batch_size = batch_size
        self.embeddings = []
        
    def _load_embed_model(self):
        embed_model = HuggingFaceEmbedding(model_name=self.embed_model_name, trust_remote_code=True)
        return embed_model
    
    def generate_embedding(self, context):
        return self.embed_model.get_text_embedding_batch(context)
    
    def batch_iterate(self, lst, batch_size):
        for i in range(0, len(lst), batch_size):
            yield lst[i : i + batch_size]
        
    def embed(self, contexts):
        self.contexts = contexts
        for batch_context in tqdm(self.batch_iterate(contexts, self.batch_size), total=len(contexts)//self.batch_size, desc="Embedding data in batches"):
            batch_embeddings = self.generate_embedding(batch_context)
            self.embeddings.extend(batch_embeddings)
            
