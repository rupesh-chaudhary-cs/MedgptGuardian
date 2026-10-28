# import os
# import logging
# from neo4j import GraphDatabase

# logger = logging.getLogger(__name__)

# class Neo4jMedicalGraph:
#     def __init__(self):
#         self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
#         self.user = os.getenv("NEO4J_USER", "neo4j")
#         self.password = os.getenv("NEO4J_PASSWORD", "password")
#         self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

#     def verify_clinical_safety(self, patient_diseases: list, patient_allergies: list, patient_factors: list, patient_labs: list, proposed_drugs: list) -> list:
#         if not self.driver or not proposed_drugs:
#             return []

#         red_flags = []
#         query = """
#         OPTIONAL MATCH (med1:Drug)-[r1:CONTRAINDICATED_BY]->(d:Disease) WHERE med1.name IN $drugs AND d.name IN $diseases
#         OPTIONAL MATCH (med2a:Drug)-[r2:INTERACTS_WITH]-(med2b:Drug) WHERE med2a.name IN $drugs AND med2b.name IN $drugs
#         OPTIONAL MATCH (med3:Drug)-[r3:TRIGGERS_ALLERGY]->(a:Allergy) WHERE med3.name IN $drugs AND a.name IN $allergies
#         OPTIONAL MATCH (med4:Drug)-[r4:UNSAFE_FOR]->(f:PatientFactor) WHERE med4.name IN $drugs AND f.name IN $factors
#         OPTIONAL MATCH (med5:Drug)-[r5:WORSENED_BY_LAB]->(l:LabValue) WHERE med5.name IN $drugs AND l.name IN $labs
        
#         RETURN 
#             med1.name AS D1, d.name AS Dis, r1.reason AS R1, r1.severity AS S1,
#             med2a.name AS D2a, med2b.name AS D2b, r2.mechanism AS R2, r2.severity AS S2,
#             med3.name AS D3, a.name AS Alg, r3.reason AS R3, r3.severity AS S3,
#             med4.name AS D4, f.name AS Fac, r4.reason AS R4, r4.severity AS S4,
#             med5.name AS D5, l.name AS Lab, r5.reason AS R5, r5.severity AS S5
#         """
        
#         with self.driver.session() as session:
#             result = session.run(query, drugs=proposed_drugs, diseases=patient_diseases, allergies=patient_allergies, factors=patient_factors, labs=patient_labs)
#             for record in result:
#                 if record['Dis']: red_flags.append(f"[{record['S1']}] DISEASE CONFLICT: {record['D1']} contraindicated for {record['Dis']} ({record['R1']})")
#                 if record['D2a'] and record['D2b'] and record['D2a'] != record['D2b']: red_flags.append(f"[{record['S2']}] DRUG INTERACTION: {record['D2a']} + {record['D2b']} ({record['R2']})")
#                 if record['Alg']: red_flags.append(f"[{record['S3']}] ALLERGY ALERT: {record['D3']} triggers {record['Alg']} ({record['R3']})")
#                 if record['Fac']: red_flags.append(f"[{record['S4']}] DEMOGRAPHIC RISK: {record['D4']} unsafe for {record['Fac']} ({record['R4']})")
#                 if record['Lab']: red_flags.append(f"[{record['S5']}] LAB/VITAL RISK: {record['D5']} dangerous with {record['Lab']} ({record['R5']})")
        
#         return list(set(red_flags))

# medical_graph = Neo4jMedicalGraph()

# import os
# import logging
# from neo4j import GraphDatabase

# logger = logging.getLogger(__name__)

# class Neo4jMedicalGraph:
#     def __init__(self):
#         self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
#         self.user = os.getenv("NEO4J_USER", "neo4j")
#         self.password = os.getenv("NEO4J_PASSWORD", "password")
#         self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

#     def verify_clinical_safety(self, patient_diseases: list, patient_allergies: list, patient_factors: list, patient_labs: list, proposed_drugs: list) -> list:
#         if not self.driver or not proposed_drugs:
#             return []

#         # 1. BULLETPROOF FIX: Lowercase all Python inputs before querying
#         drugs_lower = [str(d).lower().strip() for d in proposed_drugs]
#         diseases_lower = [str(d).lower().strip() for d in patient_diseases]
#         allergies_lower = [str(a).lower().strip() for a in patient_allergies]
#         factors_lower = [str(f).lower().strip() for f in patient_factors]
#         labs_lower = [str(l).lower().strip() for l in patient_labs]

#         red_flags = []
        
#         # 2. BULLETPROOF FIX: toLower() in Cypher and flexible relationship mapping
#         # Removing directional arrows -[r]- catches the relationship no matter which way it points.
#         query = """
#         OPTIONAL MATCH (med1:Drug)-[r1]-(d:Disease) 
#         WHERE toLower(med1.name) IN $drugs AND toLower(d.name) IN $diseases 
#           AND type(r1) CONTAINS 'CONTRAINDICATED'
          
#         OPTIONAL MATCH (med2a:Drug)-[r2:INTERACTS_WITH]-(med2b:Drug) 
#         WHERE toLower(med2a.name) IN $drugs AND toLower(med2b.name) IN $drugs
        
#         OPTIONAL MATCH (med3:Drug)-[r3:TRIGGERS_ALLERGY]-(a:Allergy) 
#         WHERE toLower(med3.name) IN $drugs AND toLower(a.name) IN $allergies
        
#         OPTIONAL MATCH (med4:Drug)-[r4:UNSAFE_FOR]-(f:PatientFactor) 
#         WHERE toLower(med4.name) IN $drugs AND toLower(f.name) IN $factors
        
#         OPTIONAL MATCH (med5:Drug)-[r5:WORSENED_BY_LAB]-(l:LabValue) 
#         WHERE toLower(med5.name) IN $drugs AND toLower(l.name) IN $labs
        
#         RETURN 
#             med1.name AS D1, d.name AS Dis, r1.reason AS R1, r1.severity AS S1,
#             med2a.name AS D2a, med2b.name AS D2b, r2.mechanism AS R2, r2.severity AS S2,
#             med3.name AS D3, a.name AS Alg, r3.reason AS R3, r3.severity AS S3,
#             med4.name AS D4, f.name AS Fac, r4.reason AS R4, r4.severity AS S4,
#             med5.name AS D5, l.name AS Lab, r5.reason AS R5, r5.severity AS S5
#         """
        
#         with self.driver.session() as session:
#             result = session.run(
#                 query, 
#                 drugs=drugs_lower, 
#                 diseases=diseases_lower, 
#                 allergies=allergies_lower, 
#                 factors=factors_lower, 
#                 labs=labs_lower
#             )
#             for record in result:
#                 if record['Dis']: red_flags.append(f"[{record['S1'] or 'HIGH'}] DISEASE CONFLICT: {record['D1']} contraindicated for {record['Dis']} ({record['R1'] or 'Risk of severe adverse event.'})")
#                 if record['D2a'] and record['D2b'] and record['D2a'] != record['D2b']: red_flags.append(f"[{record['S2'] or 'HIGH'}] DRUG INTERACTION: {record['D2a']} + {record['D2b']} ({record['R2'] or 'Adverse interaction detected.'})")
#                 if record['Alg']: red_flags.append(f"[{record['S3'] or 'HIGH'}] ALLERGY ALERT: {record['D3']} triggers {record['Alg']} ({record['R3']})")
#                 if record['Fac']: red_flags.append(f"[{record['S4'] or 'HIGH'}] DEMOGRAPHIC RISK: {record['D4']} unsafe for {record['Fac']} ({record['R4']})")
#                 if record['Lab']: red_flags.append(f"[{record['S5'] or 'HIGH'}] LAB/VITAL RISK: {record['D5']} dangerous with {record['Lab']} ({record['R5']})")
        
#         return list(set(red_flags))

# medical_graph = Neo4jMedicalGraph()

# import os
# import logging
# from neo4j import GraphDatabase

# logger = logging.getLogger(__name__)

# class Neo4jMedicalGraph:
#     def __init__(self):
#         self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
#         self.user = os.getenv("NEO4J_USER", "neo4j")
#         self.password = os.getenv("NEO4J_PASSWORD", "password")
#         self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

#     def verify_clinical_safety(self, patient_diseases: list, patient_allergies: list, patient_factors: list, patient_labs: list, proposed_drugs: list) -> list:
#         if not self.driver or not proposed_drugs:
#             return []

#         # 1. Strip whitespace and force lowercase on everything coming from the LLM
#         # This handles capitalization mismatches (e.g., "Propranolol" vs "propranolol")
#         drugs_lower = [str(d).lower().strip() for d in proposed_drugs if d]
#         diseases_lower = [str(d).lower().strip() for d in patient_diseases if d]
#         allergies_lower = [str(a).lower().strip() for a in patient_allergies if a]
#         factors_lower = [str(f).lower().strip() for f in patient_factors if f]
#         labs_lower = [str(l).lower().strip() for l in patient_labs if l]

#         red_flags = []
        
#         # 2. THE UNIVERSAL FUZZY-MATCHING CYPHER QUERY
#         # Instead of strict equality (IN), this uses dynamic sub-string scanning (CONTAINS).
#         # This automatically catches typos ("propanol" inside "propranolol") 
#         # and clinical variations ("asthma" inside "bronchial asthma").
#         query = """
#         OPTIONAL MATCH (med1:Drug)-[r1]-(d:Disease) 
#         WHERE any(drug IN $drugs WHERE toLower(med1.name) CONTAINS drug) 
#           AND any(dis IN $diseases WHERE toLower(d.name) CONTAINS dis)
#           AND type(r1) CONTAINS 'CONTRAINDICATED'
          
#         OPTIONAL MATCH (med2a:Drug)-[r2:INTERACTS_WITH]-(med2b:Drug) 
#         WHERE any(drugA IN $drugs WHERE toLower(med2a.name) CONTAINS drugA)
#           AND any(drugB IN $drugs WHERE toLower(med2b.name) CONTAINS drugB)
        
#         OPTIONAL MATCH (med3:Drug)-[r3:TRIGGERS_ALLERGY]-(a:Allergy) 
#         WHERE any(drug IN $drugs WHERE toLower(med3.name) CONTAINS drug)
#           AND any(alg IN $allergies WHERE toLower(a.name) CONTAINS alg)
        
#         OPTIONAL MATCH (med4:Drug)-[r4:UNSAFE_FOR]-(f:PatientFactor) 
#         WHERE any(drug IN $drugs WHERE toLower(med4.name) CONTAINS drug)
#           AND any(fac IN $factors WHERE toLower(f.name) CONTAINS fac)
        
#         OPTIONAL MATCH (med5:Drug)-[r5:WORSENED_BY_LAB]-(l:LabValue) 
#         WHERE any(drug IN $drugs WHERE toLower(med5.name) CONTAINS drug)
#           AND any(lab IN $labs WHERE toLower(l.name) CONTAINS lab)
        
#         RETURN 
#             med1.name AS D1, d.name AS Dis, r1.reason AS R1, r1.severity AS S1,
#             med2a.name AS D2a, med2b.name AS D2b, r2.mechanism AS R2, r2.severity AS S2,
#             med3.name AS D3, a.name AS Alg, r3.reason AS R3, r3.severity AS S3,
#             med4.name AS D4, f.name AS Fac, r4.reason AS R4, r4.severity AS S4,
#             med5.name AS D5, l.name AS Lab, r5.reason AS R5, r5.severity AS S5
#         """
        
#         with self.driver.session() as session:
#             result = session.run(
#                 query, 
#                 drugs=drugs_lower, 
#                 diseases=diseases_lower, 
#                 allergies=allergies_lower, 
#                 factors=factors_lower, 
#                 labs=labs_lower
#             )
#             for record in result:
#                 if record['Dis']: red_flags.append(f"[{record['S1'] or 'HIGH'}] DISEASE CONFLICT: {record['D1']} contraindicated for {record['Dis']} ({record['R1'] or 'Risk of severe adverse event.'})")
#                 if record['D2a'] and record['D2b'] and record['D2a'] != record['D2b']: red_flags.append(f"[{record['S2'] or 'HIGH'}] DRUG INTERACTION: {record['D2a']} + {record['D2b']} ({record['R2'] or 'Adverse interaction detected.'})")
#                 if record['Alg']: red_flags.append(f"[{record['S3'] or 'HIGH'}] ALLERGY ALERT: {record['D3']} triggers {record['Alg']} ({record['R3']})")
#                 if record['Fac']: red_flags.append(f"[{record['S4'] or 'HIGH'}] DEMOGRAPHIC RISK: {record['D4']} unsafe for {record['Fac']} ({record['R4']})")
#                 if record['Lab']: red_flags.append(f"[{record['S5'] or 'HIGH'}] LAB/VITAL RISK: {record['D5']} dangerous with {record['Lab']} ({record['R5']})")
        
#         return list(set(red_flags))

# medical_graph = Neo4jMedicalGraph()

# import os
# import logging
# from neo4j import GraphDatabase

# logger = logging.getLogger(__name__)

# class Neo4jMedicalGraph:
#     def __init__(self):
#         self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
#         self.user = os.getenv("NEO4J_USER", "neo4j")
#         self.password = os.getenv("NEO4J_PASSWORD", "password")
#         self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

#     def verify_clinical_safety(self, patient_diseases: list, patient_allergies: list, patient_factors: list, patient_labs: list, proposed_drugs: list) -> list:
#         if not self.driver or not proposed_drugs:
#             return []

#         # 1. Strip whitespace and force lowercase on everything coming from the LLM
#         # This handles capitalization mismatches (e.g., "Propranolol" vs "propranolol")
#         drugs_lower = [str(d).lower().strip() for d in proposed_drugs if d]
#         diseases_lower = [str(d).lower().strip() for d in patient_diseases if d]
#         allergies_lower = [str(a).lower().strip() for a in patient_allergies if a]
#         factors_lower = [str(f).lower().strip() for f in patient_factors if f]
#         labs_lower = [str(l).lower().strip() for l in patient_labs if l]

#         red_flags = []
        
#         # 2. THE UNIVERSAL FUZZY-MATCHING CYPHER QUERY
#         # Instead of strict equality (IN), this uses dynamic sub-string scanning (CONTAINS).
#         # This automatically catches typos ("propanol" inside "propranolol") 
#         # and clinical variations ("asthma" inside "bronchial asthma").
#         query = """
#         OPTIONAL MATCH (med1:Drug)-[r1]-(d:Disease) 
#         WHERE any(drug IN $drugs WHERE toLower(med1.name) CONTAINS drug) 
#           AND any(dis IN $diseases WHERE toLower(d.name) CONTAINS dis)
#           AND type(r1) CONTAINS 'CONTRAINDICATED'
          
#         OPTIONAL MATCH (med2a:Drug)-[r2:INTERACTS_WITH]-(med2b:Drug) 
#         WHERE any(drugA IN $drugs WHERE toLower(med2a.name) CONTAINS drugA)
#           AND any(drugB IN $drugs WHERE toLower(med2b.name) CONTAINS drugB)
        
#         OPTIONAL MATCH (med3:Drug)-[r3:TRIGGERS_ALLERGY]-(a:Allergy) 
#         WHERE any(drug IN $drugs WHERE toLower(med3.name) CONTAINS drug)
#           AND any(alg IN $allergies WHERE toLower(a.name) CONTAINS alg)
        
#         OPTIONAL MATCH (med4:Drug)-[r4:UNSAFE_FOR]-(f:PatientFactor) 
#         WHERE any(drug IN $drugs WHERE toLower(med4.name) CONTAINS drug)
#           AND any(fac IN $factors WHERE toLower(f.name) CONTAINS fac)
        
#         OPTIONAL MATCH (med5:Drug)-[r5:WORSENED_BY_LAB]-(l:LabValue) 
#         WHERE any(drug IN $drugs WHERE toLower(med5.name) CONTAINS drug)
#           AND any(lab IN $labs WHERE toLower(l.name) CONTAINS lab)
        
#         RETURN 
#             med1.name AS D1, d.name AS Dis, r1.reason AS R1, r1.severity AS S1,
#             med2a.name AS D2a, med2b.name AS D2b, r2.mechanism AS R2, r2.severity AS S2,
#             med3.name AS D3, a.name AS Alg, r3.reason AS R3, r3.severity AS S3,
#             med4.name AS D4, f.name AS Fac, r4.reason AS R4, r4.severity AS S4,
#             med5.name AS D5, l.name AS Lab, r5.reason AS R5, r5.severity AS S5
#         """
        
#         with self.driver.session() as session:
#             result = session.run(
#                 query, 
#                 drugs=drugs_lower, 
#                 diseases=diseases_lower, 
#                 allergies=allergies_lower, 
#                 factors=factors_lower, 
#                 labs=labs_lower
#             )
#             for record in result:
#                 if record['Dis']: red_flags.append(f"[{record['S1'] or 'HIGH'}] DISEASE CONFLICT: {record['D1']} contraindicated for {record['Dis']} ({record['R1'] or 'Risk of severe adverse event.'})")
#                 if record['D2a'] and record['D2b'] and record['D2a'] != record['D2b']: red_flags.append(f"[{record['S2'] or 'HIGH'}] DRUG INTERACTION: {record['D2a']} + {record['D2b']} ({record['R2'] or 'Adverse interaction detected.'})")
#                 if record['Alg']: red_flags.append(f"[{record['S3'] or 'HIGH'}] ALLERGY ALERT: {record['D3']} triggers {record['Alg']} ({record['R3']})")
#                 if record['Fac']: red_flags.append(f"[{record['S4'] or 'HIGH'}] DEMOGRAPHIC RISK: {record['D4']} unsafe for {record['Fac']} ({record['R4']})")
#                 if record['Lab']: red_flags.append(f"[{record['S5'] or 'HIGH'}] LAB/VITAL RISK: {record['D5']} dangerous with {record['Lab']} ({record['R5']})")
        
#         return list(set(red_flags))

# medical_graph = Neo4jMedicalGraph()



# """
# MedGPT Guardian — Neo4j clinical safety verification.

# Confirmed schema:
#   Nodes: Drug, Disease, Allergy, PatientFactor, LabValue
#   Relationships:
#     Drug -[:CONTRAINDICATED_BY]-> Disease
#     Drug -[:INTERACTS_WITH]- Drug
#     Drug -[:TRIGGERS_ALLERGY]-> Allergy
#     Drug -[:UNSAFE_FOR]-> PatientFactor
#     Drug -[:WORSENED_BY_LAB]-> LabValue

# Node property: name
# Relationship properties: mechanism, reason, severity
# """

# import logging
# import os
# from pathlib import Path
# from typing import Any

# from dotenv import load_dotenv
# from neo4j import GraphDatabase

# logger = logging.getLogger(__name__)

# BACKEND_DIR = Path(__file__).resolve().parents[2]
# load_dotenv(BACKEND_DIR / ".env")

# ALLOWED_LABELS = {
#     "Drug",
#     "Disease",
#     "Allergy",
#     "PatientFactor",
#     "LabValue",
# }

# ALLOWED_SEVERITIES = {
#     "LOW", "MODERATE", "MEDIUM", "HIGH", "CRITICAL"
# }


# def _as_list(values: Any) -> list[str]:
#     """Convert a string, iterable, or None into unique non-empty strings."""
#     if values is None:
#         return []

#     if isinstance(values, str):
#         values = [values]

#     result = []
#     seen = set()

#     try:
#         for value in values:
#             if value is None:
#                 continue

#             name = str(value).strip()
#             key = name.casefold()

#             if key and key not in seen:
#                 result.append(name)
#                 seen.add(key)
#     except TypeError:
#         return []

#     return result


# class MedicalGraph:
#     """Conservative safety checks against the configured Neo4j graph."""

#     def __init__(self):
#         self.uri = os.getenv("NEO4J_URI")
#         self.username = (
#             os.getenv("NEO4J_USERNAME")
#             or os.getenv("NEO4J_USER")
#         )
#         self.password = os.getenv("NEO4J_PASSWORD")
#         self.database = os.getenv("NEO4J_DATABASE") or None
#         self._driver = None

#     def _get_driver(self):
#         if not self.uri or not self.username or not self.password:
#             raise RuntimeError(
#                 "Neo4j configuration is incomplete. Check "
#                 "NEO4J_URI, NEO4J_USERNAME/NEO4J_USER, "
#                 "and NEO4J_PASSWORD in backend/.env."
#             )

#         if self._driver is None:
#             self._driver = GraphDatabase.driver(
#                 self.uri,
#                 auth=(self.username, self.password),
#             )

#         return self._driver

#     def close(self):
#         """Close the driver when the FastAPI application shuts down."""
#         if self._driver is not None:
#             self._driver.close()
#             self._driver = None

#     def health_check(self) -> bool:
#         try:
#             with self._get_driver().session(
#                 database=self.database
#             ) as session:
#                 session.run("RETURN 1 AS ok").single()
#             return True
#         except Exception:
#             logger.exception("Neo4j health check failed")
#             return False

#     def _find_node(self, label: str, name: str):
#         """
#         Resolve a node by case-insensitive exact name.

#         No fuzzy matching is used for clinical entities. The label is
#         selected only from ALLOWED_LABELS, never directly from user input.
#         """
#         if label not in ALLOWED_LABELS:
#             raise ValueError(f"Unsupported node label: {label}")

#         name = str(name).strip()
#         if not name:
#             return None

#         query = f"""
#         MATCH (n:{label})
#         WHERE n.name IS NOT NULL
#           AND toLower(trim(toString(n.name))) =
#               toLower(trim($name))
#         RETURN n.name AS matched_name
#         LIMIT 1
#         """

#         with self._get_driver().session(
#             database=self.database
#         ) as session:
#             record = session.run(query, name=name).single()

#         return record["matched_name"] if record else None

#     def _known_names(
#         self,
#         label: str,
#         names: Any,
#     ) -> dict[str, str]:
#         """
#         Return {input_name: canonical_graph_name} for resolved entities.
#         Unmatched inputs are deliberately not silently accepted.
#         """
#         resolved = {}

#         for name in _as_list(names):
#             matched = self._find_node(label, name)
#             if matched:
#                 resolved[name] = matched

#         return resolved

#     @staticmethod
#     def _severity(value: Any) -> str:
#         severity = str(value or "HIGH").strip().upper()
#         return (
#             severity
#             if severity in ALLOWED_SEVERITIES
#             else "HIGH"
#         )

#     @staticmethod
#     def _make_alert(
#         category: str,
#         drug: str,
#         related_entity: str,
#         severity: Any,
#         reason: str | None,
#     ) -> dict:
#         return {
#             "category": category,
#             "severity": MedicalGraph._severity(severity),
#             "drug": drug,
#             "related_entity": related_entity,
#             "message": (
#                 f"Graph-recorded {category.lower().replace('_', ' ')}: "
#                 f"{drug} and {related_entity}."
#             ),
#             "reason": reason,
#             "source": "neo4j_knowledge_graph",
#         }

#     def _query_directional_relationship(
#         self,
#         drug_names: list[str],
#         entity_names: list[str],
#         relationship: str,
#         target_label: str,
#         category: str,
#     ) -> list[dict]:
#         """
#         Query confirmed Drug -> target relationship directions.
#         """
#         relationship_config = {
#             "CONTRAINDICATED_BY": ("Disease", "DISEASE_CONFLICT"),
#             "TRIGGERS_ALLERGY": ("Allergy", "ALLERGY_CONFLICT"),
#             "UNSAFE_FOR": (
#                 "PatientFactor",
#                 "PATIENT_FACTOR_CONFLICT",
#             ),
#             "WORSENED_BY_LAB": ("LabValue", "LAB_CONFLICT"),
#         }

#         if relationship not in relationship_config:
#             raise ValueError("Unsupported relationship type")

#         expected_label, expected_category = relationship_config[
#             relationship
#         ]

#         if target_label != expected_label or category != expected_category:
#             raise ValueError("Relationship configuration mismatch")

#         if not drug_names or not entity_names:
#             return []

#         query = f"""
#         MATCH (d:Drug)-[r:{relationship}]->(x:{target_label})
#         WHERE d.name IN $drug_names
#           AND x.name IN $entity_names
#         RETURN DISTINCT
#             d.name AS drug,
#             x.name AS related_entity,
#             r.severity AS severity,
#             coalesce(r.reason, r.mechanism) AS reason
#         """

#         with self._get_driver().session(
#             database=self.database
#         ) as session:
#             rows = [
#                 record.data()
#                 for record in session.run(
#                     query,
#                     drug_names=drug_names,
#                     entity_names=entity_names,
#                 )
#             ]

#         return [
#             self._make_alert(
#                 category=category,
#                 drug=row["drug"],
#                 related_entity=row["related_entity"],
#                 severity=row["severity"],
#                 reason=row["reason"],
#             )
#             for row in rows
#         ]

#     def _check_drug_interactions(
#         self,
#         drug_names: list[str],
#     ) -> list[dict]:
#         """
#         Check interactions only between the proposed drugs.

#         elementId ordering ensures each unordered pair is emitted once,
#         even if the relationship can be traversed in either direction.
#         """
#         drug_names = list(dict.fromkeys(drug_names))
#         if len(drug_names) < 2:
#             return []

#         query = """
#         MATCH (a:Drug)-[r:INTERACTS_WITH]-(b:Drug)
#         WHERE a.name IN $drug_names
#           AND b.name IN $drug_names
#           AND elementId(a) < elementId(b)
#         RETURN DISTINCT
#             a.name AS drug_a,
#             b.name AS drug_b,
#             r.severity AS severity,
#             coalesce(r.reason, r.mechanism) AS reason
#         """

#         with self._get_driver().session(
#             database=self.database
#         ) as session:
#             rows = [
#                 record.data()
#                 for record in session.run(
#                     query,
#                     drug_names=drug_names,
#                 )
#             ]

#         return [
#             self._make_alert(
#                 category="DRUG_INTERACTION",
#                 drug=row["drug_a"],
#                 related_entity=row["drug_b"],
#                 severity=row["severity"],
#                 reason=row["reason"],
#             )
#             for row in rows
#         ]

#     def verify_clinical_safety(
#         self,
#         patient_diseases=None,
#         patient_allergies=None,
#         patient_factors=None,
#         patient_labs=None,
#         proposed_drugs=None,
#     ) -> dict:
#         """
#         Check graph-recorded risks.

#         A missing relationship is not proof of safety. This method is
#         not a substitute for clinical review or evidence verification.
#         """
#         inputs = {
#             "Disease": _as_list(patient_diseases),
#             "Allergy": _as_list(patient_allergies),
#             "PatientFactor": _as_list(patient_factors),
#             "LabValue": _as_list(patient_labs),
#             "Drug": _as_list(proposed_drugs),
#         }

#         matched = {}
#         unresolved = []
#         alerts = []

#         try:
#             for label, names in inputs.items():
#                 resolved = self._known_names(label, names)
#                 matched[label] = resolved

#                 resolved_inputs = {
#                     name.casefold() for name in resolved
#                 }

#                 for name in names:
#                     if name.casefold() not in resolved_inputs:
#                         unresolved.append({
#                             "entity_type": label,
#                             "name": name,
#                             "reason": (
#                                 "No case-insensitive exact name match "
#                                 "was found in Neo4j."
#                             ),
#                         })

#             drugs = list(dict.fromkeys(matched["Drug"].values()))
#             diseases = list(dict.fromkeys(matched["Disease"].values()))
#             allergies = list(dict.fromkeys(matched["Allergy"].values()))
#             factors = list(
#                 dict.fromkeys(matched["PatientFactor"].values())
#             )
#             labs = list(dict.fromkeys(matched["LabValue"].values()))

#             alerts.extend(
#                 self._query_directional_relationship(
#                     drugs,
#                     diseases,
#                     "CONTRAINDICATED_BY",
#                     "Disease",
#                     "DISEASE_CONFLICT",
#                 )
#             )

#             alerts.extend(
#                 self._query_directional_relationship(
#                     drugs,
#                     allergies,
#                     "TRIGGERS_ALLERGY",
#                     "Allergy",
#                     "ALLERGY_CONFLICT",
#                 )
#             )

#             alerts.extend(
#                 self._query_directional_relationship(
#                     drugs,
#                     factors,
#                     "UNSAFE_FOR",
#                     "PatientFactor",
#                     "PATIENT_FACTOR_CONFLICT",
#                 )
#             )

#             alerts.extend(
#                 self._query_directional_relationship(
#                     drugs,
#                     labs,
#                     "WORSENED_BY_LAB",
#                     "LabValue",
#                     "LAB_CONFLICT",
#                 )
#             )

#             alerts.extend(self._check_drug_interactions(drugs))

#             incomplete = bool(unresolved)
#             safe = not alerts and not incomplete

#             return {
#                 "is_safe": safe,
#                 "verification_complete": not incomplete,
#                 "verification_incomplete": incomplete,
#                 "alerts": alerts,
#                 "unresolved_entities": unresolved,
#                 "matched_entities": matched,
#                 "message": (
#                     "No configured graph conflicts were found. "
#                     "This is not proof of clinical safety."
#                     if safe
#                     else (
#                         "Potential graph conflicts were found."
#                         if alerts
#                         else "Verification is incomplete because "
#                              "some entities could not be resolved."
#                     )
#                 ),
#             }

#         except Exception:
#             logger.exception("Neo4j clinical verification failed")
#             return {
#                 "is_safe": False,
#                 "verification_complete": False,
#                 "verification_incomplete": True,
#                 "alerts": alerts,
#                 "unresolved_entities": unresolved,
#                 "matched_entities": matched,
#                 "error": "Neo4j verification failed.",
#                 "message": (
#                     "Safety could not be verified. Do not treat this "
#                     "verification failure as a safe result."
#                 ),
#             }


# # Preserve the common import names used by the application.
# Neo4jMedicalGraph = MedicalGraph
# medical_graph = MedicalGraph()


"""
backend/app/core/graph.py (v2) - Structured safety findings from the 5-dimension Neo4j graph.
 
What changed vs earlier versions
  * Returns structured findings (kind, drug, target, severity, source, evidence), not just strings.
  * Works whether your nodes were loaded by the old LOAD CSV script (only 'name') or the new seed script
    ('name' + 'name_lc'): ensure_schema() adds name_lc where it is missing and creates indexes.
  * Partial, plural-tolerant matching: "peptic ulcers" matches "peptic ulcer disease", "severe asthma" matches "asthma".
  * Severity is never invented. PrimeKG interaction edges have no severity -> "UNSPECIFIED".
    DDInter edges carry Major/Moderate/Minor. Label-derived rows carry High/Moderate -> CONTRAINDICATED/CAUTION.
  * Raises on database errors so callers can never mistake "check failed" for "no conflicts".
"""
import logging
import os
from typing import Dict, List, Optional, Set
 
from pathlib import Path
 
from dotenv import load_dotenv
from neo4j import GraphDatabase
 
load_dotenv(Path(__file__).resolve().parents[2] / ".env")   # backend/.env
load_dotenv()
logger = logging.getLogger(__name__)
 
LABELS = ["Drug", "Disease", "Allergy", "PatientFactor", "LabValue"]
# (finding kind, patient-side node label, relationship type)
PATIENT_SIDE = [
    ("contraindication", "Disease", "CONTRAINDICATED_BY"),
    ("allergy", "Allergy", "TRIGGERS_ALLERGY"),
    ("population", "PatientFactor", "UNSAFE_FOR"),
    ("lab", "LabValue", "WORSENED_BY_LAB"),
]
FACT_KEYS = ["INDICAT", "CONTRA", "OFF_LABEL", "PHENOTYPE", "SYMPTOM"]
KIND_ORDER = {"contraindication": 0, "allergy": 1, "population": 2, "lab": 3, "interaction": 4}
SEV_ORDER = {"CONTRAINDICATED": 0, "MAJOR": 1, "CAUTION": 2, "MODERATE": 3, "MINOR": 4, "UNSPECIFIED": 5}
 
 
def _sev_patient(v) -> str:
    s = str(v or "").strip().upper()
    return "CAUTION" if s in ("MODERATE", "CAUTION", "MEDIUM", "LOW", "MINOR") else "CONTRAINDICATED"
 
 
def _sev_interaction(v) -> str:
    s = str(v or "").strip().upper()
    if s in ("MAJOR", "SEVERE", "HIGH"):
        return "MAJOR"
    if s == "MODERATE":
        return "MODERATE"
    if s in ("MINOR", "LOW"):
        return "MINOR"
    return "UNSPECIFIED"
 
 
def _variants(term: str) -> List[str]:
    out = [term]
    if len(term) > 4 and term.endswith("s") and not term.endswith("ss"):
        out.append(term[:-1])
    return out
 
 
def format_finding(f: Dict) -> str:
    kind, d, t, sev = f["kind"], f["drug"], f["target"], f["severity"]
    src = f.get("source") or "knowledge graph"
    why = f" - {f['evidence']}" if f.get("evidence") else ""
    if kind == "interaction":
        sev_txt = "severity not specified in the source" if sev == "UNSPECIFIED" else f"severity: {sev.lower()}"
        text = f"{d} + {t}: documented drug interaction ({sev_txt})"
    elif kind == "contraindication":
        text = (f"{d} is contraindicated in {t}" if sev == "CONTRAINDICATED"
                else f"{d} should be avoided or used with caution in {t}")
    elif kind == "allergy":
        text = f"{d} may trigger a reaction in patients allergic to {t}"
    elif kind == "population":
        text = f"{d} is flagged as unsafe / needs caution for: {t}"
    else:
        text = f"{d} is flagged for caution with {t}"
    return f"{text}{why} (source: {src})"
 
 
class Neo4jMedicalGraph:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
        self.database = os.getenv("NEO4J_DATABASE") or None
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        self._schema_ready = False
 
    def _session(self):
        return self.driver.session(database=self.database) if self.database else self.driver.session()
 
    # ---------- housekeeping ----------
    def ensure_schema(self):
        if self._schema_ready:
            return
        with self._session() as s:
            for label in LABELS:
                s.run(f"MATCH (n:{label}) WHERE n.name_lc IS NULL AND n.name IS NOT NULL SET n.name_lc = toLower(n.name)")
                try:
                    s.run(f"CREATE INDEX {label.lower()}_name_lc IF NOT EXISTS FOR (n:{label}) ON (n.name_lc)")
                except Exception as e:     # an equivalent constraint/index may already exist
                    logger.info("index for %s not created: %s", label, str(e)[:100])
        self._schema_ready = True
 
    def db_stats(self) -> dict:
        with self._session() as s:
            nodes = s.run("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS c").data()
            rels = s.run("MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS c").data()
        return {"nodes": {r["label"]: r["c"] for r in nodes}, "relationships": {r["type"]: r["c"] for r in rels}}
 
    @staticmethod
    def _clean(items) -> List[str]:
        out = []
        for i in items or []:
            s = str(i).lower().strip()
            if len(s) >= 3 and s not in out:
                out.append(s)
        return out
 
    def existing_drugs(self, names_lc: List[str]) -> Set[str]:
        names = self._clean(names_lc)
        if not names:
            return set()
        self.ensure_schema()
        with self._session() as s:
            rows = s.run("MATCH (d:Drug) WHERE d.name_lc IN $names RETURN d.name_lc AS n", names=names).data()
        return {r["n"] for r in rows}
 
    # ---------- main check ----------
    def check(self, drugs, conditions=None, allergies=None, factors=None, labs=None, meds=None) -> Dict:
        """
        drugs: drugs being asked about / recommended (resolved database names, lowercase)
        meds : drugs the patient already takes (interaction partners)
        Returns {"findings": [...], "unmatched_conditions": [...]}.  Raises on database errors.
        """
        drugs = self._clean(drugs)
        if not drugs:
            return {"findings": [], "unmatched_conditions": []}
        self.ensure_schema()
        terms_by_kind = {
            "contraindication": self._clean(conditions), "allergy": self._clean(allergies),
            "population": self._clean(factors), "lab": self._clean(labs),
        }
        findings, seen, unmatched = [], set(), []
 
        with self._session() as s:
            for kind, label, rel in PATIENT_SIDE:
                originals = terms_by_kind[kind]
                if not originals:
                    continue
                expanded = sorted({v for t in originals for v in _variants(t)})
                rows = s.run(
                    f"""
                    MATCH (dr:Drug)-[x:{rel}]->(t:{label})
                    WHERE dr.name_lc IN $drugs
                      AND any(c IN $terms WHERE t.name_lc CONTAINS c
                              OR (size(t.name_lc) >= 5 AND c CONTAINS t.name_lc))
                    RETURN dr.name_lc AS drug, t.name AS target, x.severity AS severity,
                           x.reason AS reason, x.source AS source
                    """,
                    drugs=drugs, terms=expanded,
                ).data()
                for r in rows:
                    key = (kind, r["drug"], str(r["target"]).lower())
                    if key in seen:
                        continue
                    seen.add(key)
                    findings.append({"kind": kind, "drug": r["drug"], "target": r["target"],
                                     "severity": _sev_patient(r["severity"]),
                                     "source": r["source"] or "knowledge graph",
                                     "evidence": (r["reason"] or "").strip()})
                if kind == "contraindication":     # does the graph know these conditions at all?
                    hits = s.run(
                        """
                        UNWIND $terms AS term
                        OPTIONAL MATCH (t:Disease)
                        WHERE t.name_lc CONTAINS term OR (size(t.name_lc) >= 5 AND term CONTAINS t.name_lc)
                        RETURN term, count(t) AS n
                        """, terms=expanded).data()
                    known = {h["term"] for h in hits if h["n"] > 0}
                    unmatched = [t for t in originals if not any(v in known for v in _variants(t))]
 
            others = sorted(set(drugs) | set(self._clean(meds)))
            if len(others) >= 2:
                rows = s.run(
                    """
                    MATCH (a:Drug)-[x:INTERACTS_WITH]-(b:Drug)
                    WHERE a.name_lc IN $drugs AND b.name_lc IN $others AND a.name_lc <> b.name_lc
                    RETURN a.name_lc AS a, b.name_lc AS b, x.severity AS severity,
                           x.reason AS reason, x.source AS source
                    """, drugs=drugs, others=others).data()
                best: Dict = {}
                for r in rows:
                    pair = tuple(sorted((r["a"], r["b"])))
                    sev = _sev_interaction(r["severity"])
                    cur = best.get(pair)
                    if cur is None or SEV_ORDER[sev] < SEV_ORDER[cur["severity"]]:
                        best[pair] = {"kind": "interaction", "drug": pair[0], "target": pair[1], "severity": sev,
                                      "source": r["source"] or "knowledge graph",
                                      "evidence": (r["reason"] or "").strip()}
                findings.extend(best.values())
 
        findings.sort(key=lambda f: (KIND_ORDER[f["kind"]], SEV_ORDER.get(f["severity"], 9), f["drug"]))
        for i, f in enumerate(findings, 1):
            f["id"] = f"G{i}"
        return {"findings": findings, "unmatched_conditions": unmatched}
 
    # ---------- context facts for educational / treatment answers ----------
    def facts(self, label: str, terms: List[str], per_group: int = 15, max_entities: int = 2) -> List[Dict]:
        """
        Schema-agnostic: for each matching node, list neighbours reached through relationship types whose name
        contains INDICAT / CONTRA / OFF_LABEL / PHENOTYPE / SYMPTOM (side-effect lists are skipped on purpose,
        they have no frequency information). Returns [{"entity": name, "groups": {REL_TYPE: [names]}}].
        """
        if label not in LABELS:
            return []
        terms = self._clean(terms)
        if not terms:
            return []
        self.ensure_schema()
        out: List[Dict] = []
        with self._session() as s:
            for term in terms[:3]:
                ents = s.run(
                    f"""
                    MATCH (n:{label})
                    WHERE n.name_lc = $t OR (n.name_lc CONTAINS $t AND size(n.name_lc) <= size($t) + 25)
                    RETURN n.name AS name, n.name_lc AS lc
                    ORDER BY CASE WHEN n.name_lc = $t THEN 0 ELSE 1 END, size(n.name_lc) LIMIT $k
                    """, t=term, k=max_entities).data()
                for e in ents:
                    rows = s.run(
                        f"""
                        MATCH (n:{label} {{name_lc: $lc}})-[r]-(x)
                        WHERE any(k IN $keys WHERE type(r) CONTAINS k)
                        RETURN type(r) AS rel, x.name AS other LIMIT 400
                        """, lc=e["lc"], keys=FACT_KEYS).data()
                    groups: Dict[str, List[str]] = {}
                    for r in rows:
                        g = groups.setdefault(r["rel"], [])
                        if r["other"] and r["other"] not in g and len(g) < per_group:
                            g.append(r["other"])
                    if groups:
                        out.append({"entity": e["name"], "groups": groups})
        return out
 
    # ---------- legacy wrapper (old main.py signature) ----------
    def verify_clinical_safety(self, patient_diseases, patient_allergies, patient_factors,
                               patient_labs, proposed_drugs, patient_meds=None) -> List[str]:
        res = self.check(proposed_drugs, patient_diseases, patient_allergies, patient_factors,
                         patient_labs, patient_meds)
        return [f"[{f['severity']}] {format_finding(f)}" for f in res["findings"]]
 
 
MedicalGraph = Neo4jMedicalGraph          # name used by older code
medical_graph = Neo4jMedicalGraph()
 
if __name__ == "__main__":
    print(medical_graph.db_stats())
    print(medical_graph.check(["propranolol", "warfarin"], ["asthma", "peptic ulcers"], meds=["warfarin"]))
 
