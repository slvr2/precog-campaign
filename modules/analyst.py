import pandas as pd

def processar_e_achar_padroes(df: pd.DataFrame) -> dict:
    """
    Analisa o DataFrame para encontrar o segmento demográfico com melhor ROAS.
    Retorna um dicionário estruturado compatível com o Schema do Banco de Dados.
    """

    print("📊 [Analyst] Iniciando análise de dados...")

    # 1. Limpeza Básica e Garantia de Tipos
    cols_numericas = ['spend', 'revenue', 'clicks', 'impressions', 'conversions']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    # Garante que conversions existe (para evitar erro de chave)
    if 'conversions' not in df.columns:
        df['conversions'] = 0

    # 2. Agrupamento Inteligente (Soma tudo primeiro)
    group_cols = ['age_range', 'gender']     # Agrupa por Idade e Gênero
    
    analysis_group = df.groupby(group_cols).agg({
        'spend': 'sum',
        'revenue': 'sum',
        'clicks': 'sum',
        'impressions': 'sum',
        'conversions': 'sum'
    }).reset_index()

    # 3. Feature Engineering no Grupo (Matemática Correta)
    # Calcula ROAS Global do grupo (Evita média das médias)
    analysis_group['roas'] = 0
    mask_spend = analysis_group['spend'] > 0
    analysis_group.loc[mask_spend, 'roas'] = (
        analysis_group.loc[mask_spend, 'revenue'] /
        analysis_group.loc[mask_spend, 'spend']
    )
        
    # Calcula Taxa de Conversão (CVR) - Útil para 'icp_comportamento'
    analysis_group['cvr'] = 0
    mask_clicks = analysis_group['clicks'] > 0
    analysis_group.loc[mask_clicks, 'cvr'] = (
        analysis_group.loc[mask_clicks, 'conversions'] /
        analysis_group.loc[mask_clicks, 'clicks']
    )

    # 4. Filtro de Significância (Reflection)
    valid_segments = analysis_group[analysis_group['conversions'] >= 5] # Ignora grupos irrelevantes (ex: menos de 5 conversões ou gasto < 100)

    if valid_segments.empty:
        # Tenta fallback por cliques se não tiver conversão suficiente
        valid_segments = analysis_group[analysis_group['clicks'] >= 50]
        
    if valid_segments.empty:
        return {
            "status": "insufficient_data",
            "reason": "Nenhum segmento atingiu o volume mínimo de significância."
        }

    # 5. Seleção do Vencedor
    best_segment = valid_segments.loc[valid_segments['roas'].idxmax()]

    # 6. Formatação para o Novo Schema de Persistência
    resumo_padroes = { # Aqui montamos os JSONs que o banco espera
        "status": "success",
        
        # Mapeia direto para a coluna 'icp_demografia'
        "icp_demografia": {
            "age_range": best_segment['age_range'],
            "gender": best_segment['gender'],
            "location": "Brazil" # Placeholder ou derivado dos dados se tiver
        },
        
        # Mapeia direto para a coluna 'icp_comportamento'
        "icp_comportamento": {
            "expected_roas": round(best_segment['roas'], 2),
            "conversion_rate": round(best_segment['cvr'] * 100, 2), # Em porcentagem
            "click_volume": int(best_segment['clicks'])
        },
        
        # Dados brutos para logs ou debug
        "performance_metrics": {
            "total_spend": round(best_segment['spend'], 2),
            "total_revenue": round(best_segment['revenue'], 2),
            "total_conversions": int(best_segment['conversions'])
        },
        
        # Texto para o Prompt do LLM (Strategist)
        "insight_text": (
            f"O segmento {best_segment['gender']} de {best_segment['age_range']} "
            f"é o campeão com ROAS de {round(best_segment['roas'], 2)} "
            f"e Taxa de Conversão de {round(best_segment['cvr']*100, 1)}%."
        )
    }

    print(f"✅ [Analyst] Padrão identificado: {resumo_padroes['insight_text']}")
    return resumo_padroes