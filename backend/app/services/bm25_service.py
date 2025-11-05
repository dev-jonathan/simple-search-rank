"""
Serviço de busca BM25 (Modelo Probabilístico).
"""
import re
from typing import List
from rank_bm25 import BM25Okapi
from app.models.schemas import ResultItem
from app.services.preprocessing import PreprocessingService
from app.utils.text_processing import extract_snippet


class BM25Service:
    """Implementação do modelo BM25."""
    
    def __init__(self, corpus_manager, preprocessing: PreprocessingService):
        """
        Inicializa o serviço BM25.
        
        Args:
            corpus_manager: Gerenciador do corpus
            preprocessing: Serviço de pré-processamento
        """
        self.corpus_manager = corpus_manager
        self.preprocessing = preprocessing
        self.bm25_index = None
        self.doc_ids: List[str] = []
        self._is_indexed = False
    
    def _prepare_corpus(self) -> List[List[str]]:
        """Prepara o corpus para BM25 (tokenizado)."""
        corpus = []
        self.doc_ids = []
        
        for doc_id in sorted(self.corpus_manager.processed_terms.keys()):
            # Obter termos processados do documento
            termos = self.corpus_manager.processed_terms[doc_id]
            # Criar lista de tokens (repetir conforme frequência)
            tokens = []
            for termo, freq in termos.items():
                tokens.extend([termo] * freq)
            
            corpus.append(tokens)
            self.doc_ids.append(doc_id)
        
        return corpus
    
    def _build_index(self):
        """Constrói o índice BM25."""
        if self._is_indexed:
            return
        
        corpus = self._prepare_corpus()
        if not corpus:
            return
        
        # Inicializar BM25 (k1 e b serão configuráveis na busca)
        self.bm25_index = BM25Okapi(corpus, k1=1.2, b=0.75)
        self._is_indexed = True
    
    def search(self, query: str, k1: float = 1.2, b: float = 0.75, top_k: int = 20) -> List[ResultItem]:
        """
        Busca documentos usando BM25.
        
        Args:
            query: Consulta de busca
            k1: Parâmetro k₁ (saturação de frequência)
            b: Parâmetro b (normalização por tamanho)
            top_k: Número máximo de resultados
        
        Returns:
            Lista de resultados ordenados por score BM25
        """
        self._build_index()
        
        if not self.bm25_index:
            return []
        
        # Processar consulta
        query_terms = self.preprocessing.process_query(query)
        if not query_terms:
            return []
        
        # Atualizar parâmetros do BM25 se necessário
        if k1 != self.bm25_index.k1 or b != self.bm25_index.b:
            # Reconstruir com novos parâmetros (simplificado - idealmente cachear)
            corpus = self._prepare_corpus()
            self.bm25_index = BM25Okapi(corpus, k1=k1, b=b)
        
        # Calcular scores
        scores = self.bm25_index.get_scores(query_terms)
        
        # Criar lista de (doc_id, score) e ordenar
        doc_scores = [
            (self.doc_ids[i], score)
            for i, score in enumerate(scores)
            if score > 0
        ]
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Criar resultados (garantir que não há duplicações)
        results = []
        seen_doc_ids = set()
        
        for doc_id, score in doc_scores[:top_k]:
            # Verificar duplicação (não deveria acontecer, mas por segurança)
            if doc_id in seen_doc_ids:
                print(f"[DEBUG BM25] ⚠️ Duplicação detectada: {doc_id}")
                continue
            seen_doc_ids.add(doc_id)
            
            doc_info = self.corpus_manager.get_document(doc_id)
            if not doc_info:
                print(f"[DEBUG BM25] ⚠️ Documento não encontrado: {doc_id}")
                continue
            
            text = self.corpus_manager.get_document_text(doc_id) or ""
            snippet, matched_words = extract_snippet(text, query_terms, context_length=250, original_query=query)
            
            results.append(ResultItem(
                id=doc_id,
                title=doc_info["title"],
                score=float(score),
                snippet=snippet,
                matchedWords=matched_words,
                filename=doc_info.get("filename")
            ))
        
        print(f"[DEBUG BM25] Total de resultados retornados: {len(results)} (únicos: {len(seen_doc_ids)})")
        
        return results
