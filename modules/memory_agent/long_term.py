import json
import os
from collections import Counter

MEMORY_FILE = "data/long_term_memory.json"

class LongTermMemory:

    def __init__(self):
        if not os.path.exists(MEMORY_FILE):
            self.data = {
                # Estatísticas Quantitativas (Novo)
                "global_stats": {
                    "total_executions": 0,
                    "confidence_sum": 0.0  # Para calcular média
                },
                # Estatísticas Qualitativas (Existente)
                "platform_success": Counter(),
                "creative_success": Counter(),
                "interest_success": Counter()
            }
            self._persist()
        else:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                # Recarrega stats
                self.data = {
                    "global_stats": raw.get("global_stats", {"total_executions": 0, "confidence_sum": 0.0}),
                    "platform_success": Counter(raw.get("platform_success", {})),
                    "creative_success": Counter(raw.get("creative_success", {})),
                    "interest_success": Counter(raw.get("interest_success", {}))
                }

    def record_success(self, strategy, score_val: float):
        """
        Agora aceita score_val para atualizar a média histórica.
        """
        # 1. Atualiza Estatísticas Numéricas
        self.data["global_stats"]["total_executions"] += 1
        self.data["global_stats"]["confidence_sum"] += score_val

        # 2. Atualiza Preferências (Tags)
        self.data["platform_success"][strategy.get("plataforma", "unknown")] += 1
        self.data["creative_success"][strategy.get("criativo_tipo", "unknown")] += 1

        for interest in strategy.get("icp_interesses", []):
            self.data["interest_success"][interest] += 1

        self._persist()

    def get_stats(self):
        """
        Retorna os números que o Orchestrator precisa.
        """
        stats = self.data["global_stats"]
        total = stats["total_executions"]
        
        avg = 0.0
        if total > 0:
            avg = stats["confidence_sum"] / total
            
        return {
            "total_executions": total,
            "historical_confidence_avg": avg
        }

    def _persist(self):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            # Precisamos converter Counters para dicts normais para o JSON aceitar
            output = {
                "global_stats": self.data["global_stats"],
                "platform_success": dict(self.data["platform_success"]),
                "creative_success": dict(self.data["creative_success"]),
                "interest_success": dict(self.data["interest_success"])
            }
            json.dump(output, f, indent=4, ensure_ascii=False)