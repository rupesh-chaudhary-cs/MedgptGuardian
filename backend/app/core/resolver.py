"""
backend/app/core/resolver.py - Map the drug names found in a question to the exact names stored in Neo4j.
 
Order tried for every name:  as typed -> RxNav ingredient -> alias table -> must exist in the graph.
Names that still do not exist are reported as UNRESOLVED (the system then says "not checked"; it never
claims "no interaction found" for them).
 
DrugBank (used by PrimeKG) and RxNorm sometimes use different names for the same drug, e.g. aspirin is
"Acetylsalicylic acid" in DrugBank. Add rows to ALIASES whenever you see an unresolved drug you care about.
Each value is a list of candidate names; the first one that exists in your graph wins.
"""
import os
from typing import Dict, List, Set, Tuple
 
from app.core.rxnav_api import rxnav_client
 
ALIASES: Dict[str, List[str]] = {
    "aspirin": ["aspirin", "acetylsalicylic acid"], "acetylsalicylic acid": ["acetylsalicylic acid", "aspirin"],
    "acetaminophen": ["acetaminophen", "paracetamol"], "paracetamol": ["acetaminophen", "paracetamol"],
    "albuterol": ["albuterol", "salbutamol"], "salbutamol": ["salbutamol", "albuterol"],
    "epinephrine": ["epinephrine", "adrenaline"], "adrenaline": ["epinephrine", "adrenaline"],
    "norepinephrine": ["norepinephrine", "noradrenaline"], "noradrenaline": ["norepinephrine", "noradrenaline"],
    "levothyroxine": ["levothyroxine", "thyroxine"], "thyroxine": ["levothyroxine", "thyroxine"],
    "glyburide": ["glyburide", "glibenclamide"], "glibenclamide": ["glibenclamide", "glyburide"],
    "furosemide": ["furosemide", "frusemide"], "frusemide": ["furosemide", "frusemide"],
    "meperidine": ["meperidine", "pethidine"], "pethidine": ["meperidine", "pethidine"],
    "rifampin": ["rifampin", "rifampicin"], "rifampicin": ["rifampicin", "rifampin"],
    "cyclosporine": ["cyclosporine", "ciclosporin"], "ciclosporin": ["cyclosporine", "ciclosporin"],
    "lidocaine": ["lidocaine", "lignocaine"], "lignocaine": ["lidocaine", "lignocaine"],
    "nitroglycerin": ["nitroglycerin", "glyceryl trinitrate"], "glyceryl trinitrate": ["nitroglycerin", "glyceryl trinitrate"],
    "isoproterenol": ["isoproterenol", "isoprenaline"], "isoprenaline": ["isoprenaline", "isoproterenol"],
    "phenobarbital": ["phenobarbital", "phenobarbitone"], "phenobarbitone": ["phenobarbital", "phenobarbitone"],
    "vitamin k": ["phytonadione", "vitamin k"], "vitamin c": ["ascorbic acid"], "vitamin b12": ["cyanocobalamin"],
    "vitamin d": ["cholecalciferol", "vitamin d"],
}
 
 
def candidates_for(name: str) -> List[str]:
    n = name.strip().lower()
    names = [n]
    if os.getenv("RXNAV_ENABLED", "1") != "0":
        norm = rxnav_client.normalize_drug(n)
        if norm and norm != n:
            names.append(norm)
    out: List[str] = []
    for x in names:
        for c in ALIASES.get(x, [x]):
            if c not in out:
                out.append(c)
    return out
 
 
def resolve_drugs(names: List[str], graph) -> Tuple[Dict[str, str], List[str], Dict[str, Set[str]]]:
    """Returns (typed_name -> database_name, unresolved typed names, database_name -> all known spellings)."""
    clean = []
    for n in names or []:
        n = str(n).strip().lower()
        if len(n) >= 3 and n not in clean:
            clean.append(n)
    cand_map = {n: candidates_for(n) for n in clean}
    present = graph.existing_drugs(sorted({c for v in cand_map.values() for c in v}))
    resolved: Dict[str, str] = {}
    unresolved: List[str] = []
    alias_map: Dict[str, Set[str]] = {}
    for n, cands in cand_map.items():
        hit = next((c for c in cands if c in present), None)
        if hit:
            resolved[n] = hit
            alias_map.setdefault(hit, set()).update(set(cands) | {n})
        else:
            unresolved.append(n)
    return resolved, unresolved, alias_map
 