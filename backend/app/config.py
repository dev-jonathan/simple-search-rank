"""
Configurações da aplicação.
"""
from pathlib import Path
import os

# Caminho para o corpus (relativo à raiz do projeto)
# No Render com rootDir=backend, o BASE_DIR é backend/, então precisamos subir 1 nível
BASE_DIR = Path(__file__).parent.parent.parent  # backend/app -> backend -> raiz
CORPUS_PATH = BASE_DIR / "pdf_dataset"

# Pode ser sobrescrito por variável de ambiente
# Se CORPUS_PATH for absoluto, usar diretamente; senão, relativo ao BASE_DIR
corpus_path_env = os.getenv("CORPUS_PATH")
if corpus_path_env:
    corpus_path = Path(corpus_path_env)
    if corpus_path.is_absolute():
        CORPUS_PATH = corpus_path
    elif corpus_path_env.startswith("../"):
        # Caminho relativo que sobe diretórios (ex: ../pdf_dataset)
        CORPUS_PATH = BASE_DIR / corpus_path_env
    else:
        # Caminho relativo ao BASE_DIR
        CORPUS_PATH = BASE_DIR / corpus_path_env
else:
    CORPUS_PATH = BASE_DIR / "pdf_dataset"

# Se deve baixar PDFs automaticamente do GitHub (apenas para desenvolvimento local)
# Em produção, deixar como False e usar apenas o cache
DOWNLOAD_PDFS = os.getenv("DOWNLOAD_PDFS", "false").lower() == "true"

