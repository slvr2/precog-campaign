from modules.memory_agent.short_term import ShortTermMemory
from modules.memory_agent.long_term import LongTermMemory

class MemoryAgent:
    """
    Coordena memória curta e longa.
    """

    def __init__(self):
        self._executions = []

    def record_execution(self, strategy, score, ab_result):
        self._executions.append({
            "score": score["confidence_score"],
            "approved": score["confidence_score"] >= 0.6
        })

    def get_context(self) -> dict:
        if not self._executions:
            return {
                "historical_confidence_avg": 0.6,
                "total_executions": 0,
                "approved_rate": 0.0,
                "mode": "cold_start"
            }

        scores = [e["score"] for e in self._executions]
        approvals = [e["approved"] for e in self._executions]

        avg_score = sum(scores) / len(scores)
        approval_rate = sum(approvals) / len(approvals)

        return {
            "historical_confidence_avg": round(avg_score, 2),
            "total_executions": len(scores),
            "approved_rate": round(approval_rate, 2),
            "mode": "stable" if len(scores) >= 5 else "learning"
        }