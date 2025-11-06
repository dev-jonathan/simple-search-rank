# Dockerfile otimizado para Render (plano free)
# Usa Python slim para reduzir tamanho da imagem

FROM python:3.11-slim

# Metadados
LABEL maintainer="Simple Search Rank API"
LABEL description="FastAPI backend para busca e ranking de documentos"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Instalar dependências do sistema (mínimas necessárias)
# gcc, g++ são necessários para compilar algumas dependências do spaCy
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar apenas requirements primeiro (para cache de layers)
COPY requirements.txt .

# Instalar dependências Python
# Usa --no-cache-dir para reduzir tamanho e instala blis separadamente para evitar problemas
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir blis && \
    pip install --no-cache-dir -r requirements.txt

# Instalar modelo spaCy via link direto (evita problemas de compilação)
# Se falhar, tenta método padrão como fallback
RUN pip install --no-cache-dir https://github.com/explosion/spacy-models/releases/download/pt_core_news_md-3.8.0/pt_core_news_md-3.8.0.tar.gz || \
    python -m spacy download pt_core_news_md || \
    echo "⚠️ spaCy model installation failed, will use fallback"

# Baixar dados do NLTK (necessário para RSLPStemmer)
RUN python -c "import nltk; nltk.download('rslp', quiet=True)" || echo "⚠️ NLTK data download failed"

# Criar diretórios necessários
RUN mkdir -p cache pdf_dataset

# Copiar código da aplicação
COPY app/ ./app/
COPY scripts/ ./scripts/

# Copiar cache se existir (acelera startup - opcional)
# Se o diretório cache/ não existir no build context, comente a linha abaixo
# O cache será criado automaticamente na primeira execução se não existir
COPY cache/ ./cache/

# Expor porta (Render usa variável $PORT)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Comando de inicialização
# Render injeta $PORT automaticamente
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
