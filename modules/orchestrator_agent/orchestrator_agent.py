from modules.strategist import gerar_estrategia_llm
from modules.ab_agent import ABAgent
from modules.score_agent import ScoreAgent
from modules.memory_agent.memory_agent import MemoryAgent


class OrchestratorAgent:
    """
    Cérebro central de decisão.
    Controla o fluxo estratégico antes da persistência.
    """

    def __init__(
        self,
        plataforma: str,
        objetivo: str,
        confidence_threshold: float = 0.6
    ):
        self.plataforma = plataforma
        self.objetivo = objetivo
        self.confidence_threshold = confidence_threshold
        self.memory = MemoryAgent()

    def executar_pipeline(self, insights: dict) -> dict:
        """
        Executa o pipeline completo de decisão estratégica.
        Retorna a estratégia final ou um bloqueio.
        """

        print("🧠 Iniciando decisão estratégica...")

        # DECIDIR QUANTAS ESTRATÉGIAS GERAR
        num_variacoes = self._decidir_num_variacoes()
        print(f"🧪 Gerando {num_variacoes} variações.")

        estrategias = [
            gerar_estrategia_llm(insights, plataforma=self.plataforma, objetivo=self.objetivo)
            for _ in range(num_variacoes)
        ]

        # A/B TEST
        if num_variacoes > 1:
            ab_result = ABAgent.comparar(estrategias)

            print("🧪 Resultado A/B:")
            print(ab_result)

            if ab_result["status"] != "WINNER":
                return self._bloqueio(
                    reason="AB_INCONCLUSIVE",
                    ab_result=ab_result
                )

            estrategia_final = ab_result["winner_strategy"]
        else:
            ab_result = None
            estrategia_final = estrategias[0]

        # SCORE DA ESTRATÉGIA
        score = ScoreAgent.avaliar(estrategia_final)

        print("📊 Score calculado:", score)

        if score["confidence_score"] < self.confidence_threshold:
            self.memory.record_execution(
                strategy=estrategia_final,
                score=score,
                ab_result=ab_result
            )

            return self._bloqueio(
                reason="LOW_CONFIDENCE_SCORE",
                score=score
            )

        # MEMÓRIA (APRENDIZADO)
        self.memory.record_execution(
            strategy=estrategia_final,
            score=score,
            ab_result=ab_result
        )

        # RESULTADO FINAL
        estrategia_final["score_avaliacao"] = score
        estrategia_final["status"] = "APPROVED_BY_ORCHESTRATOR"

        print("✅ Estratégia aprovada.")

        return {
            "status": "APPROVED",
            "strategy": estrategia_final,
            "score": score,
            "ab_result": ab_result,
            "memory_context": self.memory.get_context()
        }

    # DECISION LOGIC
    def _decidir_num_variacoes(self) -> int:
        """
        Decide se gera 1 ou 2+ estratégias com base na memória.
        """

        context = self.memory.get_context()

        if context["long_term"]["historical_confidence_avg"] >= 0.8:
            return 1  # Confiança alta → execução direta

        return 2  # Exploração controlada

    def _bloqueio(self, reason: str, **extras) -> dict:
        """
        Retorno padrão de bloqueio.
        """

        print(f"🚫 Pipeline bloqueado: {reason}")

        return {
            "status": "BLOCKED",
            "reason": reason,
            **extras
        }
