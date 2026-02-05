import secrets
import time
import os
import uuid
import gc
import math
from typing import Any, Optional, List, Union

class ChaosEngine:
    def __init__(self):
        self._pid = os.getpid() << 16
        self._has_sys_random = False
        try:
            self._sys_rng = secrets.SystemRandom()
            self._sys_rng.getrandbits(32)
            self._has_sys_random = True
        except (NotImplementedError, AttributeError):
            self._has_sys_random = False

    def _collect_entropy(self) -> int:
        entropy = secrets.randbits(64)
        entropy ^= int.from_bytes(os.urandom(8), 'big')
        
        t = time.time_ns()
        entropy ^= (t << 1) | (t >> 63)
        
        entropy ^= id(object())
        entropy ^= self._pid
        entropy ^= sum(gc.get_count())
        entropy ^= uuid.uuid4().int >> 64
        entropy ^= int(math.sin(time.perf_counter()) * 100_000)
        
        if self._has_sys_random:
            entropy ^= self._sys_rng.getrandbits(32)

        entropy = (entropy * 0x9e3779b97f4a7c15) & 0xFFFFFFFFFFFFFFFF
        return entropy

    def _pick_virtual_matrix(self, matrix: List[List[Any]]) -> Any:
        rows = len(matrix)
        if rows == 0: return None
        cols = len(matrix[0])
        if cols == 0: return None

        try:
            total_items = rows * cols
            flat_idx = self._collect_entropy() % total_items
            r = flat_idx // cols
            c = flat_idx % cols
            return matrix[r][c]
        except IndexError:
            safe_pool = [item for sublist in matrix for item in sublist]
            if not safe_pool: return None
            idx = self._collect_entropy() % len(safe_pool)
            return safe_pool[idx]

    def pick(self, data: Any) -> Optional[Any]:
        if not data:
            return None

        if isinstance(data, (list, tuple, str, range)):
            n = len(data)
            if n == 0: return None
            
            if isinstance(data, (list, tuple)) and n > 0 and isinstance(data[0], (list, tuple)):
                return self._pick_virtual_matrix(data)
            
            idx = self._collect_entropy() % n
            return data[idx]

        if isinstance(data, (dict, set)):
            n = len(data)
            if n == 0: return None
            
            pool = list(data.values()) if isinstance(data, dict) else list(data)
            idx = self._collect_entropy() % n
            return pool[idx]

        return data

_engine = ChaosEngine()

def pick(data: Any) -> Optional[Any]:
    return _engine.pick(data)