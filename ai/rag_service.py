"""
Simple, efficient Python-based Retrieval-Augmented Generation (RAG) engine for PrepMate.
Indexes domain-specific interview knowledge files using TF-IDF and cosine similarity.
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import config

class KnowledgeChunk:
    """Represents an atomic knowledge chunk retrieved from the local knowledge base."""
    def __init__(self, doc_id: str, source_file: str, topic: str, content: str):
        self.doc_id = doc_id
        self.source_file = source_file
        self.topic = topic
        self.content = content.strip()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "source_file": self.source_file,
            "topic": self.topic,
            "content": self.content
        }


class InterviewRAGService:
    """
    RAG engine that indexes files in knowledge_base/ and provides
    fast, contextual retrieval for IBM Granite prompting.
    """
    def __init__(self, kb_dir: Optional[Path] = None):
        self.kb_dir = kb_dir or config.KNOWLEDGE_BASE_DIR
        self.chunks: List[KnowledgeChunk] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self._load_and_index()

    def _load_and_index(self):
        """Parse all .txt files in the knowledge base directory and build TF-IDF matrix."""
        self.chunks = []
        if not os.path.exists(self.kb_dir):
            return

        chunk_counter = 0
        for filename in sorted(os.listdir(self.kb_dir)):
            if not filename.endswith('.txt'):
                continue
            filepath = os.path.join(self.kb_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()

                # Split on section markers or double newlines
                sections = re.split(r'\n(?=\[Topic:)', text)
                for section in sections:
                    section = section.strip()
                    if not section:
                        continue

                    # Extract topic line if present
                    topic = "General Knowledge"
                    topic_match = re.search(r'\[Topic:\s*(.*?)\]', section)
                    if topic_match:
                        topic = topic_match.group(1).strip()

                    chunk_counter += 1
                    doc_id = f"KB-{chunk_counter:03d}"
                    self.chunks.append(KnowledgeChunk(
                        doc_id=doc_id,
                        source_file=filename,
                        topic=topic,
                        content=section
                    ))
            except Exception as e:
                print(f"[RAG] Error reading file {filename}: {e}")

        if self.chunks:
            corpus = [f"{c.topic} {c.content}" for c in self.chunks]
            self.vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=5000
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            print(f"[RAG] Successfully indexed {len(self.chunks)} knowledge chunks from {self.kb_dir}")

    def retrieve(self, query: str, top_k: int = 3, threshold: float = 0.05) -> List[Dict[str, Any]]:
        """
        Retrieve the top_k most relevant knowledge chunks for a given query or context.
        Returns list of dicts with doc_id, source_file, topic, content, and similarity_score.
        """
        if not self.chunks or not self.vectorizer or self.tfidf_matrix is None or not query.strip():
            return []

        try:
            query_vec = self.vectorizer.transform([query])
            sim_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

            # Rank by score descending
            ranked_indices = np.argsort(sim_scores)[::-1]

            results = []
            for idx in ranked_indices:
                score = float(sim_scores[idx])
                if score < threshold and len(results) >= 1:
                    break
                chunk = self.chunks[idx]
                results.append({
                    "doc_id": chunk.doc_id,
                    "source_file": chunk.source_file,
                    "topic": chunk.topic,
                    "content": chunk.content,
                    "score": round(score, 3)
                })
                if len(results) >= top_k:
                    break

            return results
        except Exception as e:
            print(f"[RAG] Retrieval error: {e}")
            return []

    def format_context_for_prompt(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks into a clean, structured context string for Granite prompts."""
        if not retrieved_chunks:
            return "No specific reference domain knowledge retrieved from local base."

        formatted_sections = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            source = chunk.get("source_file", "unknown")
            topic = chunk.get("topic", "General")
            snippet = chunk.get("content", "").strip()
            formatted_sections.append(
                f"--- Reference Document #{i} [Source: {source} | Topic: {topic}] ---\n{snippet}"
            )

        return "\n\n".join(formatted_sections)

# Global singleton instance
rag_service = InterviewRAGService()

