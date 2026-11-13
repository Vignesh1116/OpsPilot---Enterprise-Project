import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Activity } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
}) => {
  const { isAuthenticated, isLoading, hasRole } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
        <div className="flex flex-col items-center gap-3">
          <Activity className="w-8 h-8 text-brand-500 animate-spin" />
          <p className="text-sm font-medium text-slate-400">Verifying security credentials...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRole && !hasRole(requiredRole)) {
    return (
      <div className="p-8 text-center bg-white rounded-xl border border-slate-200 m-8">
        <h2 className="text-lg font-bold text-slate-800">Access Restricted</h2>
        <p className="text-sm text-slate-600 mt-2">
          Your current role does not possess the permissions required to view this module.
        </p>
      </div>
    );
  }

  return <>{children}</>;
};
