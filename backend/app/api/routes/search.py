"""
Endpoints de busca.
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter()
_search_service_getter = None


def setup_search_service(getter):
    """Configura o getter do serviço de busca."""
    global _search_service_getter
    _search_service_getter = getter


def get_search_service() -> SearchService:
    """Obtém o serviço de busca."""
    if _search_service_getter is None:
        raise HTTPException(status_code=503, detail="Serviço de busca não inicializado")
    service = _search_service_getter()
    if service is None:
        raise HTTPException(status_code=503, detail="Corpus não carregado")
    return service


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Realiza busca usando TF-IDF e BM25.
    
    Args:
        request: Parâmetros de busca (query, k1, b, tfIdfWeight)
    
    Returns:
        Resultados de busca ordenados por ambos os modelos
    """
    try:
        search_service = get_search_service()
        results = await search_service.search(
            query=request.query,
            k1=request.k1,
            b=request.b,
            tf_weight=request.tfIdfWeight,
            top_k=request.topK
        )
        return SearchResponse(**results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")


@router.get("/search/test")
async def test_search():
    """Endpoint de teste para verificar se a API está funcionando."""
    return {"message": "Search endpoint is working"}

