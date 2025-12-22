from typing import List, Dict
from modules.score_agent import ScoreAgent


class ABAgent:
    """
    Compara estratégias usando exclusivamente lógica determinística
    e o ScoreAgent como juiz.
    """

    SCORE_MINIMO = 0.6
    DIFERENCA_MINIMA = 0.05  # margem para evitar falso vencedor

    @staticmethod
    def comparar(estrategias: List[Dict]) -> Dict:
        """
        Recebe uma lista de estratégias e retorna a melhor opção
        com base no confidence_score.
        """

        if len(estrategias) < 2:
            raise ValueError("ABAgent requer no mínimo 2 estratégias.")

        resultados = []

        # Avalia todas as estratégias
        for idx, estrategia in enumerate(estrategias):
            score = ScoreAgent.avaliar(estrategia)

            resultados.append({
                "index": idx,
                "estrategia": estrategia,
                "score": score,
                "confidence_score": score["confidence_score"]
            })

        # Ordena por score decrescente
        resultados.sort(
            key=lambda x: x["confidence_score"],
            reverse=True
        )

        melhor = resultados[0]
        segundo = resultados[1]

        # Caso: nenhuma estratégia aceitável
        if melhor["confidence_score"] < ABAgent.SCORE_MINIMO:
            return {
                "status": "NO_WINNER",
                "reason": "Nenhuma estratégia atingiu o score mínimo.",
                "resultados": resultados
            }

        # Caso: empate técnico
        if melhor["confidence_score"] - segundo["confidence_score"] < ABAgent.DIFERENCA_MINIMA:
            desempate = ABAgent._desempate(melhor, segundo)

            if desempate:
                return {
                    "status": "WINNER_BY_TIEBREAK",
                    "winner_index": desempate["index"],
                    "winner_score": desempate["confidence_score"],
                    "winner_strategy": desempate["estrategia"],
                    "tie_break_reason": "deterministic_secondary_criteria",
                    "resultados": resultados
                }

            return {
                "status": "TIE",
                "reason": "Empate real após critérios secundários.",
                "resultados": resultados
            }

        # Caso: vencedor claro
        return {
            "status": "WINNER",
            "winner_index": melhor["index"],
            "winner_score": melhor["confidence_score"],
            "winner_strategy": melhor["estrategia"],
            "comparativo": {
                "winner": melhor["confidence_score"],
                "runner_up": segundo["confidence_score"]
            },
            "resultados": resultados
        }

    def _desempate(a: dict, b: dict) -> dict:
        """
        Aplica critérios determinísticos de desempate.
        Retorna a melhor estratégia.
        """

        # Menor nível de risco
        risco_rank = {"low": 3, "medium": 2, "high": 1}
        if risco_rank[a["score"]["risk_level"]] != risco_rank[b["score"]["risk_level"]]:
            return a if risco_rank[a["score"]["risk_level"]] > risco_rank[b["score"]["risk_level"]] else b

        # Menos flags críticas
        if len(a["score"]["flags"]) != len(b["score"]["flags"]):
            return a if len(a["score"]["flags"]) < len(b["score"]["flags"]) else b

        # Estratégia mais simples (menos componentes)
        if len(a["estrategia"]) != len(b["estrategia"]):
            return a if len(a["estrategia"]) < len(b["estrategia"]) else b

        return None  # empate real