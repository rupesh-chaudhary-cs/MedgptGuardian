# """
# backend/app/core/medguard.py (v3) - Intent-aware, knowledge-graph-verified, reflective generation.
 
# What is new in v3
#   * The system first works out WHAT KIND of question it is (intent), WHO is asking (patient / clinician) and HOW URGENT it is.
#     A drug-safety check, a drug explanation, a condition explainer, a treatment-options question, a symptom question and a
#     dosing question each get a different answer structure, tone and verification rules.
#   * Educational and treatment answers are grounded with facts pulled from the Neo4j graph (indications, contraindications,
#     symptoms) in addition to retrieved evidence.
#   * Missing but important information (e.g. kidney function) is asked for instead of being guessed.
 
# Pipeline (the draft is NEVER shown until it passes verification)
#   1 extract case + intent -> 2 resolve drug names -> 3 graph pre-check (and context facts) -> 4 write with the intent's format
#   -> 5 verify: recommended drugs vs graph, findings communicated, claims, structure/audience/urgency -> 6 regenerate with
#   feedback (MEDGUARD_MAX_ROUNDS) -> 7 deterministic safety summary if it still fails.
# """
# import logging
# import os
# import re
# import time
# from concurrent.futures import ThreadPoolExecutor
# from typing import Dict, List, Optional
 
# from app.core import llm as llm
# from app.core.graph import medical_graph, format_finding
# from app.core.resolver import resolve_drugs
 
# try:
#     from app.core.rag import evidence_engine
# except Exception:          # lets scripts run without the vector DB
#     evidence_engine = None
 
# logger = logging.getLogger(__name__)
# MAX_ROUNDS = int(os.getenv("MEDGUARD_MAX_ROUNDS", "3"))
 
# # ------------------------------------------------------------------ intent specifications
# INTENTS: Dict[str, Dict] = {
#     "drug_safety": {
#         "graph": "verify", "words": 350,
#         "format": ("**Bottom line** (one or two sentences giving a clear verdict: not recommended / use only with prescriber review / "
#                    "no documented conflict found), **Why** (each documented concern in plain words, naming the drug and the condition or drug involved), "
#                    "**Options to discuss with the prescriber** (safer classes, alternatives, protective measures), "
#                    "**Monitoring and when to seek urgent care**. If important information is missing, add **What I would need to know** (max 3 short items)."),
#     },
#     "drug_information": {
#         "graph": "context", "words": 400,
#         "format": ("**What it is and what it is used for**, **How it works** (two sentences), **Common and serious side effects**, "
#                    "**Who needs extra care** (conditions, other medicines, pregnancy), **Practical points** (food, alcohol, missed dose in general terms). "
#                    "No patient-specific doses. Personalise only if the patient context contains conditions or medicines that matter."),
#     },
#     "condition_information": {
#         "graph": "context", "words": 400,
#         "format": ("**Overview**, **Causes and risk factors**, **Symptoms**, **How it is diagnosed and treated**, "
#                    "**Self-care and when to see a doctor**. Educational tone, no verdict-style language."),
#     },
#     "treatment_options": {
#         "graph": "verify", "words": 400,
#         "format": ("**Bottom line** (the main approach), **Options by class** (benefits and drawbacks for THIS patient), "
#                    "**Options to avoid for this patient and why** (from graph findings and context), **Questions to discuss with the prescriber**."),
#     },
#     "symptom_assessment": {
#         "graph": "verify", "words": 350,
#         "format": ("**Urgency** first (emergency / same-day care / routine) with the reason, **Possible causes** (common to serious; this is not a diagnosis), "
#                    "**Red flags that need immediate care**, **What you can do now** (only safe general measures), **What a clinician will likely ask or test**."),
#     },
#     "dosing": {
#         "graph": "verify", "words": 300,
#         "format": ("**Short answer** (explain that exact dosing depends on the product label, age, weight, kidney/liver function and other medicines, "
#                    "and give only widely established general information), **What changes the dose for this patient**, **Where to confirm** (label, pharmacist, prescriber). "
#                    "Never give a patient-specific dose."),
#     },
#     "general_medical": {
#         "graph": "context", "words": 350,
#         "format": "A direct answer in the first sentence, then the key details in short sections, then when to seek professional care if relevant.",
#     },
# }
# DEFAULT_META = {"intent": "drug_safety", "audience": "unknown", "urgency": "routine", "missing_info": []}
 
# BASE_SYSTEM = """You are MedGuard, a medical decision-support assistant used by clinicians and informed patients.
# Write like a careful clinical pharmacist or physician: specific, calm, professional and genuinely helpful.
 
# RULES
# 1. Answer exactly what was asked. The first sentence must respond to the question. Never use a generic template that ignores the question type.
# 2. KNOWLEDGE GRAPH FINDINGS (when given) are authoritative: never recommend, or imply safety of, any drug-condition or drug-drug pair listed there. If a finding says severity is not specified, say the interaction is documented but its severity is not specified.
# 3. Never say a drug "has no interactions" or "is safe" for anything listed as NOT CHECKED. Say it could not be checked in the database.
# 4. KNOWLEDGE GRAPH CONTEXT lists are partial and names-only; use them as grounding, not as a complete list. Use retrieved evidence only where relevant and cite it as [E1], [E2]; ignore irrelevant passages silently.
#    NEVER answer with "the provided evidence does not contain..."; use established clinical knowledge instead, and make clear which statements come from the knowledge graph, which from evidence and which are general clinical knowledge.
# 5. Use the patient context only when it matters for the question. Do not force patient-specific warnings into a purely educational answer unless a listed finding applies.
# 6. No diagnosis, no patient-specific doses. If URGENCY is emergency or urgent, begin by saying so and what to do now (call local emergency services / seek same-day care).
#    If the user mentions self-harm or suicide, respond warmly, encourage contacting local emergency services or a crisis line right now, and give no method information.
# 7. Never repeat redacted placeholders such as [REDACTED_NAME].
# 8. Be concise: no filler, no repetition, no moralising."""
 
# AUDIENCE_STYLE = {
#     "clinician": "AUDIENCE: clinician. Use precise clinical terminology, be concise, refer to the patient in the third person.",
#     "patient": "AUDIENCE: patient / layperson. Use plain language, define medical terms briefly, be warm but not alarmist, address the reader as 'you' where natural.",
#     "unknown": "AUDIENCE: unknown. Use clear, plain professional language and define specialised terms briefly.",
# }
 
# EXTRACT_SYSTEM = ("You are a clinical information extraction and triage engine. Return strict JSON only. "
#                   "Correct obvious spelling mistakes in drug and disease names. Never invent facts that are not in the text.")
# VERIFY_SYSTEM = "You are a strict clinical-safety and quality reviewer for AI-written medical answers. Return strict JSON only."
 
 
# def _lst(x) -> List[str]:
#     if not isinstance(x, list):
#         return []
#     out = []
#     for v in x:
#         s = str(v).strip().lower()
#         if s and s not in out:
#             out.append(s)
#     return out
 
 
# def extract_case(context: str, question: str) -> Dict:
#     prompt = f"""PATIENT CONTEXT:
# {context}
 
# USER QUESTION:
# {question}
 
# Return a JSON object with exactly these keys (lists contain lowercase strings, [] when none):
# - "asked_drugs": medications the question asks about, proposes or wants to prescribe/take. Generic ingredient names, spelling corrected (e.g. "prophano" -> "propranolol"). No brand names or salts.
# - "patient_meds": medications the patient ALREADY takes (context or question). Generic names, spelling corrected.
# - "diseases": the patient's diseases/conditions as standard singular medical terms, spelling corrected, abbreviations expanded ("asthm" -> "asthma").
# - "allergies": substances the patient is allergic to (generic drug names or classes).
# - "factors": ONLY terms from this list that apply: pregnancy, breastfeeding, neonates, children, elderly, renal impairment, hepatic impairment. (age 65 or over -> "elderly"; under 18 -> "children")
# - "labs": abnormal lab/vital/ECG findings as standard finding terms (e.g. "hyperkalemia").
# - "topic_drugs": for questions ABOUT a drug (what is it, how it works, side effects), the drug(s) that are the subject. Generic names. [] otherwise.
# - "topic_conditions": for questions ABOUT a condition or symptom, the condition(s) that are the subject, standard singular terms. [] otherwise.
# - "intent": exactly one of: drug_safety (can a specific drug/combination be taken, prescribed, or is it safe for this patient; interactions, contraindications, allergies), drug_information (what a drug is, what it treats, how it works, its side effects), condition_information (what a disease is, causes, symptoms, prevention, outlook), treatment_options (how a condition is treated, what can be used for a condition or symptom), symptom_assessment (the user describes symptoms and asks what it could be or what to do), dosing (how much / how often / how long to take a drug), general_medical (anything else medical).
# - "audience": "clinician" if the wording is clinical (prescribe, the patient, pt, differential), "patient" if first-person or lay wording, else "unknown".
# - "urgency": "emergency" if the described situation may be life-threatening (chest pain with sweating or breathlessness, stroke signs, severe breathing difficulty, anaphylaxis, heavy bleeding, suicidal intent), "urgent" if same-day care is advisable, else "routine".
# - "missing_info": up to 3 short strings naming facts that are missing and would change the advice (e.g. "kidney function", "pregnancy status"). [] if none.
# """
#     d = llm.generate_json(prompt, system=EXTRACT_SYSTEM, model=llm.FAST_MODEL)
#     intent = str(d.get("intent", "")).strip().lower()
#     if intent not in INTENTS:
#         intent = "general_medical"
#     audience = str(d.get("audience", "unknown")).strip().lower()
#     urgency = str(d.get("urgency", "routine")).strip().lower()
#     return {"asked_drugs": _lst(d.get("asked_drugs")), "patient_meds": _lst(d.get("patient_meds")),
#             "diseases": _lst(d.get("diseases")), "allergies": _lst(d.get("allergies")),
#             "factors": _lst(d.get("factors")), "labs": _lst(d.get("labs")),
#             "topic_drugs": _lst(d.get("topic_drugs")), "topic_conditions": _lst(d.get("topic_conditions")),
#             "intent": intent, "audience": audience if audience in AUDIENCE_STYLE else "unknown",
#             "urgency": urgency if urgency in ("emergency", "urgent", "routine") else "routine",
#             "missing_info": [str(x).strip() for x in (d.get("missing_info") or []) if str(x).strip()][:3]}
 
 
# def _retrieve(question: str) -> List[Dict]:
#     if evidence_engine is None:
#         return []
#     try:
#         raw = evidence_engine.retrieve_guideline(question) or ""
#     except Exception as e:
#         logger.warning("RAG retrieval failed: %s", e)
#         return []
#     blocks = [b.strip() for b in re.split(r"(?=Clinical Query:)", raw) if b.strip()]
#     return [{"id": f"E{i + 1}", "text": b[:1100]} for i, b in enumerate(blocks[:3])]
 
 
# def _graph_block(findings, unresolved, unmatched, graph_ok) -> str:
#     if not graph_ok:
#         return "The knowledge graph was unavailable for this request. Do NOT claim any database check was done."
#     if findings:
#         txt = "\n".join(f"[{f['id']}] {format_finding(f)}" for f in findings)
#     else:
#         txt = "No conflicts were found in the knowledge graph for the identified drugs and conditions (this is not proof of safety)."
#     if unresolved:
#         txt += "\nNOT CHECKED (drug not found in the database): " + ", ".join(unresolved)
#     if unmatched:
#         txt += "\nConditions not found in the database: " + ", ".join(unmatched)
#     return txt
 
 
# def _facts_block(facts: List[Dict]) -> Optional[str]:
#     if not facts:
#         return None
#     lines = []
#     for f in facts:
#         for rel, names in f["groups"].items():
#             lines.append(f"- {f['entity']} / {rel.lower().replace('_', ' ')}: " + "; ".join(names))
#     return "\n".join(lines)
 
 
# def build_system(meta: Dict) -> str:
#     spec = INTENTS[meta["intent"]]
#     return (f"{BASE_SYSTEM}\n\n{AUDIENCE_STYLE[meta['audience']]}\n\n"
#             f"QUESTION TYPE: {meta['intent']}\nREQUIRED FORMAT (markdown, about {spec['words']} words at most): {spec['format']}")
 
 
# def build_prompt(context, question, evidence, graph_block, feedback, meta, facts_block=None) -> str:
#     parts = []
#     if context and context.strip().lower() != "general patient context":
#         parts.append(f"PATIENT CONTEXT:\n{context}")
#     parts.append(f"QUESTION:\n{question}")
#     parts.append(f"URGENCY: {meta['urgency']}")
#     if graph_block is not None:
#         parts.append("KNOWLEDGE GRAPH FINDINGS (authoritative, must be respected):\n" + graph_block)
#     if facts_block:
#         parts.append("KNOWLEDGE GRAPH CONTEXT (partial, names only):\n" + facts_block)
#     if evidence:
#         parts.append("RETRIEVED EVIDENCE (may be partly irrelevant; ignore passages that do not apply):\n" +
#                      "\n\n".join(f"[{e['id']}] {e['text']}" for e in evidence))
#     if meta.get("missing_info") and meta["intent"] in ("drug_safety", "treatment_options", "dosing", "symptom_assessment"):
#         parts.append("INFORMATION NOT PROVIDED that could change the advice: " + "; ".join(meta["missing_info"]))
#     if feedback:
#         parts.append("REVIEWER FEEDBACK ON YOUR PREVIOUS DRAFT (fix every point; do not mention this feedback):\n- " +
#                      "\n- ".join(feedback))
#     parts.append("Write the answer now.")
#     return "\n\n".join(parts)
 
 
# def generate(context, question, evidence, graph_block, feedback=None, meta=None, facts_block=None) -> str:
#     meta = {**DEFAULT_META, **(meta or {})}
#     return llm.generate_text(build_prompt(context, question, evidence, graph_block, feedback, meta, facts_block),
#                              system=build_system(meta), model=llm.GEN_MODEL, temperature=0.3, max_tokens=1200)
 
 
# _STOP = {"disease", "syndrome", "disorder", "chronic", "acute", "severe", "with", "without", "type"}
 
 
# def _covered(answer_lc: str, f: Dict, alias_map: Dict) -> bool:
#     def names(n):
#         return alias_map.get(n, {n})
#     if not any(x in answer_lc for x in names(f["drug"])):
#         return False
#     if f["kind"] == "interaction":
#         return any(x in answer_lc for x in names(f["target"]))
#     toks = [t for t in re.findall(r"[a-z]{5,}", f["target"].lower()) if t not in _STOP] or [f["target"].lower()]
#     return any(t[:6] in answer_lc for t in toks)
 
 
# def verify_draft(draft, case, findings, alias_map, resolved_meds, graph_ok):
#     """Returns (violations, critic_ok, recommended_drugs)."""
#     violations: List[str] = []
#     spec = INTENTS[case["intent"]]
#     fl = "\n".join(f"[{f['id']}] {format_finding(f)}" for f in findings) or "(none)"
#     prompt = f"""PATIENT CASE (JSON): {case}
 
# QUESTION TYPE: {case['intent']} | AUDIENCE: {case['audience']} | URGENCY: {case['urgency']}
# REQUIRED STRUCTURE: {spec['format']}
 
# KNOWLEDGE GRAPH FINDINGS:
# {fl}
 
# DRAFT ANSWER:
# {draft}
 
# Return a JSON object with exactly these keys:
# - "recommended_drugs": generic names of drugs the draft tells THIS patient to take, start, continue or consider (including suggested alternatives). General educational mentions (for example a list of drug classes used for a condition) are NOT recommendations. EXCLUDE drugs the draft advises against.
# - "endorses_unsafe_finding_ids": ids of findings whose drug/condition or drug pair the draft treats as acceptable or safe without the warning.
# - "missing_finding_ids": ids of findings that the draft never clearly communicates.
# - "risky_claims": short strings: specific patient doses, definitive diagnoses, invented citations or statistics, or statements that contradict standard clinical references.
# - "answers_the_question": true if the first sentences directly answer what was asked.
# - "follows_structure": true if the draft follows the required structure for this question type.
# - "fits_audience": true if wording and tone fit the audience.
# - "handles_urgency": true if URGENCY is routine, or if the draft clearly leads with the urgent advice.
# - "quality_issues": short strings: vagueness, saying evidence is unavailable instead of helping, repetition, unprofessional tone. Empty list if clear and professional.
# """
#     critic_ok, recommended = True, []
#     try:
#         c = llm.generate_json(prompt, system=VERIFY_SYSTEM, model=llm.FAST_MODEL)
#         recommended = _lst(c.get("recommended_drugs"))
#         ids = {f["id"]: f for f in findings}
#         for fid in c.get("endorses_unsafe_finding_ids") or []:
#             if fid in ids:
#                 violations.append(f"The draft treats [{fid}] as acceptable: {format_finding(ids[fid])}")
#         for fid in c.get("missing_finding_ids") or []:
#             if fid in ids:
#                 violations.append(f"The draft does not clearly communicate [{fid}]: {format_finding(ids[fid])}")
#         violations += [f"Risky or unsupported claim: {x}" for x in (c.get("risky_claims") or [])[:3]]
#         if c.get("answers_the_question") is False:
#             violations.append("Quality: the first sentences do not directly answer the question that was asked")
#         if c.get("follows_structure") is False:
#             violations.append(f"Quality: follow the required structure for a {case['intent']} answer")
#         if c.get("fits_audience") is False:
#             violations.append(f"Quality: adjust wording and tone for the {case['audience']} audience")
#         if c.get("handles_urgency") is False:
#             violations.append(f"Quality: urgency is {case['urgency']}; begin with the urgent advice")
#         violations += [f"Quality: {x}" for x in (c.get("quality_issues") or [])[:3]]
#     except llm.LLMError as e:
#         critic_ok = False
#         logger.warning("critic unavailable: %s", e)
 
#     al = draft.lower()
#     for f in findings:
#         if not _covered(al, f, alias_map) and not any(f"[{f['id']}]" in v for v in violations):
#             violations.append(f"The draft does not mention [{f['id']}]: {format_finding(f)}")
 
#     if recommended and graph_ok:
#         try:
#             resolved, _, _ = resolve_drugs(recommended, medical_graph)
#             rec_db = sorted(set(resolved.values()))
#             rec = medical_graph.check(rec_db, case["diseases"], case["allergies"], case["factors"],
#                                       case["labs"], resolved_meds)
#             for f in rec["findings"]:
#                 violations.append(f"The draft recommends '{f['drug']}' but the graph flags it: {format_finding(f)}")
#         except Exception as e:
#             critic_ok = False
#             logger.warning("graph re-check failed: %s", e)
#     return violations, critic_ok, recommended
 
 
# def fallback_answer(findings, unresolved) -> str:
#     lines = ["**Bottom line:** A safe recommendation could not be confirmed for this patient. "
#              "Please do not start or combine the medicines in question until the prescriber or a pharmacist has reviewed them."]
#     if findings:
#         lines.append("\n**Documented safety concerns**")
#         lines += [f"- {format_finding(f)}" for f in findings]
#     if unresolved:
#         lines.append("\n**Not checked in the database:** " + ", ".join(unresolved) +
#                      ". Absence from the database does not mean the medicine is safe.")
#     lines.append("\n**Next step:** Discuss alternative treatments and monitoring with the prescribing clinician or a pharmacist.")
#     return "\n".join(lines)
 
 
# def footer(status, findings, unresolved, intent) -> str:
#     if intent in ("drug_information", "condition_information", "general_medical"):
#         s = "\n\n---\n*General medical information, not personal medical advice."
#         if findings:
#             s += f" {len(findings)} patient-specific concern(s) from the knowledge graph were included above."
#         if status == "unverified":
#             s += " WARNING: automated verification was incomplete."
#         return s + " Please consult a healthcare professional about your own situation.*"
#     s = ("\n\n---\n*Safety review: checked against a clinical knowledge graph (drug-condition, drug-drug, allergy, "
#          "population and lab rules). ")
#     s += f"{len(findings)} documented concern(s) flagged. " if findings else "No documented concerns found, which does not prove safety. "
#     if unresolved:
#         s += "Not checked (not in database): " + ", ".join(unresolved) + ". "
#     if status == "unverified":
#         s += "WARNING: automated verification was incomplete for this answer. "
#     return s + "Decision support only, not a substitute for professional judgement.*"
 
 
# # ------------------------------------------------------------------ pipeline
# def prepare(patient_context: str, question: str) -> Dict:
#     """Steps 1-3: extraction, retrieval, name resolution, graph pre-check, context facts."""
#     t0 = time.time()
#     with ThreadPoolExecutor(max_workers=2) as pool:
#         f_case = pool.submit(extract_case, patient_context, question)
#         f_ev = pool.submit(_retrieve, question)
#         case, evidence = f_case.result(), f_ev.result()
#     t1 = time.time()
 
#     prep = {"case": case, "evidence": evidence, "findings": [], "unresolved": [], "unmatched": [], "facts_block": None,
#             "graph_ok": True, "alias_map": {}, "resolved_meds": [], "resolved_asked": []}
#     try:
#         res_asked, un_a, am_a = resolve_drugs(case["asked_drugs"], medical_graph)
#         res_meds, un_m, am_m = resolve_drugs(case["patient_meds"], medical_graph)
#         alias_map = {**am_m, **am_a}
#         for k in set(am_a) & set(am_m):
#             alias_map[k] = am_a[k] | am_m[k]
#         asked, meds = sorted(set(res_asked.values())), sorted(set(res_meds.values()))
#         chk = medical_graph.check(asked, case["diseases"], case["allergies"], case["factors"], case["labs"], meds)
#         prep.update(findings=chk["findings"], unmatched=chk["unmatched_conditions"], unresolved=sorted(set(un_a + un_m)),
#                     alias_map=alias_map, resolved_meds=meds, resolved_asked=asked)
 
#         if INTENTS[case["intent"]]["graph"] == "context" or case["intent"] == "treatment_options":
#             facts = []
#             if case["topic_drugs"]:
#                 res_t, _, _ = resolve_drugs(case["topic_drugs"], medical_graph)
#                 facts += medical_graph.facts("Drug", sorted(set(res_t.values())))
#             if case["topic_conditions"]:
#                 facts += medical_graph.facts("Disease", case["topic_conditions"])
#             prep["facts_block"] = _facts_block(facts)
#     except Exception as e:
#         logger.error("graph step failed: %s", e)
#         prep["graph_ok"] = False
#     prep["timings"] = {"extract_and_retrieve_s": round(t1 - t0, 2), "graph_s": round(time.time() - t1, 2)}
#     return prep
 
 
# def run(patient_context: str, question: str, debug: bool = False) -> Dict:
#     t_start = time.time()
#     prep = prepare(patient_context, question)
#     case, evidence, findings = prep["case"], prep["evidence"], prep["findings"]
#     # pure education questions with nothing to check do not need the findings block
#     block = _graph_block(findings, prep["unresolved"], prep["unmatched"], prep["graph_ok"]) \
#         if (findings or prep["unresolved"] or case["asked_drugs"] or not prep["graph_ok"]) else None
 
#     history, feedback, answer, status = [], None, None, "blocked_fallback"
#     critic_ever_failed, last_draft, last_violations = False, None, []
#     for rnd in range(1, MAX_ROUNDS + 1):
#         draft = generate(patient_context, question, evidence, block, feedback, case, prep["facts_block"])
#         violations, critic_ok, recommended = verify_draft(draft, case, findings, prep["alias_map"],
#                                                           prep["resolved_meds"], prep["graph_ok"])
#         critic_ever_failed = critic_ever_failed or not critic_ok
#         last_draft, last_violations = draft, violations
#         entry = {"round": rnd, "violations": violations, "recommended_drugs": recommended}
#         if debug:
#             entry["draft"] = draft
#         history.append(entry)
#         if not violations:
#             answer, status = draft, "passed"
#             break
#         feedback = violations
 
#     if answer is None:
#         safety_left = [v for v in last_violations if not v.startswith(("Quality:", "Risky or unsupported"))]
#         if last_draft and not safety_left:
#             answer, status = last_draft, "quality_warning"
#         else:
#             answer = fallback_answer(findings, prep["unresolved"])
#     if status == "passed" and (critic_ever_failed or not prep["graph_ok"]):
#         status = "unverified"
#     final_text = answer + footer(status, findings, prep["unresolved"], case["intent"])
 
#     return {
#         "answer": final_text,
#         "intent": case["intent"], "audience": case["audience"], "urgency": case["urgency"],
#         "missing_info": case["missing_info"],
#         "safety_status": status,                          # passed | unverified | quality_warning | blocked_fallback
#         "risk_detected": bool(findings),
#         "findings": findings,
#         "alerts": [f"[{f['severity']}] {format_finding(f)}" for f in findings],
#         "unresolved_drugs": prep["unresolved"],
#         "unmatched_conditions": prep["unmatched"],
#         "graph_context_used": bool(prep["facts_block"]),
#         "entities": case,
#         "evidence": evidence,
#         "rounds": len(history),
#         "regenerations": max(0, len(history) - 1),
#         "history": history,
#         "timings": {**prep["timings"], "total_s": round(time.time() - t_start, 2)},
#     }


"""
backend/app/core/medguard.py (v3.1 - False Positive Fix) - Intent-aware, knowledge-graph-verified, reflective generation.
"""
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

from app.core import llm as llm
from app.core.graph import medical_graph, format_finding
from app.core.resolver import resolve_drugs

try:
    from app.core.rag import evidence_engine
except Exception:
    evidence_engine = None

logger = logging.getLogger(__name__)
MAX_ROUNDS = int(os.getenv("MEDGUARD_MAX_ROUNDS", "3"))

# ------------------------------------------------------------------ intent specifications
INTENTS: Dict[str, Dict] = {
    "drug_safety": {
        "graph": "verify", "words": 350,
        "format": ("**Bottom line** (one or two sentences giving a clear verdict: not recommended / use only with prescriber review / "
                   "no documented conflict found), **Why** (each documented concern in plain words, naming the drug and the condition or drug involved), "
                   "**Options to discuss with the prescriber** (safer classes, alternatives, protective measures), "
                   "**Monitoring and when to seek urgent care**. If important information is missing, add **What I would need to know** (max 3 short items)."),
    },
    "drug_information": {
        "graph": "context", "words": 400,
        "format": ("**What it is and what it is used for**, **How it works** (two sentences), **Common and serious side effects**, "
                   "**Who needs extra care** (conditions, other medicines, pregnancy), **Practical points** (food, alcohol, missed dose in general terms). "
                   "No patient-specific doses. Personalise only if the patient context contains conditions or medicines that matter."),
    },
    "condition_information": {
        "graph": "context", "words": 400,
        "format": ("**Overview**, **Causes and risk factors**, **Symptoms**, **How it is diagnosed and treated**, "
                   "**Self-care and when to see a doctor**. Educational tone, no verdict-style language."),
    },
    "treatment_options": {
        "graph": "verify", "words": 400,
        "format": ("**Bottom line** (the main approach), **Options by class** (benefits and drawbacks for THIS patient), "
                   "**Options to avoid for this patient and why** (from graph findings and context), **Questions to discuss with the prescriber**."),
    },
    "symptom_assessment": {
        "graph": "verify", "words": 350,
        "format": ("**Urgency** first (emergency / same-day care / routine) with the reason, **Possible causes** (common to serious; this is not a diagnosis), "
                   "**Red flags that need immediate care**, **What you can do now** (only safe general measures), **What a clinician will likely ask or test**."),
    },
    "dosing": {
        "graph": "verify", "words": 300,
        "format": ("**Short answer** (explain that exact dosing depends on the product label, age, weight, kidney/liver function and other medicines, "
                   "and give only widely established general information), **What changes the dose for this patient**, **Where to confirm** (label, pharmacist, prescriber). "
                   "Never give a patient-specific dose."),
    },
    "general_medical": {
        "graph": "context", "words": 350,
        "format": "A direct answer in the first sentence, then the key details in short sections, then when to seek professional care if relevant.",
    },
}
DEFAULT_META = {"intent": "drug_safety", "audience": "unknown", "urgency": "routine", "missing_info": []}

BASE_SYSTEM = """You are MedGuard, a medical decision-support assistant used by clinicians and informed patients.
Write like a careful clinical pharmacist or physician: specific, calm, professional and genuinely helpful.

RULES
1. Answer exactly what was asked. The first sentence must respond to the question. Never use a generic template that ignores the question type.
2. KNOWLEDGE GRAPH FINDINGS (when given) are authoritative: never recommend, or imply safety of, any drug-condition or drug-drug pair listed there. If a finding says severity is not specified, say the interaction is documented but its severity is not specified.
3. Never say a drug "has no interactions" or "is safe" for anything listed as NOT CHECKED. Say it could not be checked in the database.
4. KNOWLEDGE GRAPH CONTEXT lists are partial and names-only; use them as grounding, not as a complete list. Use retrieved evidence only where relevant and cite it as [E1], [E2]; ignore irrelevant passages silently.
   NEVER answer with "the provided evidence does not contain..."; use established clinical knowledge instead, and make clear which statements come from the knowledge graph, which from evidence and which are general clinical knowledge.
5. Use the patient context only when it matters for the question. Do not force patient-specific warnings into a purely educational answer unless a listed finding applies.
6. No diagnosis, no patient-specific doses. If URGENCY is emergency or urgent, begin by saying so and what to do now (call local emergency services / seek same-day care).
   If the user mentions self-harm or suicide, respond warmly, encourage contacting local emergency services or a crisis line right now, and give no method information.
7. Never repeat redacted placeholders such as [REDACTED_NAME].
8. Be concise: no filler, no repetition, no moralising."""

AUDIENCE_STYLE = {
    "clinician": "AUDIENCE: clinician. Use precise clinical terminology, be concise, refer to the patient in the third person.",
    "patient": "AUDIENCE: patient / layperson. Use plain language, define medical terms briefly, be warm but not alarmist, address the reader as 'you' where natural.",
    "unknown": "AUDIENCE: unknown. Use clear, plain professional language and define specialised terms briefly.",
}

EXTRACT_SYSTEM = ("You are a clinical information extraction and triage engine. Return strict JSON only. "
                  "Correct obvious spelling mistakes in drug and disease names. Never invent facts that are not in the text.")
VERIFY_SYSTEM = "You are a strict clinical-safety and quality reviewer for AI-written medical answers. Return strict JSON only."


def _lst(x) -> List[str]:
    if not isinstance(x, list):
        return []
    out = []
    for v in x:
        s = str(v).strip().lower()
        if s and s not in out:
            out.append(s)
    return out


def extract_case(context: str, question: str) -> Dict:
    prompt = f"""PATIENT CONTEXT:
{context}

USER QUESTION:
{question}

Return a JSON object with exactly these keys (lists contain lowercase strings, [] when none):
- "asked_drugs": medications the question asks about, proposes or wants to prescribe/take. Generic ingredient names, spelling corrected (e.g. "prophano" -> "propranolol"). No brand names or salts.
- "patient_meds": medications the patient ALREADY takes (context or question). Generic names, spelling corrected.
- "diseases": the patient's diseases/conditions as standard singular medical terms, spelling corrected, abbreviations expanded ("asthm" -> "asthma").
- "allergies": substances the patient is allergic to (generic drug names or classes).
- "factors": ONLY terms from this list that apply: pregnancy, breastfeeding, neonates, children, elderly, renal impairment, hepatic impairment. (age 65 or over -> "elderly"; under 18 -> "children")
- "labs": abnormal lab/vital/ECG findings as standard finding terms (e.g. "hyperkalemia").
- "topic_drugs": for questions ABOUT a drug (what is it, how it works, side effects), the drug(s) that are the subject. Generic names. [] otherwise.
- "topic_conditions": for questions ABOUT a condition or symptom, the condition(s) that are the subject, standard singular terms. [] otherwise.
- "intent": exactly one of: drug_safety (can a specific drug/combination be taken, prescribed, or is it safe for this patient; interactions, contraindications, allergies), drug_information (what a drug is, what it treats, how it works, its side effects), condition_information (what a disease is, causes, symptoms, prevention, outlook), treatment_options (how a condition is treated, what can be used for a condition or symptom), symptom_assessment (the user describes symptoms and asks what it could be or what to do), dosing (how much / how often / how long to take a drug), general_medical (anything else medical).
- "audience": "clinician" if the wording is clinical (prescribe, the patient, pt, differential), "patient" if first-person or lay wording, else "unknown".
- "urgency": "emergency" if the described situation may be life-threatening (chest pain with sweating or breathlessness, stroke signs, severe breathing difficulty, anaphylaxis, heavy bleeding, suicidal intent), "urgent" if same-day care is advisable, else "routine".
- "missing_info": up to 3 short strings naming facts that are missing and would change the advice (e.g. "kidney function", "pregnancy status"). [] if none.
"""
    d = llm.generate_json(prompt, system=EXTRACT_SYSTEM, model=llm.FAST_MODEL)
    intent = str(d.get("intent", "")).strip().lower()
    if intent not in INTENTS:
        intent = "general_medical"
    audience = str(d.get("audience", "unknown")).strip().lower()
    urgency = str(d.get("urgency", "routine")).strip().lower()
    return {"asked_drugs": _lst(d.get("asked_drugs")), "patient_meds": _lst(d.get("patient_meds")),
            "diseases": _lst(d.get("diseases")), "allergies": _lst(d.get("allergies")),
            "factors": _lst(d.get("factors")), "labs": _lst(d.get("labs")),
            "topic_drugs": _lst(d.get("topic_drugs")), "topic_conditions": _lst(d.get("topic_conditions")),
            "intent": intent, "audience": audience if audience in AUDIENCE_STYLE else "unknown",
            "urgency": urgency if urgency in ("emergency", "urgent", "routine") else "routine",
            "missing_info": [str(x).strip() for x in (d.get("missing_info") or []) if str(x).strip()][:3]}


def _retrieve(question: str) -> List[Dict]:
    if evidence_engine is None:
        return []
    try:
        raw = evidence_engine.retrieve_guideline(question) or ""
    except Exception as e:
        logger.warning("RAG retrieval failed: %s", e)
        return []
    blocks = [b.strip() for b in re.split(r"(?=Clinical Query:)", raw) if b.strip()]
    return [{"id": f"E{i + 1}", "text": b[:1100]} for i, b in enumerate(blocks[:3])]


def _graph_block(findings, unresolved, unmatched, graph_ok) -> str:
    if not graph_ok:
        return "The knowledge graph was unavailable for this request. Do NOT claim any database check was done."
    if findings:
        txt = "\n".join(f"[{f['id']}] {format_finding(f)}" for f in findings)
    else:
        txt = "No conflicts were found in the knowledge graph for the identified drugs and conditions (this is not proof of safety)."
    if unresolved:
        txt += "\nNOT CHECKED (drug not found in the database): " + ", ".join(unresolved)
    if unmatched:
        txt += "\nConditions not found in the database: " + ", ".join(unmatched)
    return txt


def _facts_block(facts: List[Dict]) -> Optional[str]:
    if not facts:
        return None
    lines = []
    for f in facts:
        for rel, names in f["groups"].items():
            lines.append(f"- {f['entity']} / {rel.lower().replace('_', ' ')}: " + "; ".join(names))
    return "\n".join(lines)


def build_system(meta: Dict) -> str:
    spec = INTENTS[meta["intent"]]
    return (f"{BASE_SYSTEM}\n\n{AUDIENCE_STYLE[meta['audience']]}\n\n"
            f"QUESTION TYPE: {meta['intent']}\nREQUIRED FORMAT (markdown, about {spec['words']} words at most): {spec['format']}")


def build_prompt(context, question, evidence, graph_block, feedback, meta, facts_block=None) -> str:
    parts = []
    if context and context.strip().lower() != "general patient context":
        parts.append(f"PATIENT CONTEXT:\n{context}")
    parts.append(f"QUESTION:\n{question}")
    parts.append(f"URGENCY: {meta['urgency']}")
    if graph_block is not None:
        parts.append("KNOWLEDGE GRAPH FINDINGS (authoritative, must be respected):\n" + graph_block)
    if facts_block:
        parts.append("KNOWLEDGE GRAPH CONTEXT (partial, names only):\n" + facts_block)
    if evidence:
        parts.append("RETRIEVED EVIDENCE (may be partly irrelevant; ignore passages that do not apply):\n" +
                     "\n\n".join(f"[{e['id']}] {e['text']}" for e in evidence))
    if meta.get("missing_info") and meta["intent"] in ("drug_safety", "treatment_options", "dosing", "symptom_assessment"):
        parts.append("INFORMATION NOT PROVIDED that could change the advice: " + "; ".join(meta["missing_info"]))
    if feedback:
        parts.append("REVIEWER FEEDBACK ON YOUR PREVIOUS DRAFT (fix every point; do not mention this feedback):\n- " +
                     "\n- ".join(feedback))
    parts.append("Write the answer now.")
    return "\n\n".join(parts)


def generate(context, question, evidence, graph_block, feedback=None, meta=None, facts_block=None) -> str:
    meta = {**DEFAULT_META, **(meta or {})}
    return llm.generate_text(build_prompt(context, question, evidence, graph_block, feedback, meta, facts_block),
                             system=build_system(meta), model=llm.GEN_MODEL, temperature=0.3, max_tokens=1200)


_STOP = {"disease", "syndrome", "disorder", "chronic", "acute", "severe", "with", "without", "type"}


def _covered(answer_lc: str, f: Dict, alias_map: Dict) -> bool:
    def names(n):
        return alias_map.get(n, {n})
    if not any(x in answer_lc for x in names(f["drug"])):
        return False
    if f["kind"] == "interaction":
        return any(x in answer_lc for x in names(f["target"]))
    toks = [t for t in re.findall(r"[a-z]{5,}", f["target"].lower()) if t not in _STOP] or [f["target"].lower()]
    return any(t[:6] in answer_lc for t in toks)


def verify_draft(draft, case, findings, alias_map, resolved_meds, graph_ok):
    """Returns (violations, critic_ok, recommended_drugs)."""
    violations: List[str] = []
    spec = INTENTS[case["intent"]]
    fl = "\n".join(f"[{f['id']}] {format_finding(f)}" for f in findings) or "(none)"
    prompt = f"""PATIENT CASE (JSON): {case}

QUESTION TYPE: {case['intent']} | AUDIENCE: {case['audience']} | URGENCY: {case['urgency']}
REQUIRED STRUCTURE: {spec['format']}

KNOWLEDGE GRAPH FINDINGS:
{fl}

DRAFT ANSWER:
{draft}

Return a JSON object with exactly these keys:
- "recommended_drugs": generic names of drugs the draft tells THIS patient to take, start, continue or consider (including suggested alternatives). General educational mentions (for example a list of drug classes used for a condition) are NOT recommendations. EXCLUDE drugs the draft advises against.
- "endorses_unsafe_finding_ids": ids of findings whose drug/condition or drug pair the draft treats as acceptable or safe without the warning.
- "missing_finding_ids": ids of findings that the draft never clearly communicates.
- "risky_claims": short strings: specific patient doses, definitive diagnoses, invented citations or statistics, or statements that contradict standard clinical references.
- "answers_the_question": true if the first sentences directly answer what was asked.
- "follows_structure": true if the draft follows the required structure for this question type.
- "fits_audience": true if wording and tone fit the audience.
- "handles_urgency": true if URGENCY is routine, or if the draft clearly leads with the urgent advice.
- "quality_issues": short strings: vagueness, saying evidence is unavailable instead of helping, repetition, unprofessional tone. Empty list if clear and professional.
"""
    critic_ok, recommended = True, []
    try:
        c = llm.generate_json(prompt, system=VERIFY_SYSTEM, model=llm.FAST_MODEL)
        recommended = _lst(c.get("recommended_drugs"))
        ids = {f["id"]: f for f in findings}
        for fid in c.get("endorses_unsafe_finding_ids") or []:
            if fid in ids:
                violations.append(f"The draft treats [{fid}] as acceptable: {format_finding(ids[fid])}")
        for fid in c.get("missing_finding_ids") or []:
            if fid in ids:
                violations.append(f"The draft does not clearly communicate [{fid}]: {format_finding(ids[fid])}")
        violations += [f"Risky or unsupported claim: {x}" for x in (c.get("risky_claims") or [])[:3]]
        if c.get("answers_the_question") is False:
            violations.append("Quality: the first sentences do not directly answer the question that was asked")
        if c.get("follows_structure") is False:
            violations.append(f"Quality: follow the required structure for a {case['intent']} answer")
        if c.get("fits_audience") is False:
            violations.append(f"Quality: adjust wording and tone for the {case['audience']} audience")
        if c.get("handles_urgency") is False:
            violations.append(f"Quality: urgency is {case['urgency']}; begin with the urgent advice")
        violations += [f"Quality: {x}" for x in (c.get("quality_issues") or [])[:3]]
    except llm.LLMError as e:
        critic_ok = False
        logger.warning("critic unavailable: %s", e)

    al = draft.lower()
    for f in findings:
        if not _covered(al, f, alias_map) and not any(f"[{f['id']}]" in v for v in violations):
            violations.append(f"The draft does not mention [{f['id']}]: {format_finding(f)}")

    if recommended and graph_ok:
        try:
            resolved, _, _ = resolve_drugs(recommended, medical_graph)
            rec_db = sorted(set(resolved.values()))
            
            # FIXED LOGIC: Iterate over each recommended drug individually
            # This prevents alternatives (e.g., ibuprofen OR naproxen) from falsely triggering interactions with each other.
            for single_drug in rec_db:
                rec = medical_graph.check([single_drug], case["diseases"], case["allergies"], case["factors"],
                                          case["labs"], resolved_meds)
                for f in rec["findings"]:
                    violations.append(f"The draft recommends '{single_drug}' but the graph flags it: {format_finding(f)}")
                    
        except Exception as e:
            critic_ok = False
            logger.warning("graph re-check failed: %s", e)
    return violations, critic_ok, recommended


def fallback_answer(findings, unresolved) -> str:
    lines = ["**Bottom line:** A safe recommendation could not be confirmed for this patient. "
             "Please do not start or combine the medicines in question until the prescriber or a pharmacist has reviewed them."]
    if findings:
        lines.append("\n**Documented safety concerns**")
        lines += [f"- {format_finding(f)}" for f in findings]
    if unresolved:
        lines.append("\n**Not checked in the database:** " + ", ".join(unresolved) +
                     ". Absence from the database does not mean the medicine is safe.")
    lines.append("\n**Next step:** Discuss alternative treatments and monitoring with the prescribing clinician or a pharmacist.")
    return "\n".join(lines)


def footer(status, findings, unresolved, intent) -> str:
    if intent in ("drug_information", "condition_information", "general_medical"):
        s = "\n\n---\n*General medical information, not personal medical advice."
        if findings:
            s += f" {len(findings)} patient-specific concern(s) from the knowledge graph were included above."
        if status == "unverified":
            s += " WARNING: automated verification was incomplete."
        return s + " Please consult a healthcare professional about your own situation.*"
    s = ("\n\n---\n*Safety review: checked against a clinical knowledge graph (drug-condition, drug-drug, allergy, "
         "population and lab rules). ")
    s += f"{len(findings)} documented concern(s) flagged. " if findings else "No documented concerns found, which does not prove safety. "
    if unresolved:
        s += "Not checked (not in database): " + ", ".join(unresolved) + ". "
    if status == "unverified":
        s += "WARNING: automated verification was incomplete for this answer. "
    return s + "Decision support only, not a substitute for professional judgement.*"


# ------------------------------------------------------------------ pipeline
def prepare(patient_context: str, question: str) -> Dict:
    """Steps 1-3: extraction, retrieval, name resolution, graph pre-check, context facts."""
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=2) as pool:
        f_case = pool.submit(extract_case, patient_context, question)
        f_ev = pool.submit(_retrieve, question)
        case, evidence = f_case.result(), f_ev.result()
    t1 = time.time()

    prep = {"case": case, "evidence": evidence, "findings": [], "unresolved": [], "unmatched": [], "facts_block": None,
            "graph_ok": True, "alias_map": {}, "resolved_meds": [], "resolved_asked": []}
    try:
        res_asked, un_a, am_a = resolve_drugs(case["asked_drugs"], medical_graph)
        res_meds, un_m, am_m = resolve_drugs(case["patient_meds"], medical_graph)
        alias_map = {**am_m, **am_a}
        for k in set(am_a) & set(am_m):
            alias_map[k] = am_a[k] | am_m[k]
        asked, meds = sorted(set(res_asked.values())), sorted(set(res_meds.values()))
        chk = medical_graph.check(asked, case["diseases"], case["allergies"], case["factors"], case["labs"], meds)
        prep.update(findings=chk["findings"], unmatched=chk["unmatched_conditions"], unresolved=sorted(set(un_a + un_m)),
                    alias_map=alias_map, resolved_meds=meds, resolved_asked=asked)

        if INTENTS[case["intent"]]["graph"] == "context" or case["intent"] == "treatment_options":
            facts = []
            if case["topic_drugs"]:
                res_t, _, _ = resolve_drugs(case["topic_drugs"], medical_graph)
                facts += medical_graph.facts("Drug", sorted(set(res_t.values())))
            if case["topic_conditions"]:
                facts += medical_graph.facts("Disease", case["topic_conditions"])
            prep["facts_block"] = _facts_block(facts)
    except Exception as e:
        logger.error("graph step failed: %s", e)
        prep["graph_ok"] = False
    prep["timings"] = {"extract_and_retrieve_s": round(t1 - t0, 2), "graph_s": round(time.time() - t1, 2)}
    return prep


def run(patient_context: str, question: str, debug: bool = False) -> Dict:
    t_start = time.time()
    prep = prepare(patient_context, question)
    case, evidence, findings = prep["case"], prep["evidence"], prep["findings"]
    # pure education questions with nothing to check do not need the findings block
    block = _graph_block(findings, prep["unresolved"], prep["unmatched"], prep["graph_ok"]) \
        if (findings or prep["unresolved"] or case["asked_drugs"] or not prep["graph_ok"]) else None

    history, feedback, answer, status = [], None, None, "blocked_fallback"
    critic_ever_failed, last_draft, last_violations = False, None, []
    for rnd in range(1, MAX_ROUNDS + 1):
        draft = generate(patient_context, question, evidence, block, feedback, case, prep["facts_block"])
        violations, critic_ok, recommended = verify_draft(draft, case, findings, prep["alias_map"],
                                                          prep["resolved_meds"], prep["graph_ok"])
        critic_ever_failed = critic_ever_failed or not critic_ok
        last_draft, last_violations = draft, violations
        entry = {"round": rnd, "violations": violations, "recommended_drugs": recommended}
        if debug:
            entry["draft"] = draft
        history.append(entry)
        if not violations:
            answer, status = draft, "passed"
            break
        feedback = violations

    if answer is None:
        safety_left = [v for v in last_violations if not v.startswith(("Quality:", "Risky or unsupported"))]
        if last_draft and not safety_left:
            answer, status = last_draft, "quality_warning"
        else:
            answer = fallback_answer(findings, prep["unresolved"])
    if status == "passed" and (critic_ever_failed or not prep["graph_ok"]):
        status = "unverified"
    final_text = answer + footer(status, findings, prep["unresolved"], case["intent"])

    return {
        "answer": final_text,
        "intent": case["intent"], "audience": case["audience"], "urgency": case["urgency"],
        "missing_info": case["missing_info"],
        "safety_status": status,                          # passed | unverified | quality_warning | blocked_fallback
        "risk_detected": bool(findings),
        "findings": findings,
        "alerts": [f"[{f['severity']}] {format_finding(f)}" for f in findings],
        "unresolved_drugs": prep["unresolved"],
        "unmatched_conditions": prep["unmatched"],
        "graph_context_used": bool(prep["facts_block"]),
        "entities": case,
        "evidence": evidence,
        "rounds": len(history),
        "regenerations": max(0, len(history) - 1),
        "history": history,
        "timings": {**prep["timings"], "total_s": round(time.time() - t_start, 2)},
    }
 