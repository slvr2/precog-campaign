import os
from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from contextlib import contextmanager 
from datetime import datetime
from config import Config

# --- 0. Configuração do Ambiente ---
try:
    DATABASE_URL = Config.DATABASE_URL # Importa configurações (assumindo o config.py configurado)
except AttributeError as e:
    raise RuntimeError(
        "Erro de configuração: DATABASE_URL não foi definido em Config. "
        "Verifique se o arquivo config.py possui a variável DATABASE_URL."
    ) from e


# --- 1. Configuração da Engine ---
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True) # Engine para conexão com o banco de dados

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Cada requisição/thread deve criar sua própria sessão.

Base = declarative_base() # Base para os modelos

# --- 2. Definição dos Modelos (Tabelas) ---
class CampaignStrategy(Base):
    """
    Gerada pela APP A (Intelligence).
    Define O QUE fazer com base em dados agregados e LLM.
    """

    __tablename__ = 'campaign_strategies'

    id = Column(Integer, primary_key=True, index=True)

    # Identificação
    campanha_nome = Column(String, index=True)
    plataforma = Column(String, nullable=False, index=True)  # instagram, tiktok, google
    objetivo = Column(String, nullable=False, index=True)    # lead_generation, traffic, sales

    # ICP GERADO PELO LLM (ESTRUTURADO)
    icp_demografia = Column(JSON)     # idade, genero, localizacao
    icp_interesses = Column(JSON)     # interesses, palavras-chave
    icp_comportamento = Column(JSON)  # engajamento esperado, sinais

    # OUTPUT DO LLM
    perfil_alvo_descricao = Column(Text)
    mensagem_template = Column(Text)
    palavras_chave = Column(JSON)

    # HIPÓTESE / CONTEXTO
    criativo_tipo = Column(String)  # video, imagem, carrossel
    posicionamentos = Column(JSON)  # feed, reels, stories
    racional_estrategico = Column(Text, nullable=True)

    # CONTROLE
    status = Column(String, default="PENDING", index=True)
    versao_modelo_llm = Column(String)

    # FEEDBACK AGREGADO (aprendizado)
    total_leads = Column(Integer, default=0)
    taxa_resposta = Column(Float, default=0.0)
    taxa_conversao = Column(Float, default=0.0)
    custo_medio_lead = Column(Float, default=0.0)

    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    ultima_atualizacao = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamento
    leads = relationship("Lead", back_populates="strategy")


class Lead(Base):
    """
    Gerada pela APP B (Execution).
    Representa um contato encontrado e abordado.
    """

    __tablename__ = 'leads'

    id = Column(Integer, primary_key=True, index=True)

    # Estratégia que originou o lead
    strategy_id = Column(Integer, ForeignKey('campaign_strategies.id'))
    strategy = relationship("CampaignStrategy", back_populates="leads")

    # Origem
    plataforma = Column(String)  # instagram, tiktok
    fonte = Column(String)       # ads, organico, scraping
    campanha_externa_id = Column(String)  # id da campanha na plataforma

    # Identificação mínima (permitida)
    username = Column(String, index=True)
    user_id = Column(String)  # id público da plataforma

    # CONTEXTO DO ENCONTRO (muito importante pro aprendizado)
    posicionamento = Column(String)     # feed, reels
    criativo_tipo = Column(String)      # video, imagem
    interesse_detectado = Column(String)  # inferido via contexto

    # STATUS DE INTERAÇÃO
    interaction_status = Column(
        String,
        default="NEW"  # NEW → QUEUED → SENT → FAILED → REPLIED → CONVERTED
    )

    # SINAIS DE QUALIDADE
    respondeu = Column(Boolean, default=False)
    converteu = Column(Boolean, default=False)
    score_qualidade = Column(Float)  # scoring interno (opcional)

    # TIMESTAMPS
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
    except Exception as e:
        raise RuntimeError(
            "❌ [Persistence] Falha ao inicializar o banco de dados."
        ) from e


@contextmanager
def get_db_session():
    """
    Generator para gerenciar o ciclo de vida da sessão.
    Uso: with get_db_session() as db: ...
    """

    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# --- 4. Funções de Negócio (CRUD) ---
def create_strategy_record(data: dict, name: str):
    """
    Persiste a estratégia.
    O commit é feito automaticamente pelo get_db_session ao sair do bloco.
    """

    with get_db_session() as session:
        new_strategy = CampaignStrategy(
            campanha_nome=name,
            plataforma=data.get("plataforma"),
            objetivo=data.get("objetivo"),
            
            icp_demografia=data.get("icp_demografia", {}),
            icp_interesses=data.get("icp_interesses", {}),
            icp_comportamento=data.get("icp_comportamento", {}),
            
            perfil_alvo_descricao=data.get("perfil_alvo_descricao"),
            mensagem_template=data.get("mensagem_template"),
            palavras_chave=data.get("palavras_chave", []),
            
            criativo_tipo=data.get("criativo_tipo"),
            posicionamentos=data.get("posicionamentos", []),
            racional_estrategico=data.get("racional_estrategico"),
            
            status="PENDING",
            versao_modelo_llm=data.get("versao_modelo_llm"),
        )

        session.add(new_strategy)
        session.flush()  # Envia SQL para o banco (Gera ID e Defaults)
        session.refresh(new_strategy) # Puxa do banco o 'created_at' e confirma o ID
        session.expunge(new_strategy) # Desconecta o objeto da sessão para ele sobreviver fora daqui

        return new_strategy