import { useState, useEffect } from 'react';
import { MapPin, Search, AlertCircle, Building2, PhoneCall } from 'lucide-react';

export default function HospitalRouter({ entities, urgency, isSafe }) {
  const [locationStatus, setLocationStatus] = useState('idle'); // idle, requesting, success, denied
  const [hospitals, setHospitals] = useState([]);
  const [manualCity, setManualCity] = useState('');
  
  // 1. Rule-Based Specialty
  let specialty = "Internal Medicine";
  if (entities) {
    const diseases = entities.diseases || [];
    const askedDrugs = entities.asked_drugs || [];
    if (diseases.includes('asthma') || askedDrugs.includes('propranolol')) specialty = "Pulmonology / Cardiology";
    else if (diseases.includes('peptic ulcer') || diseases.includes('gastric ulcer')) specialty = "Gastroenterology";
  }

  // 2. Strict Urgency (is_safe: false does NOT mean emergency automatically)
  const isEmergency = urgency === "emergency";

  const fetchHospitalsFromGoogle = async (lat, lng, city = null) => {
    setLocationStatus('loading_api');
    
    // THE API LOGIC
    // Note: Calling Google Places directly from React can cause CORS errors in production.
    // For a production app, you would send this lat/lng to your FastAPI backend and let Python call Google.
    try {
      // If we have a city (manual fallback), search by text. If GPS, search by coordinates.
      const query = isEmergency ? 'Emergency Room Hospital' : `${specialty} Clinic`;
      const locationParam = city ? `query=${query} in ${city}` : `location=${lat},${lng}&radius=${isEmergency ? 15000 : 5000}&keyword=${query}`;
      
      const YOUR_GOOGLE_API_KEY = "YOUR_API_KEY_HERE"; // Replace when ready
      
      // Simulate API call for the UI demo since we don't have an active key injected
      setTimeout(() => {
        setHospitals([
          { name: "Demo Hospital 1", address: city || "Near your location", rating: 4.5 },
          { name: "Demo Clinic 2", address: city || "Near your location", rating: 4.2 }
        ]);
        setLocationStatus(city ? 'manual_success' : 'gps_success');
      }, 1000);

    } catch (error) {
      console.error(error);
      setLocationStatus('error');
    }
  };

  const requestGPS = () => {
    setLocationStatus('requesting');
    if (!navigator.geolocation) {
      setLocationStatus('denied');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => fetchHospitalsFromGoogle(position.coords.latitude, position.coords.longitude),
      (error) => setLocationStatus('denied')
    );
  };

  return (
    <div className="space-y-4 mt-2 border-t border-slate-800 pt-4">
      
      {/* SEPARATED SPECIALTY & TRIAGE */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-3">
          <div className="text-blue-400 font-semibold text-[10px] uppercase mb-1">Suggested Specialty</div>
          <p className="text-sm font-bold text-slate-200">{specialty}</p>
        </div>
        <div className={`border rounded-lg p-3 ${isEmergency ? 'bg-rose-950/20 border-rose-800/50' : 'bg-slate-900 border-slate-800'}`}>
          <div className={`${isEmergency ? 'text-rose-400' : 'text-blue-400'} font-semibold text-[10px] uppercase mb-1`}>Triage Level</div>
          <p className={`text-sm font-bold uppercase ${isEmergency ? 'text-rose-300' : 'text-slate-200'}`}>
            {isEmergency ? 'Emergency Room' : 'Routine Consult'}
          </p>
        </div>
      </div>

      {/* HOSPITAL DIRECTORY SECTION */}
      <div className="bg-slate-950/50 border border-slate-800/50 rounded-lg p-4">
        <div className="text-emerald-400 font-semibold text-xs uppercase mb-3 flex items-center gap-2">
          <Building2 className="w-3.5 h-3.5" /> Live Directory Search
        </div>

        {locationStatus === 'idle' && (
          <button onClick={requestGPS} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-xs px-4 py-2 rounded-md transition">
            <MapPin className="w-3.5 h-3.5" /> Find Nearby Facilities
          </button>
        )}

        {(locationStatus === 'requesting' || locationStatus === 'loading_api') && (
          <div className="text-xs text-slate-400 flex items-center gap-2 animate-pulse">
            <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-500"></div>
            {locationStatus === 'requesting' ? 'Waiting for GPS permission...' : 'Searching Google Places...'}
          </div>
        )}

        {locationStatus === 'denied' && (
          <div className="space-y-3">
            <div className="text-xs text-rose-400 flex items-center gap-2">
              <AlertCircle className="w-3.5 h-3.5" /> Location access denied. Enter city manually:
            </div>
            <div className="flex gap-2">
              <input 
                type="text" 
                value={manualCity}
                onChange={(e) => setManualCity(e.target.value)}
                placeholder="e.g. Greater Noida" 
                className="bg-slate-900 border border-slate-700 rounded text-xs px-3 py-1.5 flex-1 text-white focus:outline-none focus:border-blue-500"
              />
              <button onClick={() => fetchHospitalsFromGoogle(null, null, manualCity)} className="bg-slate-800 hover:bg-slate-700 text-white text-xs px-3 py-1.5 rounded">
                <Search className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

        {(locationStatus === 'gps_success' || locationStatus === 'manual_success') && (
          <div className="space-y-3">
            <div className="text-[10px] text-slate-500 flex items-center gap-1">
              <MapPin className="w-3 h-3" /> Showing results for your area
            </div>
            <div className="space-y-2">
              {hospitals.map((h, i) => (
                <div key={i} className="bg-slate-900 border border-slate-800 p-3 rounded flex justify-between items-center">
                  <div>
                    <div className="text-sm font-semibold text-slate-200">{h.name}</div>
                    <div className="text-xs text-slate-500">{h.address} • {h.rating} ⭐</div>
                  </div>
                  <button className="text-blue-400 hover:text-blue-300 p-1.5 bg-blue-500/10 rounded-full">
                    <PhoneCall className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
            <div className="text-[9px] text-slate-500 italic mt-2 leading-tight">
              *Disclaimer: Please call ahead to verify that the facility has the required specialist available and is accepting patients.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}