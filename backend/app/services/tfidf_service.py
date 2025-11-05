"""
Serviço de busca TF-IDF (Modelo Vetorial).
"""
import numpy as np
from math import log10
from typing import List, Dict
from collections import defaultdict
import logging
from app.models.schemas import ResultItem
from app.services.preprocessing import PreprocessingService
from app.utils.text_processing import extract_snippet

logger = logging.getLogger(__name__)


class TFIDFService:
    """Implementação do modelo TF-IDF."""
    
    def __init__(self, corpus_manager, preprocessing: PreprocessingService):
        """
        Inicializa o serviço TF-IDF.
        
        Args:
            corpus_manager: Gerenciador do corpus
            preprocessing: Serviço de pré-processamento
        """
        self.corpus_manager = corpus_manager
        self.preprocessing = preprocessing
        self.tf_idf_index: Dict[str, Dict[str, float]] = {}
        self.idf: Dict[str, float] = {}
        self._is_indexed = False
    
    def _build_index(self):
        """Constrói o índice TF-IDF."""
        if self._is_indexed:
            return
        
        processed_terms = self.corpus_manager.processed_terms
        N = len(processed_terms)  # Número total de documentos
        
        if N == 0:
            print("[DEBUG TF-IDF] ⚠️ Nenhum documento processado!")
            return
        
        print(f"[DEBUG TF-IDF] Construindo índice para {N} documentos...")
        
        # Calcular DF (Document Frequency) para cada termo
        df = defaultdict(int)
        for termos_doc in processed_terms.values():
            for termo in termos_doc.keys():
                df[termo] += 1
        
        print(f"[DEBUG TF-IDF] Total de termos únicos no índice: {len(df)}")
        
        # Calcular IDF (Inverse Document Frequency)
        # Usar fórmula que evita IDF = 0: log10((N + 1) / df) ou log10(1 + N / df)
        # Isso garante que termos que aparecem em todos documentos ainda tenham algum peso
        self.idf = {}
        for termo in df:
            df_val = df[termo]
            # Fórmula: log10(1 + N / df) - evita IDF = 0 mesmo quando df = N
            # Alternativa comum: log10((N + 1) / df) também funciona
            self.idf[termo] = log10(1 + N / df_val)
            if df_val == N:
                print(f"[DEBUG TF-IDF] Termo '{termo}' aparece em TODOS os documentos (df={df_val}, N={N}), IDF={self.idf[termo]:.4f}")
        
        # DEBUG: Verificar alguns termos específicos
        termos_importantes = ['brasil', 'engenharia', 'adele']
        for termo in termos_importantes:
            if termo in self.idf:
                print(f"[DEBUG TF-IDF] Termo '{termo}': df={df.get(termo, 0)}, N={N}, IDF={self.idf[termo]:.4f}")
        
        # Calcular TF-IDF para cada termo em cada documento
        self.tf_idf_index = {}
        for doc_id, termos in processed_terms.items():
            self.tf_idf_index[doc_id] = {}
            for termo, freq in termos.items():
                # TF com log: 1 + log10(freq)
                tf = 1 + log10(freq) if freq > 0 else 0
                self.tf_idf_index[doc_id][termo] = tf * self.idf[termo]
        
        self._is_indexed = True
        print(f"[DEBUG TF-IDF] ✅ Índice construído! Total de termos únicos: {len(self.idf)}")
    
    def search(self, query: str, tf_weight: str = "log", top_k: int = 20) -> List[ResultItem]:
        """
        Busca documentos usando TF-IDF.
        
        Args:
            query: Consulta de busca
            tf_weight: Tipo de peso ("log", "raw", "binary") - apenas "log" implementado
            top_k: Número máximo de resultados
        
        Returns:
            Lista de resultados ordenados por relevância
        """
        self._build_index()
        
        # Processar consulta
        query_terms = self.preprocessing.process_query(query)
        
        # DEBUG: Log dos termos processados
        print(f"[DEBUG TF-IDF] Query original: '{query}'")
        print(f"[DEBUG TF-IDF] Termos processados: {query_terms}")
        
        if not query_terms:
            print("[DEBUG TF-IDF] Nenhum termo processado, retornando vazio")
            return []
        
        # Verificar quais termos da query estão no índice
        termos_encontrados = [t for t in query_terms if t in self.idf]
        termos_nao_encontrados = [t for t in query_terms if t not in self.idf]
        
        # DEBUG: Log de termos encontrados/não encontrados
        print(f"[DEBUG TF-IDF] Termos encontrados no índice: {termos_encontrados}")
        if termos_nao_encontrados:
            print(f"[DEBUG TF-IDF] ⚠️ Termos NÃO encontrados no índice: {termos_nao_encontrados}")
            # Mostrar alguns exemplos de termos similares no índice
            if len(self.idf) > 0:
                # Procurar termos similares aos não encontrados
                termos_exemplo = []
                for termo_nao_encontrado in termos_nao_encontrados[:3]:  # Primeiros 3
                    similares = [t for t in list(self.idf.keys())[:100] if termo_nao_encontrado[:3] in t[:5] or t[:3] in termo_nao_encontrado[:5]]
                    termos_exemplo.extend(similares[:3])
                if termos_exemplo:
                    print(f"[DEBUG TF-IDF] Termos similares encontrados no índice: {termos_exemplo[:5]}")
                print(f"[DEBUG TF-IDF] Total de termos no índice: {len(self.idf)}")
        
        # Se nenhum termo encontrado, retornar vazio
        if not termos_encontrados:
            print("[DEBUG TF-IDF] ❌ Nenhum termo da query encontrado no índice, retornando vazio")
            return []
        
        query_terms = termos_encontrados
        
        # Contar frequência de termos na query para calcular TF
        query_term_freq = {}
        for termo in query_terms:
            query_term_freq[termo] = query_term_freq.get(termo, 0) + 1
        
        # Criar vetor da consulta usando TF-IDF (não apenas IDF)
        query_tfidf_values = []
        for termo in query_terms:
            # Calcular TF da query (com log, igual aos documentos)
            tf_query = query_term_freq.get(termo, 0)
            if tf_query > 0:
                tf_query = 1 + log10(tf_query)
            else:
                tf_query = 0
            
            # Calcular TF-IDF: TF * IDF
            idf_val = self.idf.get(termo, 0)
            tfidf_val = tf_query * idf_val
            query_tfidf_values.append(tfidf_val)
            
            # DEBUG: Verificar valor IDF de cada termo
            if idf_val == 0:
                print(f"[DEBUG TF-IDF] ⚠️ ATENÇÃO: Termo '{termo}' tem IDF = 0!")
                print(f"[DEBUG TF-IDF]   Verificando se termo está no índice: {termo in self.idf}")
                if termo in self.idf:
                    print(f"[DEBUG TF-IDF]   Valor do IDF['{termo}']: {self.idf[termo]}")
                    # Verificar em quantos documentos o termo aparece
                    docs_com_termo = sum(1 for doc_id in self.tf_idf_index.keys() if termo in self.tf_idf_index[doc_id])
                    print(f"[DEBUG TF-IDF]   Documentos com este termo: {docs_com_termo}")
        
        query_vector = np.array(query_tfidf_values)
        
        print(f"[DEBUG TF-IDF] Vetor da consulta (valores TF-IDF): {query_vector}")
        print(f"[DEBUG TF-IDF] Soma do vetor da consulta: {np.sum(query_vector)}")
        
        if query_vector.size == 0 or np.sum(query_vector) == 0:
            print("[DEBUG TF-IDF] ⚠️ Vetor da consulta está vazio ou soma é zero!")
            return []
        
        # Verificar se há apenas 1 termo na query (caso especial)
        is_single_term = len(query_terms) == 1
        
        # Normalizar vetor da consulta
        query_norm = np.linalg.norm(query_vector)
        print(f"[DEBUG TF-IDF] Norma do vetor da consulta: {query_norm}")
        if query_norm > 0:
            query_vector_normalized = query_vector / query_norm
        else:
            print("[DEBUG TF-IDF] ⚠️ Norma do vetor da consulta é zero!")
            return []
        
        # Calcular similaridade para cada documento
        similarities = {}
        documentos_com_termo = 0
        documentos_sem_termo = 0
        documentos_com_vetor_zero = 0
        
        for doc_id in self.tf_idf_index.keys():
            # Criar vetor do documento
            doc_vector = np.array([
                self.tf_idf_index[doc_id].get(termo, 0) for termo in query_terms
            ])
            
            if doc_vector.size != query_vector.size:
                continue
            
            # Verificar se documento tem o termo
            tem_termo = np.sum(doc_vector) > 0
            if tem_termo:
                documentos_com_termo += 1
            else:
                documentos_sem_termo += 1
                continue
            
            # CASO ESPECIAL: Query com apenas 1 termo
            # Usar TF-IDF bruto (não normalizado) para diferenciar documentos
            # Normalização faria todos terem similaridade = 1.0
            if is_single_term:
                # Usar TF-IDF bruto como score (já normalizado pela frequência)
                similarity = float(doc_vector[0])
                doc_norm = doc_vector[0]  # Para debug
                doc_vector_normalized = doc_vector  # Não normalizar
            else:
                # Query com múltiplos termos: usar similaridade do cosseno normalizada
                doc_norm = np.linalg.norm(doc_vector)
                if doc_norm > 0:
                    doc_vector_normalized = doc_vector / doc_norm
                else:
                    documentos_com_vetor_zero += 1
                    continue
                
                # Calcular similaridade do cosseno
                similarity = np.dot(doc_vector_normalized, query_vector_normalized)
            
            # DEBUG: Mostrar primeiros 3 documentos
            if len(similarities) < 3:
                print(f"[DEBUG TF-IDF] Doc {doc_id}: vetor={doc_vector}, norm={doc_norm}, similarity={similarity}")
            
            if similarity > 0:
                similarities[doc_id] = similarity
        
        total_docs_no_corpus = len(self.tf_idf_index.keys())
        print(f"[DEBUG TF-IDF] Total de documentos no corpus: {total_docs_no_corpus}")
        print(f"[DEBUG TF-IDF] Documentos com termo: {documentos_com_termo}, sem termo: {documentos_sem_termo}, vetor zero: {documentos_com_vetor_zero}")
        print(f"[DEBUG TF-IDF] Documentos com similaridade > 0: {len(similarities)} (esperado: {documentos_com_termo})")
        if similarities:
            top_3 = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"[DEBUG TF-IDF] Top 3 similaridades: {top_3}")
        else:
            print("[DEBUG TF-IDF] ⚠️ Nenhuma similaridade > 0 encontrada")
        
        # Ordenar por similaridade
        sorted_docs = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        
        # Criar resultados (garantir que não há duplicações)
        results = []
        seen_doc_ids = set()
        
        for doc_id, score in sorted_docs[:top_k]:
            # Verificar duplicação (não deveria acontecer, mas por segurança)
            if doc_id in seen_doc_ids:
                print(f"[DEBUG TF-IDF] ⚠️ Duplicação detectada: {doc_id}")
                continue
            seen_doc_ids.add(doc_id)
            
            doc_info = self.corpus_manager.get_document(doc_id)
            if not doc_info:
                print(f"[DEBUG TF-IDF] ⚠️ Documento não encontrado: {doc_id}")
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
        
        print(f"[DEBUG TF-IDF] Total de resultados retornados: {len(results)} (únicos: {len(seen_doc_ids)})")
        
        return results
