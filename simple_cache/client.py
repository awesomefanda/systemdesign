# client.py
import requests
from hash_ring import HashRing

class DistributedCacheClient:
    def __init__(self, nodes, replicas=2, vnodes=100, timeout=1.0):
        """
        nodes: list of base URLs e.g. ["http://127.0.0.1:5000", ...]
        replicas: how many nodes should hold each key
        """
        self.nodes = nodes
        self.replicas = replicas
        self.ring = HashRing(nodes, vnodes=vnodes)
        self.timeout = timeout

    def set(self, key, value, ttl=None):
        targets = self.ring.get_nodes(key, self.replicas)
        acks = 0
        for node in targets:
            try:
                resp = requests.post(f"{node}/store",
                                     json={"key": key, "value": value, "ttl": ttl},
                                     timeout=self.timeout)
                if resp.status_code == 200:
                    acks += 1
            except Exception as e:
                print(f"[set] node {node} error: {e}")
        # simple majority check
        return acks >= (len(targets) // 2) + 1

    def get(self, key):
        # try each replica until one returns a value
        targets = self.ring.get_nodes(key, self.replicas)
        for node in targets:
            try:
                resp = requests.get(f"{node}/get", params={"key": key}, timeout=self.timeout)
                if resp.status_code == 200:
                    return resp.json().get("value")
            except Exception as e:
                print(f"[get] node {node} error: {e}")
        return None
