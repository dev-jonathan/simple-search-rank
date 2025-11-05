"""
Serviço de cache para dados processados do corpus.
Evita reprocessar PDFs toda vez que o servidor inicia.
"""
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class CacheService:
    """Gerencia cache de dados processados do corpus."""
    
    def __init__(self, cache_dir: Path = None):
        """
        Inicializa o serviço de cache.
        
        Args:
            cache_dir: Diretório para salvar cache (padrão: backend/cache/)
        """
        if cache_dir is None:
            # Padrão: backend/cache/
            base_dir = Path(__file__).parent.parent.parent
            cache_dir = base_dir / "cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Arquivos de cache
        self.documents_file = self.cache_dir / "documents.json"
        self.texts_file = self.cache_dir / "texts.json"
        self.processed_terms_file = self.cache_dir / "processed_terms.json"
        self.corpus_hash_file = self.cache_dir / "corpus_hash.json"
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calcula hash SHA256 de um arquivo."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _calculate_corpus_hash(self, corpus_path: Path) -> Dict[str, str]:
        """
        Calcula hash de todos os PDFs no corpus.
        
        Returns:
            Dicionário {filename: hash}
        """
        pdf_files = sorted(corpus_path.glob("*.pdf"))
        hashes = {}
        
        print(f"📊 Calculando hash de {len(pdf_files)} PDFs...")
        for i, pdf_path in enumerate(pdf_files):
            try:
                hashes[pdf_path.name] = self._calculate_file_hash(pdf_path)
                if (i + 1) % 20 == 0:
                    print(f"  Hash calculado: {i+1}/{len(pdf_files)}...")
            except Exception as e:
                print(f"⚠️  Erro ao calcular hash de {pdf_path.name}: {e}")
                hashes[pdf_path.name] = None
        
        print(f"✅ Hash calculado para {len(hashes)} arquivos")
        return hashes
    
    def _load_corpus_hash(self) -> Optional[Dict[str, str]]:
        """Carrega hash do corpus do cache."""
        if not self.corpus_hash_file.exists():
            return None
        
        try:
            with open(self.corpus_hash_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Erro ao carregar hash do corpus: {e}")
            return None
    
    def _save_corpus_hash(self, hashes: Dict[str, str]):
        """Salva hash do corpus no cache."""
        try:
            with open(self.corpus_hash_file, 'w', encoding='utf-8') as f:
                json.dump(hashes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Erro ao salvar hash do corpus: {e}")
    
    def is_cache_valid(self, corpus_path: Path, skip_hash_check: bool = False) -> bool:
        """
        Verifica se o cache é válido comparando hashes dos PDFs.
        
        Args:
            corpus_path: Caminho para o corpus de PDFs
            skip_hash_check: Se True, apenas verifica se arquivos existem (mais rápido)
        
        Returns:
            True se cache é válido, False caso contrário
        """
        # Verificar se arquivos de cache existem
        if not all([
            self.documents_file.exists(),
            self.texts_file.exists(),
            self.processed_terms_file.exists(),
            self.corpus_hash_file.exists()
        ]):
            print("📦 Cache não encontrado - precisa processar")
            return False
        
        # Se skip_hash_check, apenas verificar se arquivos existem
        if skip_hash_check:
            print("✅ Cache encontrado (validação de hash pulada)")
            return True
        
        # Carregar hash do cache
        cached_hashes = self._load_corpus_hash()
        if not cached_hashes:
            print("📦 Hash do cache inválido - precisa processar")
            return False
        
        # Calcular hash atual do corpus (pode ser lento, mas necessário para validação completa)
        current_hashes = self._calculate_corpus_hash(corpus_path)
        
        # Comparar
        if set(cached_hashes.keys()) != set(current_hashes.keys()):
            print("📦 PDFs adicionados/removidos - cache inválido")
            return False
        
        for filename, cached_hash in cached_hashes.items():
            if filename not in current_hashes:
                print(f"📦 PDF removido: {filename} - cache inválido")
                return False
            if current_hashes[filename] != cached_hash:
                print(f"📦 PDF modificado: {filename} - cache inválido")
                return False
        
        print("✅ Cache válido!")
        return True
    
    def save_cache(
        self,
        documents: List[Dict],
        texts: Dict[str, str],
        processed_terms: Dict[str, Dict[str, int]],
        corpus_path: Path
    ):
        """
        Salva dados processados no cache.
        
        Args:
            documents: Lista de metadados dos documentos
            texts: Dicionário {doc_id: texto_completo}
            processed_terms: Dicionário {doc_id: {termo: frequência}}
            corpus_path: Caminho do corpus (para calcular hash)
        """
        print("💾 Salvando cache...")
        
        try:
            # Salvar documentos (metadados)
            with open(self.documents_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2, ensure_ascii=False)
            
            # Salvar textos (pode ser grande, mas necessário)
            with open(self.texts_file, 'w', encoding='utf-8') as f:
                json.dump(texts, f, ensure_ascii=False)
            
            # Salvar termos processados
            with open(self.processed_terms_file, 'w', encoding='utf-8') as f:
                json.dump(processed_terms, f, ensure_ascii=False)
            
            # Calcular e salvar hash do corpus
            hashes = self._calculate_corpus_hash(corpus_path)
            self._save_corpus_hash(hashes)
            
            print(f"✅ Cache salvo em: {self.cache_dir}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar cache: {e}")
            import traceback
            traceback.print_exc()
    
    def load_cache(
        self
    ) -> Optional[Dict[str, Any]]:
        """
        Carrega dados do cache.
        
        Returns:
            Dicionário com 'documents', 'texts', 'processed_terms' ou None se falhar
        """
        print("📂 Carregando cache...")
        
        try:
            import time
            start_time = time.time()
            
            # Carregar documentos (pequeno, rápido)
            print("  Carregando documentos...")
            with open(self.documents_file, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            print(f"  ✅ Documentos carregados ({len(documents)} docs)")
            
            # Carregar termos processados (médio)
            print("  Carregando termos processados...")
            with open(self.processed_terms_file, 'r', encoding='utf-8') as f:
                processed_terms = json.load(f)
            print(f"  ✅ Termos processados carregados")
            
            # Carregar textos (pode ser muito grande - 50-100MB)
            print("  Carregando textos (pode demorar se for muito grande)...")
            with open(self.texts_file, 'r', encoding='utf-8') as f:
                texts = json.load(f)
            
            elapsed = time.time() - start_time
            print(f"✅ Cache carregado: {len(documents)} documentos em {elapsed:.2f}s")
            
            return {
                'documents': documents,
                'texts': texts,
                'processed_terms': processed_terms
            }
            
        except Exception as e:
            print(f"❌ Erro ao carregar cache: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def clear_cache(self):
        """Remove todos os arquivos de cache."""
        print("🗑️  Limpando cache...")
        try:
            for cache_file in [
                self.documents_file,
                self.texts_file,
                self.processed_terms_file,
                self.corpus_hash_file
            ]:
                if cache_file.exists():
                    cache_file.unlink()
            print("✅ Cache limpo")
        except Exception as e:
            print(f"⚠️  Erro ao limpar cache: {e}")

