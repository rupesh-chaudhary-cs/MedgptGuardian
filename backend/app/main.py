# # import torch  # Prevents Windows DLL memory crashes
# # from fastapi import FastAPI, HTTPException, Request
# # from fastapi.middleware.cors import CORSMiddleware
# # from pydantic import BaseModel, Field
# # import time

# # from app.core.config import settings
# # from app.core.security import PrivacyGateway, logger
# # from app.core.rag import evidence_engine

# # app = FastAPI(
# #     title=settings.PROJECT_NAME,
# #     version=settings.VERSION,
# #     description="Risk-Adaptive Clinical Verification Engine for AI Safety"
# # )

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=settings.BACKEND_CORS_ORIGINS,
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # class ClinicalQuery(BaseModel):
# #     patient_context: str = Field(..., min_length=5, description="EHR or patient background context")
# #     question: str = Field(..., min_length=5, description="The clinical question to resolve")

# # class GatewayResponse(BaseModel):
# #     status: str
# #     processing_time_ms: float
# #     phi_intercepted: bool
# #     safe_context: str
# #     safe_question: str
# #     retrieved_evidence: str  # Phase 2: The RAG Output

# # @app.middleware("http")
# # async def add_process_time_header(request: Request, call_next):
# #     start_time = time.time()
# #     response = await call_next(request)
# #     process_time = time.time() - start_time
# #     response.headers["X-Process-Time"] = str(process_time)
# #     return response

# # @app.get("/health")
# # async def health_check():
# #     return {"status": "MedGPT Engine Operational", "version": settings.VERSION}

# # @app.post(f"{settings.API_V1_STR}/verify", response_model=GatewayResponse)
# # async def process_clinical_query(query: ClinicalQuery):
# #     start_time = time.time()
    
# #     try:
# #         # Phase 1: Zero-Trust Data Scrubbing
# #         safe_context, context_phi = PrivacyGateway.scrub_phi(query.patient_context)
# #         safe_question, question_phi = PrivacyGateway.scrub_phi(query.question)
        
# #         # Phase 2: RAG Evidence Retrieval
# #         retrieved_rule = evidence_engine.retrieve_guideline(safe_question)
        
# #         processing_time_ms = round((time.time() - start_time) * 1000, 2)
        
# #         return GatewayResponse(
# #             status="EVIDENCE_RETRIEVED",
# #             processing_time_ms=processing_time_ms,
# #             phi_intercepted=(context_phi or question_phi),
# #             safe_context=safe_context,
# #             safe_question=safe_question,
# #             retrieved_evidence=retrieved_rule
# #         )
        
# #     except Exception as e:
# #         logger.error(f"Critical System Failure: {str(e)}")
# #         raise HTTPException(status_code=500, detail="Internal Guardian Engine Failure")



# # from fastapi import FastAPI, HTTPException
# # from pydantic import BaseModel, Field
# # from typing import Optional
# # from app.core.rag import evidence_engine

# # app = FastAPI(title="MedGPT Guardian API", version="1.0.0")

# # # 1. Flexible Pydantic Schema that supports both test formats
# # class ClinicalQuery(BaseModel):
# #     query: Optional[str] = Field(None, description="General single-string search query")
# #     patient_context: Optional[str] = Field("General patient", description="Patient background context")
# #     question: Optional[str] = Field(None, description="Clinical question")

# # @app.get("/")
# # def read_root():
# #     return {"status": "MedGPT Guardian Backend is Online"}

# # @app.get("/health")
# # def health_check():
# #     return {"status": "healthy", "database": "NIH MedQuAD ChromaDB Connected"}

# # # 2. Endpoint handling both /query and your /api/v1/verify structure
# # @app.post("/api/v1/verify")
# # def verify_clinical_query(request: ClinicalQuery):
# #     try:
# #         # Determine which field the user passed
# #         search_target = request.question or request.query
        
# #         if not search_target:
# #             raise HTTPException(status_code=400, detail="Either 'query' or 'question' must be provided.")

# #         # Query your 5,000-record NIH MedQuAD database
# #         retrieved_text = evidence_engine.retrieve_guideline(search_target)
        
# #         return {
# #             "status": "success",
# #             "processing_time_ms": 15,
# #             "phi_intercepted": True,
# #             "safe_context": request.patient_context,
# #             "safe_question": search_target,
# #             "retrieved_evidence": retrieved_text
# #         }
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=str(e))

# import re
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from typing import Optional
# from app.core.rag import evidence_engine

# app = FastAPI(title="MedGPT Guardian API", version="1.0.0")

# # Enable CORS for React frontend integration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# def scrub_phi(text: str) -> str:
#     """Phase 1: Zero-Trust PHI Scrubber for Names, Ages, and Phone Numbers"""
#     if not text:
#         return text
    
#     # 1. Redact Phone Numbers (e.g., 555-0199)
#     text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[REDACTED_PHONE]', text)
    
#     # 2. Redact Ages (e.g., 45 years old)
#     text = re.sub(r'\b\d{1,3}\s*(?:years?\s*old|yrs?\s*old)\b', '[REDACTED_AGE]', text, flags=re.IGNORECASE)
    
#     # 3. Redact Common Names / Identifiers (e.g., John Doe)
#     text = re.sub(r'\b(John\s+Doe)\b', '[REDACTED_NAME]', text, flags=re.IGNORECASE)
    
#     return text

# # Flexible Pydantic Schema supporting BOTH formats seamlessly
# class ClinicalQuery(BaseModel):
#     query: Optional[str] = Field(None, description="Simple single-string query")
#     patient_context: Optional[str] = Field("General patient context", description="Patient background info / PHI notes")
#     question: Optional[str] = Field(None, description="Detailed clinical question")

# @app.get("/")
# def read_root():
#     return {"status": "MedGPT Guardian Backend is Online"}

# @app.get("/health")
# def health_check():
#     return {"status": "healthy", "database": "NIH MedQuAD ChromaDB Connected"}

# @app.post("/api/v1/verify")
# def verify_clinical_query(request: ClinicalQuery):
#     try:
#         # Flexible handling: accepts either 'question' or 'query'
#         search_target = request.question or request.query
#         if not search_target:
#             raise HTTPException(status_code=400, detail="Either 'query' or 'question' must be provided.")

#         # Phase 1: Apply Zero-Trust PHI Scrubbing
#         scrubbed_context = scrub_phi(request.patient_context)
#         scrubbed_query = scrub_phi(search_target)

#         # Phase 2: Query the 5,000-record NIH MedQuAD database using the safe scrubbed text
#         retrieved_text = evidence_engine.retrieve_guideline(scrubbed_query)

#         return {
#             "status": "success",
#             "processing_time_ms": 15,
#             "phi_intercepted": True,
#             "safe_context": scrubbed_context,
#             "safe_question": scrubbed_query,
#             "retrieved_evidence": retrieved_text
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



# # /*in phase 1 we have encrypted the personal data and in phase 2 we have implemented the rag pipeline and vector database*/


#phase3 main.py code containing the combination of all three phases:

# import re
# import time
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from typing import Optional

# from app.core.rag import evidence_engine
# from app.core.llm import llm_synthesizer  # Phase 3: Groq Llama 3 70B Brain

# app = FastAPI(
#     title="MedGPT Guardian API", 
#     version="1.0.0",
#     description="Risk-Adaptive Clinical Verification Engine for AI Safety"
# )

# # Enable CORS for React frontend integration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# def scrub_phi(text: str) -> tuple[str, bool]:
#     """Phase 1: Zero-Trust PHI Scrubber for Names, Ages, and Phone Numbers"""
#     if not text:
#         return text, False
    
#     original_text = text
    
#     # 1. Redact Phone Numbers (supports 7-digit and 10-digit formats)
#     text = re.sub(r'\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b|\b\d{3}[-.\s]?\d{4}\b', '[REDACTED_PHONE]', text)
    
#     # 2. Redact Ages (e.g., 45 years old)
#     text = re.sub(r'\b\d{1,3}\s*(?:years?\s*old|yrs?\s*old)\b', '[REDACTED_AGE]', text, flags=re.IGNORECASE)
    
#     # 3. Redact Common Names / Identifiers (e.g., John Doe)
#     text = re.sub(r'\b(John\s+Doe)\b', '[REDACTED_NAME]', text, flags=re.IGNORECASE)
    
#     phi_detected = (text != original_text)
#     return text, phi_detected

# # Flexible Pydantic Schema supporting BOTH formats seamlessly
# class ClinicalQuery(BaseModel):
#     query: Optional[str] = Field(None, description="Simple single-string search query")
#     patient_context: Optional[str] = Field("General patient context", description="Patient background info / PHI notes")
#     question: Optional[str] = Field(None, description="Detailed clinical question")

# @app.get("/")
# def read_root():
#     return {"status": "MedGPT Guardian Backend is Online"}

# @app.get("/health")
# def health_check():
#     return {
#         "status": "healthy",
#         "database": "NIH MedQuAD ChromaDB Connected (5,000 records)",
#         "security": "Phase 1 PHI Scrubber Active",
#         "llm": "Phase 3 Google Gemini 2.0 Flash Active"
#     }

# @app.post("/api/v1/verify")
# def verify_clinical_query(request: ClinicalQuery):
#     start_time = time.time()
#     try:
#         # Flexible handling: accepts either 'question' or 'query'
#         search_target = request.question or request.query
#         if not search_target:
#             raise HTTPException(status_code=400, detail="Either 'query' or 'question' must be provided.")

#         context_input = request.patient_context or "General patient context"

#         # Phase 1: Apply Zero-Trust PHI Scrubbing
#         safe_context, context_phi = scrub_phi(context_input)
#         safe_question, question_phi = scrub_phi(search_target)

#         # Phase 2: Query the 5,000-record NIH MedQuAD database via RAG engine
#         retrieved_evidence = evidence_engine.retrieve_guideline(safe_question)

#         # Phase 3: Synthesize conversational clinical response via Groq Llama 3 70B
#         ai_clinical_response = llm_synthesizer.synthesize_response(
#             patient_context=safe_context,
#             question=safe_question,
#             retrieved_evidence=retrieved_evidence
#         )

#         processing_time_ms = round((time.time() - start_time) * 1000, 2)

#         return {
#             "status": "success",
#             "processing_time_ms": processing_time_ms,
#             "phi_intercepted": (context_phi or question_phi),
#             "safe_context": safe_context,
#             "safe_question": safe_question,
#             "retrieved_evidence": retrieved_evidence,
#             "ai_clinical_response": ai_clinical_response
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



# import re
# import time
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from typing import Optional

# from app.core.rag import evidence_engine
# from app.core.llm import llm_synthesizer  # Phase 3: LLM Brain

# # --- PHASE 4 IMPORTS ---
# from app.core.extractor import entity_extractor
# from app.core.graph import medical_graph

# app = FastAPI(
#     title="MedGPT Guardian API", 
#     version="1.0.0",
#     description="Risk-Adaptive Clinical Verification Engine for AI Safety & 5D Knowledge Graph"
# )

# # Enable CORS for React frontend integration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# def scrub_phi(text: str) -> tuple[str, bool]:
#     """Phase 1: Zero-Trust PHI Scrubber for Names, Ages, and Phone Numbers"""
#     if not text:
#         return text, False
    
#     original_text = text
    
#     # 1. Redact Phone Numbers (supports 7-digit and 10-digit formats)
#     text = re.sub(r'\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b|\b\d{3}[-.\s]?\d{4}\b', '[REDACTED_PHONE]', text)
    
#     # 2. Redact Ages (e.g., 45 years old)
#     text = re.sub(r'\b\d{1,3}\s*(?:years?\s*old|yrs?\s*old)\b', '[REDACTED_AGE]', text, flags=re.IGNORECASE)
    
#     # 3. Redact Common Names / Identifiers (e.g., John Doe)
#     text = re.sub(r'\b(John\s+Doe)\b', '[REDACTED_NAME]', text, flags=re.IGNORECASE)
    
#     phi_detected = (text != original_text)
#     return text, phi_detected

# # Flexible Pydantic Schema supporting BOTH formats seamlessly
# class ClinicalQuery(BaseModel):
#     query: Optional[str] = Field(None, description="Simple single-string search query")
#     patient_context: Optional[str] = Field("General patient context", description="Patient background info / PHI notes")
#     question: Optional[str] = Field(None, description="Detailed clinical question")

# @app.get("/")
# def read_root():
#     return {"status": "MedGPT Guardian Backend is Online"}

# @app.get("/health")
# def health_check():
#     return {
#         "status": "healthy",
#         "database": "NIH MedQuAD ChromaDB & Neo4j 5D Connected",
#         "security": "Phase 1 PHI Scrubber Active",
#         "llm": "Phase 3 Gemini Flash Active",
#         "graph": "Phase 4 Multi-Dimensional Knowledge Graph Active"
#     }

# @app.post("/api/v1/verify")
# def verify_clinical_query(request: ClinicalQuery):
#     start_time = time.time()
#     try:
#         # Flexible handling: accepts either 'question' or 'query'
#         search_target = request.question or request.query
#         if not search_target:
#             raise HTTPException(status_code=400, detail="Either 'query' or 'question' must be provided.")

#         context_input = request.patient_context or "General patient context"

#         # Phase 1: Apply Zero-Trust PHI Scrubbing
#         safe_context, context_phi = scrub_phi(context_input)
#         safe_question, question_phi = scrub_phi(search_target)

#         # Phase 2: Query the 5,000-record NIH MedQuAD database via RAG engine
#         retrieved_evidence = evidence_engine.retrieve_guideline(safe_question)

#         # Phase 3: Synthesize conversational clinical response
#         ai_clinical_response = llm_synthesizer.synthesize_response(
#             patient_context=safe_context,
#             question=safe_question,
#             retrieved_evidence=retrieved_evidence
#         )

#         # ==========================================
#         # PHASE 4: AI Extractor Bridge
#         # ==========================================
#         # Forces Gemini (temperature=0.0) to parse text into strict JSON entity lists
#         entities = entity_extractor.extract_clinical_entities(
#             patient_context=safe_context,
#             proposed_treatment=ai_clinical_response
#         )
        
#         # ==========================================
#         # PHASE 4: 5-Dimensional Neo4j Graph Query
#         # ==========================================
#         # Checks extracted entities simultaneously across Drug-Disease, Drug-Drug,
#         # Drug-Allergy, Drug-Patient Factor, and Drug-Lab dimensions.
#         safety_warnings = medical_graph.verify_clinical_safety(
#             patient_diseases=entities.get("patient_diseases", []),
#             patient_allergies=entities.get("patient_allergies", []),
#             patient_factors=entities.get("patient_factors", []),
#             patient_labs=entities.get("patient_labs", []),
#             proposed_drugs=entities.get("proposed_drugs", [])
#         )

#         processing_time_ms = round((time.time() - start_time) * 1000, 2)

#         return {
#             "status": "success",
#             "processing_time_ms": processing_time_ms,
#             "phi_intercepted": (context_phi or question_phi),
#             "safe_context": safe_context,
#             "safe_question": safe_question,
#             "retrieved_evidence": retrieved_evidence,
#             "ai_clinical_response": ai_clinical_response,
#             "extracted_entities": entities,
#             "phase_4_safety_alerts": safety_warnings,
#             "is_safe": len(safety_warnings) == 0
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



# import re
# import time
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from typing import Optional

# from app.core.rag import evidence_engine
# from app.core.llm import llm_synthesizer  # Phase 3: LLM Brain

# # --- PHASE 4 IMPORTS ---
# from app.core.extractor import entity_extractor
# from app.core.graph import medical_graph
# from app.core.rxnav_api import rxnav_client  # <-- NEW: Live NIH API

# app = FastAPI(
#     title="MedGPT Guardian API", 
#     version="1.0.0",
#     description="Risk-Adaptive Clinical Verification Engine for AI Safety & 5D Knowledge Graph"
# )

# # Enable CORS for React frontend integration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# def scrub_phi(text: str) -> tuple[str, bool]:
#     """Phase 1: Zero-Trust PHI Scrubber for Names, Ages, and Phone Numbers"""
#     if not text:
#         return text, False
    
#     original_text = text
    
#     # 1. Redact Phone Numbers (supports 7-digit and 10-digit formats)
#     text = re.sub(r'\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b|\b\d{3}[-.\s]?\d{4}\b', '[REDACTED_PHONE]', text)
    
#     # 2. Redact Ages (e.g., 45 years old)
#     text = re.sub(r'\b\d{1,3}\s*(?:years?\s*old|yrs?\s*old)\b', '[REDACTED_AGE]', text, flags=re.IGNORECASE)
    
#     # 3. Redact Common Names / Identifiers (e.g., John Doe)
#     text = re.sub(r'\b(John\s+Doe)\b', '[REDACTED_NAME]', text, flags=re.IGNORECASE)
    
#     phi_detected = (text != original_text)
#     return text, phi_detected

# # Flexible Pydantic Schema supporting BOTH formats seamlessly
# class ClinicalQuery(BaseModel):
#     query: Optional[str] = Field(None, description="Simple single-string search query")
#     patient_context: Optional[str] = Field("General patient context", description="Patient background info / PHI notes")
#     question: Optional[str] = Field(None, description="Detailed clinical question")

# @app.get("/")
# def read_root():
#     return {"status": "MedGPT Guardian Backend is Online"}

# @app.get("/health")
# def health_check():
#     return {
#         "status": "healthy",
#         "database": "NIH MedQuAD ChromaDB & Neo4j 5D Connected",
#         "security": "Phase 1 PHI Scrubber Active",
#         "llm": "Phase 3 Gemini Flash Active",
#         "graph": "Phase 4 Multi-Dimensional Knowledge Graph & Live NIH API Active"
#     }

# @app.post("/api/v1/verify")
# def verify_clinical_query(request: ClinicalQuery):
#     start_time = time.time()
#     try:
#         # Flexible handling: accepts either 'question' or 'query'
#         search_target = request.question or request.query
#         if not search_target:
#             raise HTTPException(status_code=400, detail="Either 'query' or 'question' must be provided.")

#         context_input = request.patient_context or "General patient context"

#         # Phase 1: Apply Zero-Trust PHI Scrubbing
#         safe_context, context_phi = scrub_phi(context_input)
#         safe_question, question_phi = scrub_phi(search_target)

#         # Phase 2: Query the 5,000-record NIH MedQuAD database via RAG engine
#         retrieved_evidence = evidence_engine.retrieve_guideline(safe_question)

#         # Phase 3: Synthesize conversational clinical response
#         ai_clinical_response = llm_synthesizer.synthesize_response(
#             patient_context=safe_context,
#             question=safe_question,
#             retrieved_evidence=retrieved_evidence
#         )

#         # ==========================================
#         # PHASE 4: AI Extractor Bridge
#         # ==========================================
#         # Forces Gemini (temperature=0.0) to parse text into strict JSON entity lists
#         entities = entity_extractor.extract_clinical_entities(
#             patient_context=safe_context,
#             proposed_treatment=ai_clinical_response
#         )
        
#         # ==========================================
#         # PHASE 4: Hybrid Safety Verification
#         # ==========================================
        
#         # Step A: Local 5-Dimensional Neo4j Graph Query (PrimeKG)
#         local_safety_warnings = medical_graph.verify_clinical_safety(
#             patient_diseases=entities.get("patient_diseases", []),
#             patient_allergies=entities.get("patient_allergies", []),
#             patient_factors=entities.get("patient_factors", []),
#             patient_labs=entities.get("patient_labs", []),
#             proposed_drugs=entities.get("proposed_drugs", [])
#         )

#         # Step B: Live NIH RxNav Database Query
#         live_api_alerts = []
#         proposed_drugs = entities.get("proposed_drugs", [])
#         if proposed_drugs:
#             for drug in proposed_drugs:
#                 # Queries the government API for each extracted drug
#                 api_results = rxnav_client.check_live_interactions(drug)
#                 live_api_alerts.extend(api_results)

#         # Step C: Combine into a single Master Alert List
#         master_safety_warnings = local_safety_warnings + live_api_alerts

#         processing_time_ms = round((time.time() - start_time) * 1000, 2)

#         return {
#             "status": "success",
#             "processing_time_ms": processing_time_ms,
#             "phi_intercepted": (context_phi or question_phi),
#             "safe_context": safe_context,
#             "safe_question": safe_question,
#             "retrieved_evidence": retrieved_evidence,
#             "ai_clinical_response": ai_clinical_response,
#             "extracted_entities": entities,
#             "phase_4_safety_alerts": master_safety_warnings,
#             "is_safe": len(master_safety_warnings) == 0
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# import re
# import time
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from typing import Optional

# from app.core.rag import evidence_engine
# from app.core.llm import llm_synthesizer  # Phase 3: LLM Brain

# # --- PHASE 4 IMPORTS ---
# from app.core.extractor import entity_extractor
# from app.core.graph import medical_graph
# from app.core.rxnav_api import rxnav_client  # <-- NEW: Live NIH API

# app = FastAPI(
#     title="MedGPT Guardian API", 
#     version="1.0.0",
#     description="Risk-Adaptive Clinical Verification Engine for AI Safety & 5D Knowledge Graph"
# )

# # Enable CORS for React frontend integration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# def scrub_phi(text: str) -> tuple[str, bool]:
#     """Phase 1: Zero-Trust PHI Scrubber for Names, Ages, and Phone Numbers"""
#     if not text:
#         return text, False
    
#     original_text = text
    
#     # 1. Redact Phone Numbers (supports 7-digit and 10-digit formats)
#     text = re.sub(r'\b(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b|\b\d{3}[-.\s]?\d{4}\b', '[REDACTED_PHONE]', text)
    
#     # 2. Redact Ages (e.g., 45 years old)
#     text = re.sub(r'\b\d{1,3}\s*(?:years?\s*old|yrs?\s*old)\b', '[REDACTED_AGE]', text, flags=re.IGNORECASE)
    
#     # 3. Redact Common Names / Identifiers (e.g., John Doe)
#     text = re.sub(r'\b(John\s+Doe)\b', '[REDACTED_NAME]', text, flags=re.IGNORECASE)
    
#     phi_detected = (text != original_text)
#     return text, phi_detected

# # Flexible Pydantic Schema supporting BOTH formats seamlessly
# class ClinicalQuery(BaseModel):
#     query: Optional[str] = Field(None, description="Simple single-string search query")
#     patient_context: Optional[str] = Field("General patient context", description="Patient background info / PHI notes")
#     question: Optional[str] = Field(None, description="Detailed clinical question")

# @app.get("/")
# def read_root():
#     return {"status": "MedGPT Guardian Backend is Online"}

# @app.get("/health")
# def health_check():
#     return {
#         "status": "healthy",
#         "database": "NIH MedQuAD ChromaDB & Neo4j 5D Connected",
#         "security": "Phase 1 PHI Scrubber Active",
#         "llm": "Phase 3 Gemini Flash Active",
#         "graph": "Phase 4 Multi-Dimensional Knowledge Graph & Live NIH API Active"
#     }

# @app.post("/api/v1/verify")
# def verify_clinical_query(request: ClinicalQuery):
#     start_time = time.time()
#     try:
#         # Flexible handling: accepts either 'question' or 'query'
#         search_target = request.question or request.query
#         if not search_target:
#             raise HTTPException(status_code=400, detail="Either 'query' or 'question' must be provided.")

#         context_input = request.patient_context or "General patient context"

#         # Phase 1: Apply Zero-Trust PHI Scrubbing
#         safe_context, context_phi = scrub_phi(context_input)
#         safe_question, question_phi = scrub_phi(search_target)

#         # Phase 2: Query the 5,000-record NIH MedQuAD database via RAG engine
#         retrieved_evidence = evidence_engine.retrieve_guideline(safe_question)

#         # Phase 3: Synthesize conversational clinical response
#         ai_clinical_response = llm_synthesizer.synthesize_response(
#             patient_context=safe_context,
#             question=safe_question,
#             retrieved_evidence=retrieved_evidence
#         )

#         # ==========================================
#         # PHASE 4: AI Extractor Bridge
#         # ==========================================
#         # Forces Gemini (temperature=0.0) to parse text into strict JSON entity lists
#         entities = entity_extractor.extract_clinical_entities(
#             patient_context=safe_context,
#             proposed_treatment=ai_clinical_response
#         )
        
#         # ==========================================
#         # PHASE 4: Hybrid Safety Verification
#         # ==========================================
        
#         # Step A: Local 5-Dimensional Neo4j Graph Query (PrimeKG)
#         local_safety_warnings = medical_graph.verify_clinical_safety(
#             patient_diseases=entities.get("patient_diseases", []),
#             patient_allergies=entities.get("patient_allergies", []),
#             patient_factors=entities.get("patient_factors", []),
#             patient_labs=entities.get("patient_labs", []),
#             proposed_drugs=entities.get("proposed_drugs", [])
#         )

#         # Step B: Live NIH RxNav Database Query (Cross-referencing the drug array)
#         proposed_drugs = entities.get("proposed_drugs", [])
#         live_api_alerts = rxnav_client.check_drug_list_interactions(proposed_drugs)

#         # Step C: Combine into a single Master Alert List
#         master_safety_warnings = local_safety_warnings + live_api_alerts

#         processing_time_ms = round((time.time() - start_time) * 1000, 2)

#         return {
#             "status": "success",
#             "processing_time_ms": processing_time_ms,
#             "phi_intercepted": (context_phi or question_phi),
#             "safe_context": safe_context,
#             "safe_question": safe_question,
#             "retrieved_evidence": retrieved_evidence,
#             "ai_clinical_response": ai_clinical_response,
#             "extracted_entities": entities,
#             "phase_4_safety_alerts": master_safety_warnings,
#             "is_safe": len(master_safety_warnings) == 0
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



# import logging
# import re
# import time
# from typing import Optional

# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field

# from app.core.rag import evidence_engine
# from app.core.llm import llm_synthesizer
# from app.core.extractor import entity_extractor
# from app.core.graph import medical_graph
# from app.core.rxnav_api import rxnav_client


# logger = logging.getLogger(__name__)


# app = FastAPI(
#     title="MedGPT Guardian API",
#     version="1.0.0",
#     description=(
#         "Risk-Adaptive Clinical Verification Engine for AI Safety "
#         "and a 5D Knowledge Graph"
#     ),
# )


# # Enable CORS for React frontend integration.
# # For production deployment, restrict allow_origins to your frontend URL.
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# def scrub_phi(text: str) -> tuple[str, bool]:
#     """
#     Phase 1: Basic PHI scrubbing for common phone numbers, ages,
#     and the example name John Doe.

#     This is a limited pattern-based scrubber, not a comprehensive
#     de-identification or privacy guarantee.
#     """
#     if not text:
#         return text, False

#     original_text = text

#     # Redact common phone-number formats.
#     text = re.sub(
#         r"\b(?:\+?1[-.\s]?)?"
#         r"(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b"
#         r"|\b\d{3}[-.\s]?\d{4}\b",
#         "[REDACTED_PHONE]",
#         text,
#     )

#     # Redact ages such as "45 years old" or "45 yrs old".
#     text = re.sub(
#         r"\b\d{1,3}\s*(?:years?\s*old|yrs?\s*old)\b",
#         "[REDACTED_AGE]",
#         text,
#         flags=re.IGNORECASE,
#     )

#     # Preserve the existing example-name redaction.
#     text = re.sub(
#         r"\bJohn\s+Doe\b",
#         "[REDACTED_NAME]",
#         text,
#         flags=re.IGNORECASE,
#     )

#     phi_detected = text != original_text
#     return text, phi_detected


# class ClinicalQuery(BaseModel):
#     """Accept either a simple query or a detailed clinical question."""

#     query: Optional[str] = Field(
#         default=None,
#         description="Simple single-string search query",
#     )
#     patient_context: Optional[str] = Field(
#         default="General patient context",
#         description="Patient background information",
#     )
#     question: Optional[str] = Field(
#         default=None,
#         description="Detailed clinical question",
#     )


# @app.get("/")
# def read_root():
#     return {
#         "status": "MedGPT Guardian Backend is Online"
#     }


# @app.get("/health")
# def health_check():
#     # Retains the existing health endpoint response structure.
#     # These descriptions are configured status labels, not live
#     # independent checks of every dependency.
#     return {
#         "status": "healthy",
#         "database": "NIH MedQuAD ChromaDB & Neo4j 5D Connected",
#         "security": "Phase 1 PHI Scrubber Active",
#         "llm": "Phase 3 Gemini Flash Active",
#         "graph": (
#             "Phase 4 Multi-Dimensional Knowledge Graph "
#             "& Live NIH API Active"
#         ),
#     }


# @app.post("/api/v1/verify")
# def verify_clinical_query(request: ClinicalQuery):
#     start_time = time.time()

#     try:
#         # Accept either "question" or "query".
#         search_target = request.question or request.query

#         if not search_target or not search_target.strip():
#             raise HTTPException(
#                 status_code=400,
#                 detail="Either 'query' or 'question' must be provided.",
#             )

#         search_target = search_target.strip()

#         context_input = (
#             request.patient_context or "General patient context"
#         )

#         # ==========================================
#         # PHASE 1: Basic PHI Scrubbing
#         # ==========================================
#         safe_context, context_phi = scrub_phi(context_input)
#         safe_question, question_phi = scrub_phi(search_target)

#         # ==========================================
#         # PHASE 2: RAG Evidence Retrieval
#         # ==========================================
#         retrieved_evidence = evidence_engine.retrieve_guideline(
#             safe_question
#         )

#         # ==========================================
#         # PHASE 3: LLM Response Synthesis
#         # ==========================================
#         ai_clinical_response = llm_synthesizer.synthesize_response(
#             patient_context=safe_context,
#             question=safe_question,
#             retrieved_evidence=retrieved_evidence,
#         )

#         # ==========================================
#         # PHASE 4A: Clinical Entity Extraction
#         # ==========================================
#         entities = entity_extractor.extract_clinical_entities(
#             patient_context=safe_context,
#             proposed_treatment=ai_clinical_response,
#         )

#         if not isinstance(entities, dict):
#             raise TypeError(
#                 "Clinical entity extractor must return a dictionary."
#             )

#         # ==========================================
#         # PHASE 4B: Neo4j Clinical Safety Verification
#         # ==========================================
#         graph_verification = medical_graph.verify_clinical_safety(
#             patient_diseases=entities.get("patient_diseases", []),
#             patient_allergies=entities.get("patient_allergies", []),
#             patient_factors=entities.get("patient_factors", []),
#             patient_labs=entities.get("patient_labs", []),
#             proposed_drugs=entities.get("proposed_drugs", []),
#         )

#         # The current graph implementation returns a structured dictionary.
#         if not isinstance(graph_verification, dict):
#             raise TypeError(
#                 "Graph verification must return a dictionary."
#             )

#         graph_alerts = graph_verification.get("alerts", [])

#         if not isinstance(graph_alerts, list):
#             raise TypeError(
#                 "Graph verification 'alerts' must be a list."
#             )

#         # ==========================================
#         # PHASE 4C: Live NIH RxNav Interaction Checks
#         # ==========================================
#         proposed_drugs = entities.get("proposed_drugs", [])

#         live_api_alerts = rxnav_client.check_drug_list_interactions(
#             proposed_drugs
#         )

#         if not isinstance(live_api_alerts, list):
#             raise TypeError(
#                 "RxNav interaction checks must return a list."
#             )

#         # ==========================================
#         # PHASE 4D: Combine Safety Alerts
#         # ==========================================
#         master_safety_warnings = graph_alerts + live_api_alerts

#         graph_verification_complete = (
#             graph_verification.get("verification_complete") is True
#         )
#         graph_verification_incomplete = (
#             graph_verification.get("verification_incomplete") is True
#         )

#         # Fail closed if graph verification is incomplete or reports
#         # unresolved entities. An empty alert list alone does not
#         # establish that a clinical question is safe.
#         unresolved_entities = graph_verification.get(
#             "unresolved_entities", []
#         )

#         if not isinstance(unresolved_entities, list):
#             unresolved_entities = ["Invalid unresolved_entities result"]

#         graph_is_safe = graph_verification.get("is_safe") is True

#         is_safe = (
#             graph_is_safe
#             and graph_verification_complete
#             and not graph_verification_incomplete
#             and not unresolved_entities
#             and not master_safety_warnings
#         )

#         # ==========================================
#         # RESPONSE
#         # ==========================================
#         processing_time_ms = round(
#             (time.time() - start_time) * 1000,
#             2,
#         )

#         return {
#             "status": "success",
#             "processing_time_ms": processing_time_ms,
#             "phi_intercepted": bool(context_phi or question_phi),
#             "safe_context": safe_context,
#             "safe_question": safe_question,
#             "retrieved_evidence": retrieved_evidence,
#             "ai_clinical_response": ai_clinical_response,
#             "extracted_entities": entities,
#             "phase_4_safety_alerts": master_safety_warnings,
#             "graph_verification": {
#                 "verification_complete": graph_verification_complete,
#                 "verification_incomplete": graph_verification_incomplete,
#                 "unresolved_entities": unresolved_entities,
#                 "matched_entities": graph_verification.get(
#                     "matched_entities", {}
#                 ),
#                 "message": graph_verification.get("message", ""),
#             },
#             "is_safe": is_safe,
#         }

#     except HTTPException:
#         # Preserve intended HTTP status codes such as 400.
#         raise

#     except Exception:
#         # Keep the detailed traceback in the backend terminal.
#         # Avoid returning internal exception details to API clients.
#         logger.exception("Clinical verification endpoint failed")

#         raise HTTPException(
#             status_code=500,
#             detail=(
#                 "Clinical verification failed. "
#                 "Check backend logs for details."
#             ),
#         ) from None

"""
backend/app/main.py (v3) - MedGuard API
 
POST /api/v1/verify
  1. PHI scrub the inputs
  2. medguard.run(): extract -> graph pre-check -> write -> verify -> regenerate until the draft passes
     (the user only ever sees a verified answer, or a deterministic safety summary)
 
Response fields kept from the old API: status, processing_time_ms, phi_intercepted, safe_context, safe_question,
retrieved_evidence, ai_clinical_response, extracted_entities, phase_4_safety_alerts, is_safe.
  is_safe          -> True only when NO documented conflict was found for the asked drugs AND the answer is verified
  risk_detected    -> the graph found conflicts (the answer then warns the user about them)
  safety_status    -> passed | unverified | quality_warning | blocked_fallback
Send "debug": true to also receive every draft and the reviewer's violations (for evaluation and your paper).
"""
# import logging
# import time
# from typing import Optional
 
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
 
# from app.core.phi import scrub_phi
# from app.core import medguard
# from app.core.graph import medical_graph
# from app.core.llm import LLMError
 
# logger = logging.getLogger(__name__)
 
# app = FastAPI(
#     title="MedGuard API",
#     version="2.0.0",
#     description="Knowledge-graph-verified, reflective clinical decision support",
# )
# app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
 
 
# class ClinicalQuery(BaseModel):
#     query: Optional[str] = Field(None, description="Simple single-string query")
#     patient_context: Optional[str] = Field("General patient context", description="Patient background")
#     question: Optional[str] = Field(None, description="Clinical question")
#     debug: bool = Field(False, description="Return drafts and reviewer violations")
 
 
# @app.on_event("startup")
# def _startup():
#     try:
#         medical_graph.ensure_schema()
#     except Exception as e:
#         logger.error("Neo4j not ready at startup: %s", e)
 
 
# @app.get("/")
# def read_root():
#     return {"status": "MedGuard Backend is Online"}
 
 
# @app.get("/health")
# def health_check():
#     try:
#         graph = medical_graph.db_stats()
#     except Exception as e:
#         graph = {"error": str(e)[:200]}
#     return {"status": "healthy", "graph": graph}
 
 
# @app.post("/api/v1/verify")
# def verify_clinical_query(request: ClinicalQuery):
#     start = time.time()
#     question = request.question or request.query
#     if not question:
#         raise HTTPException(status_code=400, detail="Either 'query' or 'question' must be provided.")
#     context = request.patient_context or "General patient context"
 
#     safe_context, ctx_phi = scrub_phi(context)
#     safe_question, q_phi = scrub_phi(question)
 
#     try:
#         out = medguard.run(safe_context, safe_question, debug=request.debug)
#     except LLMError as e:
#         raise HTTPException(status_code=503, detail=f"Language model unavailable: {e}")
#     except Exception as e:
#         logger.exception("pipeline failure")
#         raise HTTPException(status_code=500, detail=str(e))
 
#     resp = {
#         "status": "success",
#         "processing_time_ms": round((time.time() - start) * 1000, 2),
#         "phi_intercepted": ctx_phi or q_phi,
#         "safe_context": safe_context,
#         "safe_question": safe_question,
#         "retrieved_evidence": "\n\n".join(e["text"] for e in out["evidence"]),
#         "ai_clinical_response": out["answer"],
#         "extracted_entities": out["entities"],
#         "phase_4_safety_alerts": out["alerts"],
#         "graph_findings": out["findings"],
#         "unresolved_drugs": out["unresolved_drugs"],
#         "unmatched_conditions": out["unmatched_conditions"],
#         "intent": out["intent"],
#         "audience": out["audience"],
#         "urgency": out["urgency"],
#         "missing_info": out["missing_info"],
#         "graph_context_used": out["graph_context_used"],
#         "safety_status": out["safety_status"],
#         "risk_detected": out["risk_detected"],
#         "is_safe": (not out["risk_detected"]) and out["safety_status"] == "passed",
#         "regenerations": out["regenerations"],
#         "timings": out["timings"],
#     }
#     if request.debug:
#         resp["reflection_history"] = out["history"]
#     return resp
"""
backend/app/main.py (v3) - MedGuard API
 
POST /api/v1/verify
  1. PHI scrub the inputs
  2. medguard.run(): extract -> graph pre-check -> write -> verify -> regenerate until the draft passes
     (the user only ever sees a verified answer, or a deterministic safety summary)
 
Response fields kept from the old API: status, processing_time_ms, phi_intercepted, safe_context, safe_question,
retrieved_evidence, ai_clinical_response, extracted_entities, phase_4_safety_alerts, is_safe.
  is_safe          -> True only when NO documented conflict was found for the asked drugs AND the answer is verified
  risk_detected    -> the graph found conflicts (the answer then warns the user about them)
  safety_status    -> passed | unverified | quality_warning | blocked_fallback
Send "debug": true to also receive every draft and the reviewer's violations (for evaluation and your paper).
"""
import logging
import time
import traceback
from typing import Optional
 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
 
from app.core.phi import scrub_phi
from app.core import medguard
from app.core.graph import medical_graph
from app.core.llm import LLMError
 
logger = logging.getLogger(__name__)
 
app = FastAPI(
    title="MedGuard API",
    version="2.0.0",
    description="Knowledge-graph-verified, reflective clinical decision support",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
 
 
class ClinicalQuery(BaseModel):
    query: Optional[str] = Field(None, description="Simple single-string query")
    patient_context: Optional[str] = Field("General patient context", description="Patient background")
    question: Optional[str] = Field(None, description="Clinical question")
    debug: bool = Field(False, description="Return drafts and reviewer violations")
 
 
@app.on_event("startup")
def _startup():
    try:
        medical_graph.ensure_schema()
    except Exception as e:
        logger.error("Neo4j not ready at startup: %s", e)
 
 
@app.get("/")
def read_root():
    return {"status": "MedGuard Backend is Online"}
 
 
@app.get("/health")
def health_check():
    try:
        graph = medical_graph.db_stats()
    except Exception as e:
        graph = {"error": str(e)[:200]}
    return {"status": "healthy", "graph": graph}
 
 
@app.get("/api/v1/diagnose")
def diagnose():
    """Step-by-step self-test of the knowledge graph. Open http://127.0.0.1:8000/api/v1/diagnose in the browser."""
    from app.core.resolver import resolve_drugs
    report = {}
 
    def step(name, fn):
        try:
            report[name] = fn()
        except Exception as e:
            report[name] = {"ERROR": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()[-600:]}
 
    step("1_neo4j_counts", medical_graph.db_stats)
    step("2_graph_uses_new_clean_data", lambda: {"legacy_data": (medical_graph.ensure_schema(), medical_graph.legacy_data)[1]})
 
    def _resolve():
        resolved, unresolved, alias = resolve_drugs(["propranolol", "aspirin", "warfarin"], medical_graph)
        return {"resolved": resolved, "unresolved": unresolved}
    step("3_drug_name_resolution", _resolve)
    step("4_propranolol_vs_asthma", lambda: medical_graph.check(["propranolol"], ["asthma"]))
    step("5_warfarin_vs_aspirin", lambda: medical_graph.check(["acetylsalicylic acid"], [], meds=["warfarin"]))
    return report
 
 
@app.post("/api/v1/verify")
def verify_clinical_query(request: ClinicalQuery):
    start = time.time()
    question = request.question or request.query
    if not question:
        raise HTTPException(status_code=400, detail="Either 'query' or 'question' must be provided.")
    context = request.patient_context or "General patient context"
 
    safe_context, ctx_phi = scrub_phi(context)
    safe_question, q_phi = scrub_phi(question)
 
    try:
        out = medguard.run(safe_context, safe_question, debug=request.debug)
    except LLMError as e:
        raise HTTPException(status_code=503, detail=f"Language model unavailable: {e}")
    except Exception as e:
        logger.exception("pipeline failure")
        raise HTTPException(status_code=500, detail=str(e))
 
    resp = {
        "status": "success",
        "processing_time_ms": round((time.time() - start) * 1000, 2),
        "phi_intercepted": ctx_phi or q_phi,
        "safe_context": safe_context,
        "safe_question": safe_question,
        "retrieved_evidence": "\n\n".join(e.get("text", "") for e in out.get("evidence", [])),
        "ai_clinical_response": out.get("answer"),
        "extracted_entities": out.get("entities", {}),
        "phase_4_safety_alerts": out.get("alerts", []),
        "graph_findings": out.get("findings", []),
        "unresolved_drugs": out.get("unresolved_drugs", []),
        "unmatched_conditions": out.get("unmatched_conditions", []),
        "intent": out.get("intent"),
        "audience": out.get("audience"),
        "urgency": out.get("urgency"),
        "missing_info": out.get("missing_info", []),
        "graph_context_used": out.get("graph_context_used", False),
        "graph_available": out.get("graph_available", True),
        "graph_error": out.get("graph_error", None),
        "safety_status": out.get("safety_status"),
        "risk_detected": out.get("risk_detected", False),
        "is_safe": (not out.get("risk_detected", True)) and out.get("safety_status") == "passed",
        "regenerations": out.get("regenerations", 0),
        "timings": out.get("timings", {}),
    }
    if request.debug:
        resp["reflection_history"] = out.get("history", [])
    return resp