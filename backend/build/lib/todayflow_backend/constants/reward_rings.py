"""
Канонические id колец прогресса (мерч, API, клиент).
Пороги по evolution_index совпадают с EVOLUTION_TIERS / фронтом.
"""

from typing import List, Tuple

# (min_evolution_index_inclusive, ring_id)
REWARD_RING_THRESHOLDS: Tuple[Tuple[int, str], ...] = (
    (0, "ring_seeker"),
    (38, "ring_initiate"),
    (50, "ring_observer"),
    (62, "ring_alchemist"),
    (70, "ring_oracle"),
    (78, "ring_architect"),
    (85, "ring_sage"),
)


def compute_reward_rings_earned(evolution_index: int) -> List[str]:
    safe = max(0, min(100, int(round(evolution_index))))
    return [ring_id for min_idx, ring_id in REWARD_RING_THRESHOLDS if safe >= min_idx]
