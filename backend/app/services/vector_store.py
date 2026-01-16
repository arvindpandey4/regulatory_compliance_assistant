import os
import pickle
from typing import List, Tuple
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

class VectorStoreService:
    _instance = None

    def __new__(cls, index_path: str = "data/faiss_index"):
        if cls._instance is None:
            cls._instance = super(VectorStoreService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, index_path: str = "data/faiss_index"):
        if getattr(self, "initialized", False):
            return
            
        self.index_path = index_path
        
        self.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        
        print("Loading Reranker Model...")
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        
        self.vector_db = None
        self._load_index()
        self.initialized = True

    def _load_index(self):
        if os.path.exists(self.index_path):
            try:
                self.vector_db = FAISS.load_local(
                    self.index_path, 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                print("Loaded existing FAISS index.")
            except Exception as e:
                print(f"Failed to load index: {e}. Creating new one.")
                self.vector_db = None
        else:
            print("No existing index found. Starting fresh.")

    def add_documents(self, documents: List[Document]):
        if not documents:
            return

        if self.vector_db is None:
            self.vector_db = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vector_db.add_documents(documents)
        
        self.save_index()

    def search(self, query: str, k: int = 4) -> List[Document]:
        if self.vector_db is None:
            return []
        
        # 1. Broad Search with scores
        # Get similarity scores to enable fast-track detection
        candidates_with_scores = self.vector_db.similarity_search_with_score(query, k=k*3)
        
        if not candidates_with_scores:
            return []
        
        # FAST TRACK: Check if top result has very high similarity (Golden KB match)
        # Similarity scores in FAISS are distances (lower = better for L2, higher = better for cosine)
        # For the default L2 distance, we check if distance is very low
        top_doc, top_score = candidates_with_scores[0]
        
        # If top result is a Golden KB entry with high confidence, skip reranking
        # L2 distance: lower is better, typically < 0.5 is excellent
        # Check metadata to confirm it's a KB entry
        is_kb_entry = top_doc.metadata.get("type") == "kb_entry"
        is_high_confidence = top_score < 0.5  # Low distance = high similarity
        
        if is_kb_entry and is_high_confidence:
            print(f"[FAST TRACK] Golden KB match detected (score: {top_score:.4f}), skipping reranking")
            # Return top k candidates directly without reranking
            return [doc for doc, score in candidates_with_scores[:k]]
        
        # 2. Standard Path: Reranking (The Advanced Step)
        # Extract just the documents for reranking
        candidates = [doc for doc, score in candidates_with_scores]
        
        # We pair the query with each document text: [(Query, Doc1), (Query, Doc2)...]
        model_inputs = [[query, doc.page_content] for doc in candidates]
        
        # The CrossEncoder gives a precise relevance score (logits) for each pair
        scores = self.reranker.predict(model_inputs)
        
        # 3. Sort & Filter
        # Combine docs with scores, sort descending
        results_with_scores = sorted(
            zip(candidates, scores), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Return top k truly relevant documents
        return [doc for doc, score in results_with_scores[:k]]

    def save_index(self):
        if self.vector_db:
            self.vector_db.save_local(self.index_path)
