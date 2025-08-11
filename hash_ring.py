# hash_ring.py
import hashlib, bisect

class HashRing:
    def __init__(self, nodes, vnodes=100):
        """
        nodes: list of node addresses (e.g. ["http://127.0.0.1:5000", ...])
        vnodes: number of virtual nodes per real node (smoothes distribution)
        """
        self.vnodes = vnodes
        self.ring = {}           # map hash -> node
        self._sorted_keys = []   # sorted list of hashes
        for node in nodes:
            for i in range(vnodes):
                token = f"{node}#{i}"
                h = self._hash(token)
                self.ring[h] = node
                self._sorted_keys.append(h)
        self._sorted_keys.sort()

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def get_node(self, key: str) -> str:
        if not self._sorted_keys:
            return None
        h = self._hash(key)
        idx = bisect.bisect(self._sorted_keys, h)
        if idx == len(self._sorted_keys):
            idx = 0
        return self.ring[self._sorted_keys[idx]]

    def get_nodes(self, key: str, count: int):
        """Return `count` distinct nodes for replication (clockwise on ring)."""
        nodes = []
        if not self._sorted_keys:
            return nodes
        h = self._hash(key)
        idx = bisect.bisect(self._sorted_keys, h)
        i = idx
        seen = set()
        while len(nodes) < count:
            if i == len(self._sorted_keys):
                i = 0
            node = self.ring[self._sorted_keys[i]]
            if node not in seen:
                nodes.append(node)
                seen.add(node)
            i += 1
        return nodes
