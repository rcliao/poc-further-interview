"""
RAG (Retrieval-Augmented Generation) utilities for knowledge base queries
"""
import os
from typing import List, Dict, Optional
from openai import OpenAI
from sales_agent.models import CommunityKnowledge
from pgvector.django import L2Distance


class KnowledgeRetriever:
    """
    Retrieves relevant knowledge from the community knowledge base
    using semantic search with pgvector
    """

    def __init__(self):
        """Initialize OpenAI client for embeddings"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError('OPENAI_API_KEY not set in environment')
        self.client = OpenAI(api_key=api_key)

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a text query using OpenAI

        Args:
            text: Query text to embed

        Returns:
            List of floats representing the embedding vector
        """
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
            dimensions=1536
        )
        return response.data[0].embedding

    def search(
        self,
        query: str,
        category_filter: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Search the knowledge base using semantic similarity

        Args:
            query: Natural language query
            category_filter: Optional list of categories to filter by
            top_k: Number of results to return

        Returns:
            List of dictionaries containing matched knowledge items with similarity scores
        """
        # Generate embedding for query
        query_embedding = self.generate_embedding(query)

        # Build query
        queryset = CommunityKnowledge.objects.all()

        # Apply category filter if provided
        if category_filter:
            queryset = queryset.filter(category__in=category_filter)

        # Order by similarity using pgvector L2 distance
        # Note: Lower L2 distance = higher similarity
        results = queryset.order_by(
            L2Distance('embedding', query_embedding)
        )[:top_k]

        # Format results
        formatted_results = []
        for item in results:
            # Calculate similarity score (convert L2 distance to similarity)
            # For display purposes, we'll use a simple transformation
            # Note: This is a rough approximation, actual similarity can vary
            distance = L2Distance('embedding', query_embedding)
            similarity_score = 1.0 / (1.0 + float(str(distance)))  # Rough approximation

            formatted_results.append({
                'id': str(item.id),
                'category': item.category,
                'content': item.content,
                'metadata': item.metadata,
                'similarity_score': similarity_score,
            })

        return formatted_results

    def search_by_category(
        self,
        query: str,
        category: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Search within a specific category

        Args:
            query: Natural language query
            category: Category to search within
            top_k: Number of results to return

        Returns:
            List of matched knowledge items
        """
        return self.search(query, category_filter=[category], top_k=top_k)

    def get_all_in_category(self, category: str) -> List[Dict]:
        """
        Get all knowledge items in a category

        Args:
            category: Category to retrieve

        Returns:
            List of all items in the category
        """
        items = CommunityKnowledge.objects.filter(category=category)
        return [
            {
                'id': str(item.id),
                'category': item.category,
                'content': item.content,
                'metadata': item.metadata,
            }
            for item in items
        ]


# Singleton instance for easy import
retriever = KnowledgeRetriever()
