import json
from google import genai
from config import Config

def gerar_estrategia_llm(padroes: dict) -> dict:
    """
    Usa o Google GenAI (Nova SDK) para gerar uma estratégia.
    """
    
    print("🧠 [Strategist] A enviar dados para o Google Gemini (Novo Cliente)...")

    if padroes.get("status") != "success":
        raise ValueError("Dados insuficientes para gerar estratégia.")

    demografico = padroes['top_demographics']
    metricas = padroes['performance_metrics']

    # Prompt
    prompt = f"""
    Atue como um estrategista de Marketing Sénior. Analise os dados:
    - Público Alvo: {demografico['gender']}, Faixa Etária {demografico['age_range']}
    - ROAS: {metricas['roas']}
    
    TAREFA:
    1. Defina uma persona curta.
    2. Escreva uma DM (Direct Message) convidativa (máx 200 caracteres).
    3. Escolha 3 hashtags.

    Responda APENAS um JSON válido neste formato:
    {{
        "target_audience": "texto...",
        "message_template": "texto...",
        "keywords": ["tag1", "tag2"]
    }}
    """

    try:
        # Inicializa o novo cliente
        client = genai.Client(api_key=Config.LLM_API_KEY)
        
        # Faz a chamada usando o modelo mais recente e leve (Flash)
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt,
            config={
                'response_mime_type': 'application/json' # Força resposta JSON
            }
        )
        
        # Na nova SDK, response.text já vem limpo se usarmos o mime_type json
        estrategia_gerada = json.loads(response.text)
        
        print("✅ [Strategist] Estratégia gerada pela IA com sucesso.")
        return estrategia_gerada

    except Exception as e:
        print(f"❌ [Strategist] Erro na API: {e}")
        # Fallback
        return {
            "target_audience": f"Público {demografico['gender']} {demografico['age_range']} (Fallback)",
            "message_template": "Olá! Vi o teu perfil e achei interessante. (Fallback)",
            "keywords": ["fallback", "erro", "teste"]
        }