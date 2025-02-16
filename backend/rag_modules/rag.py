from transformers import AutoModelForSequenceClassification, AutoTokenizer
from rag_modules.conversational_bot import Conversational_Bot
from rag_modules.rag_retriever import Retriever
import torch

class RAG:
    def __init__(self, retriever: Retriever, bot: Conversational_Bot, reranker_model_name="BAAI/bge-reranker-base", rerank_threshold = 0.7, top_k = 10):
        
        self.llm = bot
        self.retriever = retriever
        self.qa_prompt_tmpl_str = """Context information is below.
                                    ---------------------
                                    {context}
                                    ---------------------
                                    Given the context information above I want you to think step by step to answer the query, incase you don't know the answer say 'I don't know!'
                                    ---------------------
                                    Query: {query}
                                    ---------------------
                                    Answer: """
        self.reranker_model = AutoModelForSequenceClassification.from_pretrained(reranker_model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(reranker_model_name)
        self.rerank_threshold = rerank_threshold
        self.top_k = top_k
    
    def rerank(self, query, retrieved_docs):
        inputs = [f"Query: {query} Document: {doc['payload']['context']}" for doc in retrieved_docs]
        tokenized = self.tokenizer(inputs, padding=True, truncation=True, return_tensors="pt")
        
        with torch.no_grad():
            scores = self.reranker_model(**tokenized).logits.squeeze().tolist()
            
        for i, doc in enumerate(retrieved_docs):
            doc["score"] = scores[i]
            
        reranked_docs = sorted(retrieved_docs, key=lambda x: x["score"], reverse=True)
        
        reranked_filtered_docs = [doc for doc in reranked_docs if doc['score'] >= self.rerank_threshold]
        
        return reranked_filtered_docs
        
    def generate_context(self, query):
        results = self.retriever.search(query, self.top_k).model_dump()
        retrieved_docs = [dict(data) for data in results['points']]
        reranked_docs = self.rerank(query, retrieved_docs)
        if len(reranked_docs): 
            combined_prompt = []

            for entry in reranked_docs:
                context = entry["payload"]["context"]
                combined_prompt.append(context)
        else:
            combined_prompt = ['No relevant documents found']

        return "\n\n---\n\n".join(combined_prompt)

    def query(self, query, img=None):
        context = self.generate_context(query=query)
        prompt = self.qa_prompt_tmpl_str.format(context=context, query=query)
        response = self.llm.generate(prompt, image=img)
        
        return response