from transformers import AutoModelForSequenceClassification, AutoTokenizer
from rag_modules.conversational_bot import Conversational_Bot
from rag_modules.rag_retriever import Retriever
import torch
import logging

# Configure logger
logger = logging.getLogger("Multimodal_rag_bot")

class RAG:
    """
    A RAG (Retrieval-Augmented Generation) system that retrieves relevant documents,
    reranks them based on relevance, and generates responses using a conversational bot.
    """
    def __init__(self, retriever: Retriever, bot: Conversational_Bot, reranker_model_name="BAAI/bge-reranker-base", rerank_threshold = 0.7, top_k = 10):
        """
        Initializes the RAG system.
        
        Args:
            retriever (Retriever): The retriever module for fetching relevant documents.
            bot (Conversational_Bot): The conversational bot for generating responses.
            reranker_model_name (str): Model name for sequence classification reranking.
            rerank_threshold (float): Minimum score threshold for reranked documents.
            top_k (int): Number of top retrieved documents.
        """
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
                                    
        # Load reranker model and tokenizer
        logger.info(f"Loading reranker model: {reranker_model_name}")
        self.reranker_model = AutoModelForSequenceClassification.from_pretrained(reranker_model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(reranker_model_name)
        self.rerank_threshold = rerank_threshold
        self.top_k = top_k
    
    def rerank(self, query, retrieved_docs):
        """
        Reranks retrieved documents based on their relevance score.
        
        Args:
            query (str): User's query.
            retrieved_docs (list): List of retrieved documents with payloads.
        
        Returns:
            list: Filtered reranked documents above the threshold.
        """
        logger.info("Performing reranking of retrieved documents.")
        inputs = [f"Query: {query} Document: {doc['payload']['context']}" for doc in retrieved_docs]
        tokenized = self.tokenizer(inputs, padding=True, truncation=True, return_tensors="pt")
        
        with torch.no_grad():
            scores = self.reranker_model(**tokenized).logits.squeeze().tolist()
            
        for i, doc in enumerate(retrieved_docs):
            doc["score"] = scores[i]
            
        reranked_docs = sorted(retrieved_docs, key=lambda x: x["score"], reverse=True)
        
        reranked_filtered_docs = [doc for doc in reranked_docs if doc['score'] >= self.rerank_threshold]
        
        logger.info(f"Reranked {len(reranked_filtered_docs)} documents above threshold {self.rerank_threshold}")
        return reranked_filtered_docs
        
    def generate_context(self, query):
        """
        Retrieves and reranks documents to construct context for query response.
        
        Args:
            query (str): User's query.
        
        Returns:
            str: Concatenated context from top reranked documents.
        """
        logger.info(f"Retrieving and reranking context for query: {query}")
        results = self.retriever.search(query, self.top_k).model_dump()
        retrieved_docs = [dict(data) for data in results['points']]
        reranked_docs = self.rerank(query, retrieved_docs)
        if len(reranked_docs): 
            combined_prompt = []

            for entry in reranked_docs:
                context = entry["payload"]["context"]
                combined_prompt.append(context)
        else:
            logger.warning("No relevant documents found.")
            combined_prompt = ['No relevant documents found']

        return "\n\n---\n\n".join(combined_prompt)

    def query(self, query, img=None):
        """
        Processes a user query by retrieving relevant context and generating a response.
        
        Args:
            query (str): User's input query.
            img (optional): Optional image input for multimodal processing.
        
        Returns:
            str: Generated response from the conversational bot.
        """
        logger.info(f"Generating response for query: {query}")
        context = self.generate_context(query=query)
        prompt = self.qa_prompt_tmpl_str.format(context=context, query=query)
        response = self.llm.generate(prompt, image=img)
        
        logger.info("Response generated successfully.")
        return response