# import os
# import logging
# import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()
# logger = logging.getLogger(__name__)

# class LLMError(Exception):
#     pass

# class GeminiMedicalSynthesizer:
#     def __init__(self):
#         api_key = os.getenv("GEMINI_API_KEY")
#         if not api_key:
#             logger.warning("WARNING: GEMINI_API_KEY is missing from environment variables.")

#         # Initialize Google AI Studio Client
#         genai.configure(api_key=api_key)

#         # UPDATED FIX: Google's current 2026 active model
#         self.model_name = "gemini-3.5-flash-lite"     #*"gemini-3.8-flash"*#

#         # self.model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

#         # System instructions set the strict clinical personality and length limits
#         self.model = genai.GenerativeModel(
#             model_name=self.model_name,
#             system_instruction=(
#                 "You are MedGPT Guardian, an advanced Clinical Decision Support System. "
#                 "Your job is to synthesize the provided NIH MedQuAD guidelines to answer the clinical inquiry.\n\n"
#                 "STRICT RULES:\n"
#                 "1. Be extremely concise and direct. Doctors need fast answers. Keep it under 150 words if possible.\n"
#                 "2. Ground your entire response STRICTLY in the provided NIH evidence.\n"
#                 "3. Use short, readable bullet points instead of massive tables or long paragraphs.\n"
#                 "4. Maintain an objective, professional clinical tone."
#             )
#         )

#     def synthesize_response(self, patient_context: str, question: str, retrieved_evidence: str) -> str:
#         """Synthesizes RAG evidence and patient context into an expert clinical support response."""

#         prompt = (
#             f"SANITIZED PATIENT CONTEXT: {patient_context}\n"
#             f"CLINICAL INQUIRY: {question}\n\n"
#             f"RETRIEVED NIH GROUND-TRUTH EVIDENCE:\n{retrieved_evidence}\n\n"
#             "Provide a concise, evidence-based clinical evaluation:"
#         )

#         try:
#             # Low temperature reduces hallucinations in clinical text
#             response = self.model.generate_content(
#                 prompt,
#                 generation_config=genai.types.GenerationConfig(temperature=0.1)
#             )
#             return response.text
#         except Exception as e:
#             logger.error(f"Gemini LLM Synthesis Error: {str(e)}")
#             return f"Error during AI clinical synthesis: {str(e)}"

# # Instantiate a singleton handler for reuse
# llm_synthesizer = GeminiMedicalSynthesizer()

# import json
# import os

# # Define the models the new agent expects
# FAST_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
# GEN_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# def generate_json(prompt: str, system: str = "", model: str = FAST_MODEL) -> dict:
#     """Forces the LLM to return strict JSON for the Med-Reflect Agent."""
#     try:
#         import google.generativeai as genai
#         m = genai.GenerativeModel(model_name=model, system_instruction=system)
#         response = m.generate_content(
#             prompt, 
#             generation_config=genai.types.GenerationConfig(
#                 temperature=0.1, 
#                 response_mime_type="application/json"
#             )
#         )
#         return json.loads(response.text)
#     except Exception as e:
#         raise LLMError(f"JSON generation failed: {str(e)}")

# print("\n🔥 BINGO! PYTHON IS READING THE NEW LLM.PY FILE! 🔥\n")



import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Define the models the new agent expects
FAST_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEN_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

class LLMError(Exception):
    pass

def generate_json(prompt: str, system: str = "", model: str = FAST_MODEL) -> dict:
    """Forces the LLM to return strict JSON for the Med-Reflect Agent."""
    try:
        m = genai.GenerativeModel(model_name=model, system_instruction=system)
        response = m.generate_content(
            prompt, 
            generation_config=genai.types.GenerationConfig(
                temperature=0.1, 
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"JSON generation failed: {e}")
        raise LLMError(f"JSON generation failed: {str(e)}")

def generate_text(prompt: str, system: str = "", model: str = GEN_MODEL, temperature: float = 0.3, max_tokens: int = 1200) -> str:
    """Forces the LLM to return standard text/Markdown for the final protocol."""
    try:
        m = genai.GenerativeModel(model_name=model, system_instruction=system)
        response = m.generate_content(
            prompt, 
            generation_config=genai.types.GenerationConfig(
                temperature=temperature, 
                max_output_tokens=max_tokens
            )
        )
        return response.text
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise LLMError(f"Text generation failed: {str(e)}")