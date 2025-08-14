How to run this locally (step-by-step)
Create a virtualenv and install:

```python -m venv venv
source venv/bin/activate    # or venv\Scripts\activate on Windows
pip install flask requests
```
Save hash_ring.py, node.py, client.py in one directory.

Start 3 nodes in separate terminals (or background jobs) with the same node list logic (we pass same list to client; nodes themselves do not need to know the whole cluster in this simplified design):
Terminal A:
python node.py --port 5000

Terminal B:
python node.py --port 5001

Terminal C:
python node.py --port 5002
In a new Python shell run  test_run.py:


Experiment:

Kill one node (Ctrl+C in its terminal). Try c.get("foo") — client will query the replica nodes and still return value if replication present (assuming write succeeded to other replica).

Start node again — keys will not automatically move back (consistent hashing will change mapping). This is a learning exercise to see behavior — production systems re-balance or use background replication to re-populate.

