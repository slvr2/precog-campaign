# 🧠 Intelligence Previsor Core

## Visão Geral

O **Intelligence Core (App A)** é o núcleo analítico do projeto **LLM-Previsor**. Seu papel é transformar dados brutos de campanhas em **estratégias de marketing estruturadas**, utilizando análise estatística + LLM (Google Gemini).

Ele atua como o **primeiro estágio do pipeline**, sendo responsável por:

1. Ingestão de dados de campanha (CSV)
2. Identificação de padrões de performance
3. Geração de estratégia via LLM
4. Persistência da estratégia para consumo posterior (App B)

---

## Arquitetura de Alto Nível

```
Data (CSV)
   ↓
[ Analyst ]  →  Insights Estruturados
   ↓
[ Strategist (LLM) ]  →  Estratégia de Marketing
   ↓
[ Persistence ]  →  Banco de Dados (handoff)
```

---

## Estrutura de Pastas

```
LLM-Previsor/
├─ data/
│  ├─ campaign_data_minimal.csv
│  ├─ campaign_data_realistic.csv
│  └─ campaign_data_edge_cases.csv
│
├─ modules/
│  ├─ __init__.py    
│  ├─ analyst.py        # Análise estatística e identificação de padrões
│  ├─ strategist.py     # Integração com LLM (Google Gemini)
│  └─ persistence.py    # Persistência e contratos de dados
│
├─ .env                 # Variáveis de ambiente (não versionado)
├─ .gitignore
├─ docker-compose.yml   # Infraestrutura local (serviços auxiliares)
├─ requirements.txt     # Dependências do projeto
├─ main.py              # Orquestrador do pipeline (App A)
└─ README.md            # Documentação técnica do projeto
```

---

## Fluxo de Execução (main.py)

### 1️⃣ Ingestão de Dados

* O sistema lê **automaticamente o único arquivo CSV presente na pasta `data/`**
* O nome do arquivo é irrelevante
* Regras:

  * ❌ Nenhum CSV → erro e aborta
  * ❌ Mais de um CSV → erro e aborta
  * ✅ Exatamente um CSV → pipeline segue

```python
csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
```

---

### 2️⃣ Análise – `modules/analyst.py`

Responsável por:

* Agrupar dados por **faixa etária + gênero**
* Calcular métricas-chave:

  * ROAS
  * CTR
  * CVR
* Identificar o **segmento campeão**

#### Saída (contrato):

```json
{
  "status": "success",
  "best_segment": {
    "age_range": "35-44",
    "gender": "M",
    "roas": 10.0,
    "conversion_rate": 16.7,
    "clicks": 90
  }
}
```

Se nenhuma análise válida for possível:

```json
{
  "status": "fail",
  "reason": "Dados insuficientes"
}
```

---

### 3️⃣ Estratégia – `modules/strategist.py`

* Recebe **insights estruturados** (não dados crus)
* Envia payload ao **Google Gemini**
* Retorna uma **estratégia de marketing completa e validada**

#### Validação obrigatória

```python
if not estrategia_final.get("perfil_alvo_descricao"):
    raise ValueError("Payload da estratégia incompleto.")
```

#### Saída esperada:

```json
{
  "plataforma": "instagram",
  "objetivo": "conversao",
  "icp_demografia": {...},
  "icp_comportamento": {...},
  "perfil_alvo_descricao": "...",
  "mensagem_template": "...",
  "palavras_chave": [...],
  "criativo_tipo": "...",
  "posicionamentos": [...],
  "versao_modelo_llm": "gemini-2.5-flash"
}
```

---

### 4️⃣ Persistência – `modules/persistence.py`

* Inicializa o banco de dados
* Armazena a estratégia como **fonte única de verdade**
* Retorna objeto persistido com ID e status

```python
create_strategy_record(data=estrategia_final, name=nome_campanha)
```

---

## Casos de Teste Oficiais

### 🧪 1. campaign_data_minimal.csv

**Objetivo:** Smoke test / CI

* Poucos dados
* Espera-se:

  * Pipeline completo
  * Estratégia simples, porém válida

---

### 🧪 2. campaign_data_realistic.csv

**Objetivo:** Simular cenário real

* Dados mais variados
* Espera-se:

  * ICP mais refinado
  * Mensagem mais contextual

---

### 🧪 3. campaign_data_edge_cases.csv

**Objetivo:** Testar extremos

* ROAS e CVR muito altos
* Espera-se:

  * Nenhum overflow ou erro
  * Estratégia agressiva / premium

---

## Decisões Arquiteturais Importantes

* ❌ Sem dependência de nome de arquivo
* ✅ Contratos explícitos entre módulos
* ✅ LLM isolado da lógica estatística
* ✅ Pipeline aborta cedo em caso de erro
* ✅ Pronto para CI/CD e automação

---

## Próximos Passos (Roadmap)

* [ ] Testes automatizados (pytest)
* [ ] Versionamento de estratégias
* [ ] App B (Execução e Monitoramento)
* [ ] Observabilidade (logs estruturados)

---

## Status do Projeto

🟢 **Estável** | 🧪 **Testado** | 🚀 **Pronto para evolução**
