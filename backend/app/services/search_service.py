"""
Serviço unificado de busca que orquestra TF-IDF e BM25.
"""
import time
from typing import Dict
from app.models.schemas import ResultItem, Metrics
from app.services.tfidf_service import TFIDFService
from app.services.bm25_service import BM25Service
from app.services.preprocessing import PreprocessingService
from app.services.corpus_manager import CorpusManager


class SearchService:
    """Serviço principal de busca."""
    
    def __init__(self, corpus_manager: CorpusManager):
        """
        Inicializa o serviço de busca.
        
        Args:
            corpus_manager: Gerenciador do corpus
        """
        self.corpus_manager = corpus_manager
        # Usar o mesmo preprocessing do corpus_manager para consistência
        self.preprocessing = corpus_manager.preprocessing
        self.tfidf_service = TFIDFService(corpus_manager, self.preprocessing)
        self.bm25_service = BM25Service(corpus_manager, self.preprocessing)
    
    async def search(
        self,
        query: str,
        k1: float = 1.2,
        b: float = 0.75,
        tf_weight: str = "log",
        top_k: int = None
    ) -> Dict:
        """
        Realiza busca usando ambos os modelos.
        
        Args:
            query: Consulta de busca
            k1: Parâmetro k₁ do BM25
            b: Parâmetro b do BM25
            tf_weight: Tipo de peso para TF-IDF (apenas "log" suportado por enquanto)
            top_k: Número máximo de resultados por modelo (None = retornar todos)
        
        Returns:
            Dicionário com resultados TF-IDF, BM25 e métricas
        """
        start_time = time.perf_counter()
        
        # Pré-processamento da consulta
        preprocess_start = time.perf_counter()
        query_terms = self.preprocessing.process_query(query)
        preprocess_time = (time.perf_counter() - preprocess_start) * 1000  # ms
        
        if not query_terms:
            return {
                "tfidf": [],
                "bm25": [],
                "metrics": Metrics(
                    preprocessTime=preprocess_time,
                    tfidfTime=0.0,
                    bm25Time=0.0
                )
            }
        
        # Usar número total de documentos se não especificado
        if top_k is None:
            total_docs = len(self.corpus_manager.get_all_documents())
            top_k = total_docs  # Retornar todos os documentos por padrão
        
        # Busca TF-IDF
        tfidf_start = time.perf_counter()
        tfidf_results = self.tfidf_service.search(query, tf_weight=tf_weight, top_k=top_k)
        tfidf_time = (time.perf_counter() - tfidf_start) * 1000  # ms
        
        # Busca BM25
        bm25_start = time.perf_counter()
        bm25_results = self.bm25_service.search(query, k1=k1, b=b, top_k=top_k)
        bm25_time = (time.perf_counter() - bm25_start) * 1000  # ms
        
        metrics = Metrics(
            preprocessTime=preprocess_time,
            tfidfTime=tfidf_time,
            bm25Time=bm25_time
        )
        
        return {
            "tfidf": tfidf_results,
            "bm25": bm25_results,
            "metrics": metrics
        }

