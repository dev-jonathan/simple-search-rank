"""
Gerenciador do corpus de documentos em memória.
"""
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict
from app.services.pdf_parser import PDFParser
from app.services.preprocessing import PreprocessingService
from app.services.cache_service import CacheService


class CorpusManager:
    """Gerencia o corpus de documentos."""
    
    def __init__(self, corpus_path: Path, use_cache: bool = True, cache_dir: Path = None):
        """
        Inicializa o gerenciador de corpus.
        
        Args:
            corpus_path: Caminho para a pasta com os PDFs
            use_cache: Se True, usa cache para evitar reprocessar PDFs (padrão: True)
            cache_dir: Diretório do cache (padrão: backend/cache/)
        """
        self.corpus_path = Path(corpus_path)
        self.documents: List[Dict] = []
        self.texts: Dict[str, str] = {}  # Texto completo por doc_id
        self.processed_terms: Dict[str, Dict[str, int]] = {}  # Termos processados por doc_id
        self.pdf_parser = PDFParser()
        self.preprocessing = PreprocessingService(use_spacy=True)  # Usar spaCy para lematização
        self._is_loaded = False
        self.use_cache = use_cache
        self.cache_service = CacheService(cache_dir) if use_cache else None
    
    def load_corpus(self, max_documents: int = None, force_reload: bool = False):
        """
        Carrega PDFs do corpus, usando cache se disponível.
        
        Args:
            max_documents: Número máximo de documentos a carregar (None = todos)
            force_reload: Se True, força reprocessamento mesmo com cache válido
        """
        if self._is_loaded and not force_reload:
            return
        
        if not self.corpus_path.exists():
            raise FileNotFoundError(f"Pasta do corpus não encontrada: {self.corpus_path}")
        
        # Tentar carregar do cache primeiro
        if self.use_cache and self.cache_service and not force_reload:
            # Nota: max_documents não é suportado com cache (cache sempre tem todos os documentos)
            if max_documents is None:
                # Pular validação de hash na primeira vez para acelerar (só verificar se arquivos existem)
                # Se quiser validação completa, remover skip_hash_check=True
                if self.cache_service.is_cache_valid(self.corpus_path, skip_hash_check=True):
                    cached_data = self.cache_service.load_cache()
                    if cached_data:
                        self.documents = cached_data['documents']
                        self.texts = cached_data['texts']
                        self.processed_terms = cached_data['processed_terms']
                        self._is_loaded = True
                        print(f"✅ Corpus carregado do cache: {len(self.documents)} documentos")
                        return
        
        # Cache inválido, não disponível, ou max_documents especificado - processar PDFs
        print("🔄 Processando PDFs (cache não disponível ou inválido)...")
        self._process_pdfs(max_documents)
        
        # Salvar no cache se habilitado e não foi limitado por max_documents
        if self.use_cache and self.cache_service and max_documents is None:
            self.cache_service.save_cache(
                documents=self.documents,
                texts=self.texts,
                processed_terms=self.processed_terms,
                corpus_path=self.corpus_path
            )
    
    def _process_pdfs(self, max_documents: int = None):
        """
        Processa PDFs do corpus (sem cache).
        
        Args:
            max_documents: Número máximo de documentos a processar (None = todos)
        """
        # Buscar todos os PDFs
        pdf_files = sorted(list(self.corpus_path.glob("*.pdf")))
        
        # Limitar número de documentos se especificado
        if max_documents:
            pdf_files = pdf_files[:max_documents]
        
        total_files = len(pdf_files)
        print(f"📚 Processando {total_files} documentos do corpus...")
        
        for i, pdf_path in enumerate(pdf_files):
            try:
                doc_id = f"doc_{i+1}"
                
                # Extrair texto
                texto = self.pdf_parser.extract_text(pdf_path)
                if not texto.strip():
                    print(f"⚠️  PDF vazio: {pdf_path.name}")
                    continue
                
                # Processar termos
                termos = self.preprocessing.process_text(texto)
                
                # Criar documento
                documento = {
                    "id": doc_id,
                    "title": pdf_path.stem.replace("_", " "),
                    "title_raw": pdf_path.stem,  # Título com underscores preservados
                    "filename": pdf_path.name,
                    "text_length": len(texto),
                    "term_count": len(termos)
                }
                
                self.documents.append(documento)
                self.texts[doc_id] = texto
                self.processed_terms[doc_id] = termos
                
                if (i + 1) % 10 == 0 or (i + 1) == total_files:
                    print(f"  Processados {i+1}/{total_files} documentos...")
                    
            except Exception as e:
                print(f"❌ Erro ao processar {pdf_path.name}: {e}")
                continue
        
        self._is_loaded = True
        print(f"✅ Corpus processado: {len(self.documents)} documentos")
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Retorna um documento por ID."""
        for doc in self.documents:
            if doc["id"] == doc_id:
                return doc
        return None
    
    def get_document_text(self, doc_id: str) -> Optional[str]:
        """Retorna o texto completo de um documento."""
        return self.texts.get(doc_id)
    
    def get_all_documents(self) -> List[Dict]:
        """Retorna todos os documentos."""
        return self.documents
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do corpus."""
        if not self.documents:
            return {
                "total_documents": 0,
                "total_terms": 0,
                "avg_doc_length": 0
            }
        
        # Contar termos únicos
        all_terms = set()
        for termos in self.processed_terms.values():
            all_terms.update(termos.keys())
        
        total_terms = len(all_terms)
        avg_length = sum(doc["text_length"] for doc in self.documents) / len(self.documents)
        
        return {
            "total_documents": len(self.documents),
            "total_terms": total_terms,
            "avg_doc_length": int(avg_length)
        }
    
    def generate_frequency_report(self, output_path: Path = None) -> str:
        """
        Gera relatório de frequências de termos no formato:
        palavra/frequencia_total -> titledoc/freq titledocx/freq
        
        Args:
            output_path: Caminho para salvar o arquivo TXT (None = não salva)
        
        Returns:
            Conteúdo do relatório como string
        """
        if not self.processed_terms:
            return ""
        
        # Calcular frequências totais por termo
        frequencias_totais = {}
        for doc_id, termos in self.processed_terms.items():
            for termo, freq in termos.items():
                frequencias_totais[termo] = frequencias_totais.get(termo, 0) + freq
        
        # Criar mapeamento de doc_id para título (com underscores)
        doc_titles = {}
        for doc in self.documents:
            # Usar title_raw se existir, senão usar filename sem extensão
            doc_titles[doc["id"]] = doc.get("title_raw", Path(doc["filename"]).stem)
        
        # Gerar linhas do relatório
        linhas = []
        for termo, freq_total in sorted(frequencias_totais.items(), key=lambda x: x[0]):
            # Obter detalhes por documento e contar quantos documentos possuem o termo
            detalhes_por_doc = []
            doc_count = 0
            for doc_id in sorted(self.processed_terms.keys()):
                if termo in self.processed_terms[doc_id]:
                    doc_count += 1
                    freq_doc = self.processed_terms[doc_id][termo]
                    titulo = doc_titles.get(doc_id, doc_id)
                    detalhes_por_doc.append(f"{titulo}/{freq_doc}")
            
            # Formatar linha: palavra/freq [N] -> doc1/freq doc2/freq
            linha = f"{termo}/{freq_total} [{doc_count}] -> {' '.join(detalhes_por_doc)}"
            linhas.append(linha)
        
        relatorio = "\n".join(linhas)
        
        # Salvar em arquivo se especificado
        if output_path:
            try:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(relatorio)
                print(f"✅ Relatório salvo em: {output_path}")
            except Exception as e:
                print(f"⚠️  Erro ao salvar relatório: {e}")
        
        return relatorio

