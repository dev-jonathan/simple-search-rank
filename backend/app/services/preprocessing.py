"""
Serviço de pré-processamento de texto (NLP).
"""
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Optional

# Importações opcionais - podem falhar se não estiverem instaladas
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None

try:
    from nltk.stem import RSLPStemmer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    RSLPStemmer = None


class PreprocessingService:
    """Serviço de pré-processamento de texto."""
    
    def __init__(self, use_spacy: bool = False):
        """
        Inicializa o serviço de pré-processamento.
        
        Args:
            use_spacy: Se True, tenta usar spaCy (requer modelo instalado)
        """
        self.use_spacy = use_spacy and SPACY_AVAILABLE
        self.stopwords: Set[str] = set()
        self.lematizadas_corrigidas: Dict[str, str] = {}
        
        # Carregar spaCy se disponível e solicitado
        self.nlp = None
        if self.use_spacy:
            try:
                self.nlp = spacy.load('pt_core_news_md')
                print("✅ spaCy carregado com sucesso (modelo: pt_core_news_md)")
            except OSError as e:
                print("⚠️  spaCy não disponível - modelo pt_core_news_md não encontrado")
                print("   Instale o modelo com: python -m spacy download pt_core_news_md")
                print("   Usando fallback: RSLPStemmer + correções manuais")
                self.use_spacy = False
        
        # Carregar stemmer NLTK se disponível (sempre usar se spaCy não estiver disponível)
        self.stemmer = None
        if NLTK_AVAILABLE:
            try:
                self.stemmer = RSLPStemmer()
                print("✅ NLTK RSLPStemmer carregado")
            except Exception as e:
                print(f"⚠️  NLTK não disponível: {e}")
        
        # Carregar correções de lematização
        # self._load_lemmatization_corrections()
        
        # Carregar stopwords básicas
        from app.utils.constants import STOPWORDS
        self.stopwords = set(STOPWORDS)
    
    # def _load_lemmatization_corrections(self):
    #     """Carrega correções manuais de lematização do arquivo JSON."""
    #     try:
    #         Tentar carregar words lematizadasCorrigidas
    #         base_dir = Path(__file__).parent.parent.parent.parent
    #         corrections_file = base_dir / "lematizadasCorrigidas.json"
            
    #         if corrections_file.exists():
    #             with open(corrections_file, 'r', encoding='utf-8') as f:
    #                 self.lematizadas_corrigidas = json.load(f)
    #             print(f"✅ Carregadas {len(self.lematizadas_corrigidas)} correções de lematização")
    #         else:
    #             print("⚠️  Arquivo de correções não encontrado, usando apenas stemmer/spaCy")
    #     except Exception as e:
    #         print(f"⚠️  Erro ao carregar correções de lematização: {e}")
    
    def clean_text(self, text: str) -> str:
        """
        Remove caracteres especiais e normaliza texto.
        
        Args:
            text: Texto a ser limpo
        
        Returns:
            Texto limpo e normalizado
        """
        # Remove caracteres especiais, mantém apenas letras e espaços
        text = re.sub(r'[^a-záéíóúâêîôûãõç ]', ' ', text.lower())
        # Remove espaços múltiplos
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def normalize_term(self, term: str) -> str:
        """Normaliza um termo (mesma função usada no process_text)."""
        termo_limpo = term.lower().strip()
        # Remover caracteres especiais, mantendo apenas letras
        termo_limpo = re.sub(r'[^a-záéíóúâêîôûãõç]', '', termo_limpo)
        return termo_limpo
    
    def process_text(self, text: str) -> Dict[str, int]:
        """
        Processa texto: lematização, remoção de stopwords.
        
        Args:
            text: Texto a ser processado
        
        Returns:
            Dicionário {termo_lematizado: frequência}
        """
        texto_limpo = self.clean_text(text)
        termos = {}
        
        if self.use_spacy and self.nlp:
            # Processar com spaCy
            doc = self.nlp(texto_limpo)
            for token in doc:
                if token.is_alpha and not token.is_stop and token.text not in self.stopwords:
                    # Usar correções manuais se disponível
                    lemma = self.lematizadas_corrigidas.get(token.text, token.lemma_)
                    termos[lemma] = termos.get(lemma, 0) + 1
        else:
            # Processamento simplificado (sem spaCy) - usar stemmer
            palavras = texto_limpo.split()
            for palavra in palavras:
                palavra_normalizada = self.normalize_term(palavra)
                if len(palavra_normalizada) > 2 and palavra_normalizada not in self.stopwords:
                    # Usar correções manuais se disponível, senão usar stemmer
                    if palavra_normalizada in self.lematizadas_corrigidas:
                        termo_final = self.lematizadas_corrigidas[palavra_normalizada]
                    elif self.stemmer:
                        termo_final = self.stemmer.stem(palavra_normalizada)
                    else:
                        termo_final = palavra_normalizada
                    
                    termos[termo_final] = termos.get(termo_final, 0) + 1
        
        return termos
    
    def process_query(self, query: str) -> List[str]:
        """
        Processa termos da consulta.
        
        Args:
            query: Consulta de busca
        
        Returns:
            Lista de termos processados (lematizados)
        """
        termos = query.lower().split()
        termos_processados = []
        
        if self.use_spacy and self.nlp:
            for termo in termos:
                doc = self.nlp(termo)
                for token in doc:
                    if token.is_alpha and not token.is_stop:
                        lemma = self.lematizadas_corrigidas.get(token.text, token.lemma_)
                        termos_processados.append(lemma)
        else:
            # Processamento simplificado (mesmo usado no process_text) - usar stemmer
            for termo in termos:
                termo_limpo = self.normalize_term(termo)
                if len(termo_limpo) > 2 and termo_limpo not in self.stopwords:
                    # Usar correções manuais se disponível, senão usar stemmer
                    if termo_limpo in self.lematizadas_corrigidas:
                        termo_final = self.lematizadas_corrigidas[termo_limpo]
                    elif self.stemmer:
                        termo_final = self.stemmer.stem(termo_limpo)
                    else:
                        termo_final = termo_limpo
                    
                    termos_processados.append(termo_final)
        
        return termos_processados
    
    def stem_word(self, word: str) -> str:
        """Estematiza uma palavra."""
        if self.stemmer:
            return self.stemmer.stem(word)
        return word

