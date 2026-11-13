import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Building2, Lock, Mail, AlertCircle, ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { ApiError } from '../../lib/api-client';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [email, setEmail] = useState('admin@coimbatoretextiles.com');
  const [password, setPassword] = useState('AdminSecurePassword123!');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setIsLoading(true);

    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      if (err instanceof ApiError) {
        setErrorMessage(err.data.detail || 'Authentication failed. Please verify credentials.');
      } else {
        setErrorMessage('Unable to connect to the authentication service.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoFill = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setErrorMessage(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-brand-600/10 blur-[120px] pointer-events-none rounded-full" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        <div className="flex items-center justify-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-brand-600 flex items-center justify-center text-white shadow-lg shadow-brand-500/30">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">OpsPilot</h1>
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">
              Enterprise Operations Platform
            </p>
          </div>
        </div>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        <div className="bg-slate-900/90 backdrop-blur-xl py-8 px-6 shadow-2xl rounded-2xl sm:px-10 border border-slate-800">
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-white">Sign in to your account</h2>
            <p className="text-xs text-slate-400 mt-1">
              Coimbatore Industrial Textiles Ltd – Single Sign-On
            </p>
          </div>

          {errorMessage && (
            <div className="mb-4 p-3.5 bg-rose-950/60 border border-rose-800/80 rounded-xl flex items-start gap-2.5 text-rose-300 text-xs">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Work Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Account Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-2 flex items-center justify-center gap-2 py-2.5 px-4 bg-brand-600 hover:bg-brand-500 text-white font-medium rounded-lg text-sm shadow-lg shadow-brand-600/30 transition-all disabled:opacity-50"
            >
              {isLoading ? 'Authenticating...' : 'Sign in securely'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Quick Demo Fill Matrix */}
          <div className="mt-8 pt-6 border-t border-slate-800">
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-brand-400" />
              Demo Roles & Preloaded Credentials
            </p>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <button
                type="button"
                onClick={() => handleDemoFill('admin@coimbatoretextiles.com', 'AdminSecurePassword123!')}
                className="p-2 bg-slate-950/80 hover:bg-slate-800/80 border border-slate-800 rounded-lg text-left text-slate-300 transition-colors"
              >
                <p className="font-semibold text-white">Company Admin</p>
                <p className="text-[10px] text-slate-500 truncate">admin@coimbatoretextiles.com</p>
              </button>

              <button
                type="button"
                onClick={() => handleDemoFill('employee@coimbatoretextiles.com', 'EmployeePassword123!')}
                className="p-2 bg-slate-950/80 hover:bg-slate-800/80 border border-slate-800 rounded-lg text-left text-slate-300 transition-colors"
              >
                <p className="font-semibold text-white">General Employee</p>
                <p className="text-[10px] text-slate-500 truncate">employee@coimbatoretextiles.com</p>
              </button>
            </div>
          </div>
        </div>

        <p className="text-center text-xs text-slate-500 mt-6">
          Headquarters: Coimbatore, Tamil Nadu • Strict Tenant Data Isolation Enforced
        </p>
      </div>
    </div>
  );
};
