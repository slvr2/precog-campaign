import os
from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime

# Importa configurações (assumindo que você tem o config.py configurado)
# Se estiver rodando local, certifique-se que o Config aponta para localhost
try:
    from config import Config
    DATABASE_URL = Config.DATABASE_URL
except ImportError:
    # Fallback para teste rápido caso config.py não exista
    DATABASE_URL = "postgresql://admin:secret@localhost:5432/growth_engine"

# --- 1. Configuração da Engine ---
# echo=False desativa logs excessivos de SQL no terminal
engine = create_engine(DATABASE_URL, echo=False)

# SessionLocal é a fábrica de sessões. Cada requisição/thread deve criar sua própria sessão.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

# --- 2. Definição dos Modelos (Tabelas) ---

class CampaignStrategy(Base):
    """
    Tabela preenchida pela APP A (Intelligence).
    Define O QUE deve ser feito.
    """
    __tablename__ = 'campaign_strategies'

    id = Column(Integer, primary_key=True, index=True)
    campaign_name = Column(String, index=True)
    
    # Dados gerados pelo LLM
    target_profile_description = Column(Text) # Descrição humana
    keywords = Column(JSON)                   # Lista ["tag1", "tag2"]
    message_template = Column(Text)           # "Olá {name}..."
    
    # Controle de Estado para a App B
    # Status: PENDING -> PROCESSING -> COMPLETED
    status = Column(String, default="PENDING", index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamento com os leads (One-to-Many)
    leads = relationship("Lead", back_populates="strategy")


class Lead(Base):
    """
    Tabela preenchida pela APP B (Execution).
    Armazena QUEM foi encontrado e contactado.
    """
    __tablename__ = 'leads'

    id = Column(Integer, primary_key=True, index=True)
    
    # Link com a estratégia mãe
    strategy_id = Column(Integer, ForeignKey('campaign_strategies.id'))
    strategy = relationship("CampaignStrategy", back_populates="leads")
    
    # Dados do usuário encontrado
    platform = Column(String) # "instagram", "tiktok"
    username = Column(String, index=True)
    user_id = Column(String)  # ID numérico da plataforma (se houver)
    
    # Controle de envio
    # Status: NEW -> QUEUED -> SENT -> FAILED -> REPLIED
    interaction_status = Column(String, default="NEW")
    
    found_at = Column(DateTime(timezone=True), server_default=func.now())
    last_interaction_at = Column(DateTime(timezone=True), nullable=True)

# --- 3. Funções Utilitárias de Banco ---

def init_db():
    """
    Cria as tabelas no banco de dados se elas não existirem.
    Deve ser chamada no início do main.py.
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ [Persistence] Tabelas verificadas/criadas com sucesso.")
    except Exception as e:
        print(f"❌ [Persistence] Erro ao conectar ao banco: {e}")

def get_db_session():
    """
    Generator para gerenciar o ciclo de vida da sessão.
    Uso: with get_db_session() as db: ...
    """
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# --- 4. Funções de Negócio (CRUD) ---

def create_strategy_record(data: dict, name: str):
    """
    Salva a estratégia gerada pela App A.
    """
    session = SessionLocal()
    try:
        new_strategy = CampaignStrategy(
            campaign_name=name,
            target_profile_description=data['target_audience'],
            keywords=data['keywords'],
            message_template=data['message_template'],
            status='PENDING' # O gatilho inicial
        )
        session.add(new_strategy)
        session.commit()
        session.refresh(new_strategy)
        return new_strategy
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()