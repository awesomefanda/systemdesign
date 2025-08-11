# node.py
from flask import Flask, request, jsonify
from collections import OrderedDict
import threading, time, argparse

class LRUCache:
    def __init__(self, capacity=1000):
        self.capacity = capacity
        self.data = OrderedDict()  # key -> (value, expiry_ts_or_None)
        self.lock = threading.Lock()

    def _purge_expired(self):
        now = time.time()
        to_remove = []
        for k, (v, exp) in list(self.data.items()):
            if exp is not None and exp <= now:
                to_remove.append(k)
        for k in to_remove:
            self.data.pop(k, None)

    def get(self, key):
        with self.lock:
            if key not in self.data:
                return None
            value, exp = self.data.pop(key)
            if exp is not None and exp <= time.time():
                return None
            # move to end (most recently used)
            self.data[key] = (value, exp)
            return value

    def set(self, key, value, ttl=None):
        with self.lock:
            if key in self.data:
                self.data.pop(key)
            expiry = time.time() + ttl if ttl else None
            self.data[key] = (value, expiry)
            if len(self.data) > self.capacity:
                self.data.popitem(last=False)  # pop least recently used

    def delete(self, key):
        with self.lock:
            self.data.pop(key, None)

app = Flask(__name__)
cache = LRUCache(capacity=1000)

@app.route("/store", methods=["POST"])
def store():
    payload = request.get_json(force=True)
    key = payload.get("key")
    value = payload.get("value")
    ttl = payload.get("ttl", None)
    if key is None or value is None:
        return jsonify({"error": "key and value required"}), 400
    cache.set(key, value, ttl)
    return jsonify({"status": "ok"}), 200

@app.route("/get")
def get_value():
    key = request.args.get("key")
    if not key:
        return jsonify({"error": "missing key"}), 400
    val = cache.get(key)
    if val is None:
        return jsonify({"found": False}), 404
    return jsonify({"found": True, "value": val}), 200

@app.route("/delete", methods=["POST"])
def delete():
    payload = request.get_json(force=True)
    key = payload.get("key")
    cache.delete(key)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--capacity", type=int, default=1000)
    args = parser.parse_args()
    cache = LRUCache(capacity=args.capacity)
    # Run Flask app (dev server ok for local learning)
    app.run(host="127.0.0.1", port=args.port, threaded=True)
