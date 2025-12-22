import json
from google import genai
from config import Config

def gerar_estrategia_llm(padroes: dict, plataforma: str, objetivo: str) -> dict:
    """
    Usa o Google GenAI para gerar uma estratégia completa, preenchendo
    os campos ricos do novo Schema do banco de dados.
    """

    if padroes.get("status") != "success":
        raise ValueError("Dados insuficientes para gerar estratégia.")

    demografico = padroes.get('icp_demografia', {})
    metricas = padroes.get('icp_comportamento', {})

    prompt = f"""
    # AGENTE ESTRATEGISTA DE PERFORMANCE (ARQUITETURA AGÊNTICA)

    ## 1. INPUT DE DADOS (FONTE ÚNICA DE VERDADE)
    Resumo Analítico: {padroes["insight_text"]}

    Perfil Demográfico do ICP:
    - Faixa etária: {padroes["icp_demografia"]["age_range"]} | Gênero: {padroes["icp_demografia"]["gender"]} | Localização: {padroes["icp_demografia"]["location"]}

    Comportamento Observado:
    - ROAS esperado: {padroes["icp_comportamento"]["expected_roas"]} | Taxa de conversão: {padroes["icp_comportamento"]["conversion_rate"]}% | Cliques: {padroes["icp_comportamento"]["click_volume"]}

    Contexto:
    - Plataforma: {plataforma} | Objetivo: {objetivo}

    Ao definir icp_interesses e palavras_chave:
    - Baseie-se apenas em sinais implícitos do comportamento observado
    - Evite interesses altamente específicos ou identitários

    ---

    ## 2. REGRAS DE SEGURANÇA E ALINHAMENTO (GUARDRAILS)
    - **Fidelidade Estrita:** NÃO altere dados demográficos ou métricas observadas.
    - **Proibição de Alucinação:** NÃO utilize tendências externas, personas fictícias ou suposições fora do contexto fornecido.
    - **Estilo:** Use linguagem clara, objetiva e ampla, em português brasileiro.
    - **Restrição de Saída:** Retorne EXCLUSIVAMENTE um JSON válido, sem qualquer texto introdutório ou conclusivo.
    
    ---

    ## 3. INSTRUÇÕES DE PENSAMENTO (CoT IMPLÍCITO)
    Antes de gerar o JSON, analise internamente:
    1. Como o ROAS de {metricas.get('expected_roas')} influencia a agressividade da oferta?
    2. Qual tom de voz conecta melhor com {demografico.get('gender')} de {demografico.get('age_range')} anos?
    3. Revise se os interesses sugeridos são compatíveis com o comportamento de conversão observado.

    ---

    ## 4. FORMATO DE SAÍDA (JSON OBRIGATÓRIO)
    {{
    "perfil_alvo_descricao": "string",
    "icp_interesses": ["string"],
    "mensagem_template": "string",
    "palavras_chave": ["string"],
    "criativo_tipo": "string",
    "posicionamentos": ["string"],
    "racional_estrategico": "string (Explique brevemente por que essa estratégia funcionará para este público específico)"
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
        estrategia_final = {
            # Dados do Analista (Preservados)
            "plataforma": plataforma, # Default ou vindo do input
            "objetivo": objetivo,
            "icp_demografia": demografico,
            "icp_comportamento": metricas,
            
            # Dados da IA (Novos)
            "perfil_alvo_descricao": llm_output.get("perfil_alvo_descricao"),
            "icp_interesses": llm_output.get("icp_interesses") or [],
            "mensagem_template": llm_output.get("mensagem_template"),
            "palavras_chave": llm_output.get("palavras_chave") or [],
            "criativo_tipo": llm_output.get("criativo_tipo"),
            "posicionamentos": llm_output.get("posicionamentos") or [],
            "racional_estrategico": llm_output.get("racional_estrategico"),
            "versao_modelo_llm": "gemini-2.5-flash"
        }
        return estrategia_final

    except Exception as e:
        # Fallback simples para não travar o sistema
        return {
            "plataforma": plataforma,
            "objetivo": "erro_fallback",
            "icp_demografia": {},
            "icp_comportamento": {},
            "perfil_alvo_descricao": "Erro na geração.",
            "mensagem_template": "Olá!",
            "palavras_chave": [],
            "icp_interesses": [],
            "criativo_tipo": None,
            "posicionamentos": [],
            "racional_estrategico": None,
            "versao_modelo_llm": "fallback"
        }