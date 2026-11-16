import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Cpu,
  ArrowLeft,
  QrCode,
  Download,
  Printer,
  History,
  Building2,
  AlertTriangle,
  Settings,
  ShieldCheck,
} from 'lucide-react';
import { apiClient } from '../../lib/api-client';
import { Asset } from '../../types';
import { useAuth } from '../../context/AuthContext';

export const AssetDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const { hasRole } = useAuth();
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState<string>('');

  const { data: asset, isLoading, error } = useQuery<Asset>({
    queryKey: ['asset', id],
    queryFn: () => apiClient.get<Asset>(`/assets/${id}`),
    enabled: !!id,
  });

  const updateStatusMutation = useMutation({
    mutationFn: (newStatus: string) =>
      apiClient.put<Asset>(`/assets/${id}`, { status: newStatus }),
    onSuccess: (updated) => {
      queryClient.setQueryData(['asset', id], updated);
      queryClient.invalidateQueries({ queryKey: ['assets'] });
      setIsUpdatingStatus(false);
    },
  });

  if (isLoading) {
    return (
      <div className="p-12 text-center text-slate-500">
        <Cpu className="w-8 h-8 animate-spin mx-auto mb-2 text-brand-600" />
        <p className="text-sm font-medium">Loading asset specifications...</p>
      </div>
    );
  }

  if (error || !asset) {
    return (
      <div className="p-8 text-center text-rose-600">
        <AlertTriangle className="w-8 h-8 mx-auto mb-2 text-rose-500" />
        <p className="font-semibold">Asset Not Found</p>
        <p className="text-xs text-slate-500 mt-1">The requested asset does not exist or belongs to another company.</p>
        <Link to="/assets" className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-brand-600">
          <ArrowLeft className="w-4 h-4" /> Back to Assets
        </Link>
      </div>
    );
  }

  const handlePrintQR = () => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;
    printWindow.document.write(`
      <html>
        <head>
          <title>Asset QR Label – ${asset.asset_tag}</title>
          <style>
            body { font-family: monospace; text-align: center; padding: 20px; }
            .label-box { border: 2px dashed #000; padding: 16px; width: 280px; margin: auto; }
            img { width: 180px; height: 180px; }
            h2 { margin: 8px 0 4px 0; font-size: 16px; }
            p { margin: 2px 0; font-size: 12px; }
          </style>
        </head>
        <body>
          <div class="label-box">
            <h2>OpsPilot Equipment Tag</h2>
            <img src="${asset.qr_code_data_uri}" alt="${asset.asset_tag}" />
            <p><strong>${asset.asset_tag}</strong></p>
            <p>${asset.name}</p>
            <p>${asset.location_name || 'Main Facility'}</p>
          </div>
          <script>window.onload = function() { window.print(); window.close(); }</script>
        </body>
      </html>
    `);
    printWindow.document.close();
  };

  const getStatusBadge = (status: Asset['status']) => {
    switch (status) {
      case 'operational':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            Operational
          </span>
        );
      case 'in_maintenance':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
            In Maintenance
          </span>
        );
      case 'out_of_service':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            <span className="w-2 h-2 rounded-full bg-rose-500" />
            Out of Service
          </span>
        );
      case 'decommissioned':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200">
            Decommissioned
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Navigation */}
      <div className="flex items-center justify-between">
        <Link
          to="/assets"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Asset Registry
        </Link>

        <div className="flex items-center gap-3">
          <Link
            to={`/assets/${asset.id}/history`}
            className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-white hover:bg-slate-50 text-slate-700 font-medium rounded-lg text-xs border border-slate-200 shadow-sm transition-all"
          >
            <History className="w-3.5 h-3.5 text-brand-600" />
            Audit History
          </Link>
        </div>
      </div>

      {/* Main Asset Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="font-mono text-xs font-bold text-brand-700 bg-brand-50 px-2.5 py-1 rounded-md border border-brand-200">
              {asset.asset_tag}
            </span>
            {getStatusBadge(asset.status)}
            <span className="text-xs font-semibold uppercase px-2 py-0.5 rounded bg-slate-100 text-slate-600">
              {asset.critical_level} Criticality
            </span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">{asset.name}</h1>
          <p className="text-xs text-slate-500 mt-1 font-mono">
            ID: {asset.id} • Registered on {new Date(asset.created_at).toLocaleDateString()}
          </p>
        </div>

        {/* Change Status Control */}
        {hasRole('OPERATIONS_MANAGER') && (
          <div className="flex items-center gap-2">
            {isUpdatingStatus ? (
              <div className="flex items-center gap-2 bg-slate-50 p-2 rounded-xl border border-slate-200">
                <select
                  value={selectedStatus || asset.status}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="px-2 py-1 text-xs bg-white border border-slate-200 rounded-lg text-slate-800"
                >
                  <option value="operational">Operational</option>
                  <option value="in_maintenance">In Maintenance</option>
                  <option value="out_of_service">Out of Service</option>
                  <option value="decommissioned">Decommissioned</option>
                </select>
                <button
                  onClick={() => updateStatusMutation.mutate(selectedStatus || asset.status)}
                  disabled={updateStatusMutation.isPending}
                  className="px-3 py-1 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-medium"
                >
                  Save
                </button>
                <button
                  onClick={() => setIsUpdatingStatus(false)}
                  className="px-2 py-1 text-xs text-slate-500"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                onClick={() => {
                  setSelectedStatus(asset.status);
                  setIsUpdatingStatus(true);
                }}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-colors"
              >
                <Settings className="w-3.5 h-3.5" />
                Update Status
              </button>
            )}
          </div>
        )}
      </div>

      {/* Grid: Details, Financials, and QR Code */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Specifications & Location */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-100 pb-2">
              Machinery Specifications
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block font-medium">Model Number</span>
                <span className="text-slate-800 font-mono font-semibold text-sm">
                  {asset.model_number || 'N/A'}
                </span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block font-medium">Serial Number</span>
                <span className="text-slate-800 font-mono font-semibold text-sm">
                  {asset.serial_number || 'N/A'}
                </span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block font-medium">Asset Taxonomy / Category</span>
                <span className="text-slate-800 font-semibold text-sm">
                  {asset.category_name} ({asset.category_code})
                </span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block font-medium">Expected Design Lifetime</span>
                <span className="text-slate-800 font-semibold text-sm">
                  {asset.expected_lifetime_months} Months ({Math.round(asset.expected_lifetime_months / 12)} Years)
                </span>
              </div>
            </div>
          </div>

          {/* Location & Organization */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-100 pb-2 flex items-center gap-2">
              <Building2 className="w-4 h-4 text-brand-600" />
              Operating Facility & Department
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block font-medium">Assigned Operating Location</span>
                <span className="text-slate-800 font-semibold text-sm">
                  {asset.location_name || 'Coimbatore - Main Factory'}
                </span>
                <span className="text-slate-400 block text-[11px] font-mono mt-0.5">
                  Code: {asset.location_code || 'CBE-MF01'}
                </span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block font-medium">Operating Department</span>
                <span className="text-slate-800 font-semibold text-sm">
                  {asset.department_name || 'Production Operations'}
                </span>
              </div>
            </div>
          </div>

          {/* Purchase & Financials */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-100 pb-2 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              Procurement & Warranty Coverage
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block font-medium">Acquisition Cost</span>
                <span className="text-slate-900 font-bold text-base">
                  ₹{asset.purchase_cost.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block font-medium">Purchase Commission Date</span>
                <span className="text-slate-800 font-semibold text-sm">
                  {asset.purchase_date}
                </span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block font-medium">Warranty Expiration</span>
                <span className="text-slate-800 font-semibold text-sm">
                  {asset.warranty_expiry_date || 'Standard Coverage'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* QR Code Identification Card */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm text-center">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                <QrCode className="w-4 h-4 text-brand-600" />
                Equipment Tag QR
              </span>
              <span className="text-[10px] bg-slate-100 px-2 py-0.5 rounded text-slate-500 font-mono">
                PNG Label
              </span>
            </div>

            {asset.qr_code_data_uri ? (
              <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 inline-block mx-auto mb-4">
                <img
                  src={asset.qr_code_data_uri}
                  alt={`QR code for ${asset.asset_tag}`}
                  className="w-44 h-44 mx-auto object-contain"
                />
              </div>
            ) : (
              <div className="w-44 h-44 bg-slate-100 flex items-center justify-center rounded-2xl mx-auto mb-4 text-slate-400 text-xs">
                Generating QR...
              </div>
            )}

            <p className="font-mono text-sm font-bold text-slate-900">{asset.asset_tag}</p>
            <p className="text-xs text-slate-500 mt-0.5">{asset.name}</p>

            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-center gap-3">
              <button
                onClick={handlePrintQR}
                className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-colors"
              >
                <Printer className="w-3.5 h-3.5" />
                Print Label
              </button>

              <a
                href={asset.qr_code_data_uri}
                download={`qr_${asset.asset_tag.toLowerCase()}.png`}
                className="inline-flex items-center gap-1.5 px-3 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-semibold transition-all shadow-sm"
              >
                <Download className="w-3.5 h-3.5" />
                Download PNG
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
