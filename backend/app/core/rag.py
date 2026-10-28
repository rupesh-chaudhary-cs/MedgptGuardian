import torch
import os
import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

logger = logging.getLogger(__name__)

class MedicalEvidenceEngine:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.persist_directory = os.path.join(self.base_dir, "chroma_db")
        
        logger.info("Initializing Local HuggingFace Embeddings (CPU Query Mode)...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.db = self._initialize_db()

    def _initialize_db(self):
        if not os.path.exists(self.persist_directory) or not os.listdir(self.persist_directory):
            logger.error("CRITICAL: Pre-built chroma_db folder missing in backend directory!")
            raise FileNotFoundError("Missing production vector database.")
            
        logger.info("Loading production-scale NIH MedQuAD ChromaDB vector store...")
        return Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)

    def retrieve_guideline(self, query: str, k: int = 3) -> str:
        """Retrieves the top k most mathematically similar NIH clinical guidelines."""
        results = self.db.similarity_search(query, k=k)
        if not results:
            return "No matching clinical protocols found in the NIH MedQuAD dataset."
        
        combined_evidence = "\n\n".join([doc.page_content for doc in results])
        return combined_evidence

# Singleton instance
evidence_engine = MedicalEvidenceEngine()