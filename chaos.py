import secrets
import time
import os
import uuid
import gc
import math
from typing import Any, Optional, List, Sequence, Union

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

    def shuffle(self, x: List[Any]) -> None:
        for i in range(len(x) - 1, 0, -1):
            j = self._collect_entropy() % (i + 1)
            x[i], x[j] = x[j], x[i]

    def randint(self, a: int, b: int) -> int:
        return a + (self._collect_entropy() % (b - a + 1))

    def coin(self) -> bool:
        return (self._collect_entropy() & 1) == 1

    def sample(self, population: Sequence[Any], k: int) -> List[Any]:
        n = len(population)
        if not 0 <= k <= n:
            raise ValueError("Sample larger than population")
        
        pool = list(population)
        for i in range(k):
            j = (self._collect_entropy() % (n - i)) + i
            pool[i], pool[j] = pool[j], pool[i]
        
        return pool[:k]

    def token_hex(self, nbytes: int = 32) -> str:
        res = bytearray()
        for _ in range(nbytes):
            res.append(self._collect_entropy() & 0xFF)
        return res.hex()

_engine = ChaosEngine()

def pick(data: Any) -> Optional[Any]:
    return _engine.pick(data)

def shuffle(x: List[Any]) -> None:
    _engine.shuffle(x)

def randint(a: int, b: int) -> int:
    return _engine.randint(a, b)

def coin() -> bool:
    return _engine.coin()

def sample(population: Sequence[Any], k: int) -> List[Any]:
    return _engine.sample(population, k)

def token_hex(nbytes: int = 32) -> str:
    return _engine.token_hex(nbytes)
