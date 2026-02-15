import chromadb
from chromadb.config import Settings
import ollama

class FinancialSituationMemory:
    def __init__(self, name, config):
        self.client = chromadb.Client(Settings(allow_reset=True))
        self.collection = self.client.get_or_create_collection(name=name)

    def get_embedding(self, text):
        response = ollama.embeddings(
            model="nomic-embed-text",
            prompt=text
        )
        return response["embedding"]

    def add_situations(self, situations_and_advice):
        for idx, (situation, rec) in enumerate(situations_and_advice):
            self.collection.add(
                documents=[situation],
                metadatas=[{"recommendation": rec}],
                embeddings=[self.get_embedding(situation)],
                ids=[str(idx)],
            )

    def get_memories(self, situation, n_matches=1):
        emb = self.get_embedding(situation)
        res = self.collection.query(
            query_embeddings=[emb],
            n_results=n_matches
        )
        return res
