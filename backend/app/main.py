"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.config import CORPUS_PATH
from app.services.corpus_manager import CorpusManager
from app.services.search_service import SearchService
import os

app = FastAPI(
    title="Simple Search Rank API",
    description="API para comparação de modelos de RI (TF-IDF vs BM25)",
    version="1.0.0",
)

# Configurar CORS para permitir requests do Next.js
# Suporta localhost (desenvolvimento) e Vercel (produção)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    FRONTEND_URL,
]
# Se FRONTEND_URL contém múltiplos URLs (separados por vírgula)
if "," in FRONTEND_URL:
    allowed_origins.extend(FRONTEND_URL.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar serviços globais
corpus_manager = None
search_service = None


@app.on_event("startup")
async def startup_event():
    """Inicializa o corpus e serviços na inicialização da aplicação."""
    global corpus_manager, search_service
    
    import time
    startup_start = time.time()
    
    print("🚀 Inicializando serviços...")
    print(f"📂 Caminho do corpus: {CORPUS_PATH}")
    
    # Verificar se precisa baixar PDFs do GitHub
    from app.config import DOWNLOAD_PDFS
    if DOWNLOAD_PDFS:
        # Verificar se PDFs não existem ou pasta está vazia
        pdf_files_exist = CORPUS_PATH.exists() and any(CORPUS_PATH.glob("*.pdf"))
        if not pdf_files_exist:
            print("📥 PDFs não encontrados. Baixando do GitHub...")
            try:
                import sys
                # Adicionar backend ao path para importar scripts
                backend_dir = Path(__file__).parent.parent
                sys.path.insert(0, str(backend_dir))
                from scripts.download_pdfs import download_pdfs
                download_pdfs(CORPUS_PATH)
            except Exception as e:
                print(f"❌ Erro ao baixar PDFs: {e}")
                print("   Você pode baixar manualmente ou configurar DOWNLOAD_PDFS=false")
                import traceback
                traceback.print_exc()
        else:
            print(f"✅ PDFs já existem em {CORPUS_PATH}")
    elif not CORPUS_PATH.exists():
        print(f"⚠️  Pasta do corpus não encontrada: {CORPUS_PATH}")
        print("   Configure DOWNLOAD_PDFS=true para baixar automaticamente")
        print("   Ou baixe com /scripts")
    
    # Carregar corpus (com cache habilitado por padrão)
    corpus_manager = CorpusManager(CORPUS_PATH, use_cache=True)
    try:
        # Carregar todos os documentos (cache evitará reprocessamento se disponível)
        load_start = time.time()
        corpus_manager.load_corpus()
        load_time = time.time() - load_start
        print(f"⏱️  Tempo de carregamento: {load_time:.2f}s")
        
        # Gerar relatório de frequências após processar (salva em backend/frequency_report.txt)
        # Gerar apenas se o corpus foi carregado com sucesso e tem documentos
        if corpus_manager._is_loaded and len(corpus_manager.documents) > 0:
            base_dir = Path(__file__).parent.parent
            report_path = base_dir / "frequency_report.txt"
            corpus_manager.generate_frequency_report(output_path=report_path)
        
    except Exception as e:
        print(f"❌ Erro ao carregar corpus: {e}")
        import traceback
        traceback.print_exc()
        corpus_manager = None
        return
    
    # Inicializar serviço de busca
    search_service = SearchService(corpus_manager)
    
    startup_time = time.time() - startup_start
    print(f"✅ Serviços inicializados! (tempo total: {startup_time:.2f}s)")


@app.on_event("shutdown")
async def shutdown_event():
    """Limpeza na finalização da aplicação."""
    print("👋 Finalizando aplicação...")


# Registrar rotas
from app.api.routes import search, corpus

# Injetar dependências nas rotas
search.setup_search_service(lambda: search_service)
corpus.setup_corpus_manager(lambda: corpus_manager)

app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(corpus.router, prefix="/api/corpus", tags=["corpus"])


@app.get("/")
async def root():
    """Endpoint raiz da API."""
    return {
        "message": "Simple Search Rank API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "corpus_loaded": corpus_manager is not None and corpus_manager._is_loaded,
        "search_service_ready": search_service is not None
    }

