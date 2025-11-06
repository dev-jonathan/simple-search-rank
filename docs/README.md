# 📚 Documentação Técnica - Comparador de Modelos de RI

Documentação completa para desenvolvedores sobre instalação, arquitetura, desenvolvimento e detalhes técnicos do projeto.

---

## 📋 Índice

- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Arquitetura](#-arquitetura)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Como Funciona](#-como-funciona)
- [Conceitos Técnicos](#-conceitos-técnicos)
- [Desenvolvimento](#-desenvolvimento)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.11+** (recomendado usar Conda)
- **Node.js 18+** e npm/pnpm
- **Git**

### Backend (Python)

#### 0. Git Clone

```bash
git clone https://github.com/dev-jonathan/simple-search-rank
cd simple-search-rank
```

#### 1. Criar ambiente Conda

```bash
# Na raiz do projeto
conda create -n search-rank python=3.11 -y
conda activate search-rank
```

#### 2. Instalar dependências Python

```bash
cd backend
pip install -r requirements.txt
```

#### 3. Baixar modelos NLP

```bash
# Modelo spaCy para português
python -m spacy download pt_core_news_md
# Ou baixe manualmente https://github.com/explosion/spacy-models/releases/download/pt_core_news_md-3.8.0/pt_core_news_md-3.8.0.tar.gz

# Dados NLTK (RSLP stemmer)
python -c "import nltk; nltk.download('rslp')"
```

#### 4. Configurar variáveis de ambiente

```bash
# Criar .env na raiz ou backend/
echo "DOWNLOAD_PDFS=true" > .env  # Para desenvolvimento local
```

**Variáveis disponíveis:**
- `DOWNLOAD_PDFS`: `true` para baixar PDFs automaticamente do GitHub, `false` para usar apenas cache
- `CORPUS_PATH`: Caminho customizado para o corpus (opcional)

#### 5. (Alternativa) Ou use Docker

```bash
cd backend
docker build -t search-rank-api .
docker images
docker run -p 8000:8000 -e DOWNLOAD_PDFS=false -e CORPUS_PATH=/app/pdf_dataset search-rank-api
docker logs -f search-rank-api
```
### Frontend (Next.js)

```bash
# Na raiz do projeto
npm install
# ou
pnpm install
```

---

## ⚙️ Configuração

### Modo Desenvolvimento

```bash
# .env
DOWNLOAD_PDFS=true
```

O sistema baixará automaticamente os PDFs do GitHub na primeira inicialização.

### Modo Produção

```bash
# .env
DOWNLOAD_PDFS=false
```

O sistema usará apenas o cache versionado (já processado), sem necessidade dos PDFs.

### Repositório dos PDFs

Os PDFs estão hospedados em: [wiki-popular-articles-to-pdf](https://github.com/dev-jonathan/wiki-popular-articles-to-pdf/tree/main/pdf_dataset)

O script `backend/scripts/download_pdfs.py` baixa automaticamente quando `DOWNLOAD_PDFS=true`.

---

## 🏗️ Arquitetura

### Visão Geral

```
Frontend (Next.js) → API REST (FastAPI) → Serviços de Processamento → Retorno JSON
     ↓                      ↓                        ↓
  React UI          FastAPI Endpoints      TF-IDF / BM25 Models
```

### Fluxo de Dados

1. **Usuário** digita busca no frontend
2. **Frontend** envia requisição POST para `/api/search`
3. **Backend** processa query e executa TF-IDF e BM25 em paralelo
4. **Backend** retorna resultados ordenados com métricas
5. **Frontend** exibe resultados lado a lado com gráficos

---

## 📁 Estrutura do Projeto

```
simple-search-rank/
├── app/                      # Frontend Next.js
│   ├── page.tsx             # Página principal
│   ├── layout.tsx           # Layout global
│   └── globals.css          # Estilos globais
│
├── components/               # Componentes React
│   ├── header.tsx           # Cabeçalho
│   ├── control-panel.tsx   # Painel de controle
│   ├── results-display.tsx # Exibição de resultados
│   ├── metrics-panel.tsx   # Dashboard de métricas
│   └── ui/                  # Componentes UI (shadcn)
│
├── lib/                      # Utilitários frontend
│   ├── api.ts               # Cliente API
│   ├── types.ts             # Tipos TypeScript
│   └── utils.ts             # Funções auxiliares
│
├── backend/                  # Backend FastAPI
│   ├── app/
│   │   ├── main.py          # Entry point FastAPI
│   │   ├── config.py        # Configurações
│   │   │
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── search.py    # POST /api/search
│   │   │       └── corpus.py     # GET /api/corpus/*
│   │   │
│   │   ├── models/
│   │   │   └── schemas.py       # Modelos Pydantic
│   │   │
│   │   ├── services/
│   │   │   ├── search_service.py    # Orquestra TF-IDF e BM25
│   │   │   ├── tfidf_service.py     # Implementação TF-IDF
│   │   │   ├── bm25_service.py      # Implementação BM25
│   │   │   ├── preprocessing.py     # NLP (lematização, stemização)
│   │   │   ├── pdf_parser.py        # Extração de texto de PDFs
│   │   │   ├── corpus_manager.py    # Gerenciamento do corpus
│   │   │   └── cache_service.py     # Sistema de cache
│   │   │
│   │   └── utils/
│   │       ├── text_processing.py   # Utilitários de texto
│   │       └── constants.py         # Constantes
│   │
│   ├── scripts/
│   │   └── download_pdfs.py         # Script para baixar PDFs
│   │
│   ├── cache/                # Cache processado (versionado)
│   │   ├── documents.json
│   │   ├── texts.json
│   │   ├── processed_terms.json
│   │   └── corpus_hash.json
│   │
│   └── requirements.txt
│
├── public/                   # Assets estáticos
│   ├── interface_inicial.png
│   └── interface_plots.png
│
├── docs/                     # Documentação
│   ├── README.md            # Este arquivo
│   └── TODO.md              # Ideias futuras
│
└── package.json             # Dependências frontend
```

---

## 🔧 Como Funciona

### Sistema de Cache

O projeto utiliza um sistema de cache inteligente para otimizar performance:

#### ✅ Versionado no Git (~20MB)
- `backend/cache/documents.json` - Metadados dos documentos
- `backend/cache/texts.json` - Textos completos extraídos
- `backend/cache/processed_terms.json` - Termos processados com frequências
- `backend/cache/corpus_hash.json` - Hashes SHA256 dos PDFs

#### ❌ Não Versionado (~130MB)
- `backend/pdf_dataset/` - PDFs originais (baixados automaticamente)

#### Como Funciona

1. **Primeira Execução**:
   - Sistema processa todos os PDFs
   - Extrai texto, processa termos, calcula hashes
   - Salva tudo em JSON no cache

2. **Execuções Subsequentes**:
   - Sistema verifica se cache existe e é válido
   - Compara hashes dos PDFs com cache salvo
   - Se válido: carrega do cache (muito rápido!)
   - Se inválido: reprocessa e atualiza cache

3. **Invalidação Automática**:
   - PDF adicionado/removido
   - PDF modificado (hash diferente)

#### Performance

- **Sem cache**: ~2-5 minutos processando 97 PDFs
- **Com cache**: ~5-15 segundos carregando do JSON

### Processamento de Texto

1. **Extração**: `pdf_parser.py` extrai texto dos PDFs
2. **Limpeza**: Remove caracteres especiais, normaliza
3. **Lematização**: spaCy (`pt_core_news_md`) converte palavras para forma base
4. **Stemização**: NLTK RSLP para português
5. **Stopwords**: Remove palavras comuns sem significado
6. **Indexação**: Cria índice de termos com frequências

### Modelos de Busca

#### TF-IDF (Modelo Vetorial)

- **TF (Term Frequency)**: `1 + log10(frequência)` - Frequência do termo no documento
- **IDF (Inverse Document Frequency)**: `log10(1 + N / df)` - Raridade do termo na coleção
- **TF-IDF**: `TF * IDF` - Combina importância local e global
- **Similaridade**: Cosseno entre vetores normalizados

**Características:**
- Representa documentos como vetores multidimensionais
- Normaliza por tamanho do vetor
- Para queries com 1 termo: usa TF-IDF bruto (não normalizado) para diferenciar documentos

#### BM25 (Modelo Probabilístico)

- **Fórmula**: Baseada em probabilidades de relevância
- **Parâmetros**:
  - `k1`: Saturação de frequência (padrão: 1.2)
  - `b`: Normalização por tamanho (padrão: 0.75)

**Características:**
- Considera saturação de frequência (evita domínio de termos muito frequentes)
- Normaliza por tamanho do documento
- Geralmente mais eficaz que TF-IDF para busca

---

## 💻 Desenvolvimento

### Rodar o Backend

```bash
conda activate search-rank
cd backend
uvicorn app.main:app --reload --port 8000
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **Health**: http://localhost:8000/health

### Rodar o Frontend

```bash
npm run dev
# ou
pnpm dev
```

Acesse: http://localhost:3000

### Comandos Úteis

#### Baixar PDFs manualmente
```bash
cd backend
python scripts/download_pdfs.py
```

#### Limpar cache (forçar reprocessamento)
```bash
cd backend
rm -rf cache/*.json
# Reiniciar servidor com DOWNLOAD_PDFS=true
```

#### Verificar status do cache
```bash
ls -lh backend/cache/
```

---

## 📡 API Reference

### `POST /api/search`

Realiza busca usando TF-IDF e BM25.

**Request:**
```json
{
  "query": "adele",
  "k1": 1.2,
  "b": 0.75,
  "tfIdfWeight": "log",
  "topK": null
}
```

**Response:**
```json
{
  "tfidf": [
    {
      "id": "doc_1",
      "title": "Adele",
      "score": 5.4155,
      "snippet": "...texto relevante...",
      "matchedWords": ["adele"],
      "filename": "Adele.pdf"
    }
  ],
  "bm25": [...],
  "metrics": {
    "preprocessTime": 7.9,
    "tfidfTime": 17.5,
    "bm25Time": 16.0
  }
}
```

### `GET /api/corpus/info`

Retorna estatísticas do corpus.

**Response:**
```json
{
  "total_documents": 97,
  "total_terms": 72587,
  "avg_doc_length": 1500
}
```

### `GET /api/corpus/list`

Lista todos os documentos do corpus.

**Response:**
```json
{
  "documents": [
    {"id": "doc_1", "title": "Adele"},
    {"id": "doc_2", "title": "Brasil"},
    ...
  ]
}
```

### `GET /api/corpus/pdf/{doc_id}`

Retorna o arquivo PDF de um documento (redireciona para GitHub).

---

## 🔍 Conceitos Técnicos

### TF-IDF (Term Frequency-Inverse Document Frequency)

**Componentes:**

1. **TF (Term Frequency)**: `TF = 1 + log10(frequência)`
   - Quanto mais vezes a palavra aparece, maior o TF
   - Log atenua impacto de palavras muito frequentes

2. **IDF (Inverse Document Frequency)**: `IDF = log10(1 + N / df)`
   - `N` = total de documentos
   - `df` = número de documentos que contêm o termo
   - Quanto mais raro o termo, maior o IDF

3. **TF-IDF**: `TF * IDF`
   - Combina importância local (TF) com importância global (IDF)

### Similaridade do Cosseno

- Mede o ângulo entre dois vetores
- Fórmula: `similaridade = (vetor_A · vetor_B) / (norma_A * norma_B)`
- Valores: de -1 (opostos) a 1 (idênticos)
- **Problema com 1 termo**: Todos os documentos têm similaridade = 1.0 (solução: usar TF-IDF bruto)

### BM25

- Modelo probabilístico que estima relevância
- Considera saturação de frequência (k1) e normalização por tamanho (b)
- Fórmula mais complexa, geralmente mais eficaz que TF-IDF

### Norma (Norm)

- Tamanho/magnitude de um vetor
- Norma L2: `sqrt(soma dos quadrados dos valores)`
- Usada para normalizar vetores (tamanho = 1)

---

## 🐛 Troubleshooting

### Problema: Cache não encontrado

**Solução:**
```bash
# Habilitar download automático
echo "DOWNLOAD_PDFS=true" > .env
# Reiniciar servidor
```

### Problema: Similaridade TF-IDF sempre 1.0

**Causa**: Query com apenas 1 termo em corpus pequeno

**Solução**: Sistema já corrigido para usar TF-IDF bruto quando há 1 termo

### Problema: Poucos resultados retornados

**Causa**: Limite padrão de `top_k`

**Solução**: Passar `topK` na requisição ou aumentar limite padrão

### Problema: Erro ao baixar PDFs

**Solução:**
- Verificar conexão com internet
- Verificar se repositório GitHub está acessível
- Baixar manualmente: `python backend/scripts/download_pdfs.py`

### Problema: Erro ao processar PDFs

**Solução:**
- Verificar se PDFs não estão corrompidos
- Verificar logs do servidor para detalhes
- Limpar cache e reprocessar

---

## 📊 Performance

### Tempos Típicos

- **Carregamento do cache**: ~5-15 segundos
- **Processamento inicial**: ~2-5 minutos (97 PDFs)
- **Busca TF-IDF**: ~10-20ms
- **Busca BM25**: ~10-20ms
- **Pré-processamento**: ~5-10ms

### Otimizações Implementadas

1. **Cache de índices**: TF-IDF e BM25 calculados uma vez na inicialização
2. **Processamento paralelo**: TF-IDF e BM25 executam simultaneamente
3. **Cache de documentos**: Textos processados salvos em JSON
4. **Validação de hash**: Detecta mudanças automaticamente

---

## 🎯 Decisões Técnicas

### Armazenamento
- **Memória** (sem banco de dados)
- Simples para experimental
- Rápido (sem I/O)
- Suficiente para 97-200 documentos

### Parser de PDFs
- **pdfplumber**: Leve, rápido, suficiente para PDFs de texto simples
- Alternativa futura: docling (se necessário para PDFs complexos)

### Processamento de Texto
- **spaCy**: Lematização e tokenização
- **NLTK RSLP**: Stemização para português
- **Stopwords customizadas**: Lista otimizada

### Repositório Otimizado
- Cache versionado (~20MB) no Git
- PDFs não versionados (baixados automaticamente)
- Setup rápido em produção

---

## 📝 Notas Importantes

- **Corpus fixo**: 97 artigos da Wikipedia em português
- **Sem banco de dados**: Armazenamento em memória
- **Cache descartável**: Pode limpar a qualquer momento
- **Portfolio/Educacional**: Foco em demonstração e aprendizado

---

Para ideias futuras e melhorias, consulte as issues.

