"""
Script para baixar PDFs do repositório GitHub.
"""
import os
import zipfile
import shutil
from pathlib import Path
import requests
from tqdm import tqdm

GITHUB_REPO = "dev-jonathan/wiki-popular-articles-to-pdf"
GITHUB_BRANCH = "main"
PDF_DATASET_PATH = "pdf_dataset"
DOWNLOAD_URL = f"https://github.com/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"

def download_pdfs(output_dir: Path):
    """
    Baixa PDFs do repositório GitHub.
    
    Args:
        output_dir: Diretório onde os PDFs serão salvos
    """
    print(f"📥 Baixando PDFs de {GITHUB_REPO}...")
    
    # Criar diretório temporário
    temp_dir = output_dir.parent / "temp_download"
    temp_dir.mkdir(exist_ok=True)
    zip_path = temp_dir / "repo.zip"
    
    try:
        # Baixar ZIP do GitHub
        print("  Fazendo download do repositório...")
        response = requests.get(DOWNLOAD_URL, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        with open(zip_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc="  Download") as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        
        # Extrair ZIP
        print("  Extraindo arquivos...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Copiar PDFs
        repo_name = GITHUB_REPO.split('/')[-1]
        extracted_dir = temp_dir / f"{repo_name}-{GITHUB_BRANCH}" / PDF_DATASET_PATH
        if not extracted_dir.exists():
            raise FileNotFoundError(f"Pasta {PDF_DATASET_PATH} não encontrada no repositório")
        
        # Criar diretório de saída
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copiar PDFs
        pdf_files = list(extracted_dir.glob("*.pdf"))
        if not pdf_files:
            raise FileNotFoundError(f"Nenhum PDF encontrado em {extracted_dir}")
        
        print(f"  Copiando {len(pdf_files)} PDFs...")
        for pdf_file in tqdm(pdf_files, desc="  Copiando"):
            (output_dir / pdf_file.name).write_bytes(pdf_file.read_bytes())
        
        print(f"✅ {len(pdf_files)} PDFs baixados para {output_dir}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao baixar do GitHub: {e}")
        print(f"   URL: {DOWNLOAD_URL}")
        raise
    except Exception as e:
        print(f"❌ Erro ao processar download: {e}")
        raise
    finally:
        # Limpar arquivos temporários
        if zip_path.exists():
            zip_path.unlink()
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    # Para uso direto via script
    import sys
    from pathlib import Path
    
    # Adicionar backend ao path para importar config
    backend_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(backend_dir))
    
    from app.config import CORPUS_PATH
    
    if CORPUS_PATH.exists() and list(CORPUS_PATH.glob("*.pdf")):
        print(f"✅ PDFs já existem em {CORPUS_PATH}")
        response = input("Deseja baixar novamente? (s/N): ")
        if response.lower() != 's':
            print("Cancelado.")
            sys.exit(0)
    
    download_pdfs(CORPUS_PATH)
