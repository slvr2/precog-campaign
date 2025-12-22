from collections import deque

class ShortTermMemory:
    """
    Memória volátil da execução atual.
    """

    def __init__(self, max_size=10):
        self.recent_strategies = deque(maxlen=max_size)
        self.recent_scores = deque(maxlen=max_size)
        self.recent_ab_results = deque(maxlen=max_size)

    def record_strategy(self, strategy, score):
        self.recent_strategies.append(strategy)
        self.recent_scores.append(score)

    def record_ab_result(self, ab_result):
        self.recent_ab_results.append(ab_result)

    def get_context(self):
        return {
            "recent_avg_score": (
                sum(s["confidence_score"] for s in self.recent_scores) / len(self.recent_scores)
                if self.recent_scores else None
            ),
            "recent_failures": [
                s for s in self.recent_scores if s["confidence_score"] < 0.6
            ]
        }
