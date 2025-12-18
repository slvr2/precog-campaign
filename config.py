import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

class Config:
    # --- CONEXÃO COM O BANCO DE DADOS ---
    # Agora ele busca a URL completa diretamente do .env
    DATABASE_URL = os.getenv("DATABASE_URL")

    # [FIX CRÍTICO PARA SUPABASE]
    # O Supabase às vezes fornece a URL começando com "postgres://".
    # O SQLAlchemy (Python) prefere "postgresql://".
    # Esta linha faz a correção automática se necessário:
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    if not DATABASE_URL:
        raise ValueError("❌ Erro: A variável DATABASE_URL não foi encontrada no arquivo .env")

    # --- CHAVES DE API (IA) ---
    LLM_API_KEY = os.getenv("LLM_API_KEY")