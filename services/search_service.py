import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from models.opportunity import Opportunity

class SearchService:
    """Service for semantic vector search using Sentence Transformers."""
    
    _model = None
    _index = None # numpy array of embeddings
    _metadata = [] # list of opportunity IDs matching the index
    
    def __init__(self, db: Session):
        self.db = db
        if SearchService._model is None:
            # Using a small, efficient model for local/cloud inference
            SearchService._model = SentenceTransformer('all-MiniLM-L6-v2')
            
    def index_opportunities(self):
        """Indexes all active opportunities into a vector space."""
        opportunities = self.db.query(Opportunity).filter(Opportunity.status == "active").all()
        
        if not opportunities:
            return
            
        texts = [f"{o.title} {o.description} {o.tags} {o.location}" for o in opportunities]
        embeddings = SearchService._model.encode(texts)
        
        SearchService._index = np.array(embeddings)
        SearchService._metadata = [o.id for o in opportunities]
        
        print(f"Indexed {len(opportunities)} opportunities for semantic search.")

    def search(self, query: str, limit: int = 10) -> List[Opportunity]:
        """Performs a semantic search for the given query."""
        if SearchService._index is None or len(SearchService._index) == 0:
            self.index_opportunities()
            
        if SearchService._index is None or len(SearchService._index) == 0:
            return []
            
        query_embedding = SearchService._model.encode([query])
        
        # Calculate cosine similarity
        similarities = np.dot(SearchService._index, query_embedding.T).flatten()
        # Sort indices by similarity
        top_indices = np.argsort(similarities)[::-1][:limit]
        
        top_ids = [SearchService._metadata[i] for i in top_indices]
        
        # Preserve order from top_ids
        results = []
        for opp_id in top_ids:
            opp = self.db.query(Opportunity).filter(Opportunity.id == opp_id).first()
            if opp:
                results.append(opp)
                
        return results

    @classmethod
    def clear_index(cls):
        """Resets the in-memory index."""
        cls._index = None
        cls._metadata = []
