import React, { useState } from 'react';
import { MapPin, ChevronDown, Check } from 'lucide-react';
import { OperatingLocation } from '../../types';

export const DEMO_LOCATIONS: OperatingLocation[] = [
  { id: 'loc-1', name: 'Coimbatore - Main Factory', code: 'CBE-MF01', type: 'factory', city: 'Coimbatore', state: 'Tamil Nadu' },
  { id: 'loc-2', name: 'Tiruppur - Apparel Warehouse', code: 'TPR-WH01', type: 'warehouse', city: 'Tiruppur', state: 'Tamil Nadu' },
  { id: 'loc-3', name: 'Chennai - Corporate Office', code: 'CHN-HQ01', type: 'corporate_office', city: 'Chennai', state: 'Tamil Nadu' },
  { id: 'loc-4', name: 'Madurai - Service Center', code: 'MDU-SC01', type: 'service_center', city: 'Madurai', state: 'Tamil Nadu' },
  { id: 'loc-5', name: 'Salem - Spare Parts Store', code: 'SLM-SP01', type: 'spare_parts_store', city: 'Salem', state: 'Tamil Nadu' },
];

export const LocationSelector: React.FC = () => {
  const [selectedLocation, setSelectedLocation] = useState<OperatingLocation>(DEMO_LOCATIONS[0]);
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200/80 border border-slate-200 rounded-lg text-sm font-medium text-slate-800 transition-colors shadow-sm"
        title="Active Operating Facility"
      >
        <span className="flex h-2 w-2 rounded-full bg-emerald-500 ring-2 ring-emerald-200" />
        <MapPin className="w-4 h-4 text-slate-500" />
        <div className="text-left">
          <p className="text-xs font-semibold leading-tight">{selectedLocation.name}</p>
          <p className="text-[10px] text-slate-500 leading-none">{selectedLocation.code}</p>
        </div>
        <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-xl border border-slate-200 py-1.5 z-50 animate-in fade-in zoom-in-95 duration-100">
            <div className="px-3 py-1.5 border-b border-slate-100">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Switch Operating Facility</p>
            </div>
            <div className="py-1">
              {DEMO_LOCATIONS.map((loc) => (
                <button
                  key={loc.id}
                  onClick={() => {
                    setSelectedLocation(loc);
                    setIsOpen(false);
                  }}
                  className="w-full flex items-center justify-between px-3 py-2 text-left hover:bg-slate-50 text-sm transition-colors"
                >
                  <div>
                    <p className={`font-medium ${loc.id === selectedLocation.id ? 'text-brand-600' : 'text-slate-700'}`}>
                      {loc.name}
                    </p>
                    <p className="text-xs text-slate-400 capitalize">{loc.type.replace('_', ' ')} • {loc.code}</p>
                  </div>
                  {loc.id === selectedLocation.id && (
                    <Check className="w-4 h-4 text-brand-600" />
                  )}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
