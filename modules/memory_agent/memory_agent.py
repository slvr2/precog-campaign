from modules.memory_agent.short_term import ShortTermMemory
from modules.memory_agent.long_term import LongTermMemory

class MemoryAgent:
    def __init__(self):
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory()

    def record_execution(self, strategy, score, ab_result=None):
        # Memória Curta
        self.stm.record_strategy(strategy, score)
        if ab_result:
            self.stm.record_ab_result(ab_result)

        # Memória Longa
        # Precisamos passar o valor float do score agora
        confidence = score.get("confidence_score", 0.0)
        
        if confidence >= 0.7:
            # ATENÇÃO: Passamos confidence explicitamente aqui
            self.ltm.record_success(strategy, confidence)

    def get_context(self):
        """
        Monta o dicionário exato que o Orchestrator._decidir_num_variacoes espera.
        """
        # 1. Busca dados históricos (LTM)
        ltm_stats = self.ltm.get_stats()
        
        # 2. Busca dados recentes (STM)
        # O STM guarda objetos completos de score, mas o Orchestrator quer uma lista de floats
        # para fazer max() - min().
        stm_data = self.stm.recent_scores # Isso é um deque de dicts
        
        # Transforma [{'confidence_score': 0.8}, ...] em [0.8, ...]
        recent_confidences_list = [
            item.get("confidence_score", 0.0) 
            for item in stm_data
        ]

        # 3. Retorna o pacote completo
        return {
            # Usado para Cold Start (< 3) e Alta Confiança (>= 5)
            "executions_count": ltm_stats["total_executions"],
            
            # Usado para decidir se confia no histórico (>= 0.85 ou >= 0.7)
            "historical_confidence_avg": ltm_stats["historical_confidence_avg"],
            
            # Usado para calcular instabilidade (variacao > 0.15)
            "recent_confidences": recent_confidences_list,
            
            # (Opcional) Se precisar dos insights qualitativos para o prompt
            "insights": self.ltm.get_insights() if hasattr(self.ltm, "get_insights") else {}
        }