import time
from typing import Dict, Any

class MetricsTracker:
    def __init__(self):
        self.words_generated: int = 0
        self.unblock_sessions: int = 0
        self.branches_applied: int = 0
        self.premises_created: int = 0
        self.characters_created: int = 0
        self.start_time: float = time.time()

    def record_words(self, count: int) -> None:
        self.words_generated += max(0, count)

    def record_unblock(self) -> None:
        self.unblock_sessions += 1

    def record_branch_applied(self) -> None:
        self.branches_applied += 1

    def record_premise(self) -> None:
        self.premises_created += 1

    def record_character(self) -> None:
        self.characters_created += 1

    def get_summary(self) -> Dict[str, Any]:
        elapsed_mins = max((time.time() - self.start_time) / 60.0, 0.1)
        velocity_wpm = round(self.words_generated / elapsed_mins, 1)
        # Calculate velocity acceleration factor
        speedup_multiplier = round(1.0 + (self.unblock_sessions * 0.5) + (self.branches_applied * 0.4) + (self.premises_created * 0.2), 1)
        
        return {
            "words_generated": self.words_generated,
            "unblock_sessions": self.unblock_sessions,
            "branches_applied": self.branches_applied,
            "premises_created": self.premises_created,
            "characters_created": self.characters_created,
            "elapsed_minutes": round(elapsed_mins, 1),
            "current_wpm": velocity_wpm,
            "estimated_speedup": f"{speedup_multiplier}x"
        }

    def reset(self) -> None:
        self.words_generated = 0
        self.unblock_sessions = 0
        self.branches_applied = 0
        self.premises_created = 0
        self.characters_created = 0
        self.start_time = time.time()
