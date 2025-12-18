import json
import os
import pandas as pd
from datetime import datetime

# Pipeline Core
from modules.analyst import processar_e_achar_padroes
from modules.strategist import gerar_estrategia_llm

# Persistence (fonte única de verdade)
from modules.persistence import init_db, create_strategy_record


def main():
    print("\n🚀 --- INICIANDO INTELLIGENCE CORE (APP A) ---\n")

    init_db()

    # 1. Ingestão de Dados
    csv_path = "data/campaign_data.csv"

    # Mock para desenvolvimento local
    if not os.path.exists(csv_path):
        print("⚠️ CSV não encontrado. Gerando dados dummy para teste...")

        data = {
            "age_range": ["25-34", "25-34", "35-44", "18-24"],
            "gender": ["F", "F", "M", "F"],
            "spend": [100, 150, 50, 50],
            "revenue": [100, 150, 500, 25],
            "clicks": [80, 120, 90, 40],
            "impressions": [2000, 3000, 1500, 1000],
            "conversions": [2, 3, 15, 1],
        }

        os.makedirs("data", exist_ok=True)
        pd.DataFrame(data).to_csv(csv_path, index=False)

    try:
        df = pd.read_csv(csv_path)
        print(f"📂 Dados carregados com sucesso ({len(df)} linhas).")
    except Exception as e:
        print(f"❌ Erro crítico na ingestão de dados: {e}")
        return

    # 2. Análise (Data → Insights)
    insights = processar_e_achar_padroes(df)

    if insights.get("status") != "success":
        print(f"⏹️ Processo interrompido: {insights.get('reason')}")
        return
    
    # 3. Estratégia (Insights → Plano Tático via LLM)
    try:
        estrategia_final = gerar_estrategia_llm(insights)

        if not estrategia_final.get("perfil_alvo_descricao"):
            raise ValueError("Payload da estratégia incompleto.")

        print("\n🧠 --- ESTRATÉGIA GERADA PELA IA ---")
        print(json.dumps(estrategia_final, indent=4, ensure_ascii=False))
        print("---------------------------------\n")

    except Exception as e:
        print(f"❌ Erro na geração da estratégia: {e}")
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

    except Exception as e:
        print(f"❌ Falha ao persistir estratégia: {e}")
        return

    print("\n✅ --- PIPELINE FINALIZADO COM SUCESSO (APP A) ---\n")


if __name__ == "__main__":
    main()
