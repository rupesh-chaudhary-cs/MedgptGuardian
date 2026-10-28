# import os
# from neo4j import GraphDatabase
# from dotenv import load_dotenv

# load_dotenv("backend/.env")

# URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
# USER = os.getenv("NEO4J_USER", "neo4j")
# PASSWORD = os.getenv("NEO4J_PASSWORD", "password") # Ensure this matches your DB password

# def run_massive_ingestion():
#     driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
#     # Point to the exact folder where you saved the 5 CSVs
#     base_path = f"file:///{os.path.abspath('backend/data/kg/')}/"
    
#     queries = [
#         "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Drug) REQUIRE d.name IS UNIQUE",
        
#         f"""LOAD CSV WITH HEADERS FROM '{base_path}dim1_disease.csv' AS row
#         CALL {{ WITH row MERGE (med:Drug {{name: row.Drug}}) MERGE (dis:Disease {{name: row.Disease}})
#         MERGE (med)-[:CONTRAINDICATED_BY {{severity: row.Severity, reason: row.Reason}}]->(dis) }} IN TRANSACTIONS OF 10000 ROWS;""",
        
#         f"""LOAD CSV WITH HEADERS FROM '{base_path}dim2_drug.csv' AS row
#         CALL {{ WITH row MERGE (m1:Drug {{name: row.Drug1}}) MERGE (m2:Drug {{name: row.Drug2}})
#         MERGE (m1)-[:INTERACTS_WITH {{severity: row.Severity, mechanism: row.Mechanism}}]->(m2) }} IN TRANSACTIONS OF 10000 ROWS;""",
        
#         f"""LOAD CSV WITH HEADERS FROM '{base_path}dim3_allergy.csv' AS row
#         CALL {{ WITH row MERGE (med:Drug {{name: row.Drug}}) MERGE (alg:Allergy {{name: row.Allergy}})
#         MERGE (med)-[:TRIGGERS_ALLERGY {{severity: row.Severity, reason: row.Reason}}]->(alg) }} IN TRANSACTIONS OF 10000 ROWS;""",
        
#         f"""LOAD CSV WITH HEADERS FROM '{base_path}dim4_factor.csv' AS row
#         CALL {{ WITH row MERGE (med:Drug {{name: row.Drug}}) MERGE (fac:PatientFactor {{name: row.Factor}})
#         MERGE (med)-[:UNSAFE_FOR {{severity: row.Severity, reason: row.Reason}}]->(fac) }} IN TRANSACTIONS OF 10000 ROWS;""",
        
#         f"""LOAD CSV WITH HEADERS FROM '{base_path}dim5_lab.csv' AS row
#         CALL {{ WITH row MERGE (med:Drug {{name: row.Drug}}) MERGE (lab:LabValue {{name: row.Lab}})
#         MERGE (med)-[:WORSENED_BY_LAB {{severity: row.Severity, reason: row.Reason}}]->(lab) }} IN TRANSACTIONS OF 10000 ROWS;"""
#     ]

#     with driver.session() as session:
#         for query in queries:
#             session.run(query)
#             print("Batch execution successful.")
#     driver.close()

# if __name__ == "__main__":
#     run_massive_ingestion()

# 


# import os
# from neo4j import GraphDatabase

# # Put your actual password here (e.g., "Medgpt123")
# URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
# USER = os.getenv("NEO4J_USER", "neo4j")
# PASSWORD = "rupesh@2222" 

# def run_massive_ingestion():
#     driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
#     base_path = f"file:///{os.path.abspath('app/data/kg').replace(os.sep, '/')}/"
    
#     # Pure Cypher - guaranteed to run on every Neo4j version
#     # The toLower() function is preserved here to ensure typography and case-mismatch immunity
#     queries = [
#         "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Drug) REQUIRE d.name IS UNIQUE",
#         "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Disease) REQUIRE d.name IS UNIQUE",
#         "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Allergy) REQUIRE a.name IS UNIQUE",
#         "CREATE CONSTRAINT IF NOT EXISTS FOR (f:PatientFactor) REQUIRE f.name IS UNIQUE",
#         "CREATE CONSTRAINT IF NOT EXISTS FOR (l:LabValue) REQUIRE l.name IS UNIQUE",
        
#         f"""LOAD CSV WITH HEADERS FROM '{base_path}dim1_disease.csv' AS row
#         MERGE (med:Drug {{name: toLower(row.Drug)}})
#         MERGE (dis:Disease {{name: toLower(row.Disease)}})
#         MERGE (med)-[:CONTRAINDICATED_BY {{severity: row.Severity, reason: row.Reason}}]->(dis)""",
        
#         f"""LOAD CSV WITH HEADERS FROM '{base_path}dim2_drug.csv' AS row
#         MERGE (m1:Drug {{name: toLower(row.Drug1)}})
#         MERGE (m2:Drug {{name: toLower(row.Drug2)}})
#         MERGE (m1)-[:INTERACTS_WITH {{severity: row.Severity, mechanism: row.Mechanism}}]->(m2)""",
        
#         f"""LOAD CSV WITH HEADERS FROM '{base_path}dim3_allergy.csv' AS row
#         MERGE (med:Drug {{name: toLower(row.Drug)}})
#         MERGE (alg:Allergy {{name: toLower(row.Allergy)}})
#         MERGE (med)-[:TRIGGERS_ALLERGY {{severity: row.Severity, reason: row.Reason}}]->(alg)""",
        
#         f"""LOAD CSV WITH HEADERS FROM '{base_path}dim4_factor.csv' AS row
#         MERGE (med:Drug {{name: toLower(row.Drug)}})
#         MERGE (fac:PatientFactor {{name: row.Factor}})
#         MERGE (med)-[:UNSAFE_FOR {{severity: row.Severity, reason: row.Reason}}]->(fac)""",
        
#         f"""LOAD CSV WITH HEADERS FROM '{base_path}dim5_lab.csv' AS row
#         MERGE (med:Drug {{name: toLower(row.Drug)}})
#         MERGE (lab:LabValue {{name: row.Lab}})
#         MERGE (med)-[:WORSENED_BY_LAB {{severity: row.Severity, reason: row.Reason}}]->(lab)"""
#     ]

#     print(f"🚀 Starting pure Cypher Neo4j Ingestion from {base_path}...")
#     with driver.session() as session:
#         for i, query in enumerate(queries):
#             try:
#                 session.run(query)
#                 print(f"✅ Executed query {i+1}/{len(queries)} successfully.")
#             except Exception as e:
#                 print(f"❌ Error on query {i+1}: {e}")
#     driver.close()
#     print("🎉 Database fully armed!")

# if __name__ == "__main__":
#     run_massive_ingestion()


"""
backend/scripts/enterprise_seed_5D.py (v2) - Load the dimension CSVs into Neo4j with the Python driver.
 
Run from the backend folder:
  python scripts/enterprise_seed_5D.py --wipe     # FIRST TIME: deletes the old (wrong) graph, then loads
  python scripts/enterprise_seed_5D.py            # later runs: adds/updates only (safe to repeat)
 
The password is read from backend/.env (NEO4J_URI, NEO4J_USERNAME or NEO4J_USER, NEO4J_PASSWORD, optional
NEO4J_DATABASE). Never write the password inside this file.
 
Files read from app/data/kg (missing or empty files are skipped):
  dim1_disease.csv                  Drug, Disease, Severity, Reason, Source    -> CONTRAINDICATED_BY
  dim1b_disease_from_labels.csv     same columns (from FDA labels)             -> CONTRAINDICATED_BY
  dim6_indication.csv               Drug, Disease, Relation                    -> INDICATED_FOR / OFF_LABEL_FOR
  dim2_drug.csv                     Drug1, Drug2, Severity, Mechanism          -> INTERACTS_WITH   (PrimeKG, no severity)
  dim2b_drug_ddinter.csv            same columns (DDInter, with severity)      -> INTERACTS_WITH   (overwrites severity)
  dim3_allergy.csv / dim4_factor.csv / dim5_lab.csv   (from FDA labels)        -> TRIGGERS_ALLERGY / UNSAFE_FOR / WORSENED_BY_LAB
"""
import os
import sys
from pathlib import Path
 
import pandas as pd
from dotenv import find_dotenv, load_dotenv
from neo4j import GraphDatabase
 
for env_file in (".env", "backend/.env", "../.env"):
    if Path(env_file).exists():
        load_dotenv(env_file)
        break
else:
    load_dotenv(find_dotenv(usecwd=True))
 
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE") or None
BATCH = 5000
 
# file, label A, label B, relationship (None = taken from the Relation column), columns, symmetric pair?
DIMS = [
    ("dim1_disease.csv", "Drug", "Disease", "CONTRAINDICATED_BY", ("Drug", "Disease", "Severity", "Reason"), False),
    ("dim1b_disease_from_labels.csv", "Drug", "Disease", "CONTRAINDICATED_BY", ("Drug", "Disease", "Severity", "Reason"), False),
    ("dim6_indication.csv", "Drug", "Disease", None, ("Drug", "Disease", "Relation", None), False),
    ("dim2_drug.csv", "Drug", "Drug", "INTERACTS_WITH", ("Drug1", "Drug2", "Severity", "Mechanism"), True),
    ("dim2b_drug_ddinter.csv", "Drug", "Drug", "INTERACTS_WITH", ("Drug1", "Drug2", "Severity", "Mechanism"), True),
    ("dim3_allergy.csv", "Drug", "Allergy", "TRIGGERS_ALLERGY", ("Drug", "Allergy", "Severity", "Reason"), False),
    ("dim4_factor.csv", "Drug", "PatientFactor", "UNSAFE_FOR", ("Drug", "Factor", "Severity", "Reason"), False),
    ("dim5_lab.csv", "Drug", "LabValue", "WORSENED_BY_LAB", ("Drug", "Lab", "Severity", "Reason"), False),
]
REL_MAP = {"indication": "INDICATED_FOR", "off-label use": "OFF_LABEL_FOR"}
LABELS = ["Drug", "Disease", "Allergy", "PatientFactor", "LabValue"]
 
 
def find_kg_dir() -> Path:
    here = Path(__file__).resolve()
    for c in (Path("app/data/kg"), Path("backend/app/data/kg"), here.parents[1] / "app" / "data" / "kg"):
        if c.is_dir():
            return c
    skip = {"venv", ".venv", "node_modules", ".git", "__pycache__"}
    for p in Path(".").rglob("dim1_disease.csv"):
        if not (set(p.parts) & skip):
            return p.parent
    sys.exit("Could not find the folder with dim1_disease.csv. Run this script from the backend folder.")
 
 
def read_rows(path: Path, cols, symmetric: bool):
    if not path.exists() or path.stat().st_size == 0:
        return None
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        return None
    lower = {c.strip().lower(): c for c in df.columns}
    for need in cols[:2]:
        if need.lower() not in lower:
            sys.exit(f"{path.name}: missing column '{need}'. Headers found: {list(df.columns)}")
    ca, cb = lower[cols[0].lower()], lower[cols[1].lower()]
    by_relation = cols[3] is None
    c3 = lower.get(cols[2].lower())
    c4 = lower.get(cols[3].lower()) if cols[3] else None
    rows, seen = [], set()
    for _, r in df.iterrows():
        a, b = str(r[ca]).strip(), str(r[cb]).strip()
        if not a or not b:
            continue
        a_lc, b_lc = a.lower(), b.lower()
        if symmetric and a_lc > b_lc:
            a, b, a_lc, b_lc = b, a, b_lc, a_lc
        rel_name = str(r[c3]).strip().lower() if (by_relation and c3) else ""
        key = (a_lc, b_lc, rel_name)
        if key in seen:
            continue
        seen.add(key)
        rows.append({"a": a, "a_lc": a_lc, "b": b, "b_lc": b_lc,
                     "severity": "" if by_relation else (str(r[c3]).strip() if c3 else ""),
                     "reason": str(r[c4]).strip() if c4 else "",
                     "rel": rel_name, "source": path.name})
    return rows
 
 
def wipe(session):
    print("Deleting relationships ...")
    session.run("MATCH ()-[r]->() CALL { WITH r DELETE r } IN TRANSACTIONS OF 50000 ROWS")
    print("Deleting nodes ...")
    session.run("MATCH (n) CALL { WITH n DETACH DELETE n } IN TRANSACTIONS OF 10000 ROWS")
 
 
def push(session, rows, la, lb, rel):
    session.run(
        f"""
        UNWIND $rows AS r
        MERGE (a:{la} {{name_lc: r.a_lc}}) ON CREATE SET a.name = r.a
        MERGE (b:{lb} {{name_lc: r.b_lc}}) ON CREATE SET b.name = r.b
        MERGE (a)-[x:{rel}]->(b)
        SET x.severity = r.severity, x.reason = r.reason, x.source = r.source
        """, rows=rows)
 
 
def main():
    if not PASSWORD:
        sys.exit("NEO4J_PASSWORD is not set. Put it in backend/.env (never inside the script).")
    kg_dir = find_kg_dir()
    print("Reading CSVs from:", kg_dir.resolve())
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    driver.verify_connectivity()
 
    with driver.session(database=DATABASE) as session:
        existing = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        if "--wipe" in sys.argv:
            if "--yes" not in sys.argv:
                if input(f"This DELETES all {existing:,} nodes and their relationships. Type DELETE ALL to continue: ").strip() != "DELETE ALL":
                    sys.exit("Cancelled.")
            wipe(session)
        elif existing and "--allow-existing" not in sys.argv:
            sys.exit(f"The database already contains {existing:,} nodes (probably the old, wrong data). "
                     "Run with --wipe to start clean, or --allow-existing to add to what is there.")
 
        for label in LABELS:
            session.run(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.name_lc IS UNIQUE")
 
        for fname, la, lb, rel, cols, symmetric in DIMS:
            rows = read_rows(kg_dir / fname, cols, symmetric)
            if rows is None:
                print(f"- {fname}: missing or empty, skipped")
                continue
            groups = {}
            if rel is None:
                for r in rows:
                    if r["rel"] in REL_MAP:
                        groups.setdefault(REL_MAP[r["rel"]], []).append(r)
            else:
                groups[rel] = rows
            for rel_type, grp in groups.items():
                for i in range(0, len(grp), BATCH):
                    push(session, grp[i:i + BATCH], la, lb, rel_type)
                    print(f"  {fname} -> {rel_type}: {min(i + BATCH, len(grp)):,}/{len(grp):,}", end="\r")
                print(f"- {fname}: {len(grp):,} {rel_type} relationships loaded        ")
 
        nodes = session.run("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS c ORDER BY c DESC").data()
        rels = session.run("MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS c ORDER BY c DESC").data()
    driver.close()
    print("\nNodes:", {r["label"]: r["c"] for r in nodes})
    print("Relationships:", {r["type"]: r["c"] for r in rels})
 
 
if __name__ == "__main__":
    main()
 