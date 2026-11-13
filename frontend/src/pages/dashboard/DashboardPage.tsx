import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, Cpu, ClipboardList, Boxes, Building2, CheckCircle2 } from 'lucide-react';
import { DEMO_LOCATIONS } from '../../components/layout/LocationSelector';

export const DashboardPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 rounded-2xl p-6 text-white shadow-lg border border-slate-700/50">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 mb-3">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Platform Foundation Operational
            </div>
            <h1 className="text-2xl font-bold tracking-tight">OpsPilot Operations Center</h1>
            <p className="text-sm text-slate-300 mt-1 max-w-2xl">
              Centralized enterprise management platform for industrial manufacturing facilities across Coimbatore, Tiruppur, Chennai, Madurai, and Salem.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/health"
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors shadow-sm"
            >
              <Activity className="w-4 h-4" />
              Verify System Health
            </Link>
          </div>
        </div>
      </div>

      {/* Demonstration Facilities Grid */}
      <div>
        <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-3">
          Configured Industrial Facilities (Tamil Nadu)
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {DEMO_LOCATIONS.map((loc) => (
            <div
              key={loc.id}
              className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:border-slate-300 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="p-2 bg-slate-100 rounded-lg text-slate-600">
                  <Building2 className="w-4 h-4" />
                </span>
                <span className="inline-flex items-center text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                  Online
                </span>
              </div>
              <p className="text-sm font-semibold text-slate-900 leading-snug">{loc.name}</p>
              <p className="text-xs text-slate-500 mt-1 capitalize">{loc.type.replace('_', ' ')}</p>
              <p className="text-[11px] font-mono text-slate-400 mt-2">{loc.code}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Architecture Checklist */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h2 className="text-base font-semibold text-slate-900 mb-4 flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-600" />
          Foundation Architecture Status
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-200/80">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-800">
              <Cpu className="w-4 h-4 text-brand-600" />
              Backend API & Database
            </div>
            <p className="text-xs text-slate-600 mt-1">
              FastAPI, SQLAlchemy 2 Async Engine, Alembic, PostgreSQL schema blueprint, RFC 7807 error format.
            </p>
          </div>
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-200/80">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-800">
              <Boxes className="w-4 h-4 text-brand-600" />
              Frontend Framework
            </div>
            <p className="text-xs text-slate-600 mt-1">
              React 18, Vite, TypeScript strict mode, Tailwind CSS design system, React Router, TanStack Query.
            </p>
          </div>
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-200/80">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-800">
              <ClipboardList className="w-4 h-4 text-brand-600" />
              Docker & Observability
            </div>
            <p className="text-xs text-slate-600 mt-1">
              Multi-stage Dockerfiles, Docker Compose orchestrating PostgreSQL 16 & Redis 7, structured logging.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
