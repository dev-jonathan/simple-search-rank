"""
Funções auxiliares de processamento de texto.
"""
import re
from typing import List, Optional, Tuple
from difflib import SequenceMatcher


def extract_snippet(
    text: str, 
    terms: List[str], 
    context_length: int = 250,
    original_query: Optional[str] = None
) -> Tuple[str, List[str]]:
    """
    Extrai um trecho relevante do texto com os termos buscados.
    Prioriza palavras exatas da query original, depois termos lematizados.
    Evita cortar palavras no início ou fim do snippet.
    
    Args:
        text: Texto completo
        terms: Lista de termos buscados (lematizados)
        context_length: Número de caracteres ao redor do termo
        original_query: Query original (para buscar palavras exatas)
    
    Returns:
        Tupla (snippet, matched_words) onde:
        - snippet: Trecho do texto com contexto
        - matched_words: Lista de palavras encontradas (exatas, lematizadas ou similares)
    """
    matched_words = []
    
    if not text or not terms:
        # Se não há termos, retornar início do texto completo até espaço
        if len(text) > context_length:
            end_pos = text.find(' ', context_length)
            if end_pos == -1:
                end_pos = context_length
            return text[:end_pos].strip() + "...", []
        return text, []
    
    text_lower = text.lower()
    
    # Extrair palavras da query original (para buscar exatas primeiro)
    original_terms = []
    if original_query:
        # Dividir query original em palavras e normalizar
        for word in original_query.lower().split():
            # Remover pontuação mas manter acentos
            word_clean = re.sub(r'[^\wáéíóúâêîôûãõç]', '', word)
            if len(word_clean) > 2:
                original_terms.append(word_clean)
    
    # Buscar primeira ocorrência: priorizar palavras exatas da query, depois fuzzy matching
    best_match = None
    best_pos = len(text)
    match_type = None  # 'exact' ou 'fuzzy'
    
    # 1. Primeiro tentar encontrar palavras exatas da query original
    for orig_term in original_terms:
        pattern = r'\b' + re.escape(orig_term) + r'\b'
        match = re.search(pattern, text_lower)
        if match:
            pos = match.start()
            if pos < best_pos:
                best_pos = pos
                best_match = match
                match_type = 'exact'
                matched_words.append(orig_term)  # Adicionar palavra exata encontrada
    
    # 2. Se não encontrou exata, fazer fuzzy matching diretamente
    if best_match is None:
        # Extrair todas as palavras do texto (uma vez só)
        words_in_text = re.findall(r'\b\w+\b', text_lower)
        
        # Buscar palavra mais similar usando fuzzy matching
        best_fuzzy_match = None
        best_similarity = 0.7  # Threshold mínimo de similaridade (70%)
        best_fuzzy_pos = len(text)
        
        # Tentar com palavras da query original (não usar termos lematizados aqui para performance)
        search_terms = original_terms
        
        for search_term in search_terms:
            search_term_lower = search_term.lower()
            search_term_len = len(search_term_lower)
            
            # Otimização: filtrar palavras por tamanho similar (evita comparações desnecessárias)
            # Aceitar palavras com tamanho entre 70% e 130% do termo buscado
            min_len = int(search_term_len * 0.7)
            max_len = int(search_term_len * 1.3)
            
            # Para cada palavra no texto, calcular similaridade
            for word in words_in_text:
                # Pular palavras muito diferentes em tamanho
                if len(word) < min_len or len(word) > max_len:
                    continue
                
                # Pular se não começar com mesma letra (otimização adicional)
                if search_term_lower and word and search_term_lower[0] != word[0]:
                    continue
                
                similarity = SequenceMatcher(None, search_term_lower, word).ratio()
                
                if similarity >= best_similarity:
                    # Encontrar posição da palavra no texto
                    pattern = r'\b' + re.escape(word) + r'\b'
                    match = re.search(pattern, text_lower)
                    if match:
                        pos = match.start()
                        if similarity > best_similarity or (similarity == best_similarity and pos < best_fuzzy_pos):
                            best_similarity = similarity
                            best_fuzzy_pos = pos
                            best_fuzzy_match = match
                            match_type = 'fuzzy'
        
        if best_fuzzy_match:
            best_match = best_fuzzy_match
            best_pos = best_fuzzy_pos
            # Adicionar palavra similar encontrada
            matched_word = best_fuzzy_match.group()
            matched_words.append(matched_word)
            # Também adicionar termo original que gerou o match
            matched_words.extend(search_terms)
    
    if best_match:
        # Calcular início e fim desejados
        desired_start = max(0, best_pos - context_length // 2)
        desired_end = min(len(text), best_pos + len(best_match.group()) + context_length // 2)
        
        # Ajustar início para não cortar palavra
        start = desired_start
        if start > 0:
            # Retroceder até encontrar espaço ou início do texto
            while start > 0 and text[start] not in [' ', '\n', '\t']:
                start -= 1
            if start > 0:
                start += 1  # Incluir o espaço
        
        # Ajustar fim para não cortar palavra
        end = desired_end
        if end < len(text):
            # Avançar até encontrar espaço ou fim do texto
            while end < len(text) and text[end] not in [' ', '\n', '\t', '.', ',', ';', '!', '?']:
                end += 1
            if end < len(text):
                end += 1  # Incluir a pontuação ou espaço
        
        snippet = text[start:end].strip()
        
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        # Remover duplicatas e normalizar matched_words
        matched_words = list(set([w.lower() for w in matched_words if w]))
        
        return snippet, matched_words
    
    # Se não encontrar, retornar início do texto sem cortar palavra
    if len(text) > context_length:
        end_pos = text.find(' ', context_length)
        if end_pos == -1:
            end_pos = context_length
        return text[:end_pos].strip() + "...", []
    return text, []

