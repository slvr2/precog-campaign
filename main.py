import json
import os
import pandas as pd
from datetime import datetime
from modules.analyst import processar_e_achar_padroes
from modules.persistence import init_db, create_strategy_record
from modules.feedback_agent import FeedbackAgent
from modules.orchestrator_agent.orchestrator_agent import OrchestratorAgent


PLATAFORMA = "meta_ads"      # ou google_ads
OBJETIVO = "construcao_de_marca_e_desejo"       # ou leads, traffic, sales

def main():
    print("\n🚀 --- INICIANDO PRECOG ---\n")

    init_db()

    # 1. Ingestão de Dados
    DATA_DIR = "data"

    # Busca todos os CSVs na pasta
    csv_files = [
        f for f in os.listdir(DATA_DIR)
        if f.lower().endswith(".csv")
    ]

    if not csv_files:
        print("❌ Nenhum arquivo CSV encontrado na pasta 'data/'.")
        return

    if len(csv_files) > 1:
        print(
            f"❌ Mais de um CSV encontrado na pasta 'data': {csv_files}. "
            "Deixe apenas um arquivo para execução."
        )
        return

    csv_path = os.path.join(DATA_DIR, csv_files[0])
    print(f"📂 Usando arquivo de dados: {csv_files[0]}")

    # Leitura do CSV
    try:
        df = pd.read_csv(csv_path)
        print(f"📊 Dados carregados com sucesso ({len(df)} linhas).")
    except Exception as e:
        print(f"❌ Erro crítico na ingestão de dados: {e}")
        return

    # 2. Análise (Data → Insights)
    insights = processar_e_achar_padroes(df)

    if insights.get("status") != "success":
        print(f"❌ Processo interrompido: {insights.get('reason')}")
        return
    
    # 3. Estratégia (Insights → LLM) + A/B TEST
    try:
        orchestrator = OrchestratorAgent(plataforma=PLATAFORMA, objetivo=OBJETIVO)
        result = orchestrator.executar_pipeline(insights)

        if result["status"] != "APPROVED":
            print("🚫 Pipeline interrompido pelo Orchestrator.")
            return
        
        estrategia_final = result["strategy"]

    except Exception as e:
        print(f"❌ Erro na chamada do Orchestrator: {e}")
        return

    # 4. Persistência (Handoff para App B)
    nome_campanha = f"Otimização_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"

    try:
        strategy_record = create_strategy_record(
            data=estrategia_final,
            name=nome_campanha
        )

        print(
            f"💾 Estratégia persistida com sucesso | "
            f"ID={strategy_record.id} | Status={strategy_record.status}"
        )

        # 5. Feedback Agent (SIMULADO)
        feedback = FeedbackAgent.gerar_feedback_simulado(
            strategy_id=strategy_record.id
        )

        print("\n🔄 --- FEEDBACK SIMULADO ---")
        print(json.dumps(feedback, indent=4, ensure_ascii=False))

    except Exception as e:
        print(f"❌ Falha ao persistir estratégia: {e}")
        return

    print("\n✅ --- PIPELINE FINALIZADO COM SUCESSO ---\n")

if __name__ == "__main__":
    main()
