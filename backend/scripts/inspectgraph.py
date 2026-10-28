"""
scripts/inspect_graph.py - See exactly what is inside your Neo4j database (run from the project root).
 
  python scripts/inspect_graph.py
  python scripts/inspect_graph.py propranolol asthma      # also look up specific names
 
Prints node labels, relationship types with counts, and for each name you pass: whether it exists and which
relationship types it has. Paste the output to me if something is missing or unexpected.
"""
import os
import sys
from pathlib import Path
 
from dotenv import load_dotenv
from neo4j import GraphDatabase
 
for env_file in (".env", "backend/.env"):
    if Path(env_file).exists():
        load_dotenv(env_file)
        break
 
driver = GraphDatabase.driver(os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                              auth=(os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD")))
with driver.session() as s:
    print("NODE LABELS")
    for r in s.run("MATCH (n) RETURN labels(n) AS l, count(*) AS c ORDER BY c DESC").data():
        print(f"  {str(r['l']):40s} {r['c']:>10,}")
    print("\nRELATIONSHIP TYPES")
    for r in s.run("MATCH ()-[r]->() RETURN type(r) AS t, count(*) AS c ORDER BY c DESC").data():
        print(f"  {r['t']:40s} {r['c']:>10,}")
    print("\nSAMPLE PROPERTIES")
    for r in s.run("MATCH (n:Drug) RETURN properties(n) AS p LIMIT 2").data():
        print("  Drug:", r["p"])
    for r in s.run("MATCH ()-[x]->() WITH x LIMIT 3 RETURN type(x) AS t, properties(x) AS p").data():
        print("  rel:", r["t"], r["p"])
    for name in sys.argv[1:]:
        print(f"\nLOOKUP '{name}'")
        rows = s.run("""MATCH (n) WHERE toLower(n.name) CONTAINS toLower($n)
                        OPTIONAL MATCH (n)-[r]-()
                        RETURN labels(n)[0] AS label, n.name AS name, type(r) AS rel, count(r) AS c
                        ORDER BY size(n.name), c DESC LIMIT 25""", n=name).data()
        if not rows:
            print("  not found")
        for r in rows:
            print(f"  {r['label']:14s} {str(r['name'])[:45]:45s} {str(r['rel']):26s} {r['c']}")
driver.close()
 