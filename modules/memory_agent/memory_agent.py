from modules.memory_agent.short_term import ShortTermMemory
from modules.memory_agent.long_term import LongTermMemory

class MemoryAgent:
    """
    Coordena memória curta e longa.
    """

    def __init__(self):
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory()

    def record_execution(self, strategy, score, ab_result=None):
        self.stm.record_strategy(strategy, score)

        if ab_result:
            self.stm.record_ab_result(ab_result)

        # Só aprende no longo prazo se passou no score
        if score["confidence_score"] >= 0.7:
            self.ltm.record_success(strategy)

    def get_context(self):
        return {
            "short_term": self.stm.get_context(),
            "long_term": self.ltm.get_insights()
        }
