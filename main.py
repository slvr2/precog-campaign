import json
import pandas as pd
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Importações dos módulos locais
from config import Config
from modules.analyst import processar_e_achar_padroes
from modules.strategist import gerar_estrategia_llm

# --- CONFIGURAÇÃO DO ORM (SQLAlchemy) ---
Base = declarative_base()

class CampaignStrategy(Base):
    __tablename__ = 'campaign_strategies'
    
    id = Column(Integer, primary_key=True)
    campaign_name = Column(String)
    target_profile_description = Column(Text)
    keywords = Column(JSON) # Armazena lista como JSON
    message_template = Column(Text)
    status = Column(String, default='PENDING') # O gatilho para a App B
    created_at = Column(DateTime, default=datetime.utcnow)

# Configuração da conexão
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def save_strategy(strategy_data: dict, campaign_name: str):
    """
    Função de Persistência: Grava a Ordem de Serviço no PostgreSQL.
    """
    print("💾 [System] Gravando Ordem de Serviço no Banco de Dados...")
    
    # Cria a tabela se não existir (apenas para dev, em prod use Migrations/Alembic)
    Base.metadata.create_all(engine)
    
    session = SessionLocal()
    try:
        nova_estrategia = CampaignStrategy(
            campaign_name=campaign_name,
            target_profile_description=strategy_data['target_audience'],
            keywords=strategy_data['keywords'],
            message_template=strategy_data['message_template'],
            status='PENDING' # Importante: Isso avisa a App B
        )
        session.add(nova_estrategia)
        session.commit()
        print(f"🚀 [Success] Estratégia '{campaign_name}' salva com ID: {nova_estrategia.id}")
    except Exception as e:
        print(f"❌ Erro ao salvar no banco: {e}")
        session.rollback()
    finally:
        session.close()

def main():
    print("--- INICIANDO INTELLIGENCE CORE (APP A) ---")
    
    # 1. Ingestão de Dados
    csv_path = 'data/campaign_data.csv'
    
    # Mock: Se não existir arquivo, cria um fake para teste
    if not os.path.exists(csv_path): # Nota: Apague o arquivo .csv da pasta data antes de rodar!
        print("⚠️ Arquivo não encontrado. Gerando dados dummy...")
        data = {
            # Vamos inverter: Mulheres gastam muito e retornam pouco. Homens gastam pouco e retornam muito.
            'age_range': ['25-34', '25-34', '35-44', '18-24'],
            'gender':    ['F',     'F',     'M',     'F'],
            'spend':     [100,     150,     50,      50],  # Homem gastou só 50
            'revenue':   [100,     150,     500,     25],  # Homem retornou 500 (ROAS 10!)
            'conversions': [2,      3,       15,      1]
        }
        pd.DataFrame(data).to_csv(csv_path, index=False)
        
    try:
        df = pd.read_csv(csv_path)
        print(f"📂 Dados carregados: {len(df)} linhas.")
    except Exception as e:
        print(f"❌ Erro crítico na ingestão: {e}")
        return

    # 2. Análise (Data -> Insights)
    insights = processar_e_achar_padroes(df)
    
    if insights['status'] != 'success':
        print(f"⏹️ Processo interrompido: {insights.get('reason')}")
        return

    # 3. Estratégia (Insights -> Action Plan via LLM)
    try:
        estrategia_final = gerar_estrategia_llm(insights)
        # --- ADICIONE ISTO PARA VER O RESULTADO NO TERMINAL ---
        print("\n📝 --- ESTRATÉGIA GERADA PELA IA ---")
        print(json.dumps(estrategia_final, indent=4, ensure_ascii=False))
        print("---------------------------------------\n")
        # ------------------------------------------------------
    except Exception as e:
        print(f"❌ Erro na geração de estratégia: {e}")
        return

    # 4. Persistência (Handoff para App B)
    nome_campanha = f"Otimização_{datetime.now().strftime('%Y-%m-%d')}"
    save_strategy(estrategia_final, nome_campanha)
    
    print("--- FIM DO PROCESSO (APP A) ---")

if __name__ == "__main__":
    main()