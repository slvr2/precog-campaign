import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

class Config:
    # --- CONEXÃO COM O BANCO DE DADOS ---
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Fix para supabase
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    if not DATABASE_URL:
        raise ValueError("❌ Erro: A variável DATABASE_URL não foi encontrada no arquivo .env")

    # --- CHAVES DE API (IA) ---
    LLM_API_KEY = os.getenv("LLM_API_KEY")