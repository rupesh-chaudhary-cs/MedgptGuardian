// import { useState } from 'react';
// import ReactMarkdown from 'react-markdown';
// import { 
//   Send, ShieldAlert, Activity, Cpu, BookOpen, Building2, UserCheck, RefreshCw, CheckCircle2, AlertTriangle 
// } from 'lucide-react';

// export default function App() {
//   const [inputText, setInputText] = useState('');
//   const [response, setResponse] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [activeTab, setActiveTab] = useState('response'); 

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     if (!inputText.trim()) return;
    
//     setLoading(true);
//     setResponse(null);
//     setActiveTab('response');
    
//     // SYSTEM DUTY: Intelligently convert a single paragraph into the 3-part JSON format
//     // It splits the text by punctuation, takes the last sentence as the question, and the rest as context.
//     const sentences = inputText.match(/[^.!?]+[.!?]+/g) || [inputText];
//     let autoContext = "General adult patient context, no known chronic conditions.";
//     let autoQuestion = inputText.trim();

//     if (sentences.length > 1) {
//       autoQuestion = sentences.pop().trim();
//       autoContext = sentences.join(" ").trim();
//     }
    
//     try {
//       const res = await fetch('http://127.0.0.1:8000/api/v1/verify', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//           patient_context: autoContext,
//           question: autoQuestion,
//           debug: true
//         })
//       });
      
//       const data = await res.json();
//       setResponse(data);
//     } catch (error) {
//       console.error("Error connecting to MedGuard API:", error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const getSpecialistRecommendations = (entities) => {
//     if (!entities) return { specialty: "Clinical Pharmacist / General Practitioner", hospitals: ["Apollo Hospitals", "Max Super Speciality Hospital", "AIIMS New Delhi"] };
    
//     const diseases = entities.diseases || [];
//     const askedDrugs = entities.asked_drugs || [];
    
//     if (diseases.includes('asthma') || diseases.includes('severe asthma') || askedDrugs.includes('propranolol')) {
//       return {
//         specialty: "Pulmonologist & Senior Cardiologist",
//         hospitals: ["Fortis Escorts Heart Institute", "Medanta - The Medicity", "AIIMS Department of Pulmonary Medicine"]
//       };
//     }
//     if (diseases.includes('peptic ulcer') || diseases.includes('gastric ulcer')) {
//       return {
//         specialty: "Gastroenterologist & Clinical Pharmacologist",
//         hospitals: ["Apollo Hospitals (GI Unit)", "Max Super Speciality Hospital (Gastroenterology)", "Sir Ganga Ram Hospital"]
//       };
//     }
//     return {
//       specialty: "Internal Medicine Specialist & Clinical Pharmacist",
//       hospitals: ["Max Super Speciality Hospital", "Apollo Hospitals", "Fortis Healthcare"]
//     };
//   };

//   const recommendations = response ? getSpecialistRecommendations(response.entities) : null;

//   return (
//     <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center py-6 px-4 font-sans selection:bg-blue-600 selection:text-white">
//       <div className="w-full max-w-5xl bg-slate-900 border border-slate-800 shadow-2xl rounded-2xl overflow-hidden flex flex-col h-[94vh]">
        
//         {/* Header */}
//         <div className="bg-slate-900 border-b border-slate-800 p-4 flex items-center justify-between">
//           <div className="flex items-center gap-3">
//             <div className="p-2 bg-blue-600/20 border border-blue-500/30 rounded-xl">
//               <Activity className="w-6 h-6 text-blue-400" />
//             </div>
//             <div>
//               <h1 className="text-lg font-bold tracking-wide flex items-center gap-2">
//                 MedGuard AI <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded-md font-mono">v3.1 IEEE Grade</span>
//               </h1>
//               <p className="text-xs text-slate-400">Knowledge-Graph-Verified & Reflective Clinical Decision Support System</p>
//             </div>
//           </div>
//           <div className="flex items-center gap-2 text-xs">
//             <span className="flex items-center gap-1 bg-emerald-950/60 text-emerald-400 px-3 py-1.5 rounded-lg border border-emerald-800/50">
//               <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
//               Neo4j 5D Graph Active
//             </span>
//           </div>
//         </div>

//         {/* Dashboard Body */}
//         <div className="flex-1 overflow-y-auto p-6 space-y-6">
//           {!response && !loading && (
//             <div className="text-center text-slate-400 my-auto py-24 space-y-3">
//               <ShieldAlert className="w-14 h-14 mx-auto text-blue-400 opacity-90" />
//               <h2 className="text-xl font-semibold text-slate-200">Clinical Query Verification Engine</h2>
//               <p className="text-sm max-w-md mx-auto text-slate-400">
//                 Enter a full patient description and clinical question in the box below. The system automatically structures the context, flags PHI, and executes the MedReflect safety loop.
//               </p>
//             </div>
//           )}

//           {loading && (
//             <div className="flex flex-col items-center justify-center my-32 space-y-4">
//               <div className="relative">
//                 <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
//                 <Cpu className="w-5 h-5 text-blue-400 absolute inset-0 m-auto animate-pulse" />
//               </div>
//               <div className="text-center">
//                 <p className="text-sm font-medium text-slate-200">Processing JSON Payload & Running MedReflect Safety Loop...</p>
//                 <p className="text-xs text-slate-500 mt-1">Cross-referencing Neo4j Graph for drug interactions and contraindications.</p>
//               </div>
//             </div>
//           )}

//           {/* Post-Response Features & Tabs (This replaces the Swagger interface for the evaluator) */}
//           {response && (
//             <div className="space-y-6">
              
//               <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 text-xs">
//                 <div className="flex items-center gap-3">
//                   <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full font-semibold uppercase ${
//                     response.safety_status === 'passed' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800/50' :
//                     response.safety_status === 'conservative' ? 'bg-amber-950 text-amber-300 border border-amber-800/50' :
//                     'bg-rose-950 text-rose-300 border border-rose-800/50'
//                   }`}>
//                     {response.safety_status === 'passed' ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
//                     Status: {response.safety_status}
//                   </div>
//                   <span className="text-slate-400">Risk Detected: <strong className={response.risk_detected ? 'text-rose-400' : 'text-emerald-400'}>{response.risk_detected ? 'Yes (Conflicts Flagged)' : 'No'}</strong></span>
//                 </div>
//                 <div className="flex items-center gap-4 text-slate-400 font-mono">
//                   <span>⏱️ {response.timings?.total_s}s</span>
//                   <span>🔄 Refinements: {response.regenerations}</span>
//                 </div>
//               </div>

//               {/* TABS MENU: This is where you see all the raw Swagger data beautifully organized */}
//               <div className="flex border-b border-slate-800 gap-2">
//                 <button onClick={() => setActiveTab('response')} className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition-colors flex items-center gap-2 ${activeTab === 'response' ? 'bg-slate-800 text-blue-400 border-t border-x border-slate-700' : 'text-slate-400 hover:text-slate-200'}`}>
//                   <Activity className="w-3.5 h-3.5" /> Clinical AI Response
//                 </button>
//                 <button onClick={() => setActiveTab('reflection')} className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition-colors flex items-center gap-2 ${activeTab === 'reflection' ? 'bg-slate-800 text-blue-400 border-t border-x border-slate-700' : 'text-slate-400 hover:text-slate-200'}`}>
//                   <RefreshCw className="w-3.5 h-3.5" /> MedReflect History
//                 </button>
//                 <button onClick={() => setActiveTab('evidence')} className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition-colors flex items-center gap-2 ${activeTab === 'evidence' ? 'bg-slate-800 text-blue-400 border-t border-x border-slate-700' : 'text-slate-400 hover:text-slate-200'}`}>
//                   <BookOpen className="w-3.5 h-3.5" /> RAG Evidence
//                 </button>
//                 <button onClick={() => setActiveTab('swagger')} className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition-colors flex items-center gap-2 ${activeTab === 'swagger' ? 'bg-slate-800 text-blue-400 border-t border-x border-slate-700' : 'text-slate-400 hover:text-slate-200'}`}>
//                   <Cpu className="w-3.5 h-3.5" /> Raw Swagger JSON
//                 </button>
//               </div>

//               {/* Tab Content 1: Markdown Response & Recommendations */}
//               {activeTab === 'response' && (
//                 <div className="space-y-6">
//                   <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-inner prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed">
//                     <ReactMarkdown>{response.answer}</ReactMarkdown>
//                   </div>
//                   <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//                     <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 space-y-2">
//                       <div className="flex items-center gap-2 text-blue-400 font-semibold text-xs uppercase tracking-wider">
//                         <UserCheck className="w-4 h-4" /> Recommended Clinical Specialist
//                       </div>
//                       <p className="text-sm font-bold text-slate-200">{recommendations.specialty}</p>
//                     </div>
//                     <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 space-y-2">
//                       <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs uppercase tracking-wider">
//                         <Building2 className="w-4 h-4" /> Top Recommended Hospitals
//                       </div>
//                       <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
//                         {recommendations.hospitals.map((h, idx) => <li key={idx}>{h}</li>)}
//                       </ul>
//                     </div>
//                   </div>
//                 </div>
//               )}

//               {/* Tab Content 2: MedReflect Log */}
//               {activeTab === 'reflection' && (
//                 <div className="space-y-4">
//                   <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs space-y-4">
//                     <h3 className="font-bold text-blue-400 text-sm">MedReflect Audit Trail</h3>
//                     <div className="space-y-3">
//                       {response.history?.map((hist, i) => (
//                         <div key={i} className="bg-slate-900 border border-slate-800 p-3 rounded-lg space-y-2">
//                           <div className="flex justify-between items-center text-slate-300 font-semibold">
//                             <span>Round {hist.round}</span>
//                             <span className={hist.violations?.length === 0 ? "text-emerald-400" : "text-rose-400"}>
//                               {hist.violations?.length === 0 ? "✓ Passed Audit" : `⚠️ ${hist.violations.length} Violation(s) Caught`}
//                             </span>
//                           </div>
//                           {hist.violations?.length > 0 && (
//                             <ul className="list-disc list-inside text-rose-300 text-xs space-y-1 bg-rose-950/30 p-2 rounded border border-rose-900/50">
//                               {hist.violations.map((v, vi) => <li key={vi}>{v}</li>)}
//                             </ul>
//                           )}
//                         </div>
//                       ))}
//                     </div>
//                   </div>
//                 </div>
//               )}

//               {/* Tab Content 3: RAG Sources */}
//               {activeTab === 'evidence' && (
//                 <div className="space-y-4">
//                   <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs space-y-3">
//                     <h3 className="font-bold text-blue-400 text-sm">Retrieved Clinical Guidelines (RAG)</h3>
//                     {response.evidence?.length > 0 ? (
//                       response.evidence.map((ev, idx) => (
//                         <div key={idx} className="bg-slate-900 p-3 rounded-lg border border-slate-800 space-y-1">
//                           <span className="font-mono text-blue-300 font-bold">{ev.id}</span>
//                           <p className="text-slate-300">{ev.text}</p>
//                         </div>
//                       ))
//                     ) : (
//                       <p className="text-slate-400">No external RAG evidence passages were required.</p>
//                     )}
//                   </div>
//                 </div>
//               )}

//               {/* Tab Content 4: Swagger JSON */}
//               {activeTab === 'swagger' && (
//                 <div className="space-y-4">
//                   <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs font-mono space-y-4">
//                     <div>
//                       <span className="text-blue-400 font-bold">Extracted Entities (From Graph):</span>
//                       <pre className="mt-1 text-slate-400 overflow-x-auto bg-slate-900 p-3 rounded">{JSON.stringify(response.entities, null, 2)}</pre>
//                     </div>
//                     <div>
//                       <span className="text-emerald-400 font-bold">Full Swagger API Response Payload:</span>
//                       <pre className="mt-1 text-slate-400 overflow-x-auto bg-slate-900 p-3 rounded">{JSON.stringify(response, null, 2)}</pre>
//                     </div>
//                   </div>
//                 </div>
//               )}
//             </div>
//           )}
//         </div>

//         {/* Single Input Form Box */}
//         <div className="p-4 bg-slate-900 border-t border-slate-800">
//           <form onSubmit={handleSubmit} className="relative">
//             <textarea
//               value={inputText}
//               onChange={(e) => setInputText(e.target.value)}
//               placeholder="Paste patient history and question in one paragraph. (e.g., Sarah Connor is 65 with severe asthma and peptic ulcers. She takes warfarin. Is it safe to prescribe propranolol and aspirin together?)"
//               className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 px-4 pr-14 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none placeholder-slate-500"
//               rows="3"
//             />
//             <button 
//               type="submit" 
//               disabled={loading || !inputText.trim()}
//               className="absolute right-3 bottom-3 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg"
//             >
//               <Send className="w-4 h-4" />
//             </button>
//           </form>
//         </div>
//       </div>
//     </div>
//   );
// }


// import { useState, useEffect, useRef } from 'react';
// import ReactMarkdown from 'react-markdown';
// import { 
//   Send, ShieldAlert, Activity, Cpu, BookOpen, Building2, UserCheck, 
//   RefreshCw, CheckCircle2, AlertTriangle, Plus, MessageSquare, Menu, X
// } from 'lucide-react';

// export default function App() {
//   // --- 1. LOCAL STORAGE & MULTI-CHAT STATE ---
//   const [chats, setChats] = useState(() => {
//     const saved = localStorage.getItem('medguard_chats_v3');
//     return saved ? JSON.parse(saved) : [{ id: Date.now(), title: 'New Consultation', history: [] }];
//   });
//   const [activeChatId, setActiveChatId] = useState(chats[0]?.id || Date.now());
//   const [inputText, setInputText] = useState('');
//   const [loading, setLoading] = useState(false);
//   const [activeTab, setActiveTab] = useState('response'); 
//   const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  
//   const chatContainerRef = useRef(null);

//   // Save to localStorage whenever chats update
//   useEffect(() => {
//     localStorage.setItem('medguard_chats_v3', JSON.stringify(chats));
//   }, [chats]);

//   // Auto-scroll to bottom of chat
//   useEffect(() => {
//     if (chatContainerRef.current) {
//       chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
//     }
//   }, [chats, loading]);

//   const activeChat = chats.find(c => c.id === activeChatId) || chats[0];

//   const handleNewChat = () => {
//     const newChat = { id: Date.now(), title: 'New Consultation', history: [] };
//     setChats([newChat, ...chats]);
//     setActiveChatId(newChat.id);
//   };

//   // --- 2. MULTI-TURN MEMORY & SUBMIT LOGIC ---
//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     if (!inputText.trim()) return;
    
//     setLoading(true);
//     setActiveTab('response');
//     const userQuery = inputText.trim();
//     setInputText('');
    
//     // CONTEXT CHAINING: Bundle previous chat history for the backend
//     let autoContext = "General adult patient context. See question text for specific patient history.";
//     if (activeChat.history.length > 0) {
//       autoContext = "PREVIOUS CONVERSATION HISTORY (Use this for context):\n" + 
//         activeChat.history.map(h => `Patient/User: ${h.query}\nSystem: ${h.text}`).join("\n\n");
//     }
    
//     try {
//       const res = await fetch('http://127.0.0.1:8000/api/v1/verify', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//           patient_context: autoContext,
//           question: userQuery,
//           debug: true
//         })
//       });
      
//       const data = await res.json();
      
//       // MAPPED EXACTLY TO YOUR SWAGGER JSON
//       const responseText = data.ai_clinical_response || "No text received. Check Raw API Data tab.";
      
//       // Generate a title for the chat if it's the first message
//       let newTitle = activeChat.title;
//       if (activeChat.history.length === 0) {
//         newTitle = userQuery.length > 30 ? userQuery.substring(0, 30) + '...' : userQuery;
//       }

//       // Update the chat with the new Q&A turn
//       const newHistoryItem = { id: Date.now(), query: userQuery, text: responseText, rawData: data };
//       setChats(chats.map(c => 
//         c.id === activeChatId 
//           ? { ...c, title: newTitle, history: [...c.history, newHistoryItem] } 
//           : c
//       ));

//     } catch (error) {
//       console.error("Error connecting to MedGuard API:", error);
//       setChats(chats.map(c => 
//         c.id === activeChatId 
//           ? { ...c, history: [...c.history, { id: Date.now(), query: userQuery, text: "⚠️ Network Error: Could not connect to FastAPI backend.", rawData: null }] } 
//           : c
//       ));
//     } finally {
//       setLoading(false);
//     }
//   };

//   const getSpecialistRecommendations = (entities) => {
//     if (!entities) return { specialty: "Clinical Pharmacist", hospitals: ["Apollo Hospitals", "Max Super Speciality"] };
//     const diseases = entities.diseases || [];
//     const askedDrugs = entities.asked_drugs || [];
    
//     if (diseases.includes('asthma') || askedDrugs.includes('propranolol')) return { specialty: "Pulmonologist & Cardiologist", hospitals: ["Fortis Escorts", "Medanta", "AIIMS"] };
//     if (diseases.includes('peptic ulcer') || diseases.includes('gastric ulcer')) return { specialty: "Gastroenterologist", hospitals: ["Apollo (GI Unit)", "Max Super Speciality (Gastro)"] };
//     return { specialty: "Internal Medicine Specialist", hospitals: ["Max Super Speciality", "Apollo Hospitals"] };
//   };

//   return (
//     <div className="min-h-screen bg-slate-950 text-slate-100 flex font-sans selection:bg-blue-600 selection:text-white overflow-hidden">
      
//       {/* --- SIDEBAR --- */}
//       <div className={`${isSidebarOpen ? 'w-72' : 'w-0'} transition-all duration-300 bg-slate-900 border-r border-slate-800 flex flex-col flex-shrink-0 overflow-hidden`}>
//         <div className="p-4 border-b border-slate-800">
//           <button onClick={handleNewChat} className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-2.5 px-4 rounded-xl font-medium transition-colors">
//             <Plus className="w-4 h-4" /> New Consultation
//           </button>
//         </div>
//         <div className="flex-1 overflow-y-auto p-3 space-y-2">
//           {chats.map(chat => (
//             <button 
//               key={chat.id} 
//               onClick={() => setActiveChatId(chat.id)}
//               className={`w-full text-left flex items-center gap-3 px-3 py-3 rounded-xl transition-colors ${activeChatId === chat.id ? 'bg-slate-800 text-blue-400' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'}`}
//             >
//               <MessageSquare className="w-4 h-4 flex-shrink-0" />
//               <span className="text-sm truncate font-medium">{chat.title}</span>
//             </button>
//           ))}
//         </div>
//       </div>

//       {/* --- MAIN DASHBOARD --- */}
//       <div className="flex-1 flex flex-col h-screen relative">
        
//         {/* Header */}
//         <div className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 p-4 flex items-center justify-between z-10">
//           <div className="flex items-center gap-3">
//             <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 transition-colors">
//               {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
//             </button>
//             <div className="p-2 bg-blue-600/20 border border-blue-500/30 rounded-xl">
//               <Activity className="w-5 h-5 text-blue-400" />
//             </div>
//             <div>
//               <h1 className="text-lg font-bold tracking-wide flex items-center gap-2">
//                 MedGuard AI <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded-md font-mono">v3.1 IEEE Grade</span>
//               </h1>
//             </div>
//           </div>
//           <div className="flex items-center gap-2 text-xs">
//             <span className="flex items-center gap-1 bg-emerald-950/60 text-emerald-400 px-3 py-1.5 rounded-lg border border-emerald-800/50">
//               <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
//               Neo4j Graph Active
//             </span>
//           </div>
//         </div>

//         {/* Chat Feed */}
//         <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 md:p-8 scroll-smooth pb-56">
//           <div className="max-w-4xl mx-auto space-y-8">
            
//             {activeChat.history.length === 0 && !loading && (
//               <div className="text-center text-slate-400 mt-20 space-y-4">
//                 <ShieldAlert className="w-16 h-16 mx-auto text-blue-400 opacity-90" />
//                 <h2 className="text-2xl font-semibold text-slate-200">Clinical Query Engine</h2>
//                 <p className="text-sm max-w-md mx-auto text-slate-400">
//                   Paste the patient history and ask your question below. MedGuard retains conversation memory, checks graph conflicts, and runs safety audits.
//                 </p>
//               </div>
//             )}

//             {activeChat.history.map((turn, index) => {
//               const isLatest = index === activeChat.history.length - 1;
//               const response = turn.rawData;
//               const recommendations = response ? getSpecialistRecommendations(response.extracted_entities) : null;

//               // Parse RAG evidence strings into arrays for beautiful cards
//               const evidenceList = response?.retrieved_evidence ? response.retrieved_evidence.split('\n\n').filter(Boolean) : [];

//               return (
//                 <div key={turn.id} className="space-y-6">
//                   {/* User Bubble */}
//                   <div className="flex justify-end">
//                     <div className="bg-blue-600 text-white px-5 py-3.5 rounded-2xl rounded-tr-sm max-w-2xl text-sm shadow-md">
//                       {turn.query}
//                     </div>
//                   </div>

//                   {/* AI Bubble */}
//                   <div className="flex justify-start">
//                     <div className="w-full max-w-3xl space-y-4">
//                       {/* AI Text Response */}
//                       <div className="bg-slate-900 border border-slate-700/50 rounded-2xl rounded-tl-sm p-6 text-sm text-slate-200 prose prose-invert shadow-sm">
//                         <ReactMarkdown>{turn.text}</ReactMarkdown>
//                       </div>

//                       {/* Deep Dive Tabs */}
//                       {isLatest && response && (
//                         <div className="mt-4 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg animate-in slide-in-from-bottom-4 duration-500">
                          
//                           {/* Status Bar */}
//                           <div className="bg-slate-950 p-3 flex flex-wrap items-center justify-between gap-4 text-xs border-b border-slate-800">
//                             <div className="flex items-center gap-3">
//                               <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full font-semibold uppercase ${
//                                 response.safety_status === 'passed' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800/50' :
//                                 response.safety_status === 'conservative' ? 'bg-amber-950 text-amber-300 border border-amber-800/50' :
//                                 'bg-rose-950 text-rose-300 border border-rose-800/50'
//                               }`}>
//                                 {response.safety_status === 'passed' ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
//                                 Status: {response.safety_status || 'Unknown'}
//                               </div>
//                               <span className="text-slate-400">Risk Detected: <strong className={response.risk_detected ? 'text-rose-400' : 'text-emerald-400'}>{response.risk_detected ? 'Yes' : 'No'}</strong></span>
//                             </div>
//                             <span className="text-slate-400 font-mono flex items-center gap-4">
//                               <span>⏱️ {response.timings?.total_s || 'N/A'}s</span>
//                               <span>🔄 Audits: {response.regenerations || 0}</span>
//                             </span>
//                           </div>

//                           {/* Tabs Navigation */}
//                           <div className="flex overflow-x-auto border-b border-slate-800 bg-slate-900">
//                             <button onClick={() => setActiveTab('response')} className={`whitespace-nowrap px-4 py-2.5 text-xs font-semibold flex items-center gap-2 ${activeTab === 'response' ? 'bg-slate-800 text-blue-400 border-b-2 border-blue-500' : 'text-slate-400 hover:bg-slate-800/50'}`}>
//                               <UserCheck className="w-3.5 h-3.5" /> Clinical Routing
//                             </button>
//                             <button onClick={() => setActiveTab('reflection')} className={`whitespace-nowrap px-4 py-2.5 text-xs font-semibold flex items-center gap-2 ${activeTab === 'reflection' ? 'bg-slate-800 text-blue-400 border-b-2 border-blue-500' : 'text-slate-400 hover:bg-slate-800/50'}`}>
//                               <RefreshCw className="w-3.5 h-3.5" /> MedReflect Audit
//                             </button>
//                             <button onClick={() => setActiveTab('evidence')} className={`whitespace-nowrap px-4 py-2.5 text-xs font-semibold flex items-center gap-2 ${activeTab === 'evidence' ? 'bg-slate-800 text-blue-400 border-b-2 border-blue-500' : 'text-slate-400 hover:bg-slate-800/50'}`}>
//                               <BookOpen className="w-3.5 h-3.5" /> RAG Sources
//                             </button>
//                             <button onClick={() => setActiveTab('swagger')} className={`whitespace-nowrap px-4 py-2.5 text-xs font-semibold flex items-center gap-2 ${activeTab === 'swagger' ? 'bg-slate-800 text-blue-400 border-b-2 border-blue-500' : 'text-slate-400 hover:bg-slate-800/50'}`}>
//                               <Cpu className="w-3.5 h-3.5" /> Raw API Data
//                             </button>
//                           </div>

//                           {/* Tabs Content */}
//                           <div className="p-4 bg-slate-900 min-h-[200px]">
                            
//                             {/* Clinical Routing */}
//                             {activeTab === 'response' && (
//                               <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
//                                 <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
//                                   <div className="text-blue-400 font-semibold text-xs uppercase mb-2">Specialist Required</div>
//                                   <p className="text-sm font-bold text-slate-200">{recommendations?.specialty}</p>
//                                 </div>
//                                 <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
//                                   <div className="text-emerald-400 font-semibold text-xs uppercase mb-2">Hospital Routing</div>
//                                   <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
//                                     {recommendations?.hospitals.map((h, i) => <li key={i}>{h}</li>)}
//                                   </ul>
//                                 </div>
//                               </div>
//                             )}

//                             {/* MedReflect Audit */}
//                             {activeTab === 'reflection' && (
//                               <div className="space-y-3">
//                                 {response.reflection_history?.length > 0 ? response.reflection_history.map((hist, i) => (
//                                   <div key={i} className="bg-slate-950 border border-slate-800 p-3 rounded-lg text-xs">
//                                     <div className="flex justify-between items-center text-slate-300 font-semibold mb-2">
//                                       <span>Audit Round {hist.round}</span>
//                                       <span className={hist.violations?.length === 0 ? "text-emerald-400" : "text-rose-400"}>
//                                         {hist.violations?.length === 0 ? "✓ Clear" : `⚠️ ${hist.violations.length} Violation(s)`}
//                                       </span>
//                                     </div>
//                                     {hist.violations?.length > 0 && (
//                                       <ul className="list-disc list-inside text-rose-300 space-y-1 bg-rose-950/30 p-2 rounded border border-rose-900/50">
//                                         {hist.violations.map((v, vi) => <li key={vi}>{v}</li>)}
//                                       </ul>
//                                     )}
//                                   </div>
//                                 )) : <p className="text-xs text-slate-400">No MedReflect iterations required.</p>}
//                               </div>
//                             )}

//                             {/* RAG Sources */}
//                             {activeTab === 'evidence' && (
//                               <div className="space-y-3">
//                                 {evidenceList.length > 0 ? evidenceList.map((ev, idx) => (
//                                   <div key={idx} className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs">
//                                     <span className="font-mono text-blue-400 font-bold block mb-1">RAG Document {idx + 1}</span>
//                                     <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">{ev}</p>
//                                   </div>
//                                 )) : <p className="text-xs text-slate-400">No external RAG evidence pulled.</p>}
//                               </div>
//                             )}

//                             {/* Raw API Data */}
//                             {activeTab === 'swagger' && (
//                               <div className="space-y-4 text-xs font-mono">
//                                 <div>
//                                   <span className="text-blue-400 font-bold">Graph Findings:</span>
//                                   <pre className="mt-2 text-slate-400 overflow-x-auto bg-slate-950 border border-slate-800 p-3 rounded-lg max-h-48">
//                                     {JSON.stringify(response.graph_findings, null, 2)}
//                                   </pre>
//                                 </div>
//                                 <div>
//                                   <span className="text-emerald-400 font-bold">Full API Payload:</span>
//                                   <pre className="mt-2 text-slate-400 overflow-x-auto bg-slate-950 border border-slate-800 p-3 rounded-lg max-h-64">
//                                     {JSON.stringify(response, null, 2)}
//                                   </pre>
//                                 </div>
//                               </div>
//                             )}
//                           </div>
//                         </div>
//                       )}
//                     </div>
//                   </div>
//                 </div>
//               );
//             })}

//             {loading && (
//               <div className="flex justify-start">
//                 <div className="bg-slate-900 border border-slate-700/50 rounded-2xl rounded-tl-sm p-5 shadow-sm flex items-center gap-3">
//                   <div className="relative w-6 h-6">
//                     <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
//                     <Cpu className="w-3 h-3 text-blue-400 absolute inset-0 m-auto animate-pulse" />
//                   </div>
//                   <span className="text-sm text-slate-400 animate-pulse">Running Neo4j Graph & MedReflect...</span>
//                 </div>
//               </div>
//             )}
//           </div>
//         </div>

//         {/* --- FIXED INPUT AREA --- */}
//         <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-slate-950 via-slate-950 to-transparent pt-10">
//           <div className="max-w-4xl mx-auto relative">
//             <form onSubmit={handleSubmit} className="relative shadow-2xl">
//               <textarea
//                 value={inputText}
//                 onChange={(e) => setInputText(e.target.value)}
//                 onKeyDown={(e) => {
//                   if (e.key === 'Enter' && !e.shiftKey) {
//                     e.preventDefault();
//                     if(inputText.trim()) handleSubmit(e);
//                   }
//                 }}
//                 placeholder="Paste complete patient history or ask a follow-up question..."
//                 className="w-full bg-slate-900 border border-slate-700 rounded-2xl py-4 px-5 pr-16 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-none placeholder-slate-500 shadow-inner"
//                 rows="3"
//               />
//               <button 
//                 type="submit" 
//                 disabled={loading || !inputText.trim()}
//                 className="absolute right-3 bottom-3 p-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg"
//               >
//                 <Send className="w-4 h-4" />
//               </button>
//             </form>
//             <div className="text-center mt-2">
//               <span className="text-[10px] text-slate-500 font-mono">MedGuard AI limits: Verify clinical outputs via RAG & Swagger tabs.</span>
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }

import HospitalRouter from './HospitalRouter';
import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { 
  Send, ShieldAlert, Activity, Cpu, BookOpen, Building2, UserCheck, 
  RefreshCw, CheckCircle2, AlertTriangle, Plus, MessageSquare, Menu, X, Database
} from 'lucide-react';



// import { 
//   Send, ShieldAlert, Activity, Cpu, BookOpen, Building2, UserCheck, 
//   RefreshCw, CheckCircle2, AlertTriangle, Plus, MessageSquare, Menu, X, Database, MapPin
// } from 'lucide-react';

export default function App() {
  // --- 1. LOCAL STORAGE WITH BULLETPROOF STATE (Fix C) ---
  const [chats, setChats] = useState(() => {
    const saved = localStorage.getItem('medguard_chats_v5');
    const parsedChats = saved ? JSON.parse(saved) : [];
    return parsedChats.length > 0 ? parsedChats : [{ id: Date.now(), title: 'New Consultation', history: [] }];
  });
  const [activeChatId, setActiveChatId] = useState(() => chats[0].id);
  
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('response'); 
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  
  const chatContainerRef = useRef(null);

  useEffect(() => {
    localStorage.setItem('medguard_chats_v5', JSON.stringify(chats));
  }, [chats]);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chats, loading]);

  const activeChat = chats.find(c => c.id === activeChatId) || chats[0];

  const handleNewChat = () => {
    const newChat = { id: Date.now(), title: 'New Consultation', history: [] };
    setChats([newChat, ...chats]);
    setActiveChatId(newChat.id);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    
    setLoading(true);
    setActiveTab('response');
    const userQuery = inputText.trim();
    setInputText('');
    
    // --- 2. STRICT CONTEXT DEMARCATION (Fix A & B) ---
    // We use a neutral default. If history exists, we wrap it in a strict SYSTEM WARNING
    // so the backend LLM does not confuse past AI answers with verified patient data.
    let autoContext = "No patient-specific context has been provided yet. See question text for details.";
    if (activeChat.history.length > 0) {
      autoContext = "[SYSTEM WARNING: The following is previous conversation history for AI memory, DO NOT treat AI responses as verified patient clinical data]\n\n" + 
        activeChat.history.map(h => `User Query: ${h.query}\nAI System Response: ${h.text}`).join("\n\n");
    }
    
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_context: autoContext,
          question: userQuery,
          debug: true
        })
      });
      
      // --- 3. ROBUST ERROR HANDLING (Fix D) ---
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`HTTP Error ${res.status}: ${errorText}`);
      }
      
      const data = await res.json();
      const responseText = data.ai_clinical_response || "No text received. Check Raw API Data tab.";
      
      let newTitle = activeChat.title;
      if (activeChat.history.length === 0) {
        newTitle = userQuery.length > 30 ? userQuery.substring(0, 30) + '...' : userQuery;
      }

      const newHistoryItem = { id: Date.now(), query: userQuery, text: responseText, rawData: data };
      setChats(chats.map(c => 
        c.id === activeChatId ? { ...c, title: newTitle, history: [...c.history, newHistoryItem] } : c
      ));

    } catch (error) {
      console.error("Error connecting to API:", error);
      // Now displays actual HTTP error codes to the user if the backend fails
      setChats(chats.map(c => 
        c.id === activeChatId ? { ...c, history: [...c.history, { id: Date.now(), query: userQuery, text: `⚠️ Backend Error: ${error.message}`, rawData: null }] } : c
      ));
    } finally {
      setLoading(false);
    }
  };

  const getSpecialistRecommendations = (entities) => {
    if (!entities) return { specialty: "General Practitioner" };
    const diseases = entities.diseases || [];
    const askedDrugs = entities.asked_drugs || [];
    if (diseases.includes('asthma') || askedDrugs.includes('propranolol')) return { specialty: "Pulmonologist & Cardiologist" };
    if (diseases.includes('peptic ulcer') || diseases.includes('gastric ulcer')) return { specialty: "Gastroenterologist" };
    return { specialty: "Internal Medicine Specialist" };
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex font-sans selection:bg-blue-600 selection:text-white overflow-hidden">
      
      {/* SIDEBAR */}
      <div className={`${isSidebarOpen ? 'w-72' : 'w-0'} transition-all duration-300 bg-slate-900 border-r border-slate-800 flex flex-col flex-shrink-0 overflow-hidden`}>
        <div className="p-4 border-b border-slate-800">
          <button onClick={handleNewChat} className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-2.5 px-4 rounded-xl font-medium transition-colors">
            <Plus className="w-4 h-4" /> New Consultation
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {chats.map(chat => (
            <button 
              key={chat.id} 
              onClick={() => setActiveChatId(chat.id)}
              className={`w-full text-left flex items-center gap-3 px-3 py-3 rounded-xl transition-colors ${activeChatId === chat.id ? 'bg-slate-800 text-blue-400' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'}`}
            >
              <MessageSquare className="w-4 h-4 flex-shrink-0" />
              <span className="text-sm truncate font-medium">{chat.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* MAIN DASHBOARD */}
      <div className="flex-1 flex flex-col h-screen relative">
        <div className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 p-4 flex items-center justify-between z-10">
          <div className="flex items-center gap-3">
            <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 transition-colors">
              {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <div className="p-2 bg-blue-600/20 border border-blue-500/30 rounded-xl">
              <Activity className="w-5 h-5 text-blue-400" />
            </div>
            <h1 className="text-lg font-bold tracking-wide flex items-center gap-2">
              MedGuard UI <span className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-md font-mono">Evaluation Mode</span>
            </h1>
          </div>
        </div>

        <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 md:p-8 scroll-smooth pb-56">
          <div className="max-w-4xl mx-auto space-y-8">
            
            {activeChat.history.length === 0 && !loading && (
              <div className="text-center text-slate-400 mt-20 space-y-4">
                <ShieldAlert className="w-16 h-16 mx-auto text-blue-400 opacity-90" />
                <h2 className="text-2xl font-semibold text-slate-200">Clinical Verification UI</h2>
                <p className="text-sm max-w-md mx-auto text-slate-400">
                  Data rendered strictly from API payload.
                </p>
              </div>
            )}

            {activeChat.history.map((turn, index) => {
              const isLatest = index === activeChat.history.length - 1;
              const response = turn.rawData;
              const recommendations = response ? getSpecialistRecommendations(response.extracted_entities) : null;
              const evidenceList = response?.retrieved_evidence ? response.retrieved_evidence.split('\n\n').filter(Boolean) : [];
              
              const exactTimeSeconds = response?.processing_time_ms ? (response.processing_time_ms / 1000).toFixed(2) : "N/A";
              const exactReflectionRounds = response?.reflection_history?.length || 0;

              return (
                <div key={turn.id} className="space-y-6">
                  <div className="flex justify-end">
                    <div className="bg-blue-600 text-white px-5 py-3.5 rounded-2xl rounded-tr-sm max-w-2xl text-sm shadow-md">
                      {turn.query}
                    </div>
                  </div>

                  <div className="flex justify-start">
                    <div className="w-full max-w-3xl space-y-4">
                      <div className="bg-slate-900 border border-slate-700/50 rounded-2xl rounded-tl-sm p-6 text-sm text-slate-200 prose prose-invert shadow-sm">
                        <ReactMarkdown>{turn.text}</ReactMarkdown>
                      </div>

                      {isLatest && response && (
                        <div className="mt-4 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
                          
                          <div className="bg-slate-950 p-4 flex flex-col gap-3 text-xs border-b border-slate-800">
                            <div className="flex flex-wrap items-center justify-between gap-4">
                              <div className="flex items-center gap-3">
                                <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-semibold uppercase ${
                                  response.is_safe ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800' : 'bg-rose-950/60 text-rose-400 border border-rose-800'
                                }`}>
                                  {response.is_safe ? <CheckCircle2 className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
                                  Clinical Assessment: {response.is_safe ? 'Safe' : 'Unsafe / Risk Detected'}
                                </div>
                              </div>
                              <div className="flex items-center gap-4 font-mono text-slate-400">
                                <span>⏱️ Processed in {exactTimeSeconds}s</span>
                                <span>🔄 {exactReflectionRounds} Reflection Round(s)</span>
                              </div>
                            </div>
                            
                            <div className="flex flex-wrap gap-4 text-slate-500 font-mono text-[10px]">
                              <span className="flex items-center gap-1">
                                <Database className="w-3 h-3" /> Graph DB Available: {response.graph_available ? 'TRUE' : 'FALSE'}
                              </span>
                              <span className="flex items-center gap-1">
                                <Activity className="w-3 h-3" /> Graph Context Used: {response.graph_context_used ? 'TRUE' : 'FALSE'}
                              </span>
                              <span>Pipeline Status: {response.safety_status}</span>
                            </div>
                          </div>

                          <div className="flex overflow-x-auto border-b border-slate-800 bg-slate-900">
                            <button onClick={() => setActiveTab('response')} className={`whitespace-nowrap px-4 py-2.5 text-xs font-semibold flex items-center gap-2 ${activeTab === 'response' ? 'bg-slate-800 text-blue-400 border-b-2 border-blue-500' : 'text-slate-400 hover:bg-slate-800/50'}`}>
                              <UserCheck className="w-3.5 h-3.5" /> Clinical Routing
                            </button>
                            <button onClick={() => setActiveTab('reflection')} className={`whitespace-nowrap px-4 py-2.5 text-xs font-semibold flex items-center gap-2 ${activeTab === 'reflection' ? 'bg-slate-800 text-blue-400 border-b-2 border-blue-500' : 'text-slate-400 hover:bg-slate-800/50'}`}>
                              <RefreshCw className="w-3.5 h-3.5" /> MedReflect Audit ({exactReflectionRounds})
                            </button>
                            <button onClick={() => setActiveTab('evidence')} className={`whitespace-nowrap px-4 py-2.5 text-xs font-semibold flex items-center gap-2 ${activeTab === 'evidence' ? 'bg-slate-800 text-blue-400 border-b-2 border-blue-500' : 'text-slate-400 hover:bg-slate-800/50'}`}>
                              <BookOpen className="w-3.5 h-3.5" /> Raw RAG Sources
                            </button>
                            <button onClick={() => setActiveTab('swagger')} className={`whitespace-nowrap px-4 py-2.5 text-xs font-semibold flex items-center gap-2 ${activeTab === 'swagger' ? 'bg-slate-800 text-blue-400 border-b-2 border-blue-500' : 'text-slate-400 hover:bg-slate-800/50'}`}>
                              <Cpu className="w-3.5 h-3.5" /> API Payload
                            </button>
                          </div>

                          <div className="p-4 bg-slate-900 min-h-[200px]">
                            
                            {/* {activeTab === 'response' && (
                              <div className="space-y-4">
                                <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
                                  <div className="text-blue-400 font-semibold text-xs uppercase mb-2">Rule-Based Specialty Suggestion</div>
                                  <p className="text-sm font-bold text-slate-200">{recommendations?.specialty}</p>
                                  <p className="text-[10px] text-slate-500 mt-2 italic">*Based on extracted entities. Not a clinical referral.</p>
                                </div>
                                <div className="bg-slate-950/50 border border-slate-800/50 border-dashed rounded-lg p-4">
                                  <div className="text-slate-500 font-semibold text-xs uppercase mb-2">Hospital Directory Integration</div>
                                  <p className="text-xs text-slate-600 italic">[UI Placeholder - Requires integration with an external hospital directory API to display real facilities based on specialty criteria.]</p>
                                </div>
                              </div>
                            )} */}


                            {activeTab === 'response' && (
                              <HospitalRouter 
                                entities={response.extracted_entities} 
                                urgency={response.urgency} 
                                isSafe={response.is_safe} 
                              />
                            )}

                            {activeTab === 'reflection' && (
                              <div className="space-y-4">
                                {response.reflection_history?.length > 0 ? response.reflection_history.map((hist, i) => (
                                  <div key={i} className="bg-slate-950 border border-slate-800 rounded-lg overflow-hidden text-xs">
                                    <div className={`p-3 font-semibold flex justify-between items-center ${hist.violations?.length === 0 ? 'bg-emerald-950/30 text-emerald-400' : 'bg-rose-950/30 text-rose-400'}`}>
                                      <span>Audit Round {hist.round}</span>
                                      <span>{hist.violations?.length === 0 ? "✓ No Graph Conflicts Detected" : `⚠️ ${hist.violations.length} Violation(s) - Draft Blocked`}</span>
                                    </div>
                                    <div className="p-4 space-y-4">
                                      {hist.violations?.length > 0 && (
                                        <ul className="list-disc list-inside text-rose-300 space-y-1 bg-rose-950/20 p-3 rounded border border-rose-900/30">
                                          {hist.violations.map((v, vi) => <li key={vi}>{v}</li>)}
                                        </ul>
                                      )}
                                      <div>
                                        {/* STRICT LABELING (Fix E) */}
                                        <span className="text-slate-500 uppercase text-[10px] font-bold tracking-wider mb-1 block">
                                          {hist.violations?.length === 0 ? 'Draft (No Graph Conflicts Detected):' : 'Blocked Intermediate Draft:'}
                                        </span>
                                        <div className="text-slate-400 font-mono bg-slate-900 p-3 rounded h-32 overflow-y-auto whitespace-pre-wrap leading-relaxed">
                                          {hist.draft}
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                )) : <p className="text-xs text-slate-400">No MedReflect history available in payload.</p>}
                              </div>
                            )}

                            {activeTab === 'evidence' && (
                              <div className="space-y-3">
                                {evidenceList.length > 0 ? evidenceList.map((ev, idx) => (
                                  <div key={idx} className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-xs">
                                    <span className="font-mono text-blue-400 font-bold block mb-2 opacity-70">Raw Snippet {idx + 1}</span>
                                    <p className="text-slate-300 leading-relaxed whitespace-pre-wrap font-serif">{ev}</p>
                                  </div>
                                )) : <p className="text-xs text-slate-400">No external RAG evidence string found in payload.</p>}
                              </div>
                            )}

                            {activeTab === 'swagger' && (
                              <div className="space-y-4 text-xs font-mono">
                                <div>
                                  <span className="text-blue-400 font-bold mb-1 block">Data Source Findings (e.g. dim2_drug.csv):</span>
                                  <pre className="text-slate-400 overflow-x-auto bg-slate-950 border border-slate-800 p-3 rounded-lg max-h-48">
                                    {JSON.stringify(response.graph_findings, null, 2)}
                                  </pre>
                                </div>
                                <div>
                                  <span className="text-emerald-400 font-bold mb-1 block">Complete Evaluator Payload:</span>
                                  <pre className="text-slate-400 overflow-x-auto bg-slate-950 border border-slate-800 p-3 rounded-lg max-h-64">
                                    {JSON.stringify(response, null, 2)}
                                  </pre>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-slate-900 border border-slate-700/50 rounded-2xl p-5 shadow-sm flex items-center gap-3">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
                  <span className="text-sm text-slate-400">Processing Clinical Query...</span>
                </div>
              </div>
            )}
            
            <div className="h-48 w-full flex-shrink-0"></div>
          </div>
        </div>

        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-slate-950 via-slate-950 to-transparent pt-10">
          <div className="max-w-4xl mx-auto relative">
            <form onSubmit={handleSubmit} className="relative shadow-2xl">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if(inputText.trim()) handleSubmit(e);
                  }
                }}
                placeholder="Enter clinical query..."
                className="w-full bg-slate-900 border border-slate-700 rounded-2xl py-4 px-5 pr-16 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-none shadow-inner"
                rows="3"
              />
              <button 
                type="submit" 
                disabled={loading || !inputText.trim()}
                className="absolute right-3 bottom-3 p-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-500 disabled:opacity-50 transition-colors shadow-lg"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}