import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  History,
  ArrowLeft,
  Clock,
  User as UserIcon,
  Activity,
} from 'lucide-react';
import { apiClient } from '../../lib/api-client';
import { Asset, AuditLog } from '../../types';

export const AssetHistoryPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const { data: asset } = useQuery<Asset>({
    queryKey: ['asset', id],
    queryFn: () => apiClient.get<Asset>(`/assets/${id}`),
    enabled: !!id,
  });

  const { data: history = [], isLoading, error } = useQuery<AuditLog[]>({
    queryKey: ['asset-history', id],
    queryFn: () => apiClient.get<AuditLog[]>(`/assets/${id}/history`),
    enabled: !!id,
  });

  const getActionBadge = (action: string) => {
    switch (action) {
      case 'CREATE':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            Registered
          </span>
        );
      case 'STATUS_CHANGE':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            Status Transition
          </span>
        );
      case 'UPDATE':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
            Specifications Updated
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
            {action}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Navigation */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-200">
        <div>
          <Link
            to={id ? `/assets/${id}` : '/assets'}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors mb-1"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Asset Specifications
          </Link>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <History className="w-5 h-5 text-brand-600" />
            Equipment Audit & Maintenance History
          </h1>
          {asset && (
            <p className="text-xs text-slate-500 font-mono mt-0.5">
              {asset.asset_tag} • {asset.name}
            </p>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="p-12 text-center text-slate-500">
          <Activity className="w-8 h-8 animate-spin mx-auto mb-2 text-brand-600" />
          <p className="text-sm font-medium">Loading chronological audit trail...</p>
        </div>
      ) : error ? (
        <div className="p-6 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm">
          Failed to load asset audit history.
        </div>
      ) : history.length === 0 ? (
        <div className="p-12 text-center text-slate-400 bg-white rounded-2xl border border-slate-200">
          <History className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm font-medium">No recorded audit history yet</p>
        </div>
      ) : (
        <div className="relative pl-6 space-y-6 before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
          {history.map((entry) => (
            <div key={entry.id} className="relative bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <span className="absolute -left-[19px] top-6 w-3 h-3 rounded-full bg-brand-600 ring-4 ring-brand-100" />

              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  {getActionBadge(entry.action)}
                  <span className="text-xs font-semibold text-slate-700 flex items-center gap-1">
                    <UserIcon className="w-3.5 h-3.5 text-slate-400" />
                    {entry.user_name || 'System Operator'}
                  </span>
                </div>
                <div className="text-xs text-slate-400 flex items-center gap-1 font-mono">
                  <Clock className="w-3.5 h-3.5" />
                  {new Date(entry.created_at).toLocaleString()}
                </div>
              </div>

              {/* Old vs New Values Diff */}
              <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                {entry.old_values && Object.keys(entry.old_values).length > 0 && (
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                    <p className="font-semibold text-slate-500 mb-1.5 uppercase text-[10px] tracking-wider">
                      Previous State
                    </p>
                    <pre className="text-slate-600 font-mono text-[11px] whitespace-pre-wrap">
                      {JSON.stringify(entry.old_values, null, 2)}
                    </pre>
                  </div>
                )}

                {entry.new_values && Object.keys(entry.new_values).length > 0 && (
                  <div className="p-3 bg-indigo-50/50 rounded-xl border border-indigo-100/80">
                    <p className="font-semibold text-brand-700 mb-1.5 uppercase text-[10px] tracking-wider">
                      New State Applied
                    </p>
                    <pre className="text-slate-800 font-mono text-[11px] whitespace-pre-wrap">
                      {JSON.stringify(entry.new_values, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
