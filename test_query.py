from app.core.rag import evidence_engine

# Run a sample clinical test query against your 5,000 NIH records
test_query = "What are the symptoms and management of asthma?"

print(f"\n[TEST] Querying Vector Database for: '{test_query}'...\n")

evidence = evidence_engine.retrieve_guideline(test_query)

print("--- RETRIEVED NIH CLINICAL EVIDENCE ---")
print(evidence)
print("---------------------------------------")