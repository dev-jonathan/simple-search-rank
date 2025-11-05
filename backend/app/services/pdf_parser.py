"""
Serviço de extração de texto de PDFs.
"""
from pathlib import Path
from typing import Dict, Optional

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    pdfplumber = None


class PDFParser:
    """Parser de arquivos PDF."""
    
    @staticmethod
    def extract_text(pdf_path: Path) -> str:
        """
        Extrai texto de um arquivo PDF.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
        
        Returns:
            Texto extraído do PDF
        """
        if not PDFPLUMBER_AVAILABLE:
            raise ImportError("pdfplumber não está instalado")
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")
        
        texto = ''
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for pagina in pdf.pages:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto += texto_pagina + '\n'
        except Exception as e:
            raise Exception(f"Erro ao extrair texto do PDF {pdf_path}: {e}")
        
        return texto
    
    @staticmethod
    def extract_metadata(pdf_path: Path) -> Dict[str, any]:
        """
        Extrai metadados de um arquivo PDF.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
        
        Returns:
            Dicionário com metadados (título, páginas, etc.)
        """
        if not PDFPLUMBER_AVAILABLE:
            return {
                "title": pdf_path.stem,
                "pages": 0,
                "filename": pdf_path.name
            }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return {
                    "title": pdf_path.stem,
                    "pages": len(pdf.pages),
                    "filename": pdf_path.name
                }
        except Exception:
            return {
                "title": pdf_path.stem,
                "pages": 0,
                "filename": pdf_path.name
            }

