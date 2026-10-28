# import os
# import pandas as pd
# import urllib.request
# import shutil

# kg_file_path = "kg4.csv"
# output_dir = "app/data/kg"
# os.makedirs(output_dir, exist_ok=True)

# # STEP 1: AUTOMATIC DOWNLOAD WITH BROWSER DISGUISE
# if not os.path.exists(kg_file_path):
#     print("⏳ Downloading the massive PrimeKG dataset (bypassing server blocks)...")
#     url = "https://dataverse.harvard.edu/api/access/datafile/6180620"
    
#     # Disguise the Python script as a Google Chrome browser to bypass the 403 Forbidden error
#     req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
#     try:
#         with urllib.request.urlopen(req) as response, open(kg_file_path, 'wb') as out_file:
#             shutil.copyfileobj(response, out_file)
#         print("✅ Download complete!")
#     except Exception as e:
#         print(f"❌ Automated download failed: {e}")
#         print("\n⚠️ FAILSAFE INSTRUCTIONS FOR YOUR DEADLINE:")
#         print("1. Open Chrome and paste this exact URL: https://dataverse.harvard.edu/api/access/datafile/6180620")
#         print("2. Once downloaded, drag the file into your VS Code 'backend' folder.")
#         print("3. Rename it to 'kg.csv' (if it isn't already).")
#         print("4. Run this script again.")
#         exit()
# else:
#     print("✅ kg.csv already exists locally. Skipping download.")

# # STEP 2: EXTRACT THE 5 MULTIDIMENSIONAL VECTORS
# print("⏳ Loading the massive dataset into memory...")
# df = pd.read_csv(kg_file_path, usecols=['x_type', 'x_name', 'y_type', 'y_name', 'display_relation'], low_memory=False)

# print("🚀 Extracting Dimension 1: Drug-Disease Indications & Contraindications...")
# d1 = df[(df['x_type'] == 'drug') & (df['y_type'] == 'disease')].copy()
# d1.rename(columns={'x_name': 'Drug', 'y_name': 'Disease', 'display_relation': 'Reason'}, inplace=True)
# d1['Severity'] = 'HIGH'
# d1[['Drug', 'Disease', 'Severity', 'Reason']].to_csv(f"{output_dir}/dim1_disease.csv", index=False)

# print("🚀 Extracting Dimension 2: Drug-Drug Interactions...")
# d2 = df[(df['x_type'] == 'drug') & (df['y_type'] == 'drug')].copy()
# d2.rename(columns={'x_name': 'Drug1', 'y_name': 'Drug2', 'display_relation': 'Mechanism'}, inplace=True)
# d2['Severity'] = 'HIGH'
# d2[['Drug1', 'Drug2', 'Severity', 'Mechanism']].to_csv(f"{output_dir}/dim2_drug.csv", index=False)

# print("🚀 Extracting Dimension 3: Drug-Allergy Triggers...")
# allergy_kw = 'allergy|hypersensitivity|anaphylaxis|rash|dermatitis'
# d3 = df[(df['x_type'] == 'drug') & (df['y_type'] == 'effect/phenotype') & (df['y_name'].str.contains(allergy_kw, case=False, na=False))].copy()
# d3.rename(columns={'x_name': 'Drug', 'y_name': 'Allergy', 'display_relation': 'Reason'}, inplace=True)
# d3['Severity'] = 'HIGH'
# d3[['Drug', 'Allergy', 'Severity', 'Reason']].to_csv(f"{output_dir}/dim3_allergy.csv", index=False)

# print("🚀 Extracting Dimension 4: Patient Factor & Side Effects...")
# d4 = df[(df['x_type'] == 'drug') & (df['y_type'] == 'effect/phenotype') & (~df['y_name'].str.contains(allergy_kw, case=False, na=False))].copy()
# d4.rename(columns={'x_name': 'Drug', 'y_name': 'Factor', 'display_relation': 'Reason'}, inplace=True)
# d4['Severity'] = 'MODERATE'
# d4[['Drug', 'Factor', 'Severity', 'Reason']].to_csv(f"{output_dir}/dim4_factor.csv", index=False)

# print("🚀 Extracting Dimension 5: Lab Value Conflicts...")
# lab_kw = 'blood|level|deficiency|abnormal|count|pressure|hypo|hyper'
# d5 = df[(df['x_type'] == 'drug') & (df['y_name'].str.contains(lab_kw, case=False, na=False))].copy()
# d5.rename(columns={'x_name': 'Drug', 'y_name': 'Lab', 'display_relation': 'Reason'}, inplace=True)
# d5['Severity'] = 'HIGH'
# d5[['Drug', 'Lab', 'Severity', 'Reason']].to_csv(f"{output_dir}/dim5_lab.csv", index=False)

# print(f"✅ Outstanding! All 5 dimensions have been successfully extracted and saved to backend/{output_dir}/")

"""
backend/extract_dimensions.py (v2) - Build CORRECT dimension CSVs from PrimeKG.
 
Run from the backend folder:   python extract_dimensions.py            (reads kg4.csv)
                               python extract_dimensions.py other.csv
 
WHAT WAS WRONG WITH THE OLD VERSION
  * dim1 took EVERY drug->disease row (indications, off-label uses AND contraindications) and called them all
    "CONTRAINDICATED_BY, severity HIGH". A drug that TREATS a disease was recorded as contraindicated for it.
  * dim2 marked every drug-drug pair "HIGH" severity (PrimeKG has no severity).
  * dim3/dim4/dim5 were PrimeKG SIDE-EFFECT lists renamed as allergies, patient factors and lab values
    (e.g. "headache" became a PatientFactor). Those are not allergies, patient risk groups or lab conflicts.
That is why the database has 2.8 million relationships but still misses propranolol + asthma.
 
WHAT THIS VERSION WRITES (to app/data/kg)
  dim1_disease.csv     only real contraindications (relation = contraindication)       -> CONTRAINDICATED_BY
  dim6_indication.csv  indications and off-label uses (context for educational answers) -> INDICATED_FOR / OFF_LABEL_FOR
  dim2_drug.csv        drug-drug interaction pairs, each pair once, severity left blank  -> INTERACTS_WITH
  dim3/4/5             header-only files. Real allergy / patient-factor / lab data comes from FDA drug labels
                       (colab_build_all_dims.ipynb); nothing in PrimeKG represents them honestly.
"""
import sys
from collections import Counter
from pathlib import Path
 
import pandas as pd
 
KG = sys.argv[1] if len(sys.argv) > 1 else "kg4.csv"
OUT = Path("app/data/kg")
OUT.mkdir(parents=True, exist_ok=True)
 
if not Path(KG).exists():
    sys.exit(f"{KG} not found. Run this from the backend folder, or pass the path to PrimeKG's kg.csv.")
 
wanted = ["relation", "display_relation", "x_type", "x_name", "y_type", "y_name"]
header = list(pd.read_csv(KG, nrows=0).columns)
use = [c for c in wanted if c in header]
if not {"x_type", "x_name", "y_type", "y_name"} <= set(use):
    sys.exit(f"Unexpected columns in {KG}: {header}")
if not ({"relation", "display_relation"} & set(use)):
    sys.exit("Neither 'relation' nor 'display_relation' column found.")
 
contra, indic, ddi_pairs = set(), set(), set()
kinds_drug_disease, kinds_drug_drug = Counter(), Counter()
 
print(f"Reading {KG} in chunks ...")
for chunk in pd.read_csv(KG, usecols=use, dtype=str, chunksize=500_000, low_memory=False):
    rel = chunk["relation"].fillna("").str.lower() if "relation" in chunk else pd.Series("", index=chunk.index)
    disp = chunk["display_relation"].fillna("").str.lower() if "display_relation" in chunk else pd.Series("", index=chunk.index)
    kind = rel.where(rel != "", disp)
 
    dd = chunk[(chunk.x_type == "drug") & (chunk.y_type == "disease")]
    for k, x, y in zip(kind[dd.index], dd.x_name, dd.y_name):
        kinds_drug_disease[k] += 1
        if not isinstance(x, str) or not isinstance(y, str):
            continue
        if "contraindication" in k:
            contra.add((x.strip(), y.strip()))
        elif k == "indication":
            indic.add((x.strip(), y.strip(), "indication"))
        elif k.startswith("off-label"):
            indic.add((x.strip(), y.strip(), "off-label use"))
 
    pp = chunk[(chunk.x_type == "drug") & (chunk.y_type == "drug")]
    for k, x, y in zip(kind[pp.index], pp.x_name, pp.y_name):
        kinds_drug_drug[k] += 1
        if isinstance(x, str) and isinstance(y, str) and x.strip().lower() != y.strip().lower():
            a, b = sorted((x.strip(), y.strip()), key=str.lower)
            ddi_pairs.add((a, b))
 
print("\nRelation kinds found between drug and disease:", dict(kinds_drug_disease))
print("Relation kinds found between drug and drug:   ", dict(kinds_drug_drug))
 
pd.DataFrame(sorted(contra), columns=["Drug", "Disease"]).assign(Severity="", Reason="", Source="PrimeKG") \
    .to_csv(OUT / "dim1_disease.csv", index=False)
pd.DataFrame(sorted(indic), columns=["Drug", "Disease", "Relation"]).assign(Source="PrimeKG") \
    .to_csv(OUT / "dim6_indication.csv", index=False)
pd.DataFrame(sorted(ddi_pairs), columns=["Drug1", "Drug2"]).assign(
    Severity="", Mechanism="documented interaction", Source="PrimeKG").to_csv(OUT / "dim2_drug.csv", index=False)
for fname, cols in (("dim3_allergy.csv", ["Drug", "Allergy", "Severity", "Reason", "Source"]),
                    ("dim4_factor.csv", ["Drug", "Factor", "Severity", "Reason", "Source"]),
                    ("dim5_lab.csv", ["Drug", "Lab", "Severity", "Reason", "Source"])):
    pd.DataFrame(columns=cols).to_csv(OUT / fname, index=False)
 
print(f"\nWrote to {OUT.resolve()}")
print(f"  dim1_disease.csv     {len(contra):>9,} contraindications")
print(f"  dim6_indication.csv  {len(indic):>9,} indications / off-label uses")
print(f"  dim2_drug.csv        {len(ddi_pairs):>9,} drug-drug pairs")
print("  dim3/dim4/dim5       header only (to be filled from FDA labels)")
 
print("\nSanity check, propranolol:")
for name, rows, label in (("propranolol", contra, "contraindicated in"), ("propranolol", indic, "indicated/off-label for")):
    hits = sorted(r for r in rows if r[0].lower() == name)[:8]
    print(f"  {label}:", [h[1] for h in hits] if hits else "(nothing)")
if any(r[0].lower() == "propranolol" and "asthma" in r[1].lower() for r in contra):
    print("  -> propranolol + asthma IS in PrimeKG's contraindications")
else:
    print("  -> propranolol + asthma is NOT in PrimeKG's contraindications (the FDA-label step will add it)")
 