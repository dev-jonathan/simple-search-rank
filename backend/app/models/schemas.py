"""
Modelos Pydantic para validação de dados.
"""
from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class ResultItem(BaseModel):
    """Item de resultado de busca."""
    id: str = Field(..., description="ID único do documento")
    title: str = Field(..., description="Título do documento")
    score: float = Field(..., description="Score de relevância")
    snippet: str = Field(..., description="Trecho relevante do documento")
    matchedWords: List[str] = Field(default_factory=list, description="Palavras encontradas no snippet (exatas, lematizadas ou similares)")
    filename: Optional[str] = Field(default=None, description="Nome do arquivo PDF")


class Metrics(BaseModel):
    """Métricas de desempenho da busca."""
    preprocessTime: float = Field(..., description="Tempo de pré-processamento (ms)")
    tfidfTime: float = Field(..., description="Tempo de execução TF-IDF (ms)")
    bm25Time: float = Field(..., description="Tempo de execução BM25 (ms)")


class SearchRequest(BaseModel):
    """Request de busca."""
    query: str = Field(..., min_length=1, description="Consulta de busca")
    k1: float = Field(default=1.2, ge=0.5, le=2.0, description="Parâmetro k₁ do BM25")
    b: float = Field(default=0.75, ge=0.0, le=1.0, description="Parâmetro b do BM25")
    tfIdfWeight: Literal["log", "raw", "binary"] = Field(
        default="log",
        description="Função de peso para TF-IDF"
    )
    topK: Optional[int] = Field(default=None, ge=1, le=1000, description="Número máximo de resultados por modelo (None = retornar todos)")


class SearchResponse(BaseModel):
    """Response de busca."""
    tfidf: List[ResultItem] = Field(..., description="Resultados TF-IDF")
    bm25: List[ResultItem] = Field(..., description="Resultados BM25")
    metrics: Metrics = Field(..., description="Métricas de desempenho")


class CorpusInfo(BaseModel):
    """Informações sobre o corpus."""
    total_documents: int = Field(..., description="Total de documentos")
    total_terms: int = Field(..., description="Total de termos únicos")
    avg_doc_length: float = Field(..., description="Tamanho médio dos documentos")


class DocumentInfo(BaseModel):
    """Informações de um documento."""
    id: str = Field(..., description="ID único do documento")
    title: str = Field(..., description="Título do documento")


class CorpusListResponse(BaseModel):
    """Response com lista de documentos."""
    documents: List[DocumentInfo] = Field(..., description="Lista de documentos")

