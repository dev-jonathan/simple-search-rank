"""
Endpoints relacionados ao corpus de documentos.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from app.models.schemas import CorpusInfo, CorpusListResponse, DocumentInfo
from app.services.corpus_manager import CorpusManager
from app.config import CORPUS_PATH

router = APIRouter()
_corpus_manager_getter = None


def setup_corpus_manager(getter):
    """Configura o getter do gerenciador de corpus."""
    global _corpus_manager_getter
    _corpus_manager_getter = getter


def get_corpus_manager() -> CorpusManager:
    """Obtém o gerenciador de corpus."""
    if _corpus_manager_getter is None:
        raise HTTPException(status_code=503, detail="Corpus não inicializado")
    manager = _corpus_manager_getter()
    if manager is None:
        raise HTTPException(status_code=503, detail="Corpus não carregado")
    return manager


@router.get("/info", response_model=CorpusInfo)
async def get_corpus_info():
    """
    Retorna estatísticas do corpus.
    
    Returns:
        Total de documentos, termos, média de tamanho, etc.
    """
    try:
        manager = get_corpus_manager()
        stats = manager.get_statistics()
        return CorpusInfo(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter informações: {str(e)}")


@router.get("/list", response_model=CorpusListResponse)
async def list_documents():
    """
    Lista todos os documentos do corpus.
    
    Returns:
        Lista de documentos com ID e título
    """
    try:
        manager = get_corpus_manager()
        documents = manager.get_all_documents()
        doc_infos = [
            DocumentInfo(id=doc["id"], title=doc["title"])
            for doc in documents
        ]
        return CorpusListResponse(documents=doc_infos)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar documentos: {str(e)}")


@router.get("/pdf/{doc_id}")
async def get_pdf(doc_id: str):
    """
    Retorna o arquivo PDF de um documento.
    
    Args:
        doc_id: ID do documento (ex: "doc_1")
    
    Returns:
        Arquivo PDF
    """
    try:
        manager = get_corpus_manager()
        doc = manager.get_document(doc_id)
        
        if not doc:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        filename = doc.get("filename")
        if not filename:
            raise HTTPException(status_code=404, detail="Arquivo PDF não encontrado")
        
        pdf_path = CORPUS_PATH / filename
        
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail=f"PDF não encontrado: {filename}")
        
        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao servir PDF: {str(e)}")


@router.get("/frequency-report")
async def get_frequency_report():
    """
    Gera e retorna o relatório de frequências de termos.
    
    Returns:
        Arquivo TXT com frequências no formato: palavra/freq -> doc/freq doc2/freq
    """
    try:
        manager = get_corpus_manager()
        base_dir = Path(__file__).parent.parent.parent
        report_path = base_dir / "frequency_report.txt"
        
        # Gerar relatório
        manager.generate_frequency_report(output_path=report_path)
        
        if not report_path.exists():
            raise HTTPException(status_code=404, detail="Relatório não foi gerado")
        
        return FileResponse(
            path=str(report_path),
            media_type="text/plain",
            filename="frequency_report.txt"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")
