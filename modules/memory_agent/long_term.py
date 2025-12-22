import json
import os
from collections import Counter

MEMORY_FILE = "memory_long_term.json"

class LongTermMemory:

    def __init__(self):
        if not os.path.exists(MEMORY_FILE):
            self.data = {
                "platform_success": Counter(),
                "creative_success": Counter(),
                "interest_success": Counter()
            }
            self._persist()
        else:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                self.data = {
                    k: Counter(v) for k, v in raw.items()
                }

    def record_success(self, strategy):
        self.data["platform_success"][strategy["plataforma"]] += 1
        self.data["creative_success"][strategy["criativo_tipo"]] += 1

        for interest in strategy.get("icp_interesses", []):
            self.data["interest_success"][interest] += 1

        self._persist()

    def get_insights(self):
        return {
            "top_platforms": self.data["platform_success"].most_common(3),
            "top_creatives": self.data["creative_success"].most_common(3),
            "top_interests": self.data["interest_success"].most_common(5),
        }

    def _persist(self):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {k: dict(v) for k, v in self.data.items()},
                f,
                indent=4,
                ensure_ascii=False
            )
