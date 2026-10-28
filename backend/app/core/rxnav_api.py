# import requests
# import logging

# logger = logging.getLogger(__name__)

# class RxNavIntegration:
#     def __init__(self):
#         self.base_url = "https://rxnav.nlm.nih.gov/REST"

#     def get_drug_rxcui(self, drug_name: str) -> str:
#         """Fetches the official NIH RxCUI identifier for a drug."""
#         try:
#             response = requests.get(f"{self.base_url}/rxcui.json?name={drug_name}")
#             response.raise_for_status()
#             data = response.json()
#             if "idGroup" in data and "rxnormId" in data["idGroup"]:
#                 return data["idGroup"]["rxnormId"][0]
#         except Exception as e:
#             logger.error(f"RxNav API Error fetching RxCUI for {drug_name}: {e}")
#         return None

#     def check_live_interactions(self, drug_name: str) -> list:
#         """Queries the live NIH database for severe drug interactions."""
#         rxcui = self.get_drug_rxcui(drug_name)
#         alerts = []
        
#         if not rxcui:
#             return alerts

#         try:
#             response = requests.get(f"{self.base_url}/interaction/interaction.json?rxcui={rxcui}&sources=DrugBank")
#             response.raise_for_status()
#             data = response.json()
            
#             if "interactionTypeGroup" in data:
#                 for group in data["interactionTypeGroup"]:
#                     for interaction_type in group.get("interactionType", []):
#                         for pair in interaction_type.get("interactionPair", []):
#                             alerts.append(f"[FDA/NIH LIVE ALERT] {pair.get('description', 'Interaction found.')}")
                            
#         except Exception as e:
#             logger.error(f"RxNav API Error fetching interactions for {drug_name}: {e}")
            
#         return list(set(alerts))

# rxnav_client = RxNavIntegration()



# import requests
# import logging

# logger = logging.getLogger(__name__)

# class RxNavIntegration:
#     def __init__(self):
#         self.base_url = "https://rxnav.nlm.nih.gov/REST"

#     def get_drug_rxcui(self, drug_name: str) -> str:
#         """Translates a text drug name into the official NIH numerical ID (RxCUI)."""
#         try:
#             # Grabs the primary drug name to avoid API confusion with classes like 'Beta Blockers'
#             clean_name = drug_name.strip().split()[0]
#             response = requests.get(f"{self.base_url}/rxcui.json?name={clean_name}", timeout=5)
            
#             if response.status_code == 200:
#                 data = response.json()
#                 if "idGroup" in data and "rxnormId" in data["idGroup"]:
#                     return data["idGroup"]["rxnormId"][0]
#         except Exception as e:
#             logger.error(f"RxNav API Error fetching RxCUI for {drug_name}: {e}")
#         return None

#     def check_drug_list_interactions(self, drug_names: list) -> list:
#         """Cross-references a list of patient drugs for fatal interactions."""
#         rxcuis = []
#         for name in drug_names:
#             rxcui = self.get_drug_rxcui(name)
#             if rxcui:
#                 rxcuis.append(rxcui)
        
#         alerts = []
#         # The NIH requires at least 2 valid drug IDs to compare interactions
#         if len(rxcuis) < 2:
#             return alerts 
            
#         try:
#             # Joins IDs with a '+' as required by the NIH server (e.g., 8787+435)
#             rxcui_string = "+".join(rxcuis)
#             url = f"{self.base_url}/interaction/list.json?rxcuis={rxcui_string}"
#             response = requests.get(url, timeout=5)
            
#             if response.status_code == 200:
#                 data = response.json()
#                 if "fullInteractionTypeGroup" in data:
#                     for group in data["fullInteractionTypeGroup"]:
#                         for interaction_type in group.get("fullInteractionType", []):
#                             for pair in interaction_type.get("interactionPair", []):
#                                 desc = pair.get('description', 'Interaction detected.')
#                                 alerts.append(f"[NIH LIVE ALERT] {desc}")
#         except Exception as e:
#             logger.error(f"RxNav API Error cross-referencing {rxcui_string}: {e}")
            
#         return list(set(alerts))

# rxnav_client = RxNavIntegration()


# import requests
# import logging
# from typing import List

# logger = logging.getLogger(__name__)

# class RxNavIntegration:
#     def __init__(self):
#         self.base_url = "https://rxnav.nlm.nih.gov/REST"

#     def get_drug_rxcui(self, drug_name: str) -> str:
#         """
#         Universally translates ANY drug name (even messy AI extractions) 
#         into its exact NIH numerical ID (RxCUI) using fuzzy matching.
#         """
#         try:
#             # Using approximateTerm ensures we get the right ID even for slight misspellings or brand names
#             response = requests.get(
#                 f"{self.base_url}/approximateTerm.json?term={drug_name}&maxEntries=1", 
#                 timeout=5
#             )
#             if response.status_code == 200:
#                 data = response.json()
#                 if "approximateGroup" in data and "candidate" in data["approximateGroup"]:
#                     candidates = data["approximateGroup"]["candidate"]
#                     if candidates:
#                         return candidates[0]["rxcui"]
#         except Exception as e:
#             logger.error(f"RxNav API Error fetching RxCUI for {drug_name}: {e}")
#         return None

#     def check_drug_list_interactions(self, drug_names: List[str]) -> List[str]:
#         """
#         Dynamically cross-references any list of drugs against each other 
#         using the NIH's strict interaction matrix.
#         """
#         rxcuis = []
        
#         # 1. Convert all text names to precise IDs
#         for name in drug_names:
#             rxcui = self.get_drug_rxcui(name)
#             if rxcui:
#                 rxcuis.append(rxcui)
        
#         alerts = []
#         # Requires at least 2 valid IDs to check for an interaction
#         if len(rxcuis) < 2:
#             return alerts
            
#         try:
#             # 2. Query the exact interactions between these specific drugs
#             rxcui_string = "+".join(rxcuis)
#             url = f"{self.base_url}/interaction/list.json?rxcuis={rxcui_string}"
#             response = requests.get(url, timeout=5)
            
#             if response.status_code == 200:
#                 data = response.json()
#                 if "fullInteractionTypeGroup" in data:
#                     for group in data["fullInteractionTypeGroup"]:
#                         for interaction_type in group.get("fullInteractionType", []):
#                             for pair in interaction_type.get("interactionPair", []):
#                                 desc = pair.get('description', 'Clinical interaction detected.')
#                                 alerts.append(f"[NIH LIVE ALERT] {desc}")
#         except Exception as e:
#             logger.error(f"RxNav API Error checking interactions for {rxcui_string}: {e}")
            
#         return list(set(alerts))

# rxnav_client = RxNavIntegration()

# import requests
# import logging
# from typing import List

# logger = logging.getLogger(__name__)

# class RxNavIntegration:
#     def __init__(self):
#         self.base_url = "https://rxnav.nlm.nih.gov/REST"

#     def get_drug_rxcui(self, drug_name: str) -> str:
#         """Translates the drug name into the NIH ID, trying precise first, then fuzzy."""
#         try:
#             clean_name = drug_name.strip().split()[0]
#             res = requests.get(f"{self.base_url}/rxcui.json?name={clean_name}", timeout=5)
#             if res.status_code == 200:
#                 data = res.json()
#                 if "idGroup" in data and "rxnormId" in data["idGroup"]:
#                     return data["idGroup"]["rxnormId"][0]
            
#             # Fallback to fuzzy matching if exact name fails
#             res = requests.get(f"{self.base_url}/approximateTerm.json?term={drug_name}&maxEntries=1", timeout=5)
#             if res.status_code == 200:
#                 data = res.json()
#                 if "approximateGroup" in data and "candidate" in data["approximateGroup"]:
#                     return data["approximateGroup"]["candidate"][0]["rxcui"]
#         except Exception as e:
#             logger.error(f"RxNav API Error fetching RxCUI for {drug_name}: {e}")
#         return None

#     def check_drug_list_interactions(self, drug_names: List[str]) -> List[str]:
#         """Dual-Engine Verification: Tries strict matrix first, falls back to text scanning."""
#         rxcuis = []
#         valid_drug_names = []
        
#         for name in drug_names:
#             rxcui = self.get_drug_rxcui(name)
#             if rxcui:
#                 rxcuis.append(rxcui)
#                 # Keep track of the actual names for the text-scanner fallback
#                 valid_drug_names.append(name.lower())
        
#         alerts = []
#         if len(rxcuis) < 2:
#             return alerts
            
#         # ENGINE 1: The Strict NIH Matrix (What I gave you last time)
#         try:
#             rxcui_string = "+".join(rxcuis)
#             url = f"{self.base_url}/interaction/list.json?rxcuis={rxcui_string}"
#             response = requests.get(url, timeout=5)
#             if response.status_code == 200:
#                 data = response.json()
#                 if "fullInteractionTypeGroup" in data:
#                     for group in data["fullInteractionTypeGroup"]:
#                         for itype in group.get("fullInteractionType", []):
#                             for pair in itype.get("interactionPair", []):
#                                 alerts.append(f"[NIH LIVE ALERT] {pair.get('description', '')}")
#         except Exception as e:
#             logger.error(f"RxNav Engine 1 Error: {e}")

#         # ENGINE 2: The Universal Text-Scanner (The safety net that caught it earlier)
#         # If the strict matrix missed the interaction, we force it to check the raw text warnings.
#         if not alerts:
#             for rxcui in rxcuis:
#                 try:
#                     url = f"{self.base_url}/interaction/interaction.json?rxcui={rxcui}&sources=DrugBank"
#                     response = requests.get(url, timeout=5)
#                     if response.status_code == 200:
#                         data = response.json()
#                         if "interactionTypeGroup" in data:
#                             for group in data["interactionTypeGroup"]:
#                                 for itype in group.get("interactionType", []):
#                                     for pair in itype.get("interactionPair", []):
#                                         desc = pair.get('description', '')
                                        
#                                         # Check if any OTHER drug in the patient's list is mentioned
#                                         for drug in valid_drug_names:
#                                             # Avoid comparing the drug to itself
#                                             if drug in desc.lower() and not any(drug in alert.lower() for alert in alerts):
#                                                 alerts.append(f"[NIH LIVE ALERT] {desc}")
#                 except Exception as e:
#                     logger.error(f"RxNav Engine 2 Error: {e}")
                    
#         return list(set(alerts))

# rxnav_client = RxNavIntegration()


"""
backend/app/core/rxnav_api.py - RxNav is used ONLY to turn brand names / salts / misspellings into the plain
ingredient name ("Inderal" -> "propranolol").
 
WHY THE OLD RxNav INTERACTION CHECK NEVER WORKED
  NLM discontinued the RxNav Drug-Drug Interaction API on January 2, 2024 (official RxNav FAQ), so
  /interaction/list.json no longer returns interaction data. Interactions now come from DDInter inside Neo4j.
 
Safety rules: on any problem the original name is returned unchanged (never a wrong guess); successful lookups
are cached; after a network failure RxNav is skipped for 2 minutes so requests are not slowed down.
"""
import logging
import time
from typing import List
 
import requests
 
logger = logging.getLogger(__name__)
 
BASE_URL = "https://rxnav.nlm.nih.gov/REST"
MIN_SCORE = 75.0
TIMEOUT = 3
_cache = {}
_down_until = 0.0
 
 
def _normalize(name: str) -> str:
    global _down_until
    clean = (name or "").strip().lower()
    if len(clean) < 3:
        return clean
    if clean in _cache:
        return _cache[clean]
    if time.time() < _down_until:
        return clean
    try:
        r = requests.get(f"{BASE_URL}/approximateTerm.json", params={"term": clean, "maxEntries": 1}, timeout=TIMEOUT)
        r.raise_for_status()
        cands = r.json().get("approximateGroup", {}).get("candidate", [])
        result = clean
        if cands and float(cands[0].get("score", 0)) >= MIN_SCORE:
            rxcui = cands[0]["rxcui"]
            r = requests.get(f"{BASE_URL}/rxcui/{rxcui}/related.json", params={"tty": "IN"}, timeout=TIMEOUT)
            r.raise_for_status()
            groups = r.json().get("relatedGroup", {}).get("conceptGroup", []) or []
            ings = sorted({p["name"].strip().lower() for g in groups for p in (g.get("conceptProperties") or [])})
            if len(ings) == 1:                       # none or several (combination product): keep original wording
                result = ings[0]
        _cache[clean] = result
        return result
    except Exception as e:
        _down_until = time.time() + 120
        logger.warning("RxNav unavailable (%s); skipping it for 2 minutes", str(e)[:100])
        return clean
 
 
class RxNavIntegration:
    def normalize_drug(self, name: str) -> str:
        return _normalize(name)
 
    def normalize_list(self, names: List[str]) -> List[str]:
        out = []
        for n in names or []:
            nn = _normalize(str(n))
            if nn and nn not in out:
                out.append(nn)
        return out
 
 
rxnav_client = RxNavIntegration()
 