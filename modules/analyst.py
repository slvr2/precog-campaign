import pandas as pd

def processar_e_achar_padroes(df: pd.DataFrame) -> dict:
    """
    Analisa o DataFrame para encontrar o segmento demográfico com melhor ROAS.
    Retorna um dicionário com os insights.
    """
    print("📊 [Analyst] Iniciando análise de dados...")

    # 1. Limpeza Básica
    # Converte colunas numéricas caso venham como string
    cols_numericas = ['spend', 'revenue', 'clicks', 'impressions']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 2. Feature Engineering: Calcular ROAS
    # Evita divisão por zero
    df['roas'] = df.apply(lambda x: x['revenue'] / x['spend'] if x['spend'] > 0 else 0, axis=1)

    # 3. Agrupamento e Análise (Busca por Padrões)
    # Agrupa por Idade e Gênero para achar o "Avatar" vencedor
    # Filtro de Significância Estatística: Ignora grupos com menos de 10 conversões/vendas
    # Supondo que exista uma coluna 'conversions', senão usa 'clicks' como proxy
    metric_col = 'conversions' if 'conversions' in df.columns else 'clicks'
    
    analysis_group = df.groupby(['age_range', 'gender']).agg({
        'spend': 'sum',
        'revenue': 'sum',
        metric_col: 'sum',
        'roas': 'mean'
    }).reset_index()

    # Aplica o filtro de "Reflection" (Significância)
    # Só consideramos segmentos com volume mínimo de dados
    valid_segments = analysis_group[analysis_group[metric_col] > 10]

    if valid_segments.empty:
        return {
            "status": "insufficient_data",
            "reason": "Nenhum segmento atingiu o volume mínimo de significância."
        }

    # 4. Seleção do Vencedor (Winner Takes All)
    best_segment = valid_segments.loc[valid_segments['roas'].idxmax()]

    # Criação do Resumo
    resumo_padroes = {
        "status": "success",
        "top_demographics": {
            "age_range": best_segment['age_range'],
            "gender": best_segment['gender']
        },
        "performance_metrics": {
            "roas": round(best_segment['roas'], 2),
            "total_spend": round(best_segment['spend'], 2),
            "volume_metric": int(best_segment[metric_col])
        },
        "insight_text": (
            f"O segmento {best_segment['gender']} de {best_segment['age_range']} "
            f"teve o melhor desempenho com ROAS de {round(best_segment['roas'], 2)}."
        )
    }

    print(f"✅ [Analyst] Padrão identificado: {resumo_padroes['insight_text']}")
    return resumo_padroes