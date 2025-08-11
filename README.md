How to run this locally (step-by-step)
Create a virtualenv and install:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate    # or venv\Scripts\activate on Windows
pip install flask requests
Save hash_ring.py, node.py, client.py in one directory.

Start 3 nodes in separate terminals (or background jobs) with the same node list logic (we pass same list to client; nodes themselves do not need to know the whole cluster in this simplified design):
Terminal A:

css
Copy
Edit
python node.py --port 5000
Terminal B:

css
Copy
Edit
python node.py --port 5001
Terminal C:

css
Copy
Edit
python node.py --port 5002
In a new Python shell (or a script test_run.py) run:

python
Copy
Edit
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
Experiment:

Kill one node (Ctrl+C in its terminal). Try c.get("foo") — client will query the replica nodes and still return value if replication present (assuming write succeeded to other replica).

Start node again — keys will not automatically move back (consistent hashing will change mapping). This is a learning exercise to see behavior — production systems re-balance or use background replication to re-populate.

