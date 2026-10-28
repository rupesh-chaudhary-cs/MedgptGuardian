# import os
# import json
# import logging
# import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()
# logger = logging.getLogger(__name__)

# class ClinicalEntityExtractor:
#     def __init__(self):
#         api_key = os.getenv("GEMINI_API_KEY")
#         if not api_key:
#             logger.warning("WARNING: GEMINI_API_KEY is missing from environment variables.")
        
#         genai.configure(api_key=api_key)
#         # Using reliable flash model for fast and precise JSON extraction
#         self.model_name = "gemini-3.5-flash-lite"
        
#         self.model = genai.GenerativeModel(
#             model_name=self.model_name,
#             system_instruction=(
#                 "You are a precise clinical entity extraction engine. "
#                 "Your sole job is to parse patient background contexts and proposed treatments into strict, structured JSON arrays."
#             )
#         )

#     def extract_clinical_entities(self, patient_context: str, proposed_treatment: str) -> dict:
#         """
#         Extracts clinical entities into strict JSON lists matching the 5D Neo4j graph dimensions.
#         """
#         prompt = f"""
#         Analyze the following patient context and proposed clinical treatment, then extract all relevant clinical entities.
        
#         PATIENT CONTEXT:
#         {patient_context}
        
#         PROPOSED TREATMENT / AI RESPONSE:
#         {proposed_treatment}
        
#         Return ONLY a valid JSON object with these exact keys:
#         - "patient_diseases": list of strings (e.g., diseases, conditions like Hypertension, Asthma)
#         - "patient_allergies": list of strings (e.g., drug or environmental allergies)
#         - "patient_factors": list of strings (e.g., risk factors, demographics, smoking status)
#         - "patient_labs": list of strings (e.g., lab values, vitals abnormalities)
#         - "proposed_drugs": list of strings (e.g., medications suggested in the treatment like Propranolol, Aspirin)
        
#         Ensure all values are extracted accurately from the text. If a category has no entities, return an empty list [].
#         """

#         try:
#             # Temperature = 0.0 forces deterministic extraction without hallucinations
#             response = self.model.generate_content(
#                 prompt,
#                 generation_config=genai.types.GenerationConfig(
#                     temperature=0.0,
#                     response_mime_type="application/json"
#                 )
#             )
            
#             # Parse the JSON output safely
#             raw_text = response.text.strip()
            
#             # Strip markdown code fences if the model wrapped the JSON in them
#             if raw_text.startswith("```json"):
#                 raw_text = raw_text[7:]
#             if raw_text.startswith("```"):
#                 raw_text = raw_text[3:]
#             if raw_text.endswith("```"):
#                 raw_text = raw_text[:-3]
#             raw_text = raw_text.strip()

#             parsed_data = json.loads(raw_text)
            
#             # Ensure all required keys exist with default empty lists if missing
#             return {
#                 "patient_diseases": parsed_data.get("patient_diseases", []),
#                 "patient_allergies": parsed_data.get("patient_allergies", []),
#                 "patient_factors": parsed_data.get("patient_factors", []),
#                 "patient_labs": parsed_data.get("patient_labs", []),
#                 "proposed_drugs": parsed_data.get("proposed_drugs", [])
#             }
            
#         except Exception as e:
#             logger.error(f"Entity Extraction Error: {str(e)}")
#             # Fallback empty structure to prevent 500 API crashes
#             return {
#                 "patient_diseases": [],
#                 "patient_allergies": [],
#                 "patient_factors": [],
#                 "patient_labs": [],
#                 "proposed_drugs": []
#             }

# # Singleton instance for modular import
# entity_extractor = ClinicalEntityExtractor()


import os
import json
import logging
import difflib  # Built-in library for spelling correction and fuzzy matching
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# =====================================================================
# NEO4J MASTER DICTIONARY
# Add the exact names from your 5-file database here. 
# The fuzzy matcher will auto-correct any typos to these exact strings.
# =====================================================================
VALID_DISEASES = [
    "Asthma", "Hypertension", "Diabetes", "Coronary Heart Disease", 
    "Orthostatic Hypotension", "High Blood Pressure"
]
VALID_DRUGS = [
    "Propranolol", "Aspirin", "Metformin", "Lisinopril", "Atorvastatin", 
    "Warfarin", "Diuretics", "Beta Blockers", "ACE Inhibitors"
]

class ClinicalEntityExtractor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("WARNING: GEMINI_API_KEY is missing from environment variables.")
            
        genai.configure(api_key=api_key)
        self.model_name = "gemini-3.5-flash-lite"
        
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=(
                "You are a precise clinical entity extraction engine. "
                "Your sole job is to parse patient background contexts and proposed treatments into strict JSON arrays."
            )
        )

    def extract_clinical_entities(self, patient_context: str, proposed_treatment: str) -> dict:
        prompt = f"""
        Analyze the following patient context and proposed clinical treatment, then extract all relevant clinical entities.
        Map common abbreviations to their full clinical terms if possible.
        
        PATIENT CONTEXT:
        {patient_context}
        
        PROPOSED TREATMENT / AI RESPONSE:
        {proposed_treatment}
        
        Return ONLY a valid JSON object with these exact keys:
        - "patient_diseases": list of strings
        - "patient_allergies": list of strings
        - "patient_factors": list of strings
        - "patient_labs": list of strings
        - "proposed_drugs": list of strings
        """

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,
                    response_mime_type="application/json"
                )
            )
            
            # Clean JSON formatting
            raw_text = response.text.strip()
            if raw_text.startswith("```json"): raw_text = raw_text[7:]
            if raw_text.startswith("```"): raw_text = raw_text[3:]
            if raw_text.endswith("```"): raw_text = raw_text[:-3]
            
            parsed_data = json.loads(raw_text.strip())
            
            # --- THE FUZZY MATCHER & NORMALIZER ---
            def fuzzy_match(item_list, master_list):
                if not isinstance(item_list, list): return []
                
                matched_items = []
                for item in item_list:
                    # Standardize casing first
                    item_str = str(item).strip().title()
                    
                    # 1. Exact match check
                    if item_str in master_list:
                        matched_items.append(item_str)
                        continue
                        
                    # 2. Typo & Partial Match Check (cutoff=0.5 allows for severe misspellings like "asth")
                    matches = difflib.get_close_matches(item_str, master_list, n=1, cutoff=0.5)
                    if matches:
                        matched_items.append(matches[0])  # Use the perfect database string
                    else:
                        matched_items.append(item_str)    # Keep original if no match is found
                        
                # Return unique items only
                return list(set(matched_items))
            
            return {
                "patient_diseases": fuzzy_match(parsed_data.get("patient_diseases", []), VALID_DISEASES),
                "patient_allergies": [str(x).title().strip() for x in parsed_data.get("patient_allergies", [])],
                "patient_factors": [str(x).title().strip() for x in parsed_data.get("patient_factors", [])],
                "patient_labs": [str(x).title().strip() for x in parsed_data.get("patient_labs", [])],
                "proposed_drugs": fuzzy_match(parsed_data.get("proposed_drugs", []), VALID_DRUGS)
            }
            
        except Exception as e:
            logger.error(f"Entity Extraction Error: {str(e)}")
            return {
                "patient_diseases": [], "patient_allergies": [], 
                "patient_factors": [], "patient_labs": [], "proposed_drugs": []
            }

entity_extractor = ClinicalEntityExtractor()