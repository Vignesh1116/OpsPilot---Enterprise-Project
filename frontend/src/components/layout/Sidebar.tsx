import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Cpu,
  CalendarCheck,
  ClipboardList,
  Boxes,
  Truck,
  Activity,
  Settings,
  Building2,
} from 'lucide-react';

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
}

const NAV_ITEMS: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Assets Registry', href: '/assets', icon: Cpu },
  { name: 'Maintenance Schedules', href: '/maintenance', icon: CalendarCheck },
  { name: 'Work Orders', href: '/work-orders', icon: ClipboardList },
  { name: 'Inventory & Stock', href: '/inventory', icon: Boxes },
  { name: 'Procurement & Vendors', href: '/procurement', icon: Truck },
  { name: 'System Health', href: '/health', icon: Activity },
  { name: 'Settings & Admin', href: '/admin', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 h-screen sticky top-0 border-r border-slate-800">
      {/* Brand Header */}
      <div className="h-16 px-6 flex items-center gap-3 border-b border-slate-800 bg-slate-950/50">
        <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
          <Building2 className="w-4 h-4" />
        </div>
        <div>
          <span className="font-bold text-base text-white tracking-tight">OpsPilot</span>
          <span className="block text-[10px] text-slate-400 uppercase tracking-widest font-semibold">Enterprise Platform</span>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
          Operations Management
        </div>

        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            end={item.href === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-brand-600 text-white shadow-sm shadow-brand-600/30'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
              }`
            }
          >
            <item.icon className="w-4 h-4 shrink-0" />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </div>

      {/* Enterprise Organization Footer */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/40">
        <div className="text-xs text-slate-400">
          <p className="font-medium text-slate-200">Coimbatore Textiles Ltd</p>
          <p className="text-[11px] text-slate-400 mt-0.5">Headquarters: Coimbatore, TN</p>
        </div>
      </div>
    </aside>
  );
};
