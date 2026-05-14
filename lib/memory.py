"""ClawsJoy 长期记忆库"""
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
import hashlib

class ClawsJoyMemory:
    def __init__(self, persist_dir="data/memory"):
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        try:
            self.collection = self.client.get_collection("clawsjoy_memory")
        except:
            self.collection = self.client.create_collection(
                name="clawsjoy_memory",
                embedding_function=self.embedding_fn
            )
    
    def remember(self, fact, category="general"):
        doc_id = hashlib.md5(fact.encode()).hexdigest()
        self.collection.upsert(
            ids=[doc_id],
            documents=[fact],
            metadatas=[{"category": category}]
        )
        return True
    
    def recall(self, query, category=None, n=5):
        where = {"category": category} if category else None
        results = self.collection.query(
            query_texts=[query],
            n_results=n,
            where=where
        )
        if results['documents'] and results['documents'][0]:
            return results['documents'][0]
        return []
    
    def get_all(self):
        return self.collection.get()

memory = ClawsJoyMemory()
