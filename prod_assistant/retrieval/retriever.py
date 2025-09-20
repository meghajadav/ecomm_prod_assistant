import os
from langchain_core.documents import Document
from utils.config_loader import load_config
from utils.model_loader import ModelLoader
from dotenv import load_dotenv
from langchain_astradb import AstraDBVectorStore
import sys
from pathlib import Path
from langchain.retrievers.document_compressors import LLMChainFilter
from langchain.retrievers import ContextualCompressionRetriever

class Retriever:

    def __init__(self):
        self.llm = ModelLoader()
        self.config = load_config()
        self._load_env_variables()
        self.vstore = None
        self.retriever = None

    def _load_env_variables(self):
        load_dotenv()

        required_variables = ['GROQ_API_KEY','ASTRA_DB_API_ENDPOINT','ASTRA_DB_APPLICATION_TOKEN','ASTRA_DB_KEYSPACE']

        missing_variables = [var for var in required_variables if os.getenv(var) is None]

        if missing_variables:
            raise EnvironmentError(f"Missing environment variables: {missing_variables}")
        
        self.GROQ_API_KEY=os.getenv('GROQ_API_KEY')
        self.ASTRA_DB_API_ENDPOINT=os.getenv('ASTRA_DB_API_ENDPOINT')
        self.ASTRA_DB_APPLICATION_TOKEN=os.getenv('ASTRA_DB_APPLICATION_TOKEN')
        self.ASTRA_DB_KEYSPACE=os.getenv('ASTRA_DB_KEYSPACE')



    def load_retriever(self):
        collection_name = self.config['astra_db']['collection_name']
        if not self.vstore:
            self.vstore = AstraDBVectorStore(
                embedding=self.llm.load_embeddings(),
                collection_name=collection_name,
                api_endpoint=self.ASTRA_DB_API_ENDPOINT,
                token=self.ASTRA_DB_APPLICATION_TOKEN,
                namespace=self.ASTRA_DB_KEYSPACE
            )

        if not self.retriever:
            top_k = self.config['retriever']['top_k'] if "retriever" in self.config else 3
            mmr_retriever = self.vstore.as_retriever(
                search_type='mmr',
                search_kwargs={"k":top_k},
                fetch_type=20,
                lambda_mult=0.7,
                score_threshold=0.3)
            
        llm = self.llm.load_llm()
        compressor = LLMChainFilter.from_llm(llm)
        self.retriever=ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever = mmr_retriever
        )
        return self.retriever


    def call_retriver(self, query):
        retriever = self.load_retriever()
        output = retriever.invoke(query)
        return output