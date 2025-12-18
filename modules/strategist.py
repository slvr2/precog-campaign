import json
from google import genai
from config import Config

def gerar_estrategia_llm(padroes: dict) -> dict:
    """
    Usa o Google GenAI para gerar uma estratégia completa, preenchendo
    os campos ricos do novo Schema do banco de dados.
    """
    
    print("🧠 [Strategist] A enviar dados para o Google Gemini (Novo Cliente)...")

    if padroes.get("status") != "success":
        raise ValueError("Dados insuficientes para gerar estratégia.")

    demografico = padroes.get('icp_demografia', {})
    metricas = padroes.get('icp_comportamento', {})

    # Prompt Enriquecido: Pedimos para a IA preencher as lacunas do Schema
    prompt = f"""
    Atue como um estrategista de Performance e Growth Marketing.
    Analise os dados do segmento vencedor:
    
    - Perfil: {demografico.get('gender', 'N/A')}, {demografico.get('age_range', 'N/A')} anos.
    - Performance Histórica: ROAS {metricas.get('expected_roas', 0)}, Taxa de Conversão {metricas.get('conversion_rate', 0)}%.
    
    TAREFA: Desenvolva uma estratégia tática para escalar este público.
    
    Responda EXATAMENTE este JSON (sem markdown):
    {{
        "perfil_alvo_descricao": "Resumo da persona (dor e desejo) em 1 frase.",
        "icp_interesses": ["interesse_1", "interesse_2", "marca_concorrente_referencia"],
        "mensagem_template": "Direct Message curta e informal (max 200 chars) convidando para conhecer a solução.",
        "palavras_chave": ["hashtag1", "hashtag2", "hashtag3"],
        "criativo_tipo": "Sugira o melhor formato (ex: 'Reels UGC', 'Carrossel Educativo', 'Imagem Lifestyle').",
        "posicionamentos": ["Stories", "Reels", "Feed"]
    }}
    """

    try:
        client = genai.Client(api_key=Config.LLM_API_KEY)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt,
            config={
                'response_mime_type': 'application/json'
            }
        )
        
        llm_output = json.loads(response.text)

        if not isinstance(llm_output, dict):
            raise ValueError("Resposta da LLM não é um JSON válido.")
        
        # --- FUSÃO DE DADOS ---
        # Unimos o que o Analista descobriu (Passado) + O que a IA criou (Futuro)
        estrategia_final = {
            # Dados do Analista (Preservados)
            "plataforma": "instagram", # Default ou vindo do input
            "objetivo": "conversao",
            "icp_demografia": demografico,
            "icp_comportamento": metricas,
            
            # Dados da IA (Novos)
            "perfil_alvo_descricao": llm_output.get("perfil_alvo_descricao"),
            "icp_interesses": llm_output.get("icp_interesses") or [],
            "mensagem_template": llm_output.get("mensagem_template"),
            "palavras_chave": llm_output.get("palavras_chave") or [],
            "criativo_tipo": llm_output.get("criativo_tipo"),
            "posicionamentos": llm_output.get("posicionamentos") or [],
            
            "versao_modelo_llm": "gemini-2.5-flash"
        }
        
        print("✅ [Strategist] Estratégia complexa gerada com sucesso.")
        return estrategia_final

    except Exception as e:
        print(f"❌ [Strategist] Erro na API: {e}")
        # Fallback simples para não travar o sistema
        return {
            "plataforma": "instagram",
            "objetivo": "erro_fallback",
            "icp_demografia": {},
            "icp_comportamento": {},
            "perfil_alvo_descricao": "Erro na geração.",
            "mensagem_template": "Olá!",
            "palavras_chave": [],
            "icp_interesses": [],
            "criativo_tipo": None,
            "posicionamentos": [],
            "versao_modelo_llm": "fallback"
        }