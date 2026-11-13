import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Activity, Database, Server, RefreshCw, CheckCircle2, AlertTriangle, Building2 } from 'lucide-react';
import { apiClient } from '../../lib/api-client';
import { SystemHealthResponse } from '../../types';

export const SystemHealthPage: React.FC = () => {
  const { data, isLoading, error, refetch, isFetching } = useQuery<SystemHealthResponse>({
    queryKey: ['system-health'],
    queryFn: () => apiClient.get<SystemHealthResponse>('/system/health'),
    refetchInterval: 15000,
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">System Infrastructure Health</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Real-time connectivity and latency telemetry for OpsPilot core services.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 shadow-sm transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin text-brand-600' : 'text-slate-500'}`} />
          {isFetching ? 'Checking...' : 'Refresh Status'}
        </button>
      </div>

      {isLoading && (
        <div className="p-12 text-center bg-white rounded-xl border border-slate-200 shadow-sm">
          <Activity className="w-8 h-8 text-brand-600 animate-pulse mx-auto mb-3" />
          <p className="text-sm font-medium text-slate-600">Probing backend micro-services...</p>
        </div>
      )}

      {error && (
        <div className="p-6 bg-rose-50 border border-rose-200 rounded-xl text-rose-800">
          <div className="flex items-center gap-2 font-semibold">
            <AlertTriangle className="w-5 h-5 text-rose-600" />
            Backend Connection Notice
          </div>
          <p className="text-sm mt-1 text-rose-700">
            Could not contact FastAPI at <code className="bg-rose-100 px-1 py-0.5 rounded text-xs">{import.meta.env.VITE_API_BASE_URL || '/api/v1'}</code>. Ensure the backend server is running on port 8000.
          </p>
        </div>
      )}

      {data && (
        <div className="space-y-6">
          {/* Main Status Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Overall Status */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Overall Platform</span>
                <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                  data.status === 'healthy' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'
                }`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${data.status === 'healthy' ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                  {data.status.toUpperCase()}
                </span>
              </div>
              <p className="text-2xl font-bold text-slate-900">{data.service}</p>
              <p className="text-xs text-slate-500 mt-1">Environment: {data.environment}</p>
              <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
                Total Latency: <span className="font-semibold text-slate-700">{data.total_latency_ms} ms</span>
              </div>
            </div>

            {/* Database Component */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Primary Database</span>
                <Database className="w-4 h-4 text-brand-600" />
              </div>
              <p className="text-lg font-bold text-slate-900 capitalize">PostgreSQL 16</p>
              <p className="text-xs text-emerald-600 font-medium mt-1 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {data.components.database.status}
              </p>
              <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
                Ping Latency: <span className="font-semibold text-slate-700">{data.components.database.latency_ms ?? 0} ms</span>
              </div>
            </div>

            {/* Redis Component */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Cache & Broker</span>
                <Server className="w-4 h-4 text-brand-600" />
              </div>
              <p className="text-lg font-bold text-slate-900 capitalize">Redis 7</p>
              <p className={`text-xs font-medium mt-1 ${
                data.components.redis.status === 'healthy' ? 'text-emerald-600' : 'text-slate-500'
              }`}>
                {data.components.redis.status}
              </p>
              <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
                Latency: <span className="font-semibold text-slate-700">{data.components.redis.latency_ms ?? 'N/A'} ms</span>
              </div>
            </div>
          </div>

          {/* Enterprise Context */}
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-2 mb-3">
              <Building2 className="w-4 h-4 text-brand-600" />
              Enterprise Deployment Context
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-3 bg-slate-50 rounded-lg">
                <span className="text-slate-400 block font-medium">Headquarters Organization</span>
                <span className="text-slate-800 font-semibold text-sm">{data.enterprise_context.organization}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-lg">
                <span className="text-slate-400 block font-medium">Location</span>
                <span className="text-slate-800 font-semibold text-sm">{data.enterprise_context.headquarters}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
