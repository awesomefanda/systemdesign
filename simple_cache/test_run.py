from client import DistributedCacheClient
nodes = ["http://127.0.0.1:5000","http://127.0.0.1:5001","http://127.0.0.1:5002"]
c = DistributedCacheClient(nodes, replicas=2)

# Set and get
ok = c.set("foo", "bar", ttl=10)
print("set ok:", ok)
print("get foo:", c.get("foo"))

# Try multiple keys to see distribution
for k in ["a","b","c","d","e","f","g"]:
    c.set(k, f"val-{k}")
print("done")
